import os
import sys

# This is for BSS to Django developers, so they don't have to keep re-compiling into an executable.
# Simply set BSS export script setting to "dev_bss_to_django.exe".
# All it does is call python on the main script:

os.chdir(os.path.dirname(sys.argv[0]))
os.system(f'python bss_to_django.py {sys.argv[1]}')