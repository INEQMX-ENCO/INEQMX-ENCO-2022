# Importar librerías necesarias
import pandas as pd
import numpy as np
from scipy.stats import rankdata
from inequality.gini import Gini
from pathlib import Path

relative_path = Path(r"data\raw\enigh\conjunto_de_datos_concentradohogar_enigh2022_ns\conjunto_de_datos\conjunto_de_datos_concentradohogar_enigh2022_ns.csv")

# Get the absolute path to the CSV file
# This assumes your script is running from the 'proyecto_ic_gini_repo' directory
csv_path = relative_path.resolve()

# Cargar los datos desde el archivo CSV
Conc = pd.read_csv(csv_path)

# Selección de las variables de interés
Conc = Conc[['folioviv', 'foliohog', 'ing_cor', 'ingtrab', 'trabajo', 'negocio',
             'otros_trab', 'rentas', 'utilidad', 'arrenda', 'transfer', 'jubilacion',
             'becas', 'donativos', 'remesas', 'bene_gob', 'transf_hog', 'trans_inst',
             'estim_alqu', 'otros_ing', 'factor', 'upm', 'est_dis']]


# Crear una variable para agregar la entidad federativa tomando los dos primeros dígitos de folioviv
Conc['entidad'] = Conc['folioviv'].astype(str).str[:2]

# Definir la columna con los nombres de los deciles
Numdec = ["Total", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# Crear una bandera para numerar a los hogares
Conc['Nhog'] = 1

# Ordenar los datos según ing_cor, folioviv, foliohog
Conc = Conc.sort_values(by=['ing_cor', 'folioviv', 'foliohog'])

# Calcular el total de hogares sumando la columna 'factor'
tot_hogares = Conc['factor'].sum()

# Dividir el total de hogares entre 10 para determinar el tamaño de los deciles
tam_dec = np.trunc(tot_hogares / 10).astype(int)

# Guardar el tamaño del decil en una nueva columna
Conc['tam_dec'] = tam_dec

# Crear una copia de la tabla Conc para la creación de los deciles
BD1 = Conc.copy()

# Crear la variable MAXT con los valores de 'ing_cor'
BD1['MAXT'] = BD1['ing_cor']

# Ordenar por la variable MAXT
BD1 = BD1.sort_values(by='MAXT')

# Aplicar la suma acumulada sobre la columna 'factor'
BD1['ACUMULA'] = BD1['factor'].cumsum()

# Crear deciles de ingreso
for i in range(1, 10):
    a1 = BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1], 'factor']
    b1 = tam_dec * i - BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1], 'ACUMULA']
    BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1] + 1, 'factor'] = b1
    BD1.loc[BD1[BD1['ACUMULA'] < tam_dec * i].index[-1] + 2, 'factor'] = a1 - b1

# Nueva suma acumulada después de la división de los factores
BD1['ACUMULA2'] = BD1['factor'].cumsum()

# Inicializar la columna de Decil
BD1['DECIL'] = 0

# Asignar deciles
BD1.loc[BD1['ACUMULA2'] <= tam_dec, 'DECIL'] = 1
for i in range(1, 10):
    BD1.loc[(BD1['ACUMULA2'] > tam_dec * i) & (BD1['ACUMULA2'] <= tam_dec * (i + 1)), 'DECIL'] = i + 1

# Asignar el decil 10 a los que aún tengan 0
BD1.loc[BD1['DECIL'] == 0, 'DECIL'] = 10

# Calcular el total de hogares por decil
x = BD1.groupby('Nhog')['factor'].sum()
y = BD1.groupby('DECIL')['factor'].sum()

# Calcular el promedio de ingreso corriente total y por decil
ing_cormed_t = (BD1['factor'] * BD1['ing_cor']).groupby(BD1['Nhog']).sum() / x
ing_cormed_d = (BD1['factor'] * BD1['ing_cor']).groupby(BD1['DECIL']).sum() / y

# Guardar los resultados en un DataFrame
prom_rub = pd.DataFrame({"INGRESO CORRIENTE": np.concatenate(([ing_cormed_t.mean()], ing_cormed_d))})
prom_rub.index = Numdec

# Cálculo del GINI
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

    # Normalizar para que vayan de 0 a 1
    cum_weights_norm = cum_weights / cum_weights[-1]
    cum_income_norm = cum_income / cum_income[-1]

    # Cálculo del área bajo la curva Lorenz
    B = np.trapz(cum_income_norm, cum_weights_norm)  # Área bajo la curva
    return 1 - 2 * B

# Cálculo del Gini nacional usando ingreso corriente
deciles_hog_ingcor = pd.DataFrame({
    "hogaresxdecil": y,
    "ingreso": ing_cormed_d
})

gini_nacional = gini(deciles_hog_ingcor['ingreso'].values, deciles_hog_ingcor['hogaresxdecil'].values)

# Mostrar resultados
print("Promedio de ingreso corriente por decil:")
print(round(prom_rub))
print("\nCoeficiente de Gini:")
print(round(gini_nacional, 3))


# Asignar deciles
BD1.loc[BD1['ACUMULA2'] <= tam_dec, 'DECIL'] = 1
for i in range(1, 10):
    BD1.loc[(BD1['ACUMULA2'] > tam_dec * i) & (BD1['ACUMULA2'] <= tam_dec * (i + 1)), 'DECIL'] = i + 1

# Asignar el decil 10 a los que aún tengan 0
BD1.loc[BD1['DECIL'] == 0, 'DECIL'] = 10

# A esta altura, ya tienes la columna 'DECIL' dentro del DataFrame BD1, 
# que categoriza cada hogar según su ingreso en uno de los 10 deciles.

# Ahora puedes agregar esta columna a tu DataFrame original "Conc" 
# si deseas tener la columna 'DECIL' en el df principal.
Conc['DECIL'] = BD1['DECIL'].values  # Copiar la columna DECIL de BD1 a Conc

# Ahora, en el DataFrame Conc tendrás una nueva columna 'DECIL' 
# que categoriza cada hogar de acuerdo a su decil de ingreso.
conc_decils = Conc[['folioviv', 'foliohog', 'ing_cor', 'DECIL']]
print(conc_decils.head(-5))
print(conc_decils.info)
