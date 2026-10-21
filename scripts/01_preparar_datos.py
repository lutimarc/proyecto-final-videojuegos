from pathlib import Path
import ast
import pandas as pd

# 1. Leer los dos archivos originales.
carpeta = Path(__file__).resolve().parent.parent
columnas = [
    'appid', 'name', 'release_date', 'required_age', 'price', 'dlc_count',
    'windows', 'mac', 'linux', 'achievements', 'recommendations',
    'developers', 'publishers', 'genres', 'positive', 'negative'
]
juegos = pd.read_csv(carpeta / 'datos/originales/games_march2025_full.csv',
                     usecols=columnas)
jugadores = pd.read_csv(carpeta / 'datos/originales/steamcharts.csv')

# 2. Convertir las fechas y seleccionar el periodo del estudio.
jugadores['month'] = pd.to_datetime(jugadores['month'], format='%b-%y')
jugadores = jugadores[jugadores['month'].between('2024-01-01', '2025-09-01')].copy()
juegos['release_date'] = pd.to_datetime(juegos['release_date'], errors='coerce')

# 3. Convertir las listas de géneros y empresas en texto legible.
def limpiar_lista(valor):
    if pd.isna(valor) or valor == '[]':
        return 'Sin información'
    elementos = ast.literal_eval(valor)
    texto = ', '.join(str(elemento).strip() for elemento in elementos
                      if str(elemento).strip())
    return texto if texto else 'Sin información'

for columna in ['genres', 'developers', 'publishers']:
    juegos[columna] = juegos[columna].apply(limpiar_lista)

juegos['name'] = juegos['name'].str.strip()
jugadores['gain'] = pd.to_numeric(jugadores['gain'], errors='coerce')

# 4. Unir por el identificador. Conservar solo los juegos de ambas fuentes.
datos = jugadores.merge(juegos, left_on='steam_appid', right_on='appid',
                         how='inner', validate='many_to_one',
                         suffixes=('_historico', '_catalogo'))
datos = datos.drop(columns=['steam_appid', 'name_historico'])

# 5. Poner nombres en español. El precio y las reseñas son de marzo de 2025.
datos = datos.rename(columns={
    'appid': 'id_juego', 'name_catalogo': 'juego', 'month': 'mes',
    'avg_players': 'jugadores_medios', 'peak_players': 'jugadores_maximos',
    'gain': 'cambio_jugadores', 'gain_percent': 'variacion_jugadores',
    'release_date': 'fecha_lanzamiento', 'required_age': 'edad_minima',
    'price': 'precio_usd_marzo_2025', 'dlc_count': 'numero_dlc',
    'achievements': 'logros', 'recommendations': 'recomendaciones_marzo_2025',
    'developers': 'desarrolladores', 'publishers': 'editoras',
    'genres': 'generos', 'positive': 'resenas_positivas_marzo_2025',
    'negative': 'resenas_negativas_marzo_2025'
})

# 6. Añadir datos útiles para el análisis y el dashboard.
datos['ano'] = datos['mes'].dt.year
datos['numero_mes'] = datos['mes'].dt.month
datos['es_gratis_marzo_2025'] = datos['precio_usd_marzo_2025'] == 0
datos['total_resenas_marzo_2025'] = (datos['resenas_positivas_marzo_2025']
                                      + datos['resenas_negativas_marzo_2025'])
datos['proporcion_resenas_positivas_marzo_2025'] = (
    datos['resenas_positivas_marzo_2025']
    / datos['total_resenas_marzo_2025'].replace(0, float('nan'))
)

# Si falta el cambio mensual, su porcentaje tampoco se considera conocido.
datos.loc[datos['cambio_jugadores'].isna(), 'variacion_jugadores'] = float('nan')

# La fecha del catálogo puede ser la salida de acceso anticipado o una reedición.
# Conservarla, pero marcar todos los registros de los juegos que necesitan revisión.
mes_lanzamiento = datos['fecha_lanzamiento'].dt.to_period('M').dt.to_timestamp()
anteriores = datos[datos['mes'] < mes_lanzamiento]
ids_fecha_dudosa = anteriores['id_juego'].unique()
datos['fecha_lanzamiento_por_revisar'] = datos['id_juego'].isin(ids_fecha_dudosa)

# Comparar la evolución con los mismos juegos en los 21 meses.
meses_por_juego = datos.groupby('id_juego')['mes'].nunique()
ids_periodo_completo = meses_por_juego[meses_por_juego == 21].index
datos['periodo_completo'] = datos['id_juego'].isin(ids_periodo_completo)

# 7. Comprobar que la unión no repite juegos en un mismo mes.
# Se conservan los valores extremos reales y los cambios mensuales negativos.
# Los datos ausentes no se sustituyen por ceros.
assert not datos.duplicated(['id_juego', 'mes']).any(), 'Hay juegos y meses repetidos'
assert len(datos) >= 50000, 'No se alcanza el mínimo de filas'
assert len(datos.columns) >= 20, 'No se alcanza el mínimo de columnas'
assert datos[['jugadores_medios', 'jugadores_maximos']].notna().all().all()
assert (datos['jugadores_medios'] >= 0).all()
assert (datos['jugadores_maximos'] >= datos['jugadores_medios']).all()

# 8. Guardar una tabla ordenada sin modificar los originales.
datos = datos.sort_values(['id_juego', 'mes'])
primeras = ['id_juego', 'juego', 'mes', 'ano', 'numero_mes']
datos = datos[primeras + [col for col in datos.columns if col not in primeras]]
salida = carpeta / 'datos/limpios'
salida.mkdir(parents=True, exist_ok=True)
datos.to_csv(salida / 'juegos_jugadores_2024_2025.csv', index=False, encoding='utf-8-sig')

# Guardar la lista de fechas dudosas para que la revisión sea visible.
revision = anteriores.groupby(['id_juego', 'juego', 'fecha_lanzamiento']).agg(
    primer_mes_observado=('mes', 'min'),
    meses_anteriores=('mes', 'size')
).reset_index()
revision['observacion'] = 'Actividad anterior a la fecha del catálogo; no usar para calcular antigüedad'
revision['fuente_consulta'] = ''
revision.loc[revision['id_juego'] == 526870, 'observacion'] = (
    'Steam: acceso anticipado 08/06/2020; versión completa 10/09/2024. Se conserva la fecha de versión completa.'
)
revision.loc[revision['id_juego'] == 526870, 'fuente_consulta'] = 'https://www.satisfactorygame.com/support/'
revision.to_csv(salida / 'revision_fechas.csv', index=False, encoding='utf-8-sig')

print('Filas:', len(datos))
print('Columnas:', len(datos.columns))
print('Juegos:', datos['id_juego'].nunique())
print('Datos ausentes por columna:')
print(datos.isna().sum().to_string())
print('Filas sin género:', (datos['generos'] == 'Sin información').sum())
