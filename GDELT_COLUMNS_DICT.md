# Dictionnaire des colonnes GDELT — Bénin 2025

> Source : GDELT Data Format Codebook v1.03  
> Filtré pour les colonnes pertinentes au projet Bénin Insights Challenge.

## Date & Identification

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **GlobalEventID** | int | Identifiant unique global de l'événement | Clé primaire, jointure |
| **SQLDATE** | int | Date au format YYYYMMDD | Filtrage temporal |
| **MonthYear** | int | Date au format YYYYMM | Agrégation mensuelle |
| **Year** | int | Année (YYYY) | Agrégation annuelle |
| **FractionDate** | float | Date fractionnelle (YYYY.FFFF) | Tri temporel approximatif |

---

## Acteurs (Actor1 & Actor2)
La différence entre Actor1 et Actor2 :
- Actor1 est celui qui initie l'action — l'auteur
- Actor2 est celui qui reçoit l'action — la cible

Le code caméo est un dictionnaire universel qui traduit les informations en codes numériques structurés.

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **Actor1Code** | str | Code CAMEO complet de l'acteur 1 (géo, classe, ethnie, religion, type) | Parsing avancé des acteurs |
| **Actor1Name** | str | Nom de l'acteur 1 (leader, organisation, pays, groupe, etc.) | Identification acteur |
| **Actor1CountryCode** | str | Code pays CAMEO de l'acteur 1 (3 caractères) | Provenance acteur |
| **Actor1KnownGroupCode** | str | Code IGO/NGO/rebel si connu | Organisations connues |
| **Actor1EthnicCode** | str | Code ethnie CAMEO si spécifié | Dimension ethnique |
| **Actor1Religion1Code** | str | Code religion CAMEO primaire si spécifié | Dimension religieuse |
| **Actor1Type1Code** | str | Rôle/type CAMEO (Police, Government, Military, Rebels, etc.) | Catégorisation acteur |
| **Actor2Code** | str | Code CAMEO complet de l'acteur 2 | (même que Actor1) |
| **Actor2Name** | str | Nom de l'acteur 2 | (même que Actor1) |
| **Actor2CountryCode** | str | Code pays CAMEO de l'acteur 2 | (même que Actor1) |
| **Actor2Type1Code** | str | Rôle/type de l'acteur 2 | (même que Actor1) |

---

## Action (Event)

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **EventCode** | str | Code CAMEO à 4 caractères (level 3 de la taxonomie) | Type d'événement détaillé |
| **EventBaseCode** | str | Code base CAMEO (level 2 de la taxonomie) | Agrégation événement |
| **EventRootCode** | str | Code racine CAMEO (level 1 de la taxonomie) | Catégorie haute niveau |
| **QuadClass** | int | Classification haute niveau : 1=Verbal Coop, 2=Material Coop, 3=Verbal Conflict, 4=Material Conflict | Segmentation conflictualité |
| **IsRootEvent** | bool | 1 si événement en lead paragraph (important), 0 sinon | Proxy d'importance |

---

## Impact & Importance (Media Attention)

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **GoldsteinScale** | float | Score d'impact théorique : -10 (très déstabilisant) à +10 (très constructif) | Impact pays |
| **NumMentions** | int | Nombre total de mentions dans tous les articles | Viralité, couverture |
| **NumSources** | int | Nombre de sources uniques mentionnant l'événement | Validation, consensus |
| **NumArticles** | int | Nombre d'articles différents mentionnant l'événement | Importance médias |
| **AvgTone** | float | Ton moyen : -100 (très négatif) à +100 (très positif), 0 = neutre | Sentiment, contexte |

---

## Géolocalisation (Action, Actor1, Actor2)

