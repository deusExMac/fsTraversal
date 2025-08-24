
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




        

def doSearch(query='', win=None, progressLabel=None, statusLabel=None, cfg={}):

    
    cfg['guiwindow'] = win
    cfg['guiprogress'] = progressLabel
    cfg['guistatus'] = statusLabel
    
    search(query=f'{query}', criteria=cfg)
    
    closeWindow(win)


   

    

def closeWindow(w=None):
    if w is not None:
       #print('>>> destroying...')
       w.quit()
       w.destroy()


       
def progressSearch(q, config={}):

   # light, dark and System supported
   ctk.set_appearance_mode("System")
   ctk.set_default_color_theme("blue")

   # Create main window  of app
   root = ctk.CTk()
   root.geometry("550x130")
   root.title('Search progress')

   frame = ctk.CTkFrame(master=root)
   frame.pack(pady=10, padx=70, fill="both", expand=True)


   # Create elements of main window

   # Progress label (current directory being scanned)   
   progressLbl = ctk.CTkLabel(master=frame, text=".....", font=("Roboto", 14) )
   progressLbl.pack(pady=10, padx=40)

   # Status (how many found)
   statusLbl = ctk.CTkLabel(master=frame, text="Found: 0",  text_color='red', font=("Roboto", 14) )
   statusLbl.pack(pady=5, padx=40)
   
   
   root.after(2, doSearch, q, root, progressLbl, statusLbl, config)
   
   # Start the GUI
   root.mainloop()






if __name__ == '__main__':
   progressSearch('pdf')
