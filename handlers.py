from abc import ABC, abstractmethod
import os
import re
import clrprint


# Checks if obect name on complies to exclusion and inclusion pattern.
# nameComplies returns True, if name does NOT match exclusion regex pattern (xP)
# AND matches inclusion regex pattern (iP).
# An empty imclusion regex pattern means no inclusion pattern i.e. all
# object names are good.
#
# TODO: Has not been tested.
def nameMatches( on, xP='', iP='', dbg=False ):
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





# 1. Define the Visitable interface
class Visitable(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

# 2. Define the Visitor interface
class Visitor(ABC):
    @abstractmethod
    def visit_file(self, file_path):
        pass

    @abstractmethod
    def visit_directory(self, name, lvl, parentPath, dirPath, ld, lf, subdir=""):
        pass




# 3. Concrete element classes (Files and Directories)
class File(Visitable):
    def __init__(self, name, levl=0, path="", finfo={}):
        self.name = name
        self.path = path
        self.fileMeta = finfo

    def accept(self, visitor):
        visitor.visit_file(self.name, self.path, self.fileMeta)
        

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

    def visit_file(self, fn, file_path, finfo={}):
        
        if not nameMatches(self.criteria.get('exclusionRegex', ''), self.criteria.get('inclusionRegex') ):
           return                

        if  self.criteria.get('minFileSize', '') != '':
            if int(finfo.get('size', -2)) < self.criteria.get('minFileSize', -1):
               return

        if  self.criteria.get('maxFileSize', -1) >= 0:
            if int(finfo.get('size', -2)) > self.criteria.get('maxFileSize', -1):
               return    
        
        clrprint.clrprint('\t[F]', clr='green', end='')
        print(f"{fn} in {file_path} {finfo['size']}")
        self.file_count += 1

    def visit_directory(self, name, path, level, parent, ldc, lfc, subdir):
        if not nameMatches(self.criteria.get('exclusionRegex', ''), self.criteria.get('inclusionRegex') ):
           return
        
        clrprint.clrprint('\t[D]', clr='red', end='')
        print(f"{path} [level:{level}] [LD:{ldc}] [LF:{lfc}]")
        self.directory_count += 1



# 4i. Concrete visitor class
# TODO: Not yet working; Incomplete
class HTMLExporter(Visitor):
    def __init__(self, dirT, fileT, pageT, criteria):
        self.criteria = criteria
        self.file_count = 0
        self.directory_count = 0

        self.dirTemplate = dirT
        self.fileTemplate = fileT
        self.pageTemplate = pageT
        
        # actual html page
        self.htmlPage = ''
        



    def visit_file(self, file_path):
        print(f"Processing file: {file_path}")
        self.file_count += 1
        

    def visit_directory(self, dirName="", dir_path="", subdir=""):
        print(f"Processing directory: {dir_path}")
        self.directory_count += 1

        # TODO: Complete this
        self.htmlPage = self.htmlPage + prolog.replace("${ID}", dId).replace("${DIRLINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeUrl) ).replace('${DIRNAME}', encounteredDirectory).replace('${LEVEL}', str(lvl)).replace('${DIRPATH}', directoryPath).replace('${PARENTPATH}', root.replace('\\', ' / ')).replace('${SUBDIRECTORY}', subDirData[4])
        self.htmlPage = self.htmlPage.replace('${LNDIRS}', str(subDirData[2])).replace('${NDIRS}', str(subDirData[0]) if subDirData[0] >=0 else '0' )
        self.htmlPage = self.htmlPage.replace('${LNFILES}', str(subDirData[3])).replace('${NFILES}', str(subDirData[1]) )
        self.htmlPage = self.htmlPage.replace('${RLVLCOLOR}',  rClr)


        


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


# Example Usage
#root_directory = "/path/to/your/directory"  # Replace with your directory
#traverser = DirectoryTraverser()
#traverse_directory(root_directory, traverser)
#print(f"Total files: {traverser.file_count}")
#print(f"Total directories: {traverser.directory_count}")
