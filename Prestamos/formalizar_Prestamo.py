import mysql.connector
import json
import boto3
from jose import jwt
from utils_Usuarios import checkIfUserExists, Rol_Usuario, USER_POOL_ID
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, FORMALIZAR_PRESTAMO_QUERY
from utils_Material import checkIfMaterialExists
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
            if 'body' in event and event['body'] is not None:
              body = json.loads(event['body'])
              
            if (alumno_ID := checkIfUserExists(body['Alumno_Email'])):
              if (material_ID := checkIfMaterialExists(body['Material_Nombre'], body['Material_Type'])):
                cursor = connection.cursor()
                
                params = {
                  'Alumno_ID': alumno_ID,
                  'Alumno_Email': body['Alumno_Email'],
                  'Gestor_ID': decoded_token['sub'],
                  'Gestor_Email': decoded_token['email'],
                  'Material_ID': material_ID,
                  'Material_Nombre': body['Material_Nombre'],
                  'Fecha_Prestamo': datetime.now().strftime('%Y-%m-%d'),
                  'Estado': Estado_Prestamo.En_Prestamo.value
                }
                
                cursor.execute(FORMALIZAR_PRESTAMO_QUERY, params)
                
                connection.commit()
                
                return {
                  'statusCode': 201,
                  'body': json.dumps({
                    'message': 'Prestamo formalizado'
                  })
                }
                
              else:
                return {
                  'statusCode': 404,
                  'body': json.dumps({
                    'message': 'Material not found'
                  })
                }
                
            else:
              return {
                'statusCode': 404,
                'body': json.dumps({
                  'message': 'User not found'
                })
              }
            
          else:
            return {
              'statusCode': 500,
              'body': json.dumps({
                'message': 'Error connecting to database'
              })
            }
            
        except mysql.connector.Error as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': 'Internal Server Error'
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
      
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f"Internal Server Error: {e}"
      })
    }