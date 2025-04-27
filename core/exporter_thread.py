from PyQt6.QtCore import QThread, pyqtSignal

class ExporterThread(QThread):
   status_signal = pyqtSignal(str)
   progress_made = pyqtSignal(int)
   file_exported = pyqtSignal(str, str)
   
   def __init__(self, file_convs:list, parent=None):
      super().__init__(parent)
      self._fileConverters = file_convs
      
   def run(self):
      self.progress_made.emit(0)
      counter = 0
      
      for converter in self._fileConverters:
         converter.convert(thread=self)
         self.file_exported.emit(converter.input_file, "success")
         counter += 1
         self.progress_made.emit(int(counter / len(self._fileConverters) * 100))
   