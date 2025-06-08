from PyQt6.QtWidgets import QApplication
import sys
from dialog.main_window import MainWindow
import os
from dotenv import load_dotenv

# Bugfix: the taskbar icon issue:
import ctypes
myappid = 'BS2Daisy' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == '__main__':
   load_dotenv() 
   app = QApplication([])

   if len(sys.argv) == 1:
      main_window = MainWindow.load_last_session_or_new()
      app.main_window = main_window
      main_window.show()
      main_window.export_mapper.load_any_new_bss_files()      
   else:
      main_window = MainWindow.try_loading_config_from_arg()
   
   sys.exit(app.exec())