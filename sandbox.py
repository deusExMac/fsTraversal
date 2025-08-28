
"""
  Traverses a directory structure on disk and is capable of applying various operations on the encountered
  directories and files. This implementation has support for:
     * exporting and saving directory structure in various formats (html, json, plain text etc) based on a
       templating mechanism
     * searching for directories and files
     * comparing the contents of 2 directories and displaying their differences

  All above behaviors can be modified using criteria.
  For exports, a templating mechanism is used to format the output

  v0.5/mmt/Aug 2025
"""


import os
import sys
import time

import re
import random
import datetime
import clrprint

import json

import configparser
import argparse



from utilities import fontColorPalette, normalizedPathJoin, fileInfo, strToBytes, getCurrentDateTime
import handlers
import GUI




# Global flag
ON_TRAVERSE_ERROR_QUIT = False






                                              
# TODO: Replace related function in utilities with this... 
#        ==> OK fixed. Tests needed
def readHTMLTemplateFile(fname, dm='<!---directorytemplate--->\n', fm='<!---filetemplate--->\n', pm='<!---pagetemplate--->\n'):
    
    with open(fname, 'r', encoding='utf8') as content_file:
                 content = content_file.read()
                 
    # Next seems correct
    try: 
       dTemp = re.search(r'(?<=' + dm + r')(.*?)(?=' + fm +  '|' + pm + r')', content, re.DOTALL | re.MULTILINE).group()
    except:
       dTemp = ''
       
    # TODO: Fix me
    try:
       fTemp = re.search(r'(?<=' + fm + ')(.*?)(?='+ pm + '|' + dm + ')', content, re.DOTALL | re.MULTILINE).group()
    except:
       fTemp = ''

    try:   
       pTemp = re.search('(?<=' + pm + r')(.*$)', content, re.DOTALL | re.MULTILINE).group()
    except Exception as trEx:
       print(f'Read error: {str(trEx)}') 
       pTemp = '' 

    return(dTemp.strip(), fTemp.strip(), pTemp.strip())
    


# Works only for function traverseDirectory.

def timeit(f):
    
    def timed(*args, **kw):

        # This is done to avoid calling function for every call in
        # recursive functions
        if (f.__name__ == 'fsTraversal' and args[1] > 1 ):
            return( f(*args, **kw) )
        
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('[TIMING] func:%r took: %2.4f sec' % \
                 (f.__name__,  te-ts) )
        return result
        

    return(timed)


#####################################################
#
#
#
# Functions traversing directory structure 
#
#
#
#####################################################

# Ths core part of the file system traversal. This traverses all objects.
# How encountered files/directories should be handled are in the visitor classes  
# NOTE: the idea was to keep this function as generic as possible
#
# TODO: Looks too large. Needs to be optimized?
       
def fsTraversal(root, lvl, visitor=None):


    # TODO: check this
    global timeStarted



    ###########################################
    # Check if traversal should continue or not
    # based on the configuration
    ###########################################
    
    maxTime = visitor.getCriterium('maxTime', -1)
    if maxTime > 0:
       if timeStarted is None:
          timeStarted = time.perf_counter()
       else:
          # Elapsed in seconds. 
          elapsed = time.perf_counter() - timeStarted
          if elapsed >= maxTime: 
             raise handlers.criteriaException(-10, f'Maximum time constraint of {maxTime}s reached (elapsed:{elapsed:.4f}s).')


      
   # Maximum number of levels to delve into.
   # This is checked here; makes things easier
    mxLvl = visitor.getCriterium('maxLevels', -1)
    if mxLvl > 0:
       if lvl > mxLvl:
          return(0, 0, 0, 0, 0)

    # Update window if gui version is used
    guiWin = visitor.getCriterium('guiwindow', None)
    if guiWin is not None:
       try: 
          visitor.getCriterium('guiprogress', None).configure(text=f'{root}')
          if visitor.file_count + visitor.directory_count > 0:
             visitor.getCriterium('guistatus', None).configure(text_color='green')
             
          visitor.getCriterium('guistatus', None).configure(text=f'Found: {visitor.file_count + visitor.directory_count} (dirs:{visitor.directory_count} files:{visitor.file_count})')
          visitor.getCriterium('guiwindow', None).update_idletasks()
          visitor.getCriterium('guiwindow', None).update()
       except Exception as updEx:
          pass 



    # Get actual list of directories and files
    try:
      path, dirs, files = next(os.walk(root) )
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )
      if ON_TRAVERSE_ERROR_QUIT:
         return(-2, 0, 0, 0, 0)
      else:
         return(0, 0, 0, 0, 0)

        
    dirs.sort()
    files.sort()

    ###########################################
    # Handle files
    ###########################################
    
    lfc = 0 # local file count
    tfc = 0 # total file count until here
    for encounteredFile in files:
        sys.stdout.flush()
        
        filePath = normalizedPathJoin(root, encounteredFile)          
        fMeta = fileInfo(filePath)
        fv = handlers.File(encounteredFile, filePath, lvl, root, fMeta)
        fv.accept(visitor)
        # TODO: Check this
        if not fv.ignored: 
           lfc += 1
           tfc += 1 

           
    ###########################################
    # Handle directories
    ###########################################
    
    ldc = 0 # local directory count
    tdc = 0 # total directory count until here 
    for encounteredDirectory in dirs:
        sys.stdout.flush()
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)           
        dH = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               -1,
                               -1)
        dH.accept(visitor)
        # if not ignored, traverse into if so specified
        if not dH.ignored:
           ldc += 1
           tdc += 1 

           if not visitor.getCriterium('nonRecursive', False):
              # Since not ignored, go into subdirectory and traverse it
              subDirData = fsTraversal(directoryPath, lvl+1, visitor)
              dH.setLocalCounts(subDirData[1], subDirData[2], subDirData[3], subDirData[4], visitor)
              tdc += subDirData[3]
              tfc += subDirData[4]
              if subDirData[0] < 0:
                 return(subDirData[0], ldc, lfc, tdc, tfc)
     
    
    return 0, ldc, lfc, tdc, tfc





