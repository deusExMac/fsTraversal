# IMPORTANT! This Readme is outdated and under heavy update.

# Version

-v0.8b@29122022
For comments/improvements please contact: tzagara@upatras.gr

# dirsToHtml

A python program that creates a html documents that allows navigating local directory structure and the containing files.

# Description
This program attempts to do the following:
Traverses a directory structure on the disk and creates a html document (default file name index.html) linking to the files found inside these folders. The overall aim is to make a directory structure traversable via Web-links and make browsing easier.

The general idea is to offer an convenient way to browse the directory/files

[TODO: This list of option does not refer to current version] Some command line arguments (not yet exahaustive):

-d [directory] : directory to start traversing

-o [output file]: file to write html into

-c : color cycling (random) of directory names at each level

-s [css file]: Style sheet to use (default is style.css)

...and others. Sorry, no time to fully complete the list.

This has been developed in about 2 days. I apologize for any error, bad design decision or omission. Such problems are exclusively mine.


# How to run

In its simplest form, run the program with the following arguments

```ruby
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
