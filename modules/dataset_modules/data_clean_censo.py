import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import data_paths, LOGS_FOLDER

# Ensure interim data path and logs directory exist
interim_data_path_censo = data_paths["censo"]["interim"]
processed_data_path_censo = data_paths["censo"]["processed"]
os.makedirs(interim_data_path_censo, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(LOGS_FOLDER, f"data_censo_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = [
    "ENTIDAD",'MUN','LOC','POBTOT','REL_H_M' 
]

# These columns should not have nan values
REQUIRED_ALL_COLUMNS= [ 
    "ENTIDAD",'MUN','LOC','POBTOT'
]

def load_raw_censo(file_path):
    """Load raw CENSO data from a directory containing multiple CSV files."""
   
    try:
        df_censo = pd.DataFrame()
        logging.info(f"Loading raw CENSO data from {file_path}...")

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
                df_censo = pd.read_csv(file_path_full, encoding='latin-1', dtype={8: str})
                # Fix encoding issues on the first column header
                df_censo.columns = ['ENTIDAD' if col == 'ï»¿ENTIDAD' else col for col in df_censo.columns]
                logging.info(f"Loaded {csv_file} successfully, current shape: {df_censo.shape}")
            except Exception as e:
                logging.error(f"Error loading {csv_file}: {e}")

        logging.info(f"All CENSO files loaded successfully. Final shape: {df_censo.shape}")
        return df_censo
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def validate_data(data):
    """Validate the CENSO dataset to ensure it is tidy."""
    try:
        logging.info("Validating CENSO data...")

        # Check if required columns are present
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return False

        # 2. Check for missing values in key columns
        if data[REQUIRED_ALL_COLUMNS].isnull().any().any():
            logging.warning("Missing values detected in key columns.")
            # Optional: Decide whether to drop or fill missing values
            data = data.dropna(subset=REQUIRED_ALL_COLUMNS) # In this case, drop

        # Validation functions
        def validate_row_ent(entidad):
            """Validate 'ENT' column: integer value in range [0, 32]."""
            return isinstance(entidad, int) and 0 <= entidad <= 32
        
        def validate_row_mun(municipio):
            """Validate 'MUN' column: integer value in range [0, 570]."""
            return isinstance(municipio, int) and 0 <= municipio <= 570
        
        def validate_row_pob_tot(pobtot):
            """Validate 'POBTOT' column: integer value in range [0, 999999999]."""
            return isinstance(pobtot, int) and 0 <= pobtot <= 999999999
        
        def validate_row_loc(loc):
            """Validate 'LOC' column: integer value in range [0, 9999]."""
            return isinstance(loc, int) and 0 <= loc <= 9999
        
        def validate_row_rel_h_m(rel_h_m):
            """Validate 'REL_H_M' column: object, that if converted to float value it is in range [0, 999999999]."""
            return isinstance(rel_h_m, object) and 0 <= float(rel_h_m) <= 999999999

        # Apply validation functions to each column
        cond_ent = data['ENTIDAD'].apply(validate_row_ent).all()
        cond_mun = data['MUN'].apply(validate_row_mun).all()
        cond_loc = data['LOC'].apply(validate_row_loc).all()
        cond_pob_tot = data['POBTOT'].apply(validate_row_pob_tot).all()
        cond_rel_h_m = data.loc[data['LOC'] == 0, 'REL_H_M'].apply(validate_row_rel_h_m).all() # Just need to check where loc column is 0

        # Log detailed information about the validation result
        if not cond_ent:
            logging.error("Validation failed: 'ENTIDAD' column has invalid values.")
        if not cond_mun:
            logging.error("Validation failed: 'MUN' column has invalid values.")
        if not cond_loc:
            logging.error("Validation failed: 'LOC' column has invalid values.")
        if not cond_pob_tot:
            logging.error("Validation failed: 'POBTOT' column has invalid values.")
        if not cond_rel_h_m:
            logging.error("Validation failed: 'REL_H_M' column has invalid values.")

        # Check if all conditions are met
        all_valid = cond_ent and cond_mun and cond_loc and cond_pob_tot and cond_rel_h_m

        if all_valid:
            logging.info("Data validation passed.")
            return True
        else:
            logging.error("Data validation failed.")
            return False
    except Exception as e:
        logging.error(f"Error during validation: {e}")
        return False


def transform_censo_data(data):
    """Select necessary columns and create tidy dataset."""
    try:
        logging.info("Transforming CENSO data...")

        # Check if all required columns exist in the data
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return None

        # Select necessary columns
        data_censo = data[REQUIRED_COLUMNS].copy()  # Use .copy() to avoid SettingWithCopyWarning

        # Rename columns for consistency
        data_censo.rename(columns={
            "ENTIDAD": 'ent',
            "MUN": "mun",
            'LOC': 'loc',
            'POBTOT': 'pob_tot',
            'REL_H_M': 'rel_h_m'
        }, inplace=True)
        
        # Transform to tidy
        data_censo=data_censo[data_censo['loc'] == 0].drop(index=0).reset_index(drop=True) # Only those with aggregated population
        data_censo['cvegeo']=data_censo['ent'].astype(str).str.zfill(2)+data_censo['mun'].astype(str).str.zfill(3)
        data_censo['cvegeo'] = data_censo['cvegeo'].apply(lambda x: str(x)[:2] if str(x).endswith('000') else str(x))
        data_censo.drop(columns=['ent', 'mun', 'loc'], errors='ignore', inplace=True)
        #data_censo['rel_h_m'] = data_censo['rel_h_m'].astype(float)
        tidy_data_censo=data_censo[['cvegeo','pob_tot','rel_h_m']] # desired order 

        logging.info(f"Transformed data shape: {tidy_data_censo.shape}")
        return tidy_data_censo
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_tidy_data_censo(data, output_path):
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
        metadata_file = os.path.abspath(os.path.join("data", "metadata", "censo_transform_metadata.txt"))
        logging.info(f"Attempting to create metadata file at {metadata_file}")
        
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            f.write("Metadata for CENSO Data Transformation\n")
            f.write(f"Source: {raw_data_path}\n")
            f.write(f"Transformation date: {datetime.now()}\n")
            f.write(f"Tidy data saved at: {output_path}\n")
            f.write(f"Selected columns: {', '.join(REQUIRED_COLUMNS)}\n")
        logging.info(f"Metadata generated at {metadata_file}")
    except Exception as e:
        logging.error(f"Error creating metadata: {e}")

if __name__ == "__main__":
    raw_file_path = os.path.join(data_paths['censo']['raw'], "iter_00_cpv2020",'conjunto_de_datos')
    output_file_path_ent = os.path.join(processed_data_path_censo, "censo_ent_tidy_data.csv")
    output_file_path_mun = os.path.join(processed_data_path_censo, "censo_mun_tidy_data.csv")
    output_file_path = os.path.join(processed_data_path_censo, "censo_tidy_data.csv")

    # Load raw data
    raw_data = load_raw_censo(raw_file_path)

    if raw_data is not None:
        # Validate data
        if validate_data(raw_data):
            # Transform data
            tidy_data = transform_censo_data(raw_data)
            tidy_data_ent= tidy_data[tidy_data['cvegeo'].str.len() == 2].copy()
            tidy_data_mun= tidy_data[tidy_data['cvegeo'].str.len() == 5].copy()
            if tidy_data_ent is not None:
            #     # Save tidy data
                save_tidy_data_censo(tidy_data_ent, output_file_path_ent)
            #     # Create metadata
                create_metadata(output_file_path_ent, raw_file_path)

            if tidy_data_mun is not None:
            #     # Save tidy data
                save_tidy_data_censo(tidy_data_mun, output_file_path_mun)
            #     # Create metadata
                create_metadata(output_file_path_mun, raw_file_path)

    logging.info("CENSO data transformation process completed.")
