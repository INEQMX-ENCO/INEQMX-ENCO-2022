import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import data_paths, years, LOGS_FOLDER, BASE_PROCESSED_DATA_PATH
processed_enco_path = os.path.join(BASE_PROCESSED_DATA_PATH, "enco")
# Ensure interim data path and logs directory exist
#for year in [2018, 2020, 2022]:
#    interim_data_path_enco = data_paths["enco"][year]["interim"]
#os.makedirs(interim_data_path_enco, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(LOGS_FOLDER, f"data_enco_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Define column selections
columnas_comunes = ['fol', 'ent', 'con', 'v_sel', 'n_hog', 'h_mud']
viv_especificas = ['mpio', 'ageb', 'fch_def']
cs_especificas = ['i_per', 'ing']
cb_especificas = [f'p{i}' for i in range(1, 16)]

viv_cols = columnas_comunes + viv_especificas
cs_cols = columnas_comunes + cs_especificas
cb_cols = columnas_comunes + cb_especificas
valores_perdidos = [9999, 99999, 999999]

# Create output directory for each year
for year in years.keys():
    interim_data_path_year = os.path.join(data_paths["enco"][year]["interim"], str(year))
    os.makedirs(interim_data_path_year, exist_ok=True)

# Function to select relevant columns after normalizing them
def seleccionar_columnas(df, columnas_relevantes):
    if not df.empty:
        df.columns = df.columns.str.lower()
        columnas_existentes = [col for col in columnas_relevantes if col in df.columns]
        return df[columnas_existentes]
    return pd.DataFrame()

# Function to construct file path and name based on year, month, and dataset type
def construir_ruta(anio, mes, tipo):
    base_folder = data_paths['enco'][anio]['raw']
    mes_str = str(mes).zfill(2)  # Zero-pad the month
    
    # 2018 file paths
    if anio == 2018:
        if mes <= 6:
            file_name = f'enco{tipo}_0{mes}18.csv'
            folder_path = os.path.join(base_folder, f"{tipo}_enco0{mes}18", "conjunto_de_datos")
        elif mes == 7:
            file_name = f'conjunto_de_datos_enco{tipo}_0718.csv'
            folder_path = os.path.join(base_folder, f"{tipo}_enco0718", "conjunto_de_datos")
        else:
            file_name = f'conjunto_de_datos_{tipo}_enco_2018_{mes_str}.csv'
            folder_path = os.path.join(base_folder, f"conjunto_de_datos_{tipo}_enco_2018_{mes_str}", "conjunto_de_datos")
    else:
        file_name = f'conjunto_de_datos_{tipo}_enco_{anio}_{mes_str}.csv'
        folder_path = os.path.join(base_folder, f"conjunto_de_datos_{tipo}_enco_{anio}_{mes_str}", "conjunto_de_datos")

    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        # Intenta con la extensión alternativa en mayúsculas
        file_name = file_name.replace('.csv', '.CSV')
        file_path = os.path.join(folder_path, file_name)
    
    if not os.path.exists(file_path):
        logging.warning(f"File not found for year {anio}, month {mes}, type {tipo}. Tried path: {file_path}")
        return None

    return file_path


# Load data function
def cargar_datos(anio, mes, tipo):
    file_path = construir_ruta(anio, mes, tipo)
    return pd.read_csv(file_path) if file_path else pd.DataFrame()

