import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from utils.preprocessing import load_and_preprocess_data

# Configuration de la page
st.set_page_config(
    page_title="Dashboard BI - Analyse des feux de forêt aux USA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #ff6b6b;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.title("**Analyse des feux de forêts aux USA**")
st.info("L'analyse est effectuée sur un échantillon de données filtrées pour le fonctionnement du dashboard")
# Fonction de chargement avec cache
@st.cache_data
def load_cached_data():
    """Fonction pour charger les données avec cache"""
    return load_and_preprocess_data()

# Chargement des données
df, code_to_name, name_to_code = load_cached_data()

if not df.empty:
    # SIDEBAR - Navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")

    # Menu de sélection
    page = st.sidebar.selectbox(
        "Choisissez une section :",
        ["Aperçu des données",
         "Analyse temporelle", 
         "Visualisations BI"]
    )

    # Options de filtrage dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtres")

    # Filtre par années
    if 'FIRE_YEAR' in df.columns:
        years = sorted(df['FIRE_YEAR'].unique())
        selected_years = st.sidebar.multiselect(
            "Années :",
            years,
            default=years[-5:] if len(years) > 5 else years
        )
        df_filtered = df[df['FIRE_YEAR'].isin(selected_years)] if selected_years else df
    else:
        df_filtered = df
        selected_years = []

    # Filtre par états
    if 'STATE_NAME' in df.columns and not df['STATE_NAME'].empty:
        states = sorted([state for state in df['STATE_NAME'].unique() if pd.notna(state)])
        selected_states = st.sidebar.multiselect(
            "États :",
            states,
            default=states[:10] if len(states) > 10 else states
        )

        if selected_states:
            df_filtered = df_filtered[df_filtered['STATE_NAME'].isin(selected_states)]

    # Filtre par saisons
    if 'DISCOVERY_SEASON' in df.columns:
        seasons = sorted(df['DISCOVERY_SEASON'].unique())
        selected_seasons = st.sidebar.multiselect(
            "Saisons :",
            seasons,
            default=seasons  # Par défaut, toutes les saisons sont sélectionnées
        )

        if selected_seasons:
            df_filtered = df_filtered[df_filtered['DISCOVERY_SEASON'].isin(selected_seasons)]

    # Informations dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Données actuelles **")
    st.sidebar.info(f"{len(df_filtered):,} feux sélectionnées")
    if selected_years:
        st.sidebar.info(f"{len(selected_years)} années sélectionnées")
    st.sidebar.info(f"Dataset complet : {len(df):,} feux")

    # PAGE 1: APERÇU DES DONNÉES
    if page == "Aperçu des données":
        st.header("Aperçu des Données")

        # KPIs principaux
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_fires = len(df_filtered)
            st.metric(
                label="Total Incendies",
                value=f"{total_fires:,}",
                delta=None
            )

        with col2:
            avg_duration = df_filtered['DURATION_DAYS'].mean() if 'DURATION_DAYS' in df_filtered.columns else 0
            st.metric(
                label="Durée Moyenne",
                value=f"{avg_duration:.1f} jours" if pd.notna(avg_duration) else "N/A"
            )

        with col3:
            # Surface totale directement depuis FIRE_SIZE_KM2
            if 'FIRE_SIZE_KM2' in df_filtered.columns:
                total_area_km2 = df_filtered['FIRE_SIZE_KM2'].sum()
                st.metric(
                    label="Surface Totale",
                    value=f"{total_area_km2:.2f} km²" if total_area_km2 > 0 else "N/A"
                )
            else:
                st.metric(label="Surface Totale", value="N/A")

        with col4:
            # Taille moyenne directement depuis FIRE_SIZE_KM2
            if 'FIRE_SIZE_KM2' in df_filtered.columns:
                avg_size_km2 = df_filtered['FIRE_SIZE_KM2'].mean()
                st.metric(
                    label="Taille Moyenne",
                    value=f"{avg_size_km2:.2f} km²" if avg_size_km2 > 0 else "N/A"
                )
            else:
                st.metric(label="Taille Moyenne", value="N/A")

        st.markdown("---")

        # Tableau de données
        st.subheader("Données Brutes")

        # Options d'affichage
        col1, col2 = st.columns([1, 3])
        with col1:
            nb_rows = st.selectbox("Nombre de lignes :", [10, 25, 50, 100])

        st.dataframe(df_filtered.head(nb_rows), use_container_width=True)

        # Informations techniques
        st.subheader("Informations Techniques")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Colonnes disponibles :**")
            st.write(list(df_filtered.columns))

        with col2:
            st.write("**Types de données :**")
            st.write(dict(df_filtered.dtypes))

    # PAGE 2: ANALYSE TEMPORELLE
    elif page == "Analyse temporelle":
        st.header("Analyse Temporelle")

        # Évolution annuelle
        if 'FIRE_YEAR' in df_filtered.columns:
            st.subheader("Évolution Annuelle")

            yearly_stats = df_filtered.groupby('FIRE_YEAR').agg({
                'FIRE_NAME': 'count',
                'DURATION_DAYS': 'mean',
                'FIRE_SIZE_KM2': ['mean', 'sum'] if 'FIRE_SIZE_KM2' in df_filtered.columns else None
            }).reset_index()

            # Graphique avec Plotly
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Nombre d\'incendies', 'Durée moyenne (jours)',
                               'Taille moyenne (km²)', 'Surface totale (km²)'),
            )

            # Nombre d'incendies
            fig.add_trace(
                go.Scatter(
                    x=yearly_stats['FIRE_YEAR'],
                    y=yearly_stats['FIRE_NAME']['count'],
                    mode='lines+markers',
                    name='Nb incendies',
                    line=dict(color='red', width=3)
                ),
                row=1, col=1
            )

            # Durée moyenne
            if 'DURATION_DAYS' in yearly_stats.columns:
                fig.add_trace(
                    go.Scatter(
                        x=yearly_stats['FIRE_YEAR'],
                        y=yearly_stats['DURATION_DAYS']['mean'],
                        mode='lines+markers',
                        name='Durée moyenne',
                        line=dict(color='blue', width=3)
                    ),
                    row=1, col=2
                )

            # Taille moyenne
            if 'FIRE_SIZE_KM2' in yearly_stats.columns:
                avg_values = yearly_stats['FIRE_SIZE_KM2']['mean']
                fig.add_trace(
                    go.Scatter(
                        x=yearly_stats['FIRE_YEAR'],
                        y=avg_values,
                        mode='lines+markers',
                        name='Taille moyenne (km²)',
                        line=dict(color='green', width=3)
                    ),
                    row=2, col=1
                )

                # Surface totale
                total_values = yearly_stats['FIRE_SIZE_KM2']['sum']
                fig.add_trace(
                    go.Scatter(
                        x=yearly_stats['FIRE_YEAR'],
                        y=total_values,
                        mode='lines+markers',
                        name='Surface totale (km²)',
                        line=dict(color='orange', width=3)
                    ),
                    row=2, col=2
                )

            fig.update_layout(height=700, title_text="Tendances Annuelles")
            st.plotly_chart(fig, use_container_width=True)

        # Analyse saisonnière
        if 'DISCOVERY_SEASON' in df_filtered.columns:
            st.subheader("Analyse Saisonnière")

            col1, col2 = st.columns(2)

            with col1:
                seasonal_stats = df_filtered['DISCOVERY_SEASON'].value_counts()
                fig_pie = px.pie(
                    values=seasonal_stats.values,
                    names=seasonal_stats.index,
                    title="Répartition par Saison",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                fig_bar = px.bar(
                    x=seasonal_stats.index,
                    y=seasonal_stats.values,
                    title="Nombre d'incendies par saison",
                    color=seasonal_stats.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # Analyse mensuelle
        if 'MONTH' in df_filtered.columns:
            st.subheader("Analyse Mensuelle")

            monthly_stats = df_filtered['MONTH'].value_counts().sort_index()

            fig_line = px.line(
                x=monthly_stats.index,
                y=monthly_stats.values,
                title="Evolution mensuelle des incendies",
                markers=True
            )
            fig_line.update_traces(line_color='orange', line_width=3)
            fig_line.update_layout(xaxis_title="Mois", yaxis_title="Nombre d'incendies")
            st.plotly_chart(fig_line, use_container_width=True)

    # PAGE 3: VISUALISATIONS BI
    elif page == "Visualisations BI":
        st.header("Visualisations Business Intelligence")
        
        # Analyse par États
        if 'STATE_NAME' in df_filtered.columns:
            st.subheader("Analyse Géographique")

            if 'FIRE_SIZE_KM2' in df_filtered.columns:
                # TOUS les états pour les cartes
                all_states = df_filtered.groupby(['STATE','STATE_NAME']).agg({
                    'FIRE_NAME': 'count',
                    'FIRE_SIZE_KM2': 'sum'
                }).reset_index()
                all_states.columns = ['STATE','STATE_NAME', 'COUNT', 'TOTAL_SIZE']
                all_states['AVG_SIZE'] = all_states['TOTAL_SIZE'] / all_states['COUNT']
                
                # TOP 10 pour les graphiques en barres
                state_stats = all_states.sort_values('COUNT', ascending=False).head(10)

                col1, col2 = st.columns(2)

                with col1:
                    fig_states = px.bar(
                        state_stats,
                        x='COUNT',
                        y='STATE_NAME',
                        orientation='h',
                        title="Top 10 États - Nombre d'incendies",
                        color='COUNT',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_states, use_container_width=True)

                state_stats = all_states.sort_values('TOTAL_SIZE', ascending=False).head(10)
                with col2:
                    fig_size = px.bar(
                        state_stats,
                        x='TOTAL_SIZE',
                        y='STATE_NAME',
                        orientation='h',
                        title="Surface brûlée par État (km²)",
                        color='TOTAL_SIZE',
                        color_continuous_scale='Oranges'
                    )
                    fig_size.update_layout(xaxis_title="Surface totale (km²)")
                    st.plotly_chart(fig_size, use_container_width=True)

                # Carte choroplèthe avec TOUS les états
                st.subheader("Cartes des incendies par État")
                
                col3, col4 = st.columns(2)
                
                with col3:
                    fig_map_count = px.choropleth(
                        all_states, 
                        locations="STATE",
                        locationmode="USA-states",
                        color="COUNT",
                        scope="usa",
                        color_continuous_scale="Reds",
                        title="Nombre d'incendies par État",
                        labels={"COUNT": "Nombre d'incendies"},
                        hover_name="STATE_NAME"
                    )
                    st.plotly_chart(fig_map_count, use_container_width=True)

                with col4:
                    fig_map_size = px.choropleth(
                        all_states,
                        locations="STATE",
                        locationmode="USA-states",
                        color="TOTAL_SIZE",
                        scope="usa",
                        color_continuous_scale="Oranges",
                        title="Surface brûlée par État (km²)",
                        labels={"TOTAL_SIZE": "Surface (km²)"},
                        hover_name="STATE_NAME"
                    )
                    st.plotly_chart(fig_map_size, use_container_width=True)

                # Tableau récapitulatif (TOP 10 par taille)
                st.subheader("Tableau Récapitulatif - Top 10 par taille")
                display_stats = state_stats[['STATE_NAME', 'COUNT', 'TOTAL_SIZE', 'AVG_SIZE']].copy()
                display_stats.columns = ['État', 'Nb Incendies', 'Surface Totale (km²)', 'Taille Moyenne (km²)']
                display_stats['Surface Totale (km²)'] = display_stats['Surface Totale (km²)'].round(1)
                display_stats['Taille Moyenne (km²)'] = display_stats['Taille Moyenne (km²)'].round(2)
                
                st.dataframe(display_stats, use_container_width=True, hide_index=True)

        # Analyse par Causes
        if 'STAT_CAUSE_DESCR' in df_filtered.columns:
            st.subheader("Analyse par Causes")

            cause_stats = df_filtered['STAT_CAUSE_DESCR'].value_counts().head(8)

            col1, col2 = st.columns(2)

            with col1:
                fig_causes = px.pie(
                    values=cause_stats.values,
                    names=cause_stats.index,
                    title="Causes principales d'incendies"
                )
                st.plotly_chart(fig_causes, use_container_width=True)

            with col2:
                fig_causes_bar = px.bar(
                    x=cause_stats.values,
                    y=cause_stats.index,
                    orientation='h',
                    title="Détail par cause",
                    color=cause_stats.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_causes_bar, use_container_width=True)

        # Heatmap temporelle
        if 'MONTH' in df_filtered.columns and 'FIRE_YEAR' in df_filtered.columns:
            st.subheader("Heatmap Temporelle")

            # Création d'une heatmap mois vs années
            heatmap_data = df_filtered.groupby(['FIRE_YEAR', 'MONTH']).size().unstack(fill_value=0)

            fig_heatmap = px.imshow(
                heatmap_data.T,
                title="Intensité des incendies (Mois vs Années)",
                color_continuous_scale='Reds',
                aspect="auto"
            )
            fig_heatmap.update_layout(
                xaxis_title="Années",
                yaxis_title="Mois"
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

        # Insights et Recommandations
        st.markdown("---")
        st.subheader("Indicateurs clés et recommandations")

        insights_col1, insights_col2 = st.columns(2)

        with insights_col1:
            st.info("**Indicateurs**")
            if 'DISCOVERY_SEASON' in df_filtered.columns:
                peak_season = df_filtered['DISCOVERY_SEASON'].value_counts().index[0]
                st.write(f"• Saison critique: **{peak_season}**")

            if 'FIRE_SIZE_KM2' in df_filtered.columns and "STATE_NAME" in df_filtered.columns:
                top_state = df_filtered.groupby('STATE_NAME')['FIRE_SIZE_KM2'].sum().idxmax()
                top_area = df_filtered.groupby('STATE_NAME')['FIRE_SIZE_KM2'].sum().max()
                
                st.write(f"• État le plus touché : **{top_state}** (Surface totale: {top_area:.2f} km²)")

            if 'STAT_CAUSE_DESCR' in df_filtered.columns:
                top_cause = df_filtered['STAT_CAUSE_DESCR'].value_counts().index[0]
                st.write(f"• Cause principale: **{top_cause}**")

        with insights_col2:
            st.warning("**Recommandations**")
            st.write("• Renforcer la surveillance des zones à risques pendant l'été")
            st.write("• Cibler les efforts dans les états les plus touchés")
            st.write("• Campagnes de prévention spécifiques aux causes principales")
            st.write("• Optimiser les temps de réponse")


# Pied de page
st.markdown("---")
st.markdown("**Dashboard BI Analyse des feux de forêt aux USA - fev25_cda_feux_de_forets**")
