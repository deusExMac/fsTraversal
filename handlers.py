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

        
     

    # TODO: This is not working correctly.
    def visit_file(self, name, path, level, parent, finfo={}, urlEncode=False):
        
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
        





    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
        
        
        #print(f"Processing directory: {path}")
        self.directory_count += 1

        

        # TODO: Complete this
        rClr = random.choice(fontColorPalette)
        print('Adding directory:', name)
        #self.tmpHtml = self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${SUBDIRECTORY}', subdir).replace('${RLVLCOLOR}', rClr) #+ self.tmpHtml 
        #if level == 1:

        # TODO: Next is wrong...
        if (len(self.stack) <= 0):
            #print(f'>>Adding FOLDER {name} at level {level}')
            self.stack.append( {'level':level, 'html':self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${RLVLCOLOR}', rClr)} ) 
        else:    
           curr = self.stack.pop()
           if curr['level'] == level:
              #print(f'Adding to current LEVEL: {curr["level"]} new: {level}...') 
              self.stack.append( {'level':level, 'html':curr['html'] + ' ' +  self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${RLVLCOLOR}', rClr)} )
              # TODO: here same as below in merging...  
           elif (curr['level'] - level) == 1:
              #self.stack.append(curr) 
              #print(f'Adding subdir: top in stack {curr["level"]} new: {level}...')
              mergedDir = {'level':level, 'html':self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${SUBDIRECTORY}', curr['html']).replace('${RLVLCOLOR}', rClr)}
              #self.stack.append({'level':level, 'html':self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${SUBDIRECTORY}', curr['html']).replace('${RLVLCOLOR}', rClr)} )
              tmpLst = []
              #print('***before: stack size:', len(self.stack))
              while True:         
                    if len(self.stack) <= 0:
                       break
                    
                    itm = self.stack.pop()
                    if itm['level'] != level:
                       self.stack.append(itm)
                       break

                    mergedDir['html'] = itm['html'] +  mergedDir['html']
                    
                    
              self.stack.append(mergedDir)
                  
           else:
               print(f'Pushing new to existing LEVEL: {curr["level"]} new: {level}...')
               #if (curr['level'] < level):
               self.stack.append(curr)
               self.stack.append( {'level':level, 'html': self.dirTemplate.replace("${ID}", 'D-'+str(random.randint(0, 1000000))).replace("${DIRNAME}", name).replace("${PATH}", path).replace("${PARENTPATH}", parent).replace("${LEVEL}", str(level)).replace('${RLVLCOLOR}', rClr)} ) 
                
        #self.displayStack()
           
        



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
         while  len(self.stack) > 0:
              sv = self.stack.pop()
              
              if sv['level'] == level:
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



