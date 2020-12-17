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

import copy

'''
This builds the dictionary of relevant properties from the schema you feed it
'''
def BuildPropDictionary(prop, subsystem):

    myProps = {}
  
    # title
    if 'title' in subsystem:
      myProps["Title"] = subsystem['title']
    else:
      myProps["Title"] = prop
      
    # description
    if 'description' in subsystem:
      myProps["Description"] = subsystem['description']
    elif 'options' in subsystem:
      if 'infoText' in subsystem['options']:
        myProps["Description"] = subsystem['options']['infoText']
      else:
        myProps["Description"] = "MISSING"
    else:
      myProps["Description"] = "MISSING"
          
    # nitems
    if subsystem['type']=='array':
      if 'minItems' in subsystem and 'maxItems' in subsystem:
        myProps["NEntries"] = '['+str(subsystem['minItems'])+','+str(subsystem['minItems'])+']'
      elif 'minItems' in subsystem and 'maxItems' not in subsystem: 
        myProps["NEntries"] = '['+str(subsystem['minItems'])+', no max]'
      elif 'minItems' not in subsystem and 'maxItems' in subsystem: 
        myProps["NEntries"] = '[no min, '+str(subsystem['maxItems'])+']'
    
    # default
    if 'default' in subsystem:
      myProps["Default"] = subsystem['default']
          
    # enum
    if 'enum' in subsystem:
      myProps["Possible Values"] = subsystem['enum']
          
    # minimum/maximum
    min = "no min"
    max = "no max"
    if 'minimum' in subsystem:
      min = subsystem['minimum']
    elif 'exclusiveMinimum' in subsystem:
      min = subsystem['exclusiveMinimum']
      
    if 'maximum' in subsystem:
      mxa = subsystem['maximum']
    elif 'exclusiveMaximum' in subsystem:
      max = subsystem['exclusiveMaximum']
      
    if not (min=="no min" and max=="no max"):
      myProps["Input Bounds"] = '['+str(min)+','+str(max)+']'
    
    print("myProps")
    print(myProps)
    
    return myProps

'''
This is the recursive function which walks through the schema you feed
it and will either populate the settings or descend further 
'''
def GetSettings(prop, subsystem):

    allsettings = {}

    if subsystem['type']=='object':
        # add the top level singular one
        allsettings.update({prop : BuildPropDictionary(prop, subsystem)})

        # tunnel down one level and get attributes for each property
        for subprop in subsystem['properties']:       
            allsettings.update(GetSettings(subprop, subsystem['properties'][subprop]))
    elif subsystem['type']=='array':
        # add the top level singular one
        allsettings.update({prop : BuildPropDictionary(prop, subsystem)})
        # tunnel down one level and get attributes for each property
        if subsystem['items']['type']=='object':
          for subprop in subsystem['items']['properties']:       
              allsettings.update(GetSettings(subprop, subsystem['items']['properties'][subprop]))
    else:
        allsettings.update({prop : BuildPropDictionary(prop, subsystem)})
        
    return allsettings
    
'''
This writes the output markdown file with the formatting you desire
'''
def WriteFile(outpath, myconfigs):

    fout = open(outpath, "w+")
    
    for key in myconfigs:
        fout.write('  - `'+key+'` (*'+myconfigs[key]['Title']+'*)\n')
        for attrib in myconfigs[key]:
            fout.write('    - __'+attrib+'__ : '+str(myconfigs[key][attrib])+'\n')
        
    fout.close()


