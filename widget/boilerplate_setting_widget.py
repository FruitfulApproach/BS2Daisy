from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
import widget.code_generation_widget
import os
from code_gen.code_generator import CodeGenerator
from code_gen.view_generator import ViewGenerator

class BoilerplateSettingWidget(QWidget):
   status_message_signal = pyqtSignal(str)
   
   def __init__(self, input_file:str, code_gen_widget, generator:CodeGenerator, pickled=False):
      super().__init__()
      
      self._boilerplateCombo = QComboBox()
      self._jumpToCodeButton = QToolButton()
      self._jumpToCodeButton.setIcon(QIcon(':/images/img/icons/pencil-24x24.png'))
      self._jumpToCodeButton.clicked.connect(lambda: generator.jump_to_code(self.input_file, self._boilerplateCombo.currentText()))
      self._jumpToCodeButton.setMinimumHeight(28)
      self._jumpToCodeButton.setMinimumWidth(28)
      self._jumpToCodeButton.setToolTip('Jump to the code generated from the selected boilerplate.')
      self._jumpToCodeButton.setEnabled(False)
      self.setLayout(QHBoxLayout())
      label = QLabel(f'{generator.type_name}:')
      label.setAlignment(Qt.AlignRight)
      self.layout().addWidget(label)
      self.layout().addWidget(self._boilerplateCombo)
      self.layout().addWidget(self._jumpToCodeButton)
      self.layout().setContentsMargins(0,0,0,0)
      self._inputFile = input_file
      self._codeGenWidget = code_gen_widget
      self._codeGenerator = generator
      
      if not pickled:
         self.finish_setup()
         
   def __setstate__(self, data):
      self.__init__(data['input file'], data['code gen widget'], data['generator'], pickled=True)
      self._boilerplateCombo.setCurrentIndex(data['boilerplate index'])
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'boilerplate index' : self._boilerplateCombo.currentIndex(),
         'input file' : self.input_file,
         'code gen widget': self.code_generation_widget,
         'generator' : self.code_generator,
      }
   
   def finish_setup(self):
      #self._boilerplateCombo.addItems(self.code_generator.list_view_boilerplates())
      pass
   
   def populate_combo_box(self, init:bool=False):
      self.set_boilerplates(self.code_generator.list_boilerplates())
      if init:
         self._boilerplateCombo.setCurrentIndex(1)
   
   def set_boilerplates(self, boilerplates:list):
      current = self._boilerplateCombo.currentText()
      self._boilerplateCombo.clear()
      boilerplates = [' '] + sorted(boilerplates)
      self._boilerplateCombo.addItems(boilerplates)
      
      if current in boilerplates:
         self._boilerplateCombo.setCurrentText(current)
      else:
         self._boilerplateCombo.setCurrentText(' ')
         self.status_message_signal.emit(f'Boilerplate {current} must have got deleted.  Make sure to select a new boilerplate {self.code_generator.type_name} for {self.input_file} if you need one.')
         
   def boilerplates(self):
      return [self._boilerplateCombo.itemText(k) for k in self._boilerplateCombo.count()]
   
   @property
   def input_file(self):
      return self._inputFile
   
   @property
   def export_mapper(self):
      return self.code_generation_widget.export_mapper
   
   @property
   def code_generation_widget(self):
      return self._codeGenWidget
   
   @property
   def code_generator(self):
      return self._codeGenerator
