from papermill.iorw import load_notebook_node
from papermill.parameterize import parameterize_notebook

def execute_notebook(nb_path, params=None, overrides=None):
    """
    Executes a notebook (file path or url).
    params should be a dictionary that will parameterize a notebook papermill style
    overrides should be a dictionary that serve as locals() for exec/eval of cells
    returns the eval'd result of the first cell with a 'return' metadata tag
    """
    nb = load_notebook_node(nb_path)
    if not params:
        params = {}
    parameterized = parameterize_notebook(nb, params) 
    ### ^^ injects new cells after any cells which are tagged 'parameters'
    if overrides:
        ldict = overrides
    else:
        ldict = locals()
    
    for cell in parameterized.cells:
        if cell.cell_type == 'code':
            if overrides and 'override' in cell.metadata.tags:
                continue
            elif 'skip' in cell.metadata.tags:
                continue
            elif 'return' in cell.metadata.tags:
                return eval(cell.source, globals(), ldict)
            else:
                exec(cell.source, globals(), ldict)
    return