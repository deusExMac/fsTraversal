
# fsTraversal

A python program that traverses local file system (fs) structures and can apply three different operations: 
1) export filesystem structure in html/json
2) search for files/directories and
3) displays the differences between two directories.

Exporting the fs structure in html is the default operation. 

# Version

-v0.9b@29062025
First version. This project was called dirsToHtml and has been moved here (after major refactoring).

# How to execute
The operation mode is determined/activated based on the arguments provided. 
- For searching for directory files:
  
```python
_fsTraversal [regular expression]_ 
```
  : searches for files/directories whose name matches [regular expression] 

- For comparing two directories
  
    _fsTraversal -LDIR [directory A] -RDIR [directory B]_ : compares directories [directory A] (left side) and [directory B] (right side) and displays their differences in directories, files as well as the common files

- For exporting the directory structure (in html/json):
  
    _fsTraversal_ : exports the strcture of the (default) directory in html

All operation modes can be modified with arguments which are shown below.



# Supported arguments

The general idea is to offer an convenient way to browse the directory/files

[TODO: This list of option does not refer to current version] Some command line arguments (not yet exahaustive):

-d [directory] : directory to start traversing and apply operation

-NR  : non recursive. Won't traverse going into subdirectories

-X [regular expression]: exclude directories/files with name matching [regular expression]

-C [regular expression]: include only those directories/files whose names match [regular expression]

-L [integer]: maximum level to delve into during traversal

-S [integer]: minimum file size

-Z [integer]: maximum file size

-Y : ignore directories during traversal

-F : ignore files during traversal

-P [html template file] : html template file to use when exporting and displaying fs structure in html. For templating, see section html templates.

-o [file name] : output html file

-s [css style file] : CSS stylesheet file to use

-I [text or file] : Content to use as introduction when exporting in html. Text is first interpreted as a file name. If such file is present, the contents of the file is used as intro. Otherwise the text itself.

-T [string] : Title of the exported html file

-e : urlencode URLs

-O : when exporting  structure as a html tree, expand all subfolders

-D : Open the exported html file in browser

-f : export format. Currently html or json supported. Default html

-LDIR [directory] : First (left) directory of comparison. If this is non empty, difference operation is activated.

-RDIR [directory] : Second (right) director of comparison




# How to run

In its simplest form, run the program with the following arguments

```python
dirsToHtml -d C:\\someFolder
```
This will traverse recursively the folder C:\someFolder and generate the file index.html with links to all encounterred files and folders. Absolute and relative paths are supported.

NOTE: paths need to escape all  \  characters.

# Example

The included file 
```ruby
index.html
```
contains an example of what kind of file the program produces. File index.html refers to local files on the development machine when the program was executed. Hence, links will not work on your machine.

# Use cases

This program is usefull if you want to sent an entire local directory structure on your disk to people and would like to allow these people to navigate easily the files and directories.
