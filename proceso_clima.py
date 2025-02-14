from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Archivos de entrada/salida
file_name = 'data/links_tiempo_completo.txt'
file_name_act = 'crudo/clima_crudo.csv'
progreso_file = 'progreso/progreso_clima.csv'

# Cargar URLs eliminando duplicados
with open(file_name, 'r') as file:
    urls = {line.strip() for line in file if "http" in line}

print(f"Se encontraron {len(urls)} URLs en el archivo {file_name}")

# Cargar progreso y filtrar URLs pendientes
try:
    procesadas = set(pd.read_csv(progreso_file, header=None)[0])
except FileNotFoundError:
    procesadas = set()

urls_restantes = urls - procesadas
print(f"Se encontraron {len(urls_restantes)} URLs pendientes de procesar.")

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
        driver.get(url)
        driver.save_screenshot('debug_screenshot.png')

        # Intentar cerrar pop-up si existe
        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_1200818"]'))
            )
            driver.switch_to.frame(iframe)
            button_accept = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceptar")]'))
            )
            button_accept.click()
            print("Botón 'Aceptar' clickeado.")
            driver.switch_to.default_content()
            print(f"Popup cerrado")
        except:
            print(f"El iframe del popup no apareció. Continuando...")
            pass  # Si no hay pop-up, continuar normalmente

        # Extraer contenido de la página
        time.sleep(5)  # Pausa de 5 segundos antes de continuar
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extraer el título principal
        header = soup.find('div', class_='page-header')
        header_text = header.get_text(strip=True) if header else "Sin título"

        # Extraer la fecha del sub-header
        sub_header = soup.find('div', class_='page-sub-header')
        date_span = sub_header.find('span', class_='page-date') if sub_header else None
        date_text = date_span.get_text(strip=True) if date_span else "Sin fecha"

        # Formar el título
        title = f"{header_text} - {date_text}"

        # Verificar si la página tiene error
        if "Error" in title:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now} - Se detectó un error en la página. Esperando 5 minutos antes de continuar.")
            driver.quit()
            time.sleep(300)  # Pausa de 5 minutos antes de continuar
            return

        print(f"Título de la página: {title}")

        # Extraer datos del clima
        clima_divs = soup.find_all('div', class_='month-bubbles past-bubbles')
        informacion_clima = []

        if clima_divs:
            for div in clima_divs:
                informacion_clima.extend(div.text.split())  # Extraer y combinar texto de cada div encontrado
            print(f"Información de clima extraída correctamente")
        else:
            print(f"No se encontró contenido relevante en {url}")
            time.sleep(10)  # Pausa de 10 segundos antes de continuar

        # Guardar datos en CSV
        pd.DataFrame([[url, title, ' '.join(informacion_clima)]]).to_csv(
            'crudo/clima_crudo.csv', mode='a', index=False, header=False, encoding='utf-8-sig'
        )
        print("Datos de clima guardados")

        # Registrar progreso
        with open(progreso_file, 'a') as f:
            f.write(f"{url}\n")

        print(f"Procesada: {url}")

    except Exception as e:
        print(f"Error en {url}: {e}")

    finally:
        driver.quit()

# Procesar todas las URLs restantes
for url in urls_restantes:
    url_clima(url)

# Eliminar duplicados en el archivo de clima procesado
pd.read_csv(file_name_act).drop_duplicates().to_csv(file_name_act, index=False)