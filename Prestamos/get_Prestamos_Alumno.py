import mysql.connector
import json
import hashlib
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_PRESTAMOS_BY_ALUMNO_QUERY

def lambda_handler(event, context):
  try:
    print(type(event['headers']))
    token = event['headers']['auth']
    
    if token is not None and token != ' ':
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
              pathParams = json.loads(event['pathParameters'])
              
            cursor = connection.cursor(dictionary=True)
            
            params = {
              'Alumno_ID': decoded_token['sub']
            }
            
            cursor.execute(GET_PRESTAMOS_BY_ALUMNO_QUERY, params)
            
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
  
  except KeyError as e:
    return {
      'statusCode': 401,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': 'Missing required parameters'
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
        'message': f'Internal server error: {str(e)}'
      })
    }