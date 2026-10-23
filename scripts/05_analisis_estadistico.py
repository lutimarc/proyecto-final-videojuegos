from pathlib import Path
import pandas as pd

# 1. Usar los mismos juegos durante enero de 2024 a septiembre de 2025.
carpeta = Path(__file__).resolve().parent.parent
datos = pd.read_csv(carpeta / 'datos/limpios/videojuegos_2024_2025.csv')
datos = datos[datos['periodo_completo']].copy()

# 2. Una fila por juego, para no contar su precio y sus reseñas 21 veces.
actividad = datos.groupby('id_juego')['jugadores_medios'].mean()
actividad = actividad.rename('media_jugadores_periodo').reset_index()
catalogo = datos.drop_duplicates('id_juego')[[
    'id_juego', 'juego', 'precio_usd_marzo_2025',
    'proporcion_resenas_positivas_marzo_2025',
    'total_resenas_marzo_2025', 'precio_cero_marzo_2025', 'resenas_por_revisar'
]]
juegos = catalogo.merge(actividad, on='id_juego', validate='one_to_one')

# 3. Correlación de Spearman: compara el orden de los valores.
# Es útil porque unos pocos juegos tienen muchísimos más jugadores que el resto.
# Va de -1 a 1. Cerca de cero indica poca relación en el orden de los valores.
variables = {
    'precio_usd_marzo_2025': 'Precio',
    'proporcion_resenas_positivas_marzo_2025': 'Proporción de reseñas positivas',
    'total_resenas_marzo_2025': 'Cantidad de reseñas'
}
resultados = []
for columna, nombre in variables.items():
    # Cada relación usa solo los juegos con ambos valores disponibles.
    pares = juegos[[columna, 'media_jugadores_periodo']].dropna()
    # Spearman equivale a correlacionar los rangos, con promedio para los empates.
    rangos = pares.rank()
    correlacion = rangos[columna].corr(rangos['media_jugadores_periodo'])
    resultados.append({'variable': nombre, 'numero_juegos': len(pares),
                       'correlacion_spearman': correlacion})
correlaciones = pd.DataFrame(resultados)

# 4. Comparar el precio registrado sin confundir cero con gratuidad real ni causalidad.
grupos = juegos.groupby('precio_cero_marzo_2025').agg(
    numero_juegos=('id_juego', 'size'),
    media_jugadores=('media_jugadores_periodo', 'mean'),
    mediana_jugadores=('media_jugadores_periodo', 'median'),
    percentil_25=('media_jugadores_periodo', lambda valores: valores.quantile(0.25)),
    percentil_75=('media_jugadores_periodo', lambda valores: valores.quantile(0.75))
).reset_index()
grupos['tipo'] = grupos['precio_cero_marzo_2025'].map({
    True: 'Precio registrado: 0 USD', False: 'Precio registrado superior a 0 USD'
})

assert juegos['id_juego'].is_unique
assert correlaciones['correlacion_spearman'].between(-1, 1).all()
assert grupos['numero_juegos'].sum() == len(juegos)
salida = carpeta / 'resultados'
salida.mkdir(exist_ok=True)
juegos.to_csv(salida / 'base_estadistica_por_juego.csv', index=False, encoding='utf-8-sig')
correlaciones.to_csv(salida / 'correlaciones.csv', index=False, encoding='utf-8-sig')
grupos.to_csv(salida / 'actividad_por_tipo_precio.csv', index=False, encoding='utf-8-sig')
print(correlaciones.to_string(index=False, float_format='%.4f'))
print(grupos.to_string(index=False, float_format='%.2f'))
