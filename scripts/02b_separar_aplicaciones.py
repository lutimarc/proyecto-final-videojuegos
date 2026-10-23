from pathlib import Path
import pandas as pd

# Separación basada en los géneros del catálogo, no en el número de jugadores.
carpeta = Path(__file__).resolve().parent.parent
salida = carpeta / 'datos/limpios'
datos = pd.read_csv(salida / 'juegos_jugadores_2024_2025.csv')
generos_aplicacion = [
    'Utilities', 'Design & Illustration', 'Animation & Modeling',
    'Video Production', 'Audio Production', 'Photo Editing',
    'Web Publishing', 'Game Development', 'Software Training', 'Accounting'
]

def clasificar(generos):
    lista = generos.split(', ')
    if any(genero in lista for genero in generos_aplicacion):
        return 'Aplicación'
    if generos == 'Sin información' or 'Movie' in lista or 'Education' in lista:
        return 'Por revisar'
    return 'Videojuego'

datos['tipo_producto'] = datos['generos'].apply(clasificar)
# Neos VR mezcla creación y experiencias sociales: no decidir solo por sus géneros.
datos.loc[datos['id_juego'] == 740250, 'tipo_producto'] = 'Por revisar'
# La ficha oficial identifica este producto como servidor de pruebas.
# Fuente: https://store.steampowered.com/app/439700/
datos.loc[datos['id_juego'] == 439700, 'tipo_producto'] = 'Servidor de pruebas'

videojuegos = datos[datos['tipo_producto'] == 'Videojuego'].copy()
aplicaciones = datos[datos['tipo_producto'] == 'Aplicación'].copy()
pendientes = datos[datos['tipo_producto'] == 'Por revisar'].copy()
pruebas = datos[datos['tipo_producto'] == 'Servidor de pruebas'].copy()

assert len(videojuegos) + len(aplicaciones) + len(pendientes) + len(pruebas) == len(datos)
assert not videojuegos['id_juego'].eq(439700).any()
assert len(videojuegos) >= 50000
assert not videojuegos.duplicated(['id_juego', 'mes']).any()

videojuegos.to_csv(salida / 'videojuegos_2024_2025.csv', index=False, encoding='utf-8-sig')
aplicaciones.to_csv(salida / 'aplicaciones_2024_2025.csv', index=False, encoding='utf-8-sig')
pendientes.to_csv(salida / 'productos_por_revisar.csv', index=False, encoding='utf-8-sig')
pruebas.to_csv(salida / 'servidores_de_pruebas.csv', index=False, encoding='utf-8-sig')

# Una lista por producto permite revisar y explicar la clasificación.
lista_productos = datos.drop_duplicates('id_juego')[['id_juego', 'juego', 'generos', 'tipo_producto']]
lista_productos.to_csv(salida / 'clasificacion_productos.csv', index=False, encoding='utf-8-sig')
print(datos.groupby('tipo_producto').agg(filas=('id_juego', 'size'), productos=('id_juego', 'nunique')).to_string())
print('Filas de videojuegos con periodo completo:', videojuegos['periodo_completo'].sum())
