# Importamos las librerías necesarias
import pandas as pd
import re

# Ruta donde se encuentran los archivos
file_links = 'data/links_tiempo.txt'

# Cargamos el archivo en un DataFrame, eliminando líneas vacías
with open(file_links, 'r') as f:
    links = [line.strip() for line in f if line.strip()]

# Convertimos la lista en un DataFrame
df_links = pd.DataFrame(links, columns=['link'])

# Crear una nueva columna 'base' con la base de la url
df_links['base'] = df_links['link'].apply(lambda x: re.search(r'(https?://[^?]+)', x).group(1))

# Generar todas las combinaciones de días y meses
# Días en cada mes (suponiendo un año bisiesto como 2024)
dias_por_mes = {
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

# Generar las nuevas URLs usando listas por comprensión
nuevas_urls = [
    {"url_completa": f"{base_url}?page=past-weather#day={dia}&month={mes}"}
    for base_url in df_links['base']
    for mes, dias in dias_por_mes.items()
    for dia in range(1, dias + 1)
]

# Crear un nuevo DataFrame con las URLs generadas
df_resultado = pd.DataFrame(nuevas_urls)

# Mostrar resultado sin truncar columnas
pd.set_option('display.max_colwidth', None)
print(df_resultado)

# Guardar el resultado en un archivo txt
df_resultado.to_csv('data/links_tiempo_completo.txt', index=False, header=False)
