# README.md

# Dashboard BI - Analyse des feux de forêt aux USA
STREAMLIT : https://fireapp-fhgvxfzp6csdorj5kvdgyp.streamlit.app/

## Description

Tableau de bord interactif développé avec Streamlit pour l'analyse des données des feux de forêts aux USA. Cette application propose une visualisation complète et des insights business intelligence sur les tendances, répartitions géographiques et causes des incendies.

## Dataset
La base de donnée csv fires_light.csv a été réduite pour être intégrée dans un streamlit connecté à Github.
Colonnes conservées : "OBJECTID","FIRE_YEAR","STAT_CAUSE_DESCR","CONT_DATE","FIRE_SIZE","STATE","DATEGREG_DISCOVERY","DATEGREG_CONT","FIRE_NAME"
Réduction aléatoire de 50% du fichier.
Dataset sur 20 ans de 1995 à 2015.

## Fonctionnalités

### **Tableau de bord multi-pages**
- **Aperçu des données** : KPIs principaux et données brutes
- **Analyse temporelle** : Évolutions annuelles, saisonnières et mensuelles  
- **Visualisations BI** : Analyses géographiques et temporelles

### **Visualisations avancées**
- Graphiques temporels avec Plotly
- Heatmaps interactives
- Analyses géographiques par États
- Distributions par causes d'incendies
- KPIs et métriques clés

## Installation

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances
```bash
pip install -r requirements.txt
