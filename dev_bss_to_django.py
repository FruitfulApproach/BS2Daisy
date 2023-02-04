import os
import sys

# This is for BSS to Django developers, so they don't have to keep re-compiling into an executable.
# Simply set BSS export script setting to "dev_bss_to_django.exe".
# All it does is call python on the main script:

debugger_path = None

os.chdir(os.path.dirname(sys.argv[0]))
try:
   with open('DEBUGGER_PATH.txt', 'r') as debugger_path:
      debugger_path = debugger_path.read()
      debugger_path = debugger_path.strip()
      
except Exception as e:
   print("NOTE: You can set the path to your debugger exe in DEBUGGER_PATH.txt alongside this exe.")
   debugger_path = None
   
if debugger_path is None:
   os.system(f'python bss_to_django.py {sys.argv[1]}')
else:
   os.system(f'"{debugger_path}" bss_to_django.py {sys.argv[1]}')