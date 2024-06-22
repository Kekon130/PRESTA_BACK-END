import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_PRESTAMOS_QUERY

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    print('hay token')
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      print('el token es valido')
      
      if 'cognito:groups' in decoded_token and (Rol_Usuario.Gestores.value in decoded_token['cognito:groups']):
        try:
          print('conectando a la base de datos')
          connection = mysql.connector.connect(
            host=RDS_HOST,
            user=RDS_USERNAME,
            password=RDS_PASSWORD,
            database=RDS_DB_NAME
          )
          
          if connection.is_connected():
            print('conectado a la base de datos')
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(GET_PRESTAMOS_QUERY)
            
            prestamos = cursor.fetchall()
            
            return {
              'statusCode': 200,
              'body': json.dumps({
                'Prestamos': prestamos
              })
            }
            
          else:
            return {
              'statusCode': 500,
              'body': json.dumps({
                'message': 'Error connecting to database'
              })
            }
            
        except mysql.connector.Error as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': 'Internal Server Error'
            })
          }
          
      else:
        return {
          'statusCode': 403,
          'body': json.dumps({
            'message': 'The user is not authorized to perform this operation'
          })
        }
        
    else:
      return {
        'statusCode': 401,
        'body': json.dumps({
          'message': 'Missing authentication token'
        })
      }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f'Internal Server Error: {e}'
      })
    }