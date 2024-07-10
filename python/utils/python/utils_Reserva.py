from datetime import datetime, timedelta
from enum import Enum
from utils_BD import RDS_HOST, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME, GET_RESERVAS_QUERY

class Estado_Reserva(Enum):
  Pendiente_Recogida = 'Pendiente de recoger'
  Formalizada = 'Formalizada'
  Cancelada = 'Cancelada'

def getFechaExpiracion(fecha_inicio):
  fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
  
  fecha_expiracion = fecha_inicio + timedelta(days=3)
  
  while fecha_expiracion.weekday() in [5, 6]:
    fecha_expiracion += timedelta(days=1)
    
  return fecha_expiracion.strftime('%Y-%m-%d')

def checkIfReservaCancelable(Reserva_ID):
  try:
    connection = mysql.connector.connect(
      host=RDS_HOST,
      user=RDS_USERNAME,
      password=RDS_PASSWORD,
      database=RDS_DB_NAME
    )
    
    if connection.is_connected():
      cursor = connection.cursor(dictionary=True)
      
      cursor.execute(GET_RESERVAS_QUERY, {'Reserva_ID': Reserva_ID})
      
      result = cursor.fetchone()
      
      if result['Estado'] == Estado_Reserva.Pendiente_Recogida.value:
        return True
      
      else:
        return False
      
    else:
      return False
    
  except mysql.connector.Error as err:
    print(f"Error connecting to database: {str(err)}")
    return False
  
  finally:
    if connection.is_connected():
      connection.close()
      cursor.close()