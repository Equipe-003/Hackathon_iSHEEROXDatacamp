import os, json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from scipy import stats as scipy_stats

st.set_page_config(page_title="🇧🇯 Bénin Insights — Phase 2", layout="wide", initial_sidebar_state="expanded")

PALETTE = {"primary":"#1D6FA4","secondary":"#1D9E75","accent":"#E24B4A",
           "warning":"#EF9F27","neutral":"#6C757D","positive":"#2ECC71",
           "negative":"#E74C3C","purple":"#7F77DD","amber":"#BA7517"}

# ── Chemins ──────────────────────────────────────────────────────────────────
# Sur Google Drive (Colab) : adapter DRIVE_BASE_PATH
# En local : adapter current_dir
current_dir = os.path.dirname(os.path.abspath(__file__))
# Si vous tournez depuis Colab avec Drive monté, remplacer par :
# current_dir = "/content/drive/MyDrive/Challenge_Isheero"
OUTPUTS_DIR = Path(current_dir) / "outputs"

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_cameo_codes():
    cameo_dict = {
        "01":"Déclaration publique","02":"Appel / demande","03":"Expression d'intention",
        "04":"Consultation","05":"Engagement diplomatique","06":"Coopération matérielle",
        "07":"Aide / assistance","08":"Coopération judiciaire","09":"Enquête",
        "10":"Demande / pression","11":"Désapprobation","12":"Rejet / refus",
        "13":"Menace","14":"Protestation","15":"Coercition non-violente",
        "16":"Agression non-armée","17":"Coercition armée","18":"Assaut armé",
        "19":"Conflit armé","20":"Violence de masse",
    }
    return pd.DataFrame(list(cameo_dict.items()), columns=['EVENT_CODE','DESCRIPTION'])

@st.cache_data
def load_phase1_data():
    p_ev  = os.path.join(current_dir, "gdelt_bn_2025.csv")
    p_gkg = os.path.join(current_dir, "gdelt_gkg_bn_V2Tone.csv")
    if not os.path.exists(p_ev):
        return pd.DataFrame(), pd.DataFrame()
    df_ev  = pd.read_csv(p_ev, low_memory=False)
    df_gkg = pd.read_csv(p_gkg, low_memory=False)
    for col in ["GoldsteinScale","AvgTone","ActionGeo_Lat","ActionGeo_Long"]:
        if col in df_ev.columns: df_ev[col] = pd.to_numeric(df_ev[col], errors='coerce')
    df_ev['Date_Ok'] = pd.to_datetime(df_ev['SQLDATE'].astype(str), format='%Y%m%d', errors='coerce')
    df_ev = df_ev.drop_duplicates(subset=['GLOBALEVENTID'])
    quad_mapping = {1:"Coopération Verbale",2:"Coopération Matérielle",3:"Conflit Verbal",4:"Conflit Matériel"}
    df_ev['Type_evenement'] = df_ev['QuadClass'].map(quad_mapping)
    tone_sep = df_gkg['V2Tone'].astype(str).str.split(',', expand=True)
    df_gkg['Tonnalite']  = pd.to_numeric(tone_sep[0], errors='coerce')
    df_gkg['Date']       = pd.to_datetime(df_gkg['Date'].astype(str).str[:8], format='%Y%m%d', errors='coerce')
    internationaux = ['reuters','bbc','lemonde','afp','rfi','apnews','aljazeera','theguardian','france24']
    src = 'SourceCommonName' if 'SourceCommonName' in df_gkg.columns else ('DocumentIdentifier' if 'DocumentIdentifier' in df_gkg.columns else None)
    if src:
        df_gkg['Origine_Media'] = df_gkg[src].apply(lambda x: "Médias Internationaux" if any(s in str(x).lower() for s in internationaux) else "Médias Francophones/Nationaux")
    else:
        df_gkg['Origine_Media'] = "Médias Francophones/Nationaux"
    return df_ev, df_gkg

@st.cache_data
def load_phase2_data():
    d = OUTPUTS_DIR / "dashboard_dataset.csv"
    s = OUTPUTS_DIR / "scenarios_pag.csv"
    k = OUTPUTS_DIR / "kpis_dashboard.json"
    df_u = pd.read_csv(d) if d.exists() else pd.DataFrame()
    df_s = pd.read_csv(s) if s.exists() else pd.DataFrame()
    kpis = json.loads(k.read_text(encoding='utf-8')) if k.exists() else {}
    return df_u, df_s, kpis

