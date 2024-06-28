import boto3
import json
from botocore.exceptions import ClientError
from utils_Usuarios import CLIENT_ID

def lambda_handler(event, context):
  if 'body' in event and event['body'] is not None:
    body = json.loads(event['body'])
    
    code = body['confirmation_code']
    email = body['email']
    
  client = boto3.client('cognito-idp')
  
  try:
    response = client.confirm_sign_up(
      ClientId=CLIENT_ID,
      Username=email,
      ConfirmationCode=code
    )
    
    return {
      'statusCode': 200,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      'body': json.dumps({
        'message': 'Usuario confirmado exitosamente!'
      })
    }
    
  except ClientError as e:
    return {
      'statusCode': 400,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      'body': json.dumps({
        'message': f'Error al confirmar el usuario: {str(e)}'
      })
    }