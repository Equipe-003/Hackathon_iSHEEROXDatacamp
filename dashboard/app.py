import streamlit as st
import pandas as pd
import plotly.express as px

# ── Configuration (appelé UNE SEULE FOIS, en tout premier) ───────────────────
st.set_page_config(page_title="Analyse GDELT Bénin", layout="wide")


# ── 1. MAPPING CAMEO STATIQUE ────────────────────────────────────────────────
@st.cache_data
def load_cameo_codes():
    cameo_dict = {
        "01": "Déclaration publique", "010": "Déclaration publique (générique)",
        "011": "Discours, déclaration orale", "012": "Conférence de presse",
        "013": "Accusation formelle", "014": "Protestation formelle",
        "015": "Défier / questionner / contester", "016": "Nier / refuser",
        "017": "Rejeter (proposition / plan)", "018": "Menacer",
        "019": "Expliquer / justifier",
        "02": "Appel / demande", "020": "Appel (générique)",
        "021": "Appel à la coopération", "022": "Appel à l'aide matérielle",
        "023": "Appel à un accord diplomatique", "024": "Appel à la résolution de conflit",
        "025": "Appel à la médiation", "026": "Appel à réunion / sommet",
        "027": "Appel à arrêter les hostilités", "028": "Appel à soutien politique",
        "03": "Expression d'intention", "030": "Expression d'intention (générique)",
        "031": "Exprimer l'intention de coopérer", "032": "Exprimer l'intention d'aide matérielle",
        "033": "Exprimer l'intention d'accord diplomatique",
        "04": "Consultation", "040": "Consultation (générique)",
        "041": "Discussions informelles", "042": "Rencontre en face-à-face",
        "043": "Médiation", "044": "Négociation",
        "045": "Appel téléphonique / correspondance", "046": "Visite d'état / officielle",
        "05": "Engagement diplomatique", "050": "Engagement diplomatique (générique)",
        "051": "Soutien diplomatique", "052": "Échange de biens / ressources",
        "053": "Accord / traité", "054": "Normalisation des relations",
        "055": "Reconnaissance diplomatique", "056": "Réconciliation / apaisement",
        "057": "Retrait des sanctions",
        "06": "Coopération matérielle", "060": "Coopération matérielle (générique)",
        "061": "Coopération économique", "062": "Aide matérielle / assistance",
        "063": "Aide humanitaire", "064": "Aide militaire",
        "065": "Coopération judiciaire / policière",
        "07": "Aide / assistance", "070": "Aide (générique)",
        "071": "Aide économique", "072": "Aide militaire",
        "073": "Aide humanitaire", "074": "Aide médicale", "075": "Aide alimentaire",
        "08": "Coopération judiciaire", "080": "Coopération judiciaire (générique)",
        "081": "Coopération dans les enquêtes", "082": "Extradition",
        "09": "Enquête / investigation", "090": "Enquête (générique)",
        "091": "Enquête judiciaire", "092": "Enquête parlementaire",
        "10": "Demande / pression", "100": "Demande (générique)",
        "101": "Demande de sanctions", "102": "Demande de mesures administratives",
        "103": "Demande de réformes politiques",
        "11": "Désapprobation / critique", "110": "Désapprobation (générique)",
        "111": "Blâme / accusation", "112": "Dénonciation / humiliation",
        "113": "Critique / attaque verbale", "114": "Défi verbal",
        "12": "Rejet / refus", "120": "Rejet (générique)",
        "121": "Rejet d'accord", "122": "Rejet de demande",
        "123": "Rejet d'accusation", "124": "Rejet de proposition",
        "13": "Menace", "130": "Menace (générique)",
        "131": "Menace de sanctions", "132": "Menace de représailles politiques",
        "133": "Menace de représailles militaires", "137": "Menace de violence",
        "138": "Ultimatum",
        "14": "Protestation / manifestation", "140": "Protestation (générique)",
        "141": "Manifestation pacifique", "142": "Grève / boycott / obstruction",
        "143": "Manifestation avec affrontements", "144": "Émeute",
        "145": "Manifestation violente",
        "15": "Pression / coercition non-violente", "150": "Coercition non-violente (générique)",
        "151": "Sanctions économiques", "152": "Embargo",
        "153": "Sanctions politiques", "154": "Expulsion / renvoi",
        "16": "Attentat / agression (non-armé)", "160": "Agression non-armée (générique)",
        "163": "Arrestation / détention", "164": "Expulsion d'acteurs",
        "165": "Confiscation / saisie", "167": "Assassinat politique",
        "17": "Coercition avec menace de force", "170": "Coercition armée (générique)",
        "171": "Déploiement de forces", "172": "Démonstration de force militaire",
        "173": "Mobilisation militaire", "174": "Blocus militaire",
        "18": "Assaut armé", "180": "Assaut armé (générique)",
        "181": "Attaque / bombardement", "182": "Combat armé",
        "183": "Attentat / bombe", "185": "Embuscade", "186": "Assassinat / meurtre",
        "19": "Conflit armé à grande échelle", "190": "Conflit armé (générique)",
        "191": "Guerre déclarée", "192": "Guerre civile",
        "20": "Violence de masse", "200": "Violence de masse (générique)",
        "201": "Génocide", "202": "Crimes contre l'humanité",
    }
    return pd.DataFrame(list(cameo_dict.items()), columns=['EVENT_CODE', 'DESCRIPTION'])


