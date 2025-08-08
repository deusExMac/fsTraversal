import sys
from abc import ABC, abstractmethod
import os
import re
import clrprint

import random

# for stacks
from collections import deque

import urllib

from utilities import searchNameComplies, printPath, fileInfo, strToBytes



# Colors to choose from if color cycling is enabled (-c)
fontColorPalette = ['#4287f5', '#801408', '#08259c', '#4560d1', '#0a690a', '#9c5f1e', '#9c1e87', '#1313f2', '#f21313', '#34ba4a', '#19084a', '#27889c', '#317534', '#e8740e', '#000000',
                    '#1e5f85', '#2f2561', '#5c0c25', '#324530', '#f07e0c', '#e04e14', '#8f8824', '#478072', '#05998d',  '#1890a8', '#033e6b', '#0a2940', '#281a75', '#453043', '#b50e40',
                    '#fcad03', '#03a1fc', '#24b332', '#851767', '#156e82', '#8c0a0a', '#b51d39', '#232791', '#6e8c0a', '#cc7a16', '#cc4016', '#051c80', '#9e981e', '#409e1e', '#09979c', '#9c0975']



# Checks if obect name on complies to exclusion and inclusion pattern.
# nameComplies returns True, if name does NOT match exclusion regex pattern (xP)
# AND matches inclusion regex pattern (iP).
# An empty imclusion regex pattern means no inclusion pattern i.e. all
# object names are good.
#
# TODO: Has not been tested.
def nameMatches( on, xP='', iP='', lvl=-1, dbg=False ):
    #print('Exclusion pattern:', xP)
    #print('inclusion pattern:', iP)
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
              print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return(False) 

    if re.search(iP, on) is None:
       if dbg:
          print( lvl*"-", "NOT MATCHING INCLUSION:[", on, "] lvl:", lvl )
       return(False)

    return(True)





# Exception raised when *some* criteria do not hold such as maxDirs or maxFiles.
# Used to terminate traversal immediately without unfolding
# the executions.
class criteriaException(Exception):
      def __init__(self, code=-1, message=''):
          super().__init__(message)
          self.errorCode = code
          



# 1. Define the Visitable interface
class Visitable(ABC):
    
    @abstractmethod
    def accept(self, visitor):
        pass


        

# 2. Define the Visitor interface
class Visitor(ABC):
    @abstractmethod
    def visit_file(self, name, path, level, parent, finfo={}):
        pass

    @abstractmethod
    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
        pass




###################################################################
#
#  Classes for handling elements
#
###################################################################


# Concrete element classes (Files and Directories)
class File(Visitable):
    def __init__(self, name, path, level=0, parent="", finfo={}):
        self.name = name
        self.path = path
        self.level = level
        self.parent = parent
        self.fileMeta = finfo

    def accept(self, visitor):
        visitor.visit_file(self.name, self.path, self.level, self.parent, self.fileMeta)
        

class Directory(Visitable):
    def __init__(self, name, path, level, parent, ldc, lfc, subdir):
        self.name = name
        self.path = path
        self.level = level
        self.parent = parent
        self.localDirCount = ldc
        self.localFileCount = lfc
        self.subdir = subdir

    def accept(self, visitor):
        visitor.visit_directory(self.name, self.path, self.level, self.parent,  self.localDirCount, self.localFileCount, self.subdir)


    # TODO: is this correct?
    def setLocalCounts(self, ldc, lfc):
        self.localDirCount = ldc
        self.localFileCount = lfc



        
###################################################
#
#
#
# Actual visitors
#
#
#
###################################################




#####################################################################
#
#     Simple traverser. Does not make something important.
#
#####################################################################


