# Weather Scraper
Este proyecto automatiza la recopilación y el procesamiento de datos meteorológicos históricos y previsionales. Utiliza Selenium y BeautifulSoup para extraer información de sitios web de clima, procesa los datos con Pandas y los almacena en archivos CSV limpios. Es ideal para análisis climáticos, visualización de datos o integración en otros sistemas.

## Archivos principales

*links_clima.ipynb*

Este archivo genera una lista de enlaces a datos climáticos históricos desde una fuente específica y los guarda en un archivo de texto.

*proceso_clima.ipynb*

Este archivo lee las URLs generadas en links_clima.ipynb, accede a cada una con Selenium, extrae la información relevante sobre el clima con BeautifulSoup y la almacena en formato CSV para su posterior análisis.

*limpieza_clima.ipynb*

Este script se encarga de limpiar y estructurar los datos crudos extraídos con el archivo proceso_clima.ipynb. Realiza las siguientes tareas:

- Separa el título en ciudad y fecha.

- Extrae información de temperatura, precipitación, viento y humedad.

- Genera un DataFrame limpio y lo guarda en limpio/clima_limpio.csv para su análisis posterior.

*links_prevision.ipynb*

Este archivo genera una lista de enlaces a datos de previsión climática desde una fuente específica y los guarda en un archivo de texto.

*proceso_prevision.ipynb*

Este archivo lee las URLs generadas en links_prevision.ipynb, accede a cada una con Selenium, extrae la información relevante sobre el clima con BeautifulSoup y la almacena en formato CSV para su posterior análisis.

*limpieza_prevision.ipynb*

Este script se encarga de limpiar y estructurar los datos crudos extraídos con el archivo proceso_prevision.ipynb. Realiza las siguientes tareas:

- Extrae información de ciudad, fecha de recolección de datos, fecha de la previsión, temperaturas máxima y mínima, clima esperado y viento.

- Genera un DataFrame limpio y lo guarda en limpio/pronostico.csv, incluyendo la fecha de extracción de los datos para su análisis posterior.

## Requisitos

- Python 3

- Selenium

- BeautifulSoup

- Pandas

## Uso

Ejecutar los notebooks en el orden indicado para obtener y procesar los datos climáticos.





