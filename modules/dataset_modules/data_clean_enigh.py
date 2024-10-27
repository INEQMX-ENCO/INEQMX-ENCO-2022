import os
import sys
import pandas as pd
import logging
from datetime import datetime
import numpy as np

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import data_paths, LOGS_FOLDER

# Set logs folder path
logs_folder = LOGS_FOLDER

# Ensure the logs directory exists
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

# Specific file paths for each year based on the different directory structures
file_paths_by_year = {
    2018: os.path.join(
        data_paths["enigh"][2018]["raw"], 
        "conjunto_de_datos_concentradohogar_enigh_2018_ns", 
        "conjunto_de_datos",
        "conjunto_de_datos_concentradohogar_enigh_2018_ns.csv"
    ),
    2020: os.path.join(
        data_paths["enigh"][2020]["raw"], 
        "conjunto_de_datos_concentradohogar_enigh_2020_ns", 
        "conjunto_de_datos",
        "conjunto_de_datos_concentradohogar_enigh_2020_ns.csv"
    ),
    2022: os.path.join(
        data_paths["enigh"][2022]["raw"], 
        "conjunto_de_datos_concentradohogar_enigh2022_ns", 
        "conjunto_de_datos",
        "conjunto_de_datos_concentradohogar_enigh2022_ns.csv"
    )
}

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

def validate_raw_data(df):
    """Validation steps for raw data before transformation."""
    errors = []
    
    # Check for missing values in key columns before transformation
    key_columns = ["folioviv", "foliohog", "ubica_geo", "ing_cor"]
    missing_values = df[key_columns].isnull().any()
    if missing_values.any():
        errors.append(f"Error: Missing values found in columns: {missing_values[missing_values].index.tolist()}")
    
    # Ensure income columns are non-negative in raw data
    income_columns = ["ing_cor", "ingtrab", "trabajo", "negocio", "otros_trab", 
                      "rentas", "utilidad", "arrenda", "transfer", "jubilacion", 
                      "becas", "donativos", "remesas", "bene_gob", "transf_hog", 
                      "trans_inst", "estim_alqu", "otros_ing"]
    if (df[income_columns] < 0).any().any():
        errors.append("Error: Negative values found in income columns.")
    
    # Output results of validation for raw data
    if errors:
        for error in errors:
            print(error)
        return False
    else:
        print("Raw data validations passed successfully.")
        return True


def validate_transformed_data(df):
    """Validation steps for transformed data with 'entidad' and 'municipio'."""
    errors = []
    
    # 1. Validate 'entidad' values (should be between 1 and 32)
    if not df['entidad'].between(1, 32).all():
        errors.append("Error: 'entidad' column contains values outside the range 1-32.")
    
    # 2. Validate 'municipio' values (should be three digits)
    if not df['municipio'].apply(lambda x: len(str(x)) == 3).all():
        errors.append("Error: 'municipio' column contains values that are not three digits.")
    
    # 3. Validate 'factor' column to be positive
    if not (df['factor'] > 0).all():
        errors.append("Error: 'factor' column contains non-positive values.")
    
    # 4. Check for unrealistic high income values (setting a threshold, e.g., 10^6)
    unrealistic_threshold = 1_000_000
    income_columns = ["ing_cor", "ingtrab", "trabajo", "negocio", "otros_trab", 
                      "rentas", "utilidad", "arrenda", "transfer", "jubilacion", 
                      "becas", "donativos", "remesas", "bene_gob", "transf_hog", 
                      "trans_inst", "estim_alqu", "otros_ing"]
    if (df[income_columns] > unrealistic_threshold).any().any():
        errors.append(f"Warning: Income columns contain values above {unrealistic_threshold}.")
    
    # Output results of validation for transformed data
    if errors:
        for error in errors:
            print(error)
        return False
    else:
        print("Transformed data validations passed successfully.")
        return True

def transform_enigh_data(data):
    """Transform ENIGH data to create a tidy dataset."""
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
        tidy_data['ubica_geo'] = tidy_data['ubica_geo'].astype(str)

        # Extract 'entidad' as an integer and 'municipio' as a three-digit string
        tidy_data['entidad'] = tidy_data['ubica_geo'].apply(lambda x: int(x[:-3]))
        tidy_data['municipio'] = tidy_data['ubica_geo'].apply(lambda x: x[-3:].zfill(3))  # Pad to ensure three digits
        
        # Add a household flag for counting purposes
        tidy_data['Nhog'] = 1

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

