from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 1. Leer los resúmenes calculados en los pasos anteriores.
carpeta = Path(__file__).resolve().parent.parent
resultados = carpeta / 'resultados'
salida = carpeta / 'graficos'
salida.mkdir(exist_ok=True)
evolucion = pd.read_csv(resultados / 'evolucion_mensual.csv')
ranking = pd.read_csv(resultados / 'clasificacion_juegos.csv')
generos = pd.read_csv(resultados / 'comparacion_generos.csv')
correlaciones = pd.read_csv(resultados / 'correlaciones.csv')

plt.rcParams.update({'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False})

# Formato español para las cifras de los ejes.
def numero_espanol(valor, posicion):
    return f'{valor:,.0f}'.replace(',', '.')

def guardar(nombre, nota):
    plt.figtext(0.02, 0.02, nota, fontsize=9, color='#444444')
    plt.tight_layout(rect=[0, 0.10, 1, 1])
    plt.savefig(salida / nombre, dpi=160)
    plt.close()

# 2. Evolución de los mismos 2.778 videojuegos durante los 21 meses.
plt.figure(figsize=(11, 6))
etiquetas = pd.to_datetime(evolucion['mes']).dt.strftime('%m/%Y')
plt.plot(etiquetas, evolucion['suma_jugadores_medios'] / 1000000,
         marker='o', color='#2878A0')
plt.title('Evolución de la actividad en la muestra de videojuegos')
plt.ylabel('Suma de jugadores simultáneos medios (millones)')
plt.xticks(rotation=60)
plt.ylim(bottom=0)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda valor, pos: f'{valor:.1f}'.replace('.', ',')))
plt.grid(axis='y', alpha=0.2)
guardar('01_evolucion_mensual.png',
        '2.778 juegos con datos completos. Enero de 2024–septiembre de 2025.\n'
        'La suma no representa personas únicas ni todo Steam. Fuente: SteamCharts y catálogo de Steam vía Kaggle.')

# 3. Los diez videojuegos con mayor media del periodo completo.
top = ranking.head(10).sort_values('jugadores_medios')
plt.figure(figsize=(11, 7))
plt.barh(top['juego'], top['jugadores_medios'], color='#2878A0')
plt.title('Diez videojuegos más jugados de la muestra completa')
plt.xlabel('Media de jugadores simultáneos durante los 21 meses')
plt.gca().xaxis.set_major_formatter(FuncFormatter(numero_espanol))
plt.grid(axis='x', alpha=0.2)
guardar('02_juegos_mas_jugados.png',
        'Ranking entre 2.778 juegos con datos completos, no de todo Steam.\n'
        'Enero de 2024–septiembre de 2025. Fuente: SteamCharts y catálogo de Steam vía Kaggle.')

# 4. La mediana permite comparar los géneros sin que dominen unos pocos éxitos.
generos = generos.sort_values('mediana_jugadores')
etiquetas = generos['genero'] + ' (' + generos['numero_juegos'].astype(str) + ' juegos)'
plt.figure(figsize=(11, 7))
plt.barh(etiquetas, generos['mediana_jugadores'], color='#36836B')
plt.title('Actividad habitual de los videojuegos por género')
plt.xlabel('Mediana de las medias de jugadores de cada juego')
plt.gca().xaxis.set_major_formatter(FuncFormatter(numero_espanol))
plt.grid(axis='x', alpha=0.2)
guardar('03_comparacion_generos.png',
        'Un juego puede pertenecer a varios géneros; los grupos no se suman. Periodo: enero de 2024–septiembre de 2025.\n'
        '2.748 juegos con géneros comparables y datos completos. Fuente: SteamCharts y catálogo de Steam vía Kaggle.')

# 5. Relación del precio y las reseñas con la actividad.
plt.figure(figsize=(11, 6))
barras = plt.barh(correlaciones['variable'], correlaciones['correlacion_spearman'], color='#2878A0')
plt.bar_label(barras, labels=[f'{valor:.2f}'.replace('.', ',')
                            for valor in correlaciones['correlacion_spearman']], padding=5)
plt.title('Relaciones con la media de jugadores por videojuego')
plt.xlabel('Correlación de Spearman (de −1 a 1)')
plt.xlim(-1, 1)
plt.axvline(0, color='#555555', linewidth=0.8)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda valor, pos: f'{valor:.1f}'.replace('.', ',')))
guardar('04_correlaciones.png',
        '2.778 juegos; valoración disponible en 2.769. Relación no significa causa. Catálogo: marzo de 2025.\n'
        'Actividad: enero de 2024–septiembre de 2025. Fuente: SteamCharts y catálogo de Steam vía Kaggle.')
print('Cuatro gráficos guardados en la carpeta graficos.')
