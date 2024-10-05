import requests
import zipfile
import os
from io import BytesIO
from tqdm import tqdm
from datetime import datetime

# URL base de los archivos a descargar
base_url_enco = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls_enco = [f"{base_url_enco}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]

url_enigh = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"

# Definir la ruta base para guardar los datos en raw
raw_data_path_enco = os.path.abspath(os.path.join("data", "raw", "enco"))
raw_data_path_enigh = os.path.abspath(os.path.join("data", "raw", "enigh"))
os.makedirs(raw_data_path_enco, exist_ok=True)
os.makedirs(raw_data_path_enigh, exist_ok=True)

# Función para descargar y extraer archivos ZIP
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

# Descargar y extraer todos los archivos
def descargar_datos():
    for url in urls_enco:
        descargar_y_extraer_zip(url, extract_path=raw_data_path_enco)
    descargar_y_extraer_zip(url_enigh, extract_path=raw_data_path_enigh)

# Generar archivo de metadatos con información sobre la descarga
def crear_metadata():
    metadata_file = os.path.abspath(os.path.join("data", "raw", "data_sources_description.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Descripción de las fuentes de datos descargadas:\n\n")
        f.write("Fuente: ENCO 2022\n")
        f.write(f"URLs: {', '.join(urls_enco)}\n")
        f.write(f"Fecha de descarga: {datetime.now()}\n")
        f.write("Descripción: Encuesta Nacional sobre Confianza del Consumidor (ENCO) del año 2022,\n") 
        f.write("con el objetivo de generar información estadística cualitativa, que permita obtener indicadores sobre\n")
        f.write("el grado de satisfacción de la población acerca de su situación económica, la de su familia y la del país;\n")
        f.write("además de su percepción de los cambios sobre el bienestar social y desarrollo,\n")
        f.write("así como de otras variables en el transcurso del tiempo.\n\n")
        
        f.write("Fuente: ENIGH 2022\n")
        f.write(f"URL: {url_enigh}\n")
        f.write(f"Fecha de descarga: {datetime.now()}\n")
        f.write("Descripción: La Encuesta Nacional de Ingresos y Gastos de los Hogares 2022 se llevó a cabo\n") 
        f.write("del 21 de agosto al 28 de noviembre de 2022. Su objetivo es proporcionar un panorama estadístico\n")
        f.write("del comportamiento de los ingresos y gastos de los hogares en cuanto a su monto, procedencia y distribución;\n") 
        f.write("adicionalmente, ofrece información sobre las características ocupacionales y sociodemográficas de los\n") 
        f.write("integrantes del hogar, así como las características de la infraestructura de la vivienda y el equipamiento del hogar.\n\n")
    
    print(f"Metadatos generados en {metadata_file}")

# Ejecutar la descarga y generar metadatos
if __name__ == "__main__":
    descargar_datos()
    crear_metadata()