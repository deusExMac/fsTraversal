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


# Global flag
ON_TRAVERSE_ERROR_QUIT = False




# Colors to choose from if color cycling is enabled (-c)
fontColorPalette = ['#4287f5', '#801408', '#08259c', '#4560d1', '#0a690a', '#9c5f1e', '#9c1e87', '#1313f2', '#f21313', '#34ba4a', '#19084a', '#27889c', '#317534', '#e8740e', '#000000',
                    '#1e5f85', '#2f2561', '#5c0c25', '#324530', '#f07e0c', '#e04e14', '#8f8824', '#478072', '#05998d',  '#1890a8', '#033e6b', '#0a2940', '#281a75', '#453043', '#b50e40',
                    '#fcad03', '#03a1fc', '#24b332', '#851767', '#156e82', '#8c0a0a', '#b51d39', '#232791', '#6e8c0a', '#cc7a16', '#cc4016', '#051c80', '#9e981e', '#409e1e', '#09979c', '#9c0975']




#colorThemes = [vibrant_colors, cool_tech_colors, warm_retro_colors, font_colors_nature_calm, vintage_warm, cool_blues_purples]

#fontColorPalette = random.choice(colorThemes)



# Prints path formated so that 
# substrings enclosed by delim in the directory or file name
# is displayed with different color.
#
# Used to display matching directory or file paths when
# doing a search.
#
# TODO: do an aligned version of printPath???

def printPath(parent, resourceName, delim, color='red'):
    # TODO: fix slash/backslash issue
    print( os.path.normpath(parent + '\\'), sep='', end='')
    parts = resourceName.split(delim)
    for idx, p in enumerate(parts):
        if idx%2 == 1:
           clrprint.clrprint(p, clr=color, end='')
        else:
           print( p, end='')
    print('')     




# Joins and creates a path string to file
# with fixed slashes/backslashes
# TODO: Should make use or .normpath(), relpath(), normcase(), abspath()???? etc.
#       See: https://docs.python.org/3/library/os.path.html#os.path.normcase
# 
def normalizedPathJoin(base, pth):
    
    if os.path.isabs(pth): 
       return(os.path.normpath(pth) )

    return( os.path.normpath(os.path.join(base, pth)) )







#
# Shortens only the filesname part of a path
#
# Check this again.
# NOTE: This  does actually rename the files IF doRename is set to False. doRename = True will
#       actually rename the file
# Example: turns /Users/abcdefghijklmnopqrstuvw/anotherDirectory/someFile.jpg to  /Users/abcdefghijklmnopqrstuvw/anotherDirectory/som...jpg
# if max_length is set to 3
# From: https://techoverflow.net/2023/10/28/trimming-down-long-directory-and-file-names-using-python/
def shortenPath(path, max_length=6, ellipsis='...', doRename=False):
    if max_length < 0:
       return(path)
             
    if os.path.isdir(path):
        base_name = os.path.basename(path)
        if len(base_name) > max_length:
            new_name = base_name[:max_length] + ellipsis
            new_path = os.path.join(os.path.dirname(path), new_name)
            if not os.path.exists(new_path):
                if doRename:
                    os.rename(path, new_path)
                    print(f"Renamed directory: {path} -> {new_name}")
                return new_path
    else:
        base_name, ext = os.path.splitext(os.path.basename(path))
        if len(base_name) > max_length:
            new_name = base_name[:max_length] + ellipsis + ext
            new_path = os.path.join(os.path.dirname(path), new_name)
            if not os.path.exists(new_path):
                if doRename:
                    os.rename(path, new_path)
                    print(f"Renamed file: {path} -> {new_name}")
                return new_path
    return path



def getRelativePath(p, root):
    commonPrefix = os.path.commonprefix([p, root])
    if commonPrefix == '':
       return ''
      
    return( os.path.relpath(p, commonPrefix) ) 





# Checks if obect name on complies to exclusion and inclusion pattern.
# nameComplies returns True, if name does NOT match exclusion regex pattern (xP)
# AND matches inclusion regex pattern (iP).
# An empty imclusion regex pattern means no inclusion pattern i.e. all
# object names are good.
#
# TODO: Has not been tested.
def nameComplies( on, xP='', iP='', dbg=False ):
    #print(xP, iP)
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
              print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return(False) 

    if re.search(iP, on) is None:
       if dbg:
          print( lvl*"-", "NOT MATCHING INCLUSION:[", on, "] lvl:", lvl )
       return(False)

    return(True)




