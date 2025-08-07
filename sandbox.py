import os
import os.path
from os.path import join, commonprefix, relpath
import sys
import platform
import subprocess
import time

import re
import random

import urllib.parse
import datetime


import clrprint
import itertools
from filecmp import dircmp
from prettytable import PrettyTable


from utilities import fontColorPalette, normalizedPathJoin, nameComplies, searchNameComplies, fileCreationDate, fileInfo
import handlers





# Global flag
ON_TRAVERSE_ERROR_QUIT = False






                                              
# TODO: Replace related function in utilities with this... 
#        ==> OK fixe. Tests needed
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
    except:
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

        print('\t[TIMING] func:%r dir:[%r] took: %2.4f sec' % \
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









# GENERAL PURPOSE FUNCTION....
        
@timeit        
def fsTraversal(root, lvl, visitor=None):
    
    try:
      clrprint.clrprint(f'{lvl*"\t"}Inside {root}', clr='maroon')
      sys.stdout.flush()
      path, dirs, files = next( os.walk(root) )    
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )
      if ON_TRAVERSE_ERROR_QUIT:
         return(-2, 0, 0, "")
      else:
         return(0, 0, 0, "")

        
    dirs.sort()
    files.sort()

    lfc = 0
    for encounteredFile in files:
        sys.stdout.flush()
        
        filePath = normalizedPathJoin(root, encounteredFile)          
        fMeta = fileInfo(filePath)
        fv = handlers.File(encounteredFile, filePath, lvl, root, fMeta)
        fv.accept(visitor)
        lfc += 1
        

    ldc = 0    
    for encounteredDirectory in dirs:
        sys.stdout.flush()
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)           
        dH = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               -1,
                               -2,
                               '')
        dH.accept(visitor)
        ldc += 1
        
        # go into subdirectory and traverse it
        subDirData = fsTraversal(directoryPath, lvl+1, visitor)
        clrprint.clrprint(f'>>> [{encounteredDirectory}]: #directories:{subDirData[1]} #files:{subDirData[2]}', clr='yellow')
        dH.setLocalCounts(subDirData[1], subDirData[2])
        
        
        if subDirData[0] < 0:
               if (subDirData[0] != -1):
                   return(subDirData[0], -1, -1, '')
     

    return 0, ldc, lfc, ''








# TODO: incomplete and not running...but TOTALLY
def htmlExporter(root='./', templateFile='html/template1.html', criteria={}):

    dTemp, fTemp, pTemp = readHTMLTemplateFile(templateFile)

    # Create visitor
    hE = handlers.HTMLExporter(dTemp, fTemp, pTemp, criteria)



    
    # Add starting directory to stack
    hE.stack.append({'type':'directory',
                     'collapsed':False,
                     'level':0,
                     'name':root,
                     'dname':root,
                     'html':dTemp.replace('${ID}', '-8888').replace('${DIRNAME}', root).replace('${PATH}', root).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', '0')})

    try:
      fsTraversal(root, 1, visitor=hE)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='red')
    else:
      clrprint.clrprint('Terminated.', clr='yellow')
      
    # Final merge
    hE.newMERGE(stk=hE.stack)
    subD = hE.stack.pop()


    # Saving to file
    h = pTemp.replace('${SUBDIRECTORY}', subD['html']).replace('${INITIALDIRECTORY}', root).replace('${LNDIRS}', '-1').replace('${LNFILES}', '-5')
    with open('sandBoxSTACK.html', 'w', encoding='utf8') as sf:
         sf.write(h)

    clrprint.clrprint(f'\nFinished. Total file count:{hE.file_count} Total directory count:{hE.directory_count}', clr='yellow')
    return(0)







# TODO: Complete me...
def searchDirectories(root, criteria):
    pass





####################### FOR TESTING ONLY (END) #########################
    







dTemp, fTemp, pTemp = readHTMLTemplateFile('html/template1.html')


traversalCriteria = {'fileinclusionPattern':"",
                                  'fileexclusionPattern':"git|Rhistory|DS_Store|txt",
                                  'dirinclusionPattern': '',
                                  'direxclusionPattern':'stfolder',
                                  'minFileSize':-1,
                                  'maxFileSize':-1,
                                  'maxDirs':123,
                                  'maxFiles':55}


htmlExporter('exampleDir2', 'html/template1.html', traversalCriteria)
sys.exit(-2)












hE = handlers.HTMLExporter(dTemp, fTemp, pTemp, traversalCriteria)
initialDir = "exampleDir1"

clrprint.clrprint(f"Starting taversal with following critetia:\n{traversalCriteria}\n\n", clr='yellow')

# Add to stack
hE.stack.append({'type':'directory',
                 'collapsed':False,
                 'level':0,
                 'name':initialDir,
                 'dname':initialDir,
                 'html':dTemp.replace('${ID}', '-8888').replace('${DIRNAME}', initialDir).replace('${PATH}', initialDir).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', '0')})
# Actual traversal
try:
   fsTraversal(initialDir, 1, visitor=hE)
except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='red')
else:
      clrprint.clrprint('Terminated.', clr='yellow')
      
# Final merge
hE.newMERGE(stk=hE.stack)


#print('Stack length AFTER final merge:', len(hE.stack))
#showStack2(hE.stack)
subD = hE.stack.pop()
h = pTemp.replace('${SUBDIRECTORY}', subD['html']).replace('${INITIALDIRECTORY}', initialDir).replace('${LNDIRS}', '-1').replace('${LNFILES}', '-5')
with open('sandBoxSTACK.html', 'w', encoding='utf8') as sf:
     sf.write(h)
     
#testTraversal(initialDir)
clrprint.clrprint(f'\nFinished. File count:{hE.file_count} Directory count:{hE.directory_count}', clr='yellow')

sys.exit(-2)










     

