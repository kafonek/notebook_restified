from tornado import web
from jupyter_server.base.handlers import JupyterHandler, path_regex
from jupyter_server.utils import url_path_join
from .utils import execute_notebook
import json

def load_jupyter_server_extension(server_app):
    web_app = server_app.web_app
    host_pattern = '.*$'
    base_url = url_path_join(web_app.settings['base_url'])
    web_app.add_handlers(host_pattern, [(url_path_join(base_url, '/restified' + path_regex), Restified)])

class Restified(JupyterHandler):
    @web.authenticated
    def get(self, path=''):
        nb_path = path.lstrip('/')
        parameters = {k : self.get_argument(k) for k in self.request.arguments}
        result = execute_notebook(nb_path, parameters)
        try:
            self.finish(json.dumps(result))
        except:
            self.finish("Execution complete but response is not json serializable")