# A concrete visitor class
class DirectoryTraverser(Visitor):
    def __init__(self, criteria={}):
        self.criteria = criteria
        self.file_count = 0
        self.directory_count = 0
        

    def visit_file(self, name, path, level, parent, finfo={}):
        
        if not nameMatches(name, self.criteria.get('exclusionRegex', ''), self.criteria.get('inclusionRegex'), level ):
           return                


        if self.criteria.get('maxFiles', -1) > 0:
           if self.file_count >= self.criteria.get('maxFiles', -1):
              raise criteriaException(-11, 'maximum number of files reached.') 
            
        if  self.criteria.get('minFileSize', '') != '':
            if int(finfo.get('size', -2)) < self.criteria.get('minFileSize', -1):
               return

        if  self.criteria.get('maxFileSize', -1) >= 0:
            if int(finfo.get('size', -2)) > self.criteria.get('maxFileSize', -1):
               return    
        
        clrprint.clrprint(f'{level*"\t"}[F-{self.file_count+1}] ', clr='green', end='')
        print(f"{name} in {parent} {finfo['size']}")
        self.file_count += 1



    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
        if not nameMatches(name, self.criteria.get('exclusionRegex', ''), self.criteria.get('inclusionRegex'), level):
           return

        if self.criteria.get('maxDirs', -1) > 0:
           if self.directory_count >= self.criteria.get('maxDirs', -1):
              raise criteriaException(-10, 'maximum number of directories reached.') 
              #return

        # counts are shown 1-based, not 0-based    
        clrprint.clrprint(f'{level*"\t"}[D-{self.directory_count+1}] ', clr='red', end='')
        print(f"{path} [level:{level}] [LD:{ldc}] [LF:{lfc}]")
        self.directory_count += 1







#####################################################################
#
#     HTML Exporter
#
#####################################################################




def makeHtmlLink(itemPath, displayAnchor, urlEncode):
    
    if urlEncode:
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8') ) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 
  





# Another concrete visitor class
class HTMLExporter(Visitor):
    
    def __init__(self, dirT, fileT, pageT, criteria):
        
        self.file_count = 0
        self.directory_count = 0

        self.dirTemplate = dirT
        self.fileTemplate = fileT
        self.pageTemplate = pageT
        self.criteria = criteria
        
        self.stack = deque()


    # This is working!
    def newMERGE(self, newD={'type':'directory', 'level':0, 'name':''}, stk=None):
    
    
          clrprint.clrprint(f"Seen: [{newD['name']}] Level[{newD['level']}]", clr='maroon')
          sDir = ''
          
            
          if len(stk) <= 0:
             return

          top = stk.pop()
          if newD['level'] >= top['level']:
             stk.append(top)
             return
                     
          
          if top['level'] - newD['level'] > 0:
             clrprint.clrprint(f"Entering collapse", clr='maroon') 
             # The new directory that WILL be added is at a higher level than to current
             # top of the list. i.e. we went one or more levels up.
             # At this point top is the last directory/file found at the deepest level.
             # Start collapsing now...

                
             # This means that the new directory encounterred
             # is at a higher level. Hence collect all at the
             # same level and merge/concatenate them
             sDir = top['html']
             while True:

                 if len(stk) <= 0:
                     break

                 # get object below top (deepest encounterred)   
                 s = stk.pop()
                 clrprint.clrprint(f"[Collapse]: popped [{s['name']}][{s['level']}]->[{s['collapsed']}] [top:{top['name']}][{top['level']}]->[{top['collapsed']}] [newD:{newD['name']}] [{newD['level']}]", clr='maroon') 
                 if s['level'] == newD['level']:
                    clrprint.clrprint(f"\t[Collapse]: stopping... [{s['level']}]", clr='yellow') 
                    top['html'] = sDir
                    
                    s['html'] = s['html'].replace('${SUBDIRECTORY}', top['html'])
                    s['collapsed'] = True
                    stk.append(s) 
                    stk.append(top)
                        
                    return
                
                
                 if s['level'] == top['level']:
                    clrprint.clrprint(f"\t[Collapse]: Adding to [{s['name']}]", clr='yellow') 
                    if s['type']=='directory': 
                       sDir = s['html'] + ' ' + sDir
                    else:
                       sDir = sDir + ' ' + s['html']
                       
                 elif top['level'] - s['level'] == 1:
                      clrprint.clrprint(f"\t[Collapse]: Replacing subdir to [{s['name']}]", clr='yellow')  
                      sDir = s['html'].replace('${SUBDIRECTORY}', sDir)
                      top = {'type':'directory', 'collapsed':True, 'level':s['level'], 'name':s['name'], 'dname':s['dname'], 'html':sDir}
                      sDir = top['html']
                      
                      
          # TODO: Do we need this?   
          return(sDir)
    





    def visit_file(self, name, path, level, parent, finfo={}, urlEncode=False):


        if not nameMatches(name, self.criteria.get('fileexclusionPattern', ''), self.criteria.get('fileinclusionPattern', '') ):
           clrprint.clrprint(f'Ignoring FILE [{name}] due to name criteria', clr='red')   
           return

        if self.criteria.get('maxFiles', -1) > 0:
           if self.file_count >= self.criteria.get('maxFiles', -1):
              raise criteriaException(-9, 'Maximum number of FILES reached.')
            
        self.file_count += 1

        nF={'type':'file',  'collapsed':False, 'level':level, 'name':path, 'dname':name, 'html':''}
        nF['html'] = self.fileTemplate.replace('${FILELINK}', makeHtmlLink(path, name, False)).replace('${FILENAME}', name).replace('${PATH}', path).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(level))
        filename, fileExtension = os.path.splitext(path)
        nF['html'] = nF['html'].replace('${FILEEXTENSION}', fileExtension[1:])

        # Add to stack
        self.stack.append(nF)
        return




    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
               
        if not nameMatches(name, self.criteria.get('direxclusionPattern', ''), self.criteria.get('dirinclusionPattern', '')):
           clrprint.clrprint(f'Ignoring DIRECTORY [{name}] due to name criteria', clr='red') 
           return


        if self.criteria.get('maxDirs', -1) > 0:
           if self.directory_count >= self.criteria.get('maxDirs', -1):
              raise criteriaException(-10, 'Maximum number of DIRECTORIES reached.')
            
        self.directory_count += 1

        # Add to stack
        nD = {'type':'directory', 'collapsed':False, 'level':level, 'name':path, 'dname':name, 'lndir':-1, 'lnfiles':-1, 'html':''}

        # See if stack can be collapsed
        self.newMERGE(nD, self.stack)

        dId = "d" + str(level) + "-" + str( random.randint(0, 1000000) )      
        nD['html'] = self.dirTemplate.replace('${ID}', dId).replace('${DIRNAME}', name).replace('${PATH}', path).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(level))
        self.stack.append(nD)
        return 
         





