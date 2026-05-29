import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin Insights — Phase 2",
    layout="wide",
    initial_sidebar_state="expanded"
)

PALETTE = {
    "primary":   "#1D6FA4",
    "secondary": "#1D9E75",
    "accent":    "#E24B4A",
    "warning":   "#EF9F27",
    "neutral":   "#6C757D",
    "positive":  "#2ECC71",
    "negative":  "#E74C3C",
    "purple":    "#7F77DD",
    "amber":     "#BA7517",
}

# ── Chemins des fichiers ──────────────────────────────────────────────────────
# Adapter selon votre repo :
#   outputs/dashboard_dataset.csv   → produit par le notebook Phase 2
#   outputs/scenarios_pag.csv       → produit par le notebook Phase 2
#   outputs/kpis_dashboard.json     → produit par le notebook Phase 2
#   outputs/*.png                   → images produites par le notebook Phase 2
#   gdelt_bn_2025.csv               → données Phase 1 (déjà présentes)
#   gdelt_gkg_bn_V2Tone.csv         → données Phase 1 (déjà présentes)

current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = Path(current_dir) / "outputs"


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_phase1_data():
    """Charge les données Phase 1 (events + GKG) — identique à l'app Phase 1."""
    path_ev  = os.path.join(current_dir, "gdelt_bn_2025.csv")
    path_gkg = os.path.join(current_dir, "gdelt_gkg_bn_V2Tone.csv")
    df_ev  = pd.read_csv(path_ev,  low_memory=False)
    df_gkg = pd.read_csv(path_gkg, low_memory=False)

    for col in ["GoldsteinScale", "AvgTone", "ActionGeo_Lat", "ActionGeo_Long"]:
        if col in df_ev.columns:
            df_ev[col] = pd.to_numeric(df_ev[col], errors='coerce')

    df_ev['Date_Ok']    = pd.to_datetime(df_ev['SQLDATE'].astype(str), format='%Y%m%d', errors='coerce')
    df_ev['Month_Name'] = df_ev['Date_Ok'].dt.month_name()
    df_ev = df_ev.drop_duplicates(subset=['GLOBALEVENTID'])

    quad_mapping = {1:"Coopération Verbale", 2:"Coopération Matérielle",
                    3:"Conflit Verbal", 4:"Conflit Matériel"}
    df_ev['Type_evenement'] = df_ev['QuadClass'].map(quad_mapping)

    tone_sep = df_gkg['V2Tone'].astype(str).str.split(',', expand=True)
    df_gkg['Tonnalite']     = pd.to_numeric(tone_sep[0], errors='coerce')
    df_gkg['Mots_Positifs'] = pd.to_numeric(tone_sep[1], errors='coerce')
    df_gkg['Mots_Negatifs'] = pd.to_numeric(tone_sep[2], errors='coerce')
    df_gkg['Date']          = pd.to_datetime(df_gkg['Date'].astype(str).str[:8], format='%Y%m%d', errors='coerce')

    internationaux = ['reuters','bbc','lemonde','afp','rfi','apnews','aljazeera','theguardian','france24']
    source_col = 'SourceCommonName' if 'SourceCommonName' in df_gkg.columns else \
                 ('DocumentIdentifier' if 'DocumentIdentifier' in df_gkg.columns else None)
    if source_col:
        df_gkg['Origine_Media'] = df_gkg[source_col].apply(
            lambda x: "Médias Internationaux"
            if any(s in str(x).lower() for s in internationaux)
            else "Médias Francophones/Nationaux"
        )
    else:
        df_gkg['Origine_Media'] = "Médias Francophones/Nationaux"

    return df_ev, df_gkg


@st.cache_data
def load_phase2_data():
    """Charge les outputs du notebook Phase 2 (dataset unifié + scénarios + KPIs)."""
    dataset_path   = OUTPUTS_DIR / "dashboard_dataset.csv"
    scenarios_path = OUTPUTS_DIR / "scenarios_pag.csv"
    kpis_path      = OUTPUTS_DIR / "kpis_dashboard.json"

    df_unified  = pd.read_csv(dataset_path)  if dataset_path.exists()  else pd.DataFrame()
    df_scenarios = pd.read_csv(scenarios_path) if scenarios_path.exists() else pd.DataFrame()

    kpis = {}
    if kpis_path.exists():
        with open(kpis_path, encoding="utf-8") as f:
            kpis = json.load(f)

    return df_unified, df_scenarios, kpis


@st.cache_data
def load_corr_matrix():
    """Charge la matrice de corrélation depuis l'image générée."""
    path = OUTPUTS_DIR / "correlation_matrix.png"
    return str(path) if path.exists() else None


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
df_ev_raw, df_gkg_raw = load_phase1_data()
df_unified, df_scenarios, kpis = load_phase2_data()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🇧🇯 Bénin Insights 2025")
st.sidebar.markdown("**Hackathon iSHEERO × DataCamp 2026**")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Vue d'ensemble",
        "📊 Analyse Phase 1",
        "🔗 Corrélations causales",
        "🤖 Modèle bayésien",
        "🎯 Simulateur de décisions",
        "📍 Carte & Événements",
    ]
)

st.sidebar.divider()

# Filtres temporels (Phase 1)
min_d = df_ev_raw['Date_Ok'].min().date()
max_d = df_ev_raw['Date_Ok'].max().date()
date_selection = st.sidebar.date_input("Période d'analyse", [min_d, max_d])

media_options   = df_gkg_raw['Origine_Media'].unique().tolist()
media_selection = st.sidebar.multiselect("Origine des médias", options=media_options, default=media_options)

# Filtrage Phase 1
if len(date_selection) == 2:
    start, end = date_selection
    df_gkg_filtered = df_gkg_raw[
        (df_gkg_raw['Date'].dt.date >= start) &
        (df_gkg_raw['Date'].dt.date <= end) &
        (df_gkg_raw['Origine_Media'].isin(media_selection))
    ].copy()
    df_ev_filtered = df_ev_raw[
        (df_ev_raw['Date_Ok'].dt.date >= start) &
        (df_ev_raw['Date_Ok'].dt.date <= end)
    ].copy()
