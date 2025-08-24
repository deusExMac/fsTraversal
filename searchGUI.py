
#
# Trivial attemps to see how python support GUIs . Here module customtkinter is used to
# create simple windows and UI elements. The emphasis here is how these elements
# appear and how they interract. This is not a complete, coherent and finished application;
# most elements were put on windows/forms to see how they interact what characteristics they have.
# Cases that were implemented:
#    * how to place elements
#    * how to create a new window dynamically (a modal window)
#    * how to create a custom UI class (a dialog window)
#    * how to interact with buttons
#    * how to change visual cues of elements
#    * how to use progress bar
#    * how to use callbacks
#    * how to enable/disable elements/buttons
#    * ... some other ...
#
# Some basic elements were created and put on windows.
#
# A simple download form has been implemented for testing purposes only. 
#
# tzagara|v0.3@13/04/2024




import sys
import time
import datetime

import requests
import customtkinter as ctk

import configparser
import argparse

from sandbox import search




        

def doSearch(win=None, query='', statusLabel=None, cfg={}):

    '''
    cmdArgParser = argparse.ArgumentParser(description='Command line arguments', add_help=False)
    # Configuration file
    cmdArgParser.add_argument('-c', '--config', default="fsTraversal.conf")
    
    # Directory traversal related and criteria
    cmdArgParser.add_argument('-d', '--directory', default="testDirectories/exampleDir0")
    cmdArgParser.add_argument('-mxt', '--maxTime',  type=float, default=-1)
    cmdArgParser.add_argument('-ml', '--maxLevels', type=int, default=-1)
    cmdArgParser.add_argument('-if', '--fileinclusionPattern', default="")
    cmdArgParser.add_argument('-xf', '--fileexclusionPattern', default="")

    cmdArgParser.add_argument('-id', '--dirinclusionPattern', default="")
    cmdArgParser.add_argument('-xd', '--direxclusionPattern', default="")
    cmdArgParser.add_argument('-mns', '--minFileSize', type=float, default=-1)
    cmdArgParser.add_argument('-mxs', '--maxFileSize', type=float, default=-1)
    cmdArgParser.add_argument('-nd', '--maxDirs', type=int, default=-1)
    cmdArgParser.add_argument('-nf', '--maxFiles', type=int,  default=-1)
    cmdArgParser.add_argument('-cdo', '--creationDateOp',  default='==')
    cmdArgParser.add_argument('-cd', '--creationDate',  default='')
    cmdArgParser.add_argument('-lmdo', '--lastModifiedDateOp',  default='==')
    cmdArgParser.add_argument('-lmd', '--lastModifiedDate',  default='')
   
    cmdArgParser.add_argument('-NR', '--nonRecursive', action='store_true')
   


    # SEARCH functionality related
    # If set, don't search for files. 
    cmdArgParser.add_argument('-NF', '--noFiles', action='store_true')
    cmdArgParser.add_argument('-ND', '--noDirs', action='store_true')
    cmdArgParser.add_argument('-I', '--interactive', action='store_true')
    # If set, don't search for directories
    #cmdArgParser.add_argument('-Y', '--nodirectories', action='store_true')

  
    # REMAINDER is searchquery. Search query is interpreted as a regular expression
    cmdArgParser.add_argument('searchquery', nargs=argparse.REMAINDER, default=[])

    cmdArgParser.add_argument('-t', '--htmlTemplate', default="")
    cmdArgParser.add_argument('-o', '--outputFile', default="index.html")
    # Note: if many css files are specified, enclose the arguments in double quotes "" and
    # separate individual css files with a comma (,) e.g. -s "a.css, folder/b.css, c.css"
    cmdArgParser.add_argument('-s', '--css', default="html/style.css")
    cmdArgParser.add_argument('-i', '--introduction', default="")
    cmdArgParser.add_argument('-tl', '--title', default="")
    cmdArgParser.add_argument('-e', '--urlencode', action='store_true') 

    knownArgs, unknownArgs = cmdArgParser.parse_known_args()
    args = vars(knownArgs)
   
    cSettings = configparser.RawConfigParser(allow_no_value=True)
    # To make keys case sensitive (for a strange reason configparser makes all lowercase).
    cSettings.optionxform = str   
    cSettings.read(args['config'])

    # Flatten the red configuration settings and change to necessary type
    config = {}
   
    # TODO: Find a better way to do this
    intKeys = ['maxLevels', 'maxDirs', 'maxFiles']
    floatKeys = ['minFileSize', 'maxFileSize', 'maxTime']
    for s in cSettings.sections():
       for k in dict(cSettings.items(s)):
           if k in intKeys:
              config[k] = cSettings.getint(s, k, fallback=-1)
           elif k in floatKeys:
              config[k] = cSettings.getfloat(s, k, fallback=-1.0)
           else:   
              config[k] = cSettings.get(s, k, fallback='')

    config.update( (k,v) for k,v in args.items() if ((v != '' and v!=-1) or (k not in config.keys()))) 
    '''
    
    config = {'directory':'testDirectories/exampleDir0'}
    config['window'] = win
    config['guistatuslabel'] = statusLabel
    
    search(query=f'{query}', criteria=config)
    
    closeWindow(win)


   

    

def closeWindow(w=None):
    if w:
       w.destroy()


       
def progressSearch(q, config={}):

   # light, dark and System supported
   ctk.set_appearance_mode("System")
   ctk.set_default_color_theme("blue")

   # Create main window  of app
   root = ctk.CTk()
   root.geometry("550x150")
   root.title('Search progress')

   frame = ctk.CTkFrame(master=root)
   frame.pack(pady=10, padx=70, fill="both", expand=True)


   # Create elements of main window

   # Progress label   
   label = ctk.CTkLabel(master=frame, text="Status...", font=("Roboto", 14) )
   label.pack(pady=30, padx=40)

   root.after(2, doSearch, root, q, label, config)
   
   # Start the GUI
   root.mainloop()



progressSearch('doc')
