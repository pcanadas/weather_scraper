from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os
import time

# Leer las URLs del archivo
file_name = 'data/links_prevision.txt' # Nombre del archivo

# Cargar URLs eliminando duplicados
with open(file_name, 'r') as file:
    urls = {line.strip() for line in file if "http" in line}

# Imprimir el número de URLs encontradas
print(f"Se encontraron {len(urls)} urls en el archivo {file_name}") 

# Cargar progreso existente
hoy = time.strftime("%Y-%m-%d")  # Fecha actual
def cargar_progreso():
    progreso_file = f'progreso/progreso_prevision_{hoy}.csv' # Archivo para guardar el progreso
    try:
        procesadas = pd.read_csv(progreso_file, header=None)[0].tolist()
        print(f"Se encontraron {len(procesadas)} URLs procesadas anteriormente")
    except FileNotFoundError:
        procesadas = []
    return procesadas, progreso_file

procesadas, progreso_file = cargar_progreso()

# Filtrar las URLs no procesadas
urls_restantes = [url for url in urls if url not in procesadas]
print(f"Se encontraron {len(urls_restantes)} URLs restantes para procesar")

# Configuración del navegador
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
)

# Función para procesar cada URL
def url_clima(url):
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Abre la URL
        driver.get(url)
        driver.save_screenshot('debug_screenshot.png')

        # Intenta cerrar el popup si existe
        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_1200818"]'))
            )
            driver.switch_to.frame(iframe)
            try:
                # Ahora intenta localizar y hacer clic en el botón "Aceptar" dentro del iframe
                button_accept = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceptar")]'))
                )
                button_accept.click()
                print("Botón 'Aceptar' clickeado.")
            except Exception as e:
                print("El botón 'Aceptar' no se encontró o no fue clickeable.")
            finally:
                driver.switch_to.default_content()
                print(f"Popup cerrado")
        except Exception:
            print(f"El iframe del popup no apareció. Continuando...")
            pass

        # Extraer el HTML procesado
        time.sleep(5)  # Pausa de 5 segundos antes de continuar
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extraer el texto de la cabecera
        header = soup.find('div', class_='page-header')
        header_text = header.get_text(strip=True) if header else "Sin título"

        # Añadir fecha de hoy
        date_text = time.strftime("%Y-%m-%d")

        ciudad = header_text

        # Formar el título
        title = f"{header_text} - {date_text}"

        # Verificar si el título contiene "Error"
        if "Error" in title:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now} - Se detectó un error en la página. Esperando 5 minutos antes de continuar.")
            driver.quit()  # Cerrar el navegador
            time.sleep(300)  # Pausa de 5 minutos antes de continuar
            return  # Salir de la función
        
        print(f"Título de la página: {title}")

        # Extraer contenido específico de la página
        tabla = soup.find('table', class_='table fourteen-table')  # Buscar la tabla con la clase específica

        informacion_tabla = []
        if tabla:
            filas = tabla.find_all('tr')  # Encontrar todas las filas de la tabla
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])  # Buscar celdas de la fila (pueden ser 'td' o 'th')
                fila_datos = [celda.get_text(strip=True) for celda in celdas]  # Extraer el texto de cada celda
                if fila_datos:  # Si la fila no está vacía
                    informacion_tabla.append(fila_datos)
            
            print(f"Información de pronostico extraída")
        else:
            print(f"No se encontró contenido relevante en {url}")
            time.sleep(10)  # Pausa de 10 segundos antes de continuar

        # Convertir la información extraída en un DataFrame
        if informacion_tabla:
            tabla_info = pd.DataFrame(informacion_tabla)
            # Si las columnas tienen encabezados, usa la primera fila como nombres de columna
            if len(tabla_info) > 1:
                tabla_info.columns = tabla_info.iloc[0]  # Usar la primera fila como encabezado
                tabla_info = tabla_info[1:]  # Eliminar la fila de encabezados del contenido
            tabla_info.reset_index(drop=True, inplace=True)
        else:
            tabla_info = pd.DataFrame()

        # Agregar información adicional (si aplica)
        tabla_info['ciudad'] = ciudad
        tabla_info['fecha_datos'] = date_text
        tabla_info['url'] = url
        # Renombrar la columna específica
        if len(tabla_info.columns) > 5:  # Asegurarte de que exista la columna 6
            columna_actual = tabla_info.columns[5]
            if columna_actual != 'Clima':  # Solo renombrar si no se llama ya 'Clima'
                tabla_info.rename(columns={columna_actual: 'Clima'}, inplace=True)

        # Eliminar columnas duplicadas si existen
        tabla_info = tabla_info.loc[:, ~tabla_info.columns.duplicated()]

        # Reordenar columnas: 'ciudad', 'fecha_datos', 'url' primero, y luego el resto
        columnas_deseadas = ['ciudad', 'fecha_datos', 'url', 'Fecha', 'Temperatura', 'Clima', 'Viento'] # Columnas en el orden deseado
        # Eliminar filas con la fecha 'Más adelante'
        tabla_info = tabla_info[tabla_info['Fecha'] != 'Más adelante']
        tabla_final = tabla_info[columnas_deseadas]  # Reordenar las columnas

        # Nombre del archivo
        file_path = f'crudo/pronostico_{date_text}.csv'

        # Comprobar si el archivo ya existe
        file_exists = os.path.exists(file_path)

        # Guardar los datos en el archivo CSV
        tabla_final.to_csv(
            file_path,
            mode='a',  # Modo "append" para agregar datos sin sobrescribir
            index=False,
            header=not file_exists,  # Escribir encabezado solo si el archivo no existe
            encoding='utf-8-sig')
        print("Datos de pronostico guardados")
    
        # Registrar progreso
        with open(progreso_file, 'a') as f:
            f.write(f"{url}\n")
        print(f"Progreso guardado")
    
    except Exception as e:
        print(f"Error al procesar la URL {url}: {e}")
    finally:
        # Cerrar el navegador para esta URL
        driver.quit()        

# Procesar las URLs 
for url in urls_restantes:
    url_clima(url)