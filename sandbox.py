import os
import sys
import time

import re
import random
import datetime
import clrprint

import json

from utilities import fontColorPalette, normalizedPathJoin, nameComplies, searchNameComplies, fileCreationDate, fileInfo, strToBytes, getCurrentDateTime
import handlers





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
# TODO: generalize it to make it work.
def timeit(f):
    
    def timed(*args, **kw):
        
        if (f.__name__ == 'fsTraversal' and args[1] > 1 ):
            return( f(*args, **kw) )
        
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('[TIMING] func:%r dir:[%r] took: %2.4f sec' % \
                 (f.__name__, args[0], te-ts) )
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









# Ths core part of the file system traversal. This
# traverses all objects.
# How encountered files/directories should be handled are in the visitor classes  

     
      
def fsTraversal(root, lvl, visitor=None):
    # TODO: check this
    global timeStarted

    
    maxTime = visitor.getCriterium('maxTime', -1)
    if maxTime > 0:
       if timeStarted is None:
          timeStarted = time.perf_counter()
       else:
          # Elapsed in seconds. 
          elapsed = time.perf_counter() - timeStarted
          #if (int(elapsed)%10 == 0):
          #    print(f'>>>elapsed:{elapsed:.4f}')
          if elapsed >= maxTime: 
             raise handlers.criteriaException(-10, f'Maximum time constraint of {maxTime}s reached (elapsed:{elapsed:.4f}s).')




      
   # Maximum number of levels to delve into.
   # This is checked here; makes things easier
    mxLvl = visitor.getCriterium('maxLevels', -1)
    if mxLvl > 0:
       if lvl > mxLvl:
          return(0, 0, 0, 0, 0)

        
    try:
      path, dirs, files = next( os.walk(root) )    
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )
      if ON_TRAVERSE_ERROR_QUIT:
         return(-2, 0, 0, 0, 0)
      else:
         return(0, 0, 0, 0, 0)

        
    dirs.sort()
    files.sort()

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
        # TODO: Check this
        if not dH.ignored:
           ldc += 1
           tdc += 1 
        
           # Since not ignored, go into subdirectory and traverse it
           subDirData = fsTraversal(directoryPath, lvl+1, visitor)
           dH.setLocalCounts(subDirData[1], subDirData[2], subDirData[3], subDirData[4], visitor)
           tdc += subDirData[3]
           tfc += subDirData[4]
           if subDirData[0] < 0:
              #if (subDirData[0] != -1): # TODO: need this check?
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
def htmlExporter(root='./', templateFile='html/template1.html', criteria={}):

    if not os.path.isdir(root):
       clrprint.clrprint(f'[Error] Not such directory [{root}]', clr="red")
       return((-2, 0, 0, 0, 0))

    dTemp, fTemp, pTemp = readHTMLTemplateFile(templateFile)

    # Create visitor
    hE = handlers.HTMLExporter(dTemp, fTemp, pTemp, criteria)
    #hE = handlers.testhtmlEporter(dTemp, fTemp, pTemp, criteria)

    
    # Add starting directory to stack
    hE.stack.append({'type':'directory',
                     'collapsed':False,
                     'level':0,
                     'name':root,
                     'dname':root,
                     'html':dTemp.replace('${ID}', '-8888').replace('${DIRNAME}', root).replace('${PATH}', root).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', '0')})

    try:
      res=fsTraversal(root, 1, visitor=hE)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criteriaException. Message:', str(ce), clr='red')
      res = (ce.errorCode, -1, -1, hE.directory_count, hE.file_count) # TODO: check and fix this.
    else:
      clrprint.clrprint(f'[{getCurrentDateTime()}] Terminated.', clr='yellow')
      
    # Final merge
    clrprint.clrprint('\n\n#################################\n##    FINAL MERGE\n#################################\n', clr='yellow')
    hE.newMERGE(stk=hE.stack, final=True)

    
    ################################################################################
    # Save to file
    ################################################################################

    # if no directories and no files are in the initial folder,
    # generate an empty result for the SUBDIRECTORY template variable.  
    if res[3] == 0 and res[4] == 0:
       subD = {'html': ''}
    else:   
       subD = hE.stack.pop()

    fullTree = hE.stack.pop()
    h = pTemp.replace('${SUBDIRECTORY}', subD['html']).replace('${INITIALDIRECTORY}', root).replace('${LNDIRS}', str(res[1])).replace('${LNFILES}', str(res[2])).replace('${NDIRS}', str(res[3])).replace('${NFILES}', str(res[4])).replace('${TERMINATIONCODE}', str(res[0])).replace('${TREE}', fullTree['html']).replace("${OPENSTATE}", "open").replace("${CRITERIA}", json.dumps(criteria))
    with open('sandBoxSTACK.html', 'w', encoding='utf8') as sf:
         sf.write(h)

    clrprint.clrprint(f'\n[{getCurrentDateTime()}] Finished. Total file count:{hE.file_count} Total directory count:{hE.directory_count}. Ignored:{hE.nIgnored}', clr='yellow')


    return(res)





# Searching

# TODO: Complete me...
# NOTE: to avoid error messages when using case insensitive regex, use the following way:
#       (?i:<matching pattern>)
@timeit  
def search(root, query='.*', criteria={}):
    
    criteria['fileinclusionPattern'] = fr'({query})'
    criteria['dirinclusionPattern'] = '(' + query + ')'
    sV = handlers.SearchVisitor(query, criteria)

    clrprint.clrprint('Search results:', clr='maroon')
    try:
      fsTraversal(root, 1, visitor=sV)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='red')
    

    clrprint.clrprint(f'\nFound {sV.file_count} files and {sV.directory_count} directories. Ignored:{sV.nIgnored}\n', clr='maroon')
    return





####################### MAIN starts here#########################
    

# TODO: main guard here!

def main():
   mode = 'search'
   initialDir = "testDirectories/exampleDir0"

   # maxTime is in seconds
   traversalCriteria = { 'maxLevels':-1,
                      'maxTime': -1,
                      'fileinclusionPattern':r"",
                      'fileexclusionPattern':"",
                      'dirinclusionPattern': '',
                      'direxclusionPattern':'',
                      'minFileSize':-1,
                      'maxFileSize':-1,
                      'maxDirs':-1,
                      'maxFiles':-1,
                      'creationDateOp':'>',
                      'creationDate':'',
                      'lastModifiedDateOp':'>',
                      'lastModifiedDate':''}


   
   

   clrprint.clrprint(f"\nStarting [{mode}] mode from root [{initialDir}] with following paramters:")
   clrprint.clrprint(f"{traversalCriteria}\n", clr='yellow')
   for i in range(6):
       clrprint.clrprint(f'[{5-i}]', clr=random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'black']), end='')
       time.sleep(1)

   print(f'\n[{getCurrentDateTime()}] Started')
   time.sleep(0.5) # small delay to allow starting messages to appear (even when executed from within IDLE)




   if mode == 'export':
      htmlExporter(initialDir, 'html/template1.tmpl', traversalCriteria)
   elif mode == 'search':
        while (True):
            q = input('Give query (regular expression)>')
            if q == '':
               continue

            if q.lower()=='eof':
               print('terminating.') 
               break 

            search(initialDir, q,  traversalCriteria)

   sys.exit(-3)


# Reset timer
# TODO: check if this is correct
timeStarted = None
   
if __name__ == "__main__":
   main() 
























     

