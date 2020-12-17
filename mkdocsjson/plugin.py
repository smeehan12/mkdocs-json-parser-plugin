import os
import os.path
import subprocess
import shutil
import logging
logger = logging.getLogger("mkdocs")

from mkdocs.config import config_options as mkd
from .configitems import ConfigItems
from mkdocs.plugins import BasePlugin

import mkdocs.structure.files
from mkdocs.structure.files import File



def GetSettings(prop, subsystem):

    allsettings = {}

    if subsystem['type']=='object':
        # add the top level singular one
        if 'description' in subsystem:
          allsettings.update({prop : subsystem['description']})
        else:
          allsettings.update({prop : "MISSING"})
        # tunnel down one level and get attributes for each property
        for subprop in subsystem['properties']:       
            allsettings.update(GetSettings(subprop, subsystem['properties'][subprop]))
    elif subsystem['type']=='array':
        # add the top level singular one
        if 'description' in subsystem:
          allsettings.update({prop : subsystem['description']})
        else:
          allsettings.update({prop : "MISSING"})
        # tunnel down one level and get attributes for each property
        if subsystem['items']['type']=='object':
          for subprop in subsystem['items']['properties']:       
              allsettings.update(GetSettings(subprop, subsystem['items']['properties'][subprop]))
    else:
        if 'description' in subsystem:
          allsettings.update({prop : subsystem['description']})
        else:
          allsettings.update({prop : "MISSING"})
        
    return allsettings
    
    
def WriteFile(outpath, myconfigs):

    fout = open(outpath, "w+")
    
    for key in myconfigs:
        fout.write('  - '+key+' : '+myconfigs[key]+'\n')
        
    fout.close()


class JsonPlugin(BasePlugin):
    config_scheme = (
        ("url", mkd.Type(str)),
        ("schemas", mkd.Type(list))
        )

    def on_files(self, files, config):
    
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
        
                schemas = self.config["schemas"]
        
                logger.info("Running json on {0}".format(url))
        
                for schema in schemas:
                    logger.info(" >> Schema {0}".format(schema))
                    inpath  = repopath+"/"+schema
                                    
                    
                    logger.info(" >> Inpath {0}".format(inpath))
                    outpath = os.path.abspath(os.path.join(config["site_dir"], schema.split("/")[-1].replace(".schema",".md")))
                    logger.info(" >> Outpath {0}".format(outpath))
                    
                    jsonpath = inpath.replace(".schema",".json")
                    
                    logger.info(" >> JSonPath - {0}".format(str(inpath)))
                  
                    fin = open(inpath,"r")
                    lines = fin.readlines()
                    logger.info(" >> NLines {0}".format(str(len(lines))))
            
                    import json
                    
                    jsonstring = ""
                    for line in lines:
                       jsonstring += line

                    jsonschema = json.loads(jsonstring)
                    
                    myconfigs = {}
                    
                    stuff = jsonschema["properties"]["settings"]["properties"]
                    
                    for key in stuff:
                        logger.info(" >> Prop - {0}".format(str(key)))
                        myconfigs.update(GetSettings(key, stuff[key]))
                        
                    
                        
                    
                    WriteFile(outpath, myconfigs)
                        
                    os.system("cat "+outpath)    
                    
                    abspath = os.path.abspath(outpath)
                    
                    logger.info(" >> OutpathAbs - {0}".format(str(abspath)))
                    
                    os.system("ls "+config["site_dir"])
                    
                    logger.info(" >> SiteDir - {0}".format(str(config["site_dir"])))
                    
                    fin = open(abspath,"r")
                    logger.info(" >> Lines - {0}".format(str(len(fin.readlines()))))
                    
                    
        out = []
        
        docs_dir=""
                    
        # add existing files
        for i in files:
            name = i.src_path
            logger.info(" >> File - {0}".format(str(name)))        
            logger.info(" >> Type - {0}".format(str(type(i))))       
            
            logger.info(" >> File src_path      - {0}".format(str(i.src_path)))
            logger.info(" >> File abs_path      - {0}".format(str(i.abs_src_path)))
            logger.info(" >> File dest_path     - {0}".format(str(i.dest_path)))
            logger.info(" >> File abs_dest_path - {0}".format(str(i.abs_dest_path)))
            logger.info(" >> File url           - {0}".format(str(i.url)))
            
            # get abs_src_path for later use
            if "docs" ==  str(i.abs_src_path.split("/")[-2]):
                docs_dir = ""
                for dir in i.abs_src_path.split("/")[0:-1]:
                    docs_dir += dir
                    docs_dir += "/"
            
             
            out.append(i)
            
            
        # add the new parsed file
        logger.info(" New Fuckin File")
        
        # get the docs path
        path = str(abspath.split("/")[-1])
        src_dir = docs_dir
        
        newfile = File( path, src_dir, abspath, use_directory_urls=False)
        
        logger.info(" >> File src_path      - {0}".format(str(newfile.src_path)))
        logger.info(" >> File abs_src_path  - {0}".format(str(newfile.abs_src_path)))
        logger.info(" >> File dest_path     - {0}".format(str(newfile.dest_path)))
        logger.info(" >> File abs_dest_path - {0}".format(str(newfile.abs_dest_path)))
        logger.info(" >> File url           - {0}".format(str(newfile.url)))
            
        return mkdocs.structure.files.Files(out)
                    
                        
#    def on_files(self, files, config):
#        
#        for i in files:
#            name = i.src_path
#            logger.info(" >> File - {0}".format(str(name)))        