# This is a special one, like nameComplies, but only
# for use in the searchDirectory function.
# This function not only checks for compliance - it
# also replaces the matches with a special string to
# enable formated output later on.
#
# Returns empty string if on does not comply and
# on with matches replaced if it complies
def searchNameComplies(on, xP='', iP='', matchReplacement='', dbg=False):
    
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
          print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return('')

    # Note: to avoid "global flags not at the start of the expression..." errors
    # provide case insensitive search as follows e.g.: (?i:d)
    # See https://stackoverflow.com/questions/75895460/the-error-was-re-error-global-flags-not-at-the-start-of-the-expression-at-posi
    result = re.subn(iP, matchReplacement, on)
    if result[1] > 0:
       return(result[0])

    # This means no match 
    return('')






def makeHtmlLink(itemPath, displayAnchor, urlEncode):
    
    if urlEncode:
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8') ) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 
    


#
# Taken from here:
#   https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times
#
# For an explanation see:
#   http://stackoverflow.com/a/39501288/1709587
#
def fileCreationDate(filePath):
  try:  
    epochTime = -1
    if platform.system() == 'windows':
        epochTime = os.path.getctime(filePath)
    else:
        stat = os.stat(filePath)
        try:
            epochTime = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            epochTime = stat.st_mtime

    return( datetime.datetime.fromtimestamp(epochTime).strftime("%d/%m/%Y, %H:%M:%S") )    

  except Exception as fcEx:
      print('Exception getting creation date:', str(fcEx))
      return('')  
  
 


# File metadata.
# All fields are returned as strings...
# TODO: should this be changed???
def fileInfo( filePath ):
    fInf = {}
    try:
      fInf['size']  = str(os.path.getsize(filePath))
    except Exception as fszEx:
          fInf['size'] = "-1"

    try:
       lmd = datetime.datetime.fromtimestamp(os.path.getmtime(filePath)) 
       fInf['creationdate'] = lmd.strftime("%d/%m/%Y, %H:%M:%S")
    except Exception as dtmEx:
        fInf['creationdate'] = ''

    try:
       fInf['lastmodified'] = fileCreationDate(filePath)
    except Exception as fcdEx:
        fInf['lastmodified'] = ''

    return(fInf)





# Replaces pseudovariables for file entries
# when displaying fs contents in html
def formatFile(fparent, fpath, fname, prolog, level, encUrl=False):

    
    formatedContents =  prolog.replace('${FILELINK}', makeHtmlLink(fpath, fname, encUrl)).replace('${FILENAME}', fname).replace('${FILEPATH}', fpath.replace('\\', '/')).replace('${LEVEL}', str(level)).replace('${PARENTPATH}', fparent.replace('\\', ' / '))
    fMeta = fileInfo(fpath)
    if fMeta:
       formatedContents = formatedContents.replace('${FILESIZE}', fMeta['size']).replace('${FILELASTMODIFIED}', fMeta['lastmodified'])

    
    filename, fileExtension = os.path.splitext(fpath)
    #print('Checking if file exists:', 'html/' + fileExtension + '.png')
    if os.path.exists('html/' + fileExtension[1:] + '.png'):
       formatedContents = formatedContents.replace('${FILEEXTENSION}', fileExtension[1:])
    else: 
       formatedContents = formatedContents.replace('${FILEEXTENSION}', 'ukn')    
       
        
    #print('fpath:[',  fileExtension[1:],']', sep='' )
    return( formatedContents )





# Opens a file using the default application.
def openFile(filePath):

    if sys.platform.lower() == 'win32':
       os.startfile(filePath)
    else:
        opener = "open" if sys.platform.lower() == "darwin" else "xdg-open"
        subprocess.call([opener, filePath])



#text = re.search(r'Start\n.*?End', content, re.DOTALL).group()



                                              
# TODO: Not yet working when order changes. Fix this...
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

    return(dTemp.strip(), fTemp.strip(), pTemp.strip() )
    


# Works only for function traverseDirectory.
# TODO: generalize it to make it work.
def timeit(f):
    
    def timed(*args, **kw):
        
        if (f.__name__ == 'traverseDirectory' and args[1] > 1 ):
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


import handlers






####################### FOR TESTING ONLY (START) #########################

from collections import deque

theSTACK = deque()

