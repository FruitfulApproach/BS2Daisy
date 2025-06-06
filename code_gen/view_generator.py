from code_gen.code_generator import CodeGenerator
import inspect
import os

class ViewGenerator(CodeGenerator):   
   def __init__(self, code_gen_widget, pickled=False):
      super().__init__(code_gen_widget, pickled)
      
      if not pickled:
         self._viewName = None
         self._templatePath = None
         self.finish_setup()
   
   def __setstate__(self, data):
      super().__setstate__(data)
      self._viewName = data['view name']
      self._templatePath = data['template path']
      
   def __getstate__(self):
      data = super().__getstate__()
      data['view name'] = self._viewName
      data['template path'] = self._templatePath
      return data
      
   @property
   def template_path(self):
      full_path = self.export_mapper.django_output_file_mapping(self.input_file)
      rel_path = self.export_mapper.filename_rel_root(filename=full_path, root=self.django_project_root)
      parts = rel_path.split(sep=os.sep)
      
      if parts[0] == 'templates':
         rel_path =  "/".join(parts[1:])
      elif parts[1] == 'templates':
         rel_path = "/".join(parts[2:])
      else:
         rel_path = "/".join(parts)
      
      return rel_path  
   
   @property
   def view_name(self) -> str:
      return self._viewName
   
   def set_view_name(self, name:str):
      if self._viewName != name:
         self.rename_view_code(self.view_name, new_name=name)
         self._viewName = name
         
   def set_template_path(self, path:str):
      if self._templatePath != path:
         # TODO
         self._templatePath = path
         
   def list_boilerplates(self) -> list:
      _, module, attributes = self.get_boilerplate_attributes('views.py')
      boilerplates = []
      
      for name in attributes:
         attrib = getattr(module, name)
         
         if callable(attrib):
            args = inspect.getfullargspec(attrib).args
            if args and args[0] == 'request':
               boilerplates.append(name)
               
      return boilerplates
      
   def rename_view_code(self, old_name:str, new_name:str):
      module_path, module, attribs = self.module_attributes(self.django_project_root, self.app_folder, 'views.py')

      if old_name in attribs:
         function = getattr(module, old_name)
         old_source = inspect.getsource(function)
         new_source = self.function_def_renamed(old_source, new_name)
         
         with open(module_path, 'rw') as module_file:
            string = module_file.read()
            string = string.replace(old_source, new_source)
            module_file.write(string)
            
   def delete_view_code_if_unmodified(self, function):
      module_path, module, attribs = self.module_attributes(self.django_project_root, self.app_folder(), 'views.py')
      
      if callable(function):
         func_name = function.__name__
      else:
         func_name = str(function)
      
      if func_name in attribs:
         existing = getattr(module, func_name)
         
         source = self.get_boilerplate_source(function)
         existing_source = inspect.getsource(existing)
         
         if source == existing_source:
            with open(module_path, 'r') as module_file:
               module_str = module_file.read()
               
            module_str = module_str.replace(source, '')
            #module_str = module_str.strip()
            #module_str = f'{module_str}\n'
            
            with open(module_path, 'w') as module_file:   
               module_file.write(module_str)
         else:
            self.status_message_signal.emit(f"{func_name} code has been modified in {module_path}, so we won't delete it.")  
            
   def output_code(self, function=None, name=None):      
      module_path, module, attribs = self.get_boilerplate_attributes('views.py')  
      
      if function is None:
         boilerplate = self.boilderplate_widget.current_boilerplate
         if boilerplate.strip() == '' or not boilerplate:
            return            
         function = getattr(module, boilerplate)
         
      if name is None:
         name = self.export_mapper.django_view_name_mapping(self.input_file)
              
      if name:
         module_path, dest_module, attribs = self.module_attributes(self.django_project_root, self.app_folder(), 'views.py')
         
         if hasattr(dest_module, name):
            existing = getattr(dest_module, name)
            self.delete_view_code_if_unmodified(existing)
            
         source = self.get_boilerplate_source(function)
         
         if name != function.__name__:
            source = self.function_def_renamed(source, name)
            
         source = f'\n{source}'
         
         if module_path:
            with open(module_path, 'a') as module_file:
               module_file.write(source)
            
              
   def filename_line_number_of_function(self, function_name:str, create:bool=True):
      module_path, module, attribs = self.module_attributes(self.django_project_root, self.app_folder(), 'views.py')
      
      if hasattr(module, function_name):
         source_lines = inspect.getsourcelines(getattr(module, function_name))
         return module_path, source_lines[1]
      else:
         if not create:
            with open(module_path, "r") as python_file:
               num_lines = python_file.readlines()
               num_lines = len(num_lines)
               return module_path, num_lines
         else:           
            self.output_code(name=function_name)
            return self.filename_line_number_of_function(function_name, create=False)
         
   def jump_to_code(self):
      django_root = self.export_mapper.django_project_root      
      if django_root is None:
         self.error_message_signal.emit("Django project root not set. Go to the Getting Started tab to set it.")
         return
      func_name = self.export_mapper.django_view_name_mapping(self.input_file)
      if func_name:
         filename, line_number = self.filename_line_number_of_function(func_name)      
         self.jump_to_code_file_line_requested.emit(filename, line_number)
      else:
         self.error_message_signal.emit("Code not found. Try exporting first.")
         
   def get_boilerplate_source(self, function):
      source = inspect.getsource(function)
      source = source.format(template_path=f'"{self.template_path}"')
      return source
         