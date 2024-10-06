import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations (adjust paths if necessary)
from modules.config import raw_data_path_enco, interim_data_path, logs_folder

# Ensure the logs directory exists
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_enco_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
COLUMNAS_COMUNES = ['fol', 'ent', 'con', 'v_sel', 'n_hog', 'h_mud']  # Common columns
VIV_ESPECIFICAS = ['ageb', 'fch_def']
CS_ESPECIFICAS = ['i_per', 'ing']
CB_ESPECIFICAS = [f'p{i}' for i in range(1, 16)]

VIV_COLS = COLUMNAS_COMUNES + VIV_ESPECIFICAS
CS_COLS = COLUMNAS_COMUNES + CS_ESPECIFICAS
CB_COLS = COLUMNAS_COMUNES + CB_ESPECIFICAS

def cargar_datos(mes, tipo):
    """
    Load ENCO data for a given month and type (cs, viv, cb).
    """
    file_name = f'conjunto_de_datos_{tipo}_enco_2022_{str(mes).zfill(2)}.CSV'
    folder_path = os.path.join(raw_data_path_enco, f'conjunto_de_datos_{tipo}_enco_2022_{str(mes).zfill(2)}', 'conjunto_de_datos')
    file_path = os.path.join(folder_path, file_name)
    
    if os.path.exists(file_path):
        logging.info(f"Loading data from {file_path}")
        return pd.read_csv(file_path)
    else:
        logging.error(f"File not found: {file_path}")
        return pd.DataFrame()

def validate_data(df):
    # Validate the ENCO dataset to ensure it is tidy
    if df.isnull().values.any():
        logging.warning("Missing values detected in the dataset.")
    
    if 'ing' in df.columns and (df['ing'] < 0).any():
        logging.error("Negative values detected in 'ing' column.")
        return False
    
    if df.duplicated(subset=COLUMNAS_COMUNES).any():
        logging.error("Duplicate records found based on key columns.")
        return False

    return True

def transform_enco_data(cs_df, viv_df, cb_df):
    try:
        logging.info("Transforming ENCO data...")

        # Merge datasets on common columns
        merged_data = pd.merge(cs_df, viv_df, on=COLUMNAS_COMUNES, how='inner')
        merged_data = pd.merge(merged_data, cb_df, on=COLUMNAS_COMUNES, how='inner')

        # Add derived columns: extract 'ageb' as state and municipality codes
        merged_data['entidad'] = merged_data['ageb'].str[:2]  # Entity code
        merged_data['municipio'] = merged_data['ageb'].str[2:5]  # Municipality code

        logging.info(f"Transformed data shape: {merged_data.shape}")
        return merged_data
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_transformed_data(data, output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved transformed data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving transformed data: {e}")

def create_metadata(output_path, raw_data_path):
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "enco_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for ENCO Data Transformation\n")
        f.write(f"Source: {raw_data_path}\n")
        f.write(f"Transformation date: {datetime.now()}\n")
        f.write(f"Tidy data saved at: {output_path}\n")
        f.write(f"Selected columns: {', '.join(VIV_COLS + CS_COLS + CB_COLS)}\n")
        logging.info(f"Metadata generated at {metadata_file}")

def process_data():
    df_final = pd.DataFrame()
    for i in range(1, 13):
        cs_df = cargar_datos(i, 'cs')
        viv_df = cargar_datos(i, 'viv')
        cb_df = cargar_datos(i, 'cb')

        if cs_df.empty or viv_df.empty or cb_df.empty:
            logging.warning(f"Skipping month {i} due to missing data.")
            continue

        # Select relevant columns
        cs_df = cs_df[CS_COLS]
        viv_df = viv_df[VIV_COLS]
        cb_df = cb_df[CB_COLS]

        # Validate and transform data
        if validate_data(cs_df) and validate_data(viv_df) and validate_data(cb_df):
            transformed_data = transform_enco_data(cs_df, viv_df, cb_df)
            df_final = pd.concat([df_final, transformed_data], ignore_index=True)

    output_file_path = os.path.join(interim_data_path, "enco_interim_tidy.csv")
    save_transformed_data(df_final, output_file_path)
    create_metadata(output_file_path, raw_data_path_enco)

if __name__ == "__main__":
    process_data()
