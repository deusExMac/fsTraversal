from abc import ABC, abstractmethod
import os

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
    def __init__(self, path):
        self.path = path

    def accept(self, visitor):
        visitor.visit_file(self.path)

class Directory(Visitable):
    def __init__(self, path):
        self.path = path

    def accept(self, visitor):
        visitor.visit_directory(self.path)

# 4. Concrete visitor class
class DirectoryTraverser(Visitor):
    def __init__(self):
        self.file_count = 0
        self.directory_count = 0

    def visit_file(self, file_path):
        print(f"Processing file: {file_path}")
        self.file_count += 1

    def visit_directory(self, dir_path):
        print(f"Entering directory: {dir_path}")
        self.directory_count += 1

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
root_directory = "/path/to/your/directory"  # Replace with your directory
traverser = DirectoryTraverser()
traverse_directory(root_directory, traverser)
print(f"Total files: {traverser.file_count}")
print(f"Total directories: {traverser.directory_count}")
