from pathlib import Path
import pandas as pd

# 1. Leer los datos preparados.
carpeta = Path(__file__).resolve().parent.parent
datos = pd.read_csv(carpeta / 'datos/limpios/videojuegos_2024_2025.csv')
datos['mes'] = pd.to_datetime(datos['mes'])
salida = carpeta / 'resultados'
salida.mkdir(exist_ok=True)

# 2. Describir los jugadores. Cada observación es un juego en un mes.
columnas = ['jugadores_medios', 'jugadores_maximos']
resumen_jugadores = datos[columnas].describe().T
resumen_jugadores.columns = ['cantidad', 'media', 'desviacion_tipica',
                             'minimo', 'percentil_25', 'mediana',
                             'percentil_75', 'maximo']
resumen_jugadores.to_csv(salida / 'resumen_jugadores.csv', encoding='utf-8-sig')

# 3. Describir el precio y las reseñas contando cada juego una sola vez.
juegos = datos.drop_duplicates('id_juego')
columnas = ['precio_usd_marzo_2025', 'total_resenas_marzo_2025',
            'proporcion_resenas_positivas_marzo_2025']
resumen_catalogo = juegos[columnas].describe().T
resumen_catalogo.columns = resumen_jugadores.columns
resumen_catalogo.to_csv(salida / 'resumen_catalogo.csv', encoding='utf-8-sig')

# 4. Comparar los mismos juegos en los 21 meses.
completos = datos[datos['periodo_completo']].copy()
evolucion = completos.groupby('mes').agg(
    numero_juegos=('id_juego', 'nunique'),
    suma_jugadores_medios=('jugadores_medios', 'sum'),
    media_por_juego=('jugadores_medios', 'mean'),
    mediana_por_juego=('jugadores_medios', 'median')
).reset_index()
evolucion['cambio_porcentaje'] = evolucion['suma_jugadores_medios'].pct_change() * 100
evolucion.to_csv(salida / 'evolucion_mensual.csv', index=False, encoding='utf-8-sig')

# 5. Ordenar los juegos por su media durante el mismo periodo.
clasificacion = completos.groupby(['id_juego', 'juego']).agg(
    jugadores_medios=('jugadores_medios', 'mean'),
    mayor_pico_mensual=('jugadores_maximos', 'max'),
    meses=('mes', 'nunique')
).reset_index().sort_values('jugadores_medios', ascending=False)
clasificacion.to_csv(salida / 'clasificacion_juegos.csv', index=False, encoding='utf-8-sig')

# 6. Comparar juegos gratuitos y de pago según el precio de marzo de 2025.
precios = juegos.groupby('es_gratis_marzo_2025').agg(
    numero_juegos=('id_juego', 'nunique'),
    precio_medio_usd=('precio_usd_marzo_2025', 'mean'),
    precio_mediano_usd=('precio_usd_marzo_2025', 'median')
).reset_index()
precios['tipo'] = precios['es_gratis_marzo_2025'].map({True: 'Gratis', False: 'De pago'})
precios.to_csv(salida / 'tipos_precio.csv', index=False, encoding='utf-8-sig')

# Comprobar que todas las comparaciones mensuales tienen la misma cobertura.
assert evolucion['numero_juegos'].eq(completos['id_juego'].nunique()).all()
assert len(evolucion) == 21
assert clasificacion['meses'].eq(21).all()
assert precios['numero_juegos'].sum() == juegos['id_juego'].nunique()

print('Resumen de jugadores por juego y mes:')
print(resumen_jugadores.round(2).to_string())
print('\nResumen del catálogo, un registro por juego:')
print(resumen_catalogo.round(2).to_string())
print('\nCinco juegos con mayor media en el periodo completo:')
print(clasificacion.head(5).round(2).to_string(index=False))
print('\nEvolución mensual:')
print(evolucion.to_string(index=False, float_format='%.2f'))
print('\nTipos de precio:')
print(precios.to_string(index=False))
