import os
import cv2
import numpy as np
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from register import *

# Valores default para una deteccion de rostro cualquiera
scale_factor = 1.2
min_neighbors = 5
min_size = (130, 130)
biggest_only = True
flags_ = cv2.CASCADE_FIND_BIGGEST_OBJECT | \
         cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else \
         cv2.CASCADE_SCALE_IMAGE

class MainProgram(QMainWindow):
	def __init__(self):
		super(MainProgram, self).__init__()
		loadUi('interfaz/interfaz.ui', self)
		self.setWindowIcon(QIcon('interfaz/escudo.png'))
		self.setStyleSheet('QMainWindow{background-image: url(interfaz/blue.jpg)}')
		# CLASIFICADOR
		self.detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')    # Carga el clasificador detector
		# PARA INICIAR EL PROGRAMA ENTRENADO
		# No lo he querido agregar hasta que termine de transcribir el programa
		# VARIABLES AUXILIARES
		self.cam = False
		self.cont_int = 0
		self.cont_ini = 0
		self.fotos = []
		self.nombres = []
		self.nombres_dic = {}
		# CONEXIONES CON BOTONES
		self.encender.clicked.connect(self.grabar)
		self.detener.clicked.connect(self.quitar)
		self.registrarse.clicked.connect(self.registrar)
		self.actualizar.clicked.connect(self.actual)
		self.salir.clicked.connect(self.salida)
		self.lomito()
		self.label_2.setPixmap(QPixmap('interfaz/logo_eln.png'))

	def lomito(self):
		self.figura = cv2.imread('interfaz/figura.jpg')
		self.figura = cv2.resize(self.figura, (640, 480), interpolation = cv2.INTER_CUBIC)
		self.figura = QImage(self.figura, self.figura.shape[1], self.figura.shape[0], QImage.Format_RGB888)
		self.figura = self.figura.rgbSwapped()
		self.label.setPixmap(QPixmap.fromImage(self.figura))

	# FUNCIONES DE BOTONES
	# Inicia el programa
	def grabar(self):
		if self.cam:
			self.advertencia1()
		else:
			self.cont_init = 0
			self.cam = True
			self.camara = cv2.VideoCapture(0)
			# Contador que muestra cada 20ms un frame de la camara
			self.timer = QTimer(self)
			self.timer.timeout.connect(self.mostrar)
			self.timer.start(20)
    
	#Enciende la camara
	def mostrar(self):
		ret, frame = self.camara.read()
		if ret == False:
			return True
		# Convierte la imagen de la camara en blanco y negro
		grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Obtiene la posicion de la cara en la imagen
		pos_cara = self.detector.detectMultiScale(grayscale, 
																							scaleFactor = scale_factor, 
																							minNeighbors = min_neighbors, 
																							minSize = min_size, 
																							flags = flags_)
		# Dibujo de rectangulo en las caras detectadas
		for (x,y,w,h) in pos_cara:
			# Recorte
			self.caras = grayscale[y: y + h, x: x + w]
			# Reescalar
			if self.caras.shape < (130,130):
				self.caras = cv2.resize(self.caras, (130,130), interpolation=cv2.INTER_LINEAR) # INTER_CUBIC
			elif self.caras.shape > (130,130):
				self.caras = cv2.resize(self.caras, (130,130), interpolation=cv2.INTER_AREA)
			# Deteccion
			if len(self.fotos) == 0:
				cv2.putText(frame, 'Desconocido', (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (0,0,250), cv2.LINE_4)
				cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,250), 2)
			else:
				self.result = self.model_lpbh.predict(self.caras)
				if self.result[1] < 90:
					cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
					cv2.putText(frame, self.nombres_dic[self.result[0]], (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (250,0,0), cv2.LINE_4)
				else:
					cv2.putText(frame, 'Desconocido', (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (0,0,250), cv2.LINE_4)
					cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,250), 2)
		frame = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
		frame = frame.rgbSwapped()
		self.label.setPixmap(QPixmap.fromImage(frame))

	# Apaga la camara
	def quitar(self):
		if self.cam:
			self.cam = False
			self.camara.release()
			self.lomito()
		else:
			self.advertencia2()

	# Registra un nuevo usuario
	def registrar(self):
		self.ventana2 = Register()
		if self.cam:
			self.cam = False
			self.camara.release()
			self.lomito()

	# Entrena el modelo
	def actual(self):
		if len(os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/Fotos')) == 0:
			self.advertencia3()
		else:
			# Se juntan los datos
			personas = [persona for persona in os.listdir('Fotos/')]
			for i, persona in enumerate(personas):
				self.nombres_dic[i] = persona
				for imagen in os.listdir('Fotos/' + persona):
					self.fotos.append(cv2.imread('Fotos/' + persona + '/' + imagen, 0))
					self.nombres.append(i)
			self.nombres = np.array(self.nombres)
			# Entrena el modelo
			self.model_lpbh = cv2.face.LBPHFaceRecognizer_create()  # Crea el modelo
			self.model_lpbh.train(self.fotos, self.nombres)         # Entrena el modelo
			self.advertencia4()

	# Cierra el programa en modo seguro (apaga la camara)
	def salida(self):
		salida = QMessageBox.question(self, 'Advertencia', '¿Desea cerrar el programa?\nTodo el proceso se perderá',
																	QMessageBox.Yes, QMessageBox.No)
		if salida == QMessageBox.Yes:
			if self.cam:
				self.cam = False
				self.camara.release()
			self.close()

	# CUADROS DE ADVERTENCIA
	def advertencia1(self):
		QMessageBox.information(self, 'Información', 'El programa ya está identificando', QMessageBox.Ok)
    
	def advertencia2(self):
		QMessageBox.information(self, 'Error', 'La cámara ya está apagada', QMessageBox.Ok)

	def advertencia3(self):
		QMessageBox.information(self, 'Error', 'El directorio está vacío', QMessageBox.Ok)
	
	def advertencia4(self):
		QMessageBox.information(self, 'Listo', 'La base de datos fue actualizada correctamente', QMessageBox.Ok)