"""
Archivo principal para ejecutar el proceso de scraping en Amazon y enviar notificaciones por Telegram.

El archivo `run.py` es el punto de entrada del programa, donde se ejecuta el proceso de scraping en Amazon y se envían notificaciones a través de Telegram.

"""

from core.scraping import Amazonscraping
import logging
import os
from datetime import datetime
import pandas as pd
import urllib
import requests

# Configuración del registro de eventos (logging)
NOW = datetime.now()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_LOG = os.path.join(BASE_PATH, 'logs')
os.makedirs(PATH_LOG, exist_ok=True)

LOG_FILE = f'{PATH_LOG}/amazon_scraping_logs_{NOW:%Y-%m-%dT%H-%M-%S}.log'

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s : %(levelname)s : %(message)s',
    datefmt='%d-%b-%yT%H:%M:%S',
    level=logging.INFO)


if __name__ == '__main__':

    amazon_scraping = Amazonscraping()
    
    amazon_scraping.process()

    # df = pd.read_csv('results/tv_Todos_los_descuentos_products_2023-07-30.csv')
    # amazon_scraping.short_link_scraping(df)
    # import ipdb; ipdb.set_trace()

    # bitly_token = 'cb45ddafe0e86aeaaf92079d051ff3c6361872c5'
    # bitly_domain = 'https://api-ssl.bitly.com'
    # bitly_endpoint = '/v4/bitlinks'
    # bitly_url = f'{bitly_domain}{bitly_endpoint}'
    # import json
    # for i,row in df.iterrows():
    #     url = row.link

        
    #     url_parse = urllib.parse.quote(url)
    #     short_url = None
    #     split_link = url.split('/')

    #     alias = ''
    #     if split_link[3] == 'sspa':
    #         alias = url.split('url=%')[1].split('%')[0]
    #         print(alias)
    #     else:
    #         alias = split_link[3]
    #         print(alias)
    #     data = {
    #         "group_guid": "Bn81lrjhxqh",
    #         "domain": f"bit.ly",
    #         "title": alias,
    #         "long_url": url,
    #     }
    #     headers = {
    #         'Authorization': f'Bearer {bitly_token}',
    #         'Content-Type': 'application/json'
    #     }
    #     # res = requests.get('https://api-ssl.bitly.com/v4/groups', headers=headers)
    #     res = requests.post(bitly_url, data=json.dumps(data), headers=headers)
    #     print(res.json())

    #     import ipdb; ipdb.set_trace()