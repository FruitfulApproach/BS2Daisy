import os
from PyQt6.QtGui import QPixmap
from importlib.resources import path

def standard_path(filename:str, sep:str=None) -> str:
   if sep is None:
      sep = '/'
   path = os.path.normpath(filename)
   path = path.replace('\\', sep)
   drive, path1 = os.path.splitdrive(path)
   if drive:
      path = ''.join([drive.upper(), path1])
   return path   


def load_resource_pixmap(resource_path:str):
   with path("resources.img", resource_path) as f_path:
      return QPixmap(str(f_path))