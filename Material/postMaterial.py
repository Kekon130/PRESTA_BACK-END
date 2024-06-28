import mysql.connector
import json
from jose import jwt
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, POST_LIBRO_QUERY, POST_APUNTE_QUERY, POST_CALCULADORA_QUERY
from utils_Usuarios import Rol_Usuario

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and Rol_Usuario.Gestores.value in decoded_token['cognito:groups']:
        try:
          connection = mysql.connector.connect(
            host=RDS_HOST,
            user=RDS_USERNAME,
            password=RDS_PASSWORD,
            database=RDS_DB_NAME
          )
          
          if connection.is_connected():
            if 'body' in event and event['body'] is not None:
              body = json.loads(event['body'])
              
            if 'pathParameters' in event and event['pathParameters'] is not None:
              query_params = event['pathParameters']
              
              table = query_params.get('type')
              
            cursor = connection.cursor(dictionary=True)
            
            if table == 'Libros':
              params = {
                'Nombre': body['Nombre'],
                'Cantidad': body['Cantidad'],
                'Unidades_Disponibles': body['Cantidad'],
                'ISBN': body['ISBN'],
                'Año_de_Publicacion': body['Año_de_Publicacion'],
                'Asignatura': body['Asignatura']
              }
              
              cursor.execute(POST_LIBRO_QUERY, params)
              
            elif table == 'Apuntes':
              params = {
                'Nombre': body['Nombre'],
                'Cantidad': body['Cantidad'],
                'Unidades_Disponibles': body['Cantidad'],
                'Autor': body['Autor'],
                'Asignatura': body['Asignatura']
              }
              
              cursor.execute(POST_APUNTE_QUERY, params)
              
            elif table == 'Calculadoras':
              params = {
                'Nombre': body['Nombre'],
                'Cantidad': body['Cantidad'],
                'Unidades_Disponibles': body['Cantidad'],
                'Modelo': body['Modelo']
              }
              
              cursor.execute(POST_CALCULADORA_QUERY, params)
              
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'POST',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Table not found'
                })
              }
              
            connection.commit()
            
            return {
              'statusCode': 201,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Material added successfully'
              })
            }
            
          else:
            return {
                'statusCode': 500,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'POST',
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
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': str(err)
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
              'Access-Control-Allow-Methods': 'POST',
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
            'Access-Control-Allow-Methods': 'POST',
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
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type,auth'
        },
        'body': json.dumps({
          'message': str(e)
        })
    }
              
            
            