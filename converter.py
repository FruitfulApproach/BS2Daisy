#!/usr/bin/env python3

from bss_converter import TagConverter, FileManager
import os
import sys

if __name__ == "__main__":
    
    os.environ['DJANGO_PROJECT'] = os.path.dirname(sys.argv[1])
    os.chdir(sys.argv[1])
    FileManager()
