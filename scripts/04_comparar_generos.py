from pathlib import Path
import pandas as pd

# 1. Usar los videojuegos con datos en los mismos 21 meses.
carpeta = Path(__file__).resolve().parent.parent
datos = pd.read_csv(carpeta / 'datos/limpios/videojuegos_2024_2025.csv')
datos = datos[datos['periodo_completo']].copy()

# 2. Calcular una media del periodo por juego. Cada juego pesa lo mismo.
juegos = datos.groupby(['id_juego', 'juego', 'generos']).agg(
    jugadores_medios=('jugadores_medios', 'mean'),
    meses=('mes', 'nunique')
).reset_index()

# 3. Separar los géneros en filas. Un juego puede pertenecer a varios.
juegos['genero_original'] = juegos['generos'].str.split(', ')
por_genero = juegos.explode('genero_original')

# Indie, acceso anticipado y gratuito son características, no géneros de juego.
traducciones = {
    'Action': 'Acción', 'Adventure': 'Aventura', 'Strategy': 'Estrategia',
    'Simulation': 'Simulación', 'Casual': 'Casual', 'RPG': 'Rol',
    'Massively Multiplayer': 'Multijugador masivo',
    'Sports': 'Deportes', 'Racing': 'Carreras'
}
por_genero = por_genero[por_genero['genero_original'].isin(traducciones)].copy()
por_genero['genero'] = por_genero['genero_original'].map(traducciones)
por_genero = por_genero.drop_duplicates(['id_juego', 'genero'])

# 4. Comparar el juego medio y el juego situado en el centro de cada grupo.
resumen = por_genero.groupby('genero').agg(
    numero_juegos=('id_juego', 'nunique'),
    media_jugadores=('jugadores_medios', 'mean'),
    mediana_jugadores=('jugadores_medios', 'median')
).reset_index().sort_values('mediana_jugadores', ascending=False)

# 5. Mostrar el juego con mayor media de cada género.
lideres = por_genero.sort_values('jugadores_medios', ascending=False)
lideres = lideres.drop_duplicates('genero')
lideres = lideres[['genero', 'juego', 'jugadores_medios']]
lideres = lideres.rename(columns={'juego': 'juego_lider',
                                  'jugadores_medios': 'media_juego_lider'})
resumen = resumen.merge(lideres, on='genero', validate='one_to_one')

assert juegos['meses'].eq(21).all()
assert not por_genero.duplicated(['id_juego', 'genero']).any()
assert resumen['numero_juegos'].sum() == len(por_genero)

salida = carpeta / 'resultados'
salida.mkdir(exist_ok=True)
resumen.to_csv(salida / 'comparacion_generos.csv', index=False, encoding='utf-8-sig')
por_genero[['id_juego', 'juego', 'genero', 'jugadores_medios']].to_csv(
    salida / 'juegos_por_genero.csv', index=False, encoding='utf-8-sig')
print(resumen.to_string(index=False, float_format='%.2f'))
print('Juegos de la muestra completa:', len(juegos))
print('Juegos con alguno de los géneros comparados:', por_genero['id_juego'].nunique())
