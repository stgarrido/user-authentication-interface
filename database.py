import mariadb
from decouple import config

class Database():
  def __init__(self):
    try:
      self.connection = mariadb.connect(
        host = config('HOST'),
        port = config('PORT', cast=int),
        user = config('USER'),
        password = config('PASS')
      )
      self.cursor = self.connection.cursor()

      databaseQuery = "CREATE DATABASE IF NOT EXISTS user_authentication;"
      useQuery = "USE user_authentication;"
      usersTableQuery = '''
        CREATE TABLE IF NOT EXISTS users(
          id int NOT NULL auto_increment,
          name varchar(30) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (id)
        );
      '''
      photosTableQuery = '''
        CREATE TABLE IF NOT EXISTS photos(
          id int NOT NULL auto_increment,
          photo BLOB NOT NULL,
          user_id int NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
      '''
      self.cursor.execute(databaseQuery)
      self.cursor.execute(useQuery)
      self.cursor.execute(usersTableQuery)
      self.cursor.execute(photosTableQuery)
      print('Base de datos iniciada con éxito.')
    except mariadb.Error as ex:
      print('Error al intertar conectarse a la base de datos: ', ex)

  def add_user(self, username):
    try:
      userQuery = "INSERT INTO users(name) VALUE(%s);"
      self.cursor.execute(userQuery, [username])
      self.connection.commit()
      print('Usuario agregado con éxito.')
    except mariadb.Error as ex:
      print('Error al agregar usuario: ', ex)

  def add_photo(self, photo, username):
    try:
      photoQuery = '''
        INSERT INTO photos(photo, user_id)
        VALUE(%s, (SELECT id FROM users WHERE name = %s));
      '''
      self.cursor.execute(photoQuery, [photo, username])
      self.connection.commit()
      print('Foto agregada con éxito')
    except mariadb.Error as ex:
      print('Error al agregar foto de usuario: ', ex)

  def disconnect(self):
    self.cursor.close()
    self.connection.close()
    print('La conexión con la base de datos ha finalizado.')
