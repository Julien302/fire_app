# reduce_csv.py
import pandas as pd
import os

print("📊 Réduction du fichier CSV...")
df = pd.read_csv('data/fires_light.csv')
print(f"Taille actuelle: {len(df):,} lignes")

# Taille du fichier actuel
size_mb = os.path.getsize('data/fires_light.csv') / (1024*1024)
print(f"Taille fichier: {size_mb:.1f} MB")

# Réduire à ~30k lignes (environ 30-40 MB)
df_small = df.sample(n=50000, random_state=42)

# Sauvegarder
df_small.to_csv('data/fires_light.csv', index=False)

# Vérifier nouvelle taille
new_size_mb = os.path.getsize('data/fires_light.csv') / (1024*1024)
print(f"✅ Nouvelle taille: {len(df_small):,} lignes")
print(f"✅ Nouvelle taille fichier: {new_size_mb:.1f} MB")
