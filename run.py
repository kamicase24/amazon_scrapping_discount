from core.scrapping import AmazonScrapping
import logging
import os
from datetime import datetime


NOW = datetime.now()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_LOG = os.path.join(BASE_PATH, f'logs')
os.makedirs(PATH_LOG, exist_ok=True)

LOG_FILE = f'{PATH_LOG}/amazon_scrapping_logs_{NOW:%Y-%m-%dT%H-%M-%S}.log'


logging.basicConfig(
    # filename=LOG_FILE,
    format='%(asctime)s : %(levelname)s : %(message)s',
    datefmt='%d-%b-%yT%H:%M:%S',
    level=logging.INFO)


if __name__ == '__main__':
    
    amazon_scrapping = AmazonScrapping()    
    amazon_scrapping.process()