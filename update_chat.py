"""
Archivo para actualizar los ID de chat con los usuarios del bot de Telegram.

El archivo `update_chat.py` es responsable de actualizar los ID de chat con los usuarios que interactúan con el bot de Telegram y guardarlos en el archivo de configuración.

1. Configuración del registro de eventos (logging):
   - El programa configura el registro de eventos utilizando el módulo de registro `logging`. Los eventos de registro se guardan en un archivo de registro que se nombra según la fecha y hora de inicio del proceso de actualización.
   - El archivo de registro se crea en el directorio "logs" dentro de la ubicación del archivo `update_chat.py`. Si el directorio no existe, se crea automáticamente.
   - El nivel de registro está configurado en `INFO`, lo que significa que se registrarán mensajes de nivel `INFO` y superior.

2. Ejecución del proceso de actualización de los ID de chat:
   - El programa crea una instancia de la clase `TelegramBot` desde el módulo `core.telegram` para interactuar con el bot de Telegram.
   - Luego, se llama al método `update_chat_ids()` de la instancia de `TelegramBot` para obtener los ID de chat con los usuarios y guardarlos en el archivo de configuración.
   - Durante el proceso de actualización, se registran eventos relevantes utilizando el módulo de registro `logging`.

Ejecución del programa:
   - El programa se ejecuta cuando se llama directamente al archivo `update_chat.py`, es decir, cuando la condición `if __name__ == '__main__':` es verdadera.
   - Cuando se ejecuta, el programa realiza el proceso de actualización de los ID de chat con los usuarios del bot de Telegram.

"""

from core.telegram import TelegramBot
import logging
import os
from datetime import datetime


# Configuración del registro de eventos (logging)
NOW = datetime.now()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_LOG = os.path.join(BASE_PATH, 'logs')
os.makedirs(PATH_LOG, exist_ok=True)

LOG_FILE = f'{PATH_LOG}/update_chat_logs_{NOW:%Y-%m-%dT%H-%M-%S}.log'

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s : %(levelname)s : %(message)s',
    datefmt='%d-%b-%yT%H:%M:%S',
    level=logging.INFO)


if __name__ == '__main__':

    tele_bot = TelegramBot()
    tele_bot.update_chat_ids()