else:
    df_gkg_filtered = df_gkg_raw.copy()
    df_ev_filtered  = df_ev_raw.copy()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — VUE D'ENSEMBLE (KPIs Phase 2)
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Vue d'ensemble":
    st.title("🇧🇯 Bénin Insights Challenge — Tableau de bord Phase 2")
    st.markdown(
        "Analyse croisée **GDELT × PAG 2021-2026** | "
        "Modélisation bayésienne | Aide à la décision publique"
    )

    # ── KPIs principaux ──────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Ton médiatique moyen",
            f"{kpis.get('ton_moyen_global', 'N/A'):.2f}" if kpis else "N/A",
            help="AvgTone pondéré par NumMentions — négatif < 0 < positif"
        )
    with col2:
        st.metric(
            "Mois le plus négatif",
            kpis.get("mois_le_plus_negatif", "N/A"),
            delta="Pic critique",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            "Mois le moins négatif",
            kpis.get("mois_le_plus_positif", "N/A"),
            delta="Meilleure fenêtre comm.",
            delta_color="normal"
        )
    with col4:
        st.metric(
            "GoldsteinScale moyen",
            f"{kpis.get('goldstein_moyen_global', 'N/A'):.2f}" if kpis else "N/A",
            help="De -10 (conflit) à +10 (coopération)"
        )
    with col5:
        st.metric(
            "Mois analysés",
            kpis.get("nb_mois_analyses", "N/A"),
            help="Mois couverts par le dataset unifié"
        )

    st.divider()

    # ── Résumé analytique ─────────────────────────────────────────────────────
    st.subheader("💡 5 Insights clés — Phase 2")

    insights = [
        ("🔴", "Alerte décembre 2025",
         "Le mois de décembre 2025 présente un ton médiatique de **-2.49**, "
         "soit le double de la moyenne annuelle. Cela correspond à la tentative "
         "de coup d'État. Notre pipeline l'aurait signalé dès les premiers jours "
         "via la chute du GoldsteinScale."),
        ("🟢", "Octobre 2025 — fenêtre d'opportunité",
         "Avec un ton de **-0.21**, octobre est le mois le moins négatif de 2025. "
         "C'est la meilleure fenêtre de communication pour des annonces PAG à fort "
         "impact médiatique international."),
        ("🔗", "Corrélation conflit → ton (r = -0.87)",
         "La proportion d'événements conflictuels est le **prédicteur le plus fort** "
         "du ton médiatique (r = -0.87). Réduire les conflits médiatisés améliore "
         "la perception internationale plus efficacement que toute autre variable."),
        ("🎯", "Simulateur PAG : l'amélioration combinée est la plus efficace",
         "Une amélioration simultanée des indicateurs PAG (santé + électricité + PIB) "
         "porte la probabilité d'un ton acceptable à **19%** vs **11%** en status quo. "
         "Aucun investissement sectoriel isolé ne suffit."),
        ("⚖️", "Incertitude quantifiée — avantage du bayésien",
         "Avec 12 mois de données, les intervalles de crédibilité sont larges. "
         "Le modèle bayésien **dit honnêtement qu'il ne sait pas assez**. "
         "En 2026, avec 4 ans de données PAG, les coefficients se resserreront."),
    ]

    for emoji, titre, texte in insights:
        with st.expander(f"{emoji} {titre}"):
            st.markdown(texte)

    st.divider()

    # ── Évolution mensuelle du ton (Phase 1 data, style Phase 2) ─────────────
    st.subheader("📈 Évolution du ton médiatique 2025 — Vue décisionnelle")

    if not df_unified.empty:
        fig_tone = go.Figure()

        # Zone positive / négative
        fig_tone.add_hrect(y0=-0.5, y1=0.5, fillcolor="rgba(46,204,113,0.05)",
                            line_width=0, annotation_text="Zone neutre")

        fig_tone.add_trace(go.Scatter(
            x=df_unified['year_month'],
            y=df_unified['ton_moyen_pondere'],
            mode='lines+markers',
            name='Ton médiatique',
            line=dict(color=PALETTE['primary'], width=2.5),
            marker=dict(
                size=df_unified['buzz_mensuel'] / df_unified['buzz_mensuel'].max() * 20 + 6,
                color=[PALETTE['negative'] if t < -2 else
                       PALETTE['warning'] if t < -1 else
                       PALETTE['secondary'] for t in df_unified['ton_moyen_pondere']],
                line=dict(width=1.5, color='white')
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Ton : %{y:.2f}<br>"
                "Buzz : %{customdata[0]:,.0f} mentions<br>"
                "<extra></extra>"
            ),
            customdata=df_unified[['buzz_mensuel']].values
        ))

        # Ligne seuil d'alerte
        fig_tone.add_hline(y=-2.0, line_dash="dash", line_color=PALETTE['accent'],
                            annotation_text="Seuil d'alerte critique (-2.0)",
                            annotation_position="bottom right")
        fig_tone.add_hline(y=0, line_color="black", line_width=0.8)

        # Annotations octobre et décembre
        for _, row in df_unified.iterrows():
            if row['year_month'] in ['2025-10', '2025-12']:
                label = "✅ Meilleure fenêtre" if row['year_month'] == '2025-10' else "🚨 Crise"
                fig_tone.add_annotation(
                    x=row['year_month'], y=row['ton_moyen_pondere'],
                    text=label, showarrow=True, arrowhead=2,
                    font=dict(size=10, color=PALETTE['primary']),
                    bgcolor="white", bordercolor=PALETTE['primary'], borderwidth=1,
                    ay=-40 if row['year_month'] == '2025-12' else 40
                )

        fig_tone.update_layout(
            title="Ton médiatique mensuel pondéré — Taille des points ∝ volume de couverture",
            xaxis_title="Mois",
            yaxis_title="Ton moyen (AvgTone pondéré)",
            template="plotly_white",
            hovermode="x unified",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_tone, use_container_width=True)

        st.caption(
            "Lecture : points rouges = mois de crise (ton < -2) | "
            "orange = mois négatifs | vert = mois acceptables | "
            "taille des points ∝ volume de couverture médiatique"
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — ANALYSE PHASE 1 (repris de l'app originale)
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Analyse Phase 1":
    st.title("📊 Analyse de la couverture médiatique — Phase 1")
    st.info(
        "Données GDELT 2025 — Couverture mondiale du Bénin. "
        "Utilisez les filtres dans la barre latérale pour affiner l'analyse."
    )

    # Carte
    st.subheader("📍 Localisation des événements")
    df_map = (
        df_ev_filtered
        .dropna(subset=['ActionGeo_Lat', 'ActionGeo_Long'])
        .groupby(['ActionGeo_Lat', 'ActionGeo_Long', 'Type_evenement'], dropna=False)
        .agg(Nombre_Evenements=('GLOBALEVENTID', 'count'), Premiere_Date=('Date_Ok', 'min'))
        .reset_index()
    )
    df_map['Premiere_Date'] = df_map['Premiere_Date'].dt.strftime('%Y-%m-%d')

    fig_map = px.scatter_mapbox(
        df_map, lat="ActionGeo_Lat", lon="ActionGeo_Long",
        color="Type_evenement", size="Nombre_Evenements", size_max=15,
        hover_data={'Premiere_Date': True, 'Nombre_Evenements': True},
        color_discrete_map={
            "Coopération Verbale":    PALETTE['secondary'],
            "Coopération Matérielle": "#5DCAA5",
            "Conflit Verbal":         PALETTE['warning'],
            "Conflit Matériel":       PALETTE['accent'],
        },
        mapbox_style="carto-positron", zoom=6
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend_title_text='Type')
    st.plotly_chart(fig_map, use_container_width=True)
    st.divider()

    # Tonalité GKG
    st.subheader("📉 Tonalité médiatique par date")
    df_avg = df_gkg_filtered.groupby(['Date', 'Origine_Media'])['Tonnalite'].mean().reset_index()
    fig_avg = px.line(
        df_avg, x='Date', y='Tonnalite', color='Origine_Media',
        template="plotly_white",
        color_discrete_map={"Médias Internationaux": PALETTE['primary'],
                            "Médias Francophones/Nationaux": PALETTE['secondary']},
        labels={'Tonnalite': 'Tonalité moyenne', 'Date': 'Date'}
    )
    fig_avg.add_hline(y=0, line_color="black", line_width=0.8)
    fig_avg.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_avg, use_container_width=True)
    st.divider()

    # Volume d'articles
    st.subheader("📊 Volume d'articles par date")
    df_count = (
        df_gkg_filtered.groupby(['Date', 'Origine_Media'])['Tonnalite']
        .count().reset_index().rename(columns={'Tonnalite': 'Nombre_Articles'})
    )
    fig_count = px.area(
        df_count, x='Date', y='Nombre_Articles', color='Origine_Media',
        template="plotly_white",
        color_discrete_map={"Médias Internationaux": PALETTE['primary'],
                            "Médias Francophones/Nationaux": PALETTE['secondary']},
        labels={'Nombre_Articles': "Nombre d'articles", 'Date': 'Date'}
    )
    fig_count.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_count, use_container_width=True)

    with st.expander("📝 Analyse détaillée"):
        st.write("""
        L'analyse met en lumière une fracture lors du mois de décembre 2025. Alors que
        le graphique de volume révèle une explosion du nombre de publications, la courbe
        de tonalité moyenne montre une chute brutale, plongeant sous la barre des -5.
        Cette divergence confirme une crise médiatique majeure où l'intensité de
        l'information s'accompagne d'une forte négativité.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — CORRÉLATIONS CAUSALES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔗 Corrélations causales":
    st.title("🔗 Corrélations causales — GDELT × Indicateurs PAG")
    st.markdown(
        "Ces analyses répondent aux questions Q1, Q3, Q5, Q7 : "
        "**quels indicateurs de développement sont liés au ton médiatique ?**"
    )

    # Matrice de corrélation (image générée par le notebook)
    corr_img = OUTPUTS_DIR / "correlation_matrix.png"
    if corr_img.exists():
        st.subheader("Matrice de corrélation GDELT × Indicateurs PAG")
        st.image(str(corr_img), use_column_width=True)

        st.markdown("""
        **Lecture de la matrice :**
        - 🟥 **Rouge (r proche de -1)** : quand cet indicateur monte, le ton baisse
        - 🟩 **Vert (r proche de +1)** : les deux variables évoluent dans le même sens
        - ⬜ **Blanc (r ≈ 0)** : pas de relation linéaire

        **Résultats clés :**
        - `pct_conflit × ton_moyen_pondere` : **r = -0.87** — fort lien négatif
          → Plus les événements conflictuels dominent, plus le ton s'effondre
        - `goldstein_moyen × pct_conflit` : **r = -0.90** — cohérence interne du modèle
          → La GoldsteinScale capture bien la même dimension que la proportion de conflits
        - Les indicateurs BM (PIB, santé, électricité) ont des corrélations faibles avec le ton
          → Limite des données annuelles vs. mensuelles — ouvre la voie au modèle bayésien
        """)
    else:
        st.warning("Image de la matrice non trouvée. Exécuter d'abord le notebook Phase 2.")

    st.divider()

    # Graphique interactif : ton vs. indicateurs BM
    if not df_unified.empty:
        st.subheader("📊 Explorer les relations GDELT × PAG")

        wb_vars = [c for c in df_unified.columns
                   if c not in ['year','month','quarter','year_month']
                   and not c.endswith('_norm')
                   and df_unified[c].nunique() > 2
                   and c not in ['ton_moyen_pondere','goldstein_moyen',
                                  'buzz_mensuel','pct_conflit','pct_cooperation',
                                  'nb_evenements','nb_articles','volatilite_ton',
                                  'goldstein_std','ton_moyen_pondere_norm',
                                  'goldstein_moyen_norm','buzz_mensuel_norm','pct_conflit_norm']]

        col_x, col_y, col_color = st.columns(3)
        with col_x:
            x_var = st.selectbox("Axe X (indicateur PAG)", wb_vars,
                                  index=wb_vars.index('pib_par_habitant_usd') if 'pib_par_habitant_usd' in wb_vars else 0)
        with col_y:
            y_var = st.selectbox("Axe Y (variable GDELT)",
                                  ['ton_moyen_pondere', 'goldstein_moyen', 'buzz_mensuel', 'pct_conflit'],
                                  index=0)
        with col_color:
            color_var = st.selectbox("Couleur", ['month', 'quarter'], index=0)

        if x_var and y_var:
            df_plot = df_unified[[x_var, y_var, color_var, 'year_month']].dropna()
            if len(df_plot) > 1:
                r_val = np.corrcoef(df_plot[x_var], df_plot[y_var])[0, 1]
                fig_scatter = px.scatter(
                    df_plot, x=x_var, y=y_var, color=color_var,
                    hover_data=['year_month'],
                    trendline="ols",
                    template="plotly_white",
                    title=f"{y_var} × {x_var} | r = {r_val:.2f}",
                    labels={x_var: x_var.replace('_', ' ').title(),
                            y_var: y_var.replace('_', ' ').title()}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.caption(f"Corrélation de Pearson : r = {r_val:.3f} | "
                           f"{'Fort' if abs(r_val) > 0.5 else 'Modéré' if abs(r_val) > 0.3 else 'Faible'} lien linéaire")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — MODÈLE BAYÉSIEN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🤖 Modèle bayésien":
    st.title("🤖 Modélisation bayésienne — Résultats et interprétation")
    st.markdown(
        "Le modèle bayésien quantifie **l'incertitude** sur les relations entre "
        "indicateurs PAG et ton médiatique — une approche plus honnête qu'une "
        "régression classique pour des séries courtes (12 mois)."
    )

    # Image des posteriors
    bayes_img = OUTPUTS_DIR / "bayes_Prédicteurs_PAG_→_Ton_médiatique.png"
    # Chercher aussi avec underscore si le nom de fichier diffère
    if not bayes_img.exists():
        candidates = list(OUTPUTS_DIR.glob("bayes_*.png"))
        bayes_img = candidates[0] if candidates else None

    if bayes_img and Path(bayes_img).exists():
        st.subheader("Distributions postérieures des coefficients")
        st.image(str(bayes_img), use_column_width=True)

    st.divider()

    # Interprétation détaillée
    st.subheader("📖 Comment lire ces graphiques")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Distribution postérieure (colonne gauche)**

        Chaque graphique montre la distribution de probabilité du coefficient β
        pour un prédicteur PAG donné.

        - La **ligne rouge pointillée** = β = 0 (pas d'effet)
        - La **zone verte** = HDI 94% (intervalle de crédibilité)
        - Si la zone verte **ne croise pas zéro** → effet probable

        **Résultats obtenus :**
        Tous les HDI 94% croisent zéro → avec 12 mois de données,
        aucun prédicteur PAG n'a un effet statistiquement certain sur le ton.
        """)

    with col2:
        st.markdown("""
        **Trace MCMC (colonne droite)**

        Les traces montrent la convergence de l'algorithme MCMC.

        - **R-hat < 1.05** pour tous les paramètres ✅
        - Traces "en chenille" = bon mélange des chaînes ✅
        - **8 000 échantillons** = estimations fiables

        **Pourquoi c'est une force, pas une limite :**
        Le modèle bayésien dit honnêtement qu'il manque de données.
        Avec 4 ans de données PAG (2021-2025), les HDI se resserreront.
        Une régression classique aurait donné de fausses certitudes.
        """)

    st.divider()

    # Tableau des résultats
    st.subheader("📊 Résumé des coefficients postérieurs")

    results_data = {
        "Prédicteur PAG":    ["PIB/habitant", "Inflation", "Dépenses santé",
                               "Accès électricité", "Mortalité < 5 ans"],
        "β moyen":           ["+0.009", "+0.002", "-0.006", "-0.004", "-0.010"],
        "HDI 94% bas":       ["-1.538", "-1.865", "-1.665", "-1.532", "-1.853"],
        "HDI 94% haut":      ["+1.508", "+1.744", "+1.828", "+1.562", "+1.882"],
        "P(β > 0)":          ["51%", "51%", "50%", "50%", "49%"],
        "Direction":         ["↑ améliore le ton", "↑ améliore le ton",
                               "↓ dégrade le ton*", "↓ dégrade le ton*", "↓ dégrade le ton*"],
        "Certitude":         ["⚠️ Incertain", "⚠️ Incertain", "⚠️ Incertain",
                               "⚠️ Incertain", "⚠️ Incertain"],
    }
    df_results = pd.DataFrame(results_data)
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    st.caption(
        "* Direction négative attendue pour mortalité (indicateur inversé). "
        "HDI = Highest Density Interval — équivalent bayésien de l'intervalle de confiance."
    )

    st.info(
        "**Convergence validée** : R-hat < 1.05 pour tous les paramètres. "
        "4 chaînes MCMC × 2000 draws = 8000 échantillons postérieurs. "
        "Algorithme NUTS (No U-Turn Sampler)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 — SIMULATEUR DE DÉCISIONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 Simulateur de décisions":
    st.title("🎯 Simulateur de scénarios PAG — Aide à la décision")
    st.markdown(
        "Quel investissement améliore le plus la **perception internationale du Bénin** ? "
        "Le modèle bayésien simule les scénarios contrefactuels avec quantification de l'incertitude."
    )

    # Image du simulateur
    scenarios_img = OUTPUTS_DIR / "bayes_scenarios_pag.png"
    if scenarios_img.exists():
        st.image(str(scenarios_img), use_column_width=True)

    st.divider()

    # Tableau interactif des scénarios
    if not df_scenarios.empty:
        st.subheader("📊 Résultats des scénarios — Détail")

        # Formater le tableau
        df_display = df_scenarios.copy()
        if 'prob_ton_acceptable' in df_display.columns:
            df_display['prob_ton_acceptable'] = df_display['prob_ton_acceptable'].apply(
                lambda x: f"{x:.1%}"
            )
        if 'ton_prédit_moyen' in df_display.columns:
            df_display['ton_prédit_moyen'] = df_display['ton_prédit_moyen'].apply(
                lambda x: f"{x:.3f}"
            )
        if 'hdi_bas' in df_display.columns:
            df_display['hdi_bas'] = df_display['hdi_bas'].apply(lambda x: f"{x:.3f}")
        if 'hdi_haut' in df_display.columns:
            df_display['hdi_haut'] = df_display['hdi_haut'].apply(lambda x: f"{x:.3f}")

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Graphique interactif Plotly
        st.subheader("📈 Comparaison interactive des scénarios")
        df_plot = df_scenarios.copy()

        fig_scenarios = go.Figure()

        colors_bar = [
            PALETTE['secondary'] if float(row['ton_prédit_moyen']) > -0.5
            else PALETTE['accent']
            for _, row in df_plot.iterrows()
        ]

        fig_scenarios.add_trace(go.Bar(
            y=df_plot['scénario'],
            x=df_plot['ton_prédit_moyen'],
            orientation='h',
            marker_color=colors_bar,
            error_x=dict(
                type='data',
                symmetric=False,
                array=(df_plot['hdi_haut'] - df_plot['ton_prédit_moyen']).tolist(),
                arrayminus=(df_plot['ton_prédit_moyen'] - df_plot['hdi_bas']).tolist(),
                color='black', thickness=2, width=6
            ),
            text=[f"P(OK)={row['prob_ton_acceptable']:.0%}"
                  for _, row in df_plot.iterrows()],
            textposition='outside',
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Ton prédit : %{x:.3f}<br>"
                "<extra></extra>"
            )
        ))

        fig_scenarios.add_vline(x=-0.5, line_dash="dash", line_color=PALETTE['warning'],
                                 annotation_text="Seuil acceptable (-0.5)",
                                 annotation_position="top")
        fig_scenarios.add_vline(x=0, line_color="black", line_width=0.8)

        fig_scenarios.update_layout(
            title="Simulation bayésienne : quel investissement PAG améliore le plus le ton ?",
            xaxis_title="Ton médiatique prédit (AvgTone pondéré)",
            template="plotly_white",
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig_scenarios, use_container_width=True)
        st.caption(
            "Les barres d'erreur représentent l'HDI 94% (intervalle de crédibilité bayésien). "
            "P(OK) = probabilité que le ton dépasse le seuil acceptable de -0.5."
        )

    st.divider()

    # Widget interactif de simulation
    st.subheader("🔧 Simulateur manuel")
    st.markdown("Ajustez les curseurs pour simuler l'impact d'une politique PAG sur le ton médiatique.")

    col1, col2 = st.columns(2)
    with col1:
        pib_slider    = st.slider("PIB/habitant (niveau relatif 0→1)", 0.0, 1.0, 0.5, 0.05)
        sante_slider  = st.slider("Dépenses santé (niveau relatif 0→1)", 0.0, 1.0, 0.5, 0.05)
        inflat_slider = st.slider("Inflation (niveau relatif 0→1, bas = bon)", 0.0, 1.0, 0.5, 0.05)
    with col2:
        elec_slider   = st.slider("Accès électricité (niveau relatif 0→1)", 0.0, 1.0, 0.5, 0.05)
        mort_slider   = st.slider("Mortalité infantile (niveau relatif 0→1, bas = bon)", 0.0, 1.0, 0.5, 0.05)

    # Prédiction simple (alpha + betas_mean × X)
    ALPHA      = -1.253
    BETAS_MEAN = [0.009, 0.002, -0.006, -0.004, -0.010]
    X_user     = [pib_slider, inflat_slider, sante_slider, elec_slider, mort_slider]
    ton_predit = ALPHA + sum(b * x for b, x in zip(BETAS_MEAN, X_user))

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Ton prédit", f"{ton_predit:.3f}",
                  delta=f"{ton_predit - (-1.253):.3f} vs. status quo")
    with col_res2:
        status = "✅ Acceptable" if ton_predit > -0.5 else "⚠️ Négatif" if ton_predit > -2 else "🚨 Critique"
        st.metric("Statut", status)
    with col_res3:
        # Probabilité approximative (basée sur sigma = 0.592)
        from scipy import stats as scipy_stats
        prob = 1 - scipy_stats.norm.cdf(-0.5, loc=ton_predit, scale=0.592)
        st.metric("P(ton acceptable)", f"{prob:.1%}")

    st.caption(
        "⚠️ Simulation indicative basée sur les coefficients moyens postérieurs. "
        "L'incertitude réelle est représentée par les HDI 94% dans le graphique ci-dessus."
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 6 — CARTE & ÉVÉNEMENTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📍 Carte & Événements":
    st.title("📍 Carte des événements & Sources")

    # Carte avec filtre par type
    type_options = df_ev_filtered['Type_evenement'].dropna().unique().tolist()
    type_sel     = st.multiselect("Type d'événement", type_options, default=type_options)
    df_map_f     = df_ev_filtered[df_ev_filtered['Type_evenement'].isin(type_sel)]

    df_map2 = (
        df_map_f.dropna(subset=['ActionGeo_Lat', 'ActionGeo_Long'])
        .groupby(['ActionGeo_Lat', 'ActionGeo_Long', 'Type_evenement'], dropna=False)
        .agg(Nb=('GLOBALEVENTID','count'), Goldstein=('GoldsteinScale','mean'))
        .reset_index()
    )

    fig_map2 = px.scatter_mapbox(
        df_map2, lat="ActionGeo_Lat", lon="ActionGeo_Long",
        color="Type_evenement", size="Nb", size_max=18,
        hover_data={'Goldstein': ':.2f', 'Nb': True},
        color_discrete_map={
            "Coopération Verbale":    PALETTE['secondary'],
            "Coopération Matérielle": "#5DCAA5",
            "Conflit Verbal":         PALETTE['warning'],
            "Conflit Matériel":       PALETTE['accent'],
        },
        mapbox_style="carto-positron", zoom=6, center={"lat": 9.3, "lon": 2.3}
    )
    fig_map2.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_map2, use_container_width=True)
    st.divider()

    # Tableau des événements
    st.subheader("📰 Tableau des événements")
    cols = [c for c in ["GLOBALEVENTID","Date_Ok","Actor1Name","Actor2Name",
                          "Type_evenement","GoldsteinScale","SOURCEURL"]
            if c in df_ev_filtered.columns]
    st.dataframe(
        df_ev_filtered[cols].sort_values("Date_Ok", ascending=False),
        column_config={
            "GLOBALEVENTID":  st.column_config.TextColumn("ID"),
            "Date_Ok":        st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "GoldsteinScale": st.column_config.NumberColumn("Goldstein", format="%.2f"),
            "SOURCEURL":      st.column_config.LinkColumn("Source", display_text="Ouvrir"),
        },
        use_container_width=True, hide_index=True, height=400
    )