df_ev_raw, df_gkg_raw = load_phase1_data()
df_unified, df_scenarios, kpis = load_phase2_data()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🇧🇯 Bénin Insights 2021–2026")
st.sidebar.markdown("*Hackathon iSHEERO × DataCamp 2026*")
st.sidebar.divider()

page = st.sidebar.radio("Navigation", [
    "🏠 Vue d'ensemble & KPIs",
    "📡 Signaux d'alerte précoce",
    "🔗 Corrélations causales",
    "🤖 Modèle bayésien",
    "🎯 Simulateur de décisions",
    "📊 Analyse Phase 1",
    "📍 Carte & Événements",
])

st.sidebar.divider()
if not df_ev_raw.empty:
    min_d, max_d = df_ev_raw['Date_Ok'].min().date(), df_ev_raw['Date_Ok'].max().date()
    date_sel = st.sidebar.date_input("Période (Phase 1)", [min_d, max_d])
    media_opts = df_gkg_raw['Origine_Media'].unique().tolist() if not df_gkg_raw.empty else []
    media_sel  = st.sidebar.multiselect("Origine des médias", media_opts, default=media_opts)
    if len(date_sel) == 2:
        s0, e0 = date_sel
        df_gkg_f = df_gkg_raw[(df_gkg_raw['Date'].dt.date >= s0) & (df_gkg_raw['Date'].dt.date <= e0) & (df_gkg_raw['Origine_Media'].isin(media_sel))].copy() if not df_gkg_raw.empty else pd.DataFrame()
        df_ev_f  = df_ev_raw[(df_ev_raw['Date_Ok'].dt.date >= s0) & (df_ev_raw['Date_Ok'].dt.date <= e0)].copy()
    else:
        df_gkg_f, df_ev_f = df_gkg_raw.copy(), df_ev_raw.copy()
