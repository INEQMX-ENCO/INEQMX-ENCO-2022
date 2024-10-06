# Importar librerías necesarias
import pandas as pd
import numpy as np
from scipy.stats import rankdata
from pathlib import Path
import os

# Función para cargar datos desde un archivo CSV
def cargar_datos(ruta_csv):
    """Carga los datos desde el archivo CSV y selecciona las variables necesarias."""
    try:
        df = pd.read_csv(ruta_csv)
        df = df[['folioviv', 'foliohog', 'ing_cor', 'ingtrab', 'trabajo', 'negocio',
                 'otros_trab', 'rentas', 'utilidad', 'arrenda', 'transfer', 'jubilacion',
                 'becas', 'donativos', 'remesas', 'bene_gob', 'transf_hog', 'trans_inst',
                 'estim_alqu', 'otros_ing', 'factor', 'upm', 'est_dis', 'ubica_geo']]
        return df
    except FileNotFoundError:
        print(f"El archivo en la ruta {ruta_csv} no se encontró.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al cargar los datos: {e}")
        return None

def agregar_entidad(df):
    """
    Agrega las columnas 'estado' y 'municipio' basadas en la variable 'ubica_geo'.
    'ubica_geo' contiene los dos primeros dígitos para la entidad federativa y
    los siguientes tres dígitos para el municipio, según el catálogo del INEGI.
    """
    # Extraer los primeros 2 dígitos como clave de entidad
    df['estado'] = df['ubica_geo'].astype(str).str[:2]
    
    # Extraer los siguientes 3 dígitos como clave de municipio
    df['municipio'] = df['ubica_geo'].astype(str).str[2:5]
    
    return df

# Función para calcular deciles
def calcular_deciles(df):
    """Calcula los deciles de ingreso basado en el ingreso corriente."""
    df['Nhog'] = 1
    df = df.sort_values(by=['ing_cor', 'folioviv', 'foliohog'])
    tot_hogares = df['factor'].sum()
    tam_dec = np.trunc(tot_hogares / 10).astype(int)

    # Crear una copia para los cálculos
    BD1 = df.copy()
    BD1['MAXT'] = BD1['ing_cor']
    BD1 = BD1.sort_values(by='MAXT')
    BD1['ACUMULA'] = BD1['factor'].cumsum()

    # Crear deciles
    for i in range(1, 10):
        a1 = BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1], 'factor']
        b1 = tam_dec * i - BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1], 'ACUMULA']
        BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1] + 1, 'factor'] = b1
        BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1] + 2, 'factor'] = a1 - b1

    # Recalcular acumulado
    BD1['ACUMULA2'] = BD1['factor'].cumsum()
    BD1['DECIL'] = 0
    BD1.loc[BD1['ACUMULA2'] <= tam_dec, 'DECIL'] = 1

    for i in range(1, 10):
        BD1.loc[(BD1['ACUMULA2'] > tam_dec * i) & (BD1['ACUMULA2'] <= tam_dec * (i + 1)), 'DECIL'] = i + 1

    BD1.loc[BD1['DECIL'] == 0, 'DECIL'] = 10
    df['DECIL'] = BD1['DECIL'].values
    return df

# Función para calcular el coeficiente de Gini
def gini(array, weights=None):
    """Calcula el coeficiente de Gini."""
    array = np.asarray(array)
    if weights is None:
        weights = np.ones_like(array)
    else:
        weights = np.asarray(weights)

    sorted_indices = np.argsort(array)
    sorted_array = array[sorted_indices]
    sorted_weights = weights[sorted_indices]

    # Sumas acumuladas
    cum_weights = np.cumsum(sorted_weights)
    cum_income = np.cumsum(sorted_array * sorted_weights)

    # Normalizar
    cum_weights_norm = cum_weights / cum_weights[-1]
    cum_income_norm = cum_income / cum_income[-1]

    # Área bajo la curva Lorenz
    B = np.trapz(cum_income_norm, cum_weights_norm)
    return 1 - 2 * B

# Función para descomponer la variable folioviv
def descomponer_folioviv(folio):
    """Descompone 'folioviv' en sus componentes: entidad, ámbito, UPM, decena y número de control."""
    folio_str = str(folio).zfill(10)
    entidad = folio_str[:2]
    ambito = folio_str[2]
    upm = folio_str[3:7]
    decena = folio_str[7]
    num_control = folio_str[8:]
    return entidad, ambito, upm, decena, num_control

# Función para guardar el DataFrame en un archivo CSV
def guardar_datos(df, output_path):
    """Guarda el DataFrame en un archivo CSV en la ruta especificada."""
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar el archivo CSV
    try:
        df.to_csv(output_path, index=False)
        print(f"Datos guardados exitosamente en {output_path}")
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo: {e}")

# Función principal
def main():
    # Ruta relativa al archivo CSV
    relative_path = Path(r"data/raw/enigh/conjunto_de_datos_concentradohogar_enigh2022_ns/conjunto_de_datos/conjunto_de_datos_concentradohogar_enigh2022_ns.csv")
    
    # Obtener la ruta absoluta
    csv_path = relative_path.resolve()

    # Cargar los datos
    datos = cargar_datos(csv_path)
    if datos is None:
        return
    
    # Agregar entidad federativa
    datos = agregar_entidad(datos)

    # Calcular deciles de ingreso
    datos = calcular_deciles(datos)

    # Calcular el coeficiente de Gini
    deciles_hog_ingcor = datos.groupby('DECIL').agg({
        'factor': 'sum',
        'ing_cor': lambda x: (x * datos['factor']).sum() / datos['factor'].sum()
    })

    gini_nacional = gini(deciles_hog_ingcor['ing_cor'].values, deciles_hog_ingcor['factor'].values)

    # Mostrar resultados
    print("\nCoeficiente de Gini Nacional:", round(gini_nacional, 3))

    # Descomponer 'folioviv' en nuevas columnas
    datos[['entidad', 'ambito', 'upm', 'decena', 'num_control']] = datos['folioviv'].apply(descomponer_folioviv).apply(pd.Series)

    # Eliminar las columnas no deseadas
    columnas_a_eliminar = ['ingtrab', 'trabajo', 'negocio', 'otros_trab', 'rentas', 'utilidad', 'arrenda', 
                           'transfer', 'jubilacion', 'becas', 'donativos', 'remesas', 'bene_gob', 'transf_hog', 
                           'trans_inst', 'estim_alqu', 'otros_ing']
    datos = datos.drop(columns=columnas_a_eliminar)

    # Guardar el DataFrame en la ruta especificada
    interim_data_path = os.path.abspath(os.path.join("data", "interim", "enigh", "datos_procesados.csv"))
    guardar_datos(datos, interim_data_path)

# Ejecutar la función principal
if __name__ == "__main__":
    main()
