# preprocessing.py
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

file_path = 'data/fires_light.csv'

def load_state_names() -> Dict[str, str]:
    """Charge les correspondances des noms d'États depuis un fichier CSV"""
    try:
        state_df = pd.read_csv('data/state_names.csv')
        return dict(zip(state_df['Alpha code'], state_df['State']))
    except Exception as e:
        st.error(f"Erreur de chargement des noms d'États: {str(e)}")
        return {}

def load_data(file_path: str) -> pd.DataFrame:
    """Charge les données avec gestion des encodages"""
    try:
        pd.read_csv(file_path)

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        raise

def julian_to_date(julian_number: float) -> Optional[datetime]:
    """Convertit un Julian Date en date grégorienne"""
    if pd.isna(julian_number):
        return None
    try:
        J1970 = 2440587.5  # Julian date pour 1970-01-01
        timestamp = (float(julian_number) - J1970) * 86400.0
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        st.warning(f"Erreur de conversion pour {julian_number}: {str(e)}")
        return None

def calculate_duration(discovery_date: datetime, cont_date: datetime) -> Optional[int]:
    """Calcule la durée en jours entre deux dates"""
    try:
        if pd.isna(discovery_date) or pd.isna(cont_date):
            return None
        return (cont_date - discovery_date).days
    except Exception as e:
        st.warning(f"Erreur de calcul de durée: {str(e)}")
        return None
def convert_acres_to_m2(acres_value):
    """Convertit les acres en mètres carrés"""
    if pd.isna(acres_value):
        return None
    return acres_value * 4046.86

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prétraite les données avec gestion des dates et des états"""
    try:
        # 1. Conversion des dates juliennes
        for date_col in ['DISCOVERY_DATE', 'CONT_DATE']:
            if date_col in df.columns:
                df[f'DATEGREG_{date_col.split("_")[0]}'] = (
                    df[date_col]
                    .apply(lambda x: julian_to_date(x).date() if pd.notna(x) and julian_to_date(x) else None)
                )
                df[f'DATEGREG_{date_col.split("_")[0]}'] = pd.to_datetime(
                    df[f'DATEGREG_{date_col.split("_")[0]}']
                )

        # 2. Calcul de la durée
        if all(col in df.columns for col in ['DATEGREG_DISCOVERY', 'DATEGREG_CONT']):
            df['DURATION_DAYS'] = df.apply(
                lambda row: calculate_duration(row['DATEGREG_DISCOVERY'], row['DATEGREG_CONT']),
                axis=1
            )
            # Nettoyage des valeurs aberrantes
            df.loc[df['DURATION_DAYS'] < 0, 'DURATION_DAYS'] = None
            df.loc[df['DURATION_DAYS'] > 365, 'DURATION_DAYS'] = None

        # 3. Extraction des caractéristiques temporelles
        if 'DATEGREG_DISCOVERY' in df.columns:
            df['MONTH'] = df['DATEGREG_DISCOVERY'].dt.month
            df['DAY'] = df['DATEGREG_DISCOVERY'].dt.day
            df['DAY_OF_WEEK'] = df['DATEGREG_DISCOVERY'].dt.dayofweek
            df['DISCOVERY_SEASON'] = df['MONTH'].map({
                12: 'Winter', 1: 'Winter', 2: 'Winter',
                3: 'Spring', 4: 'Spring', 5: 'Spring',
                6: 'Summer', 7: 'Summer', 8: 'Summer',
                9: 'Fall', 10: 'Fall', 11: 'Fall'
            })
        # 4. conversion des surfaces
        if 'FIRE_SIZE' in df.columns:
            df['FIRE_SIZE_M2'] = df['FIRE_SIZE'].apply(convert_acres_to_m2)
            df['FIRE_SIZE_HECTARES'] = df['FIRE_SIZE_M2'] / 10000  # Conversion en hectares aussi
            
        return df

    except Exception as e:
        st.error(f"Erreur dans preprocess_data: {str(e)}")
        return df

def load_and_preprocess_data() -> Tuple[pd.DataFrame, Dict[str, str], Dict[str, str]]:
    """Charge et traite les données avec gestion complète des états"""
    try:
        # 1. Charger les données principales
        df = pd.read_csv(file_path)  # ou utilisez load_data si vous voulez la gestion d'erreur

        # 2. Charger les correspondances d'états
        state_mapping = load_state_names()

        # 3. Créer les dictionnaires dans les deux sens
        code_to_name = state_mapping
        name_to_code = {v: k for k, v in state_mapping.items()}

        # 4. Ajouter les noms d'états si la colonne STATE existe
        if 'STATE' in df.columns and code_to_name:
            df['STATE_NAME'] = df['STATE'].map(code_to_name)
            # Conserver les codes originaux si le mapping échoue
            df['STATE_NAME'] = df['STATE_NAME'].fillna(df['STATE'])

        # 5. Appliquer le preprocessing existant
        df = preprocess_data(df)

        return df, code_to_name, name_to_code


    except Exception as e:
        st.error(f"Erreur globale : {str(e)}")
        return pd.DataFrame(), {}, {}