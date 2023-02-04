from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QLineEdit, QComboBox, QLabel, QApplication, QMainWindow
from ui.ui_export_mapper_widget import Ui_ExportMapperWidget
import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from datetime import datetime
from core.tools import standard_path

class ExportMapperWidget(Ui_ExportMapperWidget, QWidget):
   bss_assets_subfolders = {'bootstrap', 'js', 'css', 'img'}
   default_ignore_bss_files = {'error.log', '.bss-to-django-config.pkl'}
   process_options = ['Ignore', 'BSS to Django', 'Copy Over']
   image_file_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'}
   
   file_moved_or_deleted = pyqtSignal(str)
   file_added = pyqtSignal(str)
   
   InputFile, ProcessOption, OutputFile, FileChanges = range(4)
   
   def __init__(self, pickled=False):
      super().__init__()
      super().__init__()
      self.setupUi(self)
      
      self._bssFileToTreeItem = {}     
      self._bssDesignExport = None
      self._djangoRoot = None
      
      if not pickled:
         self._bssFileSet = set()
         self._lastExportTime = None
         self.finish_setup()
         
   def __setstate__(self, data):
      self.__init__(pickled=True)
      self._djangoRoot = data['django root']
      self._bssDesignExport = data['bss root']
      self._lastExportTime = data['last import time']
      self.tree_from_dict(data['bss file tree'])      
      self.onlyOnChangesCheck.setChecked(data['export changes only'])
      self.promptForNewFileCheck.setChecked(data['prompt on new file'])
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'django root' : self._djangoRoot,
         'bss root' : self._bssDesignExport,
         'last import time' : self._lastExportTime,
         'bss file tree' : self.tree_to_dict(),
         'export changes only' : self.onlyOnChangesCheck.isChecked(),
         'prompt on new file' : self.promptForNewFileCheck.isChecked(),
      }
   
   def finish_setup(self):
      self.openBSSFolderButton.clicked.connect(lambda: os.startfile(self.bss_design_root))
      self.checkForBSSChangesButton.clicked.connect(self.check_for_bss_file_structure_changes)
      self.expandWholeTreeButton.clicked.connect(self.exportMappingTree.expandAll)
   
   def create_new_bss_tree_item(self, filename:str) -> QTreeWidgetItem:
      process_combo = QComboBox()
      process_combo.addItems(self.process_options)
            
      output_line = QLineEdit()
      output_line.setText(self.default_file_output_path(filename))
      output_line.current_text = output_line.text()
      output_line.textEdited.connect(lambda text: self.django_output_line_edited(filename, text))
      
      if filename in self._ignoreBSSFiles:
         process_combo.setCurrentText('Ignore')    
      else:
         if os.path.isdir(filename):
            process_combo.setCurrentText('Copy Over')
         else:               
            _, ext = os.path.splitext(filename)
            if ext == '.html':
               process_combo.setCurrentText('BSS to Django')
            elif ext in ('.js', '.css'):
               process_combo.setCurrentText('Copy Over')
            elif ext.lower() in self.image_file_extensions:
               process_combo.setCurrentText('Copy Over')
            else:
               process_combo.setCurrentText('Ignore')   # TODO ?  add more exensions like fonts?            
         
      item = QTreeWidgetItem([os.path.basename(filename), None, None, None])      
      
      process_combo.currentTextChanged.connect(lambda text: self.bss_item_process_changed(item, filename, process=text))
      
      self._bssFileToTreeItem[filename] = item
      directory = os.path.dirname(filename)   
      
      if directory in self._bssFileToTreeItem:
         parent:QTreeWidgetItem = self._bssFileToTreeItem[directory]
         parent.addChild(item)
      elif directory == self._bssDesignExport:
         self.exportMappingTree.addTopLevelItem(item)   
         
      change_label = QLabel()
      change_label.setPixmap(QPixmap(':/images/img/icons/add-file24x24.png'))
         
      self.exportMappingTree.setItemWidget(item, self.ProcessOption, process_combo)   
      self.exportMappingTree.setItemWidget(item, self.OutputFile, output_line)
      self.exportMappingTree.setItemWidget(item, self.FileChanges, change_label)
      
      #self.file_added.emit(filename)
      
      # HACKFIX: file_added signal isn't working and QCoreApplication.processEvents() does nothing to fix that.
      
      if self.promptForNewFileCheck.isChecked():
         app = QApplication.instance()
         app.main_window.show()
         app.main_window.raise_()
      
      return item
   
   def load_any_new_bss_files(self):
      bss_root = self._bssDesignExport      
      if bss_root:
         self._ignoreBSSFiles = set(os.path.join(bss_root, ignored) for ignored in self.default_ignore_bss_files)
         for root, directories, files in os.walk(bss_root):    
            root = standard_path(root, sep=os.sep)
            
            for directory in directories:
               directory = standard_path(os.path.join(root, directory), os.sep)
               if directory not in self._bssFileToTreeItem:
                  self.create_new_bss_tree_item(directory)    
                  
            for file in files:
               file = standard_path(os.path.join(root, file), os.sep)
               if file not in self._bssFileToTreeItem:
                  self.create_new_bss_tree_item(file)
               
   def bss_item_process_changed(self, item, filename, process:str):
      if process == 'Ignore':
         if filename not in self._ignoreBSSFiles:
            self._ignoreBSSFiles.add(filename)
      else:    
         if filename in self._ignoreBSSFiles:
            self._ignoreBSSFiles.remove(filename)
            
   def default_file_output_path(self, bss_filename:str):      
      rel_bss_filename = self.bss_filename_rel_root(bss_filename)
      parts = os.path.normpath(rel_bss_filename)
      parts = parts.split(os.sep)
      parts = filter(lambda x: bool(x), parts)
      parts = list(parts)
      bss_root = self._bssDesignExport
      
      if parts:
         if parts[0] == 'assets':
            if len(parts) > 1:
               rel_path = os.path.join(bss_root, *parts[:2])
               
               if os.path.isdir(rel_path):
                  subfolder = parts[1]
                  
                  if subfolder in self.bss_assets_subfolders:
                     if subfolder != 'bootstrap':                        
                        if len(parts) > 2:
                           rel_path = os.path.join(bss_root, *parts[:3])
                           if os.path.isdir(rel_path):
                              app_name = parts[2]
                              return os.path.join(app_name, 'static', subfolder, *parts[3:])
                           elif os.path.isfile(rel_path):
                              return os.path.join('static', subfolder, *parts[2:])
                        else:
                           return os.path.join('static', subfolder)                    
                     else:
                        return os.path.join('static', subfolder, *parts[2:])
                           
                  else:
                     return os.path.join(subfolder, 'static', *parts[2:])
                  
               else:
                  return os.path.join('static', *parts[1:])
            else:
               return 'static'
         else:
            rel_path = os.path.join(bss_root, parts[0])
            
            if os.path.isdir(rel_path):
               folder_name = parts[0]
               
               if len(parts) > 1:
                  return os.path.join(folder_name, 'templates', *parts[1:])
               else:
                  return os.path.join(folder_name, 'templates')
               
            elif os.path.isfile(rel_path):
               return os.path.join('templates', *parts[0:])
               
   def bss_filename_rel_root(self, bss_filename:str) -> str:
      drive, rest = os.path.splitdrive(bss_filename)
      parts = os.path.normpath(rest)
      parts = parts.split(os.sep)
         
      for i in range(1, len(parts)):
         test_directory = f'{drive}{os.sep}{os.path.join(*parts[0:i])}'
         
         if os.path.samefile(test_directory, self._bssDesignExport):
            return os.path.join(*parts[i:])   
         
   def set_bss_root(self, root:str):
      if root != self._bssDesignExport:
         self._bssDesignExport = root
         
   @property
   def bss_design_root(self):
      return self._bssDesignExport
   
   @property
   def django_project_root(self):
      return self._djangoRoot
   
   def django_output_file_mapping(self, bss_file:str):
      
         
      item = self._bssFileToTreeItem[bss_file]
      line_edit = self.exportMappingTree.itemWidget(item, self.OutputFile)
      if os.path.basename(bss_file) == 'untitled.html':
         print("DEBUG")
         print(line_edit.text())
      return os.path.join(self.django_project_root, line_edit.text())
   
   def check_for_bss_file_structure_changes(self):
      for filename in dict(self._bssFileToTreeItem):
         if not os.path.exists(filename):  # It's been deleted or moved
            item:QTreeWidgetItem = self._bssFileToTreeItem[filename]
            django_file = self.exportMappingTree.itemWidget(item, self.OutputFile)
            self.remove_file_or_folder(django_file)
            del self._bssFileToTreeItem[filename]
            item.parent().removeChild(item)
            del item
            self.file_moved_or_deleted.emit(filename)
            
      self.load_any_new_bss_files()
      
   def django_output_line_edited(self, filename, text):
      item = self._bssFileToTreeItem[filename]
      
      output_line:QLineEdit = self.exportMappingTree.itemWidget(item, self.OutputFile)
      
      if text != output_line.current_text:
         prior_django_file = os.path.join(self.django_project_root, output_line.current_text)
         
         if os.path.exists(prior_django_file):
            self.remove_file_or_folder(prior_django_file)
            
         output_line.current_text = text
         output_line.setText(text)
         
   def set_django_root(self, root:str):
      if root != self._djangoRoot:
         self._djangoRoot = root
         
   def remove_file_or_folder(self, path):
      import shutil
      """ param <path> could either be relative or absolute. """
      if os.path.isfile(path) or os.path.islink(path):
         os.remove(path)  # remove the file
      elif os.path.isdir(path):
         shutil.rmtree(path)  # remove dir and all contains
      else:
         raise ValueError("file {} is not a file or dir.".format(path))   
      
   @property
   def prompt_for_each_new_file(self):
      return self.promptForNewFileCheck.isChecked()
   
   def bss_input_files(self, changes_only:bool=None):
      if changes_only is None:
         changes_only = self.onlyOnChangesCheck.isChecked()
         
      if not changes_only:
         return self._bssFileToTreeItem.keys()
      
      files = []
      
      for file in self._bssFileToTreeItem.keys():
         if self.modification_date(file) > self._lastExportTime:
            files.append(file)
            
      return files
   
   def bss_to_django_process_option(self, filename:str) -> str:
      item = self._bssFileToTreeItem[filename]
      item:QComboBox = self.exportMappingTree.itemWidget(item, self.ProcessOption)
      return item.currentText()
   
   def bss_to_django_tree_item(self, filename:str):
      item = self._bssFileToTreeItem[filename]
      return item
   
   def tree_to_dict(self) -> dict:
      d = {}      
      toplevel = []   
      for i in range(self.exportMappingTree.topLevelItemCount()):
         toplevel.append(self.exportMappingTree.topLevelItem(i))            
      for item in toplevel:
         c = self._addBranchToDict(item, d)
         self._treeToDict(item, c[2])      
      return d
   
   def _addBranchToDict(self, item:QTreeWidgetItem, d:dict):
      infile = item.text(self.InputFile)
      process_opt:QComboBox = self.exportMappingTree.itemWidget(item, self.ProcessOption)
      process_opt = process_opt.currentText()
      outfile:QLineEdit = self.exportMappingTree.itemWidget(item, self.OutputFile)
      outfile = outfile.text()
      c = d[infile] = (process_opt, outfile, {})        
      return c
   
   def _treeToDict(self, item0:QTreeWidgetItem, d:dict):
      for k in range(item0.childCount()):
         item = item0.child(k)
         c = self._addBranchToDict(item, d)
         self._treeToDict(item, c[2])        
   
   def tree_from_dict(self, d:dict, parent:QTreeWidgetItem=None):      
      bss_root = self._bssDesignExport         
      for infile, t in d.items():
         item_path = os.path.join(bss_root, infile)
         
         if os.path.exists(item_path):
            item, process_combo, output_line = self._treeItemFromDict(item_path, t)         
            
            if parent is None:
               self.exportMappingTree.addTopLevelItem(item)         
            else:
               parent.addChild(item)           
               
            self.exportMappingTree.setItemWidget(item, self.ProcessOption, process_combo)
            self.exportMappingTree.setItemWidget(item, self.OutputFile, output_line)     
            
            if self._lastExportTime is None or self.modification_date(item_path) > self._lastExportTime:
               change_label = QLabel()
               change_label.setPixmap(QPixmap(':/images/img/icons/pencil-24x24.png'))               
               self.exportMappingTree.setItemWidget(item, self.FileChanges, change_label)
               
            self.tree_from_dict(t[2], parent=item)

   def _treeItemFromDict(self, path:str, t:tuple):
      process_opt, outfile, c = t
      process_combo = QComboBox()
      process_combo.addItems(self.process_options)
      process_combo.setCurrentText(process_opt)
      output_line = QLineEdit()    
      infile = os.path.basename(path)
      output_line.setText(self.default_file_output_path(path))
      output_line.current_text = output_line.text()
      output_line.textEdited.connect(lambda text: self.django_output_line_edited(path, text))      
      item = QTreeWidgetItem([infile, None, None, None])      
      process_combo.currentTextChanged.connect(lambda text: self.bss_item_process_changed(item, path, process=text))
      self._bssFileToTreeItem[path] = item
      return item, process_combo, output_line
      
   @staticmethod
   def modification_date(filename):
      t = os.path.getmtime(filename)
      return datetime.fromtimestamp(t)   
   
   @property
   def last_export_time(self) -> datetime:
      return self._lastExportTime
   
   def set_last_export_time(self, time:datetime):
      self._lastExportTime = time
      
   def handle_file_exported_result(self, filename:str, result:str):
      item = self._bssFileToTreeItem[filename]
      changes_label:QLabel = self.exportMappingTree.itemWidget(item, self.FileChanges)
      
      if changes_label is None:
         changes_label = QLabel()         
      
      if result == "success":
         changes_label.setPixmap(QPixmap(':/images/img/icons/success-24x24.ico'))
      elif result == "error":
         changes_label.setPixmap(QPixmap(':/images/img/icons/error-24x24.ico'))
         
      self.exportMappingTree.setItemWidget(item, self.FileChanges, changes_label)
