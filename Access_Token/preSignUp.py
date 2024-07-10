import re

def lambda_handler(event, context):
    email = event['request']['userAttributes']['email']
    
    valid_pattern = r'.*@(alumnos\.upm\.es|upm\.es)$'
    
    if re.match(valid_pattern, email):
        return event
    else:
        raise Exception("El correo electrónico no es válido. Debe terminar en @alumnos.upm.es o @upm.es")