import mysql.connector
import json
import os
from jose import jwt

def lambda_handler(event, context):
    try:
        # Se obtiene el token de autorización de la cabecera
        token = event['headers']['auth']
        
        if not token:
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized')
            }
        else:
            # Se decodifica el token
            decoded_token = jwt.get_unverified_claims(token)
            
            if 'cognito:groups' not in decoded_token or ('Alumnos' not in decoded_token['cognito:groups'] and 'Gestores' not in decoded_token['cognito:groups']):
                return {
                    'statusCode': 401,
                    'body': json.dumps('Unauthorized')
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
                        'body': json.dumps(f"Error connecting to database: {str(err)}")
                    }
                    
                try:
                    cursor = connection.cursor(dictionary=True)
                    
                    cursor.execute("SELECT Nombre, Asignatura, Cantidad FROM Libros")
                    libros = cursor.fetchall()
                    
                    cursor.execute("SELECT Nombre, Asignatura, Cantidad FROM Apuntes")
                    apuntes = cursor.fetchall()
                    
                    cursor.execute("SELECT Nombre, Modelo, Cantidad FROM Calculadoras")
                    calculadoras = cursor.fetchall()
                    
                except mysql.connector.Error as err:
                    return {
                        'statusCode': 500,
                        'body': json.dumps(f"Error querying database: {str(err)}")
                    }
                    
                finally:
                    cursor.close()
                    connection.close()
                    
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'Libros': libros,
                        'Apuntes': apuntes,
                        'Calculadoras': calculadoras
                    })
                }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }