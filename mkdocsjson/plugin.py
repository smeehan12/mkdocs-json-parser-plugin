import os.path
import subprocess
import shutil
import logging
logger = logging.getLogger("mkdocs")

from mkdocs.config import config_options as mkd
from .configitems import ConfigItems
from mkdocs.plugins import BasePlugin




def ParseSchema(schema,inputpath,outputpath):
    logger.info(" >> Parsing Schema {0} from {1} into {2}".format(schema,inputpath,outputpath))

class JsonPlugin(BasePlugin):
    config_scheme = (
        ("url", mkd.Type(str)),
        ("schemas", mkd.Type(list))
        )

    def on_post_build(self, config):
    
        url     = self.config["url"]
        
        basedir = url
        
        from urllib.parse import urlparse
        pres = urlparse(basedir)
        logger.info("PresStuff : "+str(pres.scheme)+" "+str(pres.netloc))
        if pres.scheme and pres.netloc:
            from tempfile import TemporaryDirectory
            with TemporaryDirectory() as tmpDir:
                reponame = os.path.split(basedir)[-1].split(".")[0]
                if len(reponame) == 0:
                    reponame = "repo"
                repopath = os.path.join(tmpDir, reponame)
                
                logger.info("Cloning : "+str(tmpDir)+"  "+str(reponame)+"  "+repopath)
                
                command = "git clone --depth 1 "+basedir+" "+repopath

                logger.info("Command Call : "+command)
                
                #subprocess.call([command])
                subprocess.check_call(["git", "clone", "--depth", "1", basedir, repopath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                os.system("ls "+repopath)

                #lineout = ""
                #for path in os.system("ls "+repopath):
                #    lineout += path
                #    lineout += " - "
                #logger.info("ClonedThing : "+lineout)
        
                schemas = self.config["schemas"]
        
                logger.info("Running json on {0}".format(url))
        
                for schema in schemas:
                    logger.info(" >> Schema {0}".format(schema))
                    inpath  = repopath+"/"+schema
                    logger.info(" >> Inpath {0}".format(inpath))
                    outpath = os.path.abspath(os.path.join(config["site_dir"], schema.replace(".schema",".md")))
                    logger.info(" >> Outpath {0}".format(outpath))
                    
                    jsonpath = inpath.replace(".schema",".json")
                    
                    os.system("mv "+inpath+"  "+jsonpath)
                    
                    logger.info(" >> JSonPath - {0}".format(str(jsonpath)))
                  
                    fin = open(inpath,"r")
                    lines = fin.readlines()
                    logger.info(" >> NLines {0}".format(str(len(lines))))
            
                    import json
                    
                    jsonstring = ""
                    for line in lines:
                       jsonstring += line

                    jsonschema = json.load(jsonstring)
                    
                    myconfigs = {}
                    
                    for key,entry in jsonschema["properties"]["settings"]["properties"]:
                        logger.info(" >> Prop - {0}".format(str(key)))
                        
                        
          

#        for pkgConf in self.config["packages"]:
#            for outname, cfg in pkgConf.items():
#                outpath = os.path.abspath(os.path.join(config["site_dir"], outname))
#                try:
#                    basedir = cfg.get("url", ".")
#                    icfg = cfg.get("config")
#                    logger.info("Running json SAM for {0} with {1}, saving into {2}".format(
#                        (basedir if basedir != "." else "current directory"), (icfg if icfg else "default config"), outpath))
#                    runDoxygen(basedir, cfg=icfg, workdir=cfg.get("workdir"), dest=outpath, tryClone=self.config["tryclone"], recursive=self.config["recursive"])                
#                except Exception as e:
#                    logger.error("Skipped doxygen for package {0}: {1!s}".format(outname, e))