else:
    df_gkg_f, df_ev_f = pd.DataFrame(), pd.DataFrame()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — VUE D'ENSEMBLE
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Vue d'ensemble & KPIs":
    st.title("🇧🇯 Bénin Insights Challenge — Tableau de bord Phase 2")
    st.markdown("**Analyse GDELT × PAG 2021-2026** · Modélisation bayésienne · Aide à la décision publique")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Événements analysés", "159 780", help="GDELT 2021–2026")
    with c2: st.metric("Mois couverts", "65", help="Janvier 2021 → Février 2026")
    with c3: st.metric("Ton médiatique moyen", f"{kpis.get('ton_moyen_global','N/A'):.2f}" if kpis else "~-1.5")
    with c4: st.metric("Mois le + négatif", kpis.get("mois_le_plus_negatif","Fév. 2023"), delta="🚨 Crise", delta_color="inverse")
    with c5: st.metric("Indicateurs PAG croisés", "15", help="Banque Mondiale 2015-2025")

    st.divider()

    # Évolution mensuelle avec annotations
    if not df_unified.empty and 'ton_moyen_pondere' in df_unified.columns:
        st.subheader("📈 Évolution du ton médiatique 2021-2026 — Vue décisionnelle")
        fig = go.Figure()
        fig.add_hrect(y0=-2.43, y1=-100, fillcolor="rgba(226,75,74,0.05)", line_width=0)
        fig.add_hrect(y0=-0.15, y1=1,    fillcolor="rgba(29,158,117,0.06)", line_width=0)
        col_pts = [PALETTE['negative'] if t<-2.43 else PALETTE['secondary'] if t>-0.15 else PALETTE['warning'] for t in df_unified['ton_moyen_pondere']]
        fig.add_trace(go.Scatter(
            x=df_unified['year_month'], y=df_unified['ton_moyen_pondere'],
            mode='lines+markers', name='Ton pondéré',
            line=dict(color=PALETTE['primary'], width=2),
            marker=dict(size=8, color=col_pts, line=dict(width=1.5, color='white')),
            hovertemplate="<b>%{x}</b><br>Ton : %{y:.2f}<extra></extra>"
        ))
        fig.add_hline(y=-2.43, line_dash="dash", line_color=PALETTE['accent'],    annotation_text="Seuil crise (-2.43σ)", annotation_position="bottom right")
        fig.add_hline(y=-0.15, line_dash="dash", line_color=PALETTE['secondary'], annotation_text="Seuil opportunité (-0.15σ)", annotation_position="top right")
        fig.add_hline(y=0, line_color="black", line_width=0.6)
        # Annotations mois extrêmes
        crises = df_unified[df_unified['ton_moyen_pondere'] < -2.43]
        for _, r in crises.iterrows():
            fig.add_annotation(x=r['year_month'], y=r['ton_moyen_pondere'],
                text="🚨", showarrow=False, font=dict(size=14), yshift=-18)
        opps = df_unified[df_unified['ton_moyen_pondere'] > -0.15]
        for _, r in opps.iterrows():
            fig.add_annotation(x=r['year_month'], y=r['ton_moyen_pondere'],
                text="✅", showarrow=False, font=dict(size=14), yshift=12)
        fig.update_layout(template="plotly_white", height=420,
            xaxis_title="Mois", yaxis_title="Ton médiatique pondéré (AvgTone)",
            hovermode="x unified", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🚨 = mois de crise (< -2.43σ) | ✅ = fenêtre d'opportunité (> -0.15σ) | orange = zone normale")

    st.divider()
    st.subheader("💡 5 Insights décisionnels clés")
    insights = [
        ("🔴", "Réputation négative chronique avec fenêtres d'opportunité",
         "Sur 65 mois, le système détecte **6 crises** et **4 fenêtres d'opportunité** automatiquement. "
         "Février est structurellement le mois le plus à risque (3 crises sur 5 ans). "
         "Mars-mai 2023 montrent qu'une période de calme peut suivre immédiatement une crise sévère."),
        ("🟡", "Les dépenses santé et le PIB précèdent le ton médiatique de 10 mois",
         "Les médias capturent les signaux socio-économiques **10 mois avant** les statistiques officielles "
         "(dépenses santé : r=0.486, p=0.0003 | PIB/habitant : r=0.480, p=0.0004). "
         "Le ton GDELT est un indicateur avancé des conditions économiques nationales."),
        ("🟢", "L'électrification est le signal structurel à plus longue portée (12 mois)",
         "Accès électricité × ton médiatique : r=0.410, p=0.0038 à lag -12 mois. "
         "C'est l'investissement PAG à faire en **début de mandat** pour des retombées narratives en milieu de mandat."),
        ("🤖", "Le modèle bayésien identifie l'électricité comme prédicteur le plus certain (P=90%)",
         "P(accès électricité → améliore ton) = **90%**. P(dépenses santé → améliore ton) = **79%**. "
         "Ces probabilités directement interprétables sont l'avantage clé du bayésien vs. une régression classique."),
        ("🎯", "Recommandation PAG : hausse du budget santé +30%",
         "Le simulateur de scénarios montre que la hausse du budget santé est le seul scénario qui améliore "
         "significativement le ton prédit (+0.21 vs. status quo) et multiplie la P(ton acceptable) par 11 (11% vs. 1%)."),
    ]
    for emoji, titre, texte in insights:
        with st.expander(f"{emoji} {titre}"):
            st.markdown(texte)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — SIGNAUX D'ALERTE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📡 Signaux d'alerte précoce":
    st.title("📡 Signaux d'alerte précoce — Analyse des pics et crises")
    st.markdown("Le système détecte automatiquement les mois anormaux sur 5 ans de données GDELT.")

    if not df_unified.empty:
        # Statistiques des pics
        mn  = df_unified['ton_moyen_pondere'].mean()
        std = df_unified['ton_moyen_pondere'].std()
        low, high = mn - 1.5*std, mn + 1.5*std

        crises = df_unified[df_unified['ton_moyen_pondere'] < low].copy()
        opps   = df_unified[df_unified['ton_moyen_pondere'] > high].copy()

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Seuil d'alerte (crise)", f"{low:.2f}", help="Moyenne - 1.5σ")
        with c2: st.metric("Seuil opportunité", f"{high:.2f}", help="Moyenne + 1.5σ")
        with c3: st.metric("Mois de crise détectés", len(crises))
        with c4: st.metric("Fenêtres d'opportunité", len(opps))

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚨 Mois de crise (ton < -2.43)")
            if not crises.empty:
                df_crises_disp = crises[['year_month','ton_moyen_pondere','goldstein_moyen','buzz_mensuel']].copy()
                df_crises_disp.columns = ['Mois','Ton pondéré','GoldsteinScale','Buzz (mentions)']
                df_crises_disp = df_crises_disp.sort_values('Ton pondéré')
                st.dataframe(df_crises_disp.style.background_gradient(subset=['Ton pondéré'], cmap='RdYlGn'),
                             use_container_width=True, hide_index=True)

        with col2:
            st.subheader("✅ Fenêtres d'opportunité (ton > -0.15)")
            if not opps.empty:
                df_opps_disp = opps[['year_month','ton_moyen_pondere','goldstein_moyen','buzz_mensuel']].copy()
                df_opps_disp.columns = ['Mois','Ton pondéré','GoldsteinScale','Buzz (mentions)']
                df_opps_disp = df_opps_disp.sort_values('Ton pondéré', ascending=False)
                st.dataframe(df_opps_disp.style.background_gradient(subset=['Ton pondéré'], cmap='RdYlGn'),
                             use_container_width=True, hide_index=True)

        st.divider()

        # Distribution mensuelle
        st.subheader("📊 Distribution du ton par mois de l'année (2021-2026)")
        df_month = df_unified.copy()
        df_month['mois_nom'] = pd.to_datetime(df_month['year_month']+'-01').dt.month
        mois_noms = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}
        df_month['mois_label'] = df_month['mois_nom'].map(mois_noms)
        fig_box = px.box(df_month, x='mois_label', y='ton_moyen_pondere',
                          color_discrete_sequence=[PALETTE['primary']],
                          template="plotly_white",
                          labels={'mois_label':'Mois','ton_moyen_pondere':'Ton médiatique'},
                          title="Variabilité du ton par mois — Février = mois le plus à risque")
        fig_box.add_hline(y=low,  line_dash="dash", line_color=PALETTE['accent'],    annotation_text="Seuil crise")
        fig_box.add_hline(y=high, line_dash="dash", line_color=PALETTE['secondary'], annotation_text="Seuil opportunité")
        fig_box.update_xaxes(categoryorder='array', categoryarray=list(mois_noms.values()))
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("Lecture : la boîte représente les quartiles, les points extrêmes sont les outliers. Février est structurellement le mois le plus négatif sur 5 ans.")

        st.divider()

        # Proxy d'alerte
        st.subheader("🔔 Système d'alerte précoce — Proxy opérationnel")
        st.info("""
**En l'absence de données ACLED**, voici le double critère d'alerte empirique validé sur 2021-2026 :

- **Condition 1 :** `ton_moyen_pondere < -2.0` sur le mois courant
- **Condition 2 :** `goldstein_moyen < 0` sur le mois courant

Ce double critère détecte les **6 mois de crise** avec **0 faux positif** sur 65 mois analysés.
        """)

        latest = df_unified.iloc[-1]
        alert_1 = latest['ton_moyen_pondere'] < -2.0
        alert_2 = latest['goldstein_moyen'] < 0
        alert_active = alert_1 and alert_2

        status_color = "🔴 ALERTE ACTIVE" if alert_active else ("🟡 VIGILANCE" if (alert_1 or alert_2) else "🟢 NORMAL")
        st.metric(f"Statut dernier mois disponible ({latest['year_month']})", status_color,
                  delta=f"Ton={latest['ton_moyen_pondere']:.2f} | Goldstein={latest['goldstein_moyen']:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — CORRÉLATIONS CAUSALES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔗 Corrélations causales":
    st.title("🔗 Corrélations causales — GDELT × Indicateurs PAG")
    st.markdown("Analyses cross-lag et matrice de corrélation. **Données 2021-2026 : 65 points mensuels.**")

    # Résultats lag summary
    st.subheader("⏱️ Résultats de l'analyse cross-lag (lags -12 → +12 mois)")
    lag_data = {
        "Indicateur BM":       ["Dépenses santé (% PIB)","PIB/habitant (USD)","Accès électricité (%)"],
        "Lag optimal (mois)":  [-10, -10, -12],
        "r (Pearson)":         [0.486, 0.480, 0.410],
        "p-value":             ["0.0003 ***","0.0004 ***","0.0038 **"],
        "Interprétation":      [
            "Ton précède dépenses santé de 10 mois",
            "Ton précède PIB de 10 mois",
            "Ton précède électricité de 12 mois"
        ]
    }
    st.dataframe(pd.DataFrame(lag_data), use_container_width=True, hide_index=True)
    st.info("**Lecture du lag négatif :** Le signe négatif signifie que le **ton médiatique précède l'indicateur BM**. Les médias GDELT capturent les signaux de crise ~10 mois avant que les statistiques officielles les enregistrent. C'est le phénomène de « media as leading indicator ».")

    st.divider()

    # Images des graphiques lag générés par le notebook
    lag_imgs = {
        "Q1 — PIB/habitant × Ton médiatique":        OUTPUTS_DIR / "lag_ton_moyen__pib_par_habitan.png",
        "Q5 — Dépenses santé × Ton médiatique":       OUTPUTS_DIR / "lag_ton_moyen__depenses_sante_.png",
        "Q7 — Accès électricité × Ton médiatique":    OUTPUTS_DIR / "lag_ton_moyen__acces_electrici.png",
    }
    tab_names = list(lag_imgs.keys())
    tabs = st.tabs(tab_names)
    for tab, (title, img_path) in zip(tabs, lag_imgs.items()):
        with tab:
            if img_path.exists():
                st.image(str(img_path), use_column_width=True)
            else:
                st.warning(f"Image non trouvée : {img_path.name}. Vérifier le dossier outputs/.")

    st.divider()

    # Matrice de corrélation
    st.subheader("🗺️ Matrice de corrélation multi-variables")
    corr_img = OUTPUTS_DIR / "correlation_matrix.png"
    if corr_img.exists():
        st.image(str(corr_img), use_column_width=True)
        st.markdown("""
**Corrélations clés identifiées :**
- `pct_conflit` × `ton_moyen_pondere` : **r = -0.83** → Les conflits médiatisés dégradent fortement le ton
- `goldstein_moyen` × `pct_conflit` : **r = -0.91** → Cohérence interne du modèle
- `goldstein_moyen` × `esperance_vie_ans` : **r = +0.47** → Coopération associée à une meilleure santé
- `ton_moyen_pondere` × `depenses_sante_pct_pib` : **r = +0.31** → Lien modéré mais cohérent
        """)
    else:
        st.warning("Matrice non trouvée. Exécuter d'abord le notebook Phase 2.")

    st.divider()

    # Explorateur interactif
    if not df_unified.empty:
        st.subheader("🔍 Explorateur interactif de corrélations")
        wb_vars = [c for c in df_unified.columns
                   if not c.endswith('_norm') and c not in
                   ['year','month','quarter','year_month','ton_moyen_pondere','goldstein_moyen',
                    'buzz_mensuel','pct_conflit','pct_cooperation','nb_evenements','nb_articles',
                    'volatilite_ton','goldstein_std','ton_moyen_pondere_norm','goldstein_moyen_norm',
                    'buzz_mensuel_norm','pct_conflit_norm']
                   and df_unified[c].nunique() > 3]

        c1, c2 = st.columns(2)
        with c1:
            x_var = st.selectbox("Indicateur PAG (axe X)", wb_vars,
                                  index=wb_vars.index('pib_par_habitant_usd') if 'pib_par_habitant_usd' in wb_vars else 0)
        with c2:
            y_var = st.selectbox("Variable GDELT (axe Y)",
                                  ['ton_moyen_pondere','goldstein_moyen','buzz_mensuel','pct_conflit'], index=0)

        if x_var and y_var:
            df_plot = df_unified[[x_var, y_var, 'year_month', 'year']].dropna()
            if len(df_plot) > 3:
                r_val = np.corrcoef(df_plot[x_var], df_plot[y_var])[0,1]
                fig_sc = px.scatter(df_plot, x=x_var, y=y_var, color='year',
                                     hover_data=['year_month'], trendline="ols",
                                     template="plotly_white",
                                     title=f"{y_var} × {x_var} | r = {r_val:.3f}",
                                     labels={x_var: x_var.replace('_',' ').title(),
                                             y_var: y_var.replace('_',' ').title()})
                st.plotly_chart(fig_sc, use_container_width=True)
                force = "Fort" if abs(r_val)>0.5 else "Modéré" if abs(r_val)>0.3 else "Faible"
                st.caption(f"r = {r_val:.3f} ({force} lien) | {len(df_plot)} points")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — MODÈLE BAYÉSIEN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🤖 Modèle bayésien":
    st.title("🤖 Modèle bayésien — Résultats et interprétation")
    st.markdown("Régression linéaire bayésienne (PyMC, NUTS) · 60 observations · 4 chaînes · 8 000 échantillons")

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("R-hat alpha",  "1.0007", help="< 1.05 = convergence validée ✅")
    with c2: st.metric("R-hat betas",  "1.0014", help="< 1.05 = convergence validée ✅")
    with c3: st.metric("Observations", "60",     help="Mois avec données BM complètes")

    st.divider()

    # Tableau des coefficients
    st.subheader("📊 Coefficients postérieurs — Résumé décisionnel")
    coef_data = {
        "Prédicteur PAG":   ["Dépenses santé (% PIB)","Accès électricité (%)","Inflation (%)","PIB/habitant (USD)","Mortalité < 5 ans"],
        "β moyen":          ["+0.613", "+0.599", "+0.523", "-0.686", "-0.582"],
        "HDI 94% bas":      ["-0.83", "-0.27", "-0.45", "-1.86", "-2.17"],
        "HDI 94% haut":     ["+2.03", "+1.46", "+1.50", "+0.43", "+0.92"],
        "P(β > 0)":         ["79% ↑", "90% ↑", "84% ↑", "13% ↓", "24% ↓"],
        "Décision":         ["🟢 Investir", "🟢 Investir (le + certain)", "⚠️ Complexe*", "🔴 Contre-intuitif**", "📉 Attendu (inversé)"],
    }
    st.dataframe(pd.DataFrame(coef_data), use_container_width=True, hide_index=True)
    st.caption("*L'inflation positive reflète probablement la période COVID (inflation mondiale + narratif paradoxalement neutre). **Le PIB négatif est un artefact de la période 2021-2023 (croissance + crises narratives concomitantes).")

    st.divider()

    # Image des posteriors
    bayes_imgs = list(OUTPUTS_DIR.glob("bayes_Prédicteurs*.png")) + list(OUTPUTS_DIR.glob("bayes_Pred*.png"))
    if bayes_imgs:
        st.subheader("📈 Distributions postérieures des coefficients")
        st.image(str(bayes_imgs[0]), use_column_width=True)
    else:
        st.warning("Image bayésienne non trouvée dans outputs/. Vérifier le chemin.")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔵 Comment lire les graphiques (colonne gauche)")
        st.markdown("""
- **Ligne rouge pointillée** = β = 0 (pas d'effet)
- **Zone verte** = HDI 94% (intervalle de crédibilité à 94%)
- Si la zone verte **ne croise pas zéro** → effet probable
- Plus la distribution est **concentrée à droite de zéro** → plus l'effet positif est certain
        """)
    with c2:
        st.subheader("📉 Traces MCMC (colonne droite)")
        st.markdown("""
- Traces en "chenille" = **bon mélange** des 4 chaînes ✅
- Pas de tendance visible = **stationnarité** validée ✅
- R-hat < 1.05 pour tous les paramètres ✅
- **Pourquoi 4 chaînes ?** Pour détecter si l'algorithme converge vers le même point de départ différents
        """)

    st.info("**Pourquoi bayésien et pas OLS ?** Une régression classique nous aurait donné des p-values. Notre modèle donne P(β > 0) = 90% pour l'électricité — une **probabilité directement interprétable** pour un décideur qui alloue un budget. On sait qu'on ne sait pas, et on le quantifie.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 — SIMULATEUR
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 Simulateur de décisions":
    st.title("🎯 Simulateur de scénarios PAG — Aide à la décision budgétaire")
    st.markdown("Basé sur le modèle bayésien entraîné sur 60 mois (2021-2025). Chaque scénario simule un choix d'investissement PAG.")

    # Image
    sc_img = OUTPUTS_DIR / "bayes_scenarios_pag.png"
    if sc_img.exists():
        st.image(str(sc_img), use_column_width=True)

    st.divider()

    # Tableau interactif
    if not df_scenarios.empty:
        st.subheader("📊 Résultats détaillés des scénarios")
        df_disp = df_scenarios.copy()
        for col in ['ton_prédit_moyen','hdi_bas','hdi_haut']:
            if col in df_disp.columns:
                df_disp[col] = df_disp[col].apply(lambda x: f"{x:.3f}")
        if 'prob_ton_acceptable' in df_disp.columns:
            df_disp['prob_ton_acceptable'] = df_disp['prob_ton_acceptable'].apply(lambda x: f"{float(x):.1%}")
        st.dataframe(df_disp, use_container_width=True, hide_index=True)

        # Graphique Plotly interactif
        df_p = df_scenarios.copy()
        colors = [PALETTE['secondary'] if float(r['ton_prédit_moyen'])>-1.4 else PALETTE['accent'] for _,r in df_p.iterrows()]
        fig_sc = go.Figure(go.Bar(
            y=df_p['scénario'], x=df_p['ton_prédit_moyen'], orientation='h',
            marker_color=colors,
            error_x=dict(type='data', symmetric=False,
                          array=(df_p['hdi_haut']-df_p['ton_prédit_moyen']).tolist(),
                          arrayminus=(df_p['ton_prédit_moyen']-df_p['hdi_bas']).tolist(),
                          color='black', thickness=2, width=6),
            text=[f"P(OK)={float(r['prob_ton_acceptable']):.0%}" for _,r in df_p.iterrows()],
            textposition='outside',
        ))
        fig_sc.add_vline(x=-0.5, line_dash="dash", line_color=PALETTE['warning'], annotation_text="Seuil ton acceptable")
        fig_sc.add_vline(x=0,    line_color="black", line_width=0.8)
        fig_sc.update_layout(template="plotly_white", height=380, showlegend=False,
                              xaxis_title="Ton médiatique prédit (AvgTone pondéré)",
                              title="Comparaison des scénarios PAG — Quel investissement est optimal ?")
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption("Barres d'erreur = HDI 94% (intervalle de crédibilité bayésien). P(OK) = probabilité que le ton dépasse le seuil acceptable de -0.5.")

    st.divider()

    # Simulateur manuel
    st.subheader("🔧 Simulateur interactif — Testez votre propre scénario")
    st.markdown("Ajustez les curseurs pour simuler l'impact d'un choix d'investissement sur le ton médiatique international.")

    c1, c2 = st.columns(2)
    with c1:
        pib_s    = st.slider("PIB/habitant (niveau relatif)", 0.0, 1.0, 0.5, 0.05, help="0 = minimum historique, 1 = maximum historique")
        sante_s  = st.slider("Dépenses santé % PIB",          0.0, 1.0, 0.5, 0.05)
        inflat_s = st.slider("Inflation % (bas = bon)",        0.0, 1.0, 0.5, 0.05)
    with c2:
        elec_s   = st.slider("Accès électricité %",            0.0, 1.0, 0.5, 0.05)
        mort_s   = st.slider("Mortalité infantile (bas = bon)", 0.0, 1.0, 0.5, 0.05)

    # Prédiction (coefficients postérieurs moyens du modèle)
    ALPHA_EST  = -1.743
    BETAS_EST  = [-0.686, +0.523, +0.613, +0.599, -0.582]
    X_user     = [pib_s, inflat_s, sante_s, elec_s, mort_s]
    ton_predit = ALPHA_EST + sum(b*x for b,x in zip(BETAS_EST, X_user))
    prob_ok    = 1 - scipy_stats.norm.cdf(-0.5, loc=ton_predit, scale=0.701)
    delta_sq   = ton_predit - (-1.509)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Ton prédit", f"{ton_predit:.3f}")
    with c2: st.metric("vs. status quo", f"{delta_sq:+.3f}", delta_color="normal" if delta_sq>0 else "inverse")
    with c3:
        status = "✅ Acceptable" if ton_predit > -0.5 else ("⚠️ Négatif" if ton_predit > -2 else "🚨 Critique")
        st.metric("Statut", status)
    with c4: st.metric("P(ton acceptable)", f"{prob_ok:.1%}")

    st.caption("⚠️ Simulation basée sur les coefficients moyens postérieurs. L'incertitude réelle est représentée par les HDI 94% dans le tableau ci-dessus.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 6 — PHASE 1
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Analyse Phase 1":
    st.title("📊 Analyse Phase 1 — Couverture médiatique GDELT 2025")
    if df_ev_raw.empty:
        st.warning("Données Phase 1 non trouvées. Vérifier gdelt_bn_2025.csv et gdelt_gkg_bn_V2Tone.csv.")
    else:
        st.info("Données 2025. Utilisez les filtres de la barre latérale.")

        st.subheader("📉 Tonalité médiatique par date")
        if not df_gkg_f.empty:
            df_avg = df_gkg_f.groupby(['Date','Origine_Media'])['Tonnalite'].mean().reset_index()
            fig_tone = px.line(df_avg, x='Date', y='Tonnalite', color='Origine_Media',
                                template="plotly_white",
                                color_discrete_map={"Médias Internationaux":PALETTE['primary'],"Médias Francophones/Nationaux":PALETTE['secondary']},
                                labels={'Tonnalite':'Tonalité moyenne'})
            fig_tone.add_hline(y=0, line_color="black", line_width=0.8)
            fig_tone.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_tone, use_container_width=True)

        st.divider()
        st.subheader("📊 Volume d'articles par date")
        if not df_gkg_f.empty:
            df_cnt = df_gkg_f.groupby(['Date','Origine_Media'])['Tonnalite'].count().reset_index().rename(columns={'Tonnalite':'Nb_Articles'})
            fig_vol = px.area(df_cnt, x='Date', y='Nb_Articles', color='Origine_Media', template="plotly_white",
                               color_discrete_map={"Médias Internationaux":PALETTE['primary'],"Médias Francophones/Nationaux":PALETTE['secondary']})
            fig_vol.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_vol, use_container_width=True)

        with st.expander("📝 Analyse Phase 1 — Résumé"):
            st.write("""
            L'analyse 2025 met en lumière une fracture en décembre : explosion du volume de publications
            et chute brutale de la tonalité (-2.49). Cette divergence confirme une crise médiatique majeure.
            Les médias internationaux s'alignent sur la presse francophone en fin d'année, illustrant
            une dégradation généralisée de la perception des événements béninois à l'échelle mondiale.
            """)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 7 — CARTE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📍 Carte & Événements":
    st.title("📍 Carte des événements géolocalisés")
    if df_ev_raw.empty:
        st.warning("Données Phase 1 non trouvées.")
    else:
        type_opts = df_ev_f['Type_evenement'].dropna().unique().tolist()
        type_sel  = st.multiselect("Type d'événement", type_opts, default=type_opts)
        df_map    = df_ev_f[df_ev_f['Type_evenement'].isin(type_sel)].dropna(subset=['ActionGeo_Lat','ActionGeo_Long'])
        df_map_g  = df_map.groupby(['ActionGeo_Lat','ActionGeo_Long','Type_evenement'], dropna=False).agg(
            Nb=('GLOBALEVENTID','count'), Goldstein=('GoldsteinScale','mean')).reset_index()

        fig_map = px.scatter_mapbox(df_map_g, lat="ActionGeo_Lat", lon="ActionGeo_Long",
                                     color="Type_evenement", size="Nb", size_max=18,
                                     hover_data={'Goldstein':':.2f','Nb':True},
                                     color_discrete_map={"Coopération Verbale":PALETTE['secondary'],
                                                         "Coopération Matérielle":"#5DCAA5",
                                                         "Conflit Verbal":PALETTE['warning'],
                                                         "Conflit Matériel":PALETTE['accent']},
                                     mapbox_style="carto-positron", zoom=6, center={"lat":9.3,"lon":2.3})
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=520)
        st.plotly_chart(fig_map, use_container_width=True)

        st.divider()
        st.subheader("📰 Tableau des événements")
        cols = [c for c in ["GLOBALEVENTID","Date_Ok","Actor1Name","Actor2Name","Type_evenement","GoldsteinScale","SOURCEURL"] if c in df_ev_f.columns]
        st.dataframe(df_ev_f[cols].sort_values("Date_Ok", ascending=False),
                     column_config={"Date_Ok": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                                    "GoldsteinScale": st.column_config.NumberColumn("Goldstein", format="%.2f"),
                                    "SOURCEURL": st.column_config.LinkColumn("Source", display_text="Ouvrir")},
                     use_container_width=True, hide_index=True, height=400)
