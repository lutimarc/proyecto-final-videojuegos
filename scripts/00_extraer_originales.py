from pathlib import Path
import io
import zipfile

# Recuperar los originales comprimidos sin cambiar su contenido.
carpeta = Path(__file__).resolve().parent.parent / 'datos/originales'
catalogo = carpeta / 'games_march2025_full.csv'
if not catalogo.exists():
    partes = sorted(carpeta.glob('catalogo.zip.parte*'))
    if len(partes) != 5:
        raise ValueError('Se necesitan las cinco partes del catálogo.')
    contenido = b''.join(parte.read_bytes() for parte in partes)
    with zipfile.ZipFile(io.BytesIO(contenido)) as archivo:
        archivo.extract('games_march2025_full.csv', carpeta)

if not (carpeta / 'steamcharts.csv').exists():
    with zipfile.ZipFile(carpeta / 'steamcharts.zip') as archivo:
        archivo.extract('steamcharts.csv', carpeta)

print('Los dos CSV originales están disponibles en datos/originales.')