# ── 2. CHARGEMENT ET NETTOYAGE UNIFIÉ ────────────────────────────────────────
@st.cache_data
def load_data():
    """
    Fonction unique de chargement. Retourne (df_ev, df_gkg) propres et prêts
    à l'emploi, avec toutes les colonnes nécessaires au dashboard.
    """
    df_cameo = load_cameo_codes()

    # ── Chargement brut ───────────────────────────────────────────────────────
    df_ev  = pd.read_csv("gdelt_bn_2025.csv", low_memory=False)
    df_gkg = pd.read_csv("gdelt_gkg_bn_V2Tone.csv", low_memory=False)

    # ── Nettoyage Events ──────────────────────────────────────────────────────
    # Colonnes numériques
    for col in ["GoldsteinScale", "AvgTone", "ActionGeo_Lat", "ActionGeo_Long",
                "Actor1Geo_Lat", "Actor1Geo_Long", "Actor2Geo_Lat", "Actor2Geo_Long"]:
        if col in df_ev.columns:
            df_ev[col] = pd.to_numeric(df_ev[col], errors='coerce')

    # Dates
    df_ev['Date_Ok'] = pd.to_datetime(
        df_ev['SQLDATE'].astype(str), format='%Y%m%d', errors='coerce'
    )
    df_ev['Month Name'] = df_ev['Date_Ok'].dt.month_name()

    # Exclusion Bénin City (Nigeria)
    exclusions = ["edo", "benin city", "ekpoma", "edo state, edo, nigeria"]
    for col in ['Actor1Geo_FullName', 'Actor2Geo_FullName']:
        if col in df_ev.columns:
            df_ev = df_ev[
                ~df_ev[col].str.lower().str.strip().isin(exclusions).fillna(False)
            ]

    # Dédoublonnage
    df_ev = df_ev.drop_duplicates(subset=['GLOBALEVENTID'])

    # QuadClass → libellé
    quad_mapping = {
        1: "Coopération Verbale", 2: "Coopération Matérielle",
        3: "Conflit Verbal",      4: "Conflit Matériel"
    }
    df_ev['Type_evenement'] = df_ev['QuadClass'].map(quad_mapping)

    # EventCode propre pour la jointure CAMEO
    df_ev['EventCode'] = (
        df_ev['EventCode'].astype(str).str.replace('.0', '', regex=False)
    )

    # Jointure CAMEO → colonne DESCRIPTION
    df_ev = pd.merge(df_ev, df_cameo, left_on='EventCode', right_on='EVENT_CODE', how='left')

    # Fallback DESCRIPTION si la jointure ne couvre pas tous les codes
    df_ev['DESCRIPTION'] = df_ev['DESCRIPTION'].fillna(
        df_ev['QuadClass'].map({
            1: "Coopération Verbale", 2: "Coopération Matérielle",
            3: "Conflit Verbal",      4: "Conflit Matériel"
        })
    )

    # ── Nettoyage GKG ─────────────────────────────────────────────────────────
    # Parsing V2Tone → colonnes séparées
    tone_sep = df_gkg['V2Tone'].astype(str).str.split(',', expand=True)
    df_gkg['Tonnalite']     = pd.to_numeric(tone_sep[0], errors='coerce')
    df_gkg['Mots_Positifs'] = pd.to_numeric(tone_sep[1], errors='coerce')
    df_gkg['Mots_Negatifs'] = pd.to_numeric(tone_sep[2], errors='coerce')
    df_gkg['Polarite']      = pd.to_numeric(tone_sep[3], errors='coerce')

    # Date GKG
    df_gkg['Date'] = pd.to_datetime(
        df_gkg['Date'].astype(str).str[:8], format='%Y%m%d', errors='coerce'
    )

    # Origine des médias
    internationaux = ['reuters', 'bbc', 'lemonde', 'afp', 'rfi', 'apnews',
                      'aljazeera', 'theguardian', 'france24']
    source_col = 'SourceCommonName' if 'SourceCommonName' in df_gkg.columns else \
                 ('DocumentIdentifier' if 'DocumentIdentifier' in df_gkg.columns else None)

    if source_col:
        df_gkg['Origine_Media'] = df_gkg[source_col].apply(
            lambda x: "Médias Internationaux"
            if any(s in str(x).lower() for s in internationaux)
            else "Médias Francophones/Nationaux"
        )
    else:
        # Fallback si aucune colonne source n'est trouvée
        df_gkg['Origine_Media'] = "Médias Francophones/Nationaux"

    return df_ev, df_gkg


