import requests
import zipfile
import os
import shutil
from io import BytesIO
from tqdm import tqdm

# URL base de los archivos a descargar
base_url_enco = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls = [f"{base_url_enco}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]

url_enigh = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"

# Definir la ruta base para guardar los datos en raw
raw_data_path_enco = os.path.join("..", "data", "raw", "enco")
raw_data_path_enigh = os.path.join("..", "data", "raw", "enigh")

# Función para borrar y recrear la carpeta
def reset_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)  # Eliminar la carpeta y todo su contenido
    os.makedirs(directory, exist_ok=True)  # Volver a crear la carpeta

# Función para descargar y extraer archivos ZIP en la carpeta data/raw
def descargar_y_extraer_zip(url, extract_path):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            t = tqdm(total=total_size, unit='iB', unit_scale=True)
            buffer = BytesIO()
            for data in r.iter_content(block_size):
                t.update(len(data))
                buffer.write(data)
            t.close()

            with zipfile.ZipFile(buffer) as z:
                z.extractall(extract_path)
                print(f"Archivos extraídos de {url} en {extract_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {url}: {e}")

# Descargar y extraer todos los archivos en data/raw
def descargar_datos():
    # Borrar y recrear las carpetas para asegurar que están vacías
    reset_directory(raw_data_path_enco)
    reset_directory(raw_data_path_enigh)
    
    # Descargar y extraer archivos
    for url in urls:
        descargar_y_extraer_zip(url, extract_path=raw_data_path_enco)
    descargar_y_extraer_zip(url_enigh, extract_path=raw_data_path_enigh)

if __name__ == "__main__":
    descargar_datos()

