import boto3
import json
from botocore.exceptions import ClientError
from utils_Usuarios import CLIENT_ID

def lambda_handler(event, context):
  if 'body' in event and event['body'] is not None:
    body = json.loads(event['body'])
    
    email = body['email']
    name = body['name']
    password = body['password']
    
  client = boto3.client('cognito-idp')
  
  try:
    response = client.sign_up(
      ClientId=CLIENT_ID,
      Username=email,
      Password=password,
      UserAttributes=[
        {
          'Name': 'email',
          'Value': email
        },
        {
          'Name': 'name',
          'Value': name
        }
      ]
    )
    
    return {
      'statusCode': 200,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      body: json.dumps({
        'message': 'Usuario registrado exitosamente! Por favor, revisa tu correo para confirmar tu cuenta.'
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
        'message': f'Error al registrar el usuario: {str(e)}'
      })
    }
    
  except Exception as e:
    return {
      'statusCode': 500,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      'body': json.dumps({
        'message': f'Error al registrar el usuario: {str(e)}'
      })
    }