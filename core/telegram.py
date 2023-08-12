import requests
from dotenv import load_dotenv
import os
import json
from pprint import pformat
from core.base import Base, BASE_PATH

load_dotenv(BASE_PATH+'/.env/.env')


class TelegramBot(Base):
    """
    Clase que implementa funciones para interactuar con el bot de Telegram.

    Atributos:
    domain (str): El dominio de la API de Telegram.
    token (str): El token de acceso del bot de Telegram.
    chat_ids (dict): Un diccionario con los ID de chat de los usuarios con los que puede interactuar el bot.
    """


    def __init__(self):
        super().__init__()
        self.domain = os.getenv('TELEGRAM_DOMAIN')
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_ids = self.params.get('chat_ids')
        self.alert_chat_ids = self.params.get('alert_chat_ids')


    def get_config_data(self):
        """
        Obtiene los datos de configuración del archivo config.json.
        Devuelve:
        dict: Un diccionario que contiene los datos de configuración.
        """
        config_filepath = f'{BASE_PATH}/config.json'
        with open(config_filepath, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data


    def get_updates(self):
        """
        Obtiene las actualizaciones del bot de Telegram.
        Devuelve:
        tuple: Una tupla que contiene el código de estado de la solicitud HTTP y los datos de la respuesta JSON.
        """
        endpoint = '/getUpdates'

        url = f'{self.domain}{self.token}{endpoint}'
        res = requests.get(url)
        return res.status_code, res.json()


    def get_chat_ids_from_bot(self, chat_type:str='private'):
        """
        Obtiene los ID de chat de los usuarios con los que puede interactuar el bot.
        Devuelve:
        dict: Un diccionario que contiene los ID de chat y nombres de usuario de los usuarios.
        """
        status_code, data = self.get_updates()
        chat_ids = {}
        if status_code == 200 and data.get('ok', False):
            for r in data['result']:
                if r.get('message', False):
                    if r['message']['chat']['type'] == chat_type:
                        chat_ids.update(**{str(r['message']['chat']['id']): r['message']['chat']})
        return chat_ids


    def update_chat_ids(self):
        """
        Actualiza los ID de chat de los usuarios con los que puede interactuar el bot 
        y los guarda en el archivo de configuración.
        """
        chat_ids = self.get_chat_ids_from_bot('private')
        config_data = self.get_config_data()
        config_filepath = f'{BASE_PATH}/config.json'
        config_data['params'].update(chat_ids = {**chat_ids, **config_data['params']['chat_ids']})
        with open(config_filepath, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)


    def update_chat_group_ids(self):
        """
        Actualiza los ID de grupos con los que puede interactuar el bot 
        y los guarda en el archivo de configuración.
        """
        group_chat_ids = self.get_chat_ids_from_bot('supergroup')
        config_data = self.get_config_data()
        config_filepath = f'{BASE_PATH}/config.json'
        config_data['params'].update(chat_group_ids = {**group_chat_ids, **config_data['params']['chat_group_ids']})
        with open(config_filepath, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)


    def get_chat_group_ids(self):
        """
        Obtiene los ID de grupos con los que puede interactuar el bot.
        Devuelve:
        dict: Un diccionario que contiene los ID de chat de grupos.
        """
        config_filepath = f'{BASE_PATH}/config.json'
        with open(config_filepath, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data['params'].get('chat_group_ids', {})


    def create_chat_invite_link(self, chat_id:str):
        """
        Crea un enlace de invitación para un chat.
        Parámetros:
        chat_id (str): El ID de chat para el cual se creará el enlace.
        Devuelve:
        dict: Un diccionario con los datos del enlace de invitación.
        """
        endpoint = '/createChatInviteLink'
        url = f'{self.domain}{self.token}{endpoint}'        
        link_data = {}
        res = requests.post(url, json={'chat_id': chat_id})
        if res.ok:
            link_data = res.json()['result']
        return link_data


    def get_chat_invite_link(self):
        """
        Obtiene y muestra enlaces de invitación para grupos disponibles.
        """
        chat_group_ids = self.get_chat_group_ids()
        chat_group_list = []
        for i, val in enumerate(chat_group_ids.values()):
            i += 1
            print(f'{i}) {val["title"]} [{val["id"]}]')
            chat_group_list.append(val)
        group_index = int(input('Seleccione el grupo del cual desea generar el Link: '))-1
        group_id = chat_group_list[group_index]['id']
        link_data = self.create_chat_invite_link(group_id)
        print(pformat(link_data))
        print('_'*50)


    def send_message(self, chat_id:str, message:str, parse_mode=None):
        """
        Envía un mensaje al usuario de Telegram con el ID de chat proporcionado.
        Parámetros:
        chat_id (str): El ID de chat del usuario al que se enviará el mensaje.
        message (str): El mensaje que se enviará al usuario.
        parse_mode (str, opcional): El modo de análisis del mensaje (por defecto, None).
        Devuelve:
        tuple: Una tupla que contiene el código de estado de la solicitud HTTP y los datos de la respuesta JSON.
        """
        endpoint = '/sendMessage'
        body = {
            "chat_id": chat_id,
            "text": message
        }
        if parse_mode is not None:
            body.update(parse_mode=parse_mode)
        url = f'{self.domain}{self.token}{endpoint}'
        res = requests.post(url, data=body)
        return res.status_code, res.json()






