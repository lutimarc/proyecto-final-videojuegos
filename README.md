# Análisis de videojuegos en Steam

Proyecto de análisis exploratorio y dashboard en Excel sobre la actividad de videojuegos entre enero de 2024 y septiembre de 2025.

## Objetivo

Comparar los videojuegos más jugados, la evolución mensual y las diferencias entre géneros. También se estudia la relación de la actividad con el precio y las reseñas.

## Datos y fuentes

| Conjunto | Autor en Kaggle | Archivo original |
|---|---|---|
| [Steam Games Dataset 2025](https://www.kaggle.com/datasets/artermiloff/steam-games-dataset) | artermiloff | `datos/originales/games_march2025_full.csv` |
| [Steam Monthly Average Players](https://www.kaggle.com/datasets/lunthu/steam-monthly-average-players) | lunthu | `datos/originales/steamcharts.csv` |

El primero contiene el catálogo de marzo de 2025, recopilado de Steam y Steam Spy. El segundo contiene el historial mensual de jugadores, obtenido de SteamCharts. Kaggle es la plataforma donde se publican ambas recopilaciones. Los enlaces y las fechas de consulta están en [FUENTES.txt](FUENTES.txt).

Los originales se incluyen comprimidos, sin cambiar sus datos: `catalogo.zip.parte01` a `catalogo.zip.parte06` y `steamcharts.zip`, dentro de `datos/originales/`. El script `00_extraer_originales.py` reconstruye los dos CSV. Las seis partes deben descargarse juntas; no se abren por separado. Cada parte ocupa como máximo 20.000.000 bytes para facilitar su subida web.

Se unen mediante `appid` y `steam_appid`. Cada fila representa un videojuego en un mes, no una persona.

El conjunto final, `datos/limpios/videojuegos_2024_2025.csv`, contiene "70.532 filas, 30 columnas y 4.086 videojuegos". Para comparar meses se emplean los "2.778 videojuegos con los 21 meses completos", que suman 58.338 filas.

## Organización

```text
datos/originales/   Archivos sin transformar
datos/limpios/      Datos preparados y revisiones
scripts/           Preparación, análisis y gráficos en Python
resultados/        Tablas del análisis e informe final
graficos/          Cuatro gráficos en PNG
dashboard/         Dashboard de Excel
requirements.txt   Bibliotecas de Python
```

## Pasos realizados

1. Lectura de los originales y selección del periodo.
2. Conversión de fechas y números, limpieza de textos y unión por identificador.
3. Comprobación de duplicados, valores ausentes y cifras incoherentes.
4. Separación de aplicaciones, un servidor de pruebas y productos pendientes de clasificación.
5. Análisis de medias, medianas, precios, géneros y evolución mensual.
6. Correlaciones de Spearman, contando cada juego una sola vez.
7. Creación de gráficos y dashboard con filtros de año y mes.

Las decisiones de limpieza se aplican sin modificar los originales:

| Revisión | Decisión y motivo |
|---|---|
| Textos vacíos | Indicar «Sin información», sin atribuir un género o una empresa inventados. |
| Reseñas contradictorias | Marcar 15 juegos (242 registros) con cero reseñas positivas y negativas, pero con otro recuento de reseñas del catálogo, `num_reviews_total`, mayor que cero. Sus recuentos y proporción se dejan vacíos porque los datos se contradicen. |
| Cambios de jugadores ausentes | Mantener vacíos los 15 registros sin cambio y su porcentaje; una ausencia no es un cambio de cero. |
| Fechas dudosas | Señalar los 25 títulos con actividad anterior a su lanzamiento registrado. Conservar la fecha y no usarla para calcular antigüedad. |
| Valores extremos | Mantener la actividad elevada observada y comparar media y mediana para que los grandes títulos no oculten el comportamiento habitual. |
| Precio cero | Describirlo como «Precio registrado: 0 USD», sin afirmar que el juego sea gratuito. |

El cambio de jugadores se refiere a la observación anterior disponible en la fuente, que puede no ser el mes anterior. No se utiliza para las conclusiones. Las revisiones de [reseñas](datos/limpios/revision_resenas.csv), [fechas](datos/limpios/revision_fechas.csv) y [clasificación de productos](datos/limpios/clasificacion_productos.csv) quedan guardadas.

## Cómo ejecutar el análisis

Análisis comprobado con Python 3.12, pandas 3.0.6 y matplotlib 3.11.2. Abrir la carpeta en Visual Studio Code y ejecutar en la terminal:

```bash
python -m pip install -r requirements.txt
python scripts/00_extraer_originales.py
python scripts/01_preparar_datos.py
python scripts/02_revisar_datos.py
python scripts/02b_separar_aplicaciones.py
python scripts/03_analisis_descriptivo.py
python scripts/04_comparar_generos.py
python scripts/05_analisis_estadistico.py
python scripts/06_crear_graficos.py
```

Los scripts guardan de nuevo los resultados calculados y conservan los originales. El dashboard se entrega preparado para este conjunto de datos. Recalcular los CSV no actualiza automáticamente los resúmenes del libro.

## Dashboard

Abrir [Dashboard_videojuegos.xlsx](dashboard/Dashboard_videojuegos.xlsx) y cambiar las celdas amarillas de año y mes. Los indicadores y el top 10 cambian con ambos filtros; el gráfico cambia con el año.

La hoja «Datos mensuales» contiene los resúmenes que alimentan las fórmulas. El libro funciona sin ejecutar Python. En 2025 solo hay datos hasta septiembre; `#N/A` en la tabla del gráfico representa meses sin información, no cero jugadores.

## Informe del análisis

En los 70.532 registros mensuales, la media de jugadores simultáneos medios es **985,05** y la mediana 15,42. La diferencia muestra que unos pocos títulos concentran mucha actividad. El precio medio por videojuego es 13,11 dólares, con una mediana de 9,99 dólares.

Entre los juegos con el periodo completo, "Counter-Strike 2, PUBG y Rust" encabezan el ranking. En esa misma muestra, enero de 2025 presenta la mayor suma de jugadores medios y febrero de 2024 la menor.

Multijugador masivo tiene la mayor mediana de actividad entre los géneros comparados, mientras que "Acción" reúne más videojuegos. Un juego puede pertenecer a varios géneros; sus resultados no deben sumarse.

Las correlaciones con la actividad son "0,16 para el precio", "0,17 para la proporción de reseñas positivas" y "0,74 para la cantidad de reseñas". Se usan 2.778 juegos para el precio y 2.769 para las reseñas, excluyendo nueve casos contradictorios. Los juegos con más reseñas tienden a tener más jugadores, pero estos resultados no demuestran causalidad.

El [informe final](resultados/informe_final.txt) amplía los resultados y explica el método. Los cuatro gráficos muestran la [evolución mensual](graficos/01_evolucion_mensual.png), el [ranking de juegos](graficos/02_juegos_mas_jugados.png), la [comparación de géneros](graficos/03_comparacion_generos.png) y las [correlaciones](graficos/04_correlaciones.png).

## Limitaciones

- La muestra incluye coincidencias de las dos fuentes; no representa todo Steam. La selección de periodo completo excluye juegos nuevos o con meses ausentes.
- Los precios y reseñas son de marzo de 2025, no valores históricos de cada mes.
- SteamCharts no cubre todos los juegos; su recopilador indica omisiones por poca audiencia y por el método de extracción.
- La separación de aplicaciones depende de los géneros del catálogo. Once productos ambiguos quedan aparte.
- Se detectaron 25 títulos con actividad anterior a la fecha indicada en el catálogo. No se ha confirmado individualmente la causa de todos ellos.
- Se estudian asociaciones, sin pruebas de hipótesis ni afirmaciones de significación estadística. No se pueden deducir ventas, rentabilidad o causas.
