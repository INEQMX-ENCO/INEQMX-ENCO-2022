import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import fcluster

# Cargar los datos
merged_municipios_df = pd.read_csv("data/external/dashboard/resultados_municipales_merged.csv")
merged_municipios_df['estado'] = merged_municipios_df['estado'].str.strip().str.upper()

# Crear un diccionario de mapeo de estados a regiones geográficas
region_mapping = {
    "AGUASCALIENTES": "Centro",
    "BAJA CALIFORNIA": "Noroeste",
    "BAJA CALIFORNIA SUR": "Noroeste",
    "CAMPECHE": "Sureste",
    "CHIAPAS": "Sureste",
    "CHIHUAHUA": "Norte",
    "COAHUILA DE ZARAGOZA": "Norte",
    "COLIMA": "Centro-Occidente",
    "DISTRITO FEDERAL": "Centro",
    "DURANGO": "Norte",
    "GUANAJUATO": "Centro",
    "GUERRERO": "Sur",
    "HIDALGO": "Centro",
    "JALISCO": "Centro-Occidente",
    "MEXICO": "Centro",
    "MICHOACAN DE OCAMPO": "Centro-Occidente",
    "MORELOS": "Centro",
    "NAYARIT": "Centro-Occidente",
    "NUEVO LEON": "Norte",
    "OAXACA": "Sur",
    "PUEBLA": "Centro",
    "QUERETARO DE ARTEAGA": "Centro",
    "QUINTANA ROO": "Sureste",
    "SAN LUIS POTOSI": "Centro",
    "SINALOA": "Noroeste",
    "SONORA": "Noroeste",
    "TABASCO": "Sureste",
    "TAMAULIPAS": "Norte",
    "TLAXCALA": "Centro",
    "VERACRUZ DE IGNACIO DE LA LLAVE": "Sureste",
    "YUCATAN": "Sureste",
    "ZACATECAS": "Norte"
}

# Agregar la columna 'region' al DataFrame basado en el estado
merged_municipios_df['Region'] = merged_municipios_df['estado'].map(region_mapping)

print(merged_municipios_df.columns)

# Define columns to use for clustering
clustering_columns = [
    "Percepcion_Economica_Personal_Positiva", "Percepcion_Economica_Personal_Negativa", "Percepcion_Naciona_Positiva",
    "Percepcion_Nacional_Negativa", "Consumo_Ahorro_Positivo", "Consumo_Ahorro_Negativo", "Incertidumbre_Economica_Personal",
    "Incertidumbre_Economica_Nacional", "gini", "ingreso_promedio_total"
] + [f"decil_{i}" for i in range(1, 11)]

merged_municipios_df[clustering_columns] = merged_municipios_df[clustering_columns].fillna(0)

# Standardize the data
scaler = StandardScaler()
clustering_data_scaled = scaler.fit_transform(merged_municipios_df[clustering_columns])

# Perform hierarchical clustering
linkage_matrix = linkage(clustering_data_scaled, method='ward')

# Prepare labels for the dendrogram
valid_indices = merged_municipios_df.dropna(subset=clustering_columns).index
labels = merged_municipios_df.loc[valid_indices, "estado"].astype(str).values

# Plot the dendrogram
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix, labels=labels, leaf_rotation=90, leaf_font_size=8)
plt.title("Dendrogram of Hierarchical Clustering (Municipios)")
plt.xlabel("Estados")
plt.ylabel("Euclidean Distance")
plt.show()

# Define a threshold for the number of clusters or distance
max_distance = 30  # You can adjust this value to get the desired number of clusters

# Assign cluster labels based on the linkage matrix
cluster_labels = fcluster(linkage_matrix, t=max_distance, criterion='distance')

# Add cluster labels to the original DataFrame
municipios_clustered = merged_municipios_df.copy()
municipios_clustered['Cluster'] = None
municipios_clustered.loc[valid_indices, 'Cluster'] = cluster_labels
# Select only numeric columns for cluster summary
numeric_columns = municipios_clustered.select_dtypes(include=['number']).columns

# Calculate the summary statistics only for numeric columns
cluster_summary_municipios = municipios_clustered.groupby('Cluster')[numeric_columns].mean()

municipios_clustered.to_csv('data/external/dashboard/cluster/resultados_municipales_cluster.csv', index=True)
cluster_summary_municipios.to_csv('data/external/dashboard/cluster/summary_municipales_cluster.csv', index=True)
#print(cluster_summary_estados.head)
#print(estados_clustered.head)