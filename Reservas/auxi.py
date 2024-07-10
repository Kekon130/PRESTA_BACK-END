import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, POST_RESERVA_QUERY
from utils_Material import checkIfMaterialExists
from utils_Reserva import getFechaExpiracion, Estado_Reserva
from datetime import datetime

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
            if 'body' in event and event['body'] is not None:
              body = json.loads(event['body'])
              
            if checkIfMaterialExists(body['Material_Nombre'], body['Material_Type']):
              cursor = connection.cursor(dictionary=True)

              fecha_actual = datetime.now().strftime('%Y-%m-%d')
              params = {
                'Alumno_ID': decoded_token['sub'],
                'Alumno_Email': decoded_token['email'],
                'Material_ID': body['Material_ID'],
                'Material_Nombre': body['Material_Nombre'],
                'Fecha_Inicio': fecha_actual,
                'Fecha_Expiracion': getFechaExpiracion(fecha_actual),
                'Estado': Estado_Reserva.Pendiente_Recogida.value
              }
              
              cursor.execute(POST_RESERVA_QUERY, params)
              
              connection.commit()
              
              return {
                'statusCode': 200,
                'body': json.dumps({
                  'message': 'Reserva formalizada correctamente'
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
                'statusCode': 500,
                'body': json.dumps({
                  'message': 'Error connecting to database'
                })
            }
            
        except mysql.connector.Error as err:
          return {
              'statusCode': 500,
              'body': json.dumps({
                'message': str(err)
              })
          }
      
      else:
        return {
            'statusCode': 401,
            'body': json.dumps({
              'message': 'Unauthorized'
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
          'message': str(e)
        })
    }