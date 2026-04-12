# Guide d'interopérabilité et de correspondance

Ce guide est destiné aux équipes qui connectent des systèmes existants : effectuer la correspondance de champs entre plateformes, construire des échanges de données, consolider des enregistrements provenant de sources multiples ou exécuter des pipelines ETL. PublicSchema joue le rôle d'un point de référence partagé (une pierre de Rosette) de sorte que chaque système n'ait besoin que d'une seule correspondance au lieu d'une correspondance vers chaque autre système.

## Sommaire

- [Quand utiliser cette approche](#quand-utiliser-cette-approche)
- [Le modèle de la pierre de Rosette](#le-modèle-de-la-pierre-de-rosette)
- [Étape 1 : Effectuer la correspondance de vos champs avec les propriétés PublicSchema](#étape-1--effectuer-la-correspondance-de-vos-champs-avec-les-propriétés-publicschema)
- [Étape 2 : Effectuer la correspondance de vos codes avec les vocabulaires PublicSchema](#étape-2--effectuer-la-correspondance-de-vos-codes-avec-les-vocabulaires-publicschema)
- [Étape 3 : Utiliser la correspondance pour l'échange de données](#étape-3--utiliser-la-correspondance-pour-léchange-de-données)
- [Étape 4 : Valider avec des schémas JSON](#étape-4--valider-avec-des-schémas-json)
- [Utiliser le modèle Excel pour la collecte de données](#utiliser-le-modèle-excel-pour-la-collecte-de-données)
- [Correspondances de systèmes dans les fichiers de vocabulaire](#correspondances-de-systèmes-dans-les-fichiers-de-vocabulaire)
- [Défis courants de correspondance](#défis-courants-de-correspondance)
- [Téléchargements disponibles](#téléchargements-disponibles)
- [Prochaines étapes](#prochaines-étapes)

## Quand utiliser cette approche

Cette approche fonctionne bien lorsque :

- Deux systèmes ou plus doivent échanger des données mais utilisent des noms de champs et des codes différents
- Vous déduplichez des enregistrements entre programmes ou secteurs
- Vous construisez un entrepôt de données ou un tableau de bord qui agrège des données de sources multiples
- Vous migrez des données d'une plateforme à une autre
- Vous construisez une couche de fédération entre des API d'agences

Vous n'avez pas besoin de modifier le modèle de données interne d'un quelconque système. La correspondance vit entre les systèmes, pas à l'intérieur.

## Le modèle de la pierre de Rosette

Sans référence partagée, connecter N systèmes nécessite N*(N-1)/2 correspondances bilatérales. Avec 5 systèmes, cela représente 10 tables de correspondance distinctes à maintenir.

Avec PublicSchema comme référence partagée, chaque système effectue sa correspondance vers PublicSchema une seule fois. Connecter un nouveau système signifie une seule correspondance, pas N-1. Plus important encore, comme chaque système effectue sa correspondance vers les mêmes définitions partagées, le sens est préservé tout au long de la traduction. Sans vocabulaire partagé, les correspondances bilatérales sont souvent approximatives : les codes d'un système peuvent ne pas avoir d'équivalents dans un autre.

![Chaque système effectue sa correspondance vers PublicSchema une seule fois](/images/rosetta-stone.svg)

Ce modèle fonctionne à la fois pour les noms de champs (propriétés) et les codes de valeurs (vocabulaires).

## Étape 1 : Effectuer la correspondance de vos champs avec les propriétés PublicSchema

Commencez par identifier quel concept PublicSchema correspond à l'entité dans votre système. Parcourez la [page des concepts](/concepts/) ou téléchargez le **classeur Excel de définition** pour un concept afin de voir toutes ses propriétés en un seul endroit.

Pour chaque champ de votre système, trouvez la propriété PublicSchema correspondante :

| Champ de votre système | Votre type | Propriété PublicSchema | Type PS |
|---|---|---|---|
| `first_name` | varchar(100) | `given_name` | string |
| `last_name` | varchar(100) | `family_name` | string |
| `dob` | date | `date_of_birth` | date |
| `enroll_date` | datetime | `enrollment_date` | date |
| `status` | int (FK) | `enrollment_status` | vocabulary |
| `gps_lat`, `gps_lon` | decimal | `geo_location` | geojson_geometry |

Quelques points à noter :

- **Tous les champs n'auront pas forcément une correspondance.** Certains champs sont spécifiques à votre système et n'ont pas d'équivalent canonique. C'est normal ; documentez la lacune.
- **Certains champs peuvent se diviser ou se fusionner.** Votre système peut stocker un nom complet dans un seul champ là où PublicSchema a `given_name` et `family_name` séparément, ou vice versa.
- **Les différences de type sont attendues.** Votre base de données peut utiliser des entiers ou des clés étrangères là où PublicSchema utilise des codes de vocabulaire. La correspondance gère la traduction.

Le téléchargement **CSV** du concept vous donne une liste plate de propriétés avec les types et les définitions, utile comme point de départ pour votre table de correspondance.

## Étape 2 : Effectuer la correspondance de vos codes avec les vocabulaires PublicSchema

Pour tout champ soutenu par un ensemble de valeurs contrôlées (codes de statut, genre, types de documents, etc.), effectuez la correspondance de vos codes vers le vocabulaire canonique. Consultez le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/) pour une présentation détaillée.

Le résultat clé est une table de correspondance de codes pour chaque vocabulaire :

| Votre code | Code PublicSchema | Notes |
|---|---|---|
| `1` | `active` | |
| `2` | `suspended` | |
| `3` | `completed` | Votre "closed" correspond à PS "completed" |
| `4` | *(non correspondant)* | Votre "archived" n'a pas d'équivalent PS |

## Étape 3 : Utiliser la correspondance pour l'échange de données

Une fois que vous disposez des correspondances de champs et de codes, vous pouvez les utiliser de plusieurs façons :

### Échange de données direct entre deux systèmes

Le système A exporte dans son propre format. Une couche de traduction effectue la correspondance des champs et codes du système A vers les propriétés et codes de vocabulaire PublicSchema. Une seconde couche de traduction effectue la correspondance de PublicSchema vers le format du système B.

![Le système A effectue sa correspondance vers PublicSchema, puis vers le système B](/images/data-exchange-flow.svg)

### Consolidation de données (ETL)

Plusieurs sources sont mises en correspondance avec le format canonique de PublicSchema et chargées dans un entrepôt de données partagé :

![Plusieurs sources effectuent leur correspondance vers PublicSchema, puis se consolident](/images/etl-consolidation.svg)

### Fédération d'API

Chaque agence expose une surface d'API alignée sur PublicSchema. La couche de fédération interroge toutes les API en utilisant les mêmes noms de champs et codes de vocabulaire. Consultez le [cas d'utilisation de l'harmonisation des API](/docs/use-cases/#harmonisation-des-api-au-sein-dune-fédération) pour un scénario concret.

## Étape 4 : Valider avec des schémas JSON

PublicSchema fournit un schéma JSON pour chaque concept. Utilisez-les pour valider les données après la correspondance et avant le chargement :

```python
import json
import jsonschema

schema = json.load(open("Person.schema.json"))
record = {
    "given_name": "Amina",
    "family_name": "Diallo",
    "date_of_birth": "1988-03-15",
    "gender": "female"
}
jsonschema.validate(record, schema)
```

La validation détecte :

- Les champs qui n'ont pas été correctement mis en correspondance (mauvais type, contexte requis manquant)
- Les codes de vocabulaire qui ne font pas partie de l'ensemble canonique
- Les problèmes structurels (tableaux là où des valeurs uniques sont attendues, ou vice versa)

## Utiliser le modèle Excel pour la collecte de données

Chaque page de concept propose un téléchargement de **modèle Excel**. Il s'agit d'un classeur de saisie de données où :

- La ligne 1 contient des libellés de champs lisibles par l'humain
- La ligne 2 contient les identifiants de propriétés PublicSchema
- Les champs soutenus par un vocabulaire ont une validation par liste déroulante (seuls les codes canoniques sont acceptés)
- Les commentaires de cellules incluent les définitions des propriétés

Cela est utile lorsque :

- Vous collectez des données auprès d'équipes de terrain qui travaillent avec des tableurs
- Vous avez besoin d'un format canonique pour la saisie de données sans construire une application personnalisée
- Vous souhaitez prototyper un formulaire de collecte de données avant de vous engager dans un système

Les données saisies dans le modèle sont déjà alignées sur PublicSchema et peuvent donc être chargées dans tout système disposant d'une correspondance PublicSchema.

## Correspondances de systèmes dans les fichiers de vocabulaire

Certains vocabulaires incluent des correspondances pré-construites pour des systèmes spécifiques (OpenIMIS, DCI, etc.) dans leurs fichiers source YAML. Ces correspondances listent les codes et libellés de chaque système, et la façon dont ils correspondent aux codes canoniques.

Consultez les pages de vocabulaire pour voir si votre système est déjà mis en correspondance. Si c'est le cas, vous pouvez utiliser la correspondance directement au lieu d'en construire une depuis le début.

Par exemple, le vocabulaire gender-type inclut des correspondances pour OpenIMIS et DCI, montrant qu'OpenIMIS utilise `"M"/"F"/"O"` et DCI utilise `"1"/"2"/"0"` pour les mêmes valeurs canoniques.

Consultez [Exemple de correspondance](/docs/mapping-example/) pour une présentation complète des correspondances de systèmes.

## Défis courants de correspondance

### Différences de granularité

Votre système peut avoir une entité "Personne" unique là où PublicSchema sépare Personne, Identifiant et Adresse en concepts distincts. Ou vice versa : votre système peut avoir des tables séparées qui correspondent à des propriétés sur un seul concept PublicSchema.

Approche : effectuez la correspondance des champs vers la bonne propriété PublicSchema quelle que soit l'entité sur laquelle ils se trouvent dans votre système. Les frontières des concepts dans PublicSchema sont sémantiques, pas des exigences structurelles.

### Différences temporelles

Votre système peut stocker un seul champ de statut là où PublicSchema attend un modèle borné dans le temps (start_date, end_date, status). Ou votre système peut avoir une table d'historique complète là où PublicSchema modélise un seul état courant.

Approche : décidez si vous effectuez la correspondance de l'état courant ou de l'historique complet. Pour l'état courant, effectuez la correspondance du dernier enregistrement. Pour l'historique, chaque ligne correspond à un enregistrement PublicSchema distinct avec sa propre plage de dates.

### Correspondances de valeurs un-à-plusieurs

Votre système utilise "inactive" pour des cas que PublicSchema divise en "suspended", "completed" et "exited".

Ce n'est pas seulement une difficulté de correspondance ; c'est un manque d'information. Lorsque vous effectuez la correspondance d'"inactive" vers un seul code, vous perdez la distinction entre quelqu'un dont les prestations sont temporairement suspendues et quelqu'un qui a définitivement quitté le programme. Les systèmes en aval qui consomment les données mises en correspondance ne peuvent pas récupérer la précision perdue.

Approche : si vous ne pouvez pas les distinguer à partir de vos données, effectuez la correspondance vers le code le plus large applicable et documentez l'ambiguïté. Si vous pouvez les distinguer (par exemple en examinant des champs connexes), ajoutez de la logique à la correspondance. Plus les systèmes adoptent directement des codes de vocabulaire partagés, moins ce problème se pose.

### Concepts manquants

Votre système a des entités que PublicSchema ne couvre pas, ou PublicSchema a des concepts que votre système n'implémente pas.

Approche : documentez la lacune. Pour vos entités supplémentaires, réfléchissez si elles pourraient être modélisées comme des extensions (consultez le [Mécanisme d'extension](/docs/extension-mechanism/)). Pour la couverture manquante, vous n'avez peut-être pas besoin de chaque concept.

## Téléchargements disponibles

**Par concept :**

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **CSV** | Propriétés avec types et définitions | Point de départ pour les tables de correspondance de champs |
| **Classeur Excel de définition** | Classeur multi-feuilles avec métadonnées, propriétés et vocabulaires référencés en FR/EN/ES | Comprendre un concept en détail, partager avec des parties prenantes non techniques |
| **Modèle Excel** | Classeur de saisie de données avec validation par liste déroulante | Collecte de données, prototypage, format intermédiaire canonique |
| **JSON-LD** | Concept en données liées | Accès lisible par machine, chaînes d'outils RDF |

**Par vocabulaire :**

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **CSV** | Codes avec libellés et définitions multilingues | Tables de correspondance de codes |
| **JSON-LD** | Vocabulaire en tant que SKOS ConceptScheme | Accès programmatique |

## Prochaines étapes

- Si vous avez seulement besoin d'aligner des codes de valeurs (pas des noms de champs), le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/) est un point de départ plus léger.
- Si vous concevez un nouveau système de zéro, consultez le [Guide de conception du modèle de données](/docs/data-model-guide/).
- Si vous souhaitez utiliser des contextes JSON-LD ou émettre des attestations vérifiables, consultez le [Guide JSON-LD et VC](/docs/jsonld-vc-guide/).
