import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import raw_data_path_ageb, urls_ageb, logs_folder #raw_data_path_enigh, interim_data_path_enigh, logs_folder

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_ageb_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = [
    "ENTIDAD",'MUN','NOM_LOC','AGEB','POBTOT'
]

def load_raw_ageb(file_path):
    """Load raw AGEB data from a directory containing zip files."""
    try:
        df_ageb = pd.DataFrame()
        logging.info(f"Loading raw AGEB data from {file_path}...")
        
        # Iteramos sobre todas las 32 entidades
        for ent in range(1, 33):
            ent_str = str(ent).zfill(2)  # Formato con ceros a la izquierda
            ageb_name = f"RESAGEBURB_{ent_str}CSV20.csv"
            zip_file = f"resageburb_{ent_str}csv20.zip"
            zip_path = os.path.join(file_path, zip_file) # Ruta completa del archivo ZIP
            if os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as z:
                    if ageb_name in z.namelist(): # Buscamos el archivo CSV dentro del ZIP
                        logging.info(f"Extracting and loading {ageb_name} from {zip_file}...")
                        with z.open(ageb_name) as f: # Cargamos el archivo CSV desde el ZIP
                            df = pd.read_csv(f, encoding='latin-1', dtype={6: str})
                            df.columns = ['ENTIDAD' if col == '﻿ENTIDAD' else col for col in df.columns]
                            # Concatenamos al dataframe total
                            df_ageb = pd.concat([df_ageb, df], ignore_index=True)
            else:
                logging.warning(f"{zip_file} not found in {file_path}")
        logging.info(f"Loaded df_ageb shape: {df_ageb.shape}")
        return df_ageb
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def validate_data(data):
    """Validate the AGEB dataset to ensure it is tidy."""
    # 1. Check if required columns are present
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        logging.error(f"Missing columns: {missing_columns}")
        return False

    # 2. Check for missing values in key columns
    if data[REQUIRED_COLUMNS].isnull().any().any():
        logging.warning("Missing values detected in key columns.")
        # Optional: Decide whether to drop or fill missing values
        data = data.dropna(subset=REQUIRED_COLUMNS)

    # 3. Check for negative values in total population
    pop_columns = [col for col in REQUIRED_COLUMNS if "POBTOT" in col]
    if (data[income_columns] < 0).any().any():
        logging.error("Negative population values detected.")
        return False
    return True

def transform_ageb_data(data):
    """Select necessary columns and create tidy dataset."""
    try:
        logging.info("Transforming AGEB data...")

        # Check if all required columns exist in the data
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return None

        # Select necessary columns
        tidy_data_ageb = data[REQUIRED_COLUMNS].copy()  # Use .copy() to avoid SettingWithCopyWarning
        # Rename columns
        tidy_data_ageb.rename(columns={"ENTIDAD":'ent',"MUN": "mun",'NOM_LOC':'nom_loc','AGEB':'ageb','POBTOT':'pob_tot'}, inplace=True)

        # Ensure 'pob_tot' is explicitly converted to a string
        tidy_data_ageb.loc[:, 'pob_tot'] = tidy_data_ageb['pob_tot'].astype(str)

        logging.info(f"Transformed data shape: {tidy_data_ageb.shape}")
        return tidy_data_ageb
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_tidy_data_ageb(data, output_path):
    """Save the transformed tidy data."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_metadata(output_path, raw_data_path):
    """Create metadata for the processed data."""
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "ageb_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for AGEB Data Transformation\n")
        f.write(f"Source: {raw_data_path}\n")
        f.write(f"Transformation date: {datetime.now()}\n")
        f.write(f"Tidy data saved at: {output_path}\n")
        f.write(f"Selected columns: {', '.join(REQUIRED_COLUMNS)}\n")
        logging.info(f"Metadata generated at {metadata_file}")

def generate_summary_statistics(data):
    """Generate summary statistics for validation."""
    try:
        summary_stats = data[["ing_cor", "ingtrab", "factor"]].describe()
        logging.info(f"Summary statistics:\n{summary_stats}")
    except Exception as e:
        logging.error(f"Error generating summary statistics: {e}")

if __name__ == "__main__":
    output_file_path = os.path.join(interim_data_path, "ageb_tidy_data.csv")

    # Load raw data
    raw_data = load_raw_ageb(raw_data_path_ageb)

    if raw_data is not None:
        # Validate data
        if validate_data(raw_data):
            # Transform data
            tidy_data = transform_ageb_data(raw_data)

            if tidy_data is not None:
                # Save tidy data
                save_tidy_data_ageb(tidy_data, output_file_path)

                # Create metadata
                create_metadata(output_file_path, raw_data_path_ageb)

                # Generate summary statistics for validation
                generate_summary_statistics(tidy_data)

    logging.info("AGEB data transformation process completed.")
