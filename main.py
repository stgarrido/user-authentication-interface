import sys
from PyQt5.QtWidgets import QApplication
from interface import *

def main():
  app = QApplication(sys.argv)
  application = MainProgram()
  application.setWindowTitle('Autenticación de usuario')
  application.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()