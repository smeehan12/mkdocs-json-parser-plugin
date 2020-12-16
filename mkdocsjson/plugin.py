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
        ("packages", ConfigItems(
            ("url"    , mkd.Type(str)),
            ("config" , mkd.Type(str)),
            ("workdir", mkd.Type(str)),
            )),
        ("tryclone", mkd.Type(bool, default=False)),
        ("recursive", mkd.Type(bool, default=False)),
        ("url", mkd.Type(str)),
        ("schemas", mkd.Type(list))
        )

    def on_post_build(self, config):
        for pkgConf in self.config["packages"]:
            for outname, cfg in pkgConf.items():
                outpath = os.path.abspath(os.path.join(config["site_dir"], outname))
                try:
                    basedir = cfg.get("url", ".")
                    icfg = cfg.get("config")
                    logger.info("Running json SAM for {0} with {1}, saving into {2}".format(
                        (basedir if basedir != "." else "current directory"), (icfg if icfg else "default config"), outpath))
                    runDoxygen(basedir, cfg=icfg, workdir=cfg.get("workdir"), dest=outpath, tryClone=self.config["tryclone"], recursive=self.config["recursive"])                
                except Exception as e:
                    logger.error("Skipped doxygen for package {0}: {1!s}".format(outname, e))