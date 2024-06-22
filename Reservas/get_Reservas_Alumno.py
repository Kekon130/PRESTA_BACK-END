import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_RESERVAS_BY_ALUMNO_QUERY

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
            cursor = connection.cursor(dictionary=True)
            params = {
              'Alumno_ID': decoded_token['sub']
            }
            cursor.execute(GET_RESERVAS_BY_ALUMNO_QUERY, params)
            reservas = cursor.fetchall()
            
            if reservas:
              return {
                'statusCode': 200,
                'body': json.dumps({
                  'reservas': reservas
                })
              }
            else:
              return {
                'statusCode': 404,
                'body': json.dumps({
                  'message': 'The user has no reservations'
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
        'message': 'Internal Server Error'
      })
    }