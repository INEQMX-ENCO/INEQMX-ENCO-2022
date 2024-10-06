import requests
import csv
import os

def obtener_datos_inegi(id_indicador, area_geografica="00", recientes="false", idioma="es", fuente_datos="BISE", version="2.0", formato="json", token="YOUR_TOKEN_HERE"):
    recientes_str = "true" if recientes else "false"
    url = f"https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{id_indicador}/{idioma}/{area_geografica}/{recientes_str}/{fuente_datos}/{version}/{token}?type={formato}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Error en la solicitud: {err}")
    return None

def obtener_datos_todos_indicadores_por_estado(estado, token):
    id_indicadores = "6207048662,6207048663,6207048664,6207048665,6207048666,6207048667,6207048668,6207048669,6207048670,6207048671"
    
    datos = obtener_datos_inegi(id_indicadores, area_geografica=estado, token=token)
    
    if datos is None:
        print(f"No se pudieron obtener datos para el estado {estado}")
        return []
    
    return datos.get("Series", [])

def guardar_datos_en_csv(datos, archivo_salida):
    columnas = ["ESTADO", "INDICADOR", "PERIODO", "VALOR", "UNIDAD", "CLAVE_GEOGRAFICA"]
    
    try:
        with open(archivo_salida, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columnas)
            
            for serie in datos:
                indicador = serie.get("INDICADOR")
                unidad = serie.get("UNIT")
                area_geografica = serie.get("OBSERVATIONS", [{}])[0].get("COBER_GEO", "N/A")
                
                for observacion in serie.get("OBSERVATIONS", []):
                    periodo = observacion.get("TIME_PERIOD")
                    valor = observacion.get("OBS_VALUE")
                    writer.writerow([area_geografica, indicador, periodo, valor, unidad, area_geografica])
        
        print(f"Datos guardados correctamente en {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo CSV: {e}")

if __name__ == "__main__":
    # Claves de los estados con dos dígitos
    estados = [f"{i:02d}00" for i in range(1, 33)]  # Genera claves de 01 a 32
    token = "TU TOKEN AQUI"
    archivo_salida = os.path.join("data", "raw", "enigh", "api", "enigh_api.csv")
    
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
    
    with open(archivo_salida, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        columnas = ["ESTADO", "INDICADOR", "PERIODO", "VALOR", "UNIDAD", "CLAVE_GEOGRAFICA"]
        writer.writerow(columnas)
        
        for estado in estados:
            print(f"Obteniendo datos para el estado {estado}...")
            datos_estado = obtener_datos_todos_indicadores_por_estado(estado, token)
            
            if not datos_estado:
                print(f"No se recibieron datos para el estado {estado}")
                continue
            
            for serie in datos_estado:
                indicador = serie.get("INDICADOR")
                unidad = serie.get("UNIT")
                area_geografica = serie.get("OBSERVATIONS", [{}])[0].get("COBER_GEO", "N/A")
                
                for observacion in serie.get("OBSERVATIONS", []):
                    periodo = observacion.get("TIME_PERIOD")
                    valor = observacion.get("OBS_VALUE")
                    writer.writerow([estado, indicador, periodo, valor, unidad, area_geografica])
    
    print(f"Datos de todos los estados guardados en '{archivo_salida}'")
