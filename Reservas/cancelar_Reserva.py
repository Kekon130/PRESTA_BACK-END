import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, CANCELAR_RESERVA_QUERY
from utils_Reserva import Estado_Reserva

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and (Rol_Usuario.Gestores.value in decoded_token['cognito:groups'] or Rol_Usuario.Alumnos.value in decoded_token['cognito:groups']):
        try:
          connection = mysql.connector.connect(
            host=RDS_HOST,
            user=RDS_USERNAME,
            password=RDS_PASSWORD,
            database=RDS_DB_NAME
          )
          
          if connection.is_connected():
            if 'pathParameters' in event and event['pathParameters'] is not None:
              pathParams = event['pathParameters']
              
            cursor = connection.cursor(dictionary=True)
            
            params = {
              'Reserva_ID': pathParams['reservaID'],
              'Estado': Estado_Reserva.Cancelada.value
            }
            
            cursor.execute(CANCELAR_RESERVA_QUERY, params)
            
            connection.commit()
            
            return {
              'statusCode': 200,
              'body': json.dumps({
                'message': 'Reserva cancelada correctamente'
              })
            }
            
          else:
            return {
              'statusCode': 500,
              'body': json.dumps({
                'message': 'Internal Server Error'
              })
            }
            
        except mysql.connector.Error as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': 'Internal Server Error'
            })
          }
          
        finally:
          if connection.is_connected():
            cursor.close()
            connection.close()
            
      else:
        return {
          'statusCode': 403,
          'body': json.dumps({
            'message': 'Forbidden'
          })
        }
        
    else:
      return {
        'statusCode': 403,
        'body': json.dumps({
          'message': 'Forbidden'
        })
      }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': 'Internal Server Error'
      })
    }