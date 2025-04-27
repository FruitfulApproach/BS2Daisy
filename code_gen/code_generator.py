from PyQt6.QtCore import pyqtSignal, QObject
from glob import glob
import importlib
import sys
import inspect
import os
import math
import re

class CodeGenerator(QObject):
   status_message_signal = pyqtSignal(str)
   jump_to_code_file_line_requested = pyqtSignal(str, int)
   
   def __init__(self, code_gen_widget, pickled=False):
      super().__init__()
      
      self._codeGenWidget = code_gen_widget
      self._boilerPlateWidget = None
      
      if not pickled:         
         self._djangoTree = {}
         self.finish_setup()
   
   def __setstate__(self, data):
      self.__init__(data['code gen widget'], pickled=True)
      self._djangoTree = data['django tree']
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'django tree' : self._djangoTree,
         'django root' : self.code_generation_widget,
         'code gen widget' : self.code_generation_widget,
      }
         
   def finish_setup(self):
      pass
   
   @property
   def code_generation_widget(self):
      return self._codeGenWidget
   
   @property
   def django_project_tree(self):
      return self._djangoTree
   
   @property
   def django_project_root(self):
      return self.code_generation_widget.django_project_root
   
   @property
   def num_indent_spaces(self):
      return self.code_generation_widget.indent_spaces_setting
   
   @property
   def input_file(self):
      return self.code_generation_widget.input_file
      
   def list_files_matching(self, path_pattern:str, recurse:bool=False):
      files = glob(path_pattern, recurse)
      return files
                       
   def load_module_with_path(self, module_path:str):
      parts = os.path.normpath(module_path)
      parts = parts.split(os.sep)
      module_name = parts[-1]
      module_name,_ = os.path.splitext(module_name)
      module_spec = importlib.util.spec_from_file_location(module_name, location=module_path)
      module = importlib.util.module_from_spec(module_spec)
      module_spec.loader.exec_module(module)
      return module
      
   def tabify_code(self, code:str):
      lines = code.splitlines()
      tab_size = self.num_indent_spaces
      orig_tab_size = 0
      k = 0
      
      for line in lines:
         if line.strip():
            spaces = 0
            for c in line:
               if c == ' ':
                  spaces += 1
               else:
                  lines[k] = (spaces, line)
                  orig_tab_size = math.gcd(spaces, orig_tab_size)
                  break
         k += 1
      
      tabified = []
      
      for (spaces, line) in lines:   
         if orig_tab_size != 0:
            tabs = int(spaces / orig_tab_size)
         else:
            tabs = 0
         line = line.strip(' ')
         line = f'{" " * tab_size * tabs}{line}'
         tabified.append(line)
         
      return "\n".join(tabified)
   
   def module_attributes(self, *args):
      try:            
         module_path = os.path.join(*args)
         module = self.load_module_with_path(module_path)
         attribs = dir(module)
         return module_path, module, attribs
      except Exception as e:
         self.status_message_signal.emit(str(e))
         return None, None, []
      
   func_def_name_regex = re.compile(r"(?P<prefix>.*def\s+)(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)(?P<suffix>\s*\(.*\)\s*:.*)", flags=re.DOTALL)
   def function_def_renamed(self, code_str:str, new_name:str):
      match = self.func_def_name_regex.match(code_str)
      if match:
         prefix = match.group('prefix')
         name = match.group('name')
         suffix = match.group('suffix')
         if name != new_name:
            return f'{prefix}{new_name}{suffix}'
            
   @property
   def export_mapper(self):
      return self._codeGenWidget.export_mapper
            
   def app_folder(self, absolute=False):
      django_file = self.export_mapper.django_output_file_mapping(self.input_file)
      django_file = self.export_mapper.filename_rel_root(django_file, root=self.export_mapper.django_project_root)
      
      parts = django_file.split(os.sep)
      
      if parts:
         if parts[0] == 'templates':
            return self.django_settings_folder(absolute)
         else:
            if absolute == False:
               return parts[0]   
            return os.path.join(self.export_mapper.django_project_root, parts[0])
         
   def django_settings_folder(self, absolute=False):
      django_root = self.export_mapper.django_project_root
      
      for folder in os.listdir(django_root):
         filename = os.path.join(django_root, folder)
         
         if os.path.isdir(filename):
            for file in os.listdir(filename):
               if file == 'settings.py':
                  if absolute == False:
                     return folder
                  return filename
    
   @property
   def type_name(self):
      return self.__class__.__name__[:-len('Generator')]
   
   def get_boilerplate_attributes(self, base_file:str):
      return self.module_attributes(self.django_project_root, self.export_mapper.bss_to_django_folder, self.export_mapper.boilerplates_folder, base_file)      
      
   @property
   def django_project_root(self):
      return self.export_mapper.django_project_root
   
   def list_boilerplates(self):
      raise NotImplementedError
   
   def line_number_of_function(self, function_name:str):
      raise NotImplementedError
   
   def jump_to_code(self):
      raise NotImplementedError
   
   def output_code(self, function=None, name=None):
      raise NotImplementedError
   
   def set_boilerplate_widget(self, widget):
      self._boilerPlateWidget = widget
      
   @property
   def boilderplate_widget(self):
      return self._boilerPlateWidget
   
      
if __name__ == '__main__':
   from PyQt6.QtWidgets import QApplication
   app = QApplication([])

   def test_view(request):
      print(request)
   
   code_gen = CodeGenerator(django_root='../../DiagramChaseDatabase', app_folder='DiagramChaseDatabase', indent=8)
   module = code_gen.load_module_with_path(module_path='../../DiagramChaseDatabase/DiagramChaseDatabase/views.py')   
   code_gen.output_code(test_view)
   code = inspect.getsource(test_view)
   code1 = code_gen.tabify_code(code)
   print(code1)
   print(module)
   
   sys.exit(app.exec_())