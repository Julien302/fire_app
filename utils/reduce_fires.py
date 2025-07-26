import pandas as pd

# Lire le fichier CSV
file_path = 'fires_light.csv'  # Remplacez par le chemin de votre fichier
df = pd.read_csv(file_path)

# Filtre sur 20ans
df = df[df['FIRE_YEAR'] > 1994]  

# Optionnel : retirer les colonnes moins importantes
columns_to_keep = ["OBJECTID","FIRE_YEAR","STAT_CAUSE_DESCR","FIRE_SIZE","STATE","DATEGREG_DISCOVERY","DATEGREG_CONT","FIRE_NAME"]

# Échantillonnage : Garder environ 50% des données pour réduire à 20 Mo
df_sampled = df.sample(frac=0.5, random_state=1)

df_reduced = df_sampled[columns_to_keep]

# Sauvegarder dans un nouveau fichier CSV
output_file_path = 'fires_light_gh.csv'  # Remplacez par le chemin de destination souhaité
df_reduced.to_csv(output_file_path, index=False)
