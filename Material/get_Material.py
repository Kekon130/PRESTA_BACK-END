import mysql.connector
import json
from jose import jwt
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_LIBROS_QUERY, GET_APUNTES_QUERY, GET_CALCULADORAS_QUERY
from utils_Usuarios import Rol_Usuario

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
            
            cursor.execute(GET_LIBROS_QUERY)
            libros = cursor.fetchall()
            
            cursor.execute(GET_APUNTES_QUERY)
            apuntes = cursor.fetchall()
            
            cursor.execute(GET_CALCULADORAS_QUERY)
            calculadoras = cursor.fetchall()
            
            return {
              'statusCode': 200,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'libros': libros,
                'apuntes': apuntes,
                'calculadoras': calculadoras
              })
            }
            
          else:
            return {
              'statusCode': 500,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Error connecting to database'
              })
            }
            
        except mysql.connector.Error as err:
          return {
            'statusCode': 500,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': f"Error connecting to database: {str(err)}"
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
            'Access-Control-Allow-Methods': 'GET',
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
          'Access-Control-Allow-Methods': 'GET',
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
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': str(e)
      })
    }