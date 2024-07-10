import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
  access_token = event['headers']['access_token']
  
  if access_token:
    client = boto3.client('cognito-idp')
    
    try:
      response = client.get_user(
        AccessToken=access_token
      )
      
      if response:
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,access_token'
          },
          'body': json.dumps({
            'message': 'Sesión activa'
          })
        }
        
      else:
        return {
          'statusCode': 404,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,access_token'
          },
          'body': json.dumps({
            'message': 'Sesión no encontrada'
          })
        }
        
    except ClientError as e:
      return {
        'statusCode': 500,
        'headers': {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type,access_token'
        },
        'body': json.dumps({
          'message': f'Error al verificar la sesión: {str(e)}'
        })
      }
      
  else:
    return {
      'statusCode': 400,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type,access_token'
      },
      'body': json.dumps({
        'message': 'No se ha proporcionado un token de acceso'
      })
    }
