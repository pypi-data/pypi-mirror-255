import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Configuración del cliente DynamoDB
dynamodb = boto3.resource('dynamodb')

def create_log(service_name, endpoint, response, status_code, table_name='ServiceLogs'):
    """
    Crea un nuevo registro de log en DynamoDB con un token y timestamp generados automáticamente.

    Args:
        service_name (str): Nombre del microservicio que genera el log.
        endpoint (str): Endpoint específico que fue invocado.
        response (dict): Respuesta generada por el microservicio, almacenada en formato dict.
        status_code (int): Código de estado HTTP resultante de la llamada al endpoint.
        table_name (str, opcional): Nombre de la tabla de DynamoDB donde se almacenará el log. Por defecto es 'ServiceLogs'.

    Returns:
        str: El token único generado para el registro de log, o None en caso de error.
    """
    table = dynamodb.Table(table_name)
    token = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    try:
        table.put_item(
            Item={
                'requestToken': token,
                'timestamp': timestamp,
                'serviceName': service_name,
                'endpoint': endpoint,
                'response': response,
                'statusCode': status_code
            }
        )
        return token
    except ClientError as e:
        print(f"Error al insertar el log en {table_name}: {e}")
        return None

def update_log(token, timestamp, response, status_code, table_name='ServiceLogs'):
    """
    Actualiza un registro existente en la tabla especificada de DynamoDB.

    Parámetros:
    - token (str): El token único del log a actualizar.
    - timestamp (str): El timestamp del log a actualizar.
    - response (dict): El nuevo valor del campo 'response'.
    - status_code (int): El nuevo valor del campo 'statusCode'.
    - table_name (str): Nombre de la tabla de DynamoDB (opcional, por defecto 'ServiceLogs').

    Retorna:
    - dict: La respuesta de la operación de actualización de DynamoDB, o None si hubo un error.
    """
    table = dynamodb.Table(table_name)
    
    try:
        response = table.update_item(
            Key={
                'requestToken': token,
                'timestamp': timestamp
            },
            UpdateExpression='SET #resp = :resp, #status = :status',
            ExpressionAttributeNames={
                '#resp': 'response',
                '#status': 'statusCode'
            },
            ExpressionAttributeValues={
                ':resp': response,
                ':status': status_code
            },
            ReturnValues="UPDATED_NEW"
        )
        print("Log actualizado con éxito.")
        return response
    except ClientError as e:
        print(f"Error al actualizar el log: {e}")
        return None

def delete_log(token, timestamp, table_name='ServiceLogs'):
    """
    Elimina un registro de log de la tabla especificada en DynamoDB.

    Parámetros:
    - token (str): El token único del log a eliminar.
    - timestamp (str): El timestamp del log a eliminar.
    - table_name (str): Nombre de la tabla de DynamoDB (opcional, por defecto 'ServiceLogs').

    Retorna:
    - dict: La respuesta de la operación de eliminación de DynamoDB, o None si hubo un error.
    """
    table = dynamodb.Table(table_name)
    
    try:
        response = table.delete_item(
            Key={
                'requestToken': token,
                'timestamp': timestamp
            }
        )
        print("Log eliminado con éxito.")
        return response
    except ClientError as e:
        print(f"Error al eliminar el log: {e}")
        return None
