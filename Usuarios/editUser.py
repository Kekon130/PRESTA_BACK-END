import json
import boto3
from jose import jwt
from utils_Usuarios import Rol_Usuario, USER_POOL_ID

def lambda_handler(event, context):
  try:
    token = event['headers']['auth']
    
    if token:
      decoded_token = jwt.get_unverified_claims(token)
      
      if 'cognito:groups' in decoded_token and (Rol_Usuario.Alumnos.value in decoded_token['cognito:groups'] or Rol_Usuario.Gestores.value in decoded_token['cognito:groups']):
        if 'body' in event and event['body'] is not None:
          body = json.loads(event['body'])
          
        client = boto3.client('cognito-idp')
        responses = {}
        
        if 'new_name' in body and body['new_name'] is not None:
          new_name = body['new_name']
          try:
            response = client.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=decoded_token['sub'],
                UserAttributes=[
                    {
                        'Name': 'name',
                        'Value': new_name
                    }
                ]
            )
            
            responses['name'] = 'Name updated successfully'
            
          except client.exceptions.UserNotFoundException as e:
            return {
              'statusCode': 404,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'User not found'
              })
            }
            
          except client.exceptions.InvalidParameterException as e:
            return {
              'statusCode': 400,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Invalid parameters'
              })
            }
            
            
          except Exception as e:
            print(e)
            responses['name'] = 'Name update failed'
            
        if 'new_password' in body and body['new_password'] is not None:
          new_password = body['new_password']
          try:
            response = client.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=decoded_token['sub'],
                Password=new_password,
                Permanent=True
            )
            
            responses['password'] = 'Password updated successfully'
            
          except client.exceptions.UserNotFoundException as e:
            return {
              'statusCode': 404,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'User not found'
              })
            }
            
          except client.exceptions.InvalidPasswordException as e:
            return {
              'statusCode': 400,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Invalid password'
              })
            }
            
          except client.exceptions.InvalidParameterException as e:
            return {
              'statusCode': 400,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Invalid parameters'
              })
            }
            
          except client.exceptions.NotAuthorizedException as e:
            return {
              'statusCode': 403,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'The user is not authorized to change the password'
              })
            }
            
          except Exception as e:
            return {
              'statusCode': 500,
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'PATCH',
                'Access-Control-Allow-Headers': 'Content-Type,auth'
              },
              'body': json.dumps({
                'message': 'Password update failed'
              })
            }
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PATCH',
            'Access-Control-Allow-Headers': 'Content-Type,auth'
          },
          'body': json.dumps({
            'responses': responses
          })
        }
        
      else:
        return {
          'statusCode': 403,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PATCH',
            'Access-Control-Allow-Headers': 'Content-Type,auth'
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
          'Access-Control-Allow-Methods': 'PATCH',
          'Access-Control-Allow-Headers': 'Content-Type,auth'
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
        'Access-Control-Allow-Methods': 'PATCH',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': str(e)
      })
    }