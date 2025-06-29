# Singleton class design

class someClass:
      loaded = False
      def __init__(self, a=1, b=2):
          
            
          print('\t\tExecuting init in base class with', a, b)
          
          self.c1 = a
          self.c2 = b
          self.loaded = True
          

class singleton(someClass):

      instance = None

      def __new__(cls, a=-66, b=-77):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            print('\tCreating instance')

        print('\tReturning instance')
        return cls.instance

      def __init__(self, a=-1, b=-42):
          print('\tCalling init in singleton with', a, b)
          super().__init__(a, b)



s1 = singleton()
#s1.a = 'sonia' 

s2 = singleton(88, 99)
#print(s2.a)
#s2.a = -222

s3 = singleton(110, 121)
print(s1.c1)
print(s1.c2)



#!/usr/bin/python

import sys
import os
import re
import signal

from pathlib import Path
from clrprint import *

from prettytable import PrettyTable
import itertools
from bloom_filter import BloomFilter



'''
from pynput import keyboard

# The key combination to check
COMBINATION = {keyboard.Key.cmd, keyboard.Key.ctrl}

# The currently active modifiers
current = set()


def on_press(key):
    if key in COMBINATION:
        current.add(key)
        if all(k in current for k in COMBINATION):
            print('All modifiers active!')
    if key == keyboard.Key.esc:
        listener.stop()


def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
'''    


showFiles = False
breakINTR = False

'''
def handler(signum):
   if signum == signal.SIGUSR1:
       print('user defined interrupt!')
       breakINTR = True

signal.signal(signal.SIGUSR1, handler)
'''



def compare( dir1, dir2, xP='' ):
    global   breakINTR

    # make absolute
    absDir1 = os.path.abspath(dir1)
    absDir2 = os.path.abspath(dir2)
    print(absDir1, absDir2)
    nonExistent = BloomFilter(max_elements=10000, error_rate=0.1)
    fsStats = {'nD':0, 'nDC':0, 'nDM':0, 'nDF':0, 'nF':0, 'nFC':0, 'nFM':0, 'nFF':0 }
    
    # traverse root directory, and list directories as dirs and files as files
    try:
          
      for root, dirs, files in os.walk(absDir1):
           
           
        if xP!= '' and re.search(xP, root):  
           continue

        if root == absDir1:
           clrprint(f'[SKIPPING] {root}', clr='purple')
           continue

        fsStats['nD'] += 1
        fsStats['nDC'] += 1
        # Parent path of current directory
        parentPath = Path(root).parent.absolute()
        print(root)
        print('\tChecking if parent path [', parentPath, '] in filter...', sep='', end='')
        if str(parentPath) in nonExistent:
           fsStats['nDM'] += 1 
           clrprint('[YES-Skipping]', clr='y')
           continue

        clrprint('[NO]', clr='o')
        
        # Get relative part           
        rp = os.path.relpath(root, absDir1)
        print(f'\t[RELATIVE PATH of {root} with {absDir1}]', rp)
        print('\t', absDir2 + os.sep + rp, end='')
        if not os.path.isdir(absDir2 + os.sep + rp):
           #print(root)
           clrprint(' [Does not exist]', clr='red')
           nonExistent.add( str(root) )
           clrprint('\t[Adding to bloomfilter]', root, clr='purple')
           fsStats['nDM'] += 1
        else:
              fsStats['nDF'] += 1  
              clrprint(' [Exist]', clr='green')
                  
        if showFiles:
           for file in files:
               print('   [f]', os.sep.join(path[1:]), '/', file, sep='')
               
    except KeyboardInterrupt:
           print('\n\nControl-C seen. Terminating.....')
           return(fsStats)
    except Exception as Ex:
           print('Got exception', str(Ex) )

           
    return(fsStats)




    
      

