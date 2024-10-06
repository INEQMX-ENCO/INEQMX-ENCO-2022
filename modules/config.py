import os

# Paths for storing raw data
raw_data_path_enco = os.path.abspath(os.path.join("data", "raw", "enco"))
raw_data_path_enigh = os.path.abspath(os.path.join("data", "raw", "enigh"))

# ENCO dataset URLs
base_url_enco = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls_enco = [f"{base_url_enco}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]

# ENIGH dataset URL
url_enigh = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"
processed_data_path_enigh = os.path.abspath(os.path.join("data", "interim", "enigh"))

# Path for logs folder
logs_folder = "logs"