###########################################################################
#
#
#
# Actual implementations of above general directory structure 
# traveersal to support specific cases.
#
#
###########################################################################



# Exporting

# TODO: More tests needed
@timeit
def export(criteria={}):

    if not os.path.isdir(criteria.get('directory', 'testDirectories/testDir0')):
       clrprint.clrprint(f'[Error] Not such directory [{criteria.get("directory", "testDirectories/testDir0")}]', clr="red")
       return((-2, 0, 0, 0, 0))

    dTemp, fTemp, pTemp = readHTMLTemplateFile(criteria.get('htmlTemplate', 'templates/htmlTemplate.tmpl'))

    # Create visitor
    hE = handlers.HTMLExporter(dTemp, fTemp, pTemp, criteria)
    

    
    # Add starting directory to stack
    hE.stack.append({'type':'directory',
                     'collapsed':False,
                     'level':0,
                     'name':criteria.get('directory', 'testDirectories/testDir0'),
                     'dname':criteria.get('directory', 'testDirectories/testDir0'),
                     'html':dTemp.replace('${ID}', '-8888').replace('${DIRNAME}', criteria.get('directory', 'testDirectories/testDir0')).replace('${PATH}', criteria.get('directory', 'testDirectories/testDir0')).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', '0')})

    try:
      res=fsTraversal(criteria.get('directory', 'testDirectories/testDir0'), 1, visitor=hE)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criteriaException. Message:', str(ce), clr='red')
      res = (ce.errorCode, -1, -1, hE.directory_count, hE.file_count) # TODO: check and fix this.
    else:
      clrprint.clrprint(f'[{getCurrentDateTime()}] Terminated.', clr='yellow')
      
    # Final merge
    #clrprint.clrprint('\n\n#################################\n##    FINAL MERGE\n#################################\n', clr='yellow')
    hE.collapse(final=True)

    
    ################################################################################
    #
    # Prepare saving to file
    #
    ################################################################################

    # if no directories and no files are in the initial folder,
    # generate an empty result for the SUBDIRECTORY template variable.  
    if res[3] == 0 and res[4] == 0:
       subD = {'html': ''}
    else:   
       subD = hE.stack.pop()

    fullTree = hE.stack.pop()
    fullTree['html'] = fullTree['html'].replace('${LEVELTABS}', "")

    
    #################################################################################
    # Prepare page template 
    #################################################################################

    # Replacing external css files in page template.
    # Note: if many css files are specified, separate them with a comma (,)
    cssImports = ''
    for cssFile in criteria.get('css', '').split(','):
         cssImports = cssImports + '<link rel="stylesheet" type="text/css" ' +  'href="'+ cssFile.strip() +'"><br>'

    # These keys have non-seriazable values and hence must be removed before replacing
    # psudovariable ${CRITERIA}
    excludeKeys = ['guiwindow', 'guiprogress', 'guistatus']


    # Start replacements
    
    # Replace psudovariables related to traversal
    h = pTemp.replace('${SUBDIRECTORY}', subD['html']).replace('${TRAVERSALROOTDIR}', criteria.get('directory', 'testDirectories/testDir0')).replace('${LNDIRS}', str(res[1])).replace('${LNFILES}', str(res[2])).replace('${NDIRS}', str(res[3])).replace('${NFILES}', str(res[4])).replace('${TERMINATIONCODE}', str(res[0])).replace('${TREE}', fullTree['html']).replace("${OPENSTATE}", "open").replace("${CRITERIA}", json.dumps({k: criteria[k] for k in set(list(criteria.keys())) - set(excludeKeys)}))
   
    # Replace psudovariables related to page
    h = h.replace('${TITLE}', criteria.get('title', '')).replace('${INTROTEXT}', criteria.get('introduction', ''))
    h = h.replace('${CSS}', cssImports)

    # Should remaining ${SUBDIRECTORY} -signifying empty directories - be replaced?
    if criteria.get('replaceEmptySubdirs', 'False').lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
       h = h.replace('${SUBDIRECTORY}', '')

    # Replacements done. Save to file
    with open(criteria.get('outputFile', 'index'+'-'+getCurrentDateTime().replace(':', '-') + '.html'), 'w', encoding='utf8') as sf:
         sf.write(h)

    clrprint.clrprint(f'\n[{getCurrentDateTime()}] Total file count:{hE.file_count} Total directory count:{hE.directory_count}. Ignored:{hE.nIgnored}', clr='yellow')
  

    return(res)





# Searching
# NOTE: to avoid error messages when using case insensitive regex, use the following way:
#       (?i:<matching pattern>)
@timeit  
def search(query='', criteria={}):

    print(f'Using settings: {criteria}')
    if query=='':
       q = ' '.join(criteria.get('searchquery', []))
    else:
       q = query
       
      
    criteria['fileinclusionPattern'] = fr'({q})'
    criteria['dirinclusionPattern'] = fr'({q})'

    sV = handlers.SearchVisitor(query, criteria)

    clrprint.clrprint(f'Search results for {q}:', clr='maroon')
    try:
      fsTraversal(criteria.get('directory', 'testDirectories/testDir0'), 1, visitor=sV)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='red')
    

    clrprint.clrprint(f'\nFound {sV.file_count} files and {sV.directory_count} directories. Ignored:{sV.nIgnored}\n', clr='maroon')
    return(0, sV.directory_count, sV.file_count, sV.nIgnored)








def interactiveSearch(cfg={}):
    
     while (True):
            q = input('Give query (regular expression - use (?i:<matching pattern>) for case sensitive search)> ')
            if q == '':
               continue

            if q.lower()=='eof':
               print('terminating.') 
               break

            if cfg.get('progress', False):
               GUI.progressCommand('search', q, cfg) 
            else:
               # Simple search without progress 
               res = search(q,  cfg)
               print(res)
               





def selector(mode='export', cfg={}):
   
    
    clrprint.clrprint(f"\nStarting [{mode}] mode from root [{cfg.get('directory', 'testDirectories/testDir0')}] with following paramters:")
    clrprint.clrprint(f"{cfg}\n", clr='yellow')
    for i in range(6):
        clrprint.clrprint(f'[{5-i}]', clr=random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'black']), end='')
        time.sleep(1)

    clrprint.clrprint(f'\n[{getCurrentDateTime()}] Started', clr='yellow')
    time.sleep(0.5) # small delay to allow starting messages to appear (even when executed from within IDLE)  


    if mode == 'export':
       if not cfg.get('progress', False): 
          result = export(cfg)
          print(result)
       else:
          GUI.progressCommand('export', '', cfg)  
    elif mode == 'search':
         if cfg.get('interactive'):
            interactiveSearch(cfg)
         elif not cfg.get('progress', False): 
               result=search(query='', criteria=cfg)
               print(result)
         else:
               GUI.progressCommand('search', ' '.join(cfg.get('searchquery', [])), cfg)  
             
            


