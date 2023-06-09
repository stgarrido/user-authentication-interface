import os
import cv2
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import QTimer
from instructions import *
from database import *

# Valores default para una deteccion de rostro cualquiera
scale_factor = 1.2
min_neighbors = 5
min_size = (130, 130)
biggest_only = True
flags_ = cv2.CASCADE_FIND_BIGGEST_OBJECT | \
         cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else \
         cv2.CASCADE_SCALE_IMAGE

class Register(QMainWindow):
  def __init__(self):
    super(Register, self).__init__()
    loadUi('interface/registro.ui', self)
    self.setWindowIcon(QIcon('interface/images/camara.jpg'))
    self.setStyleSheet('QMainWindow{background-image: url(interface/images/blue.jpg)}')
    self.setWindowTitle('Registro')
    # CLASIFICADOR
    self.detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')    # Carga el clasificador detector
    # BASE DE DATOS
    self.database = Database()
    # VARIABLES AUXILIARES
    self.cam = False
    self.cont = 0
    # INTERFAZ
    self.show()
    # CONEXIONES CON BOTONES
    self.comenzar.clicked.connect(self.comienzo)
    self.informacion.clicked.connect(self.informaciones)
    self.salir.clicked.connect(self.salida)
    # CREACION CARPETA DE USUARIO
    self.nombre, ok = QInputDialog.getText(self, 'Registro', 'Ingrese el nombre del nuevo usuario: ')
    self.database.add_user(self.nombre)
    dir_proyecto = os.path.dirname(os.path.abspath(__file__))   # Obtiene directorio del .py
    dir_imagenes = os.path.join(dir_proyecto, 'Fotos')          # Crea la carpeta fotos
    self.carp_usu = dir_imagenes + '/' + self.nombre            # Añade el nombre para el directo del usuario
    if not os.path.exists(self.carp_usu):                       # Crea la carpeta de usuario
      os.makedirs(self.carp_usu)

  def comienzo(self):
    if self.cam:
      self.advertencia()
    else:
      self.cam = True
      self.camara = cv2.VideoCapture(0)
      # Contador que muestra cada 1ms un frame de la camara
      self.timer = QTimer(self)
      self.timer.timeout.connect(self.grabar)
      self.timer.start(1)

  def grabar(self):
    ret, frame = self.camara.read()
    pos_cara = self.detector.detectMultiScale(frame,
                                              scaleFactor = scale_factor,
                                              minNeighbors = min_neighbors,
                                              minSize = min_size, flags = flags_)
    for (x,y,w,h) in pos_cara:
      cv2.rectangle(frame, (x, y), (x + w, y + h), (250, 0, 0), 2)
      cv2.putText(frame, 'Registrando a ' + self.nombre, (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (250,0,0), cv2.LINE_4)
      cara = frame[y: y + h, x: x + w]                # Recorta la cara
      cara = cv2.cvtColor(cara, cv2.COLOR_BGR2GRAY)   # Pasa a escala de grises
      if cara.shape < (130,130):                      # Redimensiona la cara
        cara = cv2.resize(cara, (130,130), interpolation=cv2.INTER_LINEAR) # INTER_CUBIC
      elif cara.shape > (130,130):
        cara = cv2.resize(cara, (130,130), interpolation=cv2.INTER_AREA)
      nombre_foto = self.nombre + str(self.cont) + '.png'     # Asigna nombre a la cara
      cv2.imwrite(self.carp_usu + '/' + nombre_foto, cara)   # Guarda la cara
      self.database.add_photo(cara, self.nombre)
      self.cont += 1
    if self.cam:
      frame =QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
      frame = frame.rgbSwapped()
      self.label.setPixmap(QPixmap.fromImage(frame))

  def informaciones(self):
    self.info = Instructions()

  def salida(self):
    if self.cam:
      self.cam = False
      self.camara.release()
    self.close()
    self.database.disconnect()

  def advertencia(self):          # Avisa que el programa ya esta funcionando
    QMessageBox.information(self, 'Informacion', 'El programa ya está registrando', QMessageBox.Ok)