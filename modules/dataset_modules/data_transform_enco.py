import os
import sys
import pandas as pd
from datetime import datetime
import logging

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import logs_folder, interim_data_path_enco

# Rutas de los archivos raw
raw_data_path_enco = os.path.abspath(os.path.join("data", "raw", "enco"))
interim_data_path = interim_data_path_enco
os.makedirs(interim_data_path, exist_ok=True)

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_enco_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Definir las columnas a seleccionar
columnas_comunes = ['fol', 'ent', 'con', 'v_sel', 'n_hog', 'h_mud'] # Columnas comunes en cb,cs, viv y los datos de ENIGH
viv_especificas = ['mpio', 'ageb', 'fch_def']
cs_especificas = ['i_per', 'ing'] 
cb_especificas = [f'p{i}' for i in range(1, 16)]  # Extraemos las preguntas del cuestionario básico

viv_cols = columnas_comunes + viv_especificas
cs_cols = columnas_comunes + cs_especificas
cb_cols = columnas_comunes + cb_especificas

# Función para seleccionar columnas relevantes
def seleccionar_columnas(df, columnas_relevantes):
    return df[columnas_relevantes]

# Función para cargar datos
def cargar_datos(mes, tipo):
    file_name = f'conjunto_de_datos_{tipo}_enco_2022_{str(mes).zfill(2)}.CSV'
    folder_path = f'{raw_data_path_enco}/conjunto_de_datos_{tipo}_enco_2022_{str(mes).zfill(2)}/conjunto_de_datos'
    file_path = os.path.join(folder_path, file_name)
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"Archivo no encontrado: {file_name}")
        return pd.DataFrame()
    
# Aseguramiento de la calidad - validaciones de los datos
def validar_datos(df):
    # 1. Comprobar si hay valores nulos
    if df.isnull().values.any():
        print("Advertencia: Existen valores nulos en el conjunto de datos.")
    
    # 2. Validar que los tipos de datos sean correctos
    tipos_esperados = {
        'fol': str, 'ent': int, 'con': int, 'v_sel': int, 'n_hog': int, 'h_mud': int,
        'ageb': str, 'fch_def': str, 'i_per': float, 'ing': float
    }
    
    for columna, tipo in tipos_esperados.items():
        if columna in df.columns:
            if not df[columna].map(lambda x: isinstance(x, tipo)).all():
                print(f"Advertencia: La columna {columna} tiene valores que no corresponden al tipo {tipo}.")
    
    # 3. Validar que no existan duplicados en las claves primarias (ejemplo: combinación de 'fol', 'ent', etc.)
    if df.duplicated(subset=columnas_comunes).any():
        print("Advertencia: Existen registros duplicados en las columnas de clave primaria.")
    
    # 4. Validar rangos o valores esperados en las columnas (por ejemplo, que el ingreso no sea negativo)
    if (df['ing'] < 0).any():
        print("Advertencia: Existen valores negativos en la columna 'ing'.")

    # 5. Validar que la fecha tiene un formato correcto
    try:
        pd.to_datetime(df['fch_def'], format='%Y-%m-%d')
    except ValueError:
        print("Advertencia: Existen fechas mal formateadas en la columna 'fch_def'.")    

def create_metadata(output_path, raw_data_path, columnas_relevantes):
    """Create metadata for the processed data."""
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "enco_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for ENIGH Data Transformation\n")
        f.write(f"Source: {raw_data_path}\n")
        f.write(f"Transformation date: {datetime.now()}\n")
        f.write(f"Tidy data saved at: {output_path}\n")
        f.write(f"Selected columns: {', '.join(columnas_relevantes)}\n")
        logging.info(f"Metadata generated at {metadata_file}")

# Procesar y filtrar los DataFrames
def procesar_datos():
    df_final = pd.DataFrame()
    for i in range(1, 13):
        cs_df = seleccionar_columnas(cargar_datos(i, 'cs'), cs_cols)
        viv_df = seleccionar_columnas(cargar_datos(i, 'viv'), viv_cols)
        cb_df = seleccionar_columnas(cargar_datos(i, 'cb'), cb_cols)
        
        if not cs_df.empty and not viv_df.empty and not cb_df.empty:
            temp = pd.merge(cs_df, viv_df, on=columnas_comunes, how='inner')
            temp = pd.merge(temp, cb_df, on=columnas_comunes, how='inner')
            df_final = pd.concat([df_final, temp], ignore_index=True)
    
    # Aseguramiento de la calidad de los datos: Validar el DataFrame final
    validar_datos(df_final)
    output_file_path = os.path.join(interim_data_path_enco, "enigh_tidy_data.csv")
    create_metadata(os.path.join(output_file_path, 'enco_interim_tidy.csv'), raw_data_path_enco, viv_cols + cs_cols + cb_cols)
    # Guardar el DataFrame tidy procesado
    df_final.to_csv(os.path.join(interim_data_path, 'enco_interim_tidy.csv'), index=False)
    print(f"Datos procesados y guardados en {interim_data_path}/enco_interim_tidy.csv")

if __name__ == "__main__":
    procesar_datos()