def create_metadata(output_path, raw_data_path, year):
    """Create metadata for the processed data."""
    metadata_file = os.path.abspath(os.path.join("data", "metadata", f"enigh_clean_metadata_{year}.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Metadata for ENIGH Data Transformation\n")
        f.write(f"Year: {year}\n")
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

# Function to calculate Gini coefficient
def calculate_gini(array, weights=None):
    """Calculate Gini coefficient with optional weighting."""
    array = np.asarray(array)
    if weights is None:
        weights = np.ones(len(array))
    weights = np.asarray(weights)
    
    sorted_indices = np.argsort(array)
    sorted_array = array[sorted_indices]
    sorted_weights = weights[sorted_indices]
    
    cum_weights = np.cumsum(sorted_weights)
    cum_values = np.cumsum(sorted_array * sorted_weights)
    
    total_weights = cum_weights[-1]
    total_values = cum_values[-1]
    cum_weights = cum_weights / total_weights
    cum_values = cum_values / total_values
    
    gini_index = 1 - 2 * np.sum(cum_values * (cum_weights[1:] - cum_weights[:-1]))
    return gini_index

def calculate_deciles(data):
    """Calculate income deciles based on weighted household data."""
    data = data.sort_values(by='ing_cor')
    data['cum_factor'] = data['factor'].cumsum()
    
    total_households = data['factor'].sum()
    decile_size = total_households // 10

    # Assign deciles based on cumulative factor weight
    data['decile'] = pd.cut(data['cum_factor'], bins=[0] + [decile_size * i for i in range(1, 11)] + [total_households],
                            labels=list(range(1, 11)), right=False)
    
    # Calculate weighted average income for each decile
    decile_averages = data.groupby('decile').apply(lambda x: np.average(x['ing_cor'], weights=x['factor']))
    decile_averages = decile_averages.rename('average_income')
    
    summary_table = pd.DataFrame({
        'decile': range(1, 11),
        'average_income': decile_averages.values
    })
    
    return summary_table

# Function to calculate Gini coefficient
def calculate_gini(array, weights=None):
    array = np.asarray(array)
    if weights is None:
        weights = np.ones(len(array))
    weights = np.asarray(weights)
    
    sorted_indices = np.argsort(array)
    sorted_array = array[sorted_indices]
    sorted_weights = weights[sorted_indices]
    
    cum_weights = np.cumsum(sorted_weights)
    cum_values = np.cumsum(sorted_array * sorted_weights)
    
    total_weights = cum_weights[-1]
    total_values = cum_values[-1]
    cum_weights = cum_weights / total_weights
    cum_values = cum_values / total_values
    
    gini_index = 1 - 2 * np.sum(cum_values * (cum_weights[1:] - cum_weights[:-1]))
    return gini_index

def add_gini_and_deciles(data):
    """Add Gini coefficient and decile within each entidad and year."""
    
    def process_group(group):
        # Calculate Gini coefficient for the group
        gini_coef = calculate_gini(group['ing_cor'], weights=group['factor'])
        group['gini_entidad_year'] = gini_coef

        # Sort by income and assign deciles based on cumulative factor weight
        group = group.sort_values(by='ing_cor')
        group['cum_factor'] = group['factor'].cumsum()
        
        # Determine decile size based on total factor
        total_factor = group['factor'].sum()
        decile_size = total_factor / 10

        # Assign deciles based on cumulative factor weight
        group['decile'] = pd.cut(group['cum_factor'], 
                                 bins=[0] + [decile_size * i for i in range(1, 11)] + [total_factor],
                                 labels=list(range(1, 11)), 
                                 right=False)
        
        return group

    # Apply the process_group function to each entidad and year group
    data = data.groupby(['entidad', 'year'], group_keys=False).apply(process_group)
    
    # Ensure the decile column is numeric
    data['decile'] = data['decile'].astype(int)
    
    return data

if __name__ == "__main__":
    combined_data = []  # Ensure this is only initialized once here

    for year in [2018, 2020, 2022]:
        raw_data_path = file_paths_by_year[year]
        interim_data_path = data_paths["enigh"][year]["interim"]

        raw_data = load_raw_enigh_data(raw_data_path)
        
        if raw_data is not None and validate_raw_data(raw_data):
            tidy_data = transform_enigh_data(raw_data)
            
            if tidy_data is not None and validate_transformed_data(tidy_data):
                output_file_path = os.path.join(interim_data_path, f"enigh_tidy_data_{year}.csv")
                save_tidy_data(tidy_data, output_file_path)
                
                # Check 'tidy_data' shape and ensure it's not empty before appending
                logging.info(f"Preparing to append transformed data for year {year} with shape: {tidy_data.shape}")
                if tidy_data.empty:
                    logging.error(f"tidy_data for year {year} is empty, not appending.")
                else:
                    tidy_data['year'] = year
                    combined_data += [tidy_data]  # Use `+=` to explicitly add `tidy_data` as a list item
                    
                    # Log the combined_data length after each append
                    logging.info(f"Appended transformed data for year {year}. Current combined_data length: {len(combined_data)}")

                create_metadata(output_file_path, raw_data_path, year)
                generate_summary_statistics(tidy_data)
    
    # Check if combined_data has been populated before concatenating
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        logging.info(f"Combined data shape after concatenation: {combined_df.shape}")
        
        combined_output_path = os.path.join(data_paths["enigh"][2018]["interim"].rsplit("\\", 1)[0], "enigh_tidy_data_combined.csv")
        save_tidy_data(combined_df, combined_output_path)
        create_metadata(combined_output_path, "Combined ENIGH Data", "All Years")
        generate_summary_statistics(combined_df)

        # Check columns before adding Gini and deciles
        logging.info(f"Columns before Gini and deciles: {combined_df.columns.tolist()}")

        # Add Gini coefficient and decile data per entidad and year
        combined_df = add_gini_and_deciles(combined_df)
        
        # Check columns after adding Gini and deciles
        logging.info(f"Columns after adding Gini and deciles: {combined_df.columns.tolist()}")

        # Confirm that Gini and decile columns are added
        if 'gini_entidad_year' in combined_df.columns and 'decile' in combined_df.columns:
            logging.info("Gini and decile columns successfully added to the combined data.")
        else:
            logging.warning("Gini and decile columns were not added correctly to the combined data.")

        # Set output path and attempt to save the updated combined data with Gini and decile information
        gini_decile_output_path = os.path.join(data_paths["enigh"][2018]["interim"].rsplit("\\", 1)[0], "enigh_tidy_data_combined_with_gini_deciles.csv")
        save_tidy_data(combined_df, gini_decile_output_path)
        logging.info(f"Gini and decile data saved to {gini_decile_output_path}")
    else:
        logging.error("Combined data is empty; skipping Gini and decile calculations.")
    
    logging.info("ENIGH data transformation process completed for all years with Gini and decile data.")
