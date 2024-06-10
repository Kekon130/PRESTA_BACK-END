import mysql.connector
import json
import os
from jose import jwt

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if not token:
      return {
        'StatusCode': 401,
        'body': json.dumps('Unauthorized')
      }
      
    else:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' not in decoded_token or 'Gestores' not in decoded_token['cognito:groups']:
        return {
          'StatusCode': 401,
          'body': json.dumps('Unauthorized')
        }
      
      else:
        rds_host = os.getenv('RDS_HOST')
        rds_username = os.getenv('RDS_USERNAME')
        rds_password = os.getenv('RDS_PASSWORD')
        rds_db_name = os.getenv('RDS_DB_NAME')
        
        try:
          connection = mysql.connector.connect(
            host=rds_host,
            user=rds_username,
            password=rds_password,
            database=rds_db_name
          )
          
        except mysql.connector.Error as err:
          return {
            'StatusCode': 500,
            'body': json.dumps(f"Error connecting to database: {str(err)}")
          }
          
        if event['pathParameters'] is not None:
          query_params = event['pathParameters']
          
          table = query_params.get('type')
          
        try:
          cursor = connection.cursor(dictionary=True)
          
          if table == 'Libros':
            query = f'INSERT INTO {table} (Nombre, Cantidad, ISBN, Año_de_Publicacion, Asignatura) VALUES (%(Nombre)s, %(Cantidad)s, %(ISBN)s, %(Año_de_Publicacion)s, %(Asignatura)s)'
            
          elif table == 'Apuntes':
            query = f'INSERT INTO {table} (Nombre, Cantidad, Autor, Asignatura) VALUES (%(Nombre)s, %(Cantidad)s, %(Autor)s, %(Asignatura)s)'
            
          elif table == 'Calculadoras':
            query = f'INSERT INTO {table} (Nombre, Cantidad, Modelo) VALUES (%(Nombre)s, %(Cantidad)s, %(Modelo)s)'
            
          else:
            return {
              'StatusCode': 400,
              'body': json.dumps('Invalid table name')
            }
            
          cursor.execute(query, json.loads(event['body']))
          connection.commit()
          
          return {
            'StatusCode': 200,
            'body': json.dumps('Material has been added successfully')
          }
          
        except mysql.connector.Error as err:
          return {
            'StatusCode': 500,
            'body': json.dumps(f"Error querying database: {str(err)}")
          }
          
        finally:
          cursor.close()
          connection.close()
    
  except Exception as e:
    return {
      'StatusCode': 500,
      'body': json.dumps(f"Error getting token: {str(e)}")
    }