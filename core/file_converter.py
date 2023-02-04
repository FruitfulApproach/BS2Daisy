import core.exporter_thread
import os
import shutil

class FileConverter:
   def __init__(self, in_file:str, process_opt:str, out_file:str):
      self._infile = in_file
      self._outfile = out_file
      self._processOption = process_opt
      
   @property
   def input_file(self):
      return self._infile
   
   @property
   def output_file(self):
      return self._outfile
   
   @property
   def process_option(self):
      return self._processOption
   
   def convert(self, thread:core.exporter_thread.ExporterThread):
      if self._processOption == 'Ignore':
         pass
      elif self._processOption == 'Copy Over':
         if os.path.isdir(self._infile):
            if not os.path.exists(self._outfile):
               os.makedirs(self._outfile)
         elif os.path.isfile(self._infile):
            directory = os.path.dirname(self._outfile)
            if not os.path.exists(directory):
               os.makedirs(directory)
            shutil.copyfile(self._infile, self._outfile)
      