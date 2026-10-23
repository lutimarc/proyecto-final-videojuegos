from pathlib import Path
import pandas as pd

carpeta = Path(__file__).resolve().parent.parent
datos = pd.read_csv(carpeta / 'datos/limpios/juegos_jugadores_2024_2025.csv')
datos['mes'] = pd.to_datetime(datos['mes'])
datos['fecha_lanzamiento'] = pd.to_datetime(datos['fecha_lanzamiento'])

# Comprobar el tamaño, los duplicados y las celdas vacías.
print('Filas:', len(datos))
print('Columnas:', len(datos.columns))
print('Juegos:', datos['id_juego'].nunique())
print('Juegos y meses repetidos:', datos.duplicated(['id_juego', 'mes']).sum())
print('\nCeldas vacías:')
print(datos.isna().sum().to_string())

# Revisar que las cifras de jugadores y precios sean coherentes.
print('\nPrecios negativos:', (datos['precio_usd_marzo_2025'] < 0).sum())
print('Jugadores medios negativos:', (datos['jugadores_medios'] < 0).sum())
print('Máximos inferiores a la media:',
      (datos['jugadores_maximos'] < datos['jugadores_medios']).sum())

# Contar los juegos sin información, sin repetirlos por cada mes.
juegos = datos.drop_duplicates('id_juego')
columnas_resenas = ['resenas_positivas_marzo_2025', 'resenas_negativas_marzo_2025',
                   'total_resenas_marzo_2025', 'proporcion_resenas_positivas_marzo_2025']
assert datos.loc[datos['resenas_por_revisar'], columnas_resenas].isna().all().all()
print('Productos con recuentos de reseñas por revisar:', juegos['resenas_por_revisar'].sum())
for columna in ['generos', 'desarrolladores', 'editoras']:
    sin_datos = juegos[columna].isna() | juegos[columna].eq('Sin información')
    print('Juegos sin información en', columna, ':', sin_datos.sum())

# Una actividad anterior al lanzamiento requiere revisión, no borrado automático.
mes_lanzamiento = datos['fecha_lanzamiento'].dt.to_period('M').dt.to_timestamp()
anteriores = datos[datos['mes'] < mes_lanzamiento]
print('\nFilas anteriores al mes de lanzamiento:', len(anteriores))
print('Juegos afectados:', anteriores['id_juego'].nunique())

# La cobertura cambia por mes: una ausencia no significa cero jugadores.
print('\nJuegos con datos en cada mes:')
print(datos.groupby('mes')['id_juego'].nunique().to_string())
meses_por_juego = datos.groupby('id_juego')['mes'].nunique()
print('\nJuegos con los 21 meses:', (meses_por_juego == 21).sum())
