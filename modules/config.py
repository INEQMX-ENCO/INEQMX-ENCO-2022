import os

# Base paths
BASE_RAW_DATA_PATH = os.path.abspath("data/raw")
BASE_INTERIM_DATA_PATH = os.path.abspath("data/interim")
BASE_PROCESSED_DATA_PATH = os.path.abspath("data/processed")

# Paths for storing raw and interim data, organized by dataset and year
data_paths = {
    "enco": {
        year: {
            "raw": os.path.join(BASE_RAW_DATA_PATH, "enco", str(year)),
            "interim": os.path.join(BASE_INTERIM_DATA_PATH, "enco", str(year))
        } for year in [2018, 2020, 2022]
    },
    "enigh": {
        year: {
            "raw": os.path.join(BASE_RAW_DATA_PATH, "enigh", str(year)),
            "interim": os.path.join(BASE_INTERIM_DATA_PATH, "enigh", str(year))
        } for year in [2018, 2020, 2022]
    },
    "censo": {
        "raw": os.path.join(BASE_RAW_DATA_PATH, "censo"),
        "interim": os.path.join(BASE_INTERIM_DATA_PATH, "censo")
    },
    "shp": {
        "raw": os.path.join(BASE_RAW_DATA_PATH, "shp"),
        "interim": os.path.join(BASE_INTERIM_DATA_PATH, "shp")
    }
}

# Patterns and exceptions for ENCO file naming by year and month
years = {
    2018: {
        "pattern": "conjunto_de_datos_enco_2018_{month}_csv",
        "exceptions": {
            "01": "enco_enero_2018_csv",
            "02": "enco_febrero_2018_csv",
            "03": "enco_marzo_2018_csv",
            "04": "enco_abril_2018_csv",
            "05": "enco_mayo_2018_csv",
            "06": "conjunto_de_datos_enco0618_csv",
            "07": "conjunto_de_datos_enco0718_csv"
        }
    },
    2020: {
        "pattern": "conjunto_de_datos_enco_2020_{month}_csv",
        "exceptions": {
            "04": None, "05": None, "06": None, "07": None  # Missing months
        }
    },
    2022: {
        "pattern": "conjunto_de_datos_enco_2022_{month}_csv"
    }
}

# Base URLs for datasets
BASE_URL_ENCO = "https://www.inegi.org.mx/contenidos/programas/enco/datosabiertos/{year}/{filename}.zip"
BASE_URL_ENIGH = "https://www.inegi.org.mx/contenidos/programas/enigh/nc"
BASE_URL_CENSO = "https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip"
BASE_URL_SHP = "https://www.inegi.org.mx/contenidos/descargadenue/MGdescarga/MGN2020_1"

# Download URLs by dataset and year
urls = {
    "enco": {
        year: {
            month: BASE_URL_ENCO.format(
                year=year,
                filename=years[year].get("exceptions", {}).get(month, years[year]["pattern"].format(month=month))
            )
            for month in [f"{i:02}" for i in range(1, 13)]  # Months 01 to 12
            if years[year].get("exceptions", {}).get(month) is not None or "pattern" in years[year]
        } for year in [2018, 2020, 2022]
    },
    "enigh": {
        2018: f"{BASE_URL_ENIGH}/2018/datosabiertos/conjunto_de_datos_enigh_2018_ns_csv.zip",
        2020: f"{BASE_URL_ENIGH}/2020/datosabiertos/conjunto_de_datos_enigh_ns_2020_csv.zip",
        2022: f"{BASE_URL_ENIGH}/2022/datosabiertos/conjunto_de_datos_enigh_ns_2022_csv.zip"
    },
    "censo": [f"{BASE_URL_CENSO}"],
    "shp": [f"{BASE_URL_SHP}/2020_1_00_{i}.zip" for i in ["ENT", "MUN"]]
}

# Path for logs folder
LOGS_FOLDER = os.path.abspath("logs")