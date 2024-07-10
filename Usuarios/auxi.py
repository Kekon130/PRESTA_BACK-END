import json
import os
import boto3
from jose import jwt

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if not token:
      return {
        'statusCode': 401,
        'body': json.dumps({
          'message': 'Unauthorized'
        })
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
        
        if 'pathParameters' in event and event['pathParameters'] is not None:
            path_parameters = event['pathParameters']
            
            username = path_parameters['username']
        
        if 'body' in event and event['body'] is not None:
            body = json.loads(event['body'])
            
            old_group = body['old_group']
            new_group = body['new_group']
            
        client = boto3.client('cognito-idp')
        
        try:
          client.admin_remove_user_from_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=old_group
          )
          
          client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=new_group
          )
          
          return {
            'statusCode': 200,
            'body': json.dumps({
              'message': 'User group changed successfully'
            })
          }
          
        except client.exceptions.UserNotFoundException:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'User not found'
            })
          }
          
        except client.exceptions.InvalidParametersException as e:
          return {
            'statusCode': 400,
            'body': json.dumps({
              'message': str(e)
            })
          }
          
        except client.exceptions.NotAuthorizedException as e:
          return {
            'statusCode': 403,
            'body': json.dumps({
              'message': str(e)
            })
          }
          
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': str(e)
      })
    }