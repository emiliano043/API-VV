import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

# Ruta del archivo .log
log_path = r'C:\Users\emili\Downloads\API-VV\api_logs2.log'

# Expresión para extraer los datos de las líneas
log_pattern = re.compile(
    r"Estado:\s(?P<estado>\d+),\sRespuesta:\s\{[^}]*?'tiempo':\s'(?P<tiempo>[^']+)',\s'[^']*estado':\s(?P<estado2>\d+),\s'metodo':\s'(?P<metodo>\w+)',.*?'decode':\s(?P<decode>[\d.]+)"
)

''' 
Estados HTTP:
200 - OK
404 - NOT FOUND
415 - UNSUPPORTED MEDIA TYPE
'''

# Lista para almacenar los registros
data = []

# Leer y analizar log
with open(log_path, 'r', encoding='utf-8') as file:
    for line in file:
        match = log_pattern.search(line)
        if match:
            estado = int(match.group('estado'))
            metodo = match.group('metodo')
            tiempo = datetime.strptime(match.group('tiempo'), "%Y-%m-%d %H:%M:%S.%f")
            decode = float(match.group('decode'))
            data.append({
                'estado': estado,
                'metodo': metodo,
                'tiempo': tiempo,
                'decode': decode
            })

# Crear DataFrame
df = pd.DataFrame(data)

# Gráfica 1: Conteo de peticiones por método
plt.figure(figsize=(6, 4))
df['metodo'].value_counts().plot(kind='bar', color='skyblue')
plt.title('Número de peticiones por método')
plt.xlabel('Método')
plt.ylabel('Cantidad')
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfica 2: Estados HTTP por tipo
plt.figure(figsize=(6, 4))
df['estado'].value_counts().sort_index().plot(kind='bar', color='salmon')
plt.title('Distribución de códigos de estado HTTP')
plt.xlabel('Código de estado')
plt.ylabel('Cantidad')
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfica 3: Conteo de peticiones por método y estados 
df.groupby(['metodo', 'estado']).size().unstack(fill_value=0).plot(kind='bar', stacked=True, colormap='tab20', width=0.8)
plt.title('Número de peticiones por método y estado')
plt.xlabel('Método')
plt.ylabel('Cantidad')
plt.grid(True)
plt.legend(title='Código de estado', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Gráfica 4: Tiempo promedio de decode por método
plt.figure(figsize=(6, 4))
df.groupby('metodo')['decode'].mean().plot(kind='bar', color='limegreen')
plt.title('Tiempo promedio de decode por método')
plt.xlabel('Método')
plt.ylabel('Tiempo (s)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfica 5: Tráfico temporal (peticiones por segundo)
df['hora'] = df['tiempo'].dt.floor('h')
plt.figure(figsize=(10, 4))
df.groupby('hora').size().plot(kind='line', marker='o', color='orange')
plt.title('Peticiones por hora')
plt.xlabel('Hora')
plt.ylabel('Cantidad de peticiones')
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()

# Gráfica 6: Tráfico temporal (peticiones por decode)
df['tiempo_decode_acumulado'] = df['decode'].cumsum() / 3600
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['tiempo_decode_acumulado'], color='blue', linewidth=2)
plt.title('Tiempo Acumulado usando solo Decode')
plt.xlabel('Número de solicitudes')
plt.ylabel('Tiempo acumulado (horas)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfica 7: Tráfico temporal (peticiones por factores externos)
df['tiempo_real_transcurrido'] = (df['tiempo'] - df['tiempo'].iloc[0]).dt.total_seconds() / 3600
df['factores_externos'] = df['tiempo_real_transcurrido'] - df['tiempo_decode_acumulado']
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['factores_externos'], color='purple', linewidth=2)
plt.title('Tiempo acumulado por factores externos (real - decode)')
plt.xlabel('Número de solicitudes')
plt.ylabel('Tiempo extra acumulado (horas)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfica comparativa
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['tiempo_decode_acumulado'], color='blue', linewidth=2, label='Tiempo acumulado Decode')
plt.plot(df.index, df['factores_externos'], color='green', linewidth=2, label='Tiempo acumulado por factores externos')
plt.plot(df.index, df['tiempo_real_transcurrido'], color='red', linewidth=2, label='Tiempo Real Transcurrido')
plt.title('Comparación: Tiempo Real vs Timepo Factores Externas vs Tiempo Decode')
plt.xlabel('Número de solicitudes')
plt.ylabel('Tiempo acumulado (horas)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