def showStack2(stk=theSTACK):
         lst = []
         pos=1
         clrprint.clrprint('Total of', len(stk), 'items in stack.', clr='yellow')
         while  len(stk) > 0:
                sv = stk.pop()
                lst.append(sv)
                clrprint.clrprint(f"{pos}) [{sv['name']}] [{sv['level']}]", clr='yellow')
                pos +=1

         for i in lst[::-1]:
             stk.append(i)



def showStack(stk=theSTACK):
         lst = []
         pos=1
         clrprint.clrprint('Total of', len(stk), 'items in stack.', clr='yellow')
         while  len(stk) > 0:
                sv = stk.pop()
                lst.append(sv)
                print('______' + str(pos) + '______\n', end='')
                print(sv)
                print('_________')
                pos +=1

         for i in lst[::-1]:
             stk.append(i)




    
              
    

def newMERGE(newD, stk):
    
    
    clrprint.clrprint(f"Seen: {newD['name']}", clr='maroon')
    sDir = ''
    
    while True:
          if len(stk) <= 0:
             break

          top = stk.pop()
          if newD['level'] >= top['level']:
             stk.append(top)
             return
            
          if newD['level'] == 0:
             print('POPPED:', top)
             
          
          if top['level'] - newD['level'] > 0:
             if newD['level'] == 0:
                clrprint.clrprint(f"triggering merging.....", clr='yellow')
                
             # This means that the new directory encounterred
             # is at a higher level. Hence collect all at the
             # same level and merge/concatenate them
             sDir = top['html']
             while True:

                 if len(stk) <= 0:
                     break
                    
                 s = stk.pop()
                 if s['level'] == top['level']:
                    if s['type']=='directory': 
                       sDir = s['html'] + ' ' + sDir
                    else:
                       sDir = sDir + ' ' + s['html']
                       
                 elif top['level'] - s['level'] == 1:
                      sDir = s['html'].replace('${SUBDIRECTORY}', sDir)
                      stk.append({'type':'directory', 'level':s['level'], 'name':s['name'], 'dname':s['dname'], 'html':sDir})
                      showStack2()
                      break
            
             #break
          
    
    if newD['level'] <= 0:
       print('++++++++++++++++++++\n', s, '++++++++++++++++++++++\n')
       # This is just to get/return sDir when everything is done.
       stk.append({'level':s['level'], 'name':s['name'], 'dname':s['dname'], 'html':sDir})
             
    return(sDir)






    
def testTraversal(d='exampleDir3'):
    #theSTACK.append({'level':0, 'name':d, 'dname':d, 'html':''})
    fsTraversal(d, 1)
    showStack2()
    newMERGE({'type':'directory', 'level':0, 'name':''}, theSTACK)
    showStack2()
    fp = theSTACK.pop()
    
    clrprint.clrprint('[', fp, ']', clr='maroon')
    htmlFullPage = pTemp.replace('${SUBDIRECTORY}', fp['html']).replace('${INITIALDIRECTORY}', d)
    # not working.
    htmlFullPage=htmlFullPage.replace('${SUBDIRECTORY}', '')
    
    with open('sandBoxSTACK.html', 'w', encoding='utf8') as sf:
     sf.write(htmlFullPage) 
    
    #showStack(theSTACK)



    
        
        
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

    

    
    for encounteredFile in files:
        
        sys.stdout.flush()
        
        
        filePath = normalizedPathJoin(root, encounteredFile)          
        fMeta = fileInfo(filePath)

        # Next in file handler
        nF={'type':'file',  'level':lvl, 'name':filePath, 'dname':encounteredFile, 'html':''}
        nF['html'] = fTemp.replace('${FILELINK}', makeHtmlLink(filePath, encounteredFile, False)).replace('${FILENAME}', encounteredFile).replace('${PATH}', filePath).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(lvl))
        filename, fileExtension = os.path.splitext(encounteredFile)
        nF['html'] = nF['html'].replace('${FILEEXTENSION}', fileExtension[1:])
        theSTACK.append(nF)

        #fv = handlers.File(encounteredFile, filePath, lvl, root, fMeta)
        #fv.accept(visitor)
        
        
        


        
    for encounteredDirectory in dirs:
        sys.stdout.flush()
        
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)
        #clrprint.clrprint('Processing:', directoryPath, f' total of {len(theSTACK)}', clr='yellow')


        # Next in directory handler
        nD = {'type':'directory', 'level':lvl, 'name':directoryPath, 'dname':encounteredDirectory, 'lndir':-1, 'lnfiles':-1, 'html':''}
        newMERGE(nD, theSTACK)

        dId = "d" + str(lvl) + "-" + str( random.randint(0, 1000000) )      
        nD['html'] = dTemp.replace('${ID}', dId).replace('${DIRNAME}', encounteredDirectory).replace('${PATH}', directoryPath).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(lvl))
        theSTACK.append(nD)
        
        showStack2()
        #lnDirs += 1       
          
        
        # The semantics in order: 
        # total number of directories, total number of files, local number of dirs, local number of files,
        # formatted display of subdirectory 
        #subDirData = (0,0,0, "xxx")
        #if recursive:

        '''
        dH = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               -1,
                               -2,
                               '')
        dH.accept(visitor)
        '''
        
            # go into subdirectory and traverse it
        subDirData = fsTraversal( directoryPath, lvl+1, visitor)  
        if subDirData[0] < 0:
               if (subDirData[0] != -1):
                   return(subDirData[0], -1, -1, '')
     

    return 0, -1, -1, ''



