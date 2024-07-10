import mysql.connector
import json
import hashlib
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
            
            if len(prestamos) > 0:
              etag = hashlib.md5(json.dumps(prestamos).encode('utf-8')).hexdigest()
              
              if 'headers' in event and 'If-None-Match' in event['headers'] and event['headers']['If-None-Match'] == etag:
                return {
                  'statusCode': 304,
                  'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type,auth,ETag',
                    'ETag': etag
                  }
                }
                
              else:
                return {
                  'statusCode': 200,
                  'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type,auth,ETag',
                    'ETag': etag
                  },
                  'body': json.dumps({
                    'prestamos': prestamos
                  })
                }
                
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'GET',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'El alumnos no tiene ningun prestamo'
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
            
        except mysql.connector.Error as e:
          return {
            'statusCode': 500,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': 'Internal Server Error'
            })
          }
          
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
        'message': f'Internal Server Error: {e}'
      })
    }