from PyQt5.QtWidgets import QApplication
import sys
from dialog.main_window import MainWindow
import os

# Bugfix: the taskbar icon issue:
import ctypes
myappid = 'SoundUnited.ETMADB.version-3' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

os.environ['DEBUG'] = 'True'    # TODO: comment out for release

if __name__ == '__main__':
   app = QApplication([])

   if len(sys.argv) == 1:
      main_window = MainWindow.load_last_session_or_new()
      main_window.show()
   else:
      main_window = MainWindow.try_loading_config_from_arg()
   
   sys.exit(app.exec_())