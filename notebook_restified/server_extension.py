import tornado
from jupyter_server.base.handlers import JupyterHandler, path_regex
from jupyter_server.utils import url_path_join
from .model import KernelModel
import json
import traceback
import nbformat

def load_jupyter_server_extension(server_app):
    server_app.log.info('notebook_restified loaded')
    web_app = server_app.web_app
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']
    web_app.add_handlers(host_pattern, [
        (url_path_join(base_url, '/restified' + path_regex), Restified)
    ])
    
class Restified(JupyterHandler):
    async def execute(self, nb_path, params):
        item = self.contents_manager.get(path=nb_path)
        if not item or item['type'] != 'notebook':
            raise tornado.web.HTTPError(404)
            
        nb = nbformat.from_dict(item['content'])
        model = KernelModel(nb)
        
        try:
            loop = tornado.ioloop.IOLoop.current()
            task = loop.run_in_executor(None, model.execute, params)
            result = await task
        except Exception as e:
            self.set_status(400)
            body = "<div><pre>%s</pre></div>" % traceback.format_exc()
            self.finish(body)
            return
        try:
            self.finish(json.dumps(result))
        except:
            self.finish('Execution complete but response is not json serializable')
    
    @tornado.web.authenticated
    async def get(self, path=''):
        if not path:
            self.finish('at /restified index')
            return
        params = {k : self.get_argument(k) for k in self.request.arguments}
        return await self.execute(path, params)
    
    @tornado.web.authenticated
    async def post(self, path=''):
        params = tornado.escape.json_decode(self.request.body)
        return await self.execute(path, params)
        
        
