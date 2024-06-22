import mysql.connector
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_RESERVA_QUERY, FORMALIZAR_RESERVA_QUERY, FORMALIZAR_PRESTAMO_QUERY
from utils_Material import checkIfMaterialExists
from utils_Reserva import Estado_Reserva
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
              pathParams = event['pathParameters']
              
            cursor = connection.cursor(dictionary=True)
            
            params = {
              'Reserva_ID': pathParams['reservaID']
            }
            
            cursor.execute(GET_RESERVA_QUERY, params)
            
            reserva = cursor.fetchone()
            
            if reserva:
              if reserva['Estado'] == Estado_Reserva.Pendiente_Recogida.value:
                params = {
                  'Reserva_ID': pathParams['reservaID'],
                  'Estado': Estado_Reserva.Formalizada.value
                }

                cursor.execute(FORMALIZAR_RESERVA_QUERY, params)
                connection.commit()

                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                params = {
                  'Alumno_ID': reserva['Alumno_ID'],
                  'Alumno_Email': reserva['Alumno_Email'],
                  'Gestor_ID': decoded_token['sub'],
                  'Gestor_Email': decoded_token['email'],
                  'Material_ID': reserva['Material_ID'],
                  'Material_Nombre': reserva['Material_Nombre'],
                  'Fecha_Inicio': fecha_actual,
                  'Estado': Estado_Prestamo.En_Prestamo.value
                }

                cursor.execute(FORMALIZAR_PRESTAMO_QUERY, params)
                connection.commit()

                return {
                  'statusCode': 201,
                  'body': json.dumps({
                    'message': 'Prestamo formalizado correctamente'
                  })
                }
              
              else:
                return {
                  'statusCode': 400,
                  'body': json.dumps({
                    'message': 'La reserva no se puede formalizar'
                  })
                }
                
            else:
              return {
                'statusCode': 404,
                'body': json.dumps({
                  'message': 'Reserva not found'
                })
              }
              
          else:
            return {
              'statusCode': 500,
              'body': json.dumps({
                'message': 'Internal Server Error'
              })
            }
            
        except mysql.connector.Error as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': f'Internal Server Error: {e}'
            })
          }
          
        finally:
          if connection.is_connected():
            cursor.close()
            connection.close()
            
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