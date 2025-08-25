import os
import os.path
from os.path import join, commonprefix, relpath

from pathlib import Path

import sys
import platform
import subprocess
import time

import re
import random

import urllib.parse
import datetime
from dateutil.parser import parse

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



def getCurrentDateTime(tz=None):
    return(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))


def normalizeDateTime(td):
    return(parse(td).date())


# Prints path formated so that 
# substrings enclosed by delim in the directory or file name
# is displayed with different color.
#
# Used to display matching directory or file paths when
# doing a search.
#
# TODO: Is this working?????? do an aligned version of printPath???

def printPath(parent, resourceName, delim, color='red'):
    # TODO: fix slash/backslash issue
    print( os.path.normpath(parent + os.sep), sep='', end='')
    print(os.sep, end='')
    parts = resourceName.split(delim)
    
    for idx, p in enumerate(parts):
        if idx%2 == 1:
           clrprint.clrprint(p, clr=color, end='')
        else:
           print(p, end='')
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




def shortenPathPrefix(file_path, length):
     """Split the path into separate parts, select the last 
     'length' elements and join them again"""
     return Path(*Path(file_path).parts[-length:])


def shortenFullPath(fullPath, length):
    path = os.path.normpath(fullPath)
    prts = path.split(os.sep)
    if len(prts) >=2*length:
       return(os.sep.join(prts[:length+1]) + '...' + os.sep.join(prts[-length:])) 

    return(fullPath) 




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

    return(datetime.datetime.fromtimestamp(epochTime))    

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
       fInf['lastmodified'] = lmd #.strftime("%d/%m/%Y, %H:%M:%S")
    except Exception as dtmEx:
        fInf['lastmodified'] = ''

    try:
       # TODO: is this correct? 
       fInf['creationdate'] = fileCreationDate(filePath)
    except Exception as fcdEx:
        fInf['creationdate'] = ''

    return(fInf)



def strToBytes( amount ):
    if amount.lower().endswith('k'):
        try:
          sz = int( amount[:-1] )*1024
        except Exception as convEx:
          return(-3)
        
    elif amount.lower().endswith('m'):
       try:
          sz = int( amount[:-1] )*1024*1024
       except Exception as convEx:
          return(-3)

    elif amount.lower().endswith('g'):
       try:
          sz = int( amount[:-1] )*1024*1024*1024
       except Exception as convEx:
          return(-3)
    elif amount.lower().endswith('t'):
       try:
          sz = int( amount[:-1] )*1024*1024*1024*1024
       except Exception as convEx:
          return(-3)
    else:
         try:
          sz = int(amount)
         except Exception as convEx:
            return(-3) 
        
    return(sz)





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
def readHTMLTemplateFile(fname, dm, fm, pm):
    
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



