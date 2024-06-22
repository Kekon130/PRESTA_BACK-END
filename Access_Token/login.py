import json
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
  client_id = os.getenv('CLIENT_ID')
  
  if 'body' in event and event['body'] is not None:
    body = json.loads(event['body'])
    
    email = body['email']
    password = body['password']
    
  client = boto3.client('cognito-idp')
  
  try:
    response = client.initiate_auth(
      AuthFlow='USER_PASSWORD_AUTH',
      AuthParameters={
        'USERNAME': email,
        'PASSWORD': password
      },
      ClientId=client_id
    )
    
    return {
      'statusCode': 200,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      'body': json.dumps({
        'message': 'Login successful',
        'id_token': response['AuthenticationResult']['IdToken'],
        'access_token': response['AuthenticationResult']['AccessToken'],
        'refresh_token': response['AuthenticationResult']['RefreshToken']
      })
    }
    
  except ClientError as e:
    return {
      'statusCode': 400,
      'body': json.dumps({
        'message': 'Login failed',
        'error': str(e)
      })
    }