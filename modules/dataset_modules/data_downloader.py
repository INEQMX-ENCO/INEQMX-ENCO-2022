import requests
import zipfile
import os
import sys
from io import BytesIO
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

# Now you can import modules
from modules.config import urls_enco, url_enigh, url_pob, urls_shp, raw_data_path_enco, raw_data_path_enigh, raw_data_path_pob, raw_data_path_shp

# Setup logging configuration
logging.basicConfig(filename=f"logs/data_downloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Function to clean the directory except for .gitkeep files
def clean_directory(directory_path, preserve_files=None):
    """
    Remove all files and subfolders in the directory except those in the preserve_files list.

    Args:
        directory_path (str): The path to the directory to clean.
        preserve_files (list): List of file names to preserve (e.g., ['.gitkeep']).
    """
    if preserve_files is None:
        preserve_files = []

    try:
        for root, dirs, files in os.walk(directory_path, topdown=False):
            # Remove all files except those to preserve
            for file in files:
                if file not in preserve_files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    logging.info(f"Deleted file: {file_path}")
            # Remove empty directories
            for dir_ in dirs:
                dir_path = os.path.join(root, dir_)
                os.rmdir(dir_path)
                logging.info(f"Deleted directory: {dir_path}")
    except Exception as e:
        logging.error(f"Error cleaning directory {directory_path}: {e}")

# Function for downloading and extracting ZIP files with retry logic and progress bar
def download_and_extract_zip(url, extract_path, retries=3, backoff_factor=2):
    attempt = 0
    while attempt < retries:
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                block_size = 1024  # 1 KB
                t = tqdm(total=total_size, unit='iB', unit_scale=True)
                buffer = BytesIO()
                for data in r.iter_content(block_size):
                    t.update(len(data))
                    buffer.write(data)
                t.close()

                with zipfile.ZipFile(buffer) as z:
                    z.extractall(extract_path)
                    logging.info(f"Files extracted from {url} into {extract_path}")
            break  # Exit if successful
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {url}: {e}, retrying in {backoff_factor} seconds...")
            attempt += 1
            time.sleep(backoff_factor ** attempt)  # Exponential backoff
        except zipfile.BadZipFile as e:
            logging.error(f"Error extracting {url}: {e}")
            break  # Exit loop on bad ZIP file
    else:
        logging.error(f"Failed to download {url} after {retries} attempts.")

# Parallel downloads using ThreadPoolExecutor
def download_data():
    # Clean directories before downloading new data
    clean_directory(raw_data_path_enco, preserve_files=['.gitkeep'])
    clean_directory(raw_data_path_enigh, preserve_files=['.gitkeep'])
    clean_directory(raw_data_path_pob, preserve_files=['.gitkeep'])
    clean_directory(raw_data_path_shp, preserve_files=['.gitkeep'])

    os.makedirs(raw_data_path_enco, exist_ok=True)
    os.makedirs(raw_data_path_enigh, exist_ok=True)
    os.makedirs(raw_data_path_pob, exist_ok=True)
    os.makedirs(raw_data_path_shp, exist_ok=True)

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Download ENCO datasets in parallel
        executor.map(lambda url: download_and_extract_zip(url, raw_data_path_enco), urls_enco)

        # Download SHP datasets in parallel
        executor.map(lambda url: download_and_extract_zip(url, raw_data_path_shp), urls_shp)

    # Download POB dataset after ENCO and SHP downloads
    download_and_extract_zip(url_pob, extract_path=raw_data_path_pob)

    # Download ENIGH dataset after POB downloads
    download_and_extract_zip(url_enigh, extract_path=raw_data_path_enigh)

# Function to list only files in a directory and capture their metadata
def list_files_and_folders(directory_path):
    file_info = []
    try:
        for root, dirs, files in os.walk(directory_path):
            relative_dir = os.path.relpath(root, directory_path)
            if relative_dir == ".":
                relative_dir = ""  # Root directory

            # Add directory information
            if dirs:
                file_info.append(f"Directory: {relative_dir}")

            # Add file information
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_info.append(f"File: {os.path.join(relative_dir, file)}, Size: {file_size} bytes")

        return file_info
    except Exception as e:
        logging.error(f"Error listing files and folders in {directory_path}: {e}")
        return []


# Function to create enriched metadata
def create_metadata():
    metadata_file = os.path.abspath(os.path.join("data", "metadata", "data_sources_description.txt"))
    with open(metadata_file, 'w') as f:
        f.write("Description of the downloaded data sources:\n\n")

        # ENCO Metadata
        f.write("Source: ENCO 2022\n")
        f.write(f"URLs: {', '.join(urls_enco)}\n")
        f.write(f"Download date: {datetime.now()}\n")
        f.write("Description: National Consumer Confidence Survey (ENCO) for the year 2022.\n")

        # List all files and subfolders in the ENCO directory and write to metadata
        enco_info = list_files_and_folders(raw_data_path_enco)
        if enco_info:
            for info in enco_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the ENCO folder.\n")

        # ENIGH Metadata
        f.write("\nSource: ENIGH 2022\n")
        f.write(f"URL: {url_enigh}\n")

        # List all files and subfolders in the ENIGH directory and write to metadata
        enigh_info = list_files_and_folders(raw_data_path_enigh)
        if enigh_info:
            for info in enigh_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the ENIGH folder.\n")

        # POB Metadata
        f.write("Source: INEGI 2020\n")
        f.write(f"URL: {', '.join(url_pob)}\n")
        f.write(f"Download date: {datetime.now()}\n")
        f.write("Description: Censo de Población y Vivienda 2020.\n")

        # List all files and subfolders in the POB directory and write to metadata
        pob_info = list_files_and_folders(raw_data_path_pob)
        if pob_info:
            for info in pob_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the POB folder.\n")

        # SHP Metadata
        f.write("\nSource: INEGI 2020\n")
        f.write(f"URL: {urls_shp}\n")

        # List all files and subfolders in the SHP directory and write to metadata
        shp_info = list_files_and_folders(raw_data_path_shp)
        if shp_info:
            for info in shp_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the SHP folder.\n")


    logging.info(f"Metadata generated at {metadata_file}")

# Main script execution
if __name__ == "__main__":
    logging.info("Starting download process...")
    download_data()
    create_metadata()
    logging.info("Process completed.")