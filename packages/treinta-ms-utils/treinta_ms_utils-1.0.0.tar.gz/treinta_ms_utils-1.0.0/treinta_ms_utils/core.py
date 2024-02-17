import boto3
import uuid
from datetime import datetime
import pytz
from botocore.exceptions import ClientError

# Configuración del cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
colombia_tz = pytz.timezone('America/Bogota')

def current_time_colombia():
    """
    Retorna el timestamp actual en la zona horaria de Colombia.
    """
    return datetime.now(colombia_tz).isoformat()

def create_log(service_name, endpoint, response, status_code, table_name='ServiceLogs'):
    """
    Modificaciones:
    1. Usa la zona horaria de Colombia para el timestamp.
    2. Añade manejo de created_timestamp y updated_timestamp.
    """
    table = dynamodb.Table(table_name)
    token = str(uuid.uuid4())
    timestamp = current_time_colombia()
    
    try:
        table.put_item(
            Item={
                'requestToken': token,
                'created_timestamp': timestamp,
                'updated_timestamp': timestamp,  # Igual al created_timestamp inicialmente
                'serviceName': service_name,
                'endpoint': endpoint,
                'response': response,
                'statusCode': status_code
            }
        )
        print(f"Log creado con éxito. Token: {token}")
        return token
    except ClientError as e:
        print(f"Error al insertar el log en {table_name}: {e}")
        return None

def update_log(token, response, status_code, table_name='ServiceLogs'):
    """
    Actualiza un registro existente en la tabla especificada de DynamoDB.

    Nota: La función ahora solo requiere token, response, y status_code.
          El timestamp de actualización se genera automáticamente.
    """
    table = dynamodb.Table(table_name)
    timestamp = current_time_colombia()
    
    try:
        response = table.update_item(
            Key={'requestToken': token},
            UpdateExpression='SET #resp = :resp, #status = :status, updated_timestamp = :updated',
            ExpressionAttributeNames={'#resp': 'response', '#status': 'statusCode'},
            ExpressionAttributeValues={':resp': response, ':status': status_code, ':updated': timestamp},
            ReturnValues="UPDATED_NEW"
        )
        print("Log actualizado con éxito.")
        return response
    except ClientError as e:
        print(f"Error al actualizar el log: {e}")
        return None

def delete_log(token, table_name='ServiceLogs'):
    """
    Elimina un registro de log de la tabla especificada en DynamoDB.
    """
    table = dynamodb.Table(table_name)
    
    try:
        response = table.delete_item(Key={'requestToken': token})
        print("Log eliminado con éxito.")
        return response
    except ClientError as e:
        print(f"Error al eliminar el log: {e}")
        return None

def get_log(token, table_name='ServiceLogs'):
    """
    Recupera un registro de log específico de DynamoDB usando su token.
    """
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(Key={'requestToken': token})
        if 'Item' in response:
            item = response['Item']
            # No es necesario ajustar la zona horaria, ya que se almacena como está.
            return {
                'token': item.get('requestToken'),
                'serviceName': item.get('serviceName'),
                'endpoint': item.get('endpoint'),
                'response': item.get('response'),
                'statusCode': item.get('statusCode'),
                'created_timestamp': item.get('created_timestamp'),
                'updated_timestamp': item.get('updated_timestamp')
            }
        else:
            print("Log no encontrado.")
            return None
    except ClientError as e:
        print(f"Error al leer el log: {e}")
        return None
