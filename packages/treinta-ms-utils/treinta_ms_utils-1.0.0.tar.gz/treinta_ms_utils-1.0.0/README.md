# treinta_ms_utils

`treinta_ms_utils` es una librería de Python desarrollada para simplificar y optimizar la interacción con diversos microservicios, facilitando la implementación de operaciones comunes como la creación, actualización, lectura y eliminación de registros de logs. Está dirigida a ingenieros de software, desarrolladores de backend y profesionales de TI que trabajan en la construcción y mantenimiento de arquitecturas basadas en microservicios.

## Índice

- [Introducción](#introducción)
- [Ventajas Clave](#ventajas-clave)
- [Instalación](#instalación)
- [Uso de la Librería](#uso-de-la-librería)
  - [1. `create_log`](#1-create_log)
  - [2. `update_log`](#2-update_log)
  - [3. `delete_log`](#3-delete_log)
  - [4. `read_log`](#4-read_log)  <!-- Nueva función añadida -->
- [Manejo de Errores](#manejo-de-errores)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Introducción

La librería `treinta_ms_utils` proporciona un conjunto de herramientas y utilidades diseñadas para mejorar la eficiencia del desarrollo y la gestión de microservicios, especialmente en entornos que utilizan Amazon DynamoDB para el registro y seguimiento de logs. 

## Ventajas Clave

- **Simplificación de Tareas Comunes**: Automatiza y simplifica tareas repetitivas como la inserción, actualización, lectura y eliminación de logs en DynamoDB.
- **Generación Automática de Tokens**: Facilita la generación de tokens únicos para cada registro, asegurando la trazabilidad y unicidad de los logs.
- **Manejo Preciso de la Zona Horaria**: Garantiza que todos los registros de logs se manejen en la zona horaria de Colombia (UTC-5), tanto para `created_timestamp` como para `updated_timestamp`.
- **Integración con DynamoDB**: Diseñada para trabajar de manera óptima con Amazon DynamoDB, aprovechando sus capacidades de almacenamiento NoSQL para gestionar logs de manera eficiente.
- **Manejo de Errores**: Incorpora prácticas de manejo de errores para asegurar la robustez y fiabilidad de las operaciones de microservicios.

## Instalación

Para instalar `treinta_ms_utils`, utiliza el siguiente comando pip:

```bash
pip install treinta_ms_utils
```

Este comando instala la última versión de la librería en tu entorno Python, permitiéndote comenzar a utilizarla de inmediato en tus proyectos.

## Uso de la Librería

### 1. `create_log`

Crea y almacena un nuevo registro de log en la tabla especificada de DynamoDB, incluyendo `created_timestamp` y `updated_timestamp` basados en la hora de Colombia.

### 2. `update_log`

Actualiza un registro existente de log en DynamoDB, identificado por su token único, incluyendo la actualización del `updated_timestamp` a la hora actual de Colombia.

### 3. `delete_log`

Elimina un registro de log de la tabla especificada en DynamoDB, utilizando su token único y timestamp como identificadores.

### 4. `read_log`

Recupera los detalles de un registro específico de log basado en su token, incluyendo `created_timestamp` y `updated_timestamp`, mostrando la información en la zona horaria de Colombia.

**Ejemplo:**

```python
from treinta_ms_utils import read_log

log_details = read_log(token="unique-token", table_name="ServiceLogs")
print(log_details)
```

## Manejo de Errores

`treinta_ms_utils` implementa un manejo de errores robusto para asegurar que las operaciones fallidas sean gestionadas de manera adecuada, proporcionando retroalimentación útil para la resolución de problemas.

## Licencia

`treinta_ms_utils` se distribuye bajo la Licencia MIT. Esto permite su uso, modificación y distribución libre en proyectos de cualquier tipo.

## Contacto

Para soporte, colaboraciones o preguntas, no dudes en contactarnos a través de nuestro [repositorio de GitHub](#).