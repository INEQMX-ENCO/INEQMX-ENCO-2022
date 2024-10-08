import os

# Paths for storing raw data
raw_data_path_enco = os.path.abspath(os.path.join("data", "raw", "enco"))
raw_data_path_enigh = os.path.abspath(os.path.join("data", "raw", "enigh"))
raw_data_path_ageb = os.path.abspath(os.path.join("data", "raw", "ageb"))
raw_data_path_shp = os.path.abspath(os.path.join("data", "raw", "shp"))

# ENCO dataset URLs
base_url_enco = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls_enco = [f"{base_url_enco}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]
interim_data_path_enco = os.path.abspath(os.path.join("data", "interim", "enco"))

# ENIGH dataset URL
url_enigh = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"
interim_data_path_enigh = os.path.abspath(os.path.join("data", "interim", "enigh"))

# AGEB dataset URLs
base_url_ageb = "https://www.inegi.org.mx/contenidos/programas/ccpv/iter/zip/resageburb20/"
url_ageb = [f"{base_url_ageb}resageburb_{str(i).zfill(2)}csv20.zip" for i in range(1, 33)]
interim_data_path_ageb = os.path.abspath(os.path.join("data", "interim", "ageb"))

# SHP dataset URLs
base_url_shp = "https://www.inegi.org.mx/contenidos/descargadenue/MGdescarga/MGN2020_1/"
url_shp = [f"{base_url_shp}2020_1_00_{str(i)}.zip" for i in ['ENT','MUN']]
interim_data_path_shp = os.path.abspath(os.path.join("data", "interim", "shp"))

# Path for logs folder
logs_folder = "logs"