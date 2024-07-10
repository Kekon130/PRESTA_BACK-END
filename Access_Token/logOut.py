import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
  access_token = event['headers']['access_token']
  
  if access_token:
    client = boto3.client('cognito-idp')
    
    try:
      response = client.global_sign_out(
        AccessToken=access_token
      )
      
      return {
        'statusCode': 200,
        'headers': {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type,access_token'
        },
        'body': json.dumps({
          'message': 'Sesión cerrada con éxito'
        })
      }
      
    except ClientError as e:
      raise Exception(f'Error al cerrar la sesión: {str(e)}')
    
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