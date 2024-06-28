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
          
          new_password = body['new_password']
        
        client = boto3.client('cognito-idp')
        
        try:
          response = client.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=decoded_token['sub'],
            Password=new_password,
            Permanent=True
          )
          
          return {
            'statusCode': 200,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'POST',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': 'Password changed successfully'
            })
          }
          
        except client.exceptions.UserNotFoundException:
          return {
            'statusCode': 404,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'POST',
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
              'Access-Control-Allow-Methods': 'POST',
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
              'Access-Control-Allow-Methods': 'POST',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': 'The user is not authorized to perform this action'
            })
          }
          
        except Exception as e:
          return {
            'statusCode': 500,
            'headers': {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'POST',
              'Access-Control-Allow-Headers': 'Content-Type,auth'
            },
            'body': json.dumps({
              'message': 'An error occurred'
            })
          }
          
      else:
        return {
          'statusCode': 403,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,auth'
          },
          'body': json.dumps({
            'message': 'The user is not authorized to perform this action'
          })
        }
        
    else:
      return {
        'statusCode': 401,
        'headers': {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type,auth'
        },
        'body': json.dumps({
          'message': 'Missing authorization token'
        })
      }
      
  except Exception as e:
    return {
      'statusCode': 500,
      'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type,auth'
      },
      'body': json.dumps({
        'message': 'An error occurred'
      })
    }