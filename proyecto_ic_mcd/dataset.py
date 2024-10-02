import requests
import zipfile
import os
from io import BytesIO

# URL base de los archivos a descargar
base_url = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls = [f"{base_url}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]

# Definir la ruta base para guardar los datos en raw
raw_data_path = os.path.join("..", "data", "raw")
os.makedirs(raw_data_path, exist_ok=True)

# Función para descargar y extraer archivos ZIP en la carpeta data/raw
def descargar_y_extraer_zip(url, extract_path=raw_data_path):
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(extract_path)
            print(f"Archivos extraídos de {url} en {extract_path}")
    else:
        print(f"Error al descargar {url}")

# Descargar y extraer todos los archivos en data/raw
def descargar_datos():
    for url in urls:
        descargar_y_extraer_zip(url)

if __name__ == "__main__":
    descargar_datos()
