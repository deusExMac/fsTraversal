import sys
from abc import ABC, abstractmethod
import os
import re
import clrprint

import random

# for stacks
from collections import deque

import urllib


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




# 3. Concrete element classes (Files and Directories)
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

    def setHTML(self, visitor):
        visitor.setHTML(self.name, self.path, self.level, self.parent,  self.localDirCount, self.localFileCount, self.subdir)
        
###################################################
#
#
#
# Actual visitors
#
#
#
###################################################


# 4. Concrete visitor class
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




def htmlLink(itemPath, displayAnchor, urlEncode):
    
    if urlEncode:
      # TODO: Does this work?  
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8')) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    

# 4i. Another Concrete visitor class
# TODO: Not yet working; Incomplete
class HTMLExporter(Visitor):
    def __init__(self, dirT, fileT, pageT, criteria):
        
        self.file_count = 0
        self.directory_count = 0

        self.dirTemplate = dirT
        self.fileTemplate = fileT
        self.pageTemplate = pageT
        self.criteria = criteria
        
        self.stack = deque()


        
    def mergeDir(newD, stk):
    
        sDir = ''
        while True:
              if len(stk) <= 0:
                 break

              top = stk.pop()
              if newD['level'] >= top['level']:
                 stk.append(top)
                 return
            
              if top['level'] - newD['level'] > 0:
                
             
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
                          stk.append({'type':'directory', 'level':s['level'], 'name':s['name'], 'html':sDir})
                          break
          
             
        if newD['level'] <= 0:
           stk.append({'level':s['level'], 'name':s['name'], 'html':sDir})
             
        return(sDir)



