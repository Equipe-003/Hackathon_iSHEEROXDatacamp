"""
Dashboard Streamlit - Analyse de la Gouvernance Économique du Bénin (2021-2026)
Hackathon iSHEERO × DataCamp - Bénin Insights Challenge

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

# ============================================================================
# CONFIG STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Bénin Economic Governance Dashboard",
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
    # 1. On se situe dans 'dashboard/', on remonte à la racine avec '..'
    # Ensuite on descend dans 'data' puis 'processed'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(base_dir, '..', 'data', 'processed')

    # 2. Définition des chemins
    files = {
        'gkg': os.path.join(processed_dir, 'gkg_2021_2026_cleaned', 'gkg_2021_2026_cleaned.csv'),
        'event': os.path.join(processed_dir, 'events_2021_2026_cleaned.csv'),
        'project': os.path.join(processed_dir, 'Project_List_Cleaned_1.csv'),
        'acled': os.path.join(processed_dir, 'acled_filtered_2021_2025.csv')
    }

    # 3. Chargement
    df_gkg = pd.read_csv(files['gkg'])
    df_event = pd.read_csv(files['event'])
    df_project = pd.read_csv(files['project'])
    df_acled = pd.read_csv(files['acled'])
    
    # 4. Transformations (ajustez selon vos colonnes réelles)
    df_event['SQLDATE'] = pd.to_datetime(df_event['SQLDATE'], format='%Y%m%d')
    df_project['Board Approval Date'] = pd.to_datetime(df_project['Board Approval Date'], errors='coerce')
    df_acled['WEEK'] = pd.to_datetime(df_acled['WEEK'], errors='coerce')
    df_acled = df_acled.rename(columns={'WEEK': 'EVENT_DATE'})
    
    return df_gkg, df_event, df_project, df_acled

# Charger les données
with st.spinner('📊 Chargement des données...'):
    df_gkg, df_event, df_project, df_acled = load_data()

# ============================================================================
# 2. SIDEBAR - FILTRES
# ============================================================================

st.sidebar.markdown("## 🎛️ FILTRES")
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
].copy()

df_project_filtered = df_project[
    (df_project['Board Approval Date'] >= start_date) & 
    (df_project['Board Approval Date'] <= end_date)
].copy()

# Options additionnelles
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 OPTIONS")

show_security = st.sidebar.checkbox("Inclure impact sécurité (ACLED)", value=True)
show_projections = st.sidebar.checkbox("Afficher projections", value=True)

# ============================================================================
# 3. HEADER
# ============================================================================

st.markdown("""
# 🇧🇯 Bénin Economic Governance Dashboard
## 2021-2026 | Analyse Perception Médiatique & Investissements IDE
*Hackathon iSHEERO × DataCamp - Bénin Insights Challenge*
""")

st.markdown("---")

# ============================================================================
# 4. MÉTRIQUES CLÉS (KPI CARDS)
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_articles = df_event_filtered['NumArticles'].sum()
    st.metric(
        "📰 Articles GDELT",
        f"{total_articles:,.0f}",
        f"+{total_articles / len(df_event_filtered):.0f} /événement" if len(df_event_filtered) > 0 else "N/A"
    )

with col2:
    avg_tone = df_event_filtered['AvgTone'].mean()
    tone_color = "🟢" if avg_tone > 0 else "🔴" if avg_tone < 0 else "⚪"
    st.metric(
        "🎯 Tone GDELT Moyen",
        f"{avg_tone:.3f}",
        f"{tone_color} {'Positif' if avg_tone > 0 else 'Négatif'}"
    )

with col3:
    total_ide = df_project_filtered['IDA Commitment $US'].sum() / 1e9
    st.metric(
        "💰 IDE Total (IDA)",
        f"${total_ide:.2f}B",
        f"{len(df_project_filtered)} projets"
    )

with col4:
    security_events = len(df_acled_filtered) if show_security else 0
    st.metric(
        "🔒 Incidents Sécurité (ACLED)",
        f"{security_events}",
        "En période d'analyse" if show_security else "Désactivé"
    )

st.markdown("---")

# ============================================================================
# 5. CRÉATION DES ONGLETS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Q1: Perception Internationale",
    "🔗 Q2: Médias vs IDE (+ Sécurité)",
    "🏭 Q3: Perception Secteurs",
    "📈 Q4: Hype vs Reality",
    "🔮 Projections 2026-2028"
])

# ============================================================================
# TAB 1: Q1 - PERCEPTION INTERNATIONALE
# ============================================================================

with tab1:
    st.subheader("📊 Comment l'économie du Bénin est perçue à l'international ?")
    
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
        st.markdown("#### 📈 Statistiques")
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
    st.markdown("#### 💡 Insight Q1")
    st.markdown("""
    Le tone GDELT reflète la perception médiatique internationale du Bénin. 
    Une valeur positive indique une couverture favorable, une valeur négative? en dessous de -O.5,
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
    st.subheader("🔗 Corrélation: Ton des Médias International/National & IDE (Impact Sécurité)")
    
    # Agrégation mensuelle pour corrélation
    df_event_monthly = df_event_filtered.copy()
    df_event_monthly['YearMonth'] = df_event_monthly['SQLDATE'].dt.to_period('M')
    
    media_by_month = df_event_monthly.groupby('YearMonth').agg({
        'AvgTone': 'mean',
        'NumArticles': 'sum'
    }).reset_index()
    
    # IDE par mois d'approbation
    df_project_filtered['ApprovalMonth'] = df_project_filtered['Board Approval Date'].dt.to_period('M')
    ide_by_month = df_project_filtered.groupby('ApprovalMonth')['IDA Commitment $US'].sum().reset_index()
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
        st.markdown("#### 📊 Résultats Clés (INSIGHTS1)")
        st.markdown("""
        **Médias Internationaux vs IDE:**
        - Légère Corrélation: `+0.17` ✅
        - Relation positive après décalage 6 mois
        - Les articles positifs sur le temps pourraient influencé les approbations IDE
        """)
        
        if show_security:
            st.markdown("#### 🔒 Impact Sécuritaire")
            security_events_count = len(df_acled_filtered)
            st.markdown(f"""
            **Incidents sécurité (période):** `{security_events_count}`
            
            **Corrélation Sécurité + IDE:**
            - Impact ACLED: `-0.13` 🔴
            - Tensions ↓ → IDE ↓
            """)
    
    st.markdown("---")
    st.markdown("""
    #### 💡 Insight Q2
    
    **Paradoxe interne/externe:** Les investisseurs étrangers se basent sur la couverture
    médiatique internationale (positif), PAS sur les débats locaux. Les tensions sécuritaires
    freinent les IDE (-0.13), mais les médias mondiaux restent positifs sur l'économie (+0.11).
    
    **Implication:** La stratégie de communication doit cibler les médias internationaux,
    pas les débats domestiques. La sécurité est un facteur majeur (à traiter en parallèle).
    """)

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
    st.markdown("#### 📋 Détails secteur")
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
    st.subheader("📈 Hype vs Reality: Secteurs overhypés ?")
    
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
        st.warning("⚠️ Colonne 'Secteur' non trouvée. Affichage global.")
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
    st.markdown("#### 💡 Insight Q4")
    
    top_hype = hype_comparison.nlargest(1, 'Hype_Index').iloc[0]
    
    st.markdown(f"""
    **Secteur le plus overhyped:** `{top_hype['Sector']}`
    - Articles: `{top_hype['Articles']:.0f}`
    - Projets réels: `{top_hype['Project_Count']:.0f}`
    - Hype Index: `{top_hype['Hype_Index']:.0f}` articles/projet
    
    **Implication:** 
    - ⚠️ Attention aux secteurs avec fort buzz médiatique mais peu de projets
    - Risque de déception vs attentes (media hype ≠ deliverables)
    - Prioriser secteurs avec ratio articles/projets équilibré
    """)

