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
            UserPoolId=USER_POOL_ID,
            Username=username,
            GroupName=old_group
          )
          
          client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
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
          
        except client.exceptions.ResourceNotFoundException:
          return {
            'statusCode': 404,
            'body': json.dumps({
              'message': 'Group not found'
            })
          }
          
        except client.exceptions.NotAuthorizedException:
          return {
            'statusCode': 403,
            'body': json.dumps({
              'message': 'The user is not authorized to perform this action'
            })
          }
          
        except Exception as e:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': str(e)
            })
          }
          
      else:
        return {
          'statusCode': 403,
          'body': json.dumps({
            'message': 'The user is not authorized to perform this action'
          })
        }
        
    else:
      return {
        'statusCode': 403,
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