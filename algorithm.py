import cv2
import os
import numpy as np

capture = cv2.VideoCapture(0)

# Carga el modelo entrenado que detecta rostros cualquiera
detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') # Carga el detector de caras

cont = 0    # Contador para agregar al nombre de la persona

# Crea la carpeta para almacenar las fotos
dir_proyecto = os.path.dirname(os.path.abspath(__file__))   # Directorio .py
dir_imagenes = os.path.join(dir_proyecto, 'Fotos')          # Agrega la carpeta Fotos
carp_usu = dir_imagenes + '/Usuario'                        # Agrega la carpeta del usuario especifico
if not os.path.exists(carp_usu):                            # Crea la carpeta Fotos
  os.makedirs(carp_usu)

# RECOLECTA LAS FOTOS DE UN USUARIO
while(True):
  ret, frame = capture.read()

  # Valores default para una deteccion de rostro cualquiera
  scale_factor = 1.2
  min_neighbors = 5
  min_size = (130, 130)
  biggest_only = True
  flags = cv2.CASCADE_FIND_BIGGEST_OBJECT | \
            cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else \
            cv2.CASCADE_SCALE_IMAGE

  # Convierte la imagen de la camara en blanco y negro
  grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # Obtiene la posicion de la cara en la imagen
  pos_cara = detector.detectMultiScale(grayscale, 
                                       scaleFactor = scale_factor, 
                                       minNeighbors = min_neighbors, 
                                       minSize = min_size, 
                                       flags = flags)

  # Si detecta un rostro cualquiera dibuja un rectangulo en su posicion
  for (x,y,i,j) in pos_cara:
    # Crea el marco para la cara
    i_rm = int(0.2 * i / 2)             #Crea un pequeño espacio mas grande para el rostro
    cv2.rectangle(frame, (x,y), (x+i,y+j), (255,0,0),2)
    cv2.putText(frame, 'Registrando a Usuario', (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (250,0,0), cv2.LINE_4)

    # Guarda el rostro en una imagen .png
    cara = grayscale[y: y + j, x + i_rm: x + i - i_rm]  # Recorta la cara en un frame gris
    cara = cv2.equalizeHist(cara)                       # Normaliza la cara
    
    # Redimensiona la imagen a una resolucion de 130x130
    if cara.shape < (130,130):                      
      cara_recortada = cv2.resize(cara, (130,130), interpolation = cv2.INTER_AREA)    # Agranda la imagen
    else:
      cara_recortada = cv2.resize(cara, (130,130), interpolation = cv2.INTER_CUBIC)   # Achica la imagen

    # Almacena el rostro en un directorio especifico
    nombre_cara = 'Usuario' + str(cont) + '.png'             # Se asigna el nombre de la imagen
    # cv2.imwrite(carp_usu+'\\'+nombre_cara, cara_recortada)  # Guarda la imagen
    cv2.imwrite(carp_usu+'/'+nombre_cara, cara_recortada)  # Guarda la imagen
    cont += 1

  cv2.imshow('Camara', frame)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Almacena los datos en un diccionario
fotos = []          # Almacena las fotos 
nombres = []        # Almacena el numero entero que corresponde al nombre
nombres_dicc = {}   # Almacena la relacion Numerp-Nombre para la posterior identificacion
personas = [persona for persona in os.listdir('Fotos/')]

for i, persona in enumerate(personas):
  nombres_dicc[i] = persona
  for imagen in os.listdir('Fotos/' + persona):
    fotos.append(cv2.imread('Fotos/' + persona + '/' + imagen, 0))
    nombres.append(i)
  nombres = np.array(nombres)

# Entrena el modelo con los datos almacenados
modelo_lpbh = cv2.face.LBPHFaceRecognizer_create()  # Crea el modelo con lpbh
modelo_lpbh.train(fotos, nombres)

# DETECCION CON EL MODELO ENTRENADO ANTERIORMENTE
while(True):
  ret, frame = capture.read()

  # Valores default para una deteccion de rostro cualquiera
  scale_factor = 1.2
  min_neighbors = 5
  min_size = (130, 130)
  biggest_only = True
  flags = cv2.CASCADE_FIND_BIGGEST_OBJECT | \
            cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else \
            cv2.CASCADE_SCALE_IMAGE

  # Convierte la imagen de la camara en blanco y negro
  grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # Obtiene la posicion de la cara en la imagen
  pos_cara = detector.detectMultiScale(grayscale, 
                                       scaleFactor = scale_factor, 
                                       minNeighbors = min_neighbors, 
                                       minSize = min_size, 
                                       flags = flags)
    
  for (x,y,w,h) in pos_cara:
    w_rm = int(0.2 * w/2)
    cara = grayscale[y: y + h, w + w_rm: x + w - w_rm]  # Recorta la posicion de la cara en el frame gris
    cara = cv2.equalizeHist(cara)                       # Normaliza la imagen
    print(type(cara))
    if type(cara) == np.ndarray:
      if cara.shape < (130, 130):                         # Reescala la cara a 130x130
        cara = cv2.resize(cara, (130, 130), interpolation = cv2.INTER_AREA)
      elif cara.shape > (130, 130):
        cara = cv2.resize(cara, (130, 130), interpolation = cv2.INTER_CUBIC)

      result = modelo_lpbh.predict(cara)  # Busca la foto mas parecida en el modelo entrado
                                      # result es un arreglo de 2 valores: La etiqueta y el valor de distancia
      for i, face in enumerate(cara):
        if len(fotos) == 0:
          cv2.putText(frame, 'Desconocido', (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (0,0,250), cv2.LINE_4)
          cv2.rectangle(frame, (x+w_rm, y), (x+w-w_rm, y+h), (0,0,250), 2)
        else:
          if result[1] < 90:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            cv2.putText(frame, nombres_dicc[result[0]], (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (250,0,0), cv2.LINE_4)
          else:
            cv2.putText(frame, 'Desconocido', (pos_cara[0][0], pos_cara[0][1]-5), cv2.FONT_ITALIC, 1, (0,0,250), cv2.LINE_4)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
  cv2.imshow('Camara', frame)
  if cv2.waitKey(1) & 0xFF == ord('w'):
    break

capture.release()
cv2.destroyAllWindows()