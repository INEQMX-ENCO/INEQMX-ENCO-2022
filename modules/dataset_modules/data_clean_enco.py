import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup paths and logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)
from modules.config import data_paths, years, LOGS_FOLDER, BASE_PROCESSED_DATA_PATH

processed_enco_path = os.path.join(BASE_PROCESSED_DATA_PATH, "enco")
os.makedirs(LOGS_FOLDER, exist_ok=True)
log_filename = os.path.join(LOGS_FOLDER, f"data_enco_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Define column mappings
columnas_comunes = ['fol', 'ent', 'con', 'v_sel', 'n_hog', 'h_mud']
viv_cols = columnas_comunes + ['mpio', 'ageb', 'fch_def']
cs_cols = columnas_comunes + ['i_per', 'ing']
cb_cols = columnas_comunes + [f'p{i}' for i in range(1, 16)]

# Create output directory for each year
for year in years:
    os.makedirs(os.path.join(data_paths["enco"][year]["interim"], str(year)), exist_ok=True)

# Function to construct file paths dynamically
def construir_ruta(anio, mes, tipo):
    base_folder = data_paths['enco'][anio]['raw']
    mes_str = f'{mes:02d}'
    if anio == 2018:
        if mes <= 6:
            folder_path = os.path.join(base_folder, f"{tipo}_enco0{mes}18", "conjunto_de_datos")
            file_name = f'enco{tipo}_0{mes}18.csv'
        elif mes == 7:
            folder_path = os.path.join(base_folder, f"{tipo}_enco0718", "conjunto_de_datos")
            file_name = f'conjunto_de_datos_enco{tipo}_0718.csv'
        else:
            folder_path = os.path.join(base_folder, f"conjunto_de_datos_{tipo}_enco_2018_{mes_str}", "conjunto_de_datos")
            file_name = f'conjunto_de_datos_{tipo}_enco_2018_{mes_str}.csv'
    else:
        folder_path = os.path.join(base_folder, f"conjunto_de_datos_{tipo}_enco_{anio}_{mes_str}", "conjunto_de_datos")
        file_name = f'conjunto_de_datos_{tipo}_enco_{anio}_{mes_str}.csv'

    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        file_path = file_path.replace('.csv', '.CSV')
        if not os.path.exists(file_path):
            logging.warning(f"File not found for year {anio}, month {mes}, type {tipo}. Tried path: {file_path}")
            return None
    return file_path

# Load data function with validation
def cargar_datos(anio, mes, tipo, columnas_relevantes):
    file_path = construir_ruta(anio, mes, tipo)
    if file_path:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()
        return df.loc[:, [col for col in columnas_relevantes if col in df.columns]]
    return pd.DataFrame()

# Validate and clean data
def validar_datos(df):
    if df.isnull().values.any():
        logging.warning("Null values detected in dataset.")
    for columna, tipo in {'fol': str, 'ent': int, 'con': int, 'v_sel': int, 'n_hog': int, 'h_mud': int, 'ageb': str, 'fch_def': str, 'i_per': float, 'ing': float}.items():
        if columna in df and not df[columna].map(lambda x: isinstance(x, tipo)).all():
            logging.warning(f"Column {columna} has values that don't match type {tipo}.")
    if 'ing' in df and (df['ing'] < 0).any():
        logging.warning("Negative values detected in 'ing'.")
    if 'fch_def' in df.columns:
        try:
            pd.to_datetime(df['fch_def'], format='%d-%m-%Y')
        except ValueError:
            logging.warning("Incorrect date format detected in 'fch_def' column.")    
    return df

# Data quality analysis
def analizar_calidad_datos(df):
    missing_percent = df.isnull().mean() * 100
    logging.info("Percentage of missing values per column:")
    logging.info(missing_percent[missing_percent > 0])
    return df

# Process and filter data across all months and types
def procesar_datos():
    df_all_years = pd.DataFrame()
    
    for anio in years:
        df_final = pd.DataFrame()
        cs_datos = [cargar_datos(anio, mes, 'cs', cs_cols) for mes in range(1, 13)]
        viv_datos = [cargar_datos(anio, mes, 'viv', viv_cols) for mes in range(1, 13)]
        cb_datos = [cargar_datos(anio, mes, 'cb', cb_cols) for mes in range(1, 13)]

        for cs_df, viv_df, cb_df in zip(cs_datos, viv_datos, cb_datos):
            if not cs_df.empty and not viv_df.empty and not cb_df.empty:
                merged_df = pd.merge(pd.merge(cs_df, viv_df, on=columnas_comunes, how='inner'), cb_df, on=columnas_comunes, how='inner')
                merged_df = validar_datos(merged_df)
                df_final = pd.concat([df_final, merged_df], ignore_index=True)
        
        interim_output_path = os.path.join(data_paths["enco"][anio]["interim"], f"enco_interim_{anio}.csv")
        df_final = analizar_calidad_datos(df_final)
        df_final.to_csv(interim_output_path, index=False)
        logging.info(f"Processed data for {anio} saved at {interim_output_path}")

        df_all_years = pd.concat([df_all_years, df_final], ignore_index=True)

    df_all_years['fch_def'] = pd.to_datetime(df_all_years['fch_def'], format='mixed', errors='coerce').dt.strftime('%d/%m/%Y')
    df_all_years['year'] = pd.to_datetime(df_all_years['fch_def'], errors='coerce', format='mixed').dt.year

    processed_output_path = os.path.join(processed_enco_path, "enco_processed_tidy.csv")
    df_all_years.to_csv(processed_output_path, index=False)
    logging.info(f"Combined processed data for all years saved at {processed_output_path}")

    df_grouped = df_all_years.groupby(['ent', 'mpio', 'year']).sum(numeric_only=True).reset_index()
    grouped_output_path = os.path.join(processed_enco_path, "enco_grouped.csv")
    df_grouped.to_csv(grouped_output_path, index=False)
    logging.info(f"Grouped data by state and year saved at {grouped_output_path}")

if __name__ == "__main__":
    procesar_datos()
    print(f"Data processing completed. Logs available at {log_filename}")