import os
import sys
import pandas as pd
import logging
import geopandas as gpd
from datetime import datetime
from shapely.geometry import Polygon, MultiPolygon

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import raw_data_path_shp, interim_data_path_shp, logs_folder

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_shp_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

def load_raw_shp(file_path):
    """Load raw SHP data from a directory containing multiple SHP files."""
    try:
        logging.info(f"Loading raw SHP data from {file_path}...")

        # Get all SHP files in the directory
        shp_files = [f for f in os.listdir(file_path) if f.endswith('.shp')]

        if not shp_files:
            logging.warning(f"No SHP files found in {file_path}")
            return None, None

        shp_ent, shp_mun = None, None

        # Iterate over each SHP file and load it
        for shp_file in shp_files:
            file_path_full = os.path.join(file_path, shp_file)
            logging.info(f"Loading {shp_file}...")

            # Load SHP into DataFrame
            try:
                if shp_file.endswith('ENT.shp'):
                    shp_ent = gpd.read_file(file_path_full)
                    logging.info(f"Loaded {shp_file} successfully, shape: {shp_ent.shape}")
                else:
                    shp_mun = gpd.read_file(file_path_full)
                    logging.info(f"Loaded {shp_file} successfully, shape: {shp_mun.shape}")
            except Exception as e:
                logging.error(f"Error loading {shp_file}: {e}")
        
        return shp_ent, shp_mun
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None, None

def transform_shp_data(data):
    """Select necessary columns and create tidy dataset."""
    try:
        logging.info("Transforming SHP data...")
        if data.shape[1] == 5:
            REQUIRED_COLUMNS = ['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'NOMGEO', 'geometry']
        else:
            REQUIRED_COLUMNS = ['CVEGEO', 'CVE_ENT', 'NOMGEO', 'geometry']

        # Check if all required columns exist in the data
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return None

        # Select necessary columns
        tidy_data_shp = data[REQUIRED_COLUMNS].copy()  # Use .copy() to avoid SettingWithCopyWarning

        # Rename columns
        tidy_data_shp.rename(columns={"CVEGEO": 'cvegeo', "CVE_ENT": "cve_ent", 'NOMGEO': 'nom_geo', 'geometry': 'geo'}, inplace=True)
        if 'CVE_MUN' in tidy_data_shp.columns:
            tidy_data_shp.rename(columns={"CVE_MUN": "cve_mun"}, inplace=True)

        logging.info(f"Transformed data shape: {tidy_data_shp.shape}")
        return tidy_data_shp
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def validate_data(data):
    """Validate the SHP dataset to ensure it is tidy."""
    try:
        logging.info("Validating SHP data...")

        if data.shape[1] == 5:
            cond_cvegeo = (data['CVEGEO'].apply(lambda x: isinstance(x, str)) &
                           (data['CVEGEO'] == data['CVE_ENT'] + data['CVE_MUN']))
        else:
            cond_cvegeo = (data['CVEGEO'].apply(lambda x: isinstance(x, str)) &
                           (data['CVEGEO'] == data['CVE_ENT']))

        # Condición ent: debe ser str y su conversión a entero debe estar entre 1 y 32
        cond_ent = (data['CVE_ENT'].apply(lambda x: isinstance(x, str)) &
                    data['CVE_ENT'].apply(lambda x: x.isdigit() and 1 <= int(x) <= 32))

        # Condición nom_geo: columna nom_geo debe ser str
        cond_nom_geo = data['NOMGEO'].apply(lambda x: isinstance(x, str))

        # Condición geo: columna geo debe ser del tipo geométrico Polygon o MultiPolygon
        cond_geo = data['geometry'].apply(lambda x: isinstance(x, (Polygon, MultiPolygon)))

        # Condición 5: Verificamos si hay valores NaN y en qué columnas están
        cond_nan = data.columns[data.isnull().any()].tolist()

        # Verificamos si todas las filas cumplen con todas las condiciones
        cumple_todas_condiciones = (cond_cvegeo & cond_ent & cond_nom_geo & cond_geo).all() and len(cond_nan) == 0
        
        if cumple_todas_condiciones:
            logging.info("Validation passed.")
            return True
        else:
            logging.warning(f"Validation failed. Missing columns with NaN values: {cond_nan}")
            return False
    except Exception as e:
        logging.error(f"Error during validation: {e}")
        return False

def save_tidy_data_shp(data, output_path):
    """Save the transformed tidy data."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_metadata(output_path, raw_data_path):
    """Create metadata for the processed data."""
    try:
        metadata_file = os.path.abspath(os.path.join("data", "metadata", "shp_transform_metadata.txt"))
        with open(metadata_file, 'w') as f:
            f.write("Metadata for SHP Data Transformation\n")
            f.write(f"Source: {raw_data_path}\n")
            f.write(f"Transformation date: {datetime.now()}\n")
            f.write(f"Tidy data saved at: {output_path}\n")
        logging.info(f"Metadata generated at {metadata_file}")
    except Exception as e:
        logging.error(f"Error creating metadata: {e}")

if __name__ == "__main__":
    output_file_path = os.path.join(interim_data_path_shp, "shp_tidy_data.csv")

    # Load raw data
    raw_data_ent, raw_data_mun = load_raw_shp(raw_data_path_shp)
    
    tidy_data_ent = None
    tidy_data_mun = None

    if raw_data_ent is not None and validate_data(raw_data_ent):
        tidy_data_ent = transform_shp_data(raw_data_ent)

    if raw_data_mun is not None and validate_data(raw_data_mun):
        tidy_data_mun = transform_shp_data(raw_data_mun)
    
    if tidy_data_ent is not None or tidy_data_mun is not None:
        tidy_data = pd.concat([tidy_data_ent, tidy_data_mun], ignore_index=True)
        save_tidy_data_shp(tidy_data, output_file_path)
        create_metadata(output_file_path, raw_data_path_shp)

    logging.info("SHP data transformation process completed.")
