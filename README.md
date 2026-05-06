# 🇧🇯 Bénin Insights Challenge — iSHEERO × DataCamp Donates 2026

> **Transformer des données mondiales en connaissance locale.**

## Table des matières

- [Présentation du projet](#présentation-du-projet)
- [Équipe](#équipe)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Extraction des données](#extraction-des-données)
- [Néttoyage et exploration des données](#néttoyage-et-exploration-des-données)
- [Analyse approfondir par le ML](#analyse-approfondir-par-le-ml)
- [Visualisation statistique](#visualisation-statistique)


---

## Présentation du projet

Ce projet est réalisé dans le cadre du **Hackathon iSHEERO × DataCamp Donates 2026 — Bénin Insights Challenge**.

**Mission :** Extraire et analyser les événements concernant le Bénin depuis la base de données mondiale **GDELT** sur les 12 derniers mois (Jan 2025 – Décembre 2025), puis produire des insights actionnables à destination de journalistes, chercheurs et décideurs publics.

**Source de données :** [GDELT](https://www.gdeltproject.org/) (Global Database of Events, Language and Tone) — une base publique qui surveille en temps réel les médias du monde entier dans plus de 100 langues, disponible sur Google BigQuery.

**Période analysée :** `20250101` → `20251231`  
**Filtre géographique :** `ActionGeo_CountryCode = 'BN'` (Bénin, code FIPS)

---

## Équipe

| Profil | Nom | Responsabilité |
|--------|-----|----------------|
|  Data Engineer | Martin-Junior ADECHI | Pipeline GDELT, extraction BigQuery, nettoyage des données |
|  Data Analyst | Denakpo Paule | Dashboard interactif, visualisations, executive summary |
|  ML Engineer | BONI Zoul | Analyse de sentiment, clustering, classification des événements |
|  Data Scientist | TADOGBE Ahouéfa Trésor Steffi | Approche analytique, interprétation, rapport final, pitch |

---

## Structure du projet

```
.
├── data/
│   ├── raw/              # Données brutes extraites de BigQuery
│   └── processed/        # Données nettoyées 
│   
├── notebooks/
│   └── data_extraction.ipynb       # Extraction BigQuery
│   └── data_cleaning.ipynb       # Nettoyage des données brutes extraites   
│   └── data_exploration.ipynb      # EDA des données
│   └── ml_classification.ipynb       # algorithme de ML
│   └── ml_clustering.ipynb       # algorithme de ML
│   └── ml_sentiment.ipynb       # algorithme de ML       
│   └── visualisations_insights_gdeltevents.ipynb       # visualisation statistique du dataset 
├── scripts/
│   └── data_pipeline.py  # Module Python réutilisable (BigQuery)
|
|
├── models/               # Modèles ML entraînés
│   └── classification/    # Modèle de classification des events
│   └── clustering/        # Modèle de clustering des évenements   
│   └── sentiment_analysis/       # Modèles d'analyse du ton/sentiment autour de l'actualité
|   
├── dashboard/            # Power BI
├── requirements.txt
└── README.md
```
 
> Les données sont régénérables via le notebook d'extraction (voir ci-dessous).  


---

## Installation

### Prérequis

- Python 3.11+
- Un compte Google (pour l'accès BigQuery)

### Cloner le repo et installer les dépendances

```bash
git clone https://github.com/[organisation]/[repo]
cd [repo]

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---
# Data

## Sources de données
 
Le projet exploite deux tables complémentaires de GDELT qui répondent à des questions différentes.
 
**GDELT Events** répond à la question *"Qui a fait quoi à qui, où et quand ?"*. Chaque ligne est un événement géopolitique — une action concrète entre deux acteurs. C'est une base quantitative et structurée utilisée pour compter et classer les événements, cartographier leur répartition géographique, identifier les acteurs impliqués et mesurer les pics de couverture médiatique.
 
**GDELT GKG** répond à la question *"Comment les médias parlent-ils du Bénin ?"*. Chaque ligne est un article de presse analysé — thèmes détectés, entités nommées, ton éditorial. C'est une base qualitative et sémantique utilisée pour analyser l'évolution du sentiment médiatique dans le temps et identifier les médias les plus actifs.
 
> Un événement peut avoir un **GoldsteinScale positif** (coopération) dans Events mais un **tone négatif** dans GKG si les médias le couvrent dans un contexte critique. C'est cette tension entre les faits et leur perception médiatique qui produit les insights les plus intéressants.

## Extraction des données

Le pipeline d'extraction est composé de deux fichiers qui communiquent :

- **`scripts/data_pipeline.py`** — module Python avec les fonctions BigQuery réutilisables
- **`notebooks/data_extraction.ipynb`** — notebook qui pilote l'extraction et sauvegarde le CSV dans `data/raw/`

Pour générer les données via cette pipeline, une authentification auprès de Google BigQuery est nécéssaire.Deux options sont disponibles pour gérer l'authentification.

### Option A — Service Account JSON *(recommandée pour ce projet)*

Cette option utilise une clé d'accès liée à un projet Google Cloud spécifique.

**Étape 1 — Créer un projet Google Cloud**

Aller sur [console.cloud.google.com](https://console.cloud.google.com), cliquer sur **"Nouveau projet"** et lui donner un nom.

**Étape 2 — Activer l'API BigQuery**

Dans le projet : **"API et services"** → **"Bibliothèque"** → rechercher **"BigQuery API"** → **Activer**.

**Étape 3 — Créer un Service Account**

**"API et services"** → **"Identifiants"** → **"Créer des identifiants"** → **"Compte de service"**.  
Attribuer le rôle **BigQuery User** au compte de service créé.

**Étape 4 — Télécharger la clé JSON**

Cliquer sur le service account → onglet **"Clés"** → **"Ajouter une clé"** → **"JSON"**.  
Le fichier se télécharge automatiquement. Renommer le fichier en **"credentials.json"**

**Étape 5 — Placer le fichier dans le repo**

```bash
# Créer le dossier credentials s'il n'existe pas
mkdir credentials

# Déplacer le fichier téléchargé
mv ~/Downloads/votre-fichier.json credentials/credentials.json
```

> Ne jamais committer ce fichier sur GitHub. Il est déjà listé dans le `.gitignore`.

**Étape 6 — Lancer l'extraction**

Ouvrir `notebooks/data_extraction.ipynb` **depuis la racine du repo** (dans VS Code ou avec `jupyter notebook`), puis exécuter toutes les cellules dans l'ordre.

```
Résultat : data/raw/gdelt_bn_2025.csv est généré automatiquement.
```

### Option B — Application Default Credentials (ADC) *(la plus rapide)*

Cette option ne nécessite aucun fichier JSON. Elle utilise directement votre compte Google via Google Cloud CLI.

**Étape 1 — Installer Google Cloud CLI**

Télécharger et installer depuis : [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

**Étape 2 — S'authentifier**

```bash
gcloud auth application-default login
```

Un navigateur s'ouvre automatiquement. Se connecter avec un compte Google qui a accès à BigQuery. C'est tout.

**Étape 3 — Lancer l'extraction**

Le script `scripts/data_pipeline.py` détecte automatiquement ces credentials sans aucune modification de code. Ouvrir et exécuter `notebooks/data_pipeline.ipynb` normalement.

```
Résultat : data/raw/gdelt_bn_2025.csv est généré automatiquement.
```

---

### Comparatif des deux options

| | Option A — Service Account | Option B — ADC |
|---|---|---|
| **Fichier à placer** | `credentials/credentials.json` | Aucun |
| **Outil supplémentaire** | Aucun | Google Cloud CLI |
| **Complexité** | Moyenne | Faible |
| **Recommandé pour** | Automatisation, CI/CD | Reproduction rapide, jury |



---

# Nettoyage et exploration des données

## Nettoyage des données

Après l’extraction, une étape de nettoyage des données est réalisée afin de garantir leur qualité et leur exploitabilité pour les analyses ultérieures. Dans le cadre de ce projet, il s’agit d’un **nettoyage primaire**, visant principalement à structurer et préparer les données brutes issues de GDELT.

Ce nettoyage s’organise autour de deux axes principaux :

### 1. Gestion des valeurs manquantes

Un traitement systématique des valeurs manquantes est appliqué selon un seuil de tolérance :

- les colonnes présentant plus de **80 % de valeurs manquantes** sont supprimées ;
- les colonnes dont le taux de valeurs manquantes est inférieur à ce seuil sont conservées en l’état, afin de préserver l’information utile pour les étapes d’analyse et de modélisation.

### 2. Traitement des informations linguistiques

Le dataset GKG comporte une variable `TranslationInfo` qui renseigne, pour les articles non anglophones, la langue d’origine ainsi que le système de traduction utilisé.

Les valeurs de cette variable suivent un format spécifique incluant systématiquement l’anglais comme langue de destination. À partir de cette structure, une nouvelle variable intitulée :
`translation_source_langs`
a été construite afin d’extraire et de conserver uniquement la **langue source des articles**. Cette transformation permet d’identifier la diversité linguistique des sources médiatiques et d’enrichir les analyses en intégrant une dimension géolinguistique pertinente.

### 3. Remarque

Ce nettoyage constitue une étape préliminaire du pipeline. Des traitements plus avancés (normalisation, filtrage du bruit, feature engineering) pourront être appliqués ultérieurement en fonction des besoins spécifiques des analyses et des modèles.

Le code de nettoyage est implémenté dans le module `scripts/data_pipeline.py`, qui contient les fonctions réutilisables du pipeline.
Le notebook `notebooks/data_cleaning.ipynb` orchestre l’exécution de ces fonctions, permettant de reproduire les étapes de nettoyage et d’enregistrer les données traitées dans le dossier :`data/processed/`

## Exploration des données

L'analyse exploratoire est conduite dans `notebooks/data_exploration.ipynb` et s'appuie sur les deux datasets GDELT nettoyés : **Events** (`data/processed/events_cleaned.csv`) et **GKG** (`data/processed/gkg_cleaned.csv`).
 

 
### Analyses réalisées
 
#### Types d'événements
 
Les événements sont classifiés selon la taxonomie CAMEO à deux niveaux de granularité : les **20 catégories `EventRootCode`** (déclarations publiques, protestations, conflits armés, aide humanitaire...) et les **4 grandes catégories `QuadClass`** (coopération verbale, coopération matérielle, conflit verbal, conflit matériel). Cette double lecture permet d'identifier à la fois la nature précise des événements et leur polarité générale.
 
#### Répartition géographique par département
 
Les événements localisés précisément (ActionGeo_Type 4 et 5, soit ~12% du dataset) sont mappés aux 12 départements béninois via une stratégie combinée : code ADM1 direct, inférence par nom de ville, et géolocalisation par bounding box GPS. Une heatmap département × QuadClass révèle les zones de concentration des conflits et des coopérations.
 
> **Note méthodologique :** 88% des événements GDELT sont localisés uniquement au niveau national. L'analyse départementale est indicative et porte sur les événements géolocalisés précisément.
 
#### Dimension Nationale vs internationale
 
Chaque événement est qualifié selon que les acteurs impliqués sont béninois ou étrangers, permettant de mesurer quelle part de l'actualité du Bénin implique des acteurs extérieurs et dans quels départements cette internationalisation est la plus prononcée.
 
#### Acteurs les plus impliqués par type d'événement
 
Les acteurs nommés (pays, organisations, leaders) sont croisés avec les catégories QuadClass pour identifier qui apparaît dans les événements coopératifs versus conflictuels. Les acteurs génériques (GOVERNMENT, POLICE, MILITARY) sont exclus pour ne retenir que les entités nommées significatives.
 
#### Pics de couverture médiatique (buzz)
 
Un score de buzz composite est calculé pour chaque événement en combinant `NumMentions` (×0.4), `NumSources` (×0.4) et `NumArticles` (×0.2) après normalisation Min-Max. Ce score permet d'identifier les mois où le Bénin a le plus attiré l'attention médiatique mondiale et de relier ces pics aux événements déclencheurs.
 
#### Top 10 médias couvrant le Bénin
 
Le classement est construit par croisement des deux datasets : le volume d'événements couverts est issu de Events (extraction du domaine depuis `SOURCEURL`). Cette fusion permet d'identifier non seulement les médias les plus actifs, mais aussi leur origine — A quel point le Bénin est il représenté dans les médias à l'international ?
 
#### Évolution du ton médiatique — GKG
 
Le champ `V2Tone` du GKG est parsé en 6 dimensions (tone global, score positif, score négatif, polarité, activité, auto-référence). L'agrégation mensuelle révèle les périodes de couverture la plus négative et la plus positive, ainsi que les mois de forte polarité où les médias étaient émotionnellement divisés — même si le tone net semblait modéré.

D'autre analyses détaillées répondant à des questions utiles à la décision sont présentent dans le notebook `visualisations_insights_gdeltevents.ipynb`

---

## Analyse approfondir par le ML

Les modèles de machine learning sont développés dans trois notebooks dédiés.
 
### Clustering K-Means — `notebooks/ml_clustering.ipynb`
 
Une première version du clustering est intégrée directement dans le notebook d'exploration comme preuve de concept puis dans le notebook `ml_clustering.ipynb`. Les événements sont regroupés en clusters homogènes à partir de quatre features numériques (`GoldsteinScale`, `AvgTone`, `NumMentions`, `NumSources`). Le nombre optimal de clusters est déterminé par la méthode du coude combinée au score de silhouette. Chaque cluster est ensuite profilé selon sa polarité moyenne (coopératif, conflictuel, mixte) et sa relation avec les catégories QuadClass.

 ### Classification — `notebooks/ml_classification.ipynb`
Une première version du clustering est intégrée directement dans le notebook d'exploration comme preuve de concept puis dans le notebook `ml_classification.ipynb`. Il s'agit d'un modèle de classification des catégories d'évenements (QuardClass) basé sur quatre features numériques (`GoldsteinScale`, `AvgTone`, `NumMentions`, `NumSources`).
 
### Analyse de sentiment — `notebooks/ml_sentiment.ipynb`
 
Ce notebook construit deux modèles complémentaires d'analyse de sentiment à partir des features structurelles des événements GDELT.
 
**Modèle 1 — Régression AvgTone**
 
Prédit la valeur numérique du tone médiatique d'un événement. Quatre algorithmes sont comparés : une baseline (prédiction de la moyenne), une régression Ridge, un Random Forest et un Gradient Boosting. La sélection du meilleur modèle repose sur le R² et le MAE. L'importance des features révèle quelles caractéristiques d'un événement sont les plus prédictives de sa couverture médiatique.
 
**Modèle 2 — Classification Sentiment**
 
Classifie chaque événement en trois catégories (positif, neutre, négatif) selon des seuils définis sur la distribution de `AvgTone` (seuils à ±2). Les mêmes quatre algorithmes sont comparés, évalués sur l'accuracy et le F1-macro (qui pénalise les classes ignorées). La classe `balanced` est appliquée pour gérer le déséquilibre naturel entre les catégories.
 
**Features utilisées**
 
| Feature | Source | Rôle |
|---------|--------|------|
| `GoldsteinScale` | Events | Impact théorique de l'événement sur la stabilité |
| `NumMentions` | Events | Volume de citations médias |
| `NumSources` | Events | Diversité des sources |
| `NumArticles` | Events | Couverture totale |
| `QuadClass` | Events | Grande catégorie de l'événement |
| `EventRootCode` | Events | Type précis de l'action (CAMEO) |
 
**Modèles sauvegardés**
 
Les modèles entraînés sont sérialisés en `.pkl` dans `models/sentiment_analysis/`, `models/classification/`, `models/clustering/` pour être réutilisés directement par le dashboard Streamlit sans ré-entraînement.

## Visualisation statistique


**PS:** L’intelligence artificielle a été utilisée de manière ciblée et réfléchie pour accélérer certaines étapes d’analyse, de structuration et de rédaction, tout en laissant l’interprétation et les arbitrages méthodologiques sous contrôle humain
