import mysql.connector
import json
from jose import jwt
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, DELETE_LIBRO_QUERY, DELETE_APUNTE_QUERY, DELETE_CALCULADORA_QUERY
from utils_Usuarios import Rol_Usuario
from utils_Material import Tipo_Material

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
            if 'pathParameters' in event and event['pathParameters'] is not None:
              query_params = event['pathParameters']
              
              table = query_params.get('type')
              material_id = query_params.get('materialID')
              
            cursor = connection.cursor(dictionary=True)
            
            if table == Tipo_Material.Libros.value:
              params = {
                'Material_ID': material_id
              }
              
              cursor.execute(DELETE_LIBRO_QUERY, params)
              
            elif table == Tipo_Material.Apuntes.value:
              params = {
                'Material_ID': material_id
              }
              
              cursor.execute(DELETE_APUNTE_QUERY, params)
              
            elif table == Tipo_Material.Calculadoras.value:
              params = {
                'Material_ID': material_id
              }
              
              cursor.execute(DELETE_CALCULADORA_QUERY, params)
              
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'DELETE',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Material not found'
                })
              }
              
            connection.commit()
            
            if cursor.rowcount > 0:
              return {
                'statusCode': 204,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'DELETE',
                  'Access-Control-Allow-Headers': 'Content-Type,auth'
                },
                'body': json.dumps({
                  'message': 'Material deleted successfully'
                })
              }
              
            else:
              return {
                'statusCode': 404,
                'headers': {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': 'DELETE',
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
              'Access-Control-Allow-Methods': 'DELETE',
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
            'Access-Control-Allow-Methods': 'DELETE',
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
          'Access-Control-Allow-Methods': 'DELETE',
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
        'Access-Control-Allow-Methods': 'DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': str(e)
      })
    }