import utils_BD
import mysql.connector

def checkIfMaterialExists(materialName, type):
  try:
    connection = mysql.connector.connect(
      host=utils_BD.RDS_HOST,
      user=utils_BD.RDS_USERNAME,
      password=utils_BD.RDS_PASSWORD,
      database=utils_BD.RDS_DB_NAME
    )
    
    if connection.is_connected():
      cursor = connection.cursor(dictionary=True)
      
      query = f"SELECT * FROM {type} WHERE Nombre = '{materialName}'"
      
      cursor.execute(query)
      
      material = cursor.fetchone()
      
      if material:
        return material['ID']
      
      else:
        return None
      
    else:
      return None
    
  except mysql.connector.Error as err:
    print(f"Error connecting to database: {str(err)}")
    return None
  
  finally:
    if connection.is_connected():
      connection.close()
      cursor.close()