def is_same(dir1, dir2):
    """
    Compare two directory trees content.
    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2)
    print(f'Comparison of {dir1} and {dir2}:')
    print('\tleft_only:', compared.left_only)
    print('\tright_only:', compared.right_only)
    print('\tcommon:', compared.common_dirs)
    
    if (compared.left_only or compared.right_only or compared.diff_files 
        or compared.funny_files):
        return False
      
    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
      
    return True









import sys
import keyboard
import time
import datetime
from os.path import join, commonprefix, relpath
from filecmp import dircmp



def defaultDH(l=1, side='right', path='') -> None:
    """
      Default Directory Handler displaying only formatted side and path of Directories
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """
    print('\t'*l, f'[{l}][D] [{side} only] {path}', sep='')



def defaultFH(l=1, side='right', path=''):
    """
      Default File Handler displaying only formatted side and path of Files
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """  
    print('\t'*l, f'[{l}][F] [{side} only] {path}', sep='')






def customDirectoryHandler(l=1, side='right', path='') -> None:
    print('\t'*l, f'[{l}][{side}] {path}', sep='')






def matches(mF, fname) -> bool:
    """
      Returns if the file name matches pattern specified in mF
      
      :param mF: regular expression a file name must match. Empty string for no filter.
      :param fname: file name to check regular expression agains. NOTE: No full path expected
      :return: Boolean indicating if file name matches pattern
    """
    
    if mF == '' or mF is None:
       return(True)

    if re.search(mF, fname) is not None:  
       return(True)
      
    return(False)  




def on_alt(event):
    if keyboard.is_pressed('ctrl'):
        print('\n\n\nCtrl + Alt pressed')
        input('Press any key to continue...>')







def getRelativePath(p, root):
    commonPrefix = os.path.commonprefix([p, root])
    if commonPrefix == '':
       return ''
      
    return( os.path.relpath(p, commonPrefix) ) 


          
def isEmpty(dInfo):
    if (not dInfo['D']) and (not dInfo['F']) :
        return(True)

    return(False)  












      
#
#
# Returns only the differences between two directories in terms of files and directories
# Seems to work. More testing needed though.
#
# 18/07/2024: TEST THIS!!!
#
def dirDifference(L_dir, R_dir, lvl=1, mxLvl=-1, dirOnly=False, matchFilter='', dirHandler=defaultDH, fileHandler=defaultFH, verbose=False, progress=None):

  """
       Traverses recursively directories and calculates the differences (in terms of directories and files) between
       two directories.
      
      :param L_dir: One directory path- left side
      :param fname: Second directory path - right side
      :param lvl: Current level of traversal
      :param dirOnly: If True calculates differences for directories only. Otherwise, also files are taken
      into consideration.
      :param matchFilter: regular expression directory and file names must match. Empty string indicates no filter.
      :param dirHandler: Function to call for each directory encountered
      :param fileHandler:Function to call for each file encountered 
      :return: tuple indicatins status, total objects matching, list of objects only in left side, list of objects only in right side
  """
  
        
  localTotal = 0
  prefix = '\t'*lvl
  L_only, R_only, C_only = {'D':[], 'F':[]}, {'D':[], 'F':[]}, {'D':[], 'F':[]}

  if mxLvl > 0:
     if lvl > mxLvl:
        return (0, localTotal, L_only, R_only, C_only) 


  
  verbose and print('\t'*lvl, f'{40*"+"}\n', '\t'*lvl, f'[L:{lvl}] Comparing ', f'[{L_dir}] ', 'to ', f'[{R_dir}]\n', sep='') 
  

  if L_dir == R_dir:
     verbose and print(f"{L_dir} / {R_dir}")   
     return(-2, 0, L_only, R_only, C_only)

  try:  
    dcmp = dircmp(L_dir, R_dir)
    if not dcmp:
       return(-7, 0, L_only, R_only, C_only)   
          
    L_only['D'] = [ join(L_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.left_only if  os.path.isdir( join(L_dir, f)  ) and matches(matchFilter, f)  ]
    R_only['D'] = [ join(R_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.right_only if os.path.isdir( join(R_dir, f)  ) and matches(matchFilter, f)]
    # for common files, take relative paths
    C_only['D'] = [ f  for f in dcmp.common_dirs if matches(matchFilter, f)  ]
    
    if not dirOnly:       
       L_only['F'] = [ join(L_dir, f)  + ' [L:'+str(lvl)+']' for f in dcmp.left_only if not os.path.isdir( join(L_dir, f)  ) and matches(matchFilter, f) ]
       R_only['F'] = [ join(R_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.right_only if not os.path.isdir( join(R_dir, f)  ) and matches(matchFilter, f)]
       # We use the left-sided root as the prefix for common files.
       # TODO: relative here too? 
       C_only['F'] = [ join(L_dir, f) + ' [L:'+str(lvl)+']' for f in dcmp.common_files if matches(matchFilter, f)  ]

    
    
    # TODO: This is not correct. Recheck and redesign it   
    if dirHandler:  
       for d in L_only['D']:
           dirHandler(lvl, 'left', d)
           
       for d in R_only['D']:
           dirHandler(lvl, 'right', d)

       for cd in  dcmp.common_dirs:
           dirHandler(lvl, 'common', cd)    


    if (not dirOnly) and fileHandler:
       for f in L_only['F']:    
           fileHandler(lvl, 'left', f)
       
       for f in R_only['F']:    
           fileHandler(lvl, 'right', f) 

       for cf in  dcmp.common_files:
           fileHandler(lvl, 'common', cf)          

    
    
    verbose and print('\t'*lvl + f'l_only={len(L_only["D"]) + len(L_only["F"])} r_only={len(R_only["D"]) + len(R_only["F"])} common_dirs={len(dcmp.common_dirs)} common_files={len(dcmp.common_files)}')  
    
    localTotal = len(L_only['D']) + len(L_only['F']) + len(R_only['D']) + len(R_only['F']) + len(dcmp.common_dirs) + len(dcmp.common_files)

    
    
    # Handle directories having common names. I.e. traverse these and
    # find their differences
    #
    # TODO: optimize next two lines?
    
    cd =  C_only['D'].copy()
    C_only['D'] = [ join(L_dir, f) for f in cd]
    for sub_dir in cd:
                 
        s, lt, new_L, new_R, new_C = dirDifference(join(L_dir, sub_dir), join(R_dir, sub_dir), (lvl+1), mxLvl, dirOnly, matchFilter, dirHandler, fileHandler, verbose, progress)

        if s < 0:
           return(s, localTotal, L_only, R_only, C_only)
      
        L_only['D'].extend(new_L['D'])
        if not dirOnly:
           L_only['F'].extend(new_L['F'])

        R_only['D'].extend(new_R['D'])
        if not dirOnly:
           R_only['F'].extend(new_R['F'])

        C_only['D'].extend( new_C['D'] )
        if not dirOnly:
           C_only['F'].extend( new_C['F'] )
        
        verbose and print('\t'*lvl,  f'>> # items from level below {lt}', sep='')  
        localTotal = localTotal + lt

    verbose and print('\t'*lvl + f'returning {localTotal}\n', '\t'*lvl, f'{40*"-"}', sep='')           
    return(0, localTotal, L_only, R_only, C_only)

  except KeyboardInterrupt as kI:
         #
         # Do a full/cascading unrolling. raising exceptions until
         # top level is reached; from which it is returned
         #
         print(f'\n\n[L:{lvl}] Interupted in {L_dir} {R_dir}. Terminating: Total:{localTotal}')
         if lvl > 1:
            raise kI
         else:
            return( -1, localTotal, L_only, R_only, C_only )  
         











#
# Shortens only the filesname part of a path
#
# Check this again.
# NOTE: This  does actually rename the files IF doRename is set to False. doRename = True will
#       actually rename the file
# Example: turns /Users/abcdefghijklmnopqrstuvw/anotherDirectory/someFile.jpg to  /Users/abcdefghijklmnopqrstuvw/anotherDirectory/som...jpg
# if max_length is set to 3
# From: https://techoverflow.net/2023/10/28/trimming-down-long-directory-and-file-names-using-python/
def shorten_path(path, max_length=6, ellipsis='...', doRename=False):
    if max_length < 0:
       return(path)
             
    if os.path.isdir(path):
        base_name = os.path.basename(path)
        if len(base_name) > max_length:
            new_name = base_name[:max_length] + ellipsis
            new_path = os.path.join(os.path.dirname(path), new_name)
            if not os.path.exists(new_path):
                if doRename:
                    os.rename(path, new_path)
                    print(f"Renamed directory: {path} -> {new_name}")
                return new_path
    else:
        base_name, ext = os.path.splitext(os.path.basename(path))
        if len(base_name) > max_length:
            new_name = base_name[:max_length] + ellipsis + ext
            new_path = os.path.join(os.path.dirname(path), new_name)
            if not os.path.exists(new_path):
                if doRename:
                    os.rename(path, new_path)
                    print(f"Renamed file: {path} -> {new_name}")
                return new_path
    return path



# Shortens all components of a path; not only the last part
# TODO: Check this
def shortenCompletePath(path, mxLength=7, tailLength=5, ellipsis='...'):
            sPath = ''
            if len(path) <= mxLength:
               return(path)
            
            pathParts = path.split(os.sep)
            for p in pathParts:
                if len(p) <= mxLength:
                   if sPath == '':
                      sPath = p
                   else:
                      sPath = sPath + os.sep + p 
                else:    
                   if sPath == '':
                      # bug here: ellipsis will appear if string slightly longer than max length
                      sPath = p[:mxLength] + '...' + p[ -(tailLength if abs(mxLength-len(p)) > tailLength else abs(mxLength-len(p))): ]
                   else:    
                      sPath = sPath + os.sep + p[:mxLength] +  ellipsis + p[ -(tailLength if abs(mxLength-len(p)) > tailLength else abs(mxLength-len(p))): ]

            return(sPath)



def tabularDisplay(ld, l, rd, r, c):
     if (not l['D']) and (not r['D']):
         clrprint('All directories in common.', clr='g')
     else:   
      table = PrettyTable()
      table.align = "l"
      titles = ('LEFT','RIGHT')
      table.title = 'DIRECTORIES'
      table.field_names = ["only in " + ld, "only in " + rd]
      for d in itertools.zip_longest(l['D'], r['D'],fillvalue=""):
          table.add_row([ getRelativePath( shorten_path(d[0], 22, '...'), ld), getRelativePath(shorten_path(d[1], 33, '...'), rd)]) 

      clrprint(table, clr='y')


      if l['F'] or r['F']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'FILES'
         tableF.field_names = ["only in " + ld, "only in " + rd]

         for f in itertools.zip_longest(l['F'], r['F'],fillvalue=""): 
             tableF.add_row([ getRelativePath( shorten_path(f[0], 160, '...'), dirA ), getRelativePath( shorten_path(f[1], 160, '...'), dirB)])
      
         clrprint(tableF, clr='g') 


      if c['D']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'COMMON DIRECTORIES'
         tableF.field_names = ["relative paths"]
         for f in c['D']: 
             tableF.add_row([ getRelativePath( f, ld )])

         clrprint(tableF, clr='m')    


      if c['F']:
         tableF = PrettyTable()
         tableF.align = "l"
         tableF.title = 'COMMON FILES'
         tableF.field_names = ["relative paths"]
         for f in c['F']: 
             tableF.add_row([ getRelativePath( f, ld )])

         clrprint(tableF, clr='m')     




def saveToFile(fname='diff.txt', ld='', l={'D':[], 'F':[] }, rd='', r={'D':[], 'F':[]}, c={'D':[], 'F':[]}):
      print(f'Saving to {fname}...', end='')
      with open(fname,'w',  encoding="utf-8") as tfile:
        tfile.write(f"\n{40*'*'}\n")
        tfile.write('** LEFT\n')
        tfile.write(f"{40*'*'}\n")
        tfile.write('\n'.join(l['D']))

        tfile.write(f"\n{40*'*'}\n")
        tfile.write('** RIGHT\n')
        tfile.write(f"{40*'*'}\n")

        tfile.write('\n'.join(r['D']))
        tfile.write(f"\n{40*'*'}\n")
        tfile.write('** COMMON\n')
        tfile.write(f"{40*'*'}\n")
        tfile.write('\n'.join(c['D']))
        tfile.write('\n'.join(c['F']))

      print('Done.') 


def saveListToFile(fname='', l=[]):
    if not l:
       return

    try:  
       with open(fname,'w',  encoding="utf-8") as tfile:
            tfile.write('\n'.join(l)) 
    except Exception as e:
           print(f'Error {str(e)} saving to file {fname}') 
   


def saveToFiles(namePrefix='diff-', ld='', l={'D':[], 'F':[] }, rd='', r={'D':[], 'F':[]}, c={'D':[], 'F':[]}):
      sId = '{date:%d%m%Y@%H%M%S}'.format( date=datetime.datetime.now() )
      print(f'Saving to files...', end='')
      saveListToFile( namePrefix + 'LDIR-'  +  sId + '.txt', l['D'] )
      saveListToFile( namePrefix + 'RDIR-'  +  sId + '.txt', r['D'] )
      saveListToFile( namePrefix + 'LFILES-'  + sId + '.txt', l['F'] )
      saveListToFile( namePrefix + 'RFILES-'   + sId + '.txt', r['F'] )
      saveListToFile( namePrefix + 'CDIR-'   + sId + '.txt', c['D'] )
      saveListToFile( namePrefix + 'CFILES-'   + sId + '.txt', c['F'] )
      print('Done.') 


'''
try:      
   keyboard.on_press_key('alt', on_alt)
except Exception as kEx:
   print('Error hooking keypress handler:', str(kEx))
   time.sleep(3)
'''




dirA = "/Users/manolistzagarakis/users/tzag/papers"
#dirA = "F:\\home\\econ"
dirB = "/Users/manolistzagarakis/users/tzag/reviews"
#dirB = "D:\\Backup12-07-2024\\econ"



tmStart = time.perf_counter()

sts, t, a, b, c = dirDifference(L_dir=dirA, R_dir=dirB, lvl=1, mxLvl=-1, dirHandler=None, fileHandler=None, dirOnly=False, matchFilter='', verbose=False, progress=0.01)
tmEnd = time.perf_counter()

print(f'Finished with status {sts} in {"{:.3f}".format(tmEnd-tmStart)}s. Total (directories/files) encountered: {t} # directories/files different: { str(len(a["D"]) + len(b["D"])) + "/" + str(len(a["F"]) + len(b["F"])) }')



#saveToFiles(namePrefix='test-', ld=dirA, l=a, rd=dirB, r=b, c=c)

tabularDisplay(dirA, a, dirB, b, c)

'''
if (not a['D']) and (not b['D']):
   clrprint('All directories in common.', clr='g')
else:   
   table = PrettyTable()
   table.align = "l"
   titles = ('LEFT','RIGHT')
   table.title = 'DIRECTORIES'
   table.field_names = ["only in " + dirA, "only in " + dirB]
   for r in itertools.zip_longest(a['D'], b['D'],fillvalue=""):
       table.add_row([ getRelativePath( shorten_path(r[0], -1, '...'), dirA), getRelativePath(shorten_path(r[1], -1, '...'), dirB)]) 

   clrprint(table, clr='y')



if a['F'] or b['F']:
   tableF = PrettyTable()
   tableF.align = "l"
   tableF.title = 'FILES'
   tableF.field_names = ["only in " + dirA, "only in " + dirB]

   for r in itertools.zip_longest(a['F'], b['F'],fillvalue=""): 
        tableF.add_row([ getRelativePath( shorten_path(r[0], 160, '...'), dirA ), getRelativePath( shorten_path(r[1], 160, '...'), dirB)])
      
   clrprint(tableF, clr='g')

'''



'''
if c['D']:
   tableC = PrettyTable()
   tableC.align = "l"
   tableC.title = 'COMMON DIRECTORIES'
   tableC.field_names = ["relative names"]
   for r in c['D']:  
       tableC.add_row([r])

clrprint( tableC, clr='m')


if c['F']:
   tableC = PrettyTable()
   tableC.align = "l"
   tableC.title = 'COMMON FILES'
   tableC.field_names = ["relative names"]
   for r in c['F']:
       tableC.add_row([r])

clrprint( tableC, clr='m')
'''




#fsD = compare("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", '\.svn')
#clrprint(fsD, clr='green')

#dff = diffDirs("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", False)
#dff.report()
sys.exit(-2)









maxIter = 3
n = 0
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("/Users/manolistzagarakis/users/"):
    path = root.split(os.sep)
    #print(path[1:])
    #print('[D]', os.path.abspath(os.sep.join(path[1:])) )
    
    #root = root.replace('exampleDir/', '')
    print('[', root, ']')
    print('\t[RELATIVE] ::', os.path.relpath(root, "/Users/manolistzagarakis") ) 
    print('\t[ABSOLUTE] ::', os.path.abspath(root))
    print('\t[D]', dirs)
    print('\t[F]', files)
    #break
    #print((len(path) - 1) * '---', os.path.basename(root))
    if showFiles:
      for file in files:
        #print(len(path) * '---', file)
         print('   [f]', os.sep.join(path[1:]), '/', file, sep='')

    print(n*'*')
    n += 1
    if n >= 3:
       break   

