# 🇧🇯 Bénin Insights Challenge — iSHEERO × DataCamp Donates 2026

> **Transformer des données mondiales en connaissance locale.**

## Table des matières

- [Présentation du projet](#présentation-du-projet)
- [Équipe](#équipe)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Extraction des données](#extraction-des-données)


---

## Présentation du projet

Ce projet est réalisé dans le cadre du **Hackathon iSHEERO × DataCamp Donates 2026 — Bénin Insights Challenge**.

**Mission :** Extraire et analyser les événements concernant le Bénin depuis la base de données mondiale **GDELT** sur les 12 derniers mois (mai 2025 – avril 2026), puis produire des insights actionnables à destination de journalistes, chercheurs et décideurs publics.

**Source de données :** [GDELT](https://www.gdeltproject.org/) (Global Database of Events, Language and Tone) — une base publique qui surveille en temps réel les médias du monde entier dans plus de 100 langues, disponible sur Google BigQuery.

**Période analysée :** `20250501` → `20260420`  
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
│    événements
├── scripts/
│   └── data_pipeline.py  # Module Python réutilisable (BigQuery)
├── models/               # Modèles ML entraînés
├── dashboard/            # Application Streamlit
├── credentials/          # Credentials Google Cloud (non versionnés)
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

## Extraction des données

Le pipeline d'extraction est composé de deux fichiers qui communiquent :

- **`scripts/data_pipeline.py`** — module Python avec les fonctions BigQuery réutilisables
- **`notebooks/data_extraction.ipynb`** — notebook qui pilote l'extraction et sauvegarde le CSV dans `data/raw/`

Pour générer les données via cette pipeline, une authentification auprès de Google BigQuery est nécéssaire.Deux options sont disponibles pour gérer l'authentification.

---

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
Le fichier se télécharge automatiquement.

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

---

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

>  **Pour le jury :** l'Option B (ADC) est la plus rapide. Une seule commande suffit pour s'authentifier, aucun fichier à déplacer.

---


