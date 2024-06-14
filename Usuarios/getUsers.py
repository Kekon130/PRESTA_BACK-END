import json
import boto3
import os
from jose import jwt

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if not token:
      return {
        'statusCode': 401,
        'body': json.dumps('Unauthorized')
      }
      
    else:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' not in decoded_token or 'Administradores' not in decoded_token['cognito:groups']:
        return {
          'statusCode': 401,
          'body': json.dumps({
            'message': 'Unauthorized'
          })
        }
        
      else:
        user_pool_id = os.getenv('USER_POOL_ID')
        
        client = boto3.client('cognito-idp')
        response = client.list_users(UserPoolId=user_pool_id)
        
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
            
          print(user)
        
        if len(users) == 0:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'No users found'
            })
          }
        else:
          return {
            'statusCode': 200,
            'body': json.dumps({
              'users': users
            })
          }
          
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f"Error: {str(e)}"
      })
    }