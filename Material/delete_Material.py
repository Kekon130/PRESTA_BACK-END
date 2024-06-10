import mysql.connector
import os
import json
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
      
      if 'cognito:groups' not in decoded_token or 'Gestores' not in decoded_token['cognito:groups']:
        return {
          'statusCode': 401,
          'body': json.dumps({
            'message': 'Unauthorized'
          })
        }
        
      else:
        rds_host = os.getenv('RDS_HOST')
        rds_username = os.getenv('RDS_USERNAME')
        rds_password = os.getenv('RDS_PASSWORD')
        rds_db_name = os.getenv('RDS_DB_NAME')
        
        try:
          connection = mysql.connector.connect(
            host=rds_host,
            user=rds_username,
            password=rds_password,
            database=rds_db_name
          )
          
        except mysql.connector.Error as err:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': f"Error connecting to database: {str(err)}"
            })
          }
          
        if event['pathParameters'] is not None:
          query_params = event['pathParameters']
          
          table = query_params.get('type')
          material_id = query_params.get('materialID')
          
        try:
          cursor = connection.cursor(dictionary=True)
          
          if table == 'Libros':
            query = f'DELETE FROM {table} WHERE ID = {material_id}'
            
          elif table == 'Apuntes':
            query = f'DELETE FROM {table} WHERE ID = {material_id}'
            
          elif table == 'Calculadoras':
            query = f'DELETE FROM {table} WHERE ID = {material_id}'
            
          else:
            return {
              'statusCode': 400,
              'body': json.dumps({
                'message': 'Invalid table'
              })
            }
            
          cursor.execute(query)
          connection.commit()
          
          return {
            'statusCode': 200,
            'body': json.dumps({
              'message': 'Material deleted successfully'
            })
          }
          
        except mysql.connector.Error as err:
          return {
            'statusCode': 500,
            'body': json.dumps({
              'message': f"Error querying database: {str(err)}"
            })
          }
        finally:
          cursor.close()
          connection.close()
          
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'message': f"Error: {str(e)}"
      })
    }