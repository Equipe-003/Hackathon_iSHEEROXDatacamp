# Description des données

Le jeux de données capture deux acteurs et l'action efectuée par l'acteur 1 sur l'acteur 2.

## Champs de données
### Attributs EVENTID et DATE

* GlobalEventID.  (integer) : identifiant unique attribué à chaque enregistrement évènement
* SQLDATE. (integer) : Date à laquelle l'évènement a eu lieu, au format AAAAMMJJ
* MonthYear : Autre date au format AAAAMM
* Year : Alternative de date au format AAAA
* FractionDate (numeric): Autre format de la date de l'évènement, calculé sous la forme AAAA.FFFF où FFFF est le pourcentage de l'année écoulé à cette date. Cela permet de regrouper le mois et le jour en une plage fractionnaire comprise entre 0 et 0.99999 couvrant les 365 jours de l'année. Calculé avec la formule : (MOIS * 30 + JOUR)/365
  * La partie entière est l'année et la partie décimale est le pourcentage de jours passés

### Attributs des acteurs
Ici on décrit les attributs et les caractéristiques des deux acteurs impliqués dans l'évènement.
Pour un acteur on code ses attributs indiquant son appartenance géographique, ethnique, religieuse ainsi que le rôle de l'acteur dans l'environnement (élite politique, officier militaire)

* **Actor1Code:** Code Cameo brut pour l'acteur 1 (comprend les classes géographiques, sociales, ethniques, religieuses). Vide si Acteur 1 non identifié par le système
* **Actor1Name** : Nom réel de l'acteur 1. Dirigeant politique ou organisation ==> son nom officiel; correspondance géographique ==> nom du pays/ capitale/grande ville, correspondances ethniques/religieuses/de type ==> classe de correspondance de base (KURDE, CATHOLIQUE, POLICIER)
* **Actor1CountryCode** : code à 3 caractères correspondant à l'affiliation nationale de l'acteur 1.
* **Actor1KnownGroupCode** : Si Actor1 est une organisation intergouvernementale, non gouvernementale ou rebelle connue (Nation Unies, Banque mondiale, Al qaida) disposant de son propre code cameo, ce champ contiendra ce code
* **Actor1EthnicCode** : Si le document source précise son appartenance ethnique et que ce dernier dispose de son propre code CAMEO, le code est saisi ici. **Ex: ARAB**
* **Actor1Religion1Code** : Appartenance religieuse ayant son propre code CAMEO, ce code est saisi.
* **Actor1Religion2Code** : Si plusieurs codes réligieux spécifiés pour Actor1, ceci conteint le code secondaire
* **Actor1Type1Code** : Code CAMEO a trois caractère correspondant au type ou au rôle CAMEO de Actor1 s'il est spécifié.Ex: Forces de police, gouvernement, armée,...
* **Actor1Type2Code** : Si plusieurs code de type/rôle sont spécifiés, ceci donne le 2è code
* **Actor1Type3Code** : Donne le 3è code si dispo

### Attributs de l'action de l'évènement
Ces champs détaillent divers attributs de l'évènement (ce que Acor1 fait sur Actor2) et proposent plusieurs mécanismes pour évaluer l'importance ou l'impact immédiat d'un évènement.
* IsRootEvent : **Indicateur approximatif de l'importance d'un evènement pour créer des sous ensembles du flux d'évènements**
* EventCode: Code CAMEO brut décrivant l'action que fait Actor1 sur Actor2
* EventBaseCode: les codes d'évènements sont définis selon une taxonomie à 3 niveaux.Le code (0251: Appel a assouplissement des sanctions administratives) donnerait un EventBaseCode de (025 : Appel à capitulation)
* EventRootCode : Définit la catégorie de niveau racine à laquelle appartient le code de l'évènement. Le code (0251: Appel a assouplissement des sanctions administratives) donnerait un code racine de (02:Appel)
* QuadClass : 4 classifications principales:
  * 1= coopération verbale, 2=coopération matérielle,3=conflit matériel, 4=conflit verbal
