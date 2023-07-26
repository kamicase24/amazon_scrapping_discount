import os
import json
import jinja2

BASE_PATH = os.path.dirname(os.path.abspath(__file__)).replace('/core', '')


class Base():

    def __init__(self):
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('template/'))
        config = self.get_config()
        params = config['params']
        self.params = params


    def get_config(self):
        """
        Lee y carga la configuración desde el archivo 'config.json'.
        Returns:
            dict: Un diccionario que contiene los datos de configuración.
        """
        with open(f'{BASE_PATH}/config.json', 'r') as config_file:
            data = json.loads(config_file.read())
        return data