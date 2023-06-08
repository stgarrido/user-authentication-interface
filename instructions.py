from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi

class Instructions(QMainWindow):
  def __init__(self):
    super(Instructions, self).__init__()
    loadUi('interface/instructions.ui', self)
    self.setWindowIcon(QIcon('interface/images/escudo.png'))
    self.setStyleSheet('QMainWindow{background-image: url(interface/images/black.jpg)}')
    self.setWindowTitle('Instrucciones')
    self.pushButton.clicked.connect(self.cerrar)
    self.show()

  def cerrar(self):
    self.close()