* GoldsteinScale: Score numérique attribué (entre -10 et +10) réflétant l'impact théorique que ce type d'évènement aura sur la stabilité d'un pays. Ce champs spécifie alors le score de Goldstein. ce score est basé sur le type d'évènement.
* Nummentions: Nombre total du mention de cet évènement dans l'ensemble des documents sources. **Servir à évaluer l'importance d'un évènement**: plus cet évènement fait l'objet de discussions, plus il susceptible d'être significatif. Champ mis à jour si ultérieurement prise en compte
**Recommandation:** Normaliser ce champ à la moyenne ou a une autre mesure de l'ensemble des evènements sur la période considérée.
* NumSources : Nombre de sources d'information contenant une ou plusieurs mentions de cet évènement. Peut servir à évaluer l'importance d'un évènement. Recommandé de la normalisé par rapport à la moyenne ou ... Des mises en jour pour des citations ultérieurs
* NumArticles: Nombre de documents sources contenant une ou plusieurs mentions de cet évènement. recommandé de normaliser, 
* AvgTone : Ton moyen de tous les documents contenant un ou plusieurs mentions de cet évènement. Varie entre -100 (extrêmement négatif).Les valeurs courantes varient entre -10 et +10, 0 indique une neutralité

Recommandation: Utiliser comme méthode de filtrage du contexte des évènements et constitue un indicatif de l'importance. Ex: un émeute présentant un ton moyen légèrement négatif est probablement un evènement mineur. Une émeute présentatnt un score positif suggère probablement un évènement très mineur décrit dans un contexte de récit positif.

## Géographie des évènements
Ici on géoréférence chaque évènement selon trois dimensions principales. Il géoréférence le lieu de l'action. Peut être vide (si le lieu n'est pas trouvé).
Utile pour placer les actions sur une carte ou dans un autre contexte spatial.

Privilégier le filtrage avec ActorGeo_CountryCode

* Actor1Geo_Type : niveau de précision géographique du lieu.
  *  1= Pays
  *  2 = État US
  *  3 = Ville/lieu aux US
  *  4 = Ville/lieu hors US
  *  5 = Division administrative hors US (équivalent d’un État).
* Actor1Geo_Fullname (texte) : nom complet du lieu tel qu’il apparaît (ex. « Paris, France » ou « Texas, United States »).
* Actor1Geo_CountryCode (texte)
* **Actor1Geo_ADM1Code** (texte) : code pays + code de la division administrative (ex. « US.TX » pour Texas).
* Actor1Geo_Lat (numérique) : latitude du centre du lieu.
* Actor1Geo_Long (numérique) : longitude du centre du lieu.
* Actor1Geo_FeatureID : identifiant unique du lieu dans les bases GNS/GNIS. Renseigné uniquement pour les villes/lieux (codes 3 et 4).

# Taxonomie CAMEO



## Others
La texte correspondant à la description de l'évènement utilise le dictionnaire TABARI ACTORS.

Remarque: l'un des deux champs d'acteurs peut être vide dans des situations impliquant un seul acteur, ou ne contenir que des détails minimaux pour des acteurs tels que des << hommes armés non identifiés>>

GDELT utilise la taxonomie CAMEO et donc des codes peuvent être associés

> AvgTone est une forme d'analyse de sentiment

> Dans chaque article, on associe le texte complet: GKG
> Donc dans un même article, on aura plusieurs GKG


## GKG Datasets
Pour faciliter la compréhension de votre projet par vos collaborateurs, voici une description structurée et accessible des colonnes de la table **GKG (Global Knowledge Graph) v2.1**. 

Conformément à vos observations techniques et aux sources, les préfixes utilisés dans la documentation (V1, V2, V2.1) sont retirés dans les noms de colonnes réels de la base (ex: `V2SOURCECOLLECTIONIDENTIFIER` devient **`SourceCollectionIdentifier`**).

### 1. Informations d'Identification et Source
Ces colonnes permettent de savoir d'où vient l'information et de l'identifier de manière unique.
*   **`GKGRECORDID`** : Identifiant unique de l'enregistrement, basé sur la date et l'heure.
*   **`Date`** : Date et heure de publication de l'article au format `AAAAMMJJHHMMSS`.
*   **`SourceCollectionIdentifier`** : Type de source (ex: 1 = Web, 2 = Citation hors ligne, 3 = Archive académique).
*   **`SourceCommonName`** : Nom convivial du média (ex: `lemonde.fr` ou `BBC Monitoring`).
*   **`DocumentIdentifier`** : L'URL ou l'identifiant unique permettant d'accéder à l'article original.

### 2. Entités et Thématiques (Le "Qui", "Où" et "Quoi")
Le GKG extrait les éléments clés du texte. Les versions "Enhanced" incluent les **offsets** (positions dans le texte) pour permettre une analyse de proximité.
*   **`Themes` / `EnhancedThemes`** : Liste des thèmes abordés (plus de 300 catégories comme "Économie", "Santé", "Conflit").
*   **`Locations` / `EnhancedLocations`** : Lieux géographiques mentionnés, avec coordonnées GPS et codes pays FIPS.
*   **`Persons` / `EnhancedPersons`** : Noms des personnes physiques citées dans l'article.
*   **`Organizations` / `EnhancedOrganizations`** : Noms des entreprises, ONG ou institutions gouvernementales.
*   **`AllNames`** : Liste élargie de noms propres incluant des lois, des événements nommés (ex: "Coupe du Monde") ou des mouvements sociaux.

