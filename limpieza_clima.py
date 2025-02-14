# Importamos las librerías necesarias
import pandas as pd

# Cargamos el archivo de datos con nombres de columnas
data = pd.read_csv('crudo/clima_crudo.csv', sep=',', encoding='utf-8', header=None)

# Configuración de Pandas para visualización completa
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)

# Diccionario de mapeo de meses a números
meses_a_numeros = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

# Creamos nuevas columnas con los datos necesarios
data['ciudad'] = data[1].str.split(' - ', expand=True)[0]
data['date'] = data[1].str.split(' - ', expand=True)[1]
data['mes'] = data['date'].str.split(' ').apply(lambda x: x[2]).map(meses_a_numeros)
data['fecha'] = data['date'].str.split(' ').apply(lambda x: x[0]) + '/' + data['mes'] + '/2024'
data['t_max'] = data[2].str.split(' ', expand=True)[1]
data['t_min'] = data[2].str.split(' ', expand=True)[3]
data['precipitacion'] = data[2].str.split(' ', expand=True)[5] + ' ' + data[2].str.split(' ', expand=True)[6]
data['viento'] = data[2].str.split(' ', expand=True)[8] + ' ' + data[2].str.split(' ', expand=True)[9]
data['humedad'] = data[2].str.split(' ', expand=True)[11] + ' ' + data[2].str.split(' ', expand=True)[12]

# Creamos un nuevo DataFrame con las columnas que nos interesan
limpio = data[['ciudad', 'fecha', 't_max', 't_min', 'precipitacion', 'viento', 'humedad']]

# Guardamos el nuevo DataFrame en un archivo CSV
limpio.to_csv('limpio/clima_limpio.csv', sep=',', encoding='utf-8', index=False)

print("Limpieza completada. Archivo guardado en limpio/clima_limpio.csv")