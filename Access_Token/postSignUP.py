import boto3
from utils_Usuarios import Rol_Usuario, USER_POOL_ID

def lambda_handler(event, context):
  client = boto3.client('cognito-idp')
  
  try:
    client.admin_add_user_to_group(
      UserPoolId=USER_POOL_ID,
      Username=event['username'],
      GroupName=Rol_Usuario.Alumnos.value
    )
    
    return event
    
  except Exception as e:
    raise Exception(f'Error al agregar el usuario al grupo: {str(e)}')
      