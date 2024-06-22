import mysql.connector
import json
from jose import jwt
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_LIBRO_BY_ID_QUERY, GET_APUNTE_BY_ID_QUERY, GET_CALCULADORA_BY_ID_QUERY
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
            if 'pathParameters' in event and event['pathParameters'] is not None:
              query_params = event['pathParameters']
              
              material_id = query_params.get('materialID')
              table = query_params.get('type')
              
            cursor = connection.cursor(dictionary=True)
            
            params = {
              'Material_ID': material_id
            }
            
            if table == 'Libros':
              cursor.execute(GET_LIBRO_BY_ID_QUERY, params)
              
            elif table == 'Apuntes':
              cursor.execute(GET_APUNTE_BY_ID_QUERY, params)
              
            elif table == 'Calculadoras':
              cursor.execute(GET_CALCULADORA_BY_ID_QUERY, params)
              
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'GET',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Invalid material type'
                })
              }
            
            material = cursor.fetchone()
            
            if material:
              return {
                'statusCode': 200,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'GET',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'Material': material
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
                  'message': 'Material not found'
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