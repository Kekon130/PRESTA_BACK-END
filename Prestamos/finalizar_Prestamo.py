import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, FINALIZAR_PRESTAMO_QUERY
from utils_Prestamo import Estado_Prestamo
from datetime import datetime

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and (Rol_Usuario.Gestores.value in decoded_token['cognito:groups']):
        try:
          connection = mysql.connector.connect(
            host=RDS_HOST,
            user=RDS_USERNAME,
            password=RDS_PASSWORD,
            database=RDS_DB_NAME
          )
          
          if connection.is_connected():
            if 'pathParameters' in event and event['pathParameters'] is not None:
              path_params = event['pathParameters']
              
            cursor = connection.cursor()
            
            params = {
              'Prestamo_ID': path_params['prestamoID'],
              'Fecha_Expiracion': datetime.now().strftime('%Y-%m-%d'),
              'Estado': Estado_Prestamo.Devuelto.value
            }
            
            cursor.execute(FINALIZAR_PRESTAMO_QUERY, params)
            
            connection.commit()
            
            if cursor.rowcount > 0:
              return {
                'statusCode': 200,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'PUT',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Prestamo finalizado correctamente'
                })
              }
              
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'PUT',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Prestamo no encontrado'
                })
              }
            
          else:
            return {
              'statusCode': 500,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PUT',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Error connecting to database'
              })
            }
          
        except Exception as e:
          return {
            'statusCode': 500,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'PUT',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': f'Error finalizing prestamo: {e}'
            })
          }
          
        finally:
          if connection.is_connected():
            cursor.close()
            connection.close()
            
      else:
        return {
          'statusCode': 403,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT',
            'Access-Control-Allow-Headers': 'Content-Type,auth'
          },
          'body': json.dumps({
            'message': 'The user is not authorized to perform this operation'
          })
        }
        
    else:
      return {
        'statusCode': 401,
        'headers': {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'PUT',
          'Access-Control-Allow-Headers': 'Content-Type,auth'
        },
        'body': json.dumps({
          'message': 'Missing authentication token'
        })
      }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'PUT',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': f'Error finalizing prestamo: {e}'
      })
    }