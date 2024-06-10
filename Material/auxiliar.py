import mysql.connector
import os
import json 

def lambda_handler(event, context):
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
      'body': json.dumps(f"Error connecting to database: {str(err)}")
    }
  
  if 'pathParameters' in event and event['pathParameters'] is not None:
    table = event['pathParameters']['type']
    material_id = event['pathParameters']['materialID']
    
  try:
    cursor = connection.cursor(dictionary=True)
    
    if table == 'Libros':
      query = f"DELETE FROM Libros WHERE ID = {material_id}"
      
    elif table == 'Apuntes':
      query = f"DELETE FROM Apuntes WHERE ID = {material_id}"
      
    elif table == 'Calculadoras':
      query = f"DELETE FROM Calculadoras WHERE ID = {material_id}"
      
    else:
      return {
        'statusCode': 400,
        'body': json.dumps("Invalid table name")
      }
      
    cursor.execute(query)
    connection.commit()
    
    return {
      'statusCode': 200,
      'body': json.dumps("Material deleted successfully")
    }
    
  except mysql.connector.Error as err:
    return {
      'statusCode': 500,
      'body': json.dumps(f"Error deleting material: {str(err)}")
    }
  finally:
    cursor.close()
    connection.close()