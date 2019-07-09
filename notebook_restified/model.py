import papermill
import jupyter_client
import nbformat
import warnings

class Model:
    def __init__(self, nb_name_or_node, out_stream=None):
        if isinstance(nb_name_or_node, nbformat.NotebookNode):
            self.nb = nb_name_or_node
            self.name = 'node' # for __repr__
            # TODO: PR this into papermill
            if not hasattr(self.nb.metadata, 'papermill'):
                self.nb.metadata['papermill'] = {'parameters' : dict(),
                                                 'environment_variables' : dict(),
                                                 'version' : papermill.__version__}
                
                for cell in self.nb.cells:
                    if not hasattr(cell.metadata, 'tags'):
                        cell.metadata['tags'] = []
                    if not hasattr(cell.metadata, 'papermill'):
                          cell.metadata['papermill'] = dict()
                        
        elif isinstance(nb_name_or_node, str):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.nb = papermill.iorw.load_notebook_node(nb_name_or_node)
                self.name = nb_name_or_node # for __repr__
                
        self.out_stream = out_stream # for status/print statements
        self.prepare_executor() # useful for some subclasses
        
    @property
    def kernel_name(self):
        return self.nb.metadata.get('kernelspec', {}).get('name', 'python')
      
    def prepare_executor(self):
        pass # define in subclasses where appropriate
      
    def execute(self, params=None):
        parameterized = self.parameterize(params)
        for cell in parameterized.cells:
            if cell.cell_type == 'code':
                if 'skip' in cell.metadata.tags:
                    continue
                else:
                    execution_result = self.run_cell(cell)
                    if 'return' in cell.metadata.tags:
                        return execution_result
                      
    def run_cell(self, cell):
        # this is the key method to define in subclasses for Model Execution behavior
        raise NotImplementedError 
        
    def parameterize(self, params=None):
        if not params:
            params = {}
        return papermill.parameterize.parameterize_notebook(self.nb, params)
      
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)
      
class PythonModel(Model):
    def prepare_executor(self):
        self.ldict = None
    
    def run_cell(self, cell):
        if self.ldict is None:
            self.ldict = locals()
            
        if 'override' in cell.metadata.tags and self.ldict:
            return
          
        if 'return' in cell.metadata.tags:
            return eval(cell.source, globals(), self.ldict)
          
        else:
            if self.out_stream:
                with self.out_stream:
                    exec(cell.source, globals(), self.ldict)
            else:
                exec(cell.source, globals(), self.ldict)
                
        self.ldict.update(locals())
        
class KernelModel(Model):
    def prepare_executor(self):
        self.parse_output = True
        self.km = jupyter_client.KernelManager(kernel_name=self.kernel_name)
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.allow_stdin = False
        self.kc.wait_for_ready()
        
    def run_cell(self, cell):
        parent_id = self.kc.execute(cell.source)
        exec_reply = self.kc.shell_channel.get_msg()
        output = None
        while True:
            msg = self.kc.iopub_channel.get_msg()
            msg_type = msg['msg_type']
            content = msg['content']
            if msg_type == 'stream':
                if self.out_stream:
                    with self.out_stream:
                        print(content['text'])
                        
            elif msg_type == 'execute_result':
                output = content['data']
                if self.parse_output:
                    output = list(output.values())[0]
                    
            if msg_type == 'status':
                if content['execution_state'] == 'idle':
                    return output
                  
    def run_code(self, code):
        "Useful for debug, run arbitrary line of code"
        cell = nbformat.NotebookNode(source=code)
        return self.run_cell(cell)

                