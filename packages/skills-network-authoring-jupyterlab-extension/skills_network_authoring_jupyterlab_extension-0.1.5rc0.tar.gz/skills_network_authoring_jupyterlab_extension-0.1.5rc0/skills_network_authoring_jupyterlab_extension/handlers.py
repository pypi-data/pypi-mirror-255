from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from urllib.parse import urlencode, unquote

class RouteHandler(APIHandler):
  # Route handler for the /skills_network_authoring_jupyterlab_extension/config endpoint.
  # A single endpoint that returns the Atlas base URL.
  
  @property
  def config(self):
      return self.settings["sn_config"]
  
  @tornado.web.authenticated
  def get(self):
    self.finish({
      "ATLAS_BASE_URL": self.config.atlas_base_url, 
      "SN_FILE_LIBRARY_URL": self.config.sn_file_library_url, 
      "AWB_BASE_URL": self.config.awb_base_url
    })


def setup_handlers(web_app):
  host_pattern = ".*$"

  base_url = web_app.settings["base_url"]

  # Prepend the base_url so that it works in a JupyterHub setting
  url_path = 'skills_network_authoring_jupyterlab_extension'
  handler_url_path = url_path_join(base_url, url_path, 'config')
  handlers = [(handler_url_path, RouteHandler)]
  web_app.add_handlers(host_pattern, handlers)