####################### FOR TESTING ONLY (END) #########################
    

#
# TODO: 1) Do we need epilog and fepilog??? 2) Check PSEUDOs - check DIRLINK etc
#       3) Change name to indicate formated output 
#tmpH = ''

def ABSTRACTtraverse(root=".//", lvl=1, recursive = True, maxLevel=-1,
                      encodeUrl=False,                      
                      vrb=False,
                      objVisitor=None):
    

  
   
   try: 
    if maxLevel > 0:
       if lvl > maxLevel:
          #objVisitor.tmpHtml = ''
          return(0, 0, 0, "")


    # Gather directories and files in directory identified by
    # path root.
    #
    # In case of error, quit returning special status
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


    # sort directory and files
    dirs.sort()
    files.sort()

    
    
    lnDirs = 0 # local number of directories i.e. number of directories in directory NOT including its subdirs
    lnFiles = 0 # local number of files i.e. number of files in directory NOT including files in its subdirs
    #objVisitor.tmpHtml = ''
    #tmpH = ''
    
    #objVisitor.reset() 
    #formatedContents = "" # Formated directory and files

    # At each level, a different color for directory names 
    #rClr = random.choice(fontColorPalette)

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    tmpH = ''
    for encounteredDirectory in dirs:
        sys.stdout.flush()
        
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
        #dirList.append(directoryPath)

        
        lnDirs += 1       
        # TODO: fix objVisitor.htmlPage which is wrong...
        #print(objVisitor.htmlPage)
        
        
        
        # The semantics in order: 
        # total number of directories, total number of files, local number of dirs, local number of files,
        # formatted display of subdirectory 
        subDirData = (0,0,0, "xxx")
        if recursive:

            v = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               -1,
                               -2,
                               '')
            v.accept(objVisitor)
        
            # go into subdirectory and traverse it
            subDirData = ABSTRACTtraverse( directoryPath, lvl+1, recursive, maxLevel,
                                              encodeUrl,
                                              vrb, objVisitor)  

            # Upate total number of directories and files that will
            # be propagated upwards.
            # subDirData[0] is the status message
            #if subDirData[0] >= 0:
            #   nDirs += subDirData[1]
            #   nFiles += subDirData[2]
            #else:
            if subDirData[0] < 0:
               if (subDirData[0] != -1):
                   return(subDirData[0], lnDirs, lnFiles, '')

        '''
        v = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               subDirData[1],
                               subDirData[2],
                               subDirData[3])
        v.accept(objVisitor)
        '''
        
        
        
        '''
        # Prepare the entry for one single directory encountered
        dId = "d" + str(lvl) + "-" + str( random.randint(0, 1000000) )
        formatedContents = formatedContents + prolog.replace("${ID}", dId).replace("${DIRLINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeUrl) ).replace('${DIRNAME}', encounteredDirectory).replace('${LEVEL}', str(lvl)).replace('${DIRPATH}', directoryPath).replace('${PARENTPATH}', root.replace('\\', ' / ')).replace('${SUBDIRECTORY}', subDirData[4])
        formatedContents = formatedContents.replace('${LNDIRS}', str(subDirData[2])).replace('${NDIRS}', str(subDirData[0]) if subDirData[0] >=0 else '0' )
        formatedContents = formatedContents.replace('${LNFILES}', str(subDirData[3])).replace('${NFILES}', str(subDirData[1]) )
        formatedContents = formatedContents.replace('${RLVLCOLOR}',  rClr)
        #formatedContents = formatedContents + epilog
        #for k in range(10):
        dirList.append({'id':dId, 'name':encounteredDirectory})
        '''
        
        
    
    
    #objVisitor.tmpHtml = tmpH
    
    # Process all files in current directory
    for encounteredFile in files:
        sys.stdout.flush()
        
        
        filePath = normalizedPathJoin(root, encounteredFile)          
 
        #clrprint.clrprint(filePath, clr="yellow")
        lnFiles += 1

        
        fMeta = fileInfo(filePath)
        v = handlers.File(encounteredFile, filePath, lvl, root, fMeta)
        v.accept(objVisitor)
        
        '''
        fileList.append(filePath)

        formatedContents = formatedContents + formatFile(root, filePath, encounteredFile, fprolog, lvl, encodeUrl)
        '''

    
    # Return data to upper directory
    #
    # The tuple returned has the following data
    # nDirs: total directories up to this point, nFiles: total files up to this point
    # lnDirs:  number of directories in this directory only, lnFiles: number of files
    # in this directory only, formatedContents: complete formated content up to this
    # point
    return 0, lnDirs, lnFiles, ''

   except KeyboardInterrupt:
       print('Keyboard interrupt. Terminating')
       #sys.exit(-3)
       return(0, 0, 0, '')
   except handlers.criteriaException as ce:
       raise handlers.criteriaException(ce.errorCode, str(ce)) 





