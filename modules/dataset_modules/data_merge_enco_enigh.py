import pandas as pd
import numpy as np

# Carga del archivo CSV
df_enigh = pd.read_csv("data/processed/enigh/enigh_processed_tidy.csv")

# Define el mapeo de códigos de estado a nombres de estado
estados = {
    1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR', 4: 'CAMPECHE',
    5: 'COAHUILA DE ZARAGOZA', 6: 'COLIMA', 7: 'CHIAPAS', 8: 'CHIHUAHUA', 9: 'DISTRITO FEDERAL',
    10: 'DURANGO', 11: 'GUANAJUATO', 12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
    16: 'MICHOACAN DE OCAMPO', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON', 20: 'OAXACA',
    21: 'PUEBLA', 22: 'QUERETARO DE ARTEAGA', 23: 'QUINTANA ROO', 24: 'SAN LUIS POTOSI', 25: 'SINALOA',
    26: 'SONORA', 27: 'TABASCO', 28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ DE IGNACIO DE LA LLAVE',
    31: 'YUCATAN', 32: 'ZACATECAS', 33: 'ENTIDAD FEDERATIVA NO ESPECIFICADA'
}

# Mapear los códigos de estado a nombres
df_enigh['estado_nombre'] = df_enigh['entidad'].map(estados)

