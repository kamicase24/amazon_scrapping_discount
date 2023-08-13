
from core.telegram import TelegramBot
import logging
import os
from datetime import datetime
from pprint import pformat


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

    tlg_bot = TelegramBot()

    print('¿Que acción desea ejecutar?')
    actions = [
        ('get_chat_group_ids', 'Ver los Grupos Registrados'),
        ('update_chat_group_ids', 'Actualizar ID de Grupos'), 
        ('update_chat_ids', 'Actualizar ID de Chats Privados'), 
        ('get_chat_invite_link', 'Generar Link de Invitación'),
        ('send_message', 'Enviar Mensaje'), 
        ('get_bot_data', 'Ver información del Bot'),
    ]

    for i, action in enumerate(actions):
        i += 1
        print(f'{i}) {action[1]}')
    action_index = int(input('Que acción desea ejecutar: '))-1
    active_action = actions[action_index][0]
    print(f'{actions[action_index][1]}')
    print('_'*50)
    vals = getattr(tlg_bot, active_action)()
    if vals is not None:
        print(pformat(vals))
    print('_'*50)