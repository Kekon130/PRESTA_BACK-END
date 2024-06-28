import boto3
import json
from jose import jwt
from utils_Usuarios import Rol_Usuario, USER_POOL_ID

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and (Rol_Usuario.Administradores.value in decoded_token['cognito:groups'] or Rol_Usuario.Gestores.value in decoded_token['cognito:groups'] or Rol_Usuario.Alumnos.value in decoded_token['cognito:groups']):
        client = boto3.client('cognito-idp')
        
        try:
          print(decoded_token['email'])
          
          response = client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=decoded_token['email']
          )
          
          print(response)
          
          userAtributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
          
          print(userAtributes)
          
          filtered_attributes = {
            'name': userAtributes['name'],
            'rol': decoded_token['cognito:groups'][0]
          }
          
          print(filtered_attributes)
          
          return {
            'statusCode': 200,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'user': filtered_attributes
            })
          }
          
        except client.exceptions.UserNotFoundException:
          return {
            'statusCode': 404,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': 'El usuario no existe'
            })
          }
          
        except client.exceptions.ResourceNotFoundException:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'Group not found'
            })
          }
          
        except client.exceptions.NotAuthorizedException:
          return {
            'statusCode': 403,
            'body': json.dumps({
              'message': 'The user is not authorized to perform this action'
            })
          }
          
        except Exception as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': str(e)
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
            'message': 'El usuario no está autorizado para realizar esta acción'
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
          'message': 'Falta el token de autenticación'
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