# ============================================================================
# TAB 5: PROJECTIONS 2026-2028
# ============================================================================

with tab5:
    if show_projections:
        st.subheader("🔮 Projections 2026-2028: Scénarios Dynamiques")
        
        # Paramètres de scénario
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scenario_security = st.slider(
                "🔒 Amélioration Sécurité",
                0, 100, 50,
                help="0%=Status quo, 100%=Amélioration complète"
            )
        
        with col2:
            scenario_communication = st.slider(
                "📢 Amélioration Communication",
                0, 100, 50,
                help="Renforcement stratégie média internationale"
            )
        
        with col3:
            scenario_reform = st.slider(
                "⚙️ Réformes Économiques",
                0, 100, 50,
                help="Politiques macroéconomiques"
            )
        
        st.markdown("---")
        
        # Calculs de projection
        # Baseline: tone actuel
        baseline_tone = df_event_filtered['AvgTone'].mean()
        baseline_ide = df_project_filtered['IDA Commitment $US'].sum()
        
        # Impacts estimés (basés sur corrélations Q2)
        tone_delta = (
            (scenario_communication / 100) * 0.5 +  # Communication impact
            (scenario_security / 100) * 0.3 -        # Sécurité impact (négatif si bas)
            (scenario_reform / 100) * 0.2            # Réforme impact
        )
        
        ide_delta = (
            (scenario_communication / 100) * 0.18 * baseline_ide +  # Positif si meilleure comm
            (scenario_security / 100) * (-0.13) * baseline_ide +    # Négatif si tensions
            (scenario_reform / 100) * 0.25 * baseline_ide           # Réformes positives
        )
        
        # Projection mensuelle 2026-2028
        projection_months = np.arange(0, 25)  # 24 mois + baseline
        projected_tone = baseline_tone + (tone_delta / 24) * projection_months
        projected_ide = baseline_ide + (ide_delta / 24) * projection_months
        
        # Dates
        last_date = df_event_filtered['SQLDATE'].max()
        projection_dates = [last_date + timedelta(days=30*i) for i in range(25)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Projection Tone
            fig_proj_tone = go.Figure()
            
            # Historique
            historical_tone = tone_by_month.tail(12)
            fig_proj_tone.add_trace(go.Scatter(
                x=historical_tone['YearMonth'],
                y=historical_tone['AvgTone'],
                mode='lines+markers',
                name='Historique',
                line=dict(color='#667eea', width=2),
                marker=dict(size=5)
            ))
            
            # Projection
            fig_proj_tone.add_trace(go.Scatter(
                x=[d.strftime('%Y-%m') for d in projection_dates],
                y=projected_tone,
                mode='lines+markers',
                name='Projection',
                line=dict(color='#764ba2', width=2, dash='dash'),
                marker=dict(size=5),
                fill='tozeroy',
                fillcolor='rgba(118, 75, 162, 0.2)'
            ))
            
            fig_proj_tone.update_layout(
                title=f"Projection Tone GDELT<br><sub>Sécurité:{scenario_security}% | Comm:{scenario_communication}% | Réforme:{scenario_reform}%</sub>",
                xaxis_title="Période",
                yaxis_title="Tone Prédit",
                hovermode='x unified',
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_proj_tone, use_container_width=True)
        
        with col2:
            # Projection IDE
            fig_proj_ide = go.Figure()
            
            # Projection
            fig_proj_ide.add_trace(go.Scatter(
                x=[d.strftime('%Y-%m') for d in projection_dates],
                y=projected_ide / 1e9,
                mode='lines+markers',
                name='IDE Projeté',
                line=dict(color='#2ca02c', width=2, dash='dash'),
                marker=dict(size=5),
                fill='tozeroy',
                fillcolor='rgba(44, 160, 44, 0.2)'
            ))
            
            fig_proj_ide.add_hline(
                y=baseline_ide / 1e9,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Baseline: ${baseline_ide/1e9:.2f}B",
                annotation_position="right"
            )
            
            fig_proj_ide.update_layout(
                title=f"Projection IDE (IDA)<br><sub>Sécurité:{scenario_security}% | Comm:{scenario_communication}% | Réforme:{scenario_reform}%</sub>",
                xaxis_title="Période",
                yaxis_title="IDE Commitment (Milliards USD)",
                hovermode='x unified',
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_proj_ide, use_container_width=True)
        
        # Résumé scénario
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Tone Baseline",
                f"{baseline_tone:.3f}",
                f"{tone_delta:.3f}" if tone_delta >= 0 else f"{tone_delta:.3f}",
                delta_color="inverse" if tone_delta < 0 else "normal"
            )
        
        with col2:
            projected_final_tone = projected_tone[-1]
            st.metric(
                "🔮 Tone 2028 (Estimé)",
                f"{projected_final_tone:.3f}",
                f"{projected_final_tone - baseline_tone:+.3f}",
                delta_color="inverse" if (projected_final_tone - baseline_tone) < 0 else "normal"
            )
        
        with col3:
            st.metric(
                "💰 IDE Baseline (2021-2026)",
                f"${baseline_ide/1e9:.2f}B",
                f"{baseline_ide/1e9:.2f}B"
            )
        
        with col4:
            projected_final_ide = projected_ide[-1]
            delta_ide = projected_final_ide - baseline_ide
            st.metric(
                "🔮 IDE 2028 (Estimé)",
                f"${projected_final_ide/1e9:.2f}B",
                f"{delta_ide/1e9:+.2f}B",
                delta_color="normal" if delta_ide >= 0 else "inverse"
            )
        
        # Insight
        st.markdown("---")
        st.markdown("#### 💡 Insight Projections")
        
        if scenario_security >= 70 and scenario_communication >= 70:
            st.success("✅ Scénario optimal: Amélioration sécurité + communication forte → IDE en croissance")
        elif scenario_security < 30:
            st.warning("⚠️ Tensions sécuritaires → Frein majeur aux IDE (même avec bonne communication)")
        else:
            st.info("ℹ️ Scénario modéré: Amélioration progressive basée sur les actions gouvernementales")
        
        st.markdown(f"""
        **Analyse du scénario:**
        
        - **Tone projection 2028:** `{projected_final_tone:.3f}` (vs baseline `{baseline_tone:.3f}`)
        - **IDE projection 2028:** `${projected_final_ide/1e9:.2f}B` (vs baseline `${baseline_ide/1e9:.2f}B`)
        - **Facteur de croissance IDE:** `{(projected_final_ide / max(baseline_ide, 1) - 1)*100:+.1f}%`
        
        **Recommandations:**
        1. Priorité sécurité: Impact majeur sur IDE (-0.13 corrélation)
        2. Renforcer communication médias internationaux: +0.18 corrélation avec IDE
        3. Réformes économiques: Support supplémentaire pour attractivité
        """)
    
    else:
        st.info("💡 Activez 'Afficher projections' dans la sidebar pour voir les scénarios 2026-2028")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85em;'>
    <p>📊 Dashboard Bénin Economic Governance | Hackathon iSHEERO × DataCamp 2026</p>
    <p>Données: GDELT, GKG, Project_List (World Bank), ACLED | Période: 2021-2026</p>
    <p><em>Les projections sont basées sur les corrélations observées. Les résultats réels peuvent différer.</em></p>
</div>
""", unsafe_allow_html=True)