#############



    # TODO: This is not working correctly.
    def visit_file(self, name, path, level, parent, finfo={}, urlEncode=False):
        clrprint.clrprint(name, clr='maroon')
        if not nameMatches(name, self.criteria.get('fileexclusionPattern', ''), self.criteria.get('fileinclusionPattern', '') ):
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

        
        clrprint.clrprint(f"Processing file: {path} level {level}") 
        self.file_count += 1

        
        fileHtml =  self.fileTemplate.replace('${FILELINK}', htmlLink(path, name, urlEncode)).replace('${FILENAME}', name).replace('${FILEPATH}', path.replace('\\', '/')).replace('${LEVEL}', str(level)).replace('${PARENTPATH}', parent.replace('\\', ' / '))
        if finfo:
           fileHtml = fileHtml.replace('${FILESIZE}', finfo['size']).replace('${FILELASTMODIFIED}', finfo['lastmodified'])

        filename, fileExtension = os.path.splitext(path)
        if os.path.exists('html/' + fileExtension[1:] + '.png'):
           fileHtml = fileHtml.replace('${FILEEXTENSION}', fileExtension[1:])
        else: 
           fileHtml = fileHtml.replace('${FILEEXTENSION}', 'ukn')

        if len(self.stack) <= 0:   
           self.stack.append({'level':level, 'html': fileHtml})
        else:
           curr = self.stack.pop()
           if curr['level'] < level:
              self.stack.append(curr)
              self.stack.append({'level':level, 'html': fileHtml})
           else:    
               curr['html'] = curr['html'] + fileHtml
               self.stack.append(curr)
        


    # TODO: Seems to work but test this more...
    def addDirectory(self, level, fldr):
        if len(self.stack) <= 0:
           self.stack.append( {'type':'directory', 'level':level, 'html':fldr} )  
             
        top = self.stack.pop()
        if top['level'] == level:
           # New directory is at the same level as existing one. So, concatenate it 
           self.stack.append( {'type':'directory', 'level':level, 'html':top['html'] + ' ' + fldr } )
        elif (top['level'] - level) == 1:
              # New directory is at a higher level than current. This means we return from a deeper level
              # i.e. top stack is the subdirectory of the encounterred directory
              sentry = {'type':'directory', 'level':level, 'html':fldr.replace('${SUBDIRECTORY}', top['html'])}
              while True:
                   
                  if len(self.stack) <= 0:
                       break
                  itm = self.stack.pop()
                  if itm['level'] != level:
                     self.stack.append(itm)
                     break

                  clrprint.clrprint('>>> Found same level. Concatenating...', clr='red') 
                  sentry['html'] = itm['html'] +  sentry['html']

              self.stack.append(sentry)

        else:
              self.stack.append(top)
              self.stack.append({'level':level, 'html': fldr})

        return      



    # First (directory) Encountered First Added
    def addDirectoryFEFA(self, level, fldr):
       
       if len(self.stack) <= 0:
          clrprint.clrprint(f'Adding to stack L:{level} {fldr}', clr='blue') 
          self.stack.append( {'type':'directory', 'level':level, 'html':fldr} )
          return

       top = self.stack.pop()     
        
       if top['level'] == level:
          # New directory is at the same level as existing one. So, concatenate it
          clrprint.clrprint(f'Concatenating same level L:{level} {fldr}', clr='blue') 
          self.stack.append( {'type':'directory', 'level':level, 'html':top['html'] + ' ' + fldr } )
       elif (level - top['level']) == 1:
              # New directory is at a lower level (greater level) than current. This means we are
              # going deeper. Hence, add it to the stack
              clrprint.clrprint(f'Adding to stack 2 items: current L:{level} {fldr}', clr='blue')
              self.stack.append(top)
              self.stack.append( {'type':'directory', 'level':level, 'html':fldr} )

              '''
              sentry = {'type':'directory', 'level':level, 'html':fldr.replace('${SUBDIRECTORY}', top['html'])}
              while True:
                   
                  if len(self.stack) <= 0:
                       break
                  itm = self.stack.pop()
                  if itm['level'] != level:
                     self.stack.append(itm)
                     break

                  clrprint.clrprint('>>> Found same level. Concatenating...', clr='red') 
                  sentry['html'] = itm['html'] +  sentry['html']

              self.stack.append(sentry)
              '''

       else:
              #self.stack.append(top)
              #if level < top['level']:
              #    self.stack.append(topDir)
                  
              clrprint.clrprint(f'Items in stack:{len(self.stack)} Current directory: {fldr}', clr='yellow')
              clrprint.clrprint(f'Adding SUBDIR for encounterred current L:{level} {fldr}', clr='blue')
              subd = top['html']
              topDir = self.stack.pop()
              topDir['html'] = topDir['html'].replace('${SUBDIRECTORY}', subd)
              topDir['html'] = topDir['html'] + ' ' + fldr
              self.stack.append(topDir) 
              
              '''
              while True:
                    if len(self.stack) <= 0:
                       print('>>>>>> empty stack') 
                       break
                    
                    itm = self.stack.pop()
                    if itm['level'] == level:
                       subd = itm['html'] + subd
                    elif level - itm['level'] == 1:
                         top['html'] = top['html'].replace('${SUBDIRECTORY}', subd)
                         #print(itm)
                         #self.stack.append(itm)
                         break
              ''' 
              #clrprint.clrprint(f'Generated SUBDIRECTORIES L:{level} {itm["html"]}', clr='blue')
              #clrprint.clrprint(f'Adding to stack L:{level} {fldr}', clr='blue')
              

              #self.stack.append(top)
              #self.stack.append({'type':'directory', 'level':level, 'html':fldr}) 
                    
              #clrprint.clrprint(f'Appending to stack {fldr}', clr='blue') 
              #self.stack.append(top)
              #self.stack.append({'level':level, 'html': fldr})
 
       return


              
           





    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
        
        if not nameMatches(name, self.criteria.get('direxclusionPattern', ''), self.criteria.get('dirinclusionPattern', '')):
           return


        if self.criteria.get('maxDirs', -1) > 0:
           if self.directory_count >= self.criteria.get('maxDirs', -1):
              raise criteriaException(-10, 'maximum number of directories reached.')

    
        self.directory_count += 1
       
        #self.addDirectoryFEFA(level, self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRPATH}", path).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${RLVLCOLOR}', random.choice(fontColorPalette)) )

           
        



    def displayStack(self):
         lst = []
         pos=1
         print('Total of', len(self.stack), 'items in stack.')
         while  len(self.stack) > 0:
                sv = self.stack.pop()
                lst.append(sv)
                print('______' + str(pos) + '______\n', end='')
                print(sv)
                print('_________')
                pos +=1

         for i in lst[::-1]:
             self.stack.append(i)

             

    def unwindStack(self, level=1):
         htmlC = ''
         cnt = 0
         while  len(self.stack) > 0:
              sv = self.stack.pop()
              #print(sv)
              if sv['level'] == level:
                 cnt += 1
                 clrprint.clrprint(f'[{cnt}]', clr='red', end='')
                 print('---\n', sv, '---\n') 
                 htmlC = sv['html'] + htmlC
              
         return(htmlC)     


        
    def showStack(self):
        while  len(self.stack) > 0:
              sv = self.stack.pop()
              print(sv)

   
            

    



# Not used.....
# 5. Traverse the directory structure
def traverse_directory(root_path, visitor):
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isfile(item_path):
            file_obj = File(item_path)
            file_obj.accept(visitor)
        elif os.path.isdir(item_path):
            dir_obj = Directory(item_path)
            dir_obj.accept(visitor)
            traverse_directory(item_path, visitor) # Recursive call for subdirectories



