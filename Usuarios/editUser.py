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
      
      if 'cognito:groups' not in decoded_token or ('Alumnos' not in decoded_token['cognito:groups'] and 'Gestores' not in decoded_token['cognito:groups']):
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
            
            new_password = body['new_password']
            new_name = body['new_name']
        
        client = boto3.client('cognito-idp')
        responses = {}
        
        if new_name:
          try:
            response = client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=username,
                UserAttributes=[
                    {
                        'Name': 'name',
                        'Value': new_name
                    }
                ]
            )
            
            print('Name update:\n')
            print(response)
            
            responses['name'] = 'Name updated successfully'
              
          except client.exceptions.UserNotFoundException:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'User not found'
                })
            }
            
          except client.exceptions.InvalidParameterException as e:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f'Invalid parameter: {str(e)}'
                })
            }
            
          except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': f"Error: {str(e)}"
                })
            }
            
        if new_password:
          try:
            response = client.admin_set_user_password(
              UserPoolId=user_pool_id,
              Username=username,
              Password=new_password,
              Permanent=True
            )
            
            print('Password update:\n')
            print(response)
            
            responses['password'] = 'Password changed successfully'
            
          except client.exceptions.UserNotFoundException:
            return {
              'statusCode': 404,
              'body': json.dumps({
                'message': 'User not found'
              })
            }
            
          except client.exceptions.InvalidPasswordException as e:
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
            
        return {
          'statusCode': 200,
          'body': json.dumps({
            'message': responses
          })
        }
        
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f"Error: {str(e)}"
      })
    } 