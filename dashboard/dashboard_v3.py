"""
Dashboard Streamlit - Analyse de la Gouvernance Économique du Bénin (2021-2026)
Hackathon iSHEERO × DataCamp - Bénin Insights Challenge

VERSION 3 - AMÉLIORATIONS:
- Integration ARIMA/Prophet pour prévisions rigoureuses
- Visuel impact ACLED→IDE avec décalage 6 mois
- Optimisé pour analyse profonde avec sécurité

Combine les insights de:
- INSIGHTS1.ipynb (Q1, Q2, Q3 avec analyse média + sécurité)
- Benin_Economic_Governance_Analysis.ipynb (Q3, Q4)
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import zipfile

# Imports pour prévisions
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import stats

# ============================================================================
# CONFIG STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Benin Insights",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour design chic
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .insight-box {
        background: #f0f2f6;
        padding: 15px;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: #9c97a1;
        padding: 15px;
        border-left: 4px solid #ff9800;
        border-radius: 5px;
        margin: 10px 0;
    }
    h1 {
        color: #1f3a93;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #667eea;
        margin-bottom: 30px;
    }
    h2 {
        color: #2d5016;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    h3 {
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================================

@st.cache_resource
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(base_dir, 'data', 'processed')

    # Chemin vers le ZIP
    zip_path = os.path.join(processed_dir, 'gkg_2021_2026_cleaned.zip')

    try:
        # Ouverture du zip et lecture directe du CSV interne avec le nom exact
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open('gkg_2021_2026_cleaned.csv') as f:
                df_gkg = pd.read_csv(f)
        
        # Chargement des autres fichiers normalement
        df_event = pd.read_csv(os.path.join(processed_dir, 'events_2021_2026_cleaned.csv'))
        df_project = pd.read_csv(os.path.join(processed_dir, 'Project_List_Cleaned_1.csv'))
        df_acled = pd.read_csv(os.path.join(processed_dir, 'acled_filtered_2021_2025.csv'))
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des fichiers : {e}")
        return None, None, None, None

    # Conversion des dates
    df_event['SQLDATE'] = pd.to_datetime(df_event['SQLDATE'], format='%Y%m%d')
    df_project['Board Approval Date'] = pd.to_datetime(df_project['Board Approval Date'], errors='coerce')
    
    if 'WEEK' in df_acled.columns:
        df_acled['EVENT_DATE'] = pd.to_datetime(df_acled['WEEK'], errors='coerce')
    
    return df_gkg, df_event, df_project, df_acled

# Charger les données
with st.spinner('📊 Chargement des données...'):
    df_gkg, df_event, df_project, df_acled = load_data()

# ============================================================================
# 2. SIDEBAR - FILTRES
# ============================================================================

st.sidebar.markdown("## FILTRES")
st.sidebar.markdown("---")

# Filtre temporel
min_date = df_event['SQLDATE'].min().date()
max_date = df_event['SQLDATE'].max().date()

date_range = st.sidebar.slider(
    "📅 Période d'analyse",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Conversion en datetime pour filtrage
start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])

# Filtrer les événements
df_event_filtered = df_event[
    (df_event['SQLDATE'] >= start_date) & 
    (df_event['SQLDATE'] <= end_date)
].copy()

df_acled_filtered = df_acled[
    (df_acled['EVENT_DATE'] >= start_date) & 
    (df_acled['EVENT_DATE'] <= end_date)
].copy() if 'EVENT_DATE' in df_acled.columns else pd.DataFrame()

df_project_filtered = df_project[
    (df_project['Board Approval Date'] >= start_date) & 
    (df_project['Board Approval Date'] <= end_date)
].copy()

# Options additionnelles
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 OPTIONS")

show_security = st.sidebar.checkbox(" Inclure impact sécurité (ACLED)", value=True)
show_projections = st.sidebar.checkbox(" Afficher projections ARIMA", value=True)

# ============================================================================
# 3. HEADER
# ============================================================================

st.markdown("""
# 🇧🇯 Bénin Economic Governance Dashboard
## 2021-2026 | Analyse Perception Médiatique & Investissements Direct Extérieur (IDE)
""")

st.markdown("---")

# ============================================================================
# 4. MÉTRIQUES CLÉS (KPI CARDS)
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_articles = df_event_filtered['NumArticles'].sum()
    st.metric(
        " Articles GDELT",
        f"{total_articles:,.0f}",
        f"+{total_articles / max(len(df_event_filtered), 1):.0f} /événement"
    )

with col2:
    avg_tone = df_event_filtered['AvgTone'].mean()
    tone_color = "🟢" if avg_tone > 0 else "🔴" if avg_tone < 0 else "⚪"
    st.metric(
        " Tone GDELT Moyen",
        f"{avg_tone:.3f}",
        f"{tone_color} {'Positif' if avg_tone > 0 else 'Négatif'}"
    )

with col3:
    total_ide = df_project_filtered['IDA Commitment $US'].sum() / 1e9
    st.metric(
        " IDE Total (IDA)",
        f"${total_ide:.2f}B",
        f"{len(df_project_filtered)} projets"
    )

with col4:
    security_events = len(df_acled_filtered) if show_security and len(df_acled_filtered) > 0 else 0
    st.metric(
        " Incidents Sécurité (ACLED)",
        f"{security_events}",
        "En période d'analyse" if show_security else "Désactivé"
    )

st.markdown("---")

# ============================================================================
# 5. CRÉATION DES ONGLETS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Perception Internationale",
    "Médias vs IDE (+ Sécurité)",
    "Perception Secteurs",
    "Hype vs Reality",
    "Projections ARIMA 2026-2028"
])

# ============================================================================
# TAB 1: Q1 - PERCEPTION INTERNATIONALE
# ============================================================================

with tab1:
    st.subheader(" Comment l'économie du Bénin est perçue à l'international ?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Tone timeline
        df_event_monthly = df_event_filtered.copy()
        df_event_monthly['YearMonth'] = df_event_monthly['SQLDATE'].dt.to_period('M')
        
        tone_by_month = df_event_monthly.groupby('YearMonth').agg({
            'AvgTone': 'mean',
            'NumArticles': 'sum',
            'NumSources': 'sum'
        }).reset_index()
        
        tone_by_month['YearMonth'] = tone_by_month['YearMonth'].astype(str)
        
        fig_tone = go.Figure()
        fig_tone.add_trace(go.Scatter(
            x=tone_by_month['YearMonth'],
            y=tone_by_month['AvgTone'],
            mode='lines+markers',
            name='Tone GDELT',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        fig_tone.add_hline(y=0, line_dash="dash", line_color="gray", 
                          annotation_text="Neutre", annotation_position="right")
        
        fig_tone.update_layout(
            title="Évolution du Tone GDELT (2021-2026)",
            xaxis_title="Période",
            yaxis_title="Tone Moyen (Goldstein Scale)",
            hovermode='x unified',
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_tone, use_container_width=True)
    
    with col2:
        # Statistics
        st.markdown("#### Statistiques")
        st.markdown(f"""
        **Période:** {date_range[0]} → {date_range[1]}
        
        **Tone Global:**
        - Moyen: `{df_event_filtered['AvgTone'].mean():.3f}`
        - Min: `{df_event_filtered['AvgTone'].min():.3f}`
        - Max: `{df_event_filtered['AvgTone'].max():.3f}`
        
        **Couverture:**
        - Événements: `{len(df_event_filtered):,}`
        - Articles: `{df_event_filtered['NumArticles'].sum():,}`
        - Sources: `{df_event_filtered['NumSources'].sum():,}`
        """)
    
    # Insight
    st.markdown("#### Que comprendre ?")
    st.markdown("""
    Le tone GDELT reflète la perception médiatique internationale du Bénin. 
    Une valeur positive indique une couverture favorable, une valeur négative 
    pointe des préoccupations (sécurité, stabilité, économie). 
    
    **Interprétation :** Une visibilité massive mais structurellement critique Volume d’articles (278 023) : Le Bénin n'est pas invisible. C’est le premier enseignement majeur pour un nouveau gouvernement : avec plus de 200 000 articles économiques internationaux analysés, le Bénin génère un flux d'intérêt réel à l'échelle mondiale. Sa diplomatie économique et ses réformes structurelles captent l'attention des marchés. 
    Le pays est installé sur le radar des investisseurs.
    
    Une moyenne globale légèrement négative est tout à fait standard dans les bases de données GDELT mondiales. La presse internationale sursaute plus vite sur les risques (inflation globale, tensions sécuritaires au Sahel, logistique) que sur les réussites quotidiennes.
    Cependant, cette valeur de -0,54 sert de ligne de base (Baseline) : tout période situé au-dessus est une victoire réputationnelle ; toute période situé en dessous est une alerte.
    """)

# ============================================================================
# TAB 2: Q2 - MÉDIAS vs IDE (AVEC SÉCURITÉ)
# ============================================================================

with tab2:
    st.subheader("🔗 Corrélation: Perception Médiatique International/National & IDE")
    
    # Agrégation mensuelle pour corrélation
    df_event_monthly = df_event_filtered.copy()
    df_event_monthly['YearMonth'] = df_event_monthly['SQLDATE'].dt.to_period('M')
    
    media_by_month = df_event_monthly.groupby('YearMonth').agg({
        'AvgTone': 'mean',
        'NumArticles': 'sum'
    }).reset_index()
    
    # IDE par mois d'approbation
    df_project_monthly = df_project.copy()
    df_project_monthly['ApprovalMonth'] = df_project_monthly['Board Approval Date'].dt.to_period('M')
    ide_by_month = df_project_monthly.groupby('ApprovalMonth')['IDA Commitment $US'].sum().reset_index()
    ide_by_month.columns = ['YearMonth', 'IDE_Commitment']
    
    # Fusion
    media_by_month['YearMonth_str'] = media_by_month['YearMonth'].astype(str)
    ide_by_month['YearMonth_str'] = ide_by_month['YearMonth'].astype(str)
    
    correlation_data = media_by_month.merge(
        ide_by_month[['YearMonth_str', 'IDE_Commitment']], 
        left_on='YearMonth_str', 
        right_on='YearMonth_str',
        how='left'
    ).fillna(0)
    
    # Corrélation
    corr_tone_ide = correlation_data['AvgTone'].corr(correlation_data['IDE_Commitment'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter plot
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(
            x=correlation_data['AvgTone'],
            y=correlation_data['IDE_Commitment'] / 1e6,
            mode='markers',
            marker=dict(
                size=8,
                color=correlation_data['IDE_Commitment'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="IDE (USD)")
            ),
            text=[f"Tone: {t:.2f}<br>IDE: ${i:.0f}M" 
                  for t, i in zip(correlation_data['AvgTone'], correlation_data['IDE_Commitment']/1e6)],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig_corr.update_layout(
            title=f"Tone GDELT vs IDE (Pearson r={corr_tone_ide:.3f})",
            xaxis_title="Tone GDELT Moyen",
            yaxis_title="IDE Commitment (Millions USD)",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col2:
        # Insights texte
        st.markdown("#### Résultats Clés")
        st.markdown("""
        **Médias Internationaux vs IDE:**
        - Faible Corrélation: `+0.18` ✅
        - Relation positive avec décalage 6 mois
        - Les articles positifs impacte dans une infirme proportion les IDE approuvés 6 mois plus tard
        """)
    
    # ========== SECTION ACLED - Impact Sécurité ==========
    
    if show_security and len(df_acled_filtered) > 0:
        st.markdown("---")
        st.subheader(" Analyse de l'impact sécuritaire sur les IDE - Analyse avec Lag 6 Mois")
        
        # Préparer données ACLED
        df_acled_monthly = df_acled[df_acled['EVENT_DATE'].notna()].copy()
        df_acled_monthly['YearMonth'] = df_acled_monthly['EVENT_DATE'].dt.to_period('M')
        
        acled_by_month = df_acled_monthly.groupby('YearMonth').agg({
            'EVENTS': 'sum'
        }).reset_index()
        acled_by_month.columns = ['YearMonth', 'Security_Events']
        
        # Fusion avec IDE
        acled_by_month['YearMonth_str'] = acled_by_month['YearMonth'].astype(str)
        
        acled_ide_data = acled_by_month.merge(
            ide_by_month[['YearMonth_str', 'IDE_Commitment']], 
            left_on='YearMonth_str', 
            right_on='YearMonth_str',
            how='left'
        ).fillna(0).sort_values('YearMonth')
        
        # Appliquer lag 6 mois
        acled_ide_data['IDE_Lag6'] = acled_ide_data['IDE_Commitment'].shift(-6)
        
        # Corrélation avec lag
        corr_acled_ide = acled_ide_data['Security_Events'].corr(acled_ide_data['IDE_Lag6'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Timeline: Security Events vs IDE (avec lag)
            fig_acled = go.Figure()
            
            # Incidents de sécurité
            fig_acled.add_trace(go.Bar(
                x=acled_ide_data['YearMonth_str'],
                y=acled_ide_data['Security_Events'],
                name='Incidents Sécurité (ACLED)',
                marker=dict(color='#d62728'),
                opacity=0.7,
                yaxis='y1'
            ))
            
            # IDE avec lag 6 mois
            fig_acled.add_trace(go.Scatter(
                x=acled_ide_data['YearMonth_str'],
                y=acled_ide_data['IDE_Lag6'] / 1e9,
                mode='lines+markers',
                name='IDE (t+6 mois)',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=6),
                yaxis='y2'
            ))
            
            fig_acled.update_layout(
                title=f"Incidents Sécurité → IDE avec décalage 6 mois<br><sub>Corrélation: {corr_acled_ide:.3f}</sub>",
                hovermode='x unified',
                height=400,
                template="plotly_white",
                yaxis=dict(
                    title="Incidents Sécurité (ACLED)",
                    title_font=dict(color="#d62728"),
                    tickfont=dict(color="#d62728")
                ),
                yaxis2=dict(
                    title="IDE Commitment (Milliards USD)",
                    title_font=dict(color="#2ca02c"),
                    tickfont=dict(color="#2ca02c"),
                    anchor="x",
                    overlaying="y",
                    side="right"
                )
            )
            
            st.plotly_chart(fig_acled, use_container_width=True)
        
        with col2:
            # Scatter ACLED vs IDE (lag)
            fig_scatter_acled = go.Figure()
            
            valid_data = acled_ide_data.dropna(subset=['Security_Events', 'IDE_Lag6'])
            
            fig_scatter_acled.add_trace(go.Scatter(
                x=valid_data['Security_Events'],
                y=valid_data['IDE_Lag6'] / 1e9,
                mode='markers',
                marker=dict(
                    size=10,
                    color=valid_data['Security_Events'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Incidents")
                ),
                text=[f"Incidents: {e:.0f}<br>IDE (t+6): ${i:.1f}B" 
                      for e, i in zip(valid_data['Security_Events'], valid_data['IDE_Lag6']/1e9)],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            # Fit line
            if len(valid_data) > 2:
                z = np.polyfit(valid_data['Security_Events'], valid_data['IDE_Lag6']/1e9, 1)
                p = np.poly1d(z)
                x_fit = np.linspace(valid_data['Security_Events'].min(), 
                                   valid_data['Security_Events'].max(), 100)
                fig_scatter_acled.add_trace(go.Scatter(
                    x=x_fit,
                    y=p(x_fit),
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', dash='dash', width=2)
                ))
            
            fig_scatter_acled.update_layout(
                title=f"Corrélation ACLED ↔ IDE (lag 6 mois)<br><sub>r={corr_acled_ide:.3f}</sub>",
                xaxis_title="Incidents Sécurité (ACLED)",
                yaxis_title="IDE Commitment (Milliards USD)",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_scatter_acled, use_container_width=True)
        
        # Insights ACLED
        st.markdown("#### Insight Sécurité (ACLED)")
        
        if corr_acled_ide < -0.10:
            st.markdown(f"""
            <div class="warning-box">
             <b>Impact Négatif Détecté:</b> Corrélation ACLED→IDE = <code>{corr_acled_ide:.3f}</code>
            
            **Interpretation:**
            - Plus il y a d'incidents sécuritaires un mois donné
            - Moins il y a d'IDE approuvés 6 mois plus tard
            - Les investisseurs attendent ~6 mois avant d'ajuster leurs engagements
            - **Recommandation:** Priorité à la stabilité sécuritaire pour attirer IDE
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            **Impact Sécurité:**
            Corrélation ACLED→IDE (lag 6 mois) = `{corr_acled_ide:.3f}`
            
            Relation modérée / non significative observée pendant cette période.
            """)
    
    else:
        if show_security:
            st.info(" Aucune donnée ACLED pour la période sélectionnée.")

# ============================================================================
# TAB 3: Q3 - PERCEPTION PAR SECTEUR
# ============================================================================

with tab3:
    st.subheader("🏭 Quels secteurs reçoivent meilleure perception médiatique ?")
    
    # Mapping secteurs simples
    sector_keywords = {
        'Santé': ['health', 'medical', 'hospital', 'vaccination', 'disease'],
        'Éducation': ['education', 'school', 'university', 'student'],
        'Agriculture': ['agriculture', 'farming', 'crop', 'farmer', 'harvest'],
        'Énergie': ['energy', 'power', 'electricity', 'solar', 'renewable'],
        'Eau': ['water', 'sanitation', 'irrigation', 'dam'],
        'Route': ['road', 'highway', 'transport', 'infrastructure'],
        'Environnement': ['environment', 'climate', 'forest', 'biodiversity'],
        'Réformes Macro': ['reform', 'economic', 'fiscal', 'budget', 'trade'],
        'Social': ['social', 'poverty', 'welfare', 'community'],
        'Gouvernance': ['administration', 'government', 'governance']
    }
    
    def map_sector(actor1, actor2):
        combined = f"{str(actor1).lower()} {str(actor2).lower()}"
        for sector, keywords in sector_keywords.items():
            for kw in keywords:
                if kw in combined:
                    return sector
        return 'Autre'
    
    df_event_filtered['Sector'] = df_event_filtered.apply(
        lambda r: map_sector(r['Actor1Name'], r['Actor2Name']), axis=1
    )
    
    sector_stats = df_event_filtered.groupby('Sector').agg({
        'GLOBALEVENTID': 'count',
        'NumArticles': 'sum',
        'AvgTone': 'mean',
        'NumMentions': 'sum'
    }).reset_index()
    
    sector_stats.columns = ['Sector', 'Events', 'Articles', 'Tone', 'Mentions']
    sector_stats = sector_stats[sector_stats['Sector'] != 'Autre'].sort_values('Articles', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart - Articles
        fig_sectors = go.Figure()
        fig_sectors.add_trace(go.Bar(
            y=sector_stats['Sector'],
            x=sector_stats['Articles'],
            orientation='h',
            marker=dict(
                color=sector_stats['Tone'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Tone"),
                cmin=-2,
                cmax=2
            ),
            text=sector_stats['Articles'],
            textposition='auto'
        ))
        
        fig_sectors.update_layout(
            title="Q3: Couverture médiatique par secteur",
            xaxis_title="Nombre d'articles",
            yaxis_title="Secteur",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_sectors, use_container_width=True)
    
    with col2:
        # Bubble chart - Tone vs Volume
        fig_bubble = go.Figure()
        fig_bubble.add_trace(go.Scatter(
            x=sector_stats['Tone'],
            y=sector_stats['Articles'],
            mode='markers+text',
            marker=dict(
                size=sector_stats['Mentions'] / 50,
                color=sector_stats['Articles'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Articles")
            ),
            text=sector_stats['Sector'],
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='<b>%{text}</b><br>Tone: %{x:.2f}<br>Articles: %{y:.0f}<extra></extra>'
        ))
        
        fig_bubble.add_vline(x=0, line_dash="dash", line_color="gray")
        
        fig_bubble.update_layout(
            title="Q3: Tone vs Volume (taille = mentions)",
            xaxis_title="Tone GDELT Moyen",
            yaxis_title="Nombre d'articles",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("#### Détails secteur")
    st.dataframe(
        sector_stats.sort_values('Articles', ascending=False).style.format({
            'Tone': '{:.3f}',
            'Articles': '{:.0f}',
            'Events': '{:.0f}',
            'Mentions': '{:.0f}'
        }),
        use_container_width=True
    )

# ============================================================================
# TAB 4: Q4 - HYPE vs REALITY
# ============================================================================

with tab4:
    st.subheader(" Attente vs Realité: Secteurs surestimé ?")
    
    # Calculer hype index (articles per project)
    project_sectors = df_project.copy()
    
    # Ajouter secteur simple (utiliser colonne si existe)
    if 'Secteur' in project_sectors.columns:
        project_by_sector = project_sectors.groupby('Secteur').agg({
            'Project Id': 'count',
            'IDA Commitment $US': 'sum'
        }).reset_index()
        project_by_sector.columns = ['Sector', 'Project_Count', 'Investment']
    else:
        st.warning(" Colonne 'Secteur' non trouvée. Affichage global.")
        project_by_sector = pd.DataFrame({
            'Sector': ['All Projects'],
            'Project_Count': [len(project_sectors)],
            'Investment': [project_sectors['IDA Commitment $US'].sum()]
        })
    
    # Fusionner avec stats GDELT
    hype_comparison = sector_stats.merge(
        project_by_sector,
        left_on='Sector',
        right_on='Sector',
        how='left'
    ).fillna(0)
    
    hype_comparison['Hype_Index'] = (
        hype_comparison['Articles'] / np.maximum(hype_comparison['Project_Count'], 1)
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hype Index
        hype_plot = hype_comparison.sort_values('Hype_Index', ascending=True).tail(10)
        
        fig_hype = go.Figure()
        fig_hype.add_trace(go.Bar(
            y=hype_plot['Sector'],
            x=hype_plot['Hype_Index'],
            orientation='h',
            marker=dict(
                color=hype_plot['Hype_Index'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Hype Index")
            ),
            text=hype_plot['Hype_Index'].round(0),
            textposition='auto'
        ))
        
        fig_hype.update_layout(
            title="Q4: Hype Index (Articles/Projet) - Top 10",
            xaxis_title="Articles par projet",
            yaxis_title="Secteur",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_hype, use_container_width=True)
    
    with col2:
        # Scatter - Hype vs Reality
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=hype_comparison['Hype_Index'],
            y=hype_comparison['Project_Count'],
            mode='markers+text',
            marker=dict(
                size=12,
                color=hype_comparison['Tone'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Tone")
            ),
            text=hype_comparison['Sector'],
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='<b>%{text}</b><br>Hype: %{x:.1f}<br>Projets: %{y:.0f}<extra></extra>'
        ))
        
        fig_scatter.update_layout(
            title="Q4: Hype Index vs Nombre de projets",
            xaxis_title="Articles/Projet (Hype Index)",
            yaxis_title="Nombre de projets",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Insight
    st.markdown("#### Insight Q4")
    
    top_hype = hype_comparison.nlargest(1, 'Hype_Index').iloc[0]
    
    st.markdown(f"""
    **Secteur le plus overhyped:** `{top_hype['Sector']}`
    - Articles: `{top_hype['Articles']:.0f}`
    - Projets réels: `{top_hype['Project_Count']:.0f}`
    - Hype Index: `{top_hype['Hype_Index']:.0f}` articles/projet
    
    **Implication:** 
    - Attention aux secteurs avec fort buzz médiatique mais avec peu de projets
    - Risque de déception vs attentes (media hype ≠ deliverables)
    - Prioriser secteurs avec ratio articles/projets équilibré
    """)

# ============================================================================
# TAB 5: PROJECTIONS ARIMA 2026-2028
# ============================================================================

with tab5:
    if show_projections:
        st.subheader(" Projections 2026-2028: ARIMA + Analyse Scénarios")
        
        # Préparer les séries temporelles
        df_event_monthly = df_event.copy()
        df_event_monthly['YearMonth'] = df_event_monthly['SQLDATE'].dt.to_period('M')
        
        tone_ts = df_event_monthly.groupby('YearMonth')['AvgTone'].mean()
        tone_ts.index = pd.to_datetime(tone_ts.index.astype(str))
        
        # IDE par mois
        df_project_for_ts = df_project.copy()
        df_project_for_ts['ApprovalMonth'] = df_project_for_ts['Board Approval Date'].dt.to_period('M')
        ide_ts = df_project_for_ts.groupby('ApprovalMonth')['IDA Commitment $US'].sum()
        ide_ts.index = pd.to_datetime(ide_ts.index.astype(str))
        
        # Remplir les mois manquants
        tone_ts = tone_ts.asfreq('MS', fill_value=tone_ts.mean())
        ide_ts = ide_ts.asfreq('MS', fill_value=0)
        
        # Onglets projections
        proj_tab1, proj_tab2 = st.tabs([" Projections ARIMA", " Scénarios Dynamiques"])
        
        with proj_tab1:
            st.markdown("#### Modèle: ARIMA - Auto-regressive Integrated Moving Average")
            st.markdown("""
            **Avantages:**
            - Capture tendances et saisonnalité
            - Basé sur données historiques observées
            - Intervalles de confiance pour incertitude
            
            **Limitations:**
            - Assume pattern passé continue (pas de choc externe)
            - Moins robuste avec peu de données
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Projection Tone GDELT**")
                
                try:
                    # Fit ARIMA sur tone
                    if len(tone_ts) >= 12:
                        model_tone = ARIMA(tone_ts, order=(1, 1, 1))
                        results_tone = model_tone.fit()
                        
                        # Prévoir 24 mois
                        forecast_tone = results_tone.get_forecast(steps=24)
                        forecast_tone_df = forecast_tone.conf_int(alpha=0.05)
                        forecast_tone_df['point_forecast'] = forecast_tone.predicted_mean
                        
                        # Graphique
                        fig_arima_tone = go.Figure()
                        
                        # Historique
                        fig_arima_tone.add_trace(go.Scatter(
                            x=tone_ts.index,
                            y=tone_ts.values,
                            mode='lines+markers',
                            name='Historique',
                            line=dict(color='#667eea', width=2),
                            marker=dict(size=4)
                        ))
                        
                        # Prévisions
                        fig_arima_tone.add_trace(go.Scatter(
                            x=forecast_tone_df.index,
                            y=forecast_tone_df['point_forecast'],
                            mode='lines+markers',
                            name='Forecast',
                            line=dict(color='#764ba2', width=2, dash='dash'),
                            marker=dict(size=4)
                        ))
                        
                        # Intervalle de confiance
                        fig_arima_tone.add_trace(go.Scatter(
                            x=forecast_tone_df.index.tolist() + forecast_tone_df.index.tolist()[::-1],
                            y=forecast_tone_df.iloc[:, 1].tolist() + forecast_tone_df.iloc[:, 0].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(118, 75, 162, 0.2)',
                            line=dict(color='rgba(255, 255, 255, 0)'),
                            name='IC 95%',
                            hoverinfo='skip'
                        ))
                        
                        fig_arima_tone.update_layout(
                            title=f"ARIMA(1,1,1) - Projection Tone GDELT<br><sub>AIC={results_tone.aic:.0f}</sub>",
                            xaxis_title="Période",
                            yaxis_title="Tone Prédit",
                            height=400,
                            hovermode='x unified',
                            template="plotly_white"
                        )
                        
                        st.plotly_chart(fig_arima_tone, use_container_width=True)
                        
                        st.markdown(f"""
                        **Diagnostics ARIMA:**
                        - AIC: `{results_tone.aic:.0f}`
                        - Paramètres: (1, 1, 1)
                        - Forecast 2026-2028: Tone moyen `{forecast_tone_df['point_forecast'].mean():.3f}`
                        """)
                    else:
                        st.warning(" Données insuffisantes pour ARIMA (min 12 mois)")
                
                except Exception as e:
                    st.error(f" Erreur ARIMA Tone: {str(e)}")
            
            with col2:
                st.markdown("**Projection IDE (IDA)**")
                
                try:
                    # Fit ARIMA sur IDE
                    if len(ide_ts) >= 12:
                        # Log transform pour stabiliser variance
                        ide_ts_log = np.log(ide_ts + 1)
                        
                        model_ide = ARIMA(ide_ts_log, order=(1, 1, 1))
                        results_ide = model_ide.fit()
                        
                        # Prévoir 24 mois
                        forecast_ide = results_ide.get_forecast(steps=24)
                        forecast_ide_df = forecast_ide.conf_int(alpha=0.05)
                        forecast_ide_df['point_forecast'] = forecast_ide.predicted_mean
                        
                        # Exp transform back
                        forecast_ide_df = np.exp(forecast_ide_df) - 1
                        
                        # Graphique
                        fig_arima_ide = go.Figure()
                        
                        # Historique
                        fig_arima_ide.add_trace(go.Bar(
                            x=ide_ts.index,
                            y=ide_ts.values / 1e9,
                            name='Historique',
                            marker=dict(color='#2ca02c'),
                            opacity=0.6
                        ))
                        
                        # Prévisions
                        fig_arima_ide.add_trace(go.Scatter(
                            x=forecast_ide_df.index,
                            y=forecast_ide_df['point_forecast'] / 1e9,
                            mode='lines+markers',
                            name='Forecast',
                            line=dict(color='#d62728', width=2, dash='dash'),
                            marker=dict(size=6)
                        ))
                        
                        # Intervalle de confiance
                        fig_arima_ide.add_trace(go.Scatter(
                            x=forecast_ide_df.index.tolist() + forecast_ide_df.index.tolist()[::-1],
                            y=(forecast_ide_df.iloc[:, 1] / 1e9).tolist() + (forecast_ide_df.iloc[:, 0] / 1e9).tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(214, 39, 40, 0.2)',
                            line=dict(color='rgba(255, 255, 255, 0)'),
                            name='IC 95%',
                            hoverinfo='skip'
                        ))
                        
                        fig_arima_ide.update_layout(
                            title=f"ARIMA(1,1,1) - Projection IDE (log-transform)<br><sub>AIC={results_ide.aic:.0f}</sub>",
                            xaxis_title="Période",
                            yaxis_title="IDE Commitment (Milliards USD)",
                            height=400,
                            hovermode='x unified',
                            template="plotly_white"
                        )
                        
                        st.plotly_chart(fig_arima_ide, use_container_width=True)
                        
                        st.markdown(f"""
                        **Diagnostics ARIMA:**
                        - AIC: `{results_ide.aic:.0f}`
                        - Paramètres: (1, 1, 1) - Log transform
                        - Forecast 2026-2028: IDE moyen `${forecast_ide_df['point_forecast'].mean()/1e9:.2f}B`
                        """)
                    else:
                        st.warning("⚠️ Données insuffisantes pour ARIMA IDE")
                
                except Exception as e:
                    st.error(f" Erreur ARIMA IDE: {str(e)}")
        
        with proj_tab2:
            st.markdown("#### 🎬 Scénarios Dynamiques (Sensibilité)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                scenario_security = st.slider(
                    " Amélioration Sécurité",
                    0, 100, 50,
                    help="0%=Status quo, 100%=Amélioration complète"
                )
            
            with col2:
                scenario_communication = st.slider(
                    " Amélioration Communication",
                    0, 100, 50,
                    help="Renforcement stratégie média internationale"
                )
            
            with col3:
                scenario_reform = st.slider(
                    "⚙️ Réformes Économiques",
                    0, 100, 50,
                    help="Politiques macroéconomiques"
                )
            
            # Calculs de scénario
            baseline_tone = tone_ts.mean()
            baseline_ide = ide_ts[ide_ts > 0].mean()
            
            # Impacts (basés sur corrélations Q2)
            tone_delta = (
                (scenario_communication / 100) * 0.5 +
                (scenario_security / 100) * 0.3 -
                ((100 - scenario_reform) / 100) * 0.2
            )
            
            ide_delta = (
                (scenario_communication / 100) * 0.18 * baseline_ide +
                (scenario_security / 100) * (-0.13) * baseline_ide +
                (scenario_reform / 100) * 0.25 * baseline_ide
            )
            
            # Projection
            projection_months = np.arange(0, 25)
            projected_tone = baseline_tone + (tone_delta / 24) * projection_months
            projected_ide = baseline_ide + (ide_delta / 24) * projection_months
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scen_tone = go.Figure()
                fig_scen_tone.add_trace(go.Scatter(
                    x=list(range(25)),
                    y=projected_tone,
                    mode='lines+markers',
                    name='Scénario',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=5),
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.2)'
                ))
                fig_scen_tone.add_hline(y=baseline_tone, line_dash="dash", 
                                       line_color="gray", annotation_text="Baseline")
                
                fig_scen_tone.update_layout(
                    title=f"Scénario Tone (Sec:{scenario_security}% | Comm:{scenario_communication}% | Réf:{scenario_reform}%)",
                    xaxis_title="Mois",
                    yaxis_title="Tone",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_scen_tone, use_container_width=True)
            
            with col2:
                fig_scen_ide = go.Figure()
                fig_scen_ide.add_trace(go.Scatter(
                    x=list(range(25)),
                    y=projected_ide / 1e9,
                    mode='lines+markers',
                    name='Scénario',
                    line=dict(color='#2ca02c', width=3),
                    marker=dict(size=5),
                    fill='tozeroy',
                    fillcolor='rgba(44, 160, 44, 0.2)'
                ))
                fig_scen_ide.add_hline(y=baseline_ide/1e9, line_dash="dash",
                                      line_color="gray", annotation_text="Baseline")
                
                fig_scen_ide.update_layout(
                    title=f"Scénario IDE (Sec:{scenario_security}% | Comm:{scenario_communication}% | Réf:{scenario_reform}%)",
                    xaxis_title="Mois",
                    yaxis_title="IDE (Milliards USD)",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_scen_ide, use_container_width=True)
            
            # Métriques
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(" Tone Baseline", f"{baseline_tone:.3f}", 
                         f"{tone_delta:.3f}",  delta_color="inverse" if tone_delta < 0 else "normal")
            
            with col2:
                st.metric(" Tone 2028", f"{projected_tone[-1]:.3f}",
                         f"{projected_tone[-1] - baseline_tone:+.3f}", 
                         delta_color="inverse" if (projected_tone[-1] - baseline_tone) < 0 else "normal")
            
            with col3:
                st.metric(" IDE Baseline", f"${baseline_ide/1e9:.2f}B", 
                         "Référence")
            
            with col4:
                st.metric(" IDE 2028", f"${projected_ide[-1]/1e9:.2f}B",
                         f"{(projected_ide[-1] / max(baseline_ide, 1e6) - 1)*100:+.0f}%",
                         delta_color="normal" if projected_ide[-1] >= baseline_ide else "inverse")
    
    else:
        st.info("💡 Activez 'Afficher projections ARIMA' dans la sidebar")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85em;'>
    <p> Dashboard Bénin Economic Governance | Hackathon iSHEERO × DataCamp 2026</p>
    <p>Données: GDELT, GKG, Project_List (World Bank), ACLED | Période: 2021-2026</p>
    <p><em>Les prévisions ARIMA sont basées sur les patterns historiques. Les résultats réels peuvent différer.</em></p>
    <p><b>ACLED Impact:</b> Corrélation calculée avec décalage 6 mois (t+6)</p>
</div>
""", unsafe_allow_html=True)
