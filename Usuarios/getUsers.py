import json
import boto3
from jose import jwt
from utils_Usuarios import Rol_Usuario, USER_POOL_ID

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and Rol_Usuario.Administradores.value in decoded_token['cognito:groups']:
        client = boto3.client('cognito-idp')
        response = client.list_users(UserPoolId=USER_POOL_ID)
        
        users = []
        for user in response['Users']:
          user_info = {}
          for attr in user['Attributes']:
            if attr['Name'] == 'email':
              user_info['email'] = attr['Value']
            elif attr['Name'] == 'name':
              user_info['name'] = attr['Value']
          
          if 'name' in user_info and 'email' in user_info:
            users.append(user_info)
        
        if len(users) > 0:
          return {
            'statusCode': 200,
            'body': json.dumps({
              'users': users
            })
          }
        else:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'No users found'
            })
          }
          
      else:
        return {
          'statusCode': 403,
          'body': json.dumps({
            'message': 'The user is not allowed to perform this action'
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