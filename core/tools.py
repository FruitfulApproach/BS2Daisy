import os


def standard_path(filename:str, sep:str=None) -> str:
   if sep is None:
      sep = '/'
   path = os.path.normpath(filename)
   path = path.replace('\\', sep)
   drive, path1 = os.path.splitdrive(path)
   if drive:
      path = ''.join([drive.upper(), path1])
   return path   


