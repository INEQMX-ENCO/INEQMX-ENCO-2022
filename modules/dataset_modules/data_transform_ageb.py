import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import raw_data_path_ageb, interim_data_path_ageb, logs_folder

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_ageb_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = ["ENTIDAD", 'MUN', 'NOM_LOC', 'AGEB', 'POBTOT']

def load_raw_ageb(file_path):
    """Load raw AGEB data from a directory containing multiple CSV files."""
    try:
        df_ageb = pd.DataFrame()
        logging.info(f"Loading raw AGEB data from {file_path}...")

        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(file_path) if f.endswith('.csv')]

        if not csv_files:
            logging.warning(f"No CSV files found in {file_path}")
            return None

        # Iterate over each CSV file and load it
        for csv_file in csv_files:
            file_path_full = os.path.join(file_path, csv_file)
            logging.info(f"Loading {csv_file}...")

            # Load CSV into DataFrame
            try:
                df = pd.read_csv(file_path_full, encoding='latin-1', dtype={6: str})
                # Fix encoding issues on the first column header
                df.columns = ['ENTIDAD' if col == '﻿ENTIDAD' else col for col in df.columns]
                df_ageb = pd.concat([df_ageb, df], ignore_index=True)  # Concatenate each CSV
                logging.info(f"Loaded {csv_file} successfully, current shape: {df_ageb.shape}")
            except Exception as e:
                logging.error(f"Error loading {csv_file}: {e}")

        logging.info(f"All AGEB files loaded successfully. Final shape: {df_ageb.shape}")
        return df_ageb
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def validate_data(data):
    """Validate the AGEB dataset to ensure it is tidy."""
    try:
        logging.info("Validating AGEB data...")

        # Check if required columns are present
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return False

        # Validation functions
        def validate_row_ent(entidad):
            """Validate 'ENTIDAD' column: 2-digit string in range [00, 32]."""
            if isinstance(entidad, str) and len(entidad) == 2:
                try:
                    val = int(entidad)
                    return 0 <= val <= 32
                except ValueError:
                    return False
            return False

        def validate_row_mun(municipio):
            """Validate 'MUN' column: 3-digit string in range [000, 570]."""
            if isinstance(municipio, str) and len(municipio) == 3:
                try:
                    val = int(municipio)
                    return 0 <= val <= 570
                except ValueError:
                    return False
            return False

        def validate_row_nom_loc(nom_loc):
            """Validate 'NOM_LOC' column: string with alphanumeric values, max 50 characters."""
            return isinstance(nom_loc, str) and len(nom_loc) <= 50

        def validate_row_ageb(ageb):
            """Validate 'AGEB' column: alphanumeric string, max 4 characters."""
            return isinstance(ageb, str) and len(ageb) == 4

        def validate_row_pob_tot(pobtot):
            """Validate 'POBTOT' column: integer value in range [0, 999999999]."""
            return isinstance(pobtot, int) and 0 <= pobtot <= 999999999

        # Apply validation functions to each column
        cond_ent = data['ENTIDAD'].apply(validate_row_ent).all()
        cond_mun = data['MUN'].apply(validate_row_mun).all()
        cond_nom_loc = data['NOM_LOC'].apply(validate_row_nom_loc).all()
        cond_ageb = data['AGEB'].apply(validate_row_ageb).all()
        cond_pob_tot = data['POBTOT'].apply(validate_row_pob_tot).all()

        # Log detailed information about the validation result
        if not cond_ent:
            logging.error("Validation failed: 'ENTIDAD' column has invalid values.")
        if not cond_mun:
            logging.error("Validation failed: 'MUN' column has invalid values.")
        if not cond_nom_loc:
            logging.error("Validation failed: 'NOM_LOC' column has invalid values.")
        if not cond_ageb:
            logging.error("Validation failed: 'AGEB' column has invalid values.")
        if not cond_pob_tot:
            logging.error("Validation failed: 'POBTOT' column has invalid values.")

        # Check if all conditions are met
        all_valid = cond_ent and cond_mun and cond_nom_loc and cond_ageb and cond_pob_tot

        if all_valid:
            logging.info("Data validation passed.")
            return True
        else:
            logging.error("Data validation failed.")
            return False
    except Exception as e:
        logging.error(f"Error during validation: {e}")
        return False


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

        # Rename columns for consistency
        tidy_data_ageb.rename(columns={
            "ENTIDAD": 'ent',
            "MUN": "mun",
            'NOM_LOC': 'nom_loc',
            'AGEB': 'ageb',
            'POBTOT': 'pob_tot'
        }, inplace=True)

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
        # Add a log to verify the save path
        logging.info(f"Attempting to save tidy data to {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_metadata(output_path, raw_data_path):
    """Create metadata for the processed data."""
    try:
        metadata_file = os.path.abspath(os.path.join("data", "metadata", "ageb_transform_metadata.txt"))
        logging.info(f"Attempting to create metadata file at {metadata_file}")
        
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            f.write("Metadata for AGEB Data Transformation\n")
            f.write(f"Source: {raw_data_path}\n")
            f.write(f"Transformation date: {datetime.now()}\n")
            f.write(f"Tidy data saved at: {output_path}\n")
            f.write(f"Selected columns: {', '.join(REQUIRED_COLUMNS)}\n")
        logging.info(f"Metadata generated at {metadata_file}")
    except Exception as e:
        logging.error(f"Error creating metadata: {e}")

if __name__ == "__main__":
    output_file_path = os.path.join(interim_data_path_ageb, "ageb_tidy_data.csv")

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

    logging.info("AGEB data transformation process completed.")
