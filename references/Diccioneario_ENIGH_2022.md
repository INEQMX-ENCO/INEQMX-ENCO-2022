# ENGIH Dicionario de Datos

Este diccionario de datos describe cada columna en el **CONCENTRADOHOGAR** de la encuesta ENGIH, que incluye información sobre ingresos del hogar, geografía y otras variables socioeconómicas.

| **Nombre de Columna** | **Descripción**                                                    | **Tipo** | **Detalles**                                                                                  |
|-----------------------|--------------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------|
| folioviv              | Identificador de la vivienda                                       | C (10)   | Código de vivienda única compuesto de la entidad, ámbito y número de vivienda seleccionada.   |
| foliohog              | Identificador del hogar                                            | C (1)    | Código que identifica al hogar dentro de la vivienda, el valor 1 representa al hogar principal.|
| ubica_geo             | Ubicación geográfica                                               | C (5)    | Código geográfico que incluye clave de la entidad federativa y municipio.                     |
| tam_loc               | Tamaño de localidad                                                | C (1)    | Clasificación de la localidad: 1 = >100,000 habitantes; 2 = 15,000-99,999; 3 = 2,500-14,999; 4 = <2,500.|
| est_socio             | Estrato socioeconómico                                             | C (1)    | 1 = Bajo; 2 = Medio bajo; 3 = Medio alto; 4 = Alto.                                           |
| est_dis               | Estrato de diseño muestral                                         | C (3)    | Identifica los estratos de diseño muestral, definidos en la estructura de la encuesta.        |
| upm                   | Unidad primaria de muestreo                                        | C (7)    | Código único de la Unidad Primaria de Muestreo.                                               |
| factor                | Factor de expansión                                                | N (5)    | Factor de expansión utilizado para estimar resultados poblacionales.                         |
| clase_hog             | Clase de hogar                                                     | C (1)    | 1 = Unipersonal; 2 = Nuclear; 3 = Ampliado; 4 = Compuesto; 5 = Corresidente.                  |
| sexo_jefe             | Sexo del jefe del hogar                                            | C (1)    | 1 = Hombre; 2 = Mujer.                                                                       |
| edad_jefe             | Edad del jefe del hogar                                            | N (2)    | Edad en años del jefe del hogar.                                                             |
| educa_jefe            | Nivel educativo del jefe del hogar                                 | C (2)    | 01 = Sin instrucción; 02 = Preescolar; 03 = Primaria incompleta; 04 = Primaria completa; ... |
| tot_integ             | Número total de integrantes del hogar                              | N (2)    | Total de personas que forman parte del hogar.                                                |
| hombres               | Número de hombres en el hogar                                      | N (2)    | Número de integrantes del hogar que son hombres.                                             |
| mujeres               | Número de mujeres en el hogar                                      | N (2)    | Número de integrantes del hogar que son mujeres.                                             |
| mayores               | Número de integrantes mayores de 12 años                           | N (2)    | Integrantes del hogar con más de 12 años.                                                    |
| menores               | Número de integrantes menores de 12 años                           | N (2)    | Integrantes del hogar con menos de 12 años.                                                  |
| p12_64                | Número de integrantes de 12 a 64 años                              | N (2)    | Total de integrantes con edades entre 12 y 64 años.                                          |
| p65mas                | Número de integrantes de 65 años o más                             | N (2)    | Total de integrantes con más de 65 años.                                                     |
| ocupados              | Número de ocupados                                                 | N (2)    | Total de personas que tienen trabajo.                                                        |
| percep_ing            | Perceptores de ingreso                                             | N (2)    | Total de personas que reportan ingreso en el hogar.                                          |
| perc_ocupa            | Perceptores de ingreso ocupados                                    | N (2)    | Personas con ingreso monetario y que están ocupadas.                                         |
| ing_cor               | Ingreso corriente del hogar                                        | N (12,2) | Total de ingresos del hogar, provenientes de trabajo, transferencias, rentas, etc.           |
| ingtrab               | Ingreso por trabajo                                                | N (12,2) | Ingresos derivados de trabajos subordinados o independientes.                                |
| trabajo               | Ingreso por trabajo subordinado                                    | N (12,2) | Total de sueldos, comisiones, aguinaldo, horas extras, etc.                                  |
| sueldos               | Sueldos del hogar                                                  | N (12,2) | Remuneraciones por sueldos, salarios y jornales.                                             |
| horas_extr            | Ingresos por horas extras                                           | N (12,2) | Remuneraciones obtenidas por trabajo adicional o sobretiempo.                                |
| comisiones            | Comisiones y propinas                                              | N (12,2) | Ingresos obtenidos por comisiones y propinas.                                                |
| negocio               | Ingresos por negocio propio                                        | N (12,2) | Ingresos derivados de actividades independientes o negocios propios.                         |
| noagrop               | Ingresos por negocios no agropecuarios                             | N (12,2) | Total de ingresos de negocios industriales, comerciales y de servicios.                      |
| agricolas             | Ingresos por negocios agrícolas                                    | N (12,2) | Total de ingresos derivados de actividades agrícolas.                                        |
| remesas               | Ingresos por remesas                                               | N (12,2) | Ingresos provenientes de remesas del extranjero.                                             |
| jubilacion            | Ingresos por jubilaciones                                           | N (12,2) | Total de ingresos por pensiones o jubilaciones.                                              |
| becas                 | Ingresos por becas                                                 | N (12,2) | Ingresos obtenidos por becas.                                                                |
| rentas                | Ingresos por rentas                                                | N (12,2) | Ingresos obtenidos por alquiler o arrendamiento de propiedades.                              |
| utilidades            | Ingresos por utilidades                                             | N (12,2) | Ingresos obtenidos por participación en utilidades de empresas o cooperativas.               |
| otros_ing             | Otros ingresos corrientes                                          | N (12,2) | Otros ingresos monetarios recibidos por el hogar.                                            |
| factor_expansion      | Factor de expansión                                                | N (5)    | Valor para expandir los resultados a la población total.                                      |

## Notas:
- **Tipo C (Categorical)**: Variable categórica, codificada con números o códigos.
- **Tipo N (Numeric)**: Variable numérica con decimales que indican el número de dígitos después del punto decimal.
