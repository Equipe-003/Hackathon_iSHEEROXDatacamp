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



