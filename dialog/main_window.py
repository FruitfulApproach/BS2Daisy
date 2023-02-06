from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTreeWidgetItem, QComboBox, QLineEdit
from ui.ui_main_window import Ui_MainWindow
import _pickle as pickle
import os
import sys
from PyQt5.QtCore import Qt
from datetime import datetime
from widget.export_mapper_widget import ExportMapperWidget
from core.exporter_thread import ExporterThread
from core.file_converter import FileConverter
from datetime import datetime
from core.tools import standard_path

class MainWindow(Ui_MainWindow, QMainWindow):   
   def __init__(self, pickled=False):
      super().__init__()
      super().__init__()
      self.setupUi(self)
      
      self._baseStatusCSS = self.statusBar().styleSheet()    
      
      if not pickled:
         self._exportMapper = ExportMapperWidget()
         self.finish_setup()
         
   def __setstate__(self, data):
      self.__init__(pickled=True)
      self._exportMapper = data['export mapper']
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'export mapper' : self._exportMapper,
      }
   
   def finish_setup(self):      
      self.tabs.insertTab(1, self._exportMapper, "Export Mapping")
      self._exportMapper.file_added.connect(self.prompt_user_about_new_file)

      if self.export_mapper.bss_design_root is None:
         if len(sys.argv) < 2:
            self.log_status_message('This app called without a command line argument. See the Getting Started tab.', 50000)
            self.tabs.setCurrentWidget(self.gettingStartedTab)
         else:
            if not os.path.exists(sys.argv[1]):
               os.makedirs(sys.argv[1])
               
            if os.path.isdir(sys.argv[1]):
               bss_root = standard_path(os.path.abspath(sys.argv[1]), os.sep)
               self.export_mapper.set_bss_root(bss_root)
               self.log_status_message(f'This app called with argument {os.path.relpath(bss_root)}.', 5000, 'color:blue')
               self.tabs.setCurrentWidget(self._exportMapper)
               #self._exportMapper.load_any_new_bss_files()
            else:
               self.log_status_message(f"{sys.argv[1]} is not a directory.", 10000, 'color:red')      
            
      arg0 = sys.argv[0]
      exefile, ext = os.path.splitext(arg0)
      
      if ext == '.py':
         exefile = os.path.join(os.path.dirname(exefile), f'dev_{os.path.basename(exefile)}.exe')
      else:
         exefile = f'{exefile}.exe'
         
      exefile = os.path.abspath(exefile)
      self.exeFilenameLine.setText(exefile)
      
      self.djangoProjectRootLine.setText(self._exportMapper.django_project_root)
      self.copyExeFilenameButton.clicked.connect(self.copy_exe_filename_clicked)
      self.djangoProjectBrowseButton.clicked.connect(self.browse_for_django_project_clicked)
      self.djangoProjectRootLine.textChanged.connect(self.django_project_root_line_changed)
      self.runExporterButton.clicked.connect(self.start_export_thread)
            
   def log_status_message(self, msg:str, sleep_ms:int, extra_css:str=None):
      self.statusBar().showMessage(msg, sleep_ms)      
      self.statusLogText.appendPlainText(f'{str(datetime.now())}: {msg}')
      
      if extra_css:
         self.statusBar().setStyleSheet(f'{self._baseStatusCSS};{extra_css};')      
      else:
         self.statusBar().setStyleSheet(self._baseStatusCSS)
      
   def browse_for_django_project_clicked(self):
      folder = QFileDialog.getExistingDirectory(parent=self, directory='.')
      
      if folder and os.path.exists(folder):
         self.djangoProjectRootLine.setText(standard_path(folder, os.sep))
      
   def copy_exe_filename_clicked(self):
      QApplication.clipboard().setText(self.exeFilenameLine.text())
      self.statusBar().showMessage('EXE filename copied to clipboard!', 5000)
   
   @staticmethod
   def load_last_session_or_new():
      main_window = None
      try:         
         with open('last_session.pkl', 'rb') as last_session:
            last_session = pickle.load(last_session)
            with open(last_session, 'rb') as last_session:
               main_window = pickle.load(last_session)
      except Exception as e:
         print(e)
         main_window = MainWindow()      
      return main_window
   
   def save_last_session(self):
      filename = self.save()
      
      if filename and os.path.exists(filename):
         with open('last_session.pkl', 'wb') as last_session:
            pickle.dump(filename, last_session)
         
   def closeEvent(self, event):
      self.save_last_session()
      super().closeEvent(event)
      
   def save(self):
      if self.django_project_root is None:
         return None
      
      filename = os.path.join(self.export_mapper.bss_design_root, '.bss-to-django-config.pkl')
      
      with open(filename, 'wb') as file:
         pickle.dump(self, file)
         
      return filename
   
   @property
   def django_project_root(self):
      return self._exportMapper.django_project_root

   @property
   def export_mapper(self) -> ExportMapperWidget:
      return self._exportMapper
      
   @staticmethod   
   def try_loading_config_from_arg():
      bss_root = sys.argv[1]
      main_window = None
      app = QApplication.instance()
      
      if os.path.exists(bss_root):
         config_file = standard_path(os.path.join(bss_root, '.bss-to-django-config.pkl'))
         
         try:            
            with open(config_file, 'rb') as config_file:
               main_window = pickle.load(config_file)
               app.main_window = main_window
               main_window.export_mapper.load_any_new_bss_files()
               main_window.start_export_thread()
               
         except Exception as e:
            main_window = MainWindow()
            app.main_window = main_window
            main_window.show()            
            main_window.log_status_message(str(e), 10000, 'color:red')    
            
            #if 'DEBUG' in os.environ:
               #raise e
      else:
         main_window = MainWindow()
         app.main_window = main_window
         main_window.show()
   
      if not main_window.isVisible() and 'DEBUG' in os.environ:
         main_window.show()
         
      return main_window
   
   def start_export_thread(self):
      self.export_mapper.set_last_export_time(datetime.now())
      self.runExporterButton.setEnabled(False)
      self._exportThread = ExporterThread(file_convs=self.file_converter_list(), parent=self)
      self._exportThread.finished.connect(self._exportThreadFinished)
      self._exportThread.progress_made.connect(self.exportProgress.setValue)
      self._exportThread.file_exported.connect(self.handle_file_exported_result)
      self._exportThread.start()
      
   def handle_file_exported_result(self, filename:str, result:str):
      self.export_mapper.handle_file_exported_result(filename, result)
      
      if not self.isVisible():
         self.close()
         QApplication.instance().quit()
      
   def _exportThreadFinished(self):
      self.runExporterButton.setEnabled(True)
      self.exportProgress.setValue(0)
      self.log_status_message('Export completed with 0 errors (TODO)!', 5000, 'color:green')
   
   def file_converter_list(self) -> list:
      input_file_list = list(self.export_mapper.bss_input_files())
      input_file_list.sort()
      
      converters = []
      
      for infile in input_file_list:
         try:               
            outfile = standard_path(self.export_mapper.django_output_file_mapping(infile), sep=os.sep)
            process_option = self.export_mapper.bss_to_django_process_option(infile)
            converter = FileConverter(infile, process_option, outfile, self.export_mapper)       
            converters.append(converter)
         except TypeError as e:
            self.log_status_message('Django project root is not set! Read the instructions.', 10000, 'color:red')
            self.tabs.setCurrentWidget(self.export_mapper)
            break
      
      return converters
   
   def prompt_user_about_new_file(self, filename:str):
      if self.export_mapper.prompt_for_each_new_file:
         self.show()
         self.tabs.setCurrentWidget(self.export_mapper)
         item = self.export_mapper.bss_to_django_tree_item(filename)
         self.export_mapper.exportMappingTree.expand(self.export_mapper.exportMappingTree.indexFromItem(item))
         self.export_mapper.setFocus()
         
   def django_project_root_line_changed(self, text):
      if self.export_mapper.django_project_root != text and os.path.exists(text) and os.path.isdir(text):
         folder = standard_path(text, os.sep)
         self.export_mapper.set_django_root(folder)
      else:
         self.log_status_message("The specified Django project root is either not a directory or it doesn't exist", 10000, 'color:red')