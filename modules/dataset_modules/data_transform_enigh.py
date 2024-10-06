import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import raw_data_path_enigh, processed_data_path_enigh, logs_folder

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_enigh_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = [
    "folioviv", "foliohog", "ubica_geo", "ing_cor", "ingtrab", "trabajo", "negocio",
    "otros_trab", "rentas", "utilidad", "arrenda", "transfer", "jubilacion",
    "becas", "donativos", "remesas", "bene_gob", "transf_hog", "trans_inst",
    "estim_alqu", "otros_ing", "factor", "upm", "est_dis"
]

def load_raw_enigh_data(file_path):
    """Load raw ENIGH data."""
    try:
        logging.info(f"Loading raw ENIGH data from {file_path}...")
        data = pd.read_csv(file_path)
        logging.info(f"Loaded data shape: {data.shape}")
        return data
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def validate_data(data):
    """Validate the ENIGH dataset to ensure it is tidy."""
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

    # 3. Check for duplicate household records
    if data.duplicated(subset=["folioviv", "foliohog"]).any():
        logging.error("Duplicate households found based on folioviv and foliohog.")
        return False

    # 4. Check for negative values in income columns
    income_columns = [col for col in REQUIRED_COLUMNS if "ing" in col]
    if (data[income_columns] < 0).any().any():
        logging.error("Negative income values detected.")
        return False

    # 5. Check if the weight (factor) column contains non-negative values
    if (data["factor"] < 0).any():
        logging.error("Negative values found in 'factor' column.")
        return False

    # 6. Check for unrealistic values in income columns
    unrealistic_threshold = 10**6  # Adjust based on your knowledge of the dataset
    if (data["ing_cor"] > unrealistic_threshold).any():
        logging.warning("Unrealistically high income values detected.")

    return True

def transform_enigh_data(data):
    """Select necessary columns and create tidy dataset."""
    try:
        logging.info("Transforming ENIGH data...")

        # Check if all required columns exist in the data
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return None

        # Select necessary columns
        tidy_data = data[REQUIRED_COLUMNS].copy()  # Use .copy() to avoid SettingWithCopyWarning

        # Ensure 'ubica_geo' is explicitly converted to a string
        tidy_data.loc[:, 'ubica_geo'] = tidy_data['ubica_geo'].astype(str)

        # Add derived columns: entidad (first 2 digits) and municipio (next 3 digits)
        tidy_data.loc[:, 'entidad'] = tidy_data['ubica_geo'].str[:2]  # Extract entity (state code)
        tidy_data.loc[:, 'municipio'] = tidy_data['ubica_geo'].str[2:5]  # Extract municipality code

        tidy_data.loc[:, 'Nhog'] = 1  # Add household flag

        # Sort data by income and household IDs
        tidy_data = tidy_data.sort_values(by=["ing_cor", "folioviv", "foliohog"])

        logging.info(f"Transformed data shape: {tidy_data.shape}")
        return tidy_data
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_tidy_data(data, output_path):
    """Save the transformed tidy data."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_metadata(output_path, raw_data_path):
    """Create metadata for the processed data."""
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "enigh_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for ENIGH Data Transformation\n")
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
    raw_file_path = os.path.join(raw_data_path_enigh, r"conjunto_de_datos_concentradohogar_enigh2022_ns\conjunto_de_datos\conjunto_de_datos_concentradohogar_enigh2022_ns.csv")  # Adjust based on actual raw file name
    output_file_path = os.path.join(processed_data_path_enigh, "enigh_tidy_data.csv")

    # Load raw data
    raw_data = load_raw_enigh_data(raw_file_path)
    
    if raw_data is not None:
        # Validate data
        if validate_data(raw_data):
            # Transform data
            tidy_data = transform_enigh_data(raw_data)
            
            if tidy_data is not None:
                # Save tidy data
                save_tidy_data(tidy_data, output_file_path)
                
                # Create metadata
                create_metadata(output_file_path, raw_file_path)
                
                # Generate summary statistics for validation
                generate_summary_statistics(tidy_data)

    logging.info("ENIGH data transformation process completed.")
