import mysql.connector
from mysql.connector import Error
from decouple import config

class Database():
  def __init__(self):
    try:
      self.connection = mysql.connector.connect(
        host = config('HOST'),
        port = config('PORT'),
        user = config('USER'),
        password = config('PASS')
      )

      self.cursor = self.connection.cursor()

      databaseSentence = 'CREATE DATABASE IF NOT EXISTS user_authentication;'
      self.cursor.execute(databaseSentence)

      tableSentence = '''
        USE user_authentication;

        CREATE TABLE IF NOT EXISTS users(
          id int NOT NULL auto_increment,
          name varchar(30) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (id)
        );

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

      self.cursor.execute(tableSentence)

    except Error as ex:
      print('Error al iniciar la base de datos: ', ex)

def main():
  database = Database()

if __name__ == '__main__':
  main()