# Modificar la función calcular_gini_y_deciles para retornar los deciles en columnas
def calcular_gini_y_deciles_modificado(df, year):
    # Filtrar datos para el año especificado
    grupo = df[df['year'] == year].copy()

    # Calcular el total de hogares
    total_hogares = grupo['factor'].sum()
    if total_hogares == 0:
        return None  # Retornar None si no hay hogares

    # Ordenar el grupo por ingreso y calcular el tamaño del decil
    grupo = grupo.sort_values(by='ing_cor').reset_index(drop=True)
    tam_dec = int(total_hogares // 10)

    # Sumar acumulativamente el factor para dividir en deciles
    grupo['ACUMULA'] = grupo['factor'].cumsum()
    grupo['DECIL'] = pd.cut(grupo['ACUMULA'], bins=[0] + [tam_dec * i for i in range(1, 11)], labels=range(1, 11), include_lowest=True)

    # Calcular el ingreso promedio y el número de hogares por decil, solo si el factor > 0
    ingresos_por_decil = grupo.groupby('DECIL', observed=True).apply(
        lambda x: np.average(x['ing_cor'], weights=x['factor']) if x['factor'].sum() > 0 else 0,
        include_groups=False
    )
    hogares_por_decil = grupo.groupby('DECIL', observed=True)['factor'].sum()

    # Crear tabla de deciles similar a la usada en INEGI
    tabla_deciles = pd.DataFrame({
        'hogares': hogares_por_decil,
        'ingreso_promedio': ingresos_por_decil
    }).reset_index()

    # Calcular el Gini usando ingresos promedio por decil ponderados por el número de hogares
    ingresos = tabla_deciles['ingreso_promedio'].values
    hogares = tabla_deciles['hogares'].values
    ingresos_totales = ingresos.dot(hogares)
    hogares_totales = hogares.sum()

    # Calcular la fracción acumulada de ingresos y hogares para el Gini
    ingresos_acumulados = np.cumsum(ingresos * hogares) / ingresos_totales
    hogares_acumulados = np.cumsum(hogares) / hogares_totales

    # Calcular el área entre la curva de Lorenz y la línea de igualdad perfecta (Gini)
    gini = 1 - np.sum((hogares_acumulados[1:] - hogares_acumulados[:-1]) * (ingresos_acumulados[1:] + ingresos_acumulados[:-1]))

    # Formatear el resultado para incluir deciles como columnas separadas
    resultado = {
        'year': year,
        'gini': gini
    }
    for i, ingreso in enumerate(ingresos, start=1):
        resultado[f'decil_{i}'] = ingreso

    return resultado

# Calcular los resultados Nacionales para 2018, 2020 y 2022 con el formato actualizado
resultados_nacionales = []
for year in [2018, 2020, 2022]:
    resultado = calcular_gini_y_deciles_modificado(df_enigh, year)
    if resultado:
        resultados_nacionales.append(resultado)

# Convertir los resultados a un DataFrame para visualización
df_resultados_nacionales= pd.DataFrame(resultados_nacionales)

# Ordenar el DataFrame por año para asegurar secuencia correcta
df_resultados_nacionales = df_resultados_nacionales.sort_values(by='year').reset_index(drop=True)

# Agregar una columna con los ingresos promedio (promedio de todos los deciles)
df_resultados_nacionales['ingreso_promedio_total'] = df_resultados_nacionales[
    [f'decil_{i}' for i in range(1, 11)]
].mean(axis=1)

# Guardar el DataFrame en un archivo CSV
path_resultado_enigh_nacionales = 'data/external/resultados_nacionales_enigh.csv'
df_resultados_nacionales.to_csv(path_resultado_enigh_nacionales, index=False)

# Modificar la función para calcular Gini y deciles por estado con deciles en columnas y columna de ingresos promedio
def calcular_gini_y_deciles_por_estado_modificado(df):
    # Lista para almacenar los resultados por estado y año
    resultados = []

    # Agrupamos por 'year' y 'entidad' (estado)
    for (year, entidad), grupo in df.groupby(['year', 'entidad']):
        # Calcular el total de hogares en el grupo
        total_hogares = grupo['factor'].sum()
        if total_hogares == 0:
            continue  # Omitir el grupo si no hay hogares

        # Ordenar el grupo por ingreso y calcular el tamaño del decil
        grupo = grupo.sort_values(by='ing_cor').reset_index(drop=True)
        tam_dec = int(total_hogares // 10)  # Tamaño del decil truncado

        # Sumar acumulativamente el factor para dividir en deciles
        grupo['ACUMULA'] = grupo['factor'].cumsum()
        grupo['DECIL'] = pd.cut(grupo['ACUMULA'], bins=[0] + [tam_dec * i for i in range(1, 11)], labels=range(1, 11), include_lowest=True)

        # Calcular el ingreso promedio y el número de hogares por decil, solo si el factor > 0
        ingresos_por_decil = grupo.groupby('DECIL', observed=True).apply(
            lambda x: np.average(x['ing_cor'], weights=x['factor']) if x['factor'].sum() > 0 else 0,
            include_groups=False
        )
        hogares_por_decil = grupo.groupby('DECIL', observed=True)['factor'].sum()

        # Crear tabla de deciles para calcular el Gini
        tabla_deciles = pd.DataFrame({
            'hogares': hogares_por_decil,
            'ingreso_promedio': ingresos_por_decil
        }).reset_index()

        # Calcular el Gini usando ingresos promedio por decil ponderados por el número de hogares
        ingresos = tabla_deciles['ingreso_promedio'].values
        hogares = tabla_deciles['hogares'].values
        ingresos_totales = ingresos.dot(hogares)
        hogares_totales = hogares.sum()

        # Calcular la fracción acumulada de ingresos y hogares para el Gini
        ingresos_acumulados = np.cumsum(ingresos * hogares) / ingresos_totales
        hogares_acumulados = np.cumsum(hogares) / hogares_totales

        # Calcular el área entre la curva de Lorenz y la línea de igualdad perfecta (Gini)
        gini = 1 - np.sum((hogares_acumulados[1:] - hogares_acumulados[:-1]) * (ingresos_acumulados[1:] + ingresos_acumulados[:-1]))

        # Preparar el resultado en el formato deseado
        resultado = {
            'year': year,
            'estado': grupo['estado_nombre'].iloc[0],
            'entidad': entidad,
            'gini': gini
        }
        for i, ingreso in enumerate(ingresos, start=1):
            resultado[f'decil_{i}'] = ingreso
        
        # Calcular el ingreso promedio total y agregarlo
        resultado['ingreso_promedio_total'] = ingresos.mean()

        # Agregar el resultado a la lista
        resultados.append(resultado)

    # Convertir los resultados a un DataFrame para facilitar la visualización
    df_resultados = pd.DataFrame(resultados)
    return df_resultados

# Calcular los resultados por estado
df_resultados_por_estado = calcular_gini_y_deciles_por_estado_modificado(df_enigh)

# Convertir los resultados a un DataFrame para visualización
df_resultados_estatales= pd.DataFrame(df_resultados_por_estado)

# Ordenar el DataFrame por año para asegurar secuencia correcta
df_resultados_estatales = df_resultados_estatales.sort_values(by=['estado','year']).reset_index(drop=True)

# Guardar el DataFrame en un archivo CSV
path_resultado_enigh_estatales = 'data/external/resultados_estatales_enigh.csv'
df_resultados_estatales.to_csv(path_resultado_enigh_estatales, index=False)

# Modificar la función para calcular Gini y deciles por municipio con deciles en columnas y una columna de ingresos promedio
def calcular_gini_y_deciles_por_municipio_corregido(df):
    resultados = []

    # Agrupamos por 'year', 'entidad', y 'municipio'
    for (year, entidad, municipio), grupo in df.groupby(['year', 'entidad', 'municipio'], observed=True):
        # Calcular el total de hogares en el grupo
        total_hogares = grupo['factor'].sum()
        if total_hogares == 0 or len(grupo) < 10:
            # Omitir el grupo si no hay hogares o si no hay suficientes datos para dividir en deciles
            continue

        # Ordenar el grupo por ingreso
        grupo = grupo.sort_values(by='ing_cor').reset_index(drop=True)
        
        # Ajustar el tamaño del decil dinámicamente para cubrir todos los hogares
        tam_dec = total_hogares / 10

        # Sumar acumulativamente el factor para dividir en deciles
        grupo['ACUMULA'] = grupo['factor'].cumsum()
        grupo['DECIL'] = pd.cut(
            grupo['ACUMULA'],
            bins=[0] + [tam_dec * i for i in range(1, 11)],
            labels=range(1, 11),
            include_lowest=True
        )

        # Calcular el ingreso promedio y el número de hogares por decil, solo si el factor > 0
        ingresos_por_decil = grupo.groupby('DECIL', observed=True).apply(
            lambda x: np.average(x['ing_cor'], weights=x['factor']) if x['factor'].sum() > 0 else 0,
            include_groups=False
        )
        hogares_por_decil = grupo.groupby('DECIL', observed=True)['factor'].sum()

        # Crear tabla de deciles para calcular el Gini
        tabla_deciles = pd.DataFrame({
            'hogares': hogares_por_decil,
            'ingreso_promedio': ingresos_por_decil
        }).reset_index()

        # Calcular el Gini usando ingresos promedio por decil ponderados por el número de hogares
        ingresos = tabla_deciles['ingreso_promedio'].values
        hogares = tabla_deciles['hogares'].values
        ingresos_totales = ingresos.dot(hogares)
        hogares_totales = hogares.sum()

        # Verificar si los ingresos totales son válidos
        if ingresos_totales == 0:
            continue

        # Calcular la fracción acumulada de ingresos y hogares para el Gini
        ingresos_acumulados = np.cumsum(ingresos * hogares) / ingresos_totales
        hogares_acumulados = np.cumsum(hogares) / hogares_totales

        # Calcular el área entre la curva de Lorenz y la línea de igualdad perfecta (Gini)
        gini = 1 - np.sum((hogares_acumulados[1:] - hogares_acumulados[:-1]) * (ingresos_acumulados[1:] + ingresos_acumulados[:-1]))

        # Preparar el resultado en el formato deseado
        resultado = {
            'year': year,
            'estado': grupo['estado_nombre'].iloc[0],
            'entidad': entidad,
            'municipio': municipio,
            'gini': gini
        }
        for i, ingreso in enumerate(ingresos, start=1):
            resultado[f'decil_{i}'] = ingreso

        # Calcular el ingreso promedio total y agregarlo
        resultado['ingreso_promedio_total'] = ingresos.mean()

        # Agregar el resultado a la lista
        resultados.append(resultado)

    # Convertir los resultados a un DataFrame para facilitar la visualización
    df_resultados = pd.DataFrame(resultados)
    return df_resultados

# Calcular los resultados por municipio
df_resultados_por_municipio = calcular_gini_y_deciles_por_municipio_corregido(df_enigh)

# Convertir los resultados a un DataFrame para visualización
df_resultados_municipales= pd.DataFrame(df_resultados_por_municipio)

# Función para imputar valores faltantes en los deciles
def advanced_impute_deciles(row, deciles):
    for i, col in enumerate(deciles):
        if pd.isnull(row[col]):  # Verificar si el decil actual es NaN
            if i > 0 and pd.notnull(row[deciles[i - 1]]):  # Usar el decil anterior
                prev_value = row[deciles[i - 1]]
                row[col] = prev_value * 1.15  # Asumir un aumento del 15%
            elif i == 0 and pd.notnull(row[deciles[i + 1]]):  # Manejar decil_1 usando decil_2
                next_value = row[deciles[i + 1]]
                row[col] = next_value / 1.15  # Asumir una disminución del 15%
            elif i < len(deciles) - 1 and pd.notnull(row[deciles[i + 1]]):  # Usar el próximo decil
                next_value = row[deciles[i + 1]]
                row[col] = next_value / 1.15  # Asumir una disminución del 15%
    return row

# Lista de columnas de deciles
deciles_columns = [f'decil_{i}' for i in range(1, 11)]

# Aplicar imputación avanzada a los datos de deciles
df_resultados_municipales = df_resultados_municipales.apply(
    lambda row: advanced_impute_deciles(row, deciles_columns), axis=1
)

# Ordenar el DataFrame por año para asegurar secuencia correcta
df_resultados_municipales = df_resultados_municipales.sort_values(by=['estado', 'municipio','year']).reset_index(drop=True)

# Guardar el DataFrame en un archivo CSV
path_resultado_enigh_municipales = 'data/external/resultados_municipales_enigh.csv'
df_resultados_municipales.to_csv(path_resultado_enigh_municipales, index=False)

df_enco = pd.read_csv("data/processed/enco/enco_processed_tidy.csv",
                      dtype={"columna_6": "str"},  # Ajusta el tipo de dato esperado
    low_memory=False)

# Mapear nombres de los estados
df_enco['estado_nombre'] = df_enco['ent'].map(estados)

# Reemplazar valores nulos por 0
df_enco = df_enco.fillna(0)

# Lista de preguntas
preguntas = [f'p{i}' for i in range(1, 16)]  # P1, P2, ..., P15

# Crear un DataFrame vacío para almacenar resultados
resultados_porcentajes = pd.DataFrame()

# Calcular porcentajes por año, pregunta y respuesta
for pregunta in preguntas:
    # Agrupar por año y respuesta, calcular el porcentaje
    frecuencias = df_enco.groupby(['year', pregunta]).size() / df_enco.groupby('year').size() * 100
    frecuencias_df = frecuencias.reset_index()
    frecuencias_df.columns = ['Año', 'Respuesta', 'Porcentaje']
    frecuencias_df['Pregunta'] = pregunta

    # Agregar al DataFrame general
    resultados_porcentajes = pd.concat([resultados_porcentajes, frecuencias_df], ignore_index=True)

# Reorganizar las columnas
resultados_porcentajes = resultados_porcentajes[['Pregunta', 'Año', 'Respuesta', 'Porcentaje']]

# Guardar el DataFrame en un archivo CSV
path_resultado_enco_nacionales = 'data/external/resultados_nacionales_enco.csv'
resultados_porcentajes.to_csv(path_resultado_enco_nacionales, index=False)

# Crear un DataFrame vacío para almacenar resultados
resultados_estado_porcentajes = pd.DataFrame()

# Calcular porcentajes por año, estado, pregunta y respuesta
for pregunta in preguntas:
    # Agrupar por año, estado y respuesta, calcular el porcentaje
    frecuencias_estados = df_enco.groupby(['year', 'estado_nombre', pregunta]).size() / df_enco.groupby(['year', 'estado_nombre']).size() * 100
    frecuencias_estados_df = frecuencias_estados.reset_index()
    frecuencias_estados_df.columns = ['Año', 'Estado', 'Respuesta', 'Porcentaje']
    frecuencias_estados_df['Pregunta'] = pregunta

    # Agregar al DataFrame general
    resultados_estado_porcentajes = pd.concat([resultados_estado_porcentajes, frecuencias_estados_df], ignore_index=True)

# Reorganizar las columnas
resultados_estado_porcentajes = resultados_estado_porcentajes[['Pregunta', 'Año', 'Estado', 'Respuesta', 'Porcentaje']]

# Guardar el DataFrame en un archivo CSV
path_resultado_enco_estatales = 'data/external/resultados_estatales_enco.csv'
resultados_estado_porcentajes.to_csv(path_resultado_enco_estatales, index=False)

# Crear un DataFrame vacío para almacenar resultados
resultados_municipio_porcentajes = pd.DataFrame()

# Calcular porcentajes por estado, municipio, pregunta y respuesta
for pregunta in preguntas:
    # Agrupar por estado, municipio y respuesta, calcular el porcentaje
    frecuencias_municipios = df_enco.groupby(['year', 'estado_nombre', 'mpio', pregunta]).size() / df_enco.groupby(['year','estado_nombre', 'mpio']).size() * 100
    frecuencias_municipios_df = frecuencias_municipios.reset_index()
    frecuencias_municipios_df.columns = ['Año', 'Estado', 'Municipio', 'Respuesta', 'Porcentaje']
    frecuencias_municipios_df['Pregunta'] = pregunta

    # Agregar al DataFrame general
    resultados_municipio_porcentajes = pd.concat([resultados_municipio_porcentajes, frecuencias_municipios_df], ignore_index=True)

# Reorganizar las columnas
resultados_municipio_porcentajes = resultados_municipio_porcentajes[['Año', 'Pregunta', 'Estado', 'Municipio', 'Respuesta', 'Porcentaje']]

# Guardar el DataFrame en un archivo CSV
path_resultado_enco_municipales = 'data/external/resultados_municipales_enco.csv'
resultados_municipio_porcentajes.to_csv(path_resultado_enco_municipales, index=False)


resultados_nacionales_enigh = pd.read_csv('data/external/resultados_nacionales_enigh.csv')
resultados_estatales_enigh = pd.read_csv('data/external/resultados_estatales_enigh.csv')
resultados_municipales_enigh = pd.read_csv('data/external/resultados_municipales_enigh.csv')
resultados_nacionales_enco = pd.read_csv('data/external/resultados_nacionales_enco.csv')
resultados_estatales_enco = pd.read_csv('data/external/resultados_estatales_enco.csv')
resultados_municipales_enco = pd.read_csv('data/external/resultados_municipales_enco.csv')

# Agregar una columna de categoría basada en el mapeo proporcionado
categorias = {
    "Percepcion_Economica_Personal_Positiva": [
        'p1_Respuesta_1', 'p1_Respuesta_2', 'p1_Respuesta_3',
        'p2_Respuesta_1', 'p2_Respuesta_2', 'p2_Respuesta_3',
        'p3_Respuesta_1', 'p3_Respuesta_2', 'p3_Respuesta_3',
        'p4_Respuesta_1', 'p4_Respuesta_2', 'p4_Respuesta_3'
    ],
    "Percepcion_Economica_Personal_Negativa": [
        'p1_Respuesta_4', 'p1_Respuesta_5',
        'p2_Respuesta_4', 'p2_Respuesta_5',
        'p3_Respuesta_4', 'p3_Respuesta_5',
        'p4_Respuesta_4', 'p4_Respuesta_5'
    ],
    "Percepcion_Naciona_Positiva": [
        'p5_Respuesta_1', 'p5_Respuesta_2', 'p5_Respuesta_3',
        'p6_Respuesta_1', 'p6_Respuesta_2', 'p6_Respuesta_3',
        'p12_Respuesta_1', 'p12_Respuesta_2', 'p12_Respuesta_3',
        'p13_Respuesta_1', 'p13_Respuesta_2', 'p13_Respuesta_3'
    ],
    "Percepcion_Nacional_Negativa": [
        'p5_Respuesta_4', 'p5_Respuesta_5',
        'p6_Respuesta_4', 'p6_Respuesta_5',
        'p12_Respuesta_4', 'p12_Respuesta_5',
        'p13_Respuesta_4', 'p13_Respuesta_5'
    ],
    "Consumo_Ahorro_Positivo": [
        'p7_Respuesta_1', 'p7_Respuesta_2',
        'p8_Respuesta_1', 'p8_Respuesta_2',
        'p9_Respuesta_1',
        'p10_Respuesta_1',
        'p11_Respuesta_1', 'p11_Respuesta_2', 'p11_Respuesta_3',
        'p14_Respuesta_1', 'p14_Respuesta_2',
        'p15_Respuesta_1', 'p15_Respuesta_2'
    ],
    "Consumo_Ahorro_Negativo": [
        'p7_Respuesta_3',
        'p8_Respuesta_3',
        'p9_Respuesta_2',
        'p10_Respuesta_2', 'p10_Respuesta_4',
        'p11_Respuesta_4', 'p11_Respuesta_5',
        'p14_Respuesta_3',
        'p15_Respuesta_4'
    ],
    "Incertidumbre_Economica_Personal": [
        'p1_Respuesta_6', 'p2_Respuesta_6', 'p3_Respuesta_6', 'p4_Respuesta_6', 'p7_Respuesta_4',
        'p8_Respuesta_4', 'p9_Respuesta_3', 'p10_Respuesta_3', 'p11_Respuesta_6', 'p14_Respuesta_4', 'p15_Respuesta_4'
    ],
    "Incertidumbre_Economica_Nacional": [
        'p5_Respuesta_6', 'p6_Respuesta_6', 'p12_Respuesta_7', 'p13_Respuesta_6'
    ]
}

# Merge nacionales
merged_data_nacional = pd.merge(
    resultados_nacionales_enigh,
    resultados_nacionales_enco,
    left_on=['year'],
    right_on=['Año'],
    how='inner'
)

# Pivotear el DataFrame para que 'Pregunta' y 'Respuesta' sean columnas y 'Porcentaje' sean valores
merged_data_nacional = merged_data_nacional.pivot_table(
    index=['year', 'gini'] + [f'decil_{i}' for i in range(1, 11)],
    columns=['Pregunta', 'Respuesta'],
    values='Porcentaje'
)

# Aplanar las columnas de múltiples niveles
merged_data_nacional.columns = [f'{col[0]}_Respuesta_{col[1]}' for col in merged_data_nacional.columns]
merged_data_nacional.reset_index(inplace=True)

# Asegurar que el DataFrame tenga las columnas necesarias
if {'year'}.issubset(merged_data_nacional.columns):
    # Ordenar las columnas para que Año, Estado, y Municipio estén al inicio
    columnas_ordenadas = ['year'] + [
        col for col in merged_data_nacional.columns if col not in {'year'}
    ]

    # Reorganizar el DataFrame
    merged_data_nacional = merged_data_nacional[columnas_ordenadas]

# Crear un nuevo DataFrame para la categorización
merged_data_nacional = merged_data_nacional.copy()
for category, questions in categorias.items():
    merged_data_nacional[category] = merged_data_nacional[questions].mean(axis=1, skipna=True)

merged_data_nacional.to_csv('data/external/dashboard/resultados_nacionales_merged.csv', index=False)

# Fusionar datos estatales
merged_data_estados = pd.merge(
    resultados_estatales_enigh,
    resultados_estatales_enco,
    left_on=['estado', 'year'],
    right_on=['Estado', 'Año'],
    how='inner'
)

# Resto del código sigue la misma lógica...
merged_data_estados = merged_data_estados.pivot_table(
    index=['year','estado', 'gini'] + [f'decil_{i}' for i in range(1, 11)],
    columns=['Pregunta', 'Respuesta'],
    values='Porcentaje'
)

merged_data_estados.columns = [f'{col[0]}_Respuesta_{col[1]}' for col in merged_data_estados.columns]
merged_data_estados.reset_index(inplace=True)

# Asegurar que el DataFrame tenga las columnas necesarias
if {'estado'}.issubset(merged_data_estados.columns):
    # Ordenar las columnas para que Año, Estado, y Municipio estén al inicio
    columnas_ordenadas = ['year', 'estado'] + [
        col for col in merged_data_estados.columns if col not in {'Año'}
    ]

    # Reorganizar el DataFrame
    merged_data_estados = merged_data_estados[columnas_ordenadas]

merged_data_estados = merged_data_estados.copy()
for category, questions in categorias.items():
    merged_data_estados[category] = merged_data_estados[questions].mean(axis=1, skipna=True)

if 'year' in merged_data_estados.columns:
    # Verificar si hay más de una columna 'year'
    year_columns = [col for col in merged_data_estados.columns if col == 'year']
    if len(year_columns) > 1:
        # Eliminar la segunda columna duplicada
        merged_data_estados = merged_data_estados.loc[:, ~merged_data_estados.columns.duplicated()]

merged_data_estados.to_csv('data/external/dashboard/resultados_estatales_merged.csv', index=False)

# Merge municipales
merged_data_municipios = pd.merge(
    resultados_municipales_enigh,
    resultados_municipales_enco,
    left_on=['estado','municipio', 'year'],
    right_on=['Estado','Municipio', 'Año'],
    how='inner'
)

municipios = {
    "AGUASCALIENTES": [("Aguascalientes", 1), ("Jesús María", 5)],
    "BAJA CALIFORNIA": [("Tijuana", 4)],
    "BAJA CALIFORNIA SUR": [("La Paz", 3)],
    "CAMPECHE": [("Campeche", 2)],
    "CHIAPAS": [("Chiapa de Corzo", 27), ("Tuxtla Gutiérrez", 101)],
    "CHIHUAHUA": [("Chihuahua", 19)],
    "COAHUILA DE ZARAGOZA": [("Municipio 027", 27), ("Municipio 030", 30)],
    "COLIMA": [("Colima", 2), ("Villa de Álvarez", 10)],
    "DISTRITO FEDERAL": [
        ("Azcapotzalco", 2), ("Coyoacán", 3), ("Cuajimalpa de Morelos", 4),
        ("Gustavo A. Madero", 5), ("Iztacalco", 6), ("Iztapalapa", 7),
        ("La Magdalena Contreras", 8), ("Milpa Alta", 9), ("Álvaro Obregón", 10),
        ("Tláhuac", 11), ("Tlalpan", 12), ("Xochimilco", 13), ("Benito Juárez", 14),
        ("Cuauhtémoc", 15), ("Miguel Hidalgo", 16), ("Venustiano Carranza", 17)
    ],
    "DURANGO": [("Durango", 5)],
    "GUANAJUATO": [("León", 20), ("Purísima del Rincón", 25), ("San Francisco del Rincón", 31)],
    "GUERRERO": [("Acapulco de Juárez", 1)],
    "HIDALGO": [("Pachuca de Soto", 48), ("Mineral de la Reforma", 51)],
    "JALISCO": [
        ("Guadalajara", 39), ("El Salto", 70), ("Tlajomulco de Zúñiga", 97),
        ("San Pedro Tlaquepaque", 98), ("Tonalá", 101), ("Zapopan", 120)
    ],
    "MEXICO": [
        ("Acolman", 2), ("Atenco", 11), ("Atizapán de Zaragoza", 13), ("Calimaya", 18),
        ("Coacalco de Berriozábal", 20), ("Coyotepec", 23), ("Cuautitlán", 24),
        ("Chalco", 25), ("Chicoloapan", 29), ("Chimalhuacán", 31),
        ("Ecatepec de Morelos", 33), ("Huixquilucan", 37), ("Ixtapaluca", 39),
        ("Lerma", 51), ("Metepec", 54), ("Naucalpan de Juárez", 57),
        ("Nezahualcóyotl", 58), ("Nicolás Romero", 60), ("La Paz", 70),
        ("San Mateo Atenco", 76), ("Tecámac", 81), ("Teoloyucan", 91),
        ("Texcoco", 99), ("Tlalnepantla de Baz", 104), ("Toluca", 106),
        ("Tultitlán", 109), ("Zinacantepec", 118), ("Zumpango", 120),
        ("Cuautitlán Izcalli", 121), ("Valle de Chalco Solidaridad", 122),
        ("Almoloya de Juárez", 5), ("Melchor Ocampo", 53), ("Tultepec", 108)
    ],
    "MICHOACAN DE OCAMPO": [("Morelia", 53), ("Sunuapa", 88)],
    "MORELOS": [
        ("Cuernavaca", 7), ("Emiliano Zapata", 8), ("Jiutepec", 11), ("Temixco", 18),
        ("Xochitepec", 28), ("Yautepec", 29)
    ],
    "NAYARIT": [("Xalisco", 8), ("Tepic", 17)],
    "NUEVO LEON": [
        ("Apodaca", 6), ("García", 18), ("San Pedro Garza García", 19),
        ("General Escobedo", 21), ("Guadalupe", 26), ("Juárez", 31),
        ("Monterrey", 39), ("San Nicolás de los Garza", 46), ("Santa Catarina", 48),
        ("Santiago", 49)
    ],
    "OAXACA": [
        ("Oaxaca de Juárez", 67), ("Santa Cruz Xoxocotlán", 385), ("Santa María Atzompa", 399),
        ("San Agustín de las Juntas", 83), ("San Pablo Etla", 293),
        ("Santa Lucía del Camino", 390), ("San Antonio de la Cal", 107)
    ],
    "PUEBLA": [
        ("Amozoc", 15), ("Cuautlancingo", 41), ("Puebla", 114), ("San Pedro Cholula", 140),
        ("Coronango", 34), ("San Andrés Cholula", 119), ("San Miguel Xoxtla", 136)
    ],
    "QUERETARO DE ARTEAGA": [("Corregidora", 6), ("Querétaro", 14), ("El Marqués", 11)],
    "QUINTANA ROO": [("Benito Juárez", 5), ("Isla Mujeres", 3)],
    "SAN LUIS POTOSI": [("San Luis Potosí", 28), ("Soledad de Graciano Sánchez", 35)],
    "SINALOA": [("Culiacán", 6)],
    "SONORA": [("Hermosillo", 30)],
    "TABASCO": [("Centro", 4), ("Nacajuca", 13)],
    "TAMAULIPAS": [("Altamira", 3), ("Ciudad Madero", 9), ("Tampico", 38)],
    "TLAXCALA": [
        ("Apizaco", 5), ("Chiautempan", 10), ("Mazatecochco de José María Morelos", 17),
        ("Contla de Juan Cuamatzi", 18), ("Panotla", 24), ("Santa Cruz Tlaxcala", 26),
        ("Tenancingo", 27), ("Teolocholco", 28), ("Tetla de la Solidaridad", 31),
        ("Tlaxcala", 33), ("Tzompantepec", 38), ("Papalotla de Xicohténcatl", 41),
        ("Yauhquemehcan", 43), ("Zacatelco", 44), ("La Magdalena Tlaltelulco", 48),
        ("San Francisco Tetlanohcan", 50), ("San Jerónimo Zacualpan", 51),
        ("Santa Catarina Ayometla", 58), ("Apetatitlán de Antonio Carvajal", 2),
        ("Natívitas", 23), ("San Pablo del Monte", 25), ("Tocatlán", 35),
        ("Xaltocan", 40), ("San Damián Texóloc", 49), ("San Juan Huactzinco", 53)
    ],
    "VERACRUZ DE IGNACIO DE LA LLAVE": [
        ("Boca del Río", 28), ("Pánuco", 123), ("Pueblo Viejo", 133), ("Veracruz", 193)
    ],
    "YUCATAN": [("Kanasín", 41), ("Mérida", 50), ("Progreso", 59), ("Umán", 101)],
    "ZACATECAS": [("Guadalupe", 17), ("Zacatecas", 56)]
}

# Crear un mapeo completo estado -> {municipio_codigo: municipio_nombre}
mapeo_municipios = {}
for estado, mun_list in municipios.items():
    mapeo_municipios[estado] = {codigo: nombre for nombre, codigo in mun_list}

# Crear una función para obtener el nombre del municipio
def obtener_nombre_municipio(estado, codigo_municipio):
    try:
        return mapeo_municipios[estado].get(codigo_municipio, "Desconocido")
    except KeyError:
        return "Desconocido"

# Agregar una nueva columna con el nombre del municipio
merged_data_municipios['nombre_municipio'] = merged_data_municipios.apply(lambda x: obtener_nombre_municipio(x['estado'], x['municipio']), axis=1)

merged_data_municipios = merged_data_municipios.pivot_table(
    index=['year','estado', 'municipio', 'nombre_municipio', 'gini'] + [f'decil_{i}' for i in range(1, 11)],
    columns=['Pregunta', 'Respuesta'],
    values='Porcentaje'
)

merged_data_municipios.columns = [f'{col[0]}_Respuesta_{col[1]}' for col in merged_data_municipios.columns]
merged_data_municipios.reset_index(inplace=True)

if {'municipio'}.issubset(merged_data_municipios.columns):
    # Ordenar las columnas para que Año, Estado, y Municipio estén al inicio
    columnas_ordenadas = ['year', 'estado', 'nombre_municipio', 'municipio'] + [
        col for col in merged_data_municipios.columns if col not in {'Año'}
    ]

    # Reorganizar el DataFrame
    merged_data_municipios = merged_data_municipios[columnas_ordenadas]

merged_data_municipios = merged_data_municipios.copy()
for category, questions in categorias.items():
    merged_data_municipios[category] = merged_data_municipios[questions].mean(axis=1, skipna=True)

# Eliminar una columna duplicada de 'year' si existe
if 'year' in merged_data_municipios.columns:
    # Verificar si hay más de una columna 'year'
    year_columns = [col for col in merged_data_municipios.columns if col == 'year']
    if len(year_columns) > 1:
        # Eliminar la segunda columna duplicada
        merged_data_municipios = merged_data_municipios.loc[:, ~merged_data_municipios.columns.duplicated()]

merged_data_municipios.to_csv('data/external/dashboard/resultados_municipales_merged.csv', index=False)
