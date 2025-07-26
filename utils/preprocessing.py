# preprocessing.py
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple

file_path = 'data/fires_light_gh.csv'

def load_state_names() -> Dict[str, str]:
    """Charge la correspondance entre codes et noms d'états"""
    state_df = pd.read_csv('data/state_names.csv')
    return dict(zip(state_df['Alpha code'], state_df['State']))


def calculate_duration(discovery_date, cont_date):
    """Calcule la durée en jours entre découverte et contrôle"""
    if pd.isna(discovery_date) or pd.isna(cont_date):
        return None
    return (cont_date - discovery_date).days

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applique tous les traitements nécessaires aux données brutes"""
   
    #Conversion acre km²
    # 1 acre = 0.00404686 km²
    df['FIRE_SIZE_KM2'] = df['FIRE_SIZE'] * 0.00404686
    # Arrondir à 4 décimales pour une précision correcte
    df['FIRE_SIZE_KM2'] = df['FIRE_SIZE_KM2'].round(4)

    # Conversion des colonnes de date
    df['DATEGREG_DISCOVERY'] = pd.to_datetime(df['DATEGREG_DISCOVERY'], errors='coerce')
    df['DATEGREG_CONT'] = pd.to_datetime(df['DATEGREG_CONT'], errors='coerce')
    
    # Calcul de la durée des incendies
    if all(col in df.columns for col in ['DATEGREG_DISCOVERY', 'DATEGREG_CONT']):
        df['DURATION_DAYS'] = df.apply(
            lambda row: calculate_duration(row['DATEGREG_DISCOVERY'], row['DATEGREG_CONT']),
            axis=1
        )
        # Nettoyage des valeurs aberrantes (durées négatives ou trop longues)
        df.loc[df['DURATION_DAYS'] < 0, 'DURATION_DAYS'] = None
        df.loc[df['DURATION_DAYS'] > 365, 'DURATION_DAYS'] = None

    # Extraction des informations temporelles
    if 'DATEGREG_DISCOVERY' in df.columns:
        df['MONTH'] = df['DATEGREG_DISCOVERY'].dt.month
        df['DAY'] = df['DATEGREG_DISCOVERY'].dt.day
        df['DAY_OF_WEEK'] = df['DATEGREG_DISCOVERY'].dt.dayofweek
        
        # Classification par saisons
        df['DISCOVERY_SEASON'] = df['MONTH'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })

    return df

def load_and_preprocess_data() -> Tuple[pd.DataFrame, Dict[str, str], Dict[str, str]]:
    """Fonction principale qui charge et traite toutes les données"""
    
    # Chargement des données principales
    df = pd.read_csv(file_path)
    
    # Chargement de la correspondance des états
    state_mapping = load_state_names()
    code_to_name = state_mapping
    name_to_code = {v: k for k, v in state_mapping.items()}
    
    # Ajout des noms d'états complets
    if 'STATE' in df.columns and code_to_name:
        df['STATE_NAME'] = df['STATE'].map(code_to_name)
        df['STATE_NAME'] = df['STATE_NAME'].fillna(df['STATE'])
    
    # Application de tous les traitements
    df = preprocess_data(df)
    
    return df, code_to_name, name_to_code