# ── Chargement ────────────────────────────────────────────────────────────────
df_ev_raw, df_gkg_raw = load_data()


# ── 3. SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.title("📊 Paramètres")

with st.sidebar:
    min_d = df_ev_raw['Date_Ok'].min().date()
    max_d = df_ev_raw['Date_Ok'].max().date()
    date_selection = st.date_input("Sélectionner la période", [min_d, max_d])

    media_options   = df_gkg_raw['Origine_Media'].unique().tolist()
    media_selection = st.multiselect(
        "Origine des médias", options=media_options, default=media_options
    )


# ── 4. FILTRAGE ───────────────────────────────────────────────────────────────
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
    # Sécurité : si la sélection de date est incomplète, on utilise tout le dataset
    df_gkg_filtered = df_gkg_raw.copy()
    df_ev_filtered  = df_ev_raw.copy()


# ── 5. TITRE ET DESCRIPTION ───────────────────────────────────────────────────
st.title("Analyse de la couverture médiatique au Bénin")
st.info(
    "Ce dashboard analyse la couverture médiatique du Bénin sur l'année 2025. "
    "Il permet de croiser le volume d'articles avec la tonalité moyenne des récits, "
    "tout en distinguant les médias francophones/nationaux des médias internationaux."
)


# ── 6. BLOC 1 : CARTE ───────────────────────────────────────────────────────
st.subheader("📍 Localisation des événements")

df_map = (
    df_ev_filtered
    .dropna(subset=['ActionGeo_Lat', 'ActionGeo_Long'])
    .groupby(['ActionGeo_Lat', 'ActionGeo_Long', 'DESCRIPTION'], dropna=False)
    .agg(
        Nombre_Evenements=('GLOBALEVENTID', 'count'),
        Premiere_Date=('Date_Ok', 'min')
    )
    .reset_index()
)
df_map['Premiere_Date'] = df_map['Premiere_Date'].dt.strftime('%Y-%m-%d')

fig_map = px.scatter_mapbox(
    df_map,
    lat="ActionGeo_Lat", lon="ActionGeo_Long",
    color="DESCRIPTION", size="Nombre_Evenements", size_max=15,
    hover_data={'Premiere_Date': True, 'Nombre_Evenements': True},
    mapbox_style="carto-positron", zoom=6
)
fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend_title_text='Événement'
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ── 7. BLOC 2 : TABLEAU ─────────────────────────────────────────────────────
st.subheader("📰 Prédominance des médias")

cols_tableau = [c for c in ["GLOBALEVENTID", "Date_Ok", "Actor1Name", "Actor2Name", "SOURCEURL"]
                if c in df_ev_filtered.columns]
st.dataframe(
    df_ev_filtered[cols_tableau],
    column_config={
        "GLOBALEVENTID": st.column_config.TextColumn("ID"),
        "Date_Ok":       st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "SOURCEURL":     st.column_config.LinkColumn("Lien Source", display_text="Ouvrir l'article"),
    },
    use_container_width=True, hide_index=True, height=450
)

st.divider()

# ── 8. BLOC 3 : tonnalité moyenne ───────────────────────────────────────────
st.subheader("📉 Tonalité médiatique moyenne par date")

df_avg = (
    df_gkg_filtered
    .groupby(['Date', 'Origine_Media'])['Tonnalite']
    .mean()
    .reset_index()
)
fig_avg = px.line(
    df_avg, x='Date', y='Tonnalite', color='Origine_Media',
    template="plotly_white",
    labels={'Tonnalite': 'Tonalité moyenne', 'Date': 'Date'}
)
fig_avg.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_avg, use_container_width=True)

st.divider()

# ── 9. BLOC 4 : volume d'articles ──────────────────────────────────────────
st.subheader("📊 Volume d'articles par date")

df_count = (
    df_gkg_filtered
    .groupby(['Date', 'Origine_Media'])['Tonnalite']
    .count()
    .reset_index()
    .rename(columns={'Tonnalite': 'Nombre_Articles'})
)
fig_count = px.area(
    df_count, x='Date', y='Nombre_Articles', color='Origine_Media',
    template="plotly_white",
    labels={'Nombre_Articles': "Nombre d'articles", 'Date': 'Date'}
)
fig_count.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_count, use_container_width=True)


# ── 8. ANALYSE TEXTUELLE ─────────────────────────────────────────────────────
with st.expander("📝 Voir l'analyse détaillée des résultats"):
    st.write("""
    L'analyse met en lumière une fracture lors du mois de décembre 2025. Alors que
    le graphique de volume révèle une explosion du nombre de publications, la courbe
    de tonalité moyenne montre une chute brutale, plongeant sous la barre des -5.
    Cette divergence confirme une crise médiatique majeure où l'intensité de
    l'information s'accompagne d'une forte négativité. On observe que si les médias
    internationaux maintiennent une certaine neutralité sur l'année, ils s'alignent
    sur la presse francophone en fin d'année, illustrant une dégradation généralisée
    de la perception des événements béninois à l'échelle mondiale.
    """)