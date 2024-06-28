import json
import boto3
import hashlib
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
          userGroups = client.admin_list_groups_for_user(Username=user['Username'], UserPoolId=USER_POOL_ID)
          user_info = {
            'username': user['Username'],
            'rol': userGroups['Groups'][0]['GroupName'],
          }
          for attr in user['Attributes']:
            if attr['Name'] == 'email':
              user_info['email'] = attr['Value']
            elif attr['Name'] == 'name':
              user_info['name'] = attr['Value']
          
          if 'name' in user_info and 'email' in user_info:
            users.append(user_info)
            
        response_body = json.dumps({
          'users': users
        })
        
        etag = hashlib.md5(response_body.encode('utf-8')).hexdigest()
        
        if len(users) > 0:
          if 'headers' in event and 'If-None-Match' in event['headers'] and event['headers']['If-None-Match'] == etag:
            return {
              'statusCode': 304,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type,auth,ETag',
                'ETag': etag
              }
            }
          else:
            return {
            'statusCode': 200,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth,ETag',
              'ETag': etag
            },
            'body': json.dumps({
              'users': users
            })
          }
               
        else:
          return {
            'statusCode': 404,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
              'Access-Control-Allow-Headers': 'Content-Type,auth,ETag'
            },
            'body': json.dumps({
              'message': 'No users found'
            })
          }
          
      else:
        return {
          'statusCode': 403,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type,auth,ETag'
          },
          'body': json.dumps({
            'message': 'The user is not allowed to perform this action'
          })
        }
        
    else:
      return {
        'statusCode': 401,
        'headers': {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET',
          'Access-Control-Allow-Headers': 'Content-Type,auth,ETag'
        },
        'body': json.dumps({
          'message': 'Missing authentication token'
        })
      }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type,auth,ETag'
      },
      'body': json.dumps({
        'message': str(e)
      })
    }