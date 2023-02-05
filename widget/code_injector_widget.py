from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QComboBox
from ui.ui_code_injector_widget import Ui_CodeInjectorWidget
from widget.export_mapper_widget import ExportMapperWidget
import types
import importlib
import os

InjectionSite, InputMatcher, InjectionFunction = range(3)

class CodeInjectorWidget(Ui_CodeInjectorWidget, QWidget):
   def __init__(self, file_mapper:ExportMapperWidget, pickled=False):
      super().__init__()
      super().__init__()
      self.setupUi(self) 
      
      self._exportMapper = file_mapper
      self._inplaceTree = None
      self._djangoFileTree = None
      
      if not pickled:         
         self.init_with_standard_injectors()
         self.finish_setup()
         
   def __setstate__(self, data):
      self.__init__(data['export mapper'], pickled=True)
      self.finish_setup()
      
   def __getstate__(self):
      return {
         'export mapper' : self._exportMapper
      }
   
   def finish_setup(self):
      pass
   
   def search_for_django_injection_sites(self):
      pass
   
   def init_with_standard_injectors(self, root=None):
      if root is None:
         root = QTreeWidgetItem(['Injectors'])
         self.tree.addTopLevelItem(root)
      
      for site, matcher, injector in self.standard_code_injection_mappings():
         self.create_tree_item(site, matcher, injector, parent=root)
         
   def create_tree_item(self, site, matcher, injector, parent:QTreeWidgetItem):     
      site_combo = QComboBox()
      site_combo.addItems(self.all_injection_sites())
      
      matcher_combo = QComboBox()
      matcher_combo.addItems(self.all_defined_matchers())
      
      injector_combo = QComboBox()
      injector_combo.addItems(self.all_defined_injectors())    
      
      item = QTreeWidgetItem([None, None, None])
      parent.addChild(item)
      
      self.tree.setItemWidget(item, InjectionSite, site_combo)
      self.tree.setItemWidget(item, InputMatcher, matcher_combo)
      self.tree.setItemWidget(item, InjectionFunction, injector_combo)
      
      return item
      
   @property
   def tree(self):
      return self.injectionSiteTree
   
   @property
   def export_mapper(self):
      return self._exportMapper
   
   def standard_injectors(self):
      module = importlib.import_module('core.standard_injectors')
      injectors = []
      
      for key in dir(module):
         attrib = getattr(module, key)
         
         if isinstance(attrib, types.FunctionType):
            injectors.append(attrib)
            
      return injectors
   
   def standard_code_injection_mappings(self):
      return self.standard_injectors()