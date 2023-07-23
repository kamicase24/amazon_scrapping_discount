import logging
import time
from datetime import timedelta
import json
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pytz



BASE_PATH = os.path.dirname(os.path.abspath(__file__)).replace('/core', '')
load_dotenv(BASE_PATH+'/.envs/.env')

TZ=os.getenv('TZ', 'America/Lima')

def timer(func):
    def wrapper(*args, **kwargs):
        startt = time.time()
        logging.info(f'INICIA {func.__name__}')
        result = func(*args, **kwargs)
        endt = time.time()
        logging.info(f'FIN {func.__name__}')
        logging.info(f'{"="*15} Tiempo de ejecución {func.__name__}: {timedelta(seconds=endt-startt)} {"="*25}')
        return result

    return wrapper



class AmazonScrapping():

    def __init__(self):
        self.url = "https://www.amazon.com.mx//s?k=" 
        config = self.get_config()
        params = config['params']
        self.params = params
        self.use_amazon_filters = params.get('use_amazon_filters', False)
        self.search_values = params.get('search_values', [])
        self.amazon_filters = params.get('amazon_filters', {})
        self.download_df = params.get('download_df', False)


    def get_config(self):
        """
        Lee y carga la configuración desde el archivo 'config.json'.
        Returns:
            dict: Un diccionario que contiene los datos de configuración.
        """
        with open(f'{BASE_PATH}/config.json', 'r') as config_file:
            data = json.loads(config_file.read())
        return data
    

    def get_search_url(self, value:str):
        """
        Construye la URL de búsqueda para el valor proporcionado.
        Args:
            value (str): El valor que se utilizará para construir la URL de búsqueda.
        Returns:
            str: La URL de búsqueda completa que combina la URL base con el valor proporcionado.
        """
        return f'{self.url}{value}'


    def get_product_code(self, product_element):
        """
        Obtiene el código del producto desde un elemento del producto.
        Args:
            product_element (WebElement): El elemento del producto del cual se desea obtener el código.
        Returns:
            str or None: El código del producto obtenido desde el atributo 'data-asin' del elemento,
                o None si no se pudo obtener el código o ocurrió un error.
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
        Obtiene el nombre del producto desde un elemento del producto.
        Args:
            product_element (WebElement): El elemento del producto del cual se desea obtener el nombre.
        Returns:
            str or None: El nombre del producto obtenido desde el elemento,
                o None si no se pudo obtener el nombre o ocurrió un error.
        """
        product_name = None
        try:
            product_name_element = product_element.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
            product_name = product_name_element.text
            logging.info(f'Producto: {product_name}')
        except Exception as e:
            logging.error('Error al obtener el nombre del producto')
            logging.error(e.msg)
            import ipdb; ipdb.set_trace()

        return product_name


    def get_product_type(self, product_element):
        """
        Obtiene el tipo de producto desde un elemento del producto.
        Args:
            product_element (WebElement): El elemento del producto del cual se desea obtener el tipo.
        Returns:
            str: El tipo de producto, que puede ser 'sponsored', 'featured' o 'standard'.
                Si ocurre un error al obtener el tipo, se devolverá 'standard' por defecto.
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
        Obtiene el precio del producto desde un elemento del producto.
        Args:
            product_element (WebElement): El elemento del producto del cual se desea obtener el precio.
        Returns:
            float: El precio del producto como un valor decimal, o 0.00 si no se encuentra un precio válido.
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
            import ipdb; ipdb.set_trace()

        return product_price


    def get_product_price_list(self, product_element):
        """
        Obtiene el precio de lista del producto desde un elemento del producto.
        Args:
            product_element (WebElement): El elemento del producto del cual se desea obtener el precio de lista.
        Returns:
            float: El precio de lista del producto como un valor decimal, o 0.00 si no se encuentra un precio válido.
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
            import ipdb; ipdb.set_trace()
        return product_price_list


    def get_discount(self, price_list:float, price:float):
        """
        Calcula la tasa de descuento del producto.
        Args:
            price_list (float): El precio de lista del producto.
            price (float): El precio actual del producto.
        Returns:
            int: La tasa de descuento del producto como un porcentaje entero, o 0 si no hay descuento o si el precio de lista es cero.
        """
        product_discount_rate = 0
        if price_list > 0.00:
            discount_amount = price_list - price
            product_discount_rate = round((discount_amount / price_list) * 100)
        return product_discount_rate


    def get_product_link(self, product_element):
        try:
            product_link_element = product_element.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
            product_link = product_link_element.get_attribute('href')
            return product_link
        except Exception as e:
            logging.error('Error al obtener link del producto')
            return None


    def get_product_data(self, driver):
        page = 1
        page_limit = self.params.get('pagination_level', 1)
        product_list = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
        product_dict = {
            'code': [],
            'name': [],
            'price': [],
            'price_list': [],
            'discount %': [],
            'link': [],
            'type': [],
            'page': []
        }
        for active_page in range(page, page_limit+1):
            logging.info('='*50)
            logging.info(f'Pagina #: {active_page}')
            logging.info('='*50)

            # Paginación
            if active_page > 1:
                active_page_element = driver.find_element(By.XPATH, '//span[@class="s-pagination-item s-pagination-selected"]')
                next_page_element = active_page_element.find_element(By.XPATH, './following-sibling::a')
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
                product_dict['discount %'].append(discount)
                product_dict['type'].append(product_type)
                product_dict['link'].append(product_link)
                product_dict['page'].append(active_page)
        return product_dict


    def get_product_df(self, product_dict:dict, filename:str):
        try:
            df = pd.DataFrame(product_dict)
            if self.download_df:
                df.to_csv(f'results/{filename}', index=False)
        except Exception as e:
            logging.error('Error al generar DataFrame {e}')


    def scrapper(self, url, search_val):
        driver = webdriver.Chrome()
        driver.get(url)

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
                df = self.get_product_df(product_dict, f'{search_val}_{filter.replace(" ", "_")}_products.csv')

        else:
            product_dict = self.get_product_data(driver)
            df = self.get_product_df(product_dict, f'{search_val}_products.csv')

        driver.quit()
        return df


    @timer
    def process(self):
        for search_val in self.search_values:
            search_url = self.get_search_url(search_val)
            logging.info('='*50)
            logging.info(f'Valor en busqueda: {search_val}')
            logging.info('='*50)
            self.scrapper(search_url, search_val)
