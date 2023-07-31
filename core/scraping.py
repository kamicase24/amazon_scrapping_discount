import logging
import os
import time
from datetime import datetime, timedelta

import pandas as pd
import pytz
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from core.base import BASE_PATH, Base
from core.telegram import TelegramBot

load_dotenv(BASE_PATH+'/.env/.env')

TZ=os.getenv('TZ', 'America/Lima')

def timer(func):
    """
    Decorador que mide el tiempo de ejecución de una función
    Parámetros:
    func (function): La función que se va a medir.
    Devuelve:
    function: Una función envoltorio que ejecuta `func` y registra el tiempo de inicio y finalización.
    """
    def wrapper(*args, **kwargs):
        startt = time.time()
        logging.info(f'INICIA {func.__name__}')
        result = func(*args, **kwargs)
        endt = time.time()
        logging.info(f'FIN {func.__name__}')
        logging.info(f'{"="*15} Tiempo de ejecución {func.__name__}: {timedelta(seconds=endt-startt)} {"="*25}')
        return result

    return wrapper


class Amazonscraping(Base):
    """
    Clase que implementa funciones para realizar scraping de productos en Amazon.

    Atributos:
    url (str): La URL base para realizar las búsquedas en Amazon.
    use_amazon_filters (bool): Indica si se deben aplicar los filtros de búsqueda de Amazon (por defecto, False).
    search_values (list): Una lista de valores de búsqueda para realizar scraping de productos.
    amazon_filters (dict): Un diccionario que contiene los filtros de búsqueda de Amazon.
    download_df (bool): Indica si se deben descargar los resultados en formato DataFrame (por defecto, False).
    discount_rate (float): La tasa de descuento mínima requerida para considerar un producto como válido.
    telegram_bot (TelegramBot): Una instancia de la clase TelegramBot para enviar mensajes de Telegram.
    """


    def __init__(self):
        super().__init__()
        self.url = "https://www.amazon.com.mx//s?k=" 
        self.use_amazon_filters = self.params.get('use_amazon_filters', False)
        self.search_values = self.params.get('search_values', [])
        self.amazon_filters = self.params.get('amazon_filters', {})
        self.download_df = self.params.get('download_df', False)
        self.discount_rate = self.params.get('discount_rate')
        self.tag_associates = self.params.get('tag_associates', False)
        self.telegram_bot = TelegramBot()


    def get_search_url(self, value:str):
        """
        Construye y devuelve la URL de búsqueda en Amazon con el valor proporcionado.
        Parámetros:
        value (str): El valor de búsqueda para construir la URL.
        Devuelve:
        str: La URL de búsqueda completa.
        """
        return f'{self.url}{value}'


    def get_product_code(self, product_element):
        """
        Obtiene el código del producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene el código del producto.
        Devuelve:
        str: El código del producto o None si no se puede obtener.
        """
        product_code = None
        try:
            product_code = product_element.get_attribute('data-asin')
        except Exception as e:
            logging.error('Error al obtener el codigo del producto')
            logging.error(e.msg)            

        return product_code


    def get_product_name(self, product_element):
        """
        Obtiene el nombre del producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene el nombre del producto.
        Devuelve:
        str: El nombre del producto o None si no se puede obtener.
        """
        product_name = None
        try:
            product_name_element = product_element.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
            product_name = product_name_element.text
            logging.info(f'Producto: {product_name}')
        except Exception as e:
            logging.error('Error al obtener el nombre del producto')
            logging.error(e.msg)

        return product_name


    def get_product_type(self, product_element):
        """
        Obtiene el tipo de producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene la información sobre el tipo de producto.
        Devuelve:
        str: El tipo de producto ('standard', 'sponsored', 'featured' u 'other').
        """
        product_type = None
        try:
            sponsored_element = product_element.find_element(By.XPATH, './/div[@class="a-row a-spacing-micro"]')
            if len(sponsored_element.find_elements(By.XPATH, './/span[@class="a-color-secondary"]')) > 0:
                product_type = 'sponsored'
            if len(sponsored_element.find_elements(By.XPATH, './/span[@class="a-size-micro a-color-secondary"]')) > 0:
                product_type = 'featured'
        except Exception as e:
            product_type = 'standard'
        return product_type


    def get_product_price(self, product_element):
        """
        Obtiene el precio del producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene la información sobre el precio del producto.
        Devuelve:
        float: El precio del producto o None si no se puede obtener.
        """
        product_price = None
        try:
            product_price_element = product_element.find_element(By.XPATH, './/span[@class="a-price"]')
            elements = product_price_element.find_elements(By.XPATH, 'span')
            product_price_raw = elements[0].get_attribute('innerHTML')
            product_price = float(product_price_raw.replace('$', '').replace(',', ''))
        except NoSuchElementException as e:
            logging.warn('Product sin precio')
            product_content_elements = product_element.find_element(By.XPATH, './/div[@class="a-section a-spacing-small puis-padding-left-small puis-padding-right-small"]')
            if len(product_content_elements.find_elements(By.CSS_SELECTOR, 'div')):
                product_price = 0.00
            else:
                logging.error(e)
        except Exception as e:
            logging.error('Error al obtener el precio del producto')
            logging.error(e.msg)

        return product_price


    def get_product_price_list(self, product_element):
        """
        Obtiene el precio de lista del producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene la información sobre el precio de lista del producto.
        Devuelve:
        float: El precio de lista del producto o None si no se puede obtener.
        """
        product_price_list = None
        try:
            product_price_list_element = product_element.find_element(By.XPATH, './/span[@class="a-price a-text-price"]')
            elements = product_price_list_element.find_elements(By.XPATH, 'span')
            product_price_list_raw = elements[0].get_attribute('innerHTML')
            product_price_list = float(product_price_list_raw.replace('$', '').replace(',', ''))
        except NoSuchElementException as e:
            logging.warn('Producto sin Descuento')
            product_price_list = 0.00
        except Exception as e:
            logging.error('Error al obtener el precio de lista del producto')
            logging.error(e)
        return product_price_list


    def get_discount(self, price_list:float, price:float):
        """
        Calcula el porcentaje de descuento para un producto dado.
        Parámetros:
        price_list (float): El precio de lista original del producto.
        price (float): El precio actual del producto.
        Devuelve:
        int: El porcentaje de descuento, o 0 si no hay descuento.
        """
        product_discount_rate = 0
        if price_list > 0.00:
            discount_amount = price_list - price
            product_discount_rate = round((discount_amount / price_list) * 100)
        return product_discount_rate


    def get_product_link(self, product_element):
        """
        Obtiene el enlace del producto desde el elemento Web proporcionado.
        Parámetros:
        product_element: El elemento Web que contiene el enlace del producto.
        Devuelve:
        str: El enlace del producto o None si no se puede obtener.
        """
        product_link = None
        try:
            product_link_element = product_element.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
            product_link = product_link_element.get_attribute('href')
            if self.tag_associates:
                product_link = f'{product_link}&tag={self.tag_associates}'
        except Exception as e:
            logging.error('Error al obtener link del producto')
            logging.error(e)
        return product_link


    def get_product_data(self, driver):
        """
        Realiza el scraping de datos de los productos en la página web.
        Parámetros:
        driver: Una instancia del navegador web para interactuar con la página.
        Devuelve:
        dict: Un diccionario con los datos de los productos obtenidos del scraping.
        """
        page = 1
        page_limit = self.params.get('pagination_level', 1)
        product_list = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
        product_dict = {
            'code': [],
            'name': [],
            'price': [],
            'price_list': [],
            'discount': [],
            'link': [],
            'type': [],
            'page': [],
            'sended': []
        }
        for active_page in range(page, page_limit+1):
            logging.info('='*50)
            logging.info(f'Pagina #: {active_page}')
            logging.info('='*50)

            # Paginación
            if active_page > 1:
                active_page_element = driver.find_element(By.XPATH, '//span[@class="s-pagination-item s-pagination-selected"]')
                try:
                    next_page_element = active_page_element.find_element(By.XPATH, './following-sibling::a')
                except Exception as e:
                    logging.error('Error al realizar la paginación')
                if next_page_element.text == str(active_page):
                    next_page_element.click()
                    time.sleep(8)
                    product_list = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')

            # Iteración de la lista de productos
            for i, product_element in enumerate(product_list):

                # Codigo del Producto
                product_code = self.get_product_code(product_element)

                # Nombre del Producto
                product_name = self.get_product_name(product_element)

                # Tipo de Producto
                product_type = self.get_product_type(product_element)

                # Precio del Producto
                product_price = self.get_product_price(product_element)
                if product_price == 0.00:
                    product_type = 'other'

                # Precio de Lista del producto
                product_price_list = self.get_product_price_list(product_element)

                # Descuento
                discount = self.get_discount(product_price_list, product_price)

                # Link del Producto
                product_link = self.get_product_link(product_element)

                product_dict['code'].append(product_code)
                product_dict['name'].append(product_name)
                product_dict['price_list'].append(product_price_list)
                product_dict['price'].append(product_price)
                product_dict['discount'].append(discount)
                product_dict['type'].append(product_type)
                product_dict['link'].append(product_link)
                product_dict['page'].append(active_page)
                product_dict['sended'].append(False)
        return product_dict


    def get_product_df(self, product_dict:dict, filename:str):
        """
        Genera un DataFrame a partir del diccionario de datos de los productos.
        Parámetros:
        product_dict (dict): Un diccionario con los datos de los productos.
        filename (str): El nombre del archivo para descargar los resultados.
        Devuelve:
        pd.DataFrame: El DataFrame generado a partir de los datos de los productos.
        """
        df = None
        try:
            df = pd.DataFrame(product_dict)
            if self.download_df:
                df.to_csv(f'results/{filename}', index=False)
        except Exception as e:
            logging.error(f'Error al generar DataFrame {e}')
        return df


    def scraping(self, url, search_val):
        """
        Realiza el scraping de productos en Amazon para un valor de búsqueda dado.
        Parámetros:
        url (str): La URL de búsqueda en Amazon.
        search_val (str): El valor de búsqueda para el scraping.
        Devuelve:
        pd.DataFrame: Un DataFrame con los datos de los productos obtenidos del scraping.
        """
        driver = webdriver.Chrome()
        driver.get(url)
        today = datetime.now(tz=pytz.timezone(TZ)).strftime('%Y-%m-%d')
        if self.use_amazon_filters:
            for key, filter in self.amazon_filters.items():
                logging.info(f'Filtro activo: {filter} ')
                logging.info('='*50)
                try:
                    filter_element = driver.find_element(By.ID, key).find_element(By.TAG_NAME, 'a')
                    filter_element.click()
                    time.sleep(8)
                except NoSuchElementException as e:
                    logging.error(e.msg)
                    logging.error('Filtro no encontrado')
                    continue

                product_dict = self.get_product_data(driver)
                df = self.get_product_df(product_dict, f'{search_val}_{filter.replace(" ", "_")}_products_{today}.csv')

        else:
            product_dict = self.get_product_data(driver)
            df = self.get_product_df(product_dict, f'{search_val}_products_{today}.csv')

        driver.quit()
        return df


    def process_discount(self, df:pd.DataFrame):
        """
        Procesa el DataFrame de productos y envía mensajes de descuento a través de Telegram.
        Parámetros:
        df (pd.DataFrame): El DataFrame con los datos de los productos.
        """
        try:
            discount_df = df[df['discount'] >= self.discount_rate]
        except Exception as e:
            logging.error(e)
        for i,row in discount_df.iterrows():
            template = self.jinja_env.get_template('message.html')
            message = template.render(
                product_name=row['name'],
                price=row.price,
                discount=row.discount,
                link=row.link
            )
            for chat_id in self.telegram_bot.chat_ids:
                self.telegram_bot.send_message(chat_id, message, 'html')


    @timer
    def process(self):
        """
        Procesa los valores de búsqueda y realiza el scraping de productos en Amazon.
        Devuelve:
        pd.DataFrame: Un DataFrame con los datos de los productos obtenidos del scraping.
        """
        for search_val in self.search_values:
            search_url = self.get_search_url(search_val)
            logging.info('='*50)
            logging.info(f'Valor en busqueda: {search_val}')
            logging.info('='*50)
            df = self.scraping(search_url, search_val)
            self.process_discount(df)