class JsonPlugin(BasePlugin):
    config_scheme = (
        ("url", mkd.Type(str)),
        ("schemas", mkd.Type(list)),
        ("configs", mkd.Type(dict))
        )

    '''
    Us the on_files event because you need to modify the file lists
    '''
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
                subprocess.check_call(["git", "clone", "--depth", "1", basedir, repopath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
                logger.info("Preparing file list")
                out = []
                docs_dir=""
                # add existing files
                for i in files:
                    name = i.src_path

                    # get abs_src_path for later use
                    if "docs" ==  str(i.abs_src_path.split("/")[-2]):
                        docs_dir = ""
                        for dir in i.abs_src_path.split("/")[0:-1]:
                            docs_dir += dir
                            docs_dir += "/"
        
                    out.append(i)
                    
                ##############################
                # config parsing
                ##############################
                logger.info("Adding new files to local directory for configs")
                configs = self.config["configs"]
                for config in configs:
                
                    entry  = configs[config]
                
                    logger.info(" >> Config {0}".format(config))
                    logger.info(" >> Entry {0}".format(entry))
                    
                    inpath  = repopath+"/"+config
                                                    
                    outpath = os.path.abspath(os.path.join(config["site_dir"], str(entry+".md"))
                    
                    fin = open(inpath,"r")
                    lines = fin.readlines()
            
                    import json
                    
                    jsonstring = ""
                    for line in lines:
                       jsonstring += line

                    jsonschema = json.loads(jsonstring)
                    
                    # only look at the "settings" in the schema which are system specific configurations
                    stuff = jsonschema[entry]
                    
                    abspath = os.path.abspath(outpath)
                    
                    with open(outpath, "w") as outfile:
                      json.dump(stuff, outfile, indent=4)
                        

                    # put the file in the local location from this temp directory
                    command = "cp "+abspath+" "+docs_dir
                    os.system(command)

                    #logger.info("content : {0}".format(os.system("ls "+docs_dir)))
        
                    # get the docs path
                    path = str(abspath.split("/")[-1])
                    src_dir = docs_dir
        
                    newfile = File( path, src_dir, path, use_directory_urls=True)
        
                    logger.info(" >> File src_path      - {0}".format(str(newfile.src_path)))
                    logger.info(" >> File abs_src_path  - {0}".format(str(newfile.abs_src_path)))
                    logger.info(" >> File dest_path     - {0}".format(str(newfile.dest_path)))
                    logger.info(" >> File abs_dest_path - {0}".format(str(newfile.abs_dest_path)))
                    logger.info(" >> File url           - {0}".format(str(newfile.url)))
        
                    out.append(copy.copy(newfile))                

                ##############################
                # schema parsing
                ##############################
                logger.info("Adding new files to local directory")
                schemas = self.config["schemas"]
                for schema in schemas:
                    logger.info(" >> Schema {0}".format(schema))
                    inpath  = repopath+"/"+schema
                                    
                    
                    #logger.info(" >> Inpath {0}".format(inpath))
                    outpath = os.path.abspath(os.path.join(config["site_dir"], schema.split("/")[-1].replace(".schema",".md")))
                    #logger.info(" >> Outpath {0}".format(outpath))
                  
                  
                    fin = open(inpath,"r")
                    lines = fin.readlines()
                    #logger.info(" >> NLines {0}".format(str(len(lines))))
            
                    import json
                    
                    jsonstring = ""
                    for line in lines:
                       jsonstring += line

                    jsonschema = json.loads(jsonstring)
                    
                    myconfigs = {}
                    
                    # only look at the "settings" in the schema which are system specific configurations
                    stuff = jsonschema["properties"]["settings"]["properties"]
                    
                    for key in stuff:
                        logger.info(" >> Prop - {0}".format(str(key)))
                        myconfigs.update(GetSettings(key, stuff[key]))
                        
                    # writing new markdown file
                    WriteFile(outpath, myconfigs)
                        
                    #os.system("cat "+outpath)    
                    
                    abspath = os.path.abspath(outpath)
                    
                    #logger.info(" >> OutpathAbs - {0}".format(str(abspath)))
                    
                    #os.system("ls "+config["site_dir"])
                    
                    #logger.info(" >> SiteDir - {0}".format(str(config["site_dir"])))
                    
                    fin = open(abspath,"r")
                    #logger.info(" >> Lines - {0}".format(str(len(fin.readlines()))))
                    
                    # add the new parsed file
                    #logger.info(" New Fuckin File")
        
                    # put the file in the local location from this temp directory
                    command = "cp "+abspath+" "+docs_dir
                    os.system(command)

                    #logger.info("content : {0}".format(os.system("ls "+docs_dir)))
        
                    # get the docs path
                    path = str(abspath.split("/")[-1])
                    src_dir = docs_dir
        
                    newfile = File( path, src_dir, path, use_directory_urls=True)
        
                    logger.info(" >> File src_path      - {0}".format(str(newfile.src_path)))
                    logger.info(" >> File abs_src_path  - {0}".format(str(newfile.abs_src_path)))
                    logger.info(" >> File dest_path     - {0}".format(str(newfile.dest_path)))
                    logger.info(" >> File abs_dest_path - {0}".format(str(newfile.abs_dest_path)))
                    logger.info(" >> File url           - {0}".format(str(newfile.url)))
        
                    out.append(copy.copy(newfile))
            
        return mkdocs.structure.files.Files(out)
                    
                        
