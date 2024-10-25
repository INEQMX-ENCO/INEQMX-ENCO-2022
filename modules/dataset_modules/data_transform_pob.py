import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import raw_data_path_pob, url_pob, logs_folder

# Ensure the logs and metadata directories exist
os.makedirs(logs_folder, exist_ok=True)

# Setup logging configuration
log_filename = os.path.join(logs_folder, f"data_pob_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = [
    "ENTIDAD",'MUN','POBTOT','POBFEM','POBMAS' 
]

def load_raw_pob(file_path):
    """Load raw POB data from a directory containing zip files."""
    try:
        df_pob = pd.DataFrame()
        logging.info(f"Loading raw POB data from {file_path}...")
        csv_path = f"/iter_00_cpv2020/conjunto_de_datos/"
        csv_file = f"conjunto_de_datos_iter_00CSV20.csv"
        file_path = os.path.join(file_path, csv_path, csv_file) # Ruta completa del archivo csv
        if os.path.exists(file_path):
            df_pob = pd.read_csv(file_path, encoding='utf-8')
        else:
            logging.warning(f"{csv_file} not found in {file_path}")
        logging.info(f"Loaded df_pob shape: {df_pob.shape}")
        return df_pob
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return None

def validate_data(data):
    """Validate the POB dataset to ensure it is tidy."""
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
    
    # 3. Checking the following columns in the dataframe given the data conditions
    columns_to_check = ['POBTOT', 'POBFEM', 'POBMAS']
    for col in columns_to_check:
        if col in data.columns:
            # Check if the column is not already of integer type
            int_condition=data[col].dtype != 'int64'
            if int_condition:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
                print(f"Converted column {col} to integer.")

            # Check if there are values outside the range [0, 999999999]
            range_condition=data[col].min() < 0 or data[col].max() > 999999999
            if range_condition:
                data[col] = data[col].clip(lower=0, upper=999999999)
                print(f"Clipped values in column {col} to the range [0, 999999999].")

            # Check if any value has more than 9 digits
            len_condition=(data[col].apply(lambda x: len(str(abs(x)))) > 9).any()
            if len_condition:
                data[col] = data[col].apply(lambda x: int(str(x)[:9]))  # Truncate values to 9 digits
                print(f"Truncated values in column {col} to a maximum length of 9 digits.")
            if range_condition == False and len_condition == False and int_condition == False:
                print(f'The poblation columns are valid just as they are')
    
    # 4. Checking the following columns in the dataframe given the data conditions
    columns_to_check = ['ENTIDAD', 'MUN']
    for col in columns_to_check:
        if col in data.columns:
            # Check if the column is not already of integer type
            int_condition=data[col].dtype != 'int64'
            if int_condition:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
                print(f"Converted column {col} to integer.")

            if col=='ENTIDAD':
                # Check if there are values outside their appropriate range
                range_condition=data[col].min() < 0 or data[col].max() > 32
                if range_condition:
                    data[col] = data[col].clip(lower=0, upper=32)
                    print(f"Clipped values in column {col} to the range [0, 32].")
                # Check if any value has more than their appropriate digits
                len_condition=(data[col].apply(lambda x: len(str(abs(x)))) > 2).any()
                if len_condition:
                    data[col] = data[col].apply(lambda x: int(str(x)[:2]))  # Truncate values to 2 digits
                    print(f"Truncated values in column {col} to a maximum length of 2 digits.")
            else:
                # Check if there are values outside their appropriate range
                range_condition=data[col].min() < 0 or data[col].max() > 570
                if range_condition:
                    data[col] = data[col].clip(lower=0, upper=570)
                    print(f"Clipped values in column {col} to the range [0, 570].")
                # Check if any value has more than their appropriate digits
                len_condition=(data[col].apply(lambda x: len(str(abs(x)))) > 3).any()
                if len_condition:
                    data[col] = data[col].apply(lambda x: int(str(x)[:3]))  # Truncate values to 9 digits
                    print(f"Truncated values in column {col} to a maximum length of 3 digits.")
            
            if range_condition == False and len_condition == False and int_condition == False:
                print(f'The "entidad" and "municipio" columns are valid just as they are')
    return True

def transform_pob_data(data):
    """Select necessary columns and create tidy dataset."""
    try:
        logging.info("Transforming POB data...")

        # Check if all required columns exist in the data
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return None

        # Select necessary columns
        tidy_data_pob = data[REQUIRED_COLUMNS].copy()  # Use .copy() to avoid SettingWithCopyWarning
        # Rename columns
        tidy_data_pob.rename(columns={"ENTIDAD":'ent',"MUN": "mun",'POBTOT':'pob_tot','POBFEM':'pob_fem','POBMAS':'pob_mas'}, inplace=True)

        logging.info(f"Transformed data shape: {tidy_data_pob.shape}")
        return tidy_data_pob
    except KeyError as e:
        logging.error(f"Error transforming data: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_tidy_data_pob(data, output_path):
    """Save the transformed tidy data."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_metadata(output_path, raw_data_path):
    """Create metadata for the processed data."""
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "pob_transform_metadata.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for POB Data Transformation\n")
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
    output_file_path = os.path.join(interim_data_path_pob, "pob_tidy_data.csv")

    # Load raw data
    raw_data = load_raw_pob(raw_data_path_pob)

    if raw_data is not None:
        # Validate data
        if validate_data(raw_data):
            # Transform data
            tidy_data = transform_pob_data(raw_data)

            if tidy_data is not None:
                # Save tidy data
                save_tidy_data_pob(tidy_data, output_file_path)

                # Create metadata
                create_metadata(output_file_path, raw_data_path_pob)

                # Generate summary statistics for validation
                generate_summary_statistics(tidy_data)

    logging.info("POB data transformation process completed.")
