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