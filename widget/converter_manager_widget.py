from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QLineEdit, QComboBox
from ui.ui_converter_manager_widget import Ui_ConverterManagerWidget

class ConverterManagerWidget(Ui_ConverterManagerWidget, QWidget):
   def __init__(self, pickled=False):
      super().__init__()
      super().__init__()
      self.setupUi(self)
            
      if not pickled:
         self._converterByInputFile = {}
         self.finish_setup()
         
   def __setstate__(self, data):
      self.__init__(pickled=True)
      self._converterByInputFile = data['file converters']
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'file converters' : self._converterByInputFile,
      }
   
   def finish_setup(self):
      pass
   
   def file_converter(self, infile:str):
      return self._converterByInputFile[infile]
   
   def add_converter_for(self, infile:str, outfile:str):
      self._converterByInputFile[filename] = FileConverter(infile, outfile)
   