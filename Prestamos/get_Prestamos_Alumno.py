import mysql.connector
import json
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
            
            return {
                'statusCode': 200,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'GET'
                },
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
          
        except mysql.connector.Error as err:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': f"Error connecting to database: {str(err)}"
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
  
  except KeyError as e:
    return {
      'statusCode': 401,
      'body': json.dumps({
        'message': 'Missing required parameters'
      })
    }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f'Internal server error: {str(e)}'
      })
    }