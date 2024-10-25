import os

# Paths for storing raw data
raw_data_path_enco = os.path.abspath(os.path.join("data", "raw", "enco"))
raw_data_path_enigh = os.path.abspath(os.path.join("data", "raw", "enigh"))
raw_data_path_pob = os.path.abspath(os.path.join("data", "raw", "pob"))
raw_data_path_shp = os.path.abspath(os.path.join("data", "raw", "shp"))

# ENCO dataset URLs
base_url_enco = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/2022/"
urls_enco = [f"{base_url_enco}conjunto_de_datos_enco_2022_{str(i).zfill(2)}_csv.zip" for i in range(1, 13)]

# ENIGH dataset URL
url_enigh = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"
interim_data_path_enigh = os.path.abspath(os.path.join("data", "interim", "enigh"))
interim_data_path = os.path.abspath(os.path.join("data", "interim", "enco"))

# POB dataset URL
url_pob = "https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip"

# SHP dataset URLs
base_url_shp = "https://www.inegi.org.mx/contenidos/descargadenue/MGdescarga/MGN2020_1/"
urls_shp = [f"{base_url_shp}2020_1_00_{str(i)}.zip" for i in ['ENT','MUN']]

# Path for logs folder
logs_folder = "logs"