### 3. Analyses Émotionnelles et Sentiment
*   **`Tone`** : Score moyen du sentiment de l'article (de -100 pour très négatif à +100 pour très positif).
*   **`GCAM` (Global Content Analysis Measures)** : Une analyse ultra-détaillée mesurant plus de **2 300 dimensions émotionnelles** spécifiques (anxiété, optimisme, etc.).

### 4. Données Quantitatives et Citations
*   **`Counts`** : Chiffres spécifiques liés à des événements (ex: nombre de manifestants, de blessés ou de déplacés).
*   **`Amounts`** : Montants numériques précis mentionnés (ex: prix d'une denrée, montant d'une aide financière, nombre de troupes).
*   **`Quotations`** : Extraits de citations directes identifiées dans le texte, parfois accompagnées du verbe introducteur (ex: "a déclaré", "a nié").

### 5. Multimédia et Traduction
*   **`SharingImage`** : URL de l'image principale choisie par le média pour le partage sur les réseaux sociaux.
*   **`RelatedImages` / `SocialVideoEmbeds`** : Liens vers les images, vidéos (YouTube, Vimeo) ou publications sociales (Twitter, Instagram) intégrées dans l'article.
*   **`TranslationInfo`** : Pour les articles non anglais, précise la langue d'origine (parmi 65 langues) et le système de traduction utilisé.

### Note sur les "Offsets" (Positions)
Les colonnes préfixées par **"Enhanced"** (ou incluant le terme "Offset") indiquent la position précise des mots dans l'article. Cela permet à vos collaborateurs de savoir si deux entités (ex: un ministre et une ville) sont citées dans la même phrase, ce qui renforce la précision de l'analyse de leur relation.




Comment relier le GKG à la base Events ?
Il est tout à fait possible de joindre (performer un "join") les deux bases de données. Les sources indiquent plusieurs mécanismes pour établir ce lien :
L'identifiant EventID : Le fichier complet du GKG contient une liste des EventIDs de chaque événement trouvé dans le même article que les informations extraites par le GKG
. Cela permet une "contextualisation riche" en reliant directement une ligne du GKG aux événements CAMEO correspondants


## Plan de travail
Pour faire ressortir des insights forts sur ce qui est rapporté sur le Bénin, le Global Knowledge Graph (GKG) est un complément indispensable à la base des événements (Events). Alors que la table des événements se limite à cataloguer des actions physiques ("qui a fait quoi à qui"), le GKG est conçu pour quantifier les dimensions latentes, géographiques et structurelles du discours médiatique mondial

1. Au-delà de l'action : Le "Sentiment" et le "Contexte"
Analyse émotionnelle profonde (GCAM) : Là où la table Events ne propose qu'un score de "ton" basique, le système GCAM du GKG mesure plus de 2 300 dimensions émotionnelles et thématiques (ex: anxiété, optimisme, passivité)
* Cela vous permet de comprendre non pas seulement ce qui arrive au Bénin, mais comment le monde réagit émotionnellement à ces événements
* Thématiques riches : Le GKG reconnaît plus de 300 thèmes (contre environ 20 catégories de base dans CAMEO), incluant des indicateurs économiques (prix des denrées), des enjeux sociaux (marginalisation) ou des crises sanitaires

2. Données chiffrées et Citations (Le "Dur")
Extractions de montants (Amounts) : Le GKG extrait les chiffres précis cités dans les articles : promesses d'aide financière, prix de la nourriture au Bénin, nombre de troupes déployées ou nombre de foyers affectés par une catastrophe. C'est une mine d'or pour transformer des récits médiatiques en données statistiques exploitables
* Citations directes (Quotations) : Il permet d'isoler les déclarations officielles ou les témoignages, en précisant même le verbe utilisé (ex: "a nié", "a accepté"), offrant un aperçu direct de la posture des leaders d'opinion

3. Réseautage et Proximité
Le réseau global : Le GKG connecte les personnes, les organisations et les lieux dans un réseau holistique
* Grâce aux offsets de caractères (positions dans le texte), vous pouvez techniquement associer une fonction (ex: "Ministre") à une personne précise et à un lieu, ce qui permet de reconstruire la structure d'influence autour du Bénin
