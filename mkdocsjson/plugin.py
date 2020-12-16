import os.path
import subprocess
import shutil
import logging
logger = logging.getLogger("mkdocs")

from mkdocs.config import config_options as mkd
from .configitems import ConfigItems
from mkdocs.plugins import BasePlugin


class JsonPlugin(BasePlugin):
    config_scheme = (
        "url"    ,  mkd.Type(str),
        "schemas" , mkd.Type(str)
        )

    def on_post_build(self, config):
    
        url     = self.config["url"]
        schemas = self.config["schemas"]
        
        logger.info("Running json parse for {0}".format(url))
        for schema in schemas:
          logger.info("Parsing schema : ".format(schema))
          
        outpath = os.path.abspath(os.path.join(config["site_dir"], schema.split('.')[0], ".md"))
        
        logger.info("Outpath : ".format(outpath))
    

