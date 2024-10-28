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

# Import entire dictionaries from config
from modules.config import data_paths, urls, years, BASE_URL_ENCO, LOGS_FOLDER

# Ensure logs directory exist
os.makedirs(LOGS_FOLDER, exist_ok=True)

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    while attempt < retries:
        try:
            # Get the file with redirection allowed and browser-like headers
            with requests.get(url, stream=True, allow_redirects=True, headers=headers) as r:
                r.raise_for_status()  # Check for HTTP errors

                # Verify Content-Type
                content_type = r.headers.get('Content-Type', '')
                if 'zip' not in content_type:
                    logging.warning(f"Expected a ZIP file from {url}, got {content_type}. URL may be incorrect.")
                    return  # Exit if not receiving a ZIP file

                # Track download progress
                total_size = int(r.headers.get('content-length', 0))
                block_size = 1024  # 1 KB
                buffer = BytesIO()
                with tqdm(total=total_size, unit='iB', unit_scale=True) as t:
                    for data in r.iter_content(block_size):
                        t.update(len(data))
                        buffer.write(data)

                # Check if the buffer contains a valid ZIP file
                buffer.seek(0)
                if zipfile.is_zipfile(buffer):
                    with zipfile.ZipFile(buffer) as z:
                        z.extractall(extract_path)
                        logging.info(f"Files successfully extracted from {url} to {extract_path}")
                        return  # Exit function if successful
                else:
                    logging.error(f"The downloaded file from {url} is not a valid ZIP archive.")
                    return  # Exit if file is not a valid ZIP archive

        except requests.exceptions.RequestException as e:
            logging.error(f"Download error for {url}: {e}. Retrying in {backoff_factor ** attempt} seconds.")
            time.sleep(backoff_factor ** attempt)  # Exponential backoff for retries
            attempt += 1
        except zipfile.BadZipFile:
            logging.error(f"Bad ZIP file encountered at {url}. Exiting download attempts.")
            return  # Exit if ZIP extraction fails with a BadZipFile error

    logging.error(f"Failed to download {url} after {retries} attempts.")

def build_url(year, month, info):
    if "exceptions" in info and month in info["exceptions"]:
        filename = info["exceptions"][month]
        if filename is None:
            return None  # Skip months with no file available
    else:
        filename = info["pattern"].format(month=month)
    return BASE_URL_ENCO.format(year=year, filename=filename)

# Parallel downloads using ThreadPoolExecutor
def download_data():
    # Clean directories for each dataset and year
    for year in years.keys():
        enco_path = data_paths['enco'][year]['raw']
        clean_directory(enco_path, preserve_files=['.gitkeep'])
        os.makedirs(enco_path, exist_ok=True)
    clean_directory(data_paths['enigh'][2018]['raw'], preserve_files=['.gitkeep'])
    clean_directory(data_paths['enigh'][2020]['raw'], preserve_files=['.gitkeep'])
    clean_directory(data_paths['enigh'][2022]['raw'], preserve_files=['.gitkeep'])
    clean_directory(data_paths['censo']['raw'], preserve_files=['.gitkeep'])
    clean_directory(data_paths['shp']['raw'], preserve_files=['.gitkeep'])

    # Download ENCO datasets using the `years` dictionary
    for year, info in years.items():
        enco_path = data_paths['enco'][year]['raw']
        
        for month in [str(i).zfill(2) for i in range(1, 13)]:
            url = build_url(year, month, info)
            if url:  # Skip months without a file
                download_and_extract_zip(url, enco_path)          

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Download CENSO datasets in parallel
        executor.map(lambda url: download_and_extract_zip(url, data_paths['censo']['raw']), urls['censo'])
        # Download SHP datasets in parallel
        executor.map(lambda url: download_and_extract_zip(url, data_paths['shp']['raw']), urls['shp'])

    # Download ENIGH datasets after ENCO downloads
    for year in [2018, 2020, 2022]:
        download_and_extract_zip(urls['enigh'][year], extract_path=data_paths['enigh'][year]['raw'])


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

        # ENCO Metadata for 2022
        f.write("Source: ENCO 2022\n")
        f.write(f"URLs: {', '.join(urls['enco'][2022])}\n")
        f.write(f"Download date: {datetime.now()}\n")
        f.write("Description: National Consumer Confidence Survey (ENCO) for the year 2022.\n")
        enco_info = list_files_and_folders(data_paths['enco'][2022]['raw'])
        if enco_info:
            for info in enco_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the ENCO folder.\n")

        # ENIGH Metadata for 2022
        f.write("\nSource: ENIGH 2022\n")
        f.write(f"URL: {urls['enigh'][2022]}\n")
        enigh_info = list_files_and_folders(data_paths['enigh'][2022]['raw'])
        if enigh_info:
            for info in enigh_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the ENIGH folder.\n")
        
        # CENSO Metadata for 2020
        f.write("Source: INEGI 2020\n")
        f.write(f"URLs: {', '.join(urls['censo'])}\n")
        f.write(f"Download date: {datetime.now()}\n")
        f.write("Description: Population and Housing Census for the year 2020.\n")
        censo_info = list_files_and_folders(data_paths['censo']['raw'])
        if censo_info:
            for info in censo_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the CENSO folder.\n")

        # SHP Metadata for 2020
        f.write("Source: INEGI 2020\n")
        f.write(f"URLs: {', '.join(urls['shp'])}\n")
        f.write(f"Download date: {datetime.now()}\n")
        f.write("Description: Shapefile of mexico by entity and municipality for the year 2020.\n")
        shp_info = list_files_and_folders(data_paths['shp']['raw'])
        if shp_info:
            for info in shp_info:
                f.write(f"{info}\n")
        else:
            f.write("No files or directories found in the SHP folder.\n")

# Main script execution
if __name__ == "__main__":
    logging.info("Starting download process...")
    download_data()
    create_metadata()
    logging.info("Process completed.")