from PyQt5.QtCore import pyqtSignal, QObject
from glob import glob
import importlib
import sys
import inspect
import os
import math
import re

class CodeGenerator(QObject):   
   status_message_signal = pyqtSignal(str)
   
   def __init__(self, django_root:str, app_folder:str, indent:int, pickled=False):
      super().__init__()
      self._djangoRoot = django_root
      self._indentSpaces = indent
      self._appFolder = app_folder
      
      if not pickled:         
         self._djangoTree = {}
         self.finish_setup()
   
   def __setstate__(self, data):
      self.__init__(data['django root'], data['app folder'], data['indent'], pickled=True)
      self._djangoTree = data['django tree']
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'django tree' : self._djangoTree,
         'django root' : self._djangoRoot,
         'indent' : self._indentSpaces,
         'app folder' : self._appFolder,
      }
         
   def finish_setup(self):
      pass
   
   @property
   def django_project_tree(self):
      return self._djangoTree
   
   @property
   def django_project_root(self):
      return self._djangoRoot
   
   @property
   def num_indent_spaces(self):
      return self._indentSpaces
   
   @property
   def app_folder(self):
      return self._appFolder
      
   def list_files_matching(self, path_pattern:str, recurse:bool=False):
      files = glob(path_pattern, recurse)
      return files
   
   def output_view_code(self, function, name=None):
      module_path, module, attribs = self.get_module_attributes(self.django_project_root, self.app_folder, 'views.py')

      if (name and name not in attribs) or function.__name__ not in attribs:
         if callable(function):
            source = inspect.getsource(function)
         else:
            source = str(function)
         
         source = f'\n{source}'
         
         with open(module_path, 'a') as module_file:
            module_file.write(source) 
                     
   def load_module_with_path(self, module_path:str):
      parts = os.path.normpath(module_path)
      parts = parts.split(os.sep)
      module_name = parts[-1]
      module_name,_ = os.path.splitext(module_name)
      module_spec = importlib.util.spec_from_file_location(module_name, location=module_path)
      module = importlib.util.module_from_spec(module_spec)     
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
   
   def get_module_attributes(self, *args):
      module_path = os.path.join(*args)
      module = self.load_module_with_path(module_path)
      attribs = set(dir(module))      
      return module_path, module, attribs
   
   def delete_view_code_if_unmodified(self, function):
      module_path, module, attribs = self.get_module_attributes(self.django_project_root, self.app_folder, 'views.py')
      
      if callable(function):
         func_name = function.__name__
      else:
         func_name = str(function)
      
      if func_name in attribs:
         existing = getattr(module, func_name)
         
         source = inspect.getsource(function)
         existing_source = inspect.getsource(existing)
         
         if source == existing_source:
            with open(module_path, 'rw') as module_file:
               module_str = module_file.read()
               module_str = module_str.replace(source, '')
               module_file.write(module_str)
         else:
            self.status_message_signal.emit(f"{func_name} code has been modified in {module_path}, so we won't delete it.")
      
   func_def_name_regex = re.compile(r"(?P<prefix>.*def\s+)(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)(?P<suffix>\s*\(.*\)\s*:.*)", flags=re.DOTALL)
   def function_def_renamed(self, code_str:str, new_name:str):
      match = self.func_def_name_regex.match(code_str)
      if match:
         prefix = match.group('prefix')
         name = match.group('name')
         suffix = match.group('suffix')
         if name != new_name:
            return f'{prefix}{new_name}{suffix}'
         
   def rename_view_code(self, old_name:str, new_name:str):
      module_path, module, attribs = self.get_module_attributes(self.django_project_root, self.app_folder, 'views.py')

      if old_name in attribs:
         function = getattr(module, old_name)
         old_source = inspect.getsource(function)
         new_source = self.function_def_renamed(old_source, new_name)
         
         with open(module_path, 'rw') as module_file:
            string = module_file.read()
            string = string.replace(old_source, new_source)
            module_file.write(string)
      
if __name__ == '__main__':
   from PyQt5.QtWidgets import QApplication
   app = QApplication([])

   def test_view(request):
      print(request)
   
   code_gen = CodeGenerator(django_root='../../DiagramChaseDatabase', app_folder='DiagramChaseDatabase', indent=8)
   module = code_gen.load_module_with_path(module_path='../../DiagramChaseDatabase/DiagramChaseDatabase/views.py')   
   code_gen.output_view_code(test_view)
   code = inspect.getsource(test_view)
   code1 = code_gen.tabify_code(code)
   print(code1)
   print(module)
   
   sys.exit(app.exec_())