dTemp, fTemp, pTemp = readHTMLTemplateFile('html/template1.html')

'''
defDT = handlers.DirectoryTraverser({'dirinclusionPattern':"",
                                  'direxclusionPattern':r"git|Rhistory|DS_Store|stfolder",
                                  'minFileSize':-1,
                                  'maxFileSize':-1,
                                  'maxDirs':-1,
                                  'maxFiles':-1})

'''




hE = handlers.HTMLExporter(dTemp, fTemp, pTemp, {'fileinclusionPattern':"",
                                  'fileexclusionPattern':"git|Rhistory|DS_Store",
                                  'dirinclusionPattern': '',
                                  'direxclusionPattern':'stfolder',
                                  'minFileSize':-1,
                                  'maxFileSize':-1,
                                  'maxDirs':-1,
                                  'maxFiles':-1})




initialDir = "exampleDir6"

testTraversal(initialDir)
clrprint.clrprint('Finished.', clr='yellow')
sys.exit(-2)





try:
    
  rootData = ABSTRACTtraverse(root=initialDir, maxLevel=3, objVisitor=hE)
except handlers.criteriaException as ce:
    clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='yellow')
    #sys.exit(-7)
else:    
    print(f'Terminated with {rootData[0]}. Root directory: [LD:{rootData[1]}] [LF:{rootData[2]}]')
    print('######################################################')
    print(f'Total directories:', hE.directory_count)
    print(f'Total files:', hE.file_count)
    #sys.exit(-2)

import io

clrprint.clrprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', clr='yellow')
hE.displayStack()
clrprint.clrprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', clr='yellow')

#rrr = hE.stack.pop()
'''
htmlContent = pTemp.replace('${SUBDIRECTORY}', rootData[3]).replace('${INITIALDIRECTORY}', initialDir).replace('${LNDIRS}', str(rootData[1])).replace('${LNFILES}', str(rootData[2]))
htmlContent = htmlContent.replace('${NDIRS}', str(hE.directory_count)).replace('${NFILES}', str(hE.file_count))

print('Saving....')
with open('sandBox.html', 'w', encoding='utf8') as f:
               f.write(htmlContent)

'''

print('Saving stack...')
print('Total of [', len(hE.stack), '] items in stack.', sep='')
h = hE.unwindStack()
h = pTemp.replace('${SUBDIRECTORY}', h).replace('${INITIALDIRECTORY}', initialDir).replace('${LNDIRS}', '-1').replace('${LNFILES}', '-5')
#htmlContent = htmlContent.replace('${NDIRS}', str(hE.directory_count)).replace('${NFILES}', str(hE.file_count))

with open('sandBoxSTACK.html', 'w', encoding='utf8') as sf:
     sf.write(h) 
     

