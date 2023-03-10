from code_gen.code_generator import CodeGenerator
import inspect


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
      return self._templatePath
   
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
         
   def output_view_code(self, function=None):
      if function is None:
         function = boilerplate_view_function
      view_name = self.view_name
      source = inspect.getsource(function)
      source = source.format(template_path=f'"{self.template_path}"')
      source = self.function_def_renamed(source, view_name)
      super().output_view_code(function=source, name=view_name)
      
   def list_boilerplates(self) -> list:
      _, module, attributes = self.get_boilerplate_attributes('views.py')
      boilerplates = []
      
      for name in attributes:
         attrib = getattr(module, name)
         
         if callable(attrib):
            args = inspect.getargspec(attrib).args
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
      module_path, module, attribs = self.module_attributes(self.django_project_root, self.app_folder, 'views.py')
      
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
            
   def output_view_code(self, function, name=None):
      module_path, module, attribs = self.module_attributes(self.django_project_root, self.app_folder, 'views.py')

      if (name and name not in attribs) or function.__name__ not in attribs:
         if callable(function):
            source = inspect.getsource(function)
         else:
            source = str(function)
         
         source = f'\n{source}'
         
         with open(module_path, 'a') as module_file:
            module_file.write(source) 
