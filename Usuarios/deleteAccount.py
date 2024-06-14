import json
import os
import boto3
from jose import jwt

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if not token:
      return {
        'statusCode': 403,
        'body': json.dumps({
          'message': 'Unauthorized'
        })
      }
      
    else:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' not in decoded_token or ('Alumnos' not in decoded_token['cognito:groups'] and 'Gestores' not in decoded_token['cognito:groups']):
        return {
          'statusCode': 403,
          'body': json.dumps({
            'message': 'Unauthorized'
          })
        }
        
      else:
        user_pool_id = os.getenv('USER_POOL_ID')
        
        if 'pathParameters' in event and event['pathParameters'] is not None:
            path_parameters = event['pathParameters']
            
            username = path_parameters['username']
          
        client = boto3.client('cognito-idp')
        
        try:
          response = client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=username
          )
          
          print(response)
          
          return {
            'statusCode': 200,
            'body': json.dumps({
              'message': 'Account deleted successfully'
            })
          }
          
        except client.exceptions.UserNotFoundException:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'User not found'
            })
          }
          
        except client.exceptions.NotAuthorizedException as e:
          return {
            'statusCode': 403,
            'body': json.dumps({
              'message': str(e)
            })
          }
          
        except client.exceptions.InvalidParameterException as e:
          return {
            'statusCode': 400,
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