###############################################################################
#
# Main parses command line arguments
#
###############################################################################   

def main():

   cmdArgParser = argparse.ArgumentParser(description='Command line arguments', add_help=False)

   # Configuration file
   cmdArgParser.add_argument('-c', '--config', default="fsTraversal.conf")
    
   # Directory traversal related and criteria
   cmdArgParser.add_argument('-d', '--directory', default="testDirectories/testDir0")
   cmdArgParser.add_argument('-mxt', '--maxTime',  type=float, default=-1)
   cmdArgParser.add_argument('-mxl', '--maxLevels', type=int, default=-1)
   cmdArgParser.add_argument('-if', '--fileinclusionPattern', default="")
   cmdArgParser.add_argument('-xf', '--fileexclusionPattern', default="")

   cmdArgParser.add_argument('-id', '--dirinclusionPattern', default="")
   cmdArgParser.add_argument('-xd', '--direxclusionPattern', default="")
   cmdArgParser.add_argument('-fsz', '--fileSize', type=float, default=-1) # TODO: implement this
   cmdArgParser.add_argument('-mns', '--minFileSize', type=float, default=-1)
   cmdArgParser.add_argument('-mxs', '--maxFileSize', type=float, default=-1)
   cmdArgParser.add_argument('-nd', '--maxDirs', type=int, default=-1)
   cmdArgParser.add_argument('-nf', '--maxFiles', type=int,  default=-1)
   cmdArgParser.add_argument('-cdo', '--creationDateOp',  default='==')
   cmdArgParser.add_argument('-cd', '--creationDate',  default='')
   cmdArgParser.add_argument('-lmdo', '--lastModifiedDateOp',  default='==')
   cmdArgParser.add_argument('-lmd', '--lastModifiedDate',  default='')
   cmdArgParser.add_argument('-NR', '--nonRecursive', action='store_true')
   

   # SEARCH functionality related
   # If set, don't search for files. 
   cmdArgParser.add_argument('-NF', '--noFiles', action='store_true')
   cmdArgParser.add_argument('-ND', '--noDirs', action='store_true')
   cmdArgParser.add_argument('-I', '--interactive', action='store_true')

   # If set, this will display a gui showing the progress of search as it
   # proceeds.
   cmdArgParser.add_argument('-P', '--progress', action='store_true')
   
   # PAGE TEMPLATE  related
   cmdArgParser.add_argument('-t', '--htmlTemplate', default="")
   cmdArgParser.add_argument('-o', '--outputFile', default="index.html")
   # Note: if many css files are specified, enclose the arguments in double quotes "" and
   # separate individual css files with a comma (,) e.g. -s "a.css, folder/b.css, c.css"
   cmdArgParser.add_argument('-s', '--css', default="html/style.css")
   cmdArgParser.add_argument('-i', '--introduction', default="")
   cmdArgParser.add_argument('-tl', '--title', default="")
   cmdArgParser.add_argument('-e', '--urlencode', action='store_true')


   # Debugging
   # TODO: Not yet used
   cmdArgParser.add_argument('-D', '--debugmode', action='store_true')

   # REMAINDER is always the searchquery. Search query is interpreted as a regular expression.
   # NOTE: if a remainder exists, the mode is set to search.  
   cmdArgParser.add_argument('searchquery', nargs=argparse.REMAINDER, default=[])

   knownArgs, unknownArgs = cmdArgParser.parse_known_args()
   args = vars(knownArgs)
     

   print('\n\nLoading configuration settings from [', args['config'], ']\n', sep='' )
   cSettings = configparser.RawConfigParser(allow_no_value=True)
   # To make keys case sensitive (for a strange reason configparser makes all lowercase).
   cSettings.optionxform = str   
   cSettings.read(args['config'])

   # Flatten the red configuration settings and change to necessary type
   config = {}
   
   # Flatten the configuration settings while at the same time
   # change the data type for some settings.
   # TODO: Is there a better way?
   intKeys = ['maxLevels', 'maxDirs', 'maxFiles']
   floatKeys = ['fileSize', 'minFileSize', 'maxFileSize', 'maxTime']
   for s in cSettings.sections():
       for k in dict(cSettings.items(s)):
           if k in intKeys:
              config[k] = cSettings.getint(s, k, fallback=-1)
           elif k in floatKeys:
              config[k] = cSettings.getfloat(s, k, fallback=-1.0)
           else:   
              config[k] = cSettings.get(s, k, fallback='')
           

   
   # Override configuration with non-default command line settings.
   # Command line arguments have highest priority.
   # TODO: What about boolean arguments????
   config.update( (k,v) for k,v in args.items() if ((v != '' and v!=-1) or (k not in config.keys())))

   # if these options are set, don't search for directories. Currently
   # these are supported only for files
   if config['minFileSize'] >=0 or config['maxFileSize'] >=0 or config['fileSize'] >=0 or config['creationDate']!='' or config['lastModifiedDate'] != '':
      config['noDirs'] = True    

   
   mode = ''
   # If there is a searchquery of interactive mode, we do search
   if not config.get('searchquery', []) and not config.get('interactive'):
      mode = 'export'
   else:
      mode = 'search'

   # Settings set. Now, execute operation based on mode   
   selector(mode, config)
   



   

# Reset timer
# TODO: check if this is correct
timeStarted = None
   
if __name__ == "__main__":
   main() 
























     

