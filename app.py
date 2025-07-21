import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from utils.preprocessing import load_and_preprocess_data

# Configuration de la page
st.set_page_config(
    page_title="🔥 Dashboard BI - Analyse des feux de forêts",
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
st.title("🔥 Dashboard BI - Analyse des feux de forêts")
st.markdown("**Tableau de bord interactif pour l'analyse des données des feux de forêts**")

# Fonction de chargement avec cache
@st.cache_data
def load_cached_data():
    """Fonction pour charger les données avec cache"""
    return load_and_preprocess_data()

def format_area(area_m2):
    """Formate l'affichage des surfaces selon leur taille"""
    if pd.isna(area_m2):
        return "N/A"
    
    if area_m2 >= 1_000_000:  # Plus d'1 million de m² = affichage en km²
        return f"{area_m2 / 1_000_000:.2f} km²"
    elif area_m2 >= 10_000:  # Plus de 10 000 m² = affichage en hectares
        return f"{area_m2 / 10_000:.1f} ha"
    else:  # Moins de 10 000 m² = affichage en m²
        return f"{area_m2:,.0f} m²"

def format_area_value(area_m2):
    """Retourne la valeur numérique formatée pour les calculs"""
    if pd.isna(area_m2):
        return 0
    
    if area_m2 >= 1_000_000:  # Conversion en km²
        return area_m2 / 1_000_000
    elif area_m2 >= 10_000:  # Conversion en hectares
        return area_m2 / 10_000
    else:  # Garder en m²
        return area_m2

def get_area_unit(area_m2):
    """Retourne l'unité correspondant à la superficie"""
    if pd.isna(area_m2):
        return ""
    
    if area_m2 >= 1_000_000:
        return "km²"
    elif area_m2 >= 10_000:
        return "ha"
    else:
        return "m²"

# Chargement des données avec gestion des erreurs
try:
    with st.spinner("Chargement des données en cours..."):
        df, code_to_name, name_to_code = load_cached_data()
    
    if df.empty:
        st.error("❌ Aucune donnée n'a pu être chargée.")
        st.stop()
    else:
        st.success(f"✅ {len(df):,} enregistrements chargés avec succès")

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
    st.stop()

if not df.empty:
    # SIDEBAR - Navigation
    st.sidebar.title("📋 Navigation")
    st.sidebar.markdown("---")

    # Menu de sélection
    page = st.sidebar.selectbox(
        "Choisissez une section :",
        ["🏠 Aperçu des données",
         "📊 Analyse temporelle", 
         "📈 Visualisations BI"]
    )

    # Options de filtrage dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtres")

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

    # Bouton de refresh
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()

    # Informations dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Données actuelles**")
    st.sidebar.info(f"📄 {len(df_filtered):,} enregistrements")
    if selected_years:
        st.sidebar.info(f"📅 {len(selected_years)} années sélectionnées")
    
    # Information sur le formatage automatique des surfaces
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📏 Format des surfaces**")
    st.sidebar.info("Les surfaces sont automatiquement formatées :\n- < 10,000 m² → m²\n- 10,000 - 1M m² → hectares\n- > 1M m² → km²")

    # =========================
    # PAGE 1: APERÇU DES DONNÉES
    # =========================
    if page == "🏠 Aperçu des données":
        st.header("🏠 Aperçu des Données")

        # KPIs principaux avec format_area
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_fires = len(df_filtered)
            st.metric(
                label="🔥 Total Incendies",
                value=f"{total_fires:,}",
                delta=None
            )

        with col2:
            avg_duration = df_filtered['DURATION_DAYS'].mean() if 'DURATION_DAYS' in df_filtered.columns else 0
            st.metric(
                label="⏱️ Durée Moyenne",
                value=f"{avg_duration:.1f} jours" if pd.notna(avg_duration) else "N/A"
            )

        with col3:
            # Surface totale avec format_area
            if 'FIRE_SIZE_M2' in df_filtered.columns:
                total_area_m2 = df_filtered['FIRE_SIZE_M2'].sum()
                st.metric(
                    label="🌍 Surface Totale",
                    value=format_area(total_area_m2)
                )
            else:
                st.metric(label="🌍 Surface Totale", value="N/A")

        with col4:
            # Taille moyenne avec format_area
            if 'FIRE_SIZE_M2' in df_filtered.columns:
                avg_size_m2 = df_filtered['FIRE_SIZE_M2'].mean()
                st.metric(
                    label="📏 Taille Moyenne",
                    value=format_area(avg_size_m2)
                )
            else:
                st.metric(label="📏 Taille Moyenne", value="N/A")

        st.markdown("---")

        # Tableau de données
        st.subheader("📋 Données Brutes")

        # Options d'affichage
        col1, col2 = st.columns([1, 3])
        with col1:
            nb_rows = st.selectbox("Nombre de lignes :", [10, 25, 50, 100])

        st.dataframe(df_filtered.head(nb_rows), use_container_width=True)

        # Informations techniques
        st.subheader("🔧 Informations Techniques")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Colonnes disponibles :**")
            st.write(list(df_filtered.columns))

        with col2:
            st.write("**Types de données :**")
            st.write(dict(df_filtered.dtypes))

    # ================================
    # PAGE 2: ANALYSE TEMPORELLE
    # ================================
    elif page == "📊 Analyse temporelle":
        st.header("📊 Analyse Temporelle")
        
        st.info("📏 Les surfaces sont automatiquement formatées selon leur taille pour une meilleure lisibilité")

        # Évolution annuelle
        if 'FIRE_YEAR' in df_filtered.columns:
            st.subheader("📈 Évolution Annuelle")

            yearly_stats = df_filtered.groupby('FIRE_YEAR').agg({
                'FIRE_NAME': 'count',
                'DURATION_DAYS': 'mean',
                'FIRE_SIZE_M2': ['mean', 'sum'] if 'FIRE_SIZE_M2' in df_filtered.columns else None
            }).reset_index()

            # Graphique avec Plotly
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Nombre d\'incendies', 'Durée moyenne (jours)',
                               'Taille moyenne', 'Surface totale'),
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

            # Surface - utilisation de FIRE_SIZE_M2 si disponible
            size_column = 'FIRE_SIZE_M2' if 'FIRE_SIZE_M2' in df_filtered.columns else 'FIRE_SIZE'
            
            if size_column in yearly_stats.columns:
                # Taille moyenne - on applique format_area pour les labels
                avg_values = yearly_stats[size_column]['mean']
                fig.add_trace(
                    go.Scatter(
                        x=yearly_stats['FIRE_YEAR'],
                        y=avg_values,
                        mode='lines+markers',
                        name='Taille moyenne',
                        line=dict(color='green', width=3)
                    ),
                    row=2, col=1
                )

                # Surface totale
                total_values = yearly_stats[size_column]['sum']
                fig.add_trace(
                    go.Scatter(
                        x=yearly_stats['FIRE_YEAR'],
                        y=total_values,
                        mode='lines+markers',
                        name='Surface totale',
                        line=dict(color='orange', width=3)
                    ),
                    row=2, col=2
                )

            fig.update_layout(height=700, title_text="Tendances Annuelles")
            st.plotly_chart(fig, use_container_width=True)

        # Analyse saisonnière
        if 'DISCOVERY_SEASON' in df_filtered.columns:
            st.subheader("🌍 Analyse Saisonnière")

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
            st.subheader("📅 Analyse Mensuelle")

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

    # ===============================
    # PAGE 3: VISUALISATIONS BI
    # ===============================
    elif page == "📈 Visualisations BI":
        st.header("📈 Visualisations Business Intelligence")
        
        st.info("📏 Les surfaces sont automatiquement formatées selon leur taille pour une meilleure lisibilité")
        
        # Analyse par États
        if 'STATE_NAME' in df_filtered.columns:
            st.subheader("📍 Analyse Géographique")

            # Utiliser toujours FIRE_SIZE_M2 avec format_area
            size_column = 'FIRE_SIZE_M2' if 'FIRE_SIZE_M2' in df_filtered.columns else 'FIRE_SIZE'
            
            if size_column in df_filtered.columns:
                state_stats = df_filtered.groupby('STATE_NAME').agg({
                    'FIRE_NAME': 'count',
                    size_column: 'sum'
                }).reset_index()
                
                state_stats.columns = ['STATE_NAME', 'COUNT', 'TOTAL_SIZE']
                state_stats = state_stats.sort_values('COUNT', ascending=False).head(10)

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

                with col2:
                    # Créer des labels formatés pour les surfaces
                    state_stats_display = state_stats.copy()
                    state_stats_display['SIZE_FORMATTED'] = state_stats_display['TOTAL_SIZE'].apply(format_area)
                    
                    fig_size = px.bar(
                        state_stats_display,
                        x='TOTAL_SIZE',
                        y='STATE_NAME',
                        orientation='h',
                        title="Surface brûlée par État",
                        color='TOTAL_SIZE',
                        color_continuous_scale='Oranges',
                        hover_data={'SIZE_FORMATTED': True}
                    )
                    fig_size.update_layout(xaxis_title="Surface totale (unité adaptée)")
                    st.plotly_chart(fig_size, use_container_width=True)

                # Tableau des statistiques avec format_area
                st.subheader("📊 Détail par État")
                display_stats = state_stats.copy()
                display_stats['Surface Totale'] = display_stats['TOTAL_SIZE'].apply(format_area)
                display_stats = display_stats[['STATE_NAME', 'COUNT', 'Surface Totale']]
                display_stats.columns = ['État', 'Nombre d\'incendies', 'Surface Totale']
                st.dataframe(display_stats, use_container_width=True)

        # Analyse par Causes
        if 'STAT_CAUSE_DESCR' in df_filtered.columns:
            st.subheader("⚡ Analyse par Causes")

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
            st.subheader("🔥 Heatmap Temporelle")

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
        st.subheader("💡 Insights Automatiques")

        insights_col1, insights_col2 = st.columns(2)

        with insights_col1:
            st.info("📊 **Insights Clés**")
            if 'DISCOVERY_SEASON' in df_filtered.columns:
                peak_season = df_filtered['DISCOVERY_SEASON'].value_counts().index[0]
                st.write(f"🌡️ Saison critique: **{peak_season}**")

            if 'STATE_NAME' in df_filtered.columns:
                top_state = df_filtered['STATE_NAME'].value_counts().index[0]
                st.write(f"🏆 État le plus touché: **{top_state}**")

            if 'STAT_CAUSE_DESCR' in df_filtered.columns:
                top_cause = df_filtered['STAT_CAUSE_DESCR'].value_counts().index[0]
                st.write(f"⚡ Cause principale: **{top_cause}**")

        with insights_col2:
            st.warning("🎯 **Recommandations**")
            st.write("• Renforcer la surveillance en période critique")
            st.write("• Cibler les efforts dans les zones à risque")
            st.write("• Campagnes de prévention spécialisées")
            st.write("• Optimiser les temps de réponse")

else:
    st.error("❌ Impossible de charger les données. Vérifiez le fichier source.")

# Footer
st.markdown("---")
st.markdown("**🔥 Dashboard BI Incendies** - fev25_cda_feux_de_forets")