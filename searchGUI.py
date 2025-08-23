
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



# Class representing a modal window.
# For downloading Urls.
class newWindow(ctk.CTkToplevel):
    
    def __init__(self, parent=None, callback=None):

        super().__init__()
        #self.top = ctk.CTkToplevel(root)

        #self.geometry("150x250")
        self.parentWindow = parent
        self.callback = callback
        self.stopped = False

        
        self.wait_visibility()
        self.title("Second window")
        self.geometry("550x350")    # By default, it is kept as the geometry of the main window, but you can change it.
        self.title("Modal window")
        
        self.lab = ctk.CTkLabel(self, text="Download progress:---")
        self.lab.pack(pady=20)

        self.downloadUrl = ctk.CTkEntry(master=self, placeholder_text="Url", width=430)
        self.downloadUrl.pack(pady=12, padx=10)
        # default value
        self.downloadUrl.insert(0, 'https://onlinetestcase.com/wp-content/uploads/2023/06/15MB.mp4')
        
        self.bar = ctk.CTkProgressBar(master=self,
                                  orientation='horizontal',
                                  mode='determinate',
                                  border_color='#000000', # TODO: check border_color.    
                                  progress_color='#0f69fa')

        self.bar.pack(padx=5, pady=10)    
        
    
        # Set default starting point to 0
        self.bar.set(0)


        self.buttonStart = ctk.CTkButton( self, text="Start download",command=self.startDownload )
        self.buttonStart.pack(padx=5, pady=10)

        # checkbox
        self.debugMode = ctk.CTkCheckBox(master=self, text="Debug mode on/off")
        self.debugMode.pack(pady=12, padx=10)

        self.buttonStop = ctk.CTkButton( self, text="Stop download", fg_color=("red", "lightgray"), command=self.stopDownload )
        self.buttonStop.pack(padx=5, pady=10)
        
        self.button_close = ctk.CTkButton( self, text="Close window",command=self.closeWindow )
        self.button_close.pack(padx=5, pady=10)
    
        # The next makes the window modal.
        self.focus()
        self.grab_set()


    def reset(self):
        #self.bar['mode'] = 'determinate'
        self.stopped = False
        self.lab.configure(text="Download progress:---")
        self.bar.set(0)
        self.update_idletasks()
        self.update()


    def stopDownload(self):
        self.stopped = True



    # Does the actual download.
    # TODO: Needs refactoring
    def startDownload(self):
        
        # clear/initialize some settings.
        self.reset()

        # Disable some buttons
        self.buttonStart.configure(state = 'disabled')
        self.button_close.configure(state = 'disabled')
        
        link = self.downloadUrl.get()
        if link.strip() == '':
            print('Empty URL.')
            return()

        start_time = time.time()
        print('Downloading ' + link)
        file_name = "download.data"
        
        with open(file_name, "wb") as f:
            print("Downloading to local file [%s]" % file_name)
            # By default, Accept-Encoding: gzip, deflate is sent in the request headers.
            # In order not to deal with chunked transfer encoding that requires special interpretation of
            # contene-length and make the code easier, Accept-Encoding is  set to None .
            response = requests.get(link, stream=True, headers={'Accept-Encoding': None})
            total_length = response.headers.get('content-length')
                
            if total_length is None: # no content length header
               if self.debugMode.get() == 1:
                  print('[DEBUG] No content-length seen')
                  
               print("Content length: ???") 
               self.lab.configure(text="Download progress:???")
               #self.bar['mode'] = 'indeterminate'
               
               f.write(response.content)
               dl = len(response.content)
               self.lab.configure(text=f"Download progress:??? in {(time.time() - start_time):.1f}secs.")
               self.update_idletasks()
               self.update()
            else:
               print(f"Content lenngth: {total_length}")
               total_length = int(total_length)
               dl = 0
               for data in response.iter_content(chunk_size=4096):
                   dl += len(data)
                   if self.debugMode.get() == 1:
                      print(f'[DEBUG][{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] Received: {len(data)}. Total received: [{dl}] Content length: [{total_length}]', flush=True)
                      #time.sleep(0.01)
                      
                   f.write(data)

                   done = dl/total_length
                   # TODO: speed calculation needs to be re-checked.
                   self.lab.configure(text="Download progress: {:.1f}KB/{:.1f}KB  {:.1f}% at {:.2f}KB/sec".format(dl/1024, total_length/1024, 100*done, dl/(1024*(time.time() - start_time)) ))
                   self.bar.set(done)
                   self.update_idletasks()
                   self.update()
                   if self.stopped:
                      if self.debugMode.get() == 1:
                          print(f'[DEBUG] Stp signal seen.', flush=True)
                          
                      break
                    

        elapsedTime = time.time() - start_time         
        print(f'\nDownload of [{self.downloadUrl.get()}] complete in {elapsedTime:.1f} secs.')
        if self.debugMode.get() == 1:
           print(f'[DEBUG] [{self.downloadUrl.get()}] Done {dl} bytes in {elapsedTime:.3f} secs')

        # Enable buttons
        self.buttonStart.configure(state = 'normal')
        self.button_close.configure(state = 'normal')         
        self.update_idletasks()
        self.update()
        
                                    
                   
               


    def closeWindow(self):
        if self.callback:
           self.callback()

        # IMPORTANT! This seems to be crucial as it fixes
        # the issue of unresponsive entries in the
        # root/parent window when newWindow closes
        #root.focus()
        if self.parentWindow:
           self.parentWindow.focus()
        
        self.destroy()
        