#####################################################################
#
#     Searching - First version.
#
#####################################################################

           
class SearchVisitor(Visitor):
      
      def __init__(self, qry, criteria):

        # TODO: Do we need this?
        #self.scanned_cound = 0
        
        self.file_count = 0
        self.directory_count = 0

        self.query = qry
        self.criteria = criteria
        
        self.matches = []



        
      def visit_file(self, name, path, level, parent, finfo={}):
            
            matchedFileName = searchNameComplies(name, self.criteria.get('fileexclusionPattern', ''), self.criteria.get('fileinclusionPattern', ''), r'/\1/', False)
            if matchedFileName == '':
               return

            fileMeta = fileInfo(path)
               
            if self.criteria.get('minFileSize', -1) >= 0:
               if int(fileMeta['size']) < self.criteria.get('minFileSize', -1): 
                   return

            if self.criteria.get('maxFileSize', -1) >= 0:
               if int(fileMeta['size']) > self.criteria.get('maxFileSize', -1): 
                   return

            self.file_count += 1

            clrprint.clrprint('[F] ', clr='green', end='')
            self.matches.append(path)
            printPath(parent, matchedFileName, '/', 'green')

            


            

      def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):

            if self.criteria.get('maxDirs', -1) > 0:
               if self.directory_count >= self.criteria.get('maxDirs', -1):
                  raise criteriaException(-10, 'Maximum number of DIRECTORIES reached.')
            
            matchedDirName = searchNameComplies(name, self.criteria.get('direxclusionPattern', ''), self.criteria.get('dirinclusionPattern', ''), r'/\1/', False)
            if matchedDirName == '':
               return

            self.directory_count += 1
            clrprint.clrprint('[D] ', clr='red', end='')
            self.matches.append(path)
            printPath(parent, matchedDirName, '/', 'red')




