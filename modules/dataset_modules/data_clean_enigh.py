import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Import configurations
from modules.config import data_paths, LOGS_FOLDER, BASE_PROCESSED_DATA_PATH
processed_enigh_path = os.path.join(BASE_PROCESSED_DATA_PATH, "enigh")

# Set logs folder path and ensure directory exists
logs_folder = LOGS_FOLDER
os.makedirs(logs_folder, exist_ok=True)

# Setup logging
log_filename = os.path.join(logs_folder, f"data_enigh_transform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Columns to select
REQUIRED_COLUMNS = ["folioviv", "foliohog", "ubica_geo", "ing_cor", "factor", "upm", "est_dis",
                    "ingtrab", "trabajo", "negocio", "otros_trab", "rentas", "utilidad", 
                    "arrenda", "transfer", "jubilacion", "becas", "donativos", "remesas", 
                    "bene_gob", "transf_hog", "trans_inst", "estim_alqu", "otros_ing"]

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

def clean_missing_data(data):
    """Clean missing data by handling NaN values in important columns."""
    # Log initial count of missing values
    missing_summary = data.isnull().sum()
    logging.info(f"Initial missing values per column:\n{missing_summary[missing_summary > 0]}")
    
    # Drop rows with missing values in essential columns
    essential_columns = ["folioviv", "foliohog", "ubica_geo", "ing_cor", "factor"]
    data.dropna(subset=essential_columns, inplace=True)
    
    # Fill income-related columns with 0 where values are missing
    income_columns = [col for col in REQUIRED_COLUMNS if "ing" in col or col in ["factor"]]
    data[income_columns] = data[income_columns].fillna(0)
    
    # Log the remaining missing values after cleaning
    remaining_missing_summary = data.isnull().sum()
    if remaining_missing_summary.any():
        logging.warning(f"Remaining missing values after cleaning:\n{remaining_missing_summary[remaining_missing_summary > 0]}")
    else:
        logging.info("No missing values remain after cleaning.")
    
    return data

def validate_data(data):
    """Validate the ENIGH dataset to ensure it is tidy."""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        logging.error(f"Missing columns: {missing_columns}")
        return False

    if data[REQUIRED_COLUMNS].isnull().any().any():
        logging.warning("Missing values detected in key columns.")
        data = data.dropna(subset=REQUIRED_COLUMNS)

    if data.duplicated(subset=["folioviv", "foliohog"]).any():
        logging.error("Duplicate households found based on folioviv and foliohog.")
        return False

    income_columns = [col for col in REQUIRED_COLUMNS if "ing" in col]
    if (data[income_columns] < 0).any().any():
        logging.error("Negative income values detected.")
        return False

    if (data["factor"] < 0).any():
        logging.error("Negative values found in 'factor' column.")
        return False

    unrealistic_threshold = 10**6  
    if (data["ing_cor"] > unrealistic_threshold).any():
        logging.warning("Unrealistically high income values detected.")

    return True

def transform_enigh_data(data):
    """Apply transformations and prepare data."""
    try:
        logging.info("Transforming ENIGH data...")
        tidy_data = data[REQUIRED_COLUMNS].copy()
        tidy_data['ubica_geo'] = tidy_data['ubica_geo'].astype(str)
        tidy_data['entidad'] = tidy_data['ubica_geo'].str[:-3].astype(int)
        tidy_data['municipio'] = tidy_data['ubica_geo'].str[-3:].astype(str).str.zfill(3)
        tidy_data['Nhog'] = 1

        logging.info(f"Transformed data shape: {tidy_data.shape}")
        return tidy_data
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return None

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
    
    gini_index = 1 - 2 * np.sum(cum_values[:-1] * (cum_weights[1:] - cum_weights[:-1]))
    return gini_index

def add_gini_and_deciles(data):
    """Add Gini coefficient and decile within each entidad, municipio, and year."""
    
    def process_group(group):
        gini_coef = calculate_gini(group['ing_cor'], weights=group['factor'])
        group['gini_year'] = gini_coef
        
        group = group.sort_values('ing_cor')
        group['cum_factor'] = group['factor'].cumsum()
        
        total_factor = group['factor'].sum()
        group['decile'] = pd.cut(group['cum_factor'], bins=np.linspace(0, total_factor, 11), labels=False, right=False)
        return group

    data = data.groupby(['entidad', 'municipio', 'year'], group_keys=False).apply(process_group)
    data['decile'] = data['decile'].fillna(0).astype(int)
    return data

def save_tidy_data(data, output_path):
    """Save the transformed tidy data."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        logging.info(f"Saved tidy data to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tidy data: {e}")

def create_summary_csv(data, output_path):
    """Create a summary CSV file with Gini coefficients and cumulative statistics by state, municipality, and year."""
    
    # Group by entidad (state) for Gini by state and calculate metrics
    summary_state = data.groupby(['entidad', 'year']).apply(
        lambda x: pd.Series({
            'gini_entidad_year': calculate_gini(x['ing_cor'], weights=x['factor']),
            'total_income_state': (x['ing_cor'] * x['factor']).sum(),
            'avg_income_state': np.average(x['ing_cor'], weights=x['factor']),
            'total_households_state': x['Nhog'].sum()
        })
    ).reset_index()

    # Group by entidad, municipio, and year for Gini by municipio and year
    summary_municipio = data.groupby(['entidad', 'municipio', 'year']).apply(
        lambda x: pd.Series({
            'gini_municipio_year': calculate_gini(x['ing_cor'], weights=x['factor']),
            'total_income_municipio': (x['ing_cor'] * x['factor']).sum(),
            'avg_income_municipio': np.average(x['ing_cor'], weights=x['factor']),
            'total_households_municipio': x['Nhog'].sum()
        })
    ).reset_index()

    # Merge the state and municipio summaries
    summary = pd.merge(summary_municipio, summary_state, on=['entidad', 'year'], how='left')

    # Save the summary DataFrame to a CSV file
    summary.to_csv(output_path, index=False)
    logging.info(f"Summary CSV saved to {output_path}")

# Main script
if __name__ == "__main__":
    combined_data = []

    for year in [2018, 2020, 2022]:
        raw_data_path = file_paths_by_year[year]
        interim_data_path = data_paths["enigh"][year]["interim"]

        raw_data = load_raw_enigh_data(raw_data_path)
        
        if raw_data is not None:
            # Clean missing values
            raw_data = clean_missing_data(raw_data)

            # Validate and transform
            if validate_data(raw_data):
                tidy_data = transform_enigh_data(raw_data)
                
                if tidy_data is not None:
                    tidy_data['year'] = year
                    combined_data.append(tidy_data)
                    
                    output_file = os.path.join(interim_data_path, f"enigh_tidy_{year}.csv")
                    save_tidy_data(tidy_data, output_file)

    # Combine data and add Gini/decile information
    combined_df = pd.concat(combined_data, ignore_index=True)
    combined_df = add_gini_and_deciles(combined_df)

    # Save the combined data to the processed ENIGH path
    final_output_file = os.path.join(processed_enigh_path, "enigh_interim_tidy.csv")
    save_tidy_data(combined_df, final_output_file)

    # Generate and save the summary CSV
    summary_output_file = os.path.join(processed_enigh_path, "enigh_summary_gini.csv")
    create_summary_csv(combined_df, summary_output_file)

    logging.info("Data processing complete.")