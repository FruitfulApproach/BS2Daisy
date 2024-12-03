import core.exporter_thread
import os
import shutil
from core.tag_converter import TagConverter
from widget.export_mapper_widget import ExportMapperWidget
from widget.code_generation_widget import CodeGenerationWidget
from widget.boilerplate_setting_widget import BoilerplateSettingWidget

class FileConverter:
   def __init__(self, in_file:str, process_opt:str, out_file:str, export_mapper:ExportMapperWidget):
      self._infile = in_file
      self._outfile = out_file
      self._processOption = process_opt
      self._exportMapper = export_mapper
      
   @property
   def input_file(self):
      return self._infile
   
   @property
   def output_file(self):
      return self._outfile
   
   @property
   def process_option(self):
      return self._processOption

   @property
   def export_mapper(self):
      return self._exportMapper
   
   def convert(self, thread:core.exporter_thread.ExporterThread):
      if self._processOption == 'Ignore':
         pass
      else:
         outdir = os.path.dirname(self.output_file)
         
         if not os.path.exists(outdir):
            os.makedirs(outdir)
         
         if self._processOption == 'Copy Over':
            if os.path.isdir(self._infile):
               if not os.path.exists(self.output_file):
                  os.makedirs(self.output_file)
            elif os.path.isfile(self._infile):
               directory = os.path.dirname(self.output_file)
               if not os.path.exists(directory):
                  os.makedirs(directory)
               shutil.copyfile(self._infile, self.output_file)
         elif self._processOption == 'BSS to Django':
            if 'login.html' in self.input_file :
               print("DEBUG ME")
               
            tag_converter = TagConverter(self.input_file, self.export_mapper, thread)
            
            with open(self.output_file, 'w', encoding='utf8') as output_file:
               output_file.write(tag_converter.convert())
               
            code_gen:CodeGenerationWidget = self.export_mapper.code_generation_mapping(bss_file=self.input_file)
            
            if code_gen:
               for boilerplate in code_gen.boilerplate_widgets:
                  boilerplate:BoilerplateSettingWidget
                  generator = boilerplate.code_generator
                  generator.output_code()
                  
            
      