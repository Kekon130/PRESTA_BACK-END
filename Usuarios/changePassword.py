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
      
      if 'cognito:groups' not in decoded_token or ('Administradores' not in decoded_token['cognito:groups'] and 'Alumnos' not in decoded_token['cognito:groups']):
        return {
          'statusCode': 401,
          'body': json.dumps({
            'message': 'Unauthorized'
          })
        }
        
      else:
        user_pool_id = os.getenv('USER_POOL_ID')
        
        if 'pathParameters' in event and event['pathParameters'] is not None:
            path_params = event['pathParameters']
            
            username = path_params['username']
        
        if 'body' in event and event['body'] is not None:
            body = json.loads(event['body'])
            
            new_password = body['new_password']
        
        client = boto3.client('cognito-idp')
        
        try:
          response = client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=new_password,
            Permanent=True
          )
          
          print(response)
          
          return {
            'statusCode': 200,
            'body': json.dumps({
              'message': 'Password changed successfully'
            })
          }
          
        except client.exceptions.UserNotFoundException:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'User not found'
            })
          }
          
        except client.exceptions.InvalidPasswordExceptionm as e:
          return {
            'statusCode': 400,
            'body': json.dumps({
              'message': f'Invalid password: {str(e)}'
            })
          }
          
        except client.exceptions.InvalidParameterException as e:
          return {
            'statusCode': 400,
            'body': json.dumps({
              'message': f'Invalid parameters: {str(e)}'
            })
          }
          
        except client.exceptions.NotAuthorizedException as e:
          return {
            'statusCode': 403,
            'body': json.dumps({
              'message': f'Not authorized: {str(e)}'
            })
          }
        
        except Exception as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': f"Error: {str(e)}"
            })
          }
          
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f"Error: {str(e)}"
      })
    }