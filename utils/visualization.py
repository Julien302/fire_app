import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_yearly_trends(df):
    """Visualisation des tendances annuelles avec métriques BI"""
    
    # Vérifier quelles colonnes sont disponibles
    agg_dict = {'FOD_ID': 'count'}
    
    if 'DURATION_DAYS' in df.columns:
        agg_dict['DURATION_DAYS'] = 'mean'
    
    if 'FIRE_SIZE' in df.columns:
        agg_dict['FIRE_SIZE'] = ['mean', 'sum']
    
    yearly_stats = df.groupby('FIRE_YEAR').agg(agg_dict).reset_index()
    
    # Aplatir les colonnes multi-niveaux si nécessaire
    if isinstance(yearly_stats.columns, pd.MultiIndex):
        yearly_stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in yearly_stats.columns.values]
    
    # Renommer pour simplicité
    yearly_stats = yearly_stats.rename(columns={
        'FOD_ID_count': 'COUNT',
        'DURATION_DAYS_mean': 'AVG_DURATION',
        'FIRE_SIZE_mean': 'AVG_SIZE',
        'FIRE_SIZE_sum': 'TOTAL_SIZE'
    })

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Evolution du nombre d\'incendies', 
            'Durée moyenne des incendies',
            'Taille moyenne des incendies', 
            'Surface totale brûlée par année'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )

    # Style des graphiques
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

    fig.add_trace(
        go.Scatter(
            x=yearly_stats['FIRE_YEAR'], 
            y=yearly_stats['COUNT'],
            mode='lines+markers', 
            name='Nb incendies',
            line=dict(color=colors[0], width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=yearly_stats['FIRE_YEAR'], 
            y=yearly_stats['AVG_DURATION'],
            mode='lines+markers', 
            name='Durée moy',
            line=dict(color=colors[1], width=3),
            marker=dict(size=8)
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=yearly_stats['FIRE_YEAR'], 
            y=yearly_stats['AVG_SIZE'],
            mode='lines+markers', 
            name='Taille moy',
            line=dict(color=colors[2], width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=yearly_stats['FIRE_YEAR'], 
            y=yearly_stats['TOTAL_SIZE'],
            mode='lines+markers', 
            name='Surface totale',
            line=dict(color=colors[3], width=3),
            marker=dict(size=8)
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=700, 
        title_text="📊 Dashboard - Évolution Temporelle des Incendies",
        title_font_size=20,
        showlegend=False,
        template="plotly_white"
    )
    
    # Personnalisation des axes
    fig.update_xaxes(title_text="Année", showgrid=True)
    fig.update_yaxes(title_text="Nombre", row=1, col=1)
    fig.update_yaxes(title_text="Jours", row=1, col=2)
    fig.update_yaxes(title_text="Acres", row=2, col=1)
    fig.update_yaxes(title_text="Acres", row=2, col=2)
    
    return fig

def plot_seasonal_analysis(df):
    """Analyse saisonnière améliorée"""
    seasonal_stats = df.groupby('DISCOVERY_SEASON').agg({
        'FOD_ID': 'count',
        'DURATION_DAYS': 'mean',
        'FIRE_SIZE': 'mean'
    }).reset_index()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Répartition Saisonnière', 'Impact par Saison'),
        specs=[[{"type": "domain"}, {"type": "xy"}]]
    )

    # Graphique en secteurs
    fig.add_trace(
        go.Pie(
            labels=seasonal_stats['DISCOVERY_SEASON'],
            values=seasonal_stats['FOD_ID'],
            name="Saisons",
            marker_colors=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'],
            textinfo='label+percent',
            textfont_size=12
        ),
        row=1, col=1
    )

    # Graphique en barres pour la durée
    fig.add_trace(
        go.Bar(
            x=seasonal_stats['DISCOVERY_SEASON'],
            y=seasonal_stats['DURATION_DAYS'],
            name="Durée/Saison",
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            text=seasonal_stats['DURATION_DAYS'].round(1),
            textposition='outside'
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=500, 
        title_text="🌱 Analyse Saisonnière des Incendies",
        title_font_size=18,
        template="plotly_white"
    )
    
    return fig

def create_geographic_analysis(df):
    """Analyse géographique par états"""
    if 'STATE' in df.columns:
        state_stats = df.groupby('STATE').agg({
            'FOD_ID': 'count',
            'DURATION_DAYS': 'mean',
            'FIRE_SIZE': 'mean'
        }).reset_index().sort_values('FOD_ID', ascending=False).head(15)
        
        fig = px.bar(
            state_stats,
            x='STATE',
            y='FOD_ID',
            title='🗺️ Top 15 États par Nombre d\'Incendies',
            color='FOD_ID',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            template="plotly_white"
        )
        
        return fig
    else:
        return None

def create_cause_analysis(df):
    """Analyse des causes d'incendies"""
    if 'STAT_CAUSE_DESCR' in df.columns:
        cause_stats = df['STAT_CAUSE_DESCR'].value_counts().head(10)
        
        fig = px.horizontal_bar(
            x=cause_stats.values,
            y=cause_stats.index,
            title='⚡ Top 10 Causes d\'Incendies',
            color=cause_stats.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=500,
            template="plotly_white",
            yaxis={'categoryorder':'total ascending'}
        )
        
        return fig
    else:
        return None
