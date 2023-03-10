from PyQt5.QtWidgets import QWidget, QHBoxLayout
from widget.boilerplate_setting_widget import BoilerplateSettingWidget
import widget.export_mapper_widget
from PyQt5.QtCore import pyqtSignal, Qt
import os
from code_gen.code_generator import CodeGenerator
from code_gen.view_generator import ViewGenerator

class CodeGenerationWidget(QWidget):
   indent_setting:int = 3
   status_message_signal = pyqtSignal(str)
   jump_to_code_file_line_requested = pyqtSignal(str, int)
   
   View = range(1)
   
   def __init__(self, input_file:str, export_mapper, pickled=False):
      super().__init__()
            
      self._inputFile = input_file
      self._exportMapper = export_mapper
      
      if not pickled:
         self._boilerplateWidgets = [
            BoilerplateSettingWidget(input_file, code_gen_widget=self, generator=ViewGenerator(self))
         ]
         
         self.finish_setup()
   
   def __setstate__(self, data):
      self.__init__(data['input file'], data['export mapper'], pickled=True)
      self._boilerplateWidgets = data['boilerplate widgets']
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'boilerplate widgets' : self.boilerplate_widgets,
         'input file' : self.input_file,
         'export mapper' : self.export_mapper,
      }
      
   def finish_setup(self):
      self.setLayout(QHBoxLayout())
      self.layout().setContentsMargins(0,0,0,0)
      
      for widget in self._boilerplateWidgets:
         widget.status_message_signal.connect(self.status_message_signal.emit)
         self.layout().addWidget(widget)
         #widget.jump_to_code_requested.connect(self.jump_to_code_requested.emit)     
   
   @property
   def input_file(self):
      return self._inputFile
   
   @property
   def export_mapper(self):
      return self._exportMapper
   
   @property
   def boilerplate_widgets(self):
      return self._boilerplateWidgets
   
   def populate_boilerplate_combo_boxes(self, init:bool=False):
      for boilerplate_widget in self.boilerplate_widgets:
         boilerplate_widget.populate_combo_box(init)
         
   def boilerplate_widget(self, index:int):
      return self._boilerplateWidgets[index]

   