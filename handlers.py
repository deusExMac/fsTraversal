from abc import ABC, abstractmethod
import os
import clrprint

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
    def visit_directory(self, dir_path):
        pass

# 3. Concrete element classes (Files and Directories)
class File(Visitable):
    def __init__(self, name, path, finfo={}, lvl=0):
        self.name = name
        self.path = path
        self.fileMeta = finfo

    def accept(self, visitor):
        visitor.visit_file(self.name, self.path)

class Directory(Visitable):
    def __init__(self, name, levl, path, dirPath, ld, lf):
        self.name = name
        self.level = levl
        self.path = path
        self.dirPath = dirPath
        self.localDir = ld
        self.localFile = lf

    def accept(self, visitor):
        visitor.visit_directory(self.name, self.level, self.path,  self.dirPath, self.localDir, self.localFile, "")

# 4. Concrete visitor class
class DirectoryTraverser(Visitor):
    def __init__(self):
        self.file_count = 0
        self.directory_count = 0

    def visit_file(self, fn, file_path):
        clrprint.clrprint('[F]', clr='green', end='')
        print(f"{fn} in {file_path}")
        self.file_count += 1

    def visit_directory(self, name, lvl, parentPath, dirPath, ld, lf, subdir=""):
        clrprint.clrprint('[D]', clr='red', end='')
        print(f"{dirPath} [level:{lvl}] [LD:{ld}] [LF:{lf}]")
        self.directory_count += 1


# 4i. Concrete visitor class
# TODO: Not yet working; Incomplete
class HTMLExporter(Visitor):
    def __init__(self, dirT, fileT, pageT):
        self.file_count = 0
        self.directory_count = 0

        self.dirTemplate = dirT
        self.fileTemplate = fileT
        self.pageTemplate = pageT
        
        self.formattedHTML = ""



    def visit_file(self, file_path):
        print(f"Processing file: {file_path}")
        self.file_count += 1
        

    def visit_directory(self, dirName="", dir_path="", subdir=""):
        print(f"Processing directory: {dir_path}")
        self.directory_count += 1

        # TODO: Complete this
        self.formattedHTML = self.formattedHTML + prolog.replace("${ID}", dId).replace("${DIRLINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeUrl) ).replace('${DIRNAME}', encounteredDirectory).replace('${LEVEL}', str(lvl)).replace('${DIRPATH}', directoryPath).replace('${PARENTPATH}', root.replace('\\', ' / ')).replace('${SUBDIRECTORY}', subDirData[4])
        formatedContents = formatedContents.replace('${LNDIRS}', str(subDirData[2])).replace('${NDIRS}', str(subDirData[0]) if subDirData[0] >=0 else '0' )
        formatedContents = formatedContents.replace('${LNFILES}', str(subDirData[3])).replace('${NFILES}', str(subDirData[1]) )
        formatedContents = formatedContents.replace('${RLVLCOLOR}',  rClr)


        

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
