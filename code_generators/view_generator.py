from code_generator import CodeGenerator
import inspect

def boilerplate_view_function(request):
   from django.shortcuts import render
   return render(request, {template_path})

class ViewGenerator(CodeGenerator):   
   def __init__(self, django_root:str, app_folder:str, indent:int, pickled=False):
      super().__init__(django_root, app_folder, indent, pickled)
      
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
      

if __name__ == '__main__':
   view_gen = ViewGenerator(django_root='../../DiagramChaseDatabase', app_folder='DiagramChaseDatabase', indent=8)
   view_gen.set_view_name('my_view')
   view_gen.set_template_path('index.html' )
   view_gen.output_view_code()