#
# TODO: 1) Do we need epilog and fepilog??? 2) Check PSEUDOs - check DIRLINK etc
#       3) Change name to indicate formated output 
@timeit
def traverseDirectory(root=".//", lvl=1, recursive = True, maxLevel=-1,
                      exclusionPattern="", inclusionPattern="",
                      dirList=None, fileList=None,
                      encodeUrl=False,                      
                      prolog="", 
                      fprolog="",  vrb=False):
    
    
    
    if maxLevel > 0:
       if lvl > maxLevel: 
          return(-1, 0, 0, 0, "")


    # Gather directories and files in directory identified by
    # path root.
    #
    # In case of error, quit returning special status
    try:      
      path, dirs, files = next( os.walk(root) )    
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )
      if ON_TRAVERSE_ERROR_QUIT:
         return(-2, 0, 0, 0, "")
      else:
         return(0, 0, 0, 0, "") 


    # sort directory and files
    dirs.sort()
    files.sort()

    
    nDirs  = 0 # TOTAL number of directories
    nFiles = 0 # TOTAL number of files
    lnDirs = 0 # local number of directories i.e. number of directories in directory NOT including its subdirs
    lnFiles = 0 # local number of files i.e. number of files in directory NOT including files in its subdirs
    formatedContents = "" # Formated directory and files

    # At each level, a different color for directory names 
    rClr = random.choice(fontColorPalette)

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
         
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern): 
           continue
            
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
        #dirList.append(directoryPath)

        nDirs +=1
        lnDirs += 1       
        
        # The semantics in order: 
        # total number of directories, total number of files, local number of dirs, local number of files,
        # formatted display of subdirectory 
        subDirData = (0,0,0,0, "")
        if recursive:
            # go into subdirectory and traverse it
            subDirData = traverseDirectory( directoryPath, lvl+1, recursive, maxLevel,
                                              exclusionPattern, inclusionPattern,
                                              dirList, fileList,
                                              encodeUrl,
                                              prolog,  
                                              fprolog,  vrb)  

            # Upate total number of directories and files that will
            # be propagated upwards.
            # subDirData[0] will also carry any error encountered
            # during traversal of subdirectories.
            if subDirData[0] >= 0:
               nDirs += subDirData[0]
               nFiles += subDirData[1]

        # Prepare the entry for one single directory encountered
        dId = "d" + str(lvl) + "-" + str( random.randint(0, 1000000) )
        formatedContents = formatedContents + prolog.replace("${ID}", dId).replace("${DIRLINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeUrl) ).replace('${DIRNAME}', encounteredDirectory).replace('${LEVEL}', str(lvl)).replace('${DIRPATH}', directoryPath).replace('${PARENTPATH}', root.replace('\\', ' / ')).replace('${SUBDIRECTORY}', subDirData[4])
        formatedContents = formatedContents.replace('${LNDIRS}', str(subDirData[2])).replace('${NDIRS}', str(subDirData[0]) if subDirData[0] >=0 else '0' )
        formatedContents = formatedContents.replace('${LNFILES}', str(subDirData[3])).replace('${NFILES}', str(subDirData[1]) )
        formatedContents = formatedContents.replace('${RLVLCOLOR}',  rClr)
        #formatedContents = formatedContents + epilog
        #for k in range(10):
        dirList.append({'id':dId, 'name':encounteredDirectory})
        
        
    
    
    
    # Process all files in current directory
    for encounteredFile in files:

        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           continue
        
        filePath = normalizedPathJoin(root, encounteredFile)          
 
        nFiles +=1
        lnFiles += 1
        
        fileList.append(filePath)

        formatedContents = formatedContents + formatFile(root, filePath, encounteredFile, fprolog, lvl, encodeUrl)


    
    # Return data to upper directory
    #
    # The tuple returned has the following data
    # nDirs: total directories up to this point, nFiles: total files up to this point
    # lnDirs:  number of directories in this directory only, lnFiles: number of files
    # in this directory only, formatedContents: complete formated content up to this
    # point
    return nDirs, nFiles, lnDirs, lnFiles, formatedContents









# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def jsonTraverseDirectory(root=".//", lvl=1, recursive = True, maxLevel=-1,
                          exclusionPattern="", inclusionPattern="", encodeUrl=False):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          #if vrb: 
             #print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return({})
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return ({})
    

    directoryContents = {}
    

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
        
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern): 
           continue
            
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
    
        #directoryPath = normalizedPathJoin(root, encounteredDirectory)
       
        if recursive:
            directoryContents[encounteredDirectory]  = jsonTraverseDirectory( directoryPath,
                                                                              lvl+1,
                                                                              recursive,
                                                                              maxLevel,
                                                                              exclusionPattern,
                                                                              inclusionPattern,
                                                                              encodeUrl)
                                              
            
            
            
    # Process all files in current directory
    
    fileList = []
    for encounteredFile in files:
        
        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           continue
        
        filePath = normalizedPathJoin(root, encounteredFile)  

        try:
           fMeta = fileInfo(filePath)
           fileList.append( {'path':encounteredFile,
                             'size':fMeta['size'],
                             'lastmodified':fMeta['lastmodified'],
                             'creationdate': fMeta['creationdate']
                             })
        except Exception as szEx:
           # TODO: specialize exceptions. Might get a "File name too long"
           # exception
           ileList.append( {'path':encounteredFile,
                            'size':'-1',
                            'lastmodified':'---',
                            'creationdate': '---'}) 

    directoryContents['__files'] = fileList
    
    return directoryContents







# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def searchDirectories(root=".//", lvl=1, recursive = True, maxLevel=-1, 
                      exclusionPattern="", inclusionPattern="", 
                      matchDirectories=True, matchFiles=True, fileCriteria={},
                      matchingPaths=[], scannedCount=0, matchCount=0, vrb=False):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print(f'Current Level {lvl} greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return((-1, scannedCount, matchCount))
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except Exception as walkExc:
      print('[WALK ERROR]', str(walkExc))
      if ON_TRAVERSE_ERROR_QUIT:
         return ( (-2, scannedCount, matchCount) ) 
      else:    
         return ( (0, scannedCount, matchCount) )

    
    
    #print('Entering searchDirectories with matchCount:', matchCount)
    nScanned = scannedCount
    nFound = matchCount

    try:
        
      # Process all directories in current directory.
      # If recursive is True, traverse into each directory
      # Does a depth first search (DFS) approach
      for encounteredDirectory in dirs:
         
        nScanned += 1 
        if vrb:
            print( lvl*"-", nScanned, ')', normalizedPathJoin(root, encounteredDirectory), "lvl:", lvl )

        directoryPath = normalizedPathJoin(root, encounteredDirectory)
        #print(f'\tChecking {directoryPath}')
        parentPath = os.path.dirname( directoryPath )

        if matchDirectories:
           matchedDirName = searchNameComplies(encounteredDirectory, exclusionPattern, inclusionPattern, r'/\1/', False)
           if matchedDirName == '':
              if vrb:
                 print('IGNORING DIRECTRORY', encounteredDirectory)              
           else:           
              nFound += 1
              matchingPaths.append(directoryPath)
              print('\t', nFound, ') ', sep='', end='')
              clrprint.clrprint('[D] ', clr='green', end='')
              printPath(parentPath, matchedDirName, '/', 'green')
                  
        if recursive:
            sts, nScanned, nFound = searchDirectories( directoryPath, lvl+1,
                                                  recursive, maxLevel, 
                                                  exclusionPattern, inclusionPattern, 
                                                  matchDirectories, matchFiles, fileCriteria,
                                                  matchingPaths, nScanned, nFound, vrb )
                                                
            # TODO: make this and                 
            if sts < 0:
               if sts != -1:
                  return( sts, nScanned, nFound )
                
            
            
      # Process all files in current directory
      fileList = []
      if matchFiles:
        for encounteredFile in files:

          nScanned += 1
          fullPath = normalizedPathJoin(root, encounteredFile)
          if vrb:
            print( lvl*"-", nScanned, ')', fullPath, "lvl:", lvl )

          parentPath = os.path.dirname( fullPath )
          matchedFileName = searchNameComplies(encounteredFile, exclusionPattern, inclusionPattern, r'/\1/', False)
          if matchedFileName == '':
             continue
          else:
            # Match found.  
            # Check file metadata criteria...
            if fileCriteria:            
               fileMeta = fileInfo(fullPath)
               
               if fileCriteria.get('minfilesize', -1) >= 0:
                if int(fileMeta['size']) < fileCriteria.get('minfilesize', -1): 
                  continue

               
               if  fileCriteria.get('maxfilesize', -1) > 0:
                if int(fileMeta['size']) > fileCriteria.get('maxfilesize', -1):
                  #print(f"{fullPath} Does not meed maxfilesize: {fileCriteria.get('maxfilesize', -1)}. Actual:{fileMeta['size']}" )  
                  continue 
               
            nFound += 1
            matchingPaths.append(fullPath)
            print('\t', nFound, ') ', sep='', end='')
            clrprint.clrprint('[F] ', clr='red', end='')
            printPath( parentPath, matchedFileName, '/', 'red' ) 

    except KeyboardInterrupt:
           print('\n\nKeyboard interrupt seen. Stopping...')
           return( -5, nScanned, nFound ) # Control-C seen. Propagate error while recursion is unwinded.

            
    return 0, nScanned, nFound






# Code section below is related to finding the differences between two directories in terms of files and directories
# Seems to work. More testing needed though.
#
# 18/07/2024: TEST THIS!!!
#

def defaultDH(l=1, side='right', path='') -> None:
    """
      Default Directory Handler displaying only formatted side and path of Directories
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """
    print('\t'*l, f'[{l}][D] [{side} only] {path}', sep='')



def defaultFH(l=1, side='right', path=''):
    """
      Default File Handler displaying only formatted side and path of Files
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """  
    print('\t'*l, f'[{l}][F] [{side} only] {path}', sep='')






def customDirectoryHandler(l=1, side='right', path='') -> None:
    print('\t'*l, f'[{l}][{side}] {path}', sep='')






def matches(mF, fname) -> bool:
    """
      Returns if the file name matches pattern specified in mF
      
      :param mF: regular expression a file name must match. Empty string for no filter.
      :param fname: file name to check regular expression agains. NOTE: No full path expected
      :return: Boolean indicating if file name matches pattern
    """
    
    if mF == '' or mF is None:
       return(True)

    if re.search(mF, fname) is not None:  
       return(True)
      
    return(False)  




def tabularDisplay(ld, l, rd, r, c):
     if (not l['D']) and (not r['D']):
         clrprint('All directories in common.', clr='g')
     else:   
      table = PrettyTable()
      table.align = "l"
      titles = ('LEFT','RIGHT')
      table.title = 'DIRECTORIES'
      table.field_names = ["only in " + ld, "only in " + rd]
      for d in itertools.zip_longest(l['D'], r['D'],fillvalue=""):
          table.add_row([ getRelativePath( shortenPath(d[0], 22, '...'), ld), getRelativePath(shortenPath(d[1], 33, '...'), rd)]) 

      clrprint.clrprint(table, clr='y')


      if l['F'] or r['F']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'FILES'
         tableF.field_names = ["only in " + ld, "only in " + rd]

         for f in itertools.zip_longest(l['F'], r['F'],fillvalue=""): 
             tableF.add_row([ getRelativePath( shortenPath(f[0], 50, '...'), ld ), getRelativePath( shortenPath(f[1], 50, '...'), rd)])
      
         clrprint.clrprint(tableF, clr='g') 


      if c['D']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'COMMON DIRECTORIES'
         tableF.field_names = ["relative paths"]
         for f in c['D']: 
             tableF.add_row([ getRelativePath( shortenPath(f, 45, '...'), ld )])

         clrprint.clrprint(tableF, clr='m')    


      if c['F']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'COMMON FILES'
         tableF.field_names = ["relative paths"]
         for f in c['F']: 
             tableF.add_row([ getRelativePath( shortenPath(f, 45, '...'), ld )])

         clrprint.clrprint(tableF, clr='m')   



def dirDifference(L_dir, R_dir, lvl=1, mxLvl=-1, dirOnly=False, matchFilter='', dirHandler=defaultDH, fileHandler=defaultFH, verbose=False, progress=None):

  """
       Traverses recursively directories and calculates the differences (in terms of directories and files) between
       two directories.
      
      :param L_dir: One directory path- left side
      :param fname: Second directory path - right side
      :param lvl: Current level of traversal
      :param dirOnly: If True calculates differences for directories only. Otherwise, also files are taken
      into consideration.
      :param matchFilter: regular expression directory and file names must match. Empty string indicates no filter.
      :param dirHandler: Function to call for each directory encountered
      :param fileHandler:Function to call for each file encountered 
      :return: tuple indicatins status, total objects matching, list of objects only in left side, list of objects only in right side
  """
  
        
  localTotal = 0
  prefix = '\t'*lvl
  L_only, R_only, C_only = {'D':[], 'F':[]}, {'D':[], 'F':[]}, {'D':[], 'F':[]}

  if mxLvl > 0:
     if lvl > mxLvl:
        return (0, localTotal, L_only, R_only, C_only) 


  
  verbose and print('\t'*lvl, f'{40*"+"}\n', '\t'*lvl, f'[L:{lvl}] Comparing ', f'[{L_dir}] ', 'to ', f'[{R_dir}]\n', sep='') 
  

  if L_dir == R_dir:
     verbose and print(f"{L_dir} / {R_dir}")   
     return(-2, 0, L_only, R_only, C_only)

  try:  
    dcmp = dircmp(L_dir, R_dir)
    if not dcmp:
       return(-7, 0, L_only, R_only, C_only)   
          
    L_only['D'] = [ join(L_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.left_only if  os.path.isdir( join(L_dir, f)  ) and matches(matchFilter, f)  ]
    R_only['D'] = [ join(R_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.right_only if os.path.isdir( join(R_dir, f)  ) and matches(matchFilter, f)]
    # for common files, take relative paths
    C_only['D'] = [ f  for f in dcmp.common_dirs if matches(matchFilter, f)  ]
    
    if not dirOnly:       
       L_only['F'] = [ join(L_dir, f)  + ' [L:'+str(lvl)+']' for f in dcmp.left_only if not os.path.isdir( join(L_dir, f)  ) and matches(matchFilter, f) ]
       R_only['F'] = [ join(R_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.right_only if not os.path.isdir( join(R_dir, f)  ) and matches(matchFilter, f)]
       # We use the left-sided root as the prefix for common files.
       # TODO: relative here too? 
       C_only['F'] = [ join(L_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.common_files if matches(matchFilter, f)  ]

    
    
    # TODO: This is not correct. Recheck and redesign it   
    if dirHandler:  
       for d in L_only['D']:
           dirHandler(lvl, 'left', d)
           
       for d in R_only['D']:
           dirHandler(lvl, 'right', d)

       for cd in  dcmp.common_dirs:
           dirHandler(lvl, 'common', cd)    


    if (not dirOnly) and fileHandler:
       for f in L_only['F']:    
           fileHandler(lvl, 'left', f)
       
       for f in R_only['F']:    
           fileHandler(lvl, 'right', f) 

       for cf in  dcmp.common_files:
           fileHandler(lvl, 'common', cf)          

    
    
    verbose and print('\t'*lvl + f'l_only={len(L_only["D"]) + len(L_only["F"])} r_only={len(R_only["D"]) + len(R_only["F"])} common_dirs={len(dcmp.common_dirs)} common_files={len(dcmp.common_files)}')  
    
    localTotal = len(L_only['D']) + len(L_only['F']) + len(R_only['D']) + len(R_only['F']) + len(dcmp.common_dirs) + len(dcmp.common_files)

    
    
    # Handle directories having common names. I.e. traverse these and
    # find their differences
    #
    # TODO: optimize next two lines?
    
    cd =  C_only['D'].copy()
    C_only['D'] = [ join(L_dir, f) for f in cd]
    for sub_dir in cd:
                 
        s, lt, new_L, new_R, new_C = dirDifference(join(L_dir, sub_dir), join(R_dir, sub_dir), (lvl+1), mxLvl, dirOnly, matchFilter, dirHandler, fileHandler, verbose, progress)

        if s < 0:
           return(s, localTotal, L_only, R_only, C_only)
      
        L_only['D'].extend(new_L['D'])
        if not dirOnly:
           L_only['F'].extend(new_L['F'])

        R_only['D'].extend(new_R['D'])
        if not dirOnly:
           R_only['F'].extend(new_R['F'])

        C_only['D'].extend( new_C['D'] )
        if not dirOnly:
           C_only['F'].extend( new_C['F'] )
        
        verbose and print('\t'*lvl,  f'>> # items from level below {lt}', sep='')  
        localTotal = localTotal + lt

    verbose and print('\t'*lvl + f'returning {localTotal}\n', '\t'*lvl, f'{40*"-"}', sep='')           
    return(0, localTotal, L_only, R_only, C_only)

  except KeyboardInterrupt as kI:
         #
         # Do a full/cascading unrolling. raising exceptions until
         # top level is reached; from which it is returned
         #
         print(f'\n\n[L:{lvl}] Interupted in {L_dir} {R_dir}. Terminating: Total:{localTotal}')
         if lvl > 1:
            raise kI
         else:
            return( -1, localTotal, L_only, R_only, C_only )  
         