def doSearch(statusLabel=None):
    
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

    config['window'] = root
    config['guistatuslabel'] = statusLabel
    #config['directory'] = ''
    search(query='2', criteria=config)





def login():
   print(f"Login clicked with username [{userName.get()}] and password [{passWord.get()}]")


def windowClosed():
    print('CALLBACK: window closed.')
    
   
def newModalwindow(mainWin=None):
    # How to create a new window dynamically, see https://pythonassets.com/posts/create-a-new-window-in-tk-tkinter/
    newWindow(parent=mainWin, callback=windowClosed)
    
    '''
    # Example code of creating new modal window.
    top = ctk.CTkToplevel(root)
    top.title("Second window")
    top.geometry("400x500")    # By default, it is kept as the geometry of the main window, but you can change it.
    lab = ctk.CTkLabel(top, text="This is second window!")
    lab.pack(pady=20)

    button_close = ctk.CTkButton( top, text="Close window",command=top.destroy )
    button_close.place(x=75, y=75)
        
    # The next makes the window modal. 
    top.grab_set()
    '''
    

def closeMainWindow():
    root.destroy()
    



if __name__ == "__main__":

   # light, dark and System supported
   ctk.set_appearance_mode("System")
   ctk.set_default_color_theme("blue")

   # Create main window  of app
   
   root = ctk.CTk()
   root.geometry("500x450")
   root.title('Main application window')

   frame = ctk.CTkFrame(master=root)
   frame.pack(pady=10, padx=70, fill="both", expand=True)


   # Create all elements of main window

   # label   
   label = ctk.CTkLabel(master=frame, text="Status...", font=("Roboto", 14) )
   label.pack(pady=30, padx=40)

   # entries i.e. input boxes
   userName = ctk.CTkEntry(master=frame, placeholder_text="Username")
   userName.pack(pady=12, padx=10)

   passWord = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
   passWord.pack(pady=12, padx=10)   

   # buttons
   button = ctk.CTkButton(master=frame, text="Search", command=lambda: doSearch(label))
   button.pack(pady=12, padx=10)

   # pass as argument the main window.
   newWinbutton = ctk.CTkButton(master=frame, text="Download window", command=lambda: newModalwindow(root) )
   newWinbutton.pack(pady=12, padx=10)

   closeButton = ctk.CTkButton(master=frame, text="Terminate", command=closeMainWindow)
   closeButton.pack(pady=12, padx=10) 

   # checkbox
   chkBox = ctk.CTkCheckBox(master=frame, text="Remember Me")
   chkBox.pack(pady=12, padx=10)

   # Start the GUI
   root.mainloop()