# Data validation function
def validar_datos(df):
    # 1. Check for null values
    if df.isnull().values.any():
        logging.warning("Null values detected in the dataset.")

    # Expected data types
    tipos_esperados = {
        'fol': str, 'ent': int, 'con': int, 'v_sel': int, 'n_hog': int, 'h_mud': int,
        'ageb': str, 'fch_def': str, 'i_per': float, 'ing': float
    }
    
    # 2. Validate data types for each expected column
    for columna, tipo in tipos_esperados.items():
        if columna in df.columns:
            if not df[columna].map(lambda x: isinstance(x, tipo)).all():
                logging.warning(f"Column {columna} contains values that do not match the expected type {tipo}.")
        else:
            logging.warning(f"Column {columna} is missing from the DataFrame.")

    # 3. Check for duplicate records in primary key columns
    if df.duplicated(subset=columnas_comunes).any():
        logging.warning("Duplicate records detected in primary key columns.")

    # 4. Check for negative values in 'ing' if the column exists
    if 'ing' in df.columns and (df['ing'] < 0).any():
        logging.warning("Negative values detected in 'ing' column.")

    # 5. Validate date format in 'fch_def' if the column exists
    if 'fch_def' in df.columns:
        try:
            pd.to_datetime(df['fch_def'], format='%Y-%m-%d')
        except ValueError:
            logging.warning("Incorrect date format detected in 'fch_def' column.")

# Metadata creation function
def create_metadata(output_path):
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "enco_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for ENCO Data Transformation\n")
        f.write(f"Transformation date: {datetime.now()}\n")
        f.write(f"Data saved at: {output_path}\n")
        f.write(f"Selected columns: {', '.join(viv_cols + cs_cols + cb_cols)}\n")
        logging.info(f"Metadata generated at {metadata_file}")

# Data cleaning and processing
def reemplazar_valores_perdidos(df, valores):
    return df.replace(valores, np.nan)

def analizar_calidad_datos(df):
    df_limpio = reemplazar_valores_perdidos(df, valores_perdidos)
    porcentaje_perdidos = df_limpio.isnull().mean() * 100
    logging.info("Percentage of missing values per column:")
    logging.info(porcentaje_perdidos[porcentaje_perdidos > 0])
    return df_limpio

# Process and filter DataFrames
def procesar_datos():
    df_all_years = pd.DataFrame()  # To store combined data across all years
    
    for anio in years.keys():
        df_final = pd.DataFrame()  # To store data for each year
        cs_enco_filtrado = [seleccionar_columnas(cargar_datos(anio, i, 'cs'), cs_cols) for i in range(1, 13)]
        viv_enco_filtrado = [seleccionar_columnas(cargar_datos(anio, i, 'viv'), viv_cols) for i in range(1, 13)]
        cb_enco_filtrado = [seleccionar_columnas(cargar_datos(anio, i, 'cb'), cb_cols) for i in range(1, 13)]

        for cs_df, viv_df, cb_df in zip(cs_enco_filtrado, viv_enco_filtrado, cb_enco_filtrado):
            if not cs_df.empty and not viv_df.empty and not cb_df.empty:
                temp = pd.merge(cs_df, viv_df, on=columnas_comunes, how='inner')
                temp = pd.merge(temp, cb_df, on=columnas_comunes, how='inner')
                df_final = pd.concat([df_final, temp], ignore_index=True)

        validar_datos(df_final)
        df_final_limpio = analizar_calidad_datos(df_final)

        # Save cleaned data for each year
        interim_output_path = os.path.join(data_paths["enco"][anio]["interim"], f"enco_interim_{anio}.csv")
        df_final_limpio.to_csv(interim_output_path, index=False)
        logging.info(f"Processed data for {anio} saved at {interim_output_path}")

        # Append to all years DataFrame
        df_all_years = pd.concat([df_all_years, df_final_limpio], ignore_index=True)

    # Save combined data for all years
    processed_enco_folder = os.path.join(project_root, "data", "processed", "enco")
    os.makedirs(processed_enco_folder, exist_ok=True)
    combined_output_path = os.path.join(processed_enco_folder, "enco_interim_tidy.csv")
    df_all_years.to_csv(combined_output_path, index=False)
    logging.info(f"Combined processed data for all years saved at {combined_output_path}")

    # Generate metadata for combined file
    create_metadata(combined_output_path)

if __name__ == "__main__":
    procesar_datos()
    print(f"Data processing completed. Logs available at {log_filename}")
