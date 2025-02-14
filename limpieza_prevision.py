# Importamos las librerías necesarias
import pandas as pd
import time

# Cargamos el archivo de datos
hoy = time.strftime('%Y-%m-%d')
data = pd.read_csv(f'crudo/pronostico_{hoy}.csv', sep=',', encoding='utf-8-sig')

# Configuración de Pandas para visualización completa
pd.set_option('display.max_columns', None)  # Muestra todas las columnas
pd.set_option('display.max_colwidth', None)  # Evita truncar el contenido de las celdas
pd.set_option('display.expand_frame_repr', False)  # Evita dividir el DataFrame en varias líneas

# Mostramos los primeros registros  
print(data.head(10))

# Diccionario de mapeo de meses a números
meses_a_numeros = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

# Creamos nuevas columnas con los datos necesarios
data['date'] = data['Fecha'].str.split(', ', expand=True)[1]
data['mes'] = data['date'].str.split(' ').apply(lambda x: x[1]).map(meses_a_numeros)
data['fecha_prevision'] = '2025-' + data['mes'] + '-' + data['date'].str.split(' ').apply(lambda x: x[0])
data['t_max'] = data['Temperatura'].str.split('/', expand=True)[0]
data['t_min'] = data['Temperatura'].str.split('/', expand=True)[1]

# Creamos un nuevo DataFrame con las columnas que nos interesan
limpio = data[['ciudad', 'fecha_datos', 'fecha_prevision', 't_max', 't_min', 'Clima', 'Viento']]

# Guardamos el nuevo DataFrame en un archivo CSV
limpio.to_csv(f'limpio/pronostico_{hoy}.csv', sep=',', encoding='utf-8', index=False)