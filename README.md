# Amazon scraping

Este proyecto es un web scraper que realiza la extracción de datos de productos de Amazon. Utiliza Selenium WebDriver para interactuar con la página web de búsqueda de Amazon y obtener información sobre productos como su código, nombre, precio, descuento, enlace, entre otros. El scraping se puede realizar para diferentes valores de búsqueda y con filtros opcionales aplicados a la búsqueda. Además, la herramienta utiliza el bot de Telegram para enviar notificaciones a los usuarios interesados en ciertos productos.

## Archivos de la Herramienta

La herramienta se compone de los siguientes archivos:

1. `run.py`: Archivo principal que ejecuta el proceso de scraping en Amazon y envía notificaciones por Telegram a los usuarios configurados.

2. `update_chat.py`: Archivo encargado de actualizar los ID de chat con los usuarios del bot de Telegram y guardarlos en el archivo de configuración.

3. `config.json`: Archivo JSON que contiene los parámetros de configuración de la herramienta.

## Requisitos

Antes de utilizar este proyecto, asegúrese de tener los siguientes requisitos instalados:

* Python 3.x (se recomienda la versión más reciente)
* Selenium WebDriver (se utiliza para interactuar con el navegador)
* pandas (para el manejo de datos en forma de DataFrame)
* ChromeDriver (controlador del navegador Chrome) o el controlador adecuado para su navegador preferido

## Configuración

El archivo `config.json` contiene los parámetros de configuración necesarios para el funcionamiento de la herramienta. Estos parámetros son los siguientes:

* `version` (float): La versión de la herramienta.
* `params` (dict): Un diccionario que contiene los siguientes parámetros:
  * `discount_rate` (int): La tasa de descuento mínima requerida para enviar notificaciones por Telegram. Si un producto tiene un descuento igual o mayor a esta tasa, se enviará una notificación.
  * `search_values` (list): Una lista de cadenas que representan los valores de búsqueda para los productos en Amazon.
  * `use_amazon_filters` (bool): Un valor booleano que indica si se deben utilizar filtros específicos de Amazon al realizar el scraping.
  * `amazon_filters` (dict): Un diccionario que contiene filtros específicos de Amazon para aplicar durante el proceso de scraping. Las claves son los identificadores de los filtros, y los valores son las descripciones de los filtros.
  * `pagination_level` (int): El nivel de paginación, que determina la cantidad de páginas a recorrer durante el proceso de scraping.
  * `download_df` (bool): Un valor booleano que indica si se deben descargar los datos obtenidos durante el scraping en un archivo CSV.
  * `chat_ids` (dict): Un diccionario vacío que se llenará automáticamente con los ID de chat de los usuarios que interactúan con el bot de Telegram.

## Ejecución

Para ejecutar el proceso de scraping, simplemente ejecute el archivo `run.py` en la línea de comandos:

```bash
python run.py
```

El proceso de scraping en Amazon se llevará a cabo de acuerdo con los parámetros de configuración y se enviarán notificaciones por Telegram según los descuentos encontrados. Opcionalmente, si necesitas actualizar los ID de chat con los usuarios del bot de Telegram, ejecuta el archivo `update_chat.py`:

```bash
python update_chat.py
```

Esto actualizará automáticamente el diccionario `chat_ids` en el archivo `config.json` con los nuevos ID de chat.

## Resultados

Los resultados del scraping se almacenan en archivos CSV en la carpeta "results". Cada archivo contendrá los datos de productos para un valor de búsqueda específico o un valor de búsqueda más un filtro aplicado.

## Registro de Eventos

Durante la ejecución de la herramienta, se generará un registro de eventos que se guardará en el directorio `logs`. Los eventos registrados incluyen información relevante sobre el proceso de scraping y las notificaciones enviadas por Telegram.

## Notas

* La herramienta utiliza el módulo `selenium` para realizar el scraping en el sitio web de Amazon. Asegúrate de tener el controlador de navegador adecuado (por ejemplo, el controlador de Chrome) instalado y configurado correctamente para que `selenium` funcione correctamente.

* Para recibir notificaciones por Telegram, asegúrate de haber configurado el token de acceso y otros detalles del bot en el archivo `core/telegram.py`.

* Esta herramienta es solo un ejemplo y puede requerir modificaciones y ajustes adicionales según tus necesidades específicas.
