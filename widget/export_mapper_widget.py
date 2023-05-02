from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QLineEdit, QComboBox, QLabel, QApplication, QTreeWidget
from ui.ui_export_mapper_widget import Ui_ExportMapperWidget
import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from datetime import datetime
from core.tools import standard_path
import stringcase
from widget.code_generation_widget import CodeGenerationWidget
from code_gen.view_generator import ViewGenerator

class ExportMapperWidget(Ui_ExportMapperWidget, QWidget):
   bss_to_django_folder = 'BSSToDjango'
   boilerplates_folder = 'DjangoBoilerplates'
   
   bss_assets_subfolders = {'bootstrap', 'js', 'css', 'img'}
   default_ignore_bss_files = {'error.log', '.bss-to-django-config.pkl'}
   process_options = ['Ignore', 'BSS to Django', 'Copy Over']
   image_file_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.svg'}
   
   # TODO: font formats: ttf, woff, woff2, eot => Copy Over
   
   file_moved_or_deleted = pyqtSignal(str)
   file_added = pyqtSignal(str)
   status_message_signal = pyqtSignal(str)
   jump_to_code_file_line_requested = pyqtSignal(str, int)
   
   InputFile, FileChanges, ProcessOption, OutputFile, DjangoURL, DjangoView, CodeGeneration = range(7)
   TreeIndex = 5
   
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
      self.expandWholeTreeButton.clicked.connect(self.expand_whole_tree)
      self.boilerplateViewsButton.clicked.connect(lambda: self.jump_to_boilerplates('views.py'))
      self.boilerplateURLsButton.clicked.connect(lambda: self.jump_to_boilerplates('urls.py'))
      
   def expand_whole_tree(self):
      self.tree.expandAll()
      self.resize_tree_columns_to_fit_contents()
   
   def create_new_bss_tree_item(self, filename:str) -> QTreeWidgetItem:
      process_combo = QComboBox()
      process_combo.addItems(self.process_options)
            
      output_line = QLineEdit()
      output_line.setText(self.default_file_output_path(filename))
      output_line.current_text = output_line.text()
      output_line.textEdited.connect(lambda text: self.django_output_line_edited(filename, text))
   
      django_url_line = QLineEdit()
      django_url_line.setText(self.default_django_url(filename))
      django_url_line.current_text = django_url_line.text()
      django_url_line.textEdited.connect(lambda text: self.django_url_line_edited(filename, text))
      
      if self.is_html_file(filename):
         django_view_line = QLineEdit()
         django_view_line.setText(self.default_django_view(filename))
         django_view_line.current_text = django_view_line.text()
         django_view_line.textEdited.connect(lambda text: self.django_view_line_edited(filename, text))
         code_generation = self.create_code_generation_widget(filename)
      else:
         django_view_line = None
         code_generation = None
      
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
         
      item = QTreeWidgetItem([os.path.basename(filename), None, None, None, None])      
      
      process_combo.currentTextChanged.connect(lambda text: self.bss_item_process_changed(item, filename, process=text))
      
      self._bssFileToTreeItem[filename] = item
      directory = os.path.dirname(filename)   
      
      if directory in self._bssFileToTreeItem:
         parent:QTreeWidgetItem = self._bssFileToTreeItem[directory]
         parent.addChild(item)
      elif directory == self._bssDesignExport:
         self.tree.addTopLevelItem(item)   
         
      change_label = QLabel()
      change_label.setPixmap(QPixmap(':/images/img/icons/add-file24x24.png'))
         
      self.tree.setItemWidget(item, self.ProcessOption, process_combo)   
      self.tree.setItemWidget(item, self.OutputFile, output_line)
      self.tree.setItemWidget(item, self.FileChanges, change_label)
      self.tree.setItemWidget(item, self.DjangoURL, django_url_line)
      
      if django_view_line:
         self.tree.setItemWidget(item, self.DjangoView, django_view_line)
      
      if code_generation:
         self.tree.setItemWidget(item, self.CodeGeneration, code_generation)
      
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
         self.resize_tree_columns_to_fit_contents()
               
   def bss_item_process_changed(self, item, filename, process:str):
      if process == 'Ignore':
         if filename not in self._ignoreBSSFiles:
            self._ignoreBSSFiles.add(filename)
      else:    
         if filename in self._ignoreBSSFiles:
            self._ignoreBSSFiles.remove(filename)
            
   def default_file_output_path(self, bss_filename:str):      
      rel_bss_filename = self.filename_rel_root(bss_filename)
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
                              return os.path.join(app_name, 'static', app_name, subfolder, *parts[3:])
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
                  return os.path.join(folder_name, 'templates', *parts)
               else:
                  return os.path.join(folder_name, 'templates')
               
            elif os.path.isfile(rel_path):
               return os.path.join('templates', *parts[0:])
      return "/"
            
   def default_django_url(self, bss_filename:str):       
      rel_bss_filename = self.filename_rel_root(bss_filename)
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
                              return standard_path(self.remove_dot_html(os.path.join(app_name, subfolder, *parts[3:])))
                           elif os.path.isfile(rel_path):
                              return standard_path(self.remove_dot_html(os.path.join(subfolder, *parts[2:])))
                        else:
                           return standard_path(subfolder)
                     else:
                        return standard_path(self.remove_dot_html(os.path.join(subfolder, *parts[2:])))
                           
                  else:
                     return standard_path(self.remove_dot_html(os.path.join(subfolder, *parts[2:])))
                  
               else:
                  return standard_path(self.remove_dot_html(os.path.join(*parts[1:])))
            else:
               return standard_path('/')
         else:
            rel_path = os.path.join(bss_root, parts[0])
            
            if os.path.isdir(rel_path):
               folder_name = parts[0]
               
               if len(parts) > 1:
                  return standard_path(self.remove_dot_html(os.path.join(folder_name, *parts[1:])))
               else:
                  return standard_path(folder_name)
               
            elif os.path.isfile(rel_path):
               return standard_path(self.remove_dot_html(os.path.join(*parts[0:])))
      return standard_path("/")
   
   def default_django_view(self, bss_filename:str):
      identifier = self.default_django_url(bss_filename)
      parts = identifier.split(sep="/")
      parts = [stringcase.snakecase(x) for x in parts]
      #identifier = "/".join(parts)
      identifier = parts[-1]
      return identifier
               
   def filename_rel_root(self, filename:str, root:str=None) -> str:
      if root is None:
         root = self._bssDesignExport
         
      drive, rest = os.path.splitdrive(filename)
      parts = os.path.normpath(rest)
      parts = parts.split(os.sep)
         
      for i in range(1, len(parts)):
         test_directory = f'{drive}{os.sep}{os.path.join(*parts[0:i])}'
         
         if os.path.samefile(test_directory, root):
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
      outfile = self.tree.itemWidget(item, self.OutputFile)
      outfile = outfile.text()
      return os.path.join(self.django_project_root, outfile)
   
   def django_view_name_mapping(self, bss_file:str):
      item = self._bssFileToTreeItem[bss_file]
      line_edit = self.tree.itemWidget(item, self.DjangoView)
      return line_edit.text()
   
   def code_generation_mapping(self, bss_file:str):
      item = self._bssFileToTreeItem[bss_file]
      code_gen_widget = self.tree.itemWidget(item, self.CodeGeneration)
      return code_gen_widget
   
   def check_for_bss_file_structure_changes(self):
      for filename in dict(self._bssFileToTreeItem):
         if not os.path.exists(filename):  # It's been deleted or moved
            item:QTreeWidgetItem = self._bssFileToTreeItem[filename]
            django_file = self.tree.itemWidget(item, self.OutputFile)
            django_file = django_file.text()
            self.remove_file_or_folder(django_file)
            del self._bssFileToTreeItem[filename]
            item.parent().removeChild(item)
            del item
            self.file_moved_or_deleted.emit(filename)
            
      self.load_any_new_bss_files()
      
   def django_output_line_edited(self, filename, text):
      item = self._bssFileToTreeItem[filename]
      
      output_line:QLineEdit = self.tree.itemWidget(item, self.OutputFile)
      
      if text != output_line.current_text:
         prior_django_file = os.path.join(self.django_project_root, output_line.current_text)
         
         if os.path.exists(prior_django_file):
            self.remove_file_or_folder(prior_django_file)
            
         output_line.current_text = text
         
   def django_url_line_edited(self, filename, text):
      item = self._bssFileToTreeItem[filename]
      django_url_line:QLineEdit = self.tree.itemWidget(item, self.DjangoURL)
      
      if text != django_url_line.current_text:
         django_url_line.current_text = text
         
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
      item:QComboBox = self.tree.itemWidget(item, self.ProcessOption)
      return item.currentText()
   
   def bss_to_django_tree_item(self, filename:str):
      item = self._bssFileToTreeItem[filename]
      return item
   
   def tree_to_dict(self) -> dict:
      d = {}      
      toplevel = []   
      for i in range(self.tree.topLevelItemCount()):
         toplevel.append(self.tree.topLevelItem(i))            
      for item in toplevel:
         c = self._addBranchToDict(item, d)
         self._treeToDict(item, c[self.TreeIndex])      
      return d
   
   def _addBranchToDict(self, item:QTreeWidgetItem, d:dict):
      infile = item.text(self.InputFile)
      process_opt:QComboBox = self.tree.itemWidget(item, self.ProcessOption)
      process_opt = process_opt.currentText()
      outfile:QLineEdit = self.tree.itemWidget(item, self.OutputFile)
      outfile = outfile.text()
      django_url:QLineEdit = self.tree.itemWidget(item, self.DjangoURL)
      django_url = django_url.text()
      django_view:QLineEdit = self.tree.itemWidget(item, self.DjangoView)
      code_gen:CodeGenerationWidget = self.tree.itemWidget(item, self.CodeGeneration)
      
      if django_view:
         django_view = django_view.text()
      c = d[infile] = (process_opt, outfile, django_url, django_view, code_gen, {})        
      return c
   
   def _treeToDict(self, item0:QTreeWidgetItem, d:dict):
      for k in range(item0.childCount()):
         item = item0.child(k)
         c = self._addBranchToDict(item, d)
         self._treeToDict(item, c[self.TreeIndex])        
   
   def tree_from_dict(self, d:dict, parent:QTreeWidgetItem=None, path=None):      
      bss_root = self._bssDesignExport  
   
      if path is None:
         path = bss_root
         
      for infile, t in d.items():
         item_path = os.path.join(path, infile)
         
         if os.path.exists(item_path):
            item, process_combo, output_line, django_url_line, django_view_line, code_generation = self._treeItemFromDict(item_path, t)         
            
            if parent is None:
               self.tree.addTopLevelItem(item)         
            else:
               parent.addChild(item)           
               
            self.tree.setItemWidget(item, self.ProcessOption, process_combo)
            self.tree.setItemWidget(item, self.OutputFile, output_line)    
            self.tree.setItemWidget(item, self.DjangoURL, django_url_line)
            
            if django_view_line:
               self.tree.setItemWidget(item, self.DjangoView, django_view_line)    
               
            if code_generation:
               self.tree.setItemWidget(item, self.CodeGeneration, code_generation)
            
            if self._lastExportTime is None or self.modification_date(item_path) > self._lastExportTime:
               change_label = QLabel()
               change_label.setPixmap(QPixmap(':/images/img/icons/pencil-24x24.png'))               
               self.tree.setItemWidget(item, self.FileChanges, change_label)
               
            self.tree_from_dict(t[self.TreeIndex], parent=item, path=item_path)
      self.resize_tree_columns_to_fit_contents()

   def _treeItemFromDict(self, path:str, t:tuple):
      process_opt, outfile, django_url, django_view, code_generation, c = t
      process_combo = QComboBox()
      process_combo.addItems(self.process_options)
      process_combo.setCurrentText(process_opt)
      output_line = QLineEdit()    
      infile = os.path.basename(path)
      output_line.setText(outfile)
      output_line.current_text = output_line.text()
      output_line.textEdited.connect(lambda text: self.django_output_line_edited(path, text))   
      django_url_line = QLineEdit()
      django_url_line.setText(django_url)
      django_url_line.current_text = django_url_line.text()
      django_url_line.textEdited.connect(lambda text: self.django_url_line_edited(path, text))
            
      if self.is_html_file(path):
         django_view_line = QLineEdit()
         django_view_line.setText(django_view)
         django_view_line.current_text = django_view_line.text()
         #django_view_line.textEdited.connect(lambda text: self.django_view_line_edited(path, text))
      else:
         django_view_line = None
         
      if code_generation:
         code_generation.populate_boilerplate_combo_boxes()
         self.connect_code_generation_widget(code_generation)
         
      item = QTreeWidgetItem([infile, None, None, None, None, None])      
      process_combo.currentTextChanged.connect(lambda text: self.bss_item_process_changed(item, path, process=text))
      self._bssFileToTreeItem[path] = item
      return item, process_combo, output_line, django_url_line, django_view_line, code_generation
      
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
      changes_label:QLabel = self.tree.itemWidget(item, self.FileChanges)
      
      if changes_label is None:
         changes_label = QLabel()         
      
      if result == "success":
         changes_label.setPixmap(QPixmap(':/images/img/icons/success-24x24.ico'))
      elif result == "error":
         changes_label.setPixmap(QPixmap(':/images/img/icons/error-24x24.ico'))
         
      self.tree.setItemWidget(item, self.FileChanges, changes_label)

   def bss_input_file_exists(self, rel_filename:str):
      if rel_filename.startswith('/'):
         rel_filename = rel_filename[1:]
      filename = os.path.join(self.bss_design_root, rel_filename)
      filename = standard_path(filename, os.sep)
      return filename in self._bssFileToTreeItem
   
   def django_template_url(self, bss_filename:str):
      if bss_filename.startswith('#'):
         return bss_filename
      bss_root = self.bss_design_root
      if bss_filename.startswith('/') or bss_filename.startswith('\\'):
         bss_filename = bss_filename[1:]
      bss_path = os.path.join(bss_root, bss_filename)
      bss_path = standard_path(bss_path, sep=os.sep)
      if bss_path in self._bssFileToTreeItem:
         item = self._bssFileToTreeItem[bss_path]
         widget:QLineEdit = self.tree.itemWidget(item, self.DjangoURL)
         django_url = widget.text()
         django_url = standard_path(self.remove_dot_html(django_url))
         return django_url
      else:
         self.status_message_signal.emit(f"Broken link detected on the BSS side. Did you create {bss_filename} yet?")
         return bss_filename
   
   def remove_dot_html(self, filename:str):
      if filename.endswith('.html'):
         filename = filename[:-len('.html')]
      return filename
   
   def is_html_file(self, filename:str):
      return filename.endswith('.html')
   
   @property
   def tree(self) -> QTreeWidget:
      return self.exportMappingTree
   
   def resize_tree_columns_to_fit_contents(self):
      for i in range(self.tree.columnCount()):
         self.tree.resizeColumnToContents(i)
         
   def create_code_generation_widget(self, input_file:str):
      code_gen_widget = CodeGenerationWidget(input_file, export_mapper=self)
      code_gen_widget.populate_boilerplate_combo_boxes(init=True)
      self.connect_code_generation_widget(code_gen_widget)
      return code_gen_widget
   
   def connect_code_generation_widget(self, code_gen_widget:CodeGenerationWidget):
      code_gen_widget.status_message_signal.connect(self.status_message_signal.emit)
      code_gen_widget.jump_to_code_file_line_requested.connect(self.jump_to_code_file_line_requested.emit)
      
   def jump_to_boilerplates(self, filename:str):
      self.jump_to_code_file_line_requested.emit(os.path.join(self.django_boilerplates_folder, filename), 1)

   @property
   def absolute_bss_to_django_folder(self):
      return os.path.join(self.django_project_root, self.bss_to_django_folder)
   
   @property
   def django_boilerplates_folder(self):
      return os.path.join(self.absolute_bss_to_django_folder, self.boilerplates_folder)
   
   def django_boilerplates_filename(self, basename:str) -> str:
      return os.path.join(self.django_boilerplates_folder, basename)