**Champs pour ActionGeo_* (lieu de l'action) — Principaux :**

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **ActionGeo_Type** | int | Résolution : 1=COUNTRY, 2=USSTATE, 3=USCITY, 4=WORLDCITY, 5=WORLDSTATE | Précision géo |
| **ActionGeo_Fullname** | str | Nom complet du lieu (ex: "Cotonou, Benin" ou "Benin") | Identification lieu |
| **ActionGeo_CountryCode** | str | Code FIPS pays (ex: "BN" pour Bénin) | Filtrage géographique |
| **ActionGeo_ADM1Code** | str | Code admin division 1 (province/région, ex: "BN24") | Localisation détaillée |
| **ActionGeo_Lat** | float | Latitude du centroïde | Mapping |
| **ActionGeo_Long** | float | Longitude du centroïde | Mapping |
| **ActionGeo_FeatureID** | int | GNS/GNIS Feature ID (identifiant géographique standard) | Jointure géo |

**Actor1Geo_*, Actor2Geo_* — Même structure pour les localisations des acteurs.**

---

## Métadonnées

| Colonne | Type | Description | Utilité |
|---------|------|-------------|---------|
| **DATEADDED** | int | Date d'ajout à la base (YYYYMMDD) | Détection mise à jour tardive |
| **SOURCEURL** | str | URL de l'article source (si depuis 2013-04-01) | Tracabilité, validation |

---

## Colonnes à Privilégier pour Bénin Insights

### Pour l'Analyse de Sentiment & Ton
- **AvgTone** — sentiment des événements
- **QuadClass** — cooperation vs conflict
- **GoldsteinScale** — impact théorique

### Pour l'Analyse d'Acteurs
- **Actor1Name, Actor2Name** — qui sont les acteurs
- **Actor1CountryCode, Actor2CountryCode** — d'où viennent-ils
- **Actor1Type1Code, Actor2Type1Code** — rôle (military, govt, rebels, etc.)

### Pour l'Analyse Géographique
- **ActionGeo_Fullname** — où se passe l'événement
- **ActionGeo_CountryCode** — confirmation filtrage pays
- **ActionGeo_Lat, ActionGeo_Long** — pour mapping
- **ActionGeo_Type** — qualité de la localisation

### Pour l'Analyse Temporelle & Importance
- **SQLDATE** — quand
- **EventRootCode** — type d'événement
- **NumMentions, NumArticles** — couverture médias
- **IsRootEvent** — importance approximative

### Pour la Traçabilité
- **GlobalEventID** — clé unique
- **DATEADDED, SOURCEURL** — provenance

---

## Notes Importantes

1. **CAMEO Taxonomy** : EventCode/EventRootCode utilisent la taxonomie CAMEO 1.1b3. Cf. [CAMEO Manual](http://gdeltproject.org/data/documentation/CAMEO.Manual.1.1b3.pdf)
2. **Codes Pays** : Actor*CountryCode utilise les codes CAMEO (3 caractères, ex: "BN"). ActionGeo_CountryCode utilise FIPS10-4 (2 caractères, ex: "BN").
3. **Valeurs Manquantes** : Actor1/2Name, Codes peuvent être vides si l'article ne spécifie pas (ex: "armed gunmen").
4. **Duplication** : Quelques GlobalEventID dupliqués existent (erreur historique dans GDELT) — déduplication sur attributs recommandée.
5. **Updates** : NumMentions/NumArticles/AvgTone peuvent être mises à jour si le même événement est mentionné ultérieurement (retrouvailled dans archives, pas dans stream quotidien).

---
## Documentation des données GDELT GKG (Colonnes extraites)

| Colonne | Type | Description | Utilité |
| :--- | :--- | :--- | :--- |
| **`Date`** | Entier | Date et heure de publication de l'article au format `AAAAMMJJHHMMSS`. | Permet une synchronisation temporelle précise et l'analyse de l'évolution chronologique des récits. |
| **`SourceCommonName`** | Texte | Nom convivial du média (ex: `lemonde.fr`) ou de la source (ex: `BBC Monitoring`). | Essentiel pour l'analyse des flux d'information et l'identification des sources d'influence médiatique. |
| **`Persons`** | Liste délimitée | Noms des personnes physiques identifiées dans le texte par l'algorithme de GDELT. | Permet de repérer les acteurs clés, les leaders d'opinion et de reconstruire les réseaux d'influence. |
| **`Organizations`** | Liste délimitée | Noms des entreprises, ONG, institutions gouvernementales ou organisations locales. | Utile pour suivre l'implication des entités institutionnelles et corporatives dans les événements mondiaux. |
| **`Locations`** | Blocs délimitées | Liste des lieux mentionnés incluant codes pays FIPS, coordonnées GPS et noms complets. | Indispensable pour la cartographie et l'analyse spatiale haute résolution des événements. |
| **`Counts`** | Blocs délimités | Données chiffrées explicites liées à des catégories (ex: "100 manifestants", "50 blessés"). | Permet une évaluation quantitative immédiate de l'ampleur et de l'impact physique des situations rapportées. |
| **`TranslationInfo`** | Séquence de codes | Informations sur la langue source originale et le système de traduction utilisé. | Permet d'isoler les sources locales non-anglophones issues des 65 langues traduites en temps réel. |

---

### Colonnes stratégiques (Non extraites par limitation de quota)

Il est important de noter que deux colonnes majeures ont été volontairement exclues de notre extraction BigQuery afin de respecter le quota gratuit de **1 To par mois**. Ces colonnes sont les plus volumineuses du dataset GDELT :

1.  **`Themes` / `V2EnhancedThemes` :** Cette colonne catégorise le "Quoi". Elle contient une liste de plus de **300 thématiques** identifiées (Économie, Conflit, Santé, etc.). Son poids est important car elle liste chaque occurrence thématique avec sa position précise dans le texte (offsets).
2.  **`GCAM` (Global Content Analysis Measures) :** C'est la colonne la plus lourde de GDELT. Elle réalise ce que le projet considère comme le plus grand déploiement d'analyse de sentiment au monde, mesurant plus de **2 300 dimensions émotionnelles** (anxiété, optimisme, passivité, etc.) pour chaque article. À elle seule, elle représente souvent plus de **90 % du volume de données scanné** lors d'une requête.

