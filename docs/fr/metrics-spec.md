# Spécification des indicateurs

**Statut :** Conception en brouillon, partiellement implémentée &middot; **Auteur :** groupe de travail PublicSchema &middot; **Statut de l'implémentation revu le :** 7 septembre 2026

## Implémentation actuelle

Le dépôt fournit le modèle de métriques LinkML dans `schema/metrics.yaml`, des sources de catalogue en brouillon dans `schema/metric_catalog/`, et une projection du catalogue pour le site générée par `just build` (ou par `just metrics-data` pour cette seule projection). Les catalogues versionnés contiennent actuellement 597 entrées en brouillon : 580 entrées DHS et 17 entrées de l'OIT. Seules trois entrées DHS comportent des blocs de calcul rédigés ; les autres entrées sont des amorces de métadonnées, et non des définitions d'indicateurs exécutables.

La compilation projette ces sources dans `dist/metrics_catalog.json` pour la navigation. Elle n'exécute pas de SQL, de VTL ni de CQL, n'établit pas l'exactitude des calculs et ne fournit pas de liaison CQL ModelInfo pour PublicSchema. La publication CSVW, SDMX et RDF Data Cube propre aux métriques constitue une cible de conception, et non des exports implémentés. Le pipeline ordinaire de RDF, de JSON Schema et de téléchargements du vocabulaire n'établit pas ces capacités de publication des métriques.

Les sections ci-dessous décrivent le modèle proposé et les exigences de conformité. Les règles relatives aux calculs exécutables, aux librairies par défaut, à l'acceptation par les agences et aux formats de publication sont des cibles de conception, sauf lorsqu'elles sont explicitement identifiées ci-dessus comme implémentées. L'exemple détaillé est illustratif ; ses URL de librairie et de schéma ne sont pas des artefacts dont la publication est promise. Les versions et dates de la feuille de route reflètent la proposition d'origine, et non un engagement de livraison.

Cette spécification propose un nouveau domaine au sein de PublicSchema pour des **définitions déclaratives et exécutables d'indicateurs dérivables** : des métriques agrégées calculées à partir des concepts de PublicSchema au niveau de l'enregistrement (Person, Household, Enrollment, PaymentEvent, ScoringEvent, etc.). Elle complète la couche existante au niveau de l'enregistrement ; elle ne la remplace pas.

**Cible de conception limitée aux indicateurs dérivables.** Une définition de métrique complète doit inclure un calcul portant sur des microdonnées mises en correspondance avec PS. Une amorce de catalogue dépourvue de ce calcul n'atteint pas encore cette cible. Les indicateurs sourcés (compilés à partir de tableaux amont d'INS ou d'agences, sans dérivation depuis des microdonnées) restent précieux mais sont hors du périmètre de ce document ; ils relèvent de la couche de provenance existante.

La forme est empruntée à FHIR R5 Measure (calcul) et à SDMX 3.0 (structure). PublicSchema est la source de vérité LinkML ; les formats en aval sont produits par des générateurs.

## Pourquoi PublicSchema en a besoin

PublicSchema couvre aujourd'hui les personnes, les ménages, les programmes, les paiements, les profils et les exécutions de notation : la forme, au niveau de l'enregistrement, des systèmes de protection sociale et des systèmes de prestation voisins. Les bailleurs de fonds, les statisticiens, les équipes de suivi-évaluation et les chercheurs en politiques publiques ne consomment pas ces données enregistrement par enregistrement ; ils consomment des **indicateurs** agrégés : taux de couverture, adéquation, régularité des paiements, fuites, taux d'erreur, prestation moyenne par bénéficiaire, part des femmes parmi les bénéficiaires.

Trois problèmes concrets de la situation actuelle :

1. **Chaque programme réinvente les mêmes indicateurs**, avec des dénominateurs subtilement différents. Une « couverture de la protection sociale » calculée sur un dénominateur d'inscriptions actives n'est pas comparable à une couverture calculée sur un dénominateur de population éligible. Sans définitions exécutables partagées, la comparaison entre pays est illusoire.
2. **Le même indicateur est reconditionné 4 à 6 fois** pour alimenter l'OIT ([ILOSTAT](https://ilostat.ilo.org/)), la Banque mondiale ([ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire)), Eurostat ([ESSPROS](https://ec.europa.eu/eurostat/web/social-protection)), l'OCDE ([SOCX](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html)), l'ONU ([ODD 1.3.1](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf)) et l'office statistique du pays lui-même. Chaque consommateur veut sa propre Data Structure Definition (DSD).
3. **On peut rarement répondre à la question « Comment cela a-t-il été calculé ? ».** La méthodologie se trouve dans un PDF, la formule dans un tableur, les tables de correspondance dans une liste de codes que personne ne versionne.

La primitive de métriques proposée vise à résoudre ces trois problèmes : une **définition exécutable canonique** par indicateur, des **URI d'alignement** qui acheminent une même observation vers de nombreuses DSD de consommateurs, et un **bloc de calcul déclaratif** auditable et réexécutable.

## Périmètre

**Dans le périmètre :**
- Définition déclarative d'indicateurs ou de métriques agrégés dérivables.
- Calcul déclaratif portant sur les concepts de PublicSchema au niveau de l'enregistrement.
- Métadonnées dimensionnelles (les désagrégations qu'une métrique prend en charge).
- Métadonnées de référence (définition, méthodologie, source, propriétaire, licence, version).
- Observations (les valeurs effectivement rapportées, avec les valeurs de dimension et les attributs au niveau de l'observation).
- Tables de correspondance vers des cadres d'indicateurs externes (DSD SDMX d'agences, ODD de l'ONU, ASPIRE, ESSPROS, SOCX, DHIS2, IATI, HXL).

**Hors périmètre :**
- **Indicateurs sourcés.** Si une « métrique » n'est qu'une citation d'une valeur compilée en amont par un INS ou une agence, sans dérivation au niveau des microdonnées, elle n'a pas sa place ici ; elle reste dans la couche de provenance que portent déjà les concepts de PS au niveau de l'enregistrement.
- Remplacer la notation par enregistrement. `ScoringEvent` continue d'enregistrer l'application d'une règle à un sujet ; les métriques agrègent sur de nombreux sujets.
- Remplacer l'outillage des agences statistiques. La couche de publication proposée décrit la métrique et émettrait du SDMX ; elle n'exploite ni les services web SDMX ni les registres des agences.
- Héberger des données brutes au niveau de l'enregistrement. Une définition de métrique référence les concepts au niveau de l'enregistrement par URI ; les observations ne portent que la valeur agrégée.
- Définir un nouvel environnement d'exécution de calcul. Le langage de critères est enfichable (identifié par type de média IANA) ; les intégrations proposées ciblent des moteurs SQL, VTL et CQL existants.
- Métriques d'évaluation de modèles d'IA ou d'apprentissage automatique. Sujet voisin qui mérite une spécification distincte ; il n'est pas intégré ici.

## Niveaux de conformité

Le modèle de conformité proposé définit trois niveaux. Il ne s'agit pas de certifications du catalogue ou de la compilation actuels :

| Niveau | Nom | Capacité |
|------|------|------------|
| **1** | Consommateur de catalogue | Lit les définitions de Metric de PS (LinkML / JSON Schema), résout les URI d'alignement. Aucune émission. |
| **2** | Éditeur d'observations | Émet du JSON-LD `MetricObservation` et du CSVW valides au regard des schémas PS. Le seuil minimal pour « cette plateforme parle PS Metrics ». |
| **3** | Éditeur lié à SDMX | Niveau 2, plus l'émission SDMX-CSV v2.1 conforme à une DSD référencée. Le seuil pour une publication de niveau agence vers l'OIT, la Banque mondiale, l'OCDE ou Eurostat. |

Le niveau 1 correspond à la plupart des outils de recherche en lecture seule. Le niveau 2 correspond aux plateformes de prestation (OpenSPP, OpenIMIS, bases de données de programmes DHIS2). Le niveau 3 correspond aux instituts nationaux de statistique et aux organismes dépositaires.

## Modèle conceptuel

Le modèle conceptuel comporte sept classes principales, avec des classes auxiliaires de calcul et de valeurs structurées en LinkML. Sa forme est celle du modèle d'information SDMX 3.0 (dimensions, mesures, attributs, listes de codes, observations), étendue avec la sémantique de calcul de FHIR Measure. La [séparation observation et notation](/docs/design-principles/#6-séparation-observation-et-notation) (Principe 6) s'étend de la notation par enregistrement aux métriques agrégées : une `MetricObservation` est à une `Metric` ce qu'un `ScoringEvent` est à une `ScoringRule`. Les métriques peuvent porter [`core: true`](/docs/design-principles/#9-core-and-extended-property-tiers) (Principe 9) pour marquer le sous-ensemble indispensable.

```text
                     +--------+
                     | Metric +--- family (slot, optional grouping)
                     +---+----+
                         | 1
                         | has
                         v
   +---------+    +------+------+   +------------+
   | Concept |<---+ Metric defs +-->| MetricCalc |
   | (skos)  |    +------+------+   +------------+
   +---------+           |
                         |
                         | declares
                         v
                  +------+------+      +------+------+
                  | MetricDim   |      | MetricAttr  |
                  +------+------+      +-------------+
                         ^
                         |  realises against
                         |
                  +------+------+         +------------+
                  | MetricObs   +-------->|   Period   |
                  +------+------+         +------------+
                         ^
                         | bundled in
                         |
                  +------+------+
                  | MetricRpt   |
                  +-------------+
```

### `Metric`

Un indicateur nommé, avec un URI stable, une définition en prose, un type de valeur, une unité, des dimensions déclarées, des attributs déclarés au niveau de l'observation, des alignements externes déclarés et un calcul (unique et primaire).

Slots principaux :
- `id` : identifiant opaque, fragment d'URI sous forme de slug.
- `class_uri` : `publicschema:Metric`. Correspondance RDF proposée : une `qb:MeasureProperty` et un `skos:Concept`.
- `title`, `description` : libellés multilingues portés dans `annotations.label_es` / `label_fr` / `description_es` / `description_fr` (convention maison de PS).
- `value_type` : vocabulaire contrôlé : `count`, `proportion`, `ratio`, `currency_amount`, `index`, `duration`, `nominal`, `ordinal`, `qualitative`.
- `unit` : UCUM, ISO 4217 (devise) ou `unitless`.
- `multiplier` : `0` / `3` / `6` au format SDMX (unités / milliers / millions). Valeur par défaut `0`.
- `decimals` : précision de rapport.
- `dimensions` : liste ordonnée de références `MetricDimension`.
- `attributes` : liste de références `MetricAttribute`.
- `calculation` : un `MetricCalculation` (voir [Modèle de calcul](#modèle-de-calcul)).
- `topic` : coverage / adequacy / expenditure / leakage / targeting / inclusion_error / exclusion_error / regularity / processing_time / satisfaction.
- `concept_uri` : URI `skos:Concept` (afin que plusieurs Metrics puissent partager un concept).
- `family` : étiquette URI optionnelle regroupant les métriques qui partagent des dimensions (elle pilote la génération de la DSD lorsqu'elle est présente ; pas de classe distincte). Une classe `MetricFamily` de premier rang est reportée jusqu'à ce qu'il existe trois familles réelles.
- `aligns_with` : liste d'URI externes.
- `core` : indicateur booléen pour le sous-ensemble indispensable.
- `status` : `bibo:draft` / `bibo:published` / `bibo:deprecated`.
- `version`, `replaces`, `replaced_by` : slots de versionnement, introduits dans ce domaine ; à remonter dans `schema/common.yaml` si d'autres concepts porteurs d'enregistrements les adoptent.

`Metric` est une définition de catalogue, et non un événement dans le temps ; elle n'est donc pas une sous-classe d'`Event`.

### `MetricDimension`

Une dimension typée qui désagrège une métrique. Slots :
- `id`, `title`, `description` (+ multilingue).
- `class_uri` : `publicschema:MetricDimension` ; correspondance RDF proposée : `qb:DimensionProperty`.
- `concept_uri` : concept transversal SDMX lorsqu'il en existe un (`REF_AREA`, `SEX`, `AGE`, `UNIT_MEASURE`, `TIME_PERIOD`, `FREQ`). Référencé par URN dans la prose ; aucun IRI RDF `sdmx:` fictif.
- `range` : enum LinkML (vocabulaire PublicSchema) ou URI d'une liste de codes externe.
- `code_list_uri` : URN canonique de la liste de codes (liste de codes d'agence SDMX lorsqu'il en existe une). Les vocabulaires PS sont canoniques ; l'émetteur SDMX les enveloppe.
- `is_required` : booléen.
- `ordering` : entier (position dans la DSD).

La librairie initiale proposée de MetricDimensions comprend : pays (ISO 3166-1 alpha-2 lié à `CL_AREA`), région / admin1 (OCHA COD-AB), sexe (vocabulaire de sexe PS lié à `CL_SEX(2.1)`), âge (année unique et tranches standard, lié à `CL_AGE`), urbain / rural, quintile de richesse, situation de handicap (WG-SS), type de programme (taxonomie des programmes PS), modalité de prestation, période de référence, fréquence (`FREQ`).

### `MetricAttribute`

Une annotation non-clé sur une observation, une série ou un jeu de données. La librairie par défaut proposée reflète les [concepts transversaux SDMX](https://sdmx.org/sdmx_cdcl/) afin de préparer un futur émetteur SDMX. Identifiants par défaut et **niveaux de rattachement corrects** (modèle d'information SDMX 3.0) :

- **Niveau de l'observation :** `OBS_STATUS` (liste de codes `CL_OBS_STATUS(2.3)`), `CONF_STATUS` (`CL_CONF_STATUS(1.4)`), `COMMENT_OBS`, plus les extensions PS `cell_count`, `confidentiality_status`, `data_quality_flag`.
- **Niveau de la série / groupe de dimensions :** `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `REF_PERIOD`, `BASE_PER`, `EMBARGO_DATE`, `COMMENT_TS`.
- **Niveau du jeu de données :** `COMPILING_ORG`, `SOURCE_AGENCY`, `TITLE`, `TITLE_COMPL`, `CURRENCY`, `CURRENCY_DENOM`, `PRICE_BASE`. (`DATA_PROVIDER` se trouve dans l'en-tête du Dataset SDMX, et non sous forme d'attribut.)
- **Traitement des ruptures de série :** `OBS_PRE_BREAK`, `BREAK_REASON` (`CL_BREAK_REASON`).

Remarques :
- `OBS_VALUE` est le composant de mesure SDMX 3.0 (et non un attribut) ; il est porté par `MetricObservation.value`.
- `TIME_FORMAT` est déprécié dans SDMX 3.0 (ISO 8601 est présumé) et ne figure pas dans la librairie par défaut.
- Lié à `qb:AttributeProperty` lors de l'émission RDF. Le slot `attachment_level` (`dataset` / `series` / `observation`) détermine où l'émetteur SDMX place chaque attribut.

Le périmètre de fondation proposé retient six attributs par défaut rédigés par PS : `OBS_STATUS`, `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `cell_count`, `confidentiality_status`. Les autres attributs sont reportés jusqu'à ce qu'un cas d'utilisation concret en ait besoin.

### `MetricCalculation`

Le calcul déclaratif. Voir [Modèle de calcul](#modèle-de-calcul). Un par Metric ; les variantes plus riches sont portées par une référence de librairie. L'analogue au niveau de l'enregistrement est [`ScoringRule`](/ScoringRule/) (`schema/misc.yaml`) ; `MetricCalculation` agrège à travers les sujets.

### `MetricObservation`

Une valeur rapportée. Slots :
- `metric` : URI de la `Metric`.
- `period` : une `Period`.
- `dimension_values` : liste ordonnée de paires `{dimension_uri, code}` (pas une map ; l'ordre importe pour l'aller-retour de la DSD).
- `value` : nombre, dont le type correspond au `value_type` de la métrique. L'**échelle est fixée par `Metric.unit` + `Metric.multiplier`** : pour `value_type: proportion` avec `unit: unitless`, la valeur est comprise entre 0 et 1 (0..1) ; pour les pourcentages, définissez `unit: PT` (code SDMX `UNIT_MEASURE`) et la valeur est comprise entre 0 et 100 (0..100). Lorsque `UNIT_MEASURE` apparaît également dans `attribute_values`, il doit être égal à `Metric.unit` ; l'observation ne peut pas remplacer l'échelle.
- `attribute_values` : map associant un URI de `MetricAttribute` à une valeur.
- `calculation_uri` : URI de la définition `MetricCalculation` que cette observation réalise.
- `execution_uri` : URI optionnel d'un enregistrement d'exécution (provenance : agent logiciel, horodatage de l'exécution, jeu de paramètres). Un alignement léger sur PROV-O est recommandé ; les détails sont reportés.

Lié à `qb:Observation` et à l'Observation SDMX 3.0. `MetricObservation` est `is_a: Event` ([Principe 5](/docs/design-principles/#5-supertypes-abstraits)) ; elle hérite des `identifiers` d'`Event`.

### `MetricReport`

Un ensemble d'observations avec des métadonnées d'éditeur : `publisher` (dont la plage est [`Agent`](/docs/design-principles/#5-supertypes-abstraits)), `published_at`, `reference_date`, `methodology_uri`, `license`, `contact_uri`, `observations[]`, `dsd_uri`. Lié à `qb:DataSet`.

### `Period`

La couverture temporelle d'une MetricObservation. PS réifie la période (plutôt que de porter `start_date` / `end_date` en ligne comme les autres sous-types d'`Event`) parce que l'émetteur SDMX / Data Cube a besoin d'un intervalle unique adressable par URI pour satisfaire la [contrainte d'intégrité IC-11 du W3C Data Cube](https://www.w3.org/TR/vocab-data-cube/#wf). Slots : `period_type` (`point_in_time` / `span` / `cohort` / `fiscal_year` / `calendar_year`), `start_date`, `end_date`, `granularity` (year / quarter / month / day), `reference_period_type`, `frequency` (valeur de la liste de codes `FREQ` : A / Q / M / D / W / H). `end_date` est le dernier jour couvert, comme partout dans PublicSchema ([ADR-027](../../decisions/027-end-date-boundary.md)) : l'année civile 2024 va du `2024-01-01` au `2024-12-31`, de la même manière que l'exprime une `Period` FHIR ou une couverture temporelle DCAT.

## Modèle de calcul

Emprunté à [FHIR R5 Measure](https://hl7.org/fhir/R5/measure.html) et transposé aux URI de slots PS. FHIR Measure est la seule norme dont l'adoption atteint un niveau réglementaire (eCQM des CMS, mesures numériques HEDIS du NCQA) pour « calculer un indicateur agrégé à partir de données hétérogènes au niveau de l'enregistrement, avec des définitions auditables et une provenance réexécutable ». Nous empruntons la forme ; nous ne dépendons pas des types FHIR.

### Forme de `MetricCalculation`

```yaml
calculation:
  scoring: proportion | ratio | continuous-variable | cohort
  subject_class: <PS class URI>   # e.g., publicschema:Person, publicschema:Enrollment
  populations:
    - type: initial-population
      language: application/sql | application/vtl | text/cql
      criteria: <expression string OR @ref to library>
    - type: denominator
      language: ...
      criteria: ...
    - type: denominator-exclusion
      language: ...
      criteria: ...
    - type: numerator
      language: ...
      criteria: ...
    # optional: numerator-exclusion, denominator-exception,
    # measure-population, measure-population-exclusion, measure-observation
  stratifiers:
    - code: by-sex
      language: ...
      criteria: ...
      components:
        - code: by-sex-and-age
          language: ...
          criteria: ...
  rate_aggregation: average | sum | none
  improvement_notation: increase | decrease | policy_dependent
  libraries:
    - https://publicschema.org/metrics/library/sp-coverage-cql-1.0
```

`subject_class` diverge du `subject[x]` de FHIR Measure (qui est `CodeableConcept | Reference(Group)`) : les sujets PS sont des URI de classes PS. `improvement_notation` accepte `policy_dependent` pour les métriques non cliniques dont le sens souhaitable dépend du cadrage des politiques publiques (par exemple, le ratio dépenses / PIB).

### Types de population et validité de la notation

Les neuf populations de FHIR Measure et leur applicabilité à chaque méthode de notation :

| Type | Objet |
|------|---------|
| `initial-population` | L'univers des enregistrements que la métrique considère. |
| `denominator` | Sous-ensemble d'initial-population qui entre dans le dénominateur. |
| `denominator-exclusion` | Enregistrements retirés du dénominateur. |
| `denominator-exception` | Enregistrements comptés dans le dénominateur mais exemptés du numérateur. |
| `numerator` | Sous-ensemble du dénominateur qui remplit la condition de réussite. |
| `numerator-exclusion` | Enregistrements retirés du numérateur. |
| `measure-population` | Enregistrements dont l'observation par enregistrement est agrégée. |
| `measure-population-exclusion` | Enregistrements retirés de `measure-population`. |
| `measure-observation` | La valeur calculée par enregistrement dans `measure-population`. |

| Méthode de notation | Populations requises |
|---------|----------------------|
| `proportion` | initial-population, denominator, numerator (plus exclusions / exception optionnelles) |
| `ratio` | initial-population, denominator, numerator (indépendant du dénominateur) |
| `continuous-variable` | initial-population, measure-population, measure-observation (plus measure-population-exclusion optionnelle) |
| `cohort` | initial-population uniquement |

La validation de calcul proposée doit vérifier `populations[*].type` au regard de la valeur `scoring` de la métrique. Le projecteur de catalogue actuel n'effectue pas cette validation sémantique.

### Langage de critères

Chaque champ `criteria` est associé à un type de média IANA `language`. PublicSchema ne désigne pas de gagnant ; il fixe le type de média pour que les consommateurs sachent quel moteur invoquer. **Trois langages sont proposés :**

1. **`application/sql`** : lié à l'entrepôt de données ; le choix par défaut pragmatique pour les implémenteurs de plateformes de prestation. Convention : des marqueurs `${ps.Enrollment}` pour les références de classe, résolus par l'exécuteur. Devrait couvrir environ 80 % des métriques de la v0.1.
2. **`application/vtl`** : le [Validation and Transformation Language](https://github.com/sdmx-twg/vtl) du SDMX-TWG (v2.1, 11 avril 2025). Le choix naturel pour les agrégations liées à SDMX, les correspondances de listes de codes, les consolidations hiérarchiques et l'arithmétique des périodes. Pour les métriques dont les consommateurs cibles sont des agences SDMX, VTL est recommandé. Réalité des moteurs : **un seul moteur actif** ([`vpinna80/VTL` de la Banca d'Italia](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). Voir [Risques](#risques).
3. **`text/cql`** : le Clinical Quality Language de HL7 ([spécification v1.5.3](https://cql.hl7.org/), adopté par les CMS et HEDIS). Recommandé pour les métriques qui recoupent le domaine clinique ou la qualité des soins (couverture effective de la CSU, vaccination, SMNI). Un XML **ModelInfo** CQL proposé lierait CQL aux classes PS, en ciblant le **[moteur de référence HL7 `cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language)** (Apache-2.0, v4.8.0).

FHIRPath est trop limité pour l'agrégation au niveau des ensembles et n'est pas de premier rang. Les auteurs qui souhaitent exprimer un stratificateur en FHIRPath peuvent le faire avec `language: text/fhirpath`, mais PS ne livre ni sous-ensemble normatif ni banc de test.

### Résolution des librairies

`criteria: @ref:LibraryName.Symbol` se résout en `<library_uri>#<Symbol>`, où `library_uri` figure dans la liste `calculation.libraries[]` de la métrique. Les librairies sont déréférençables par HTTPS ; leur contenu est le texte du langage déclaré par `language` (un fichier CQL, un fichier VTL, un fichier SQL). Les URI de librairies portent une étiquette de version ; PS recommande des URI adressés par contenu (par exemple, `.../sp-coverage-cql-1.0`) afin que le calcul d'une métrique reste identique au bit près d'une publication à l'autre.

Reflète la référence `Measure.library = canonical(Library)` de FHIR Measure.

## URI d'alignement

`aligns_with` sur `Metric`, `MetricDimension` et `MetricAttribute` porte des URI externes qui acheminent un même artefact PublicSchema vers le bon pipeline de consommateur. **C'est le mécanisme de déduplication** : une définition de Metric PS, de nombreux alias d'agences. C'est l'enjeu politique de toute la spécification.

| Cible | Modèle d'URI | Propriétaire |
|--------|-------------|-------|
| DSD SDMX d'agence | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)` (structure d'URN issue du [SDMX-IM](https://github.com/sdmx-twg/sdmx-im)) | SDMX TWG, émis par l'agence |
| Concept transversal SDMX | `urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=SDMX:CROSS_DOMAIN_CONCEPTS(2.0).REF_AREA` (vérifier la version sur [registry.sdmx.org](https://registry.sdmx.org)) | SDMX TWG |
| Mesure SDMX (SDMX 3.0) | `urn:sdmx:org.sdmx.infomodel.datastructure.Measure=<Agency>:<DSD>(<Version>).<Code>` | SDMX TWG |
| Indicateur ODD de l'ONU | `https://unstats.un.org/sdgs/indicators/series/<SERIES_CODE>` | Division de statistique de l'ONU |
| DSD mondiale des ODD de l'ONU | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=IAEG-SDGs:SDG(1.0)` (vérifier l'identifiant exact de l'agence sur [unstats.un.org/sdgs/sdmx](https://unstats.un.org/sdgs/sdmx)) | Division de statistique de l'ONU |
| Famille ASPIRE | `https://datacatalog.worldbank.org/aspire/<family-code>` (modèle provisoire ; la forme d'URL de l'agence peut changer) | Banque mondiale |
| Métadonnées de référence ESSPROS | `https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm` | Eurostat |
| DSD SOCX de l'OCDE | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=OECD.ELS.SPD:DSD_SOCX_AGG(1.0)` (en service, vérifiée sur `sdmx.oecd.org`) | OCDE |
| Indicateur DHIS2 | `dhis2://indicator/<uid>` (local au programme) | Instance DHIS2 locale |
| Résultat / indicateur IATI | `https://iatistandard.org/en/iati-standard/203/codelists/IndicatorMeasure/` | IATI |
| Hashtag HXL | `https://hxlstandard.org/standard/hashtags/#indicator+value+num` | HXL |
| Mesure RDF Data Cube | `<publicschema metric URI>` rendu comme `qb:MeasureProperty` | lui-même |

L'alignement est sémantique et à sens unique ; PublicSchema ne se synchronise pas avec ces registres. Une modification de la DSD de l'OIT exige une nouvelle version du schéma PS qui met à jour l'URI d'alignement.

**Pointeur retour d'une DSD d'agence vers une Metric PS.** SDMX n'a pas de référence native entre systèmes. Utilisez le mécanisme `Annotation` du SDMX-IM sur la DSD de l'agence : `AnnotationType = ps:alignedMetric`, `AnnotationURL = <PS Metric URI>`. Cette approche est normativement correcte et fait l'aller-retour sans perte. Dans SDMX 3.0, « extends » désigne un héritage interne à la DSD, et non un alignement externe ; le mécanisme d'Annotation est donc la seule voie valide.

## Cibles d'émission

LinkML est la source de vérité. Ce tableau recense les sorties propres aux métriques proposées et les bases d'implémentation possibles. La disponibilité d'un générateur LinkML ou du `rdf_export.py` existant ne signifie pas que l'éditeur de métriques correspondant a été intégré ou vérifié dans ce dépôt.

| Sortie | Pourquoi | Statut | Priorité |
|--------|-----|--------|----------|
| **JSON Schema** (par Metric, MetricObservation, MetricReport) | Format de consommation par défaut ; producteurs de données tabulaires ; intégration OpenAPI. | Publication propre aux métriques en attente ; `gen-jsonschema` de LinkML est une base possible | P0 |
| **Contexte JSON-LD** | Modèle PS existant. | Publication propre aux métriques en attente ; `gen-jsonld-context` de LinkML est une base possible | P0 |
| **Formes SHACL** | Validation ; modèle PS existant. | Publication propre aux métriques en attente ; `gen-shacl` de LinkML est une base possible | P0 |
| **CSVW** (CSV on the Web, métadonnées JSON-LD) | Publication tabulaire la plus simple ; seuil minimal pour la soumission par les analystes. | **À construire** ([linkml/linkml#86](https://github.com/linkml/linkml/issues/86) ouvert depuis novembre 2020, aucune PR) | P0 |
| **SDMX-CSV v2.1** | Seuil minimal pour les analystes de données de la Banque mondiale, de l'OIT, de l'OCDE et d'Eurostat. Spécification : [sdmx-twg/sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) (v2.1.0, 27 août 2025). | **À construire** (pas de `gen-sdmx` LinkML ; aucun convertisseur tiers) | P0 |
| **SDMX-ML v3.1 (messages structurels)** | Soumissions de DSD / Codelist / ConceptScheme aux registres des agences. Spécification : [sdmx-twg/sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) (v3.1.0, 16 mai 2025). | **À construire** | P0 |
| **SDMX-ML v3.1 (messages de données)** | Échange complet de structures et de données. | **À construire** | P1 |
| **SDMX-JSON v2.1** | Format web de diffusion ; les API des agences (OCDE, BCE, OIT) répondent en JSON par défaut. Spécification : [sdmx-twg/sdmx-json](https://github.com/sdmx-twg/sdmx-json) (v2.1.0, 16 mai 2025). | **À construire** | P1 |
| **RDF Data Cube TTL** | Consommateurs natifs des graphes ; pipelines LOD ; requêtes SPARQL. | **À construire** (environ 200 lignes de code ; PS en est directement responsable) | P2 |
| **Excel** (par définition de Metric) | Classeur de définition, aligné sur les téléchargements Excel par concept existants de PS. | Classeurs de définition de métriques en attente ; le pipeline existant exporte les concepts du vocabulaire | P2 |
| **JSON d'indicateur DHIS2** | Import direct dans les instances DHIS2. Avec perte : dépend de la résolution locale des UID. | **À construire** ; aucune table de correspondance publique n'existe | P3 |
| **Suggestion de hashtags HXL** | En-tête de hashtags en ligne pour les exports CSV. Au mieux. | **À construire** | P3 |
| **Fragment XML d'indicateur IATI** | Pour l'intégration des résultats rapportés par les bailleurs. | **À construire** | P3 |

SDMX 3.0 fait de `Measure` une liste de composants de premier rang (il a supprimé la `MeasureDimension` de SDMX 2.1). PS cible uniquement la 3.0 ; l'aller-retour vers les consommateurs de l'ancienne version 2.1 est hors périmètre. Composition de l'URN de DSD : `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)`. SDMX 3.0 autorise un semver étendu selon [sdmx-twg/semver](https://github.com/sdmx-twg/semver). PublicSchema ne crée pas d'URN d'agence ; une agence qui réutilise une métrique PS crée son propre URN et renvoie vers la métrique par une `Annotation` (voir [URI d'alignement](#uri-dalignement)).

Il n'existe pas d'espace de noms RDF `sdmx:` canonique publié par le SDMX-TWG. Le schéma ne liste que `qb:` dans `exact_mappings`, avec les références d'URN SDMX dans la prose. L'émetteur Data Cube TTL proposé devrait faire respecter : IC-1, IC-2, IC-3, IC-4, IC-5, IC-6, IC-11, IC-13, IC-14. IC-7 à IC-10 (tranches) ne s'appliquent pas dans la v0.1 ; la v0.2 pourra ajouter la génération de tranches si un consommateur le demande. IC-12 (pas de tuples de dimensions en double) exigerait aussi une validation au moment de l'émission ; cette validation n'est pas implémentée par le projecteur de catalogue.

## Corpus d'amorçage

La proposition d'origine visait **environ 240 indicateurs dérivables issus de la Banque mondiale, de l'OIT, de l'ONU et de l'UNICEF**, chacun doté d'un `MetricCalculation` exécutable et des URI `aligns_with` pertinents. Les estimations ci-dessous constituent un carnet de recherche, et non le corpus actuellement implémenté ; voir [Implémentation actuelle](#implémentation-actuelle).

| Source | Indicateurs dérivables (ordre de grandeur) | Entrée lisible par machine |
|--------|-----------------------------------|------------------------|
| **ODD de l'ONU** (métadonnées publiées par les organismes dépositaires) | ~30 (1.1.1, 1.2.1, l'ensemble 1.3.1, 3.8.x CSU, 5.2&ndash;5.6, 10.1.1, 16.9.1) | [metadata.un.org/sdg/ontology](https://metadata.un.org/sdg/ontology) + PDF par indicateur |
| **OIT** (organisme dépositaire de 14 indicateurs ODD ; séries SPSI) | ~50 (couverture, adéquation, couverture effective par type de programme) | [ILOSTAT SDMX](https://ilostat.ilo.org/resources/sdmx-tools/) + CSV en masse |
| **ASPIRE de la Banque mondiale** | ~100 (couverture, adéquation, incidence des prestations, réduction de la pauvreté, par quintile) | [API Indicators de la Banque mondiale](https://api.worldbank.org/v2/indicator?format=json) + méthodologie ASPIRE Quality Check |
| **Poverty &amp; Inequality Platform de la Banque mondiale** | ~20 (taux de pauvreté extrême / nationale, écart, sévérité, Gini, croissance des 40 % les plus pauvres) | [API PIP](https://pip.worldbank.org/) |
| **Indicateurs dérivés des MICS de l'UNICEF** | ~40 (bien-être de l'enfant, WASH, éducation) | Rapports MICS + dictionnaire des indicateurs |

**Estimation initiale du corpus : environ 240 indicateurs.** La v0.2 s'étend aux indicateurs dérivables de l'OCDE IDD / SOCX et d'EU-SILC d'Eurostat. La v0.3 s'élargit aux indicateurs humanitaires (au format HXL) et de gestion de programme (fuites, délai de traitement) qui n'ont pas d'organisme dépositaire interinstitutions unique.

Voie d'ingestion pratique : extraire le catalogue d'indicateurs lisible par machine de chaque source, générer automatiquement un squelette `Metric` par indicateur (titre, description, URL source, thématique), puis rédiger à la main le `MetricCalculation` par rapport aux classes PS pour le sous-ensemble dérivable. Les indicateurs uniquement sourcés (l'essentiel de la macroéconomie des WDI) sont écartés de cet exercice ; ils restent des citations valides, mais pas des Metrics PS.

## Processus de revue par les organismes dépositaires

La proposition maintiendrait une métrique à `bibo:draft` jusqu'à la revue par l'organisme dépositaire, une transition de statut ultérieure enregistrant cette revue. Les amorces actuelles sont toutes en brouillon ; l'inclusion dans le catalogue n'implique aucune approbation par une agence. Acheminement proposé vers les organismes dépositaires, par domaine :

- Couverture / adéquation de la protection sociale &rarr; OIT (organisme dépositaire de l'ODD 1.3.1).
- Pauvreté / inégalités &rarr; Banque mondiale (PIP / ASPIRE ; ODD 1.1.1 / 1.2.1).
- Bien-être / nutrition de l'enfant &rarr; UNICEF (MICS).
- Santé / CSU &rarr; OMS (ODD 3.8.x).
- Enregistrement des faits d'état civil / identité juridique &rarr; UNICEF / HCR / DAES (ODD 16.9.1).
- Égalité des genres &rarr; ONU Femmes / UNSD (ODD 5.x).

La validation par l'organisme dépositaire est un contrat social, et non un contrôle technique ; PS ne contrôle pas l'espace de noms. La transition `bibo:draft` &rarr; `bibo:published` signale, métrique par métrique, une revue par l'organisme dépositaire. Les URI de Metrics PS validées par l'organisme dépositaire deviennent citables dans les propres métadonnées de celui-ci.

## Exemple détaillé : couverture de l'ODD 1.3.1

Indicateur : *« Proportion de la population couverte par des socles ou systèmes de protection sociale »*, organisme dépositaire OIT, ODD 1.3.1a (couverture effective).

Définition PublicSchema (conceptuelle) :

```yaml
metric:
  id: sp_coverage_at_least_one_program
  title: Coverage by at least one social-protection program
  description: |
    Share of the resident population effectively covered by at least one
    social-protection cash benefit during the reference period, regardless
    of program type.
  value_type: proportion
  unit: PT                          # SDMX UNIT_MEASURE "Percentage", value in 0..100
  decimals: 1
  topic: coverage
  concept_uri: publicschema:concept/effective_coverage
  family: publicschema:metric_family/sp_coverage    # tag; drives DSD generation
  dimensions:
    - ps:dim/ref_area
    - ps:dim/time_period
    - ps:dim/freq
    - ps:dim/sex
    - ps:dim/age_band
    - ps:dim/urban_rural
    - ps:dim/wealth_quintile
  attributes:
    - ps:attr/unit_measure
    - ps:attr/obs_status
    - ps:attr/cell_count
    - ps:attr/confidentiality_status
  calculation:
    scoring: proportion
    subject_class: publicschema:Person
    populations:
      - type: initial-population
        language: text/cql
        criteria: "@ref:sp_coverage_lib.ResidentPopulation"
      - type: denominator
        language: text/cql
        criteria: "@ref:sp_coverage_lib.ResidentPopulation"
      - type: numerator
        language: text/cql
        criteria: "@ref:sp_coverage_lib.CoveredByAtLeastOneProgram"
    stratifiers:
      - code: by-sex
        language: application/sql
        criteria: "SELECT sex FROM ${ps.Person}"
      - code: by-age-band
        language: application/sql
        criteria: "SELECT age_band FROM ${ps.Person}"
    rate_aggregation: none
    improvement_notation: increase
    libraries:
      - https://publicschema.org/metrics/library/sp-coverage-cql-1.0
  aligns_with:
    - https://unstats.un.org/sdgs/indicators/series/SI_COV_BENFTS
    - urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=IAEG-SDGs:SDG(1.0)
    - https://datacatalog.worldbank.org/aspire/coverage   # placeholder; verify against live ASPIRE registry
  core: true
  status: bibo:draft
  version: 1.0.0
```

Exemple d'observation :

```yaml
observation:
  metric: publicschema:metric/sp_coverage_at_least_one_program
  period:
    period_type: calendar_year
    start_date: 2024-01-01
    end_date: 2024-12-31
    granularity: year
    frequency: A
  dimension_values:
    - { dimension_uri: ps:dim/ref_area, code: "TH" }       # Thailand
    - { dimension_uri: ps:dim/time_period, code: "2024" }
    - { dimension_uri: ps:dim/freq, code: "A" }
    - { dimension_uri: ps:dim/sex, code: "_T" }            # Total
    - { dimension_uri: ps:dim/age_band, code: "_T" }
    - { dimension_uri: ps:dim/urban_rural, code: "_T" }
    - { dimension_uri: ps:dim/wealth_quintile, code: "_T" }
  value: 68.3
  attribute_values:
    ps:attr/unit_measure: "PT"
    ps:attr/obs_status: "A"
    ps:attr/cell_count: 4982104
    ps:attr/confidentiality_status: "F"
  calculation_uri: publicschema:metric/sp_coverage_at_least_one_program#calculation
  # execution_uri optional
```

Le résultat visé est de réutiliser une même observation dans les formats destinés aux agences, aux graphes et aux tableaux de bord. Cet exemple ne démontre pas ces intégrations : les émetteurs, l'exécution des calculs, les liaisons aux DSD cibles et la validation par les consommateurs restent nécessaires. Les URI d'alignement à eux seuls n'établissent pas une acceptation par ILOSTAT ou ASPIRE.

Pour les praticiens moins familiers du vocabulaire de FHIR Measure : `initial-population` est « l'univers des enregistrements considérés » (toutes les personnes inscrites au registre de la population résidente) ; `denominator` est « ceux *dont* nous mesurons la couverture » (identique à initial-population pour le 1.3.1a) ; `numerator` est « ceux que nous déclarons *être* couverts » (les personnes ayant au moins une inscription active à un programme de protection sociale au cours de 2024) ; `denominator-exclusion` retire les enregistrements comptés par erreur (non-résidents) ; `numerator-exclusion` retire les enregistrements comptés à tort comme couverts (inscriptions frauduleuses ou en double).

## Schéma LinkML

La source normative est [`schema/metrics.yaml`](https://github.com/PublicSchema/publicschema.org/blob/main/schema/metrics.yaml), rattaché au schéma composite par l'entrée `metrics` de `schema/publicschema.yaml`. Il comprend onze classes (`Metric`, `MetricDimension`, `MetricAttribute`, `MetricCalculation`, `PopulationCriterion`, `Stratifier`, `MetricObservation`, `MetricReport`, `Period`, plus les classes auxiliaires de paires structurées `DimensionValue` et `AttributeValue`), les slots qu'elles référencent et les enums (`ValueType`, `ScoringMethod`, `ImprovementNotation`, `RateAggregation`, `MetricTopic`, `AttachmentLevel`, `PopulationType`, `PeriodType`, `Granularity`, `Frequency`). Les codes `ObsStatus` ne sont pas republiés ; ils se résolvent via l'URN SDMX `urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_OBS_STATUS(2.3)`.

Deux ajustements liés aux mots-clés LinkML méritent d'être signalés aux lecteurs :

- `MetricDimension.range` et `MetricAttribute.range` (les noms utilisés dans la prose de la spécification) s'écrivent `value_range` dans le fichier LinkML pour éviter de masquer le mot-clé `range`. La correspondance RDF proposée propre aux métriques utiliserait le `range` voulu ; la projection du catalogue n'effectue pas cette correspondance.
- `MetricObservation.value` s'écrit `metric_value` pour éviter une collision avec les slots `value` définis ailleurs dans le composite. Le JSON Schema illustratif ci-dessous utilise `value` ; ne présumez pas que l'exportateur de schéma général actuel effectue ce renommage.

`MetricObservation` est `is_a: Event`. `MetricReport.publisher` a pour plage `Agent` (voir [Principe 5](/docs/design-principles/#5-supertypes-abstraits)). `dimension_values` et `attribute_values` sont modélisés comme des listes ordonnées de paires structurées (`DimensionValue` et `AttributeValue`) plutôt que comme des maps, afin que l'aller-retour de la DSD SDMX soit stable.

## JSON Schema (en ligne)

La proposition prévoit `metric.schema.json`, `metric-observation.schema.json` et `metric-report.schema.json` à des URI de publication stables. Ces artefacts rédigés à la main et propres aux métriques ne sont pas fournis actuellement. Le schéma ci-dessous est indicatif et ne constitue pas un contrat publié ; en particulier, sa map d'attributs diffère de la liste de paires structurées du modèle LinkML actuel.

Schéma `MetricObservation` indicatif (Draft 2020-12) :

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://publicschema.org/schemas/v1/metric-observation.schema.json",
  "title": "MetricObservation",
  "type": "object",
  "required": ["metric", "period", "dimension_values", "value", "calculation_uri"],
  "properties": {
    "metric": { "type": "string", "format": "uri" },
    "period": { "$ref": "period.schema.json" },
    "dimension_values": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["dimension_uri", "code"],
        "properties": {
          "dimension_uri": { "type": "string", "format": "uri" },
          "code": { "type": "string" }
        }
      }
    },
    "value": { "type": "number" },
    "attribute_values": {
      "type": "object",
      "additionalProperties": { "type": ["string", "number", "boolean"] }
    },
    "calculation_uri": { "type": "string", "format": "uri" },
    "execution_uri": { "type": "string", "format": "uri" }
  }
}
```

## Questions ouvertes

Ces questions restent ouvertes après la passe de conception de la v0.1.

1. **Hiérarchies et schémas de catégories pour les dimensions.** Les dimensions SDMX portent des hiérarchies (M49 pour REF_AREA, hiérarchies de tranches d'âge pour AGE). La conception initiale prévoit des listes de codes plates ; la v0.2 ajoute les hiérarchies lorsqu'un consommateur d'émission l'exige.
2. **Content Constraints.** Les agences attachent des artefacts `ContentConstraint` indiquant « pour ce dataflow, REF_AREA est limité à ces codes ». La conception initiale propose des DSD sans contraintes ; la v0.2 pourra ajouter une forme `MetricConstraint` si l'émission vers les agences l'exige.
3. **Notation de cohorte.** La rétention de cohorte (couverture à 12 mois compte tenu d'une inscription au mois 0) nécessite une arithmétique de décalage de Period et une filiation dans le temps. Exclue du périmètre de la v0.1 ; à réexaminer dans la v0.2.
4. **Confidentialité / suppression des petites cellules.** Le mode de défaillance le plus courant dans la publication d'indicateurs publics. `cell_count` et `confidentiality_status` figurent dans la librairie `MetricAttribute` par défaut ; les agences fixent les seuils au moment de l'émission. La *logique* de suppression est propre à chaque agence et n'est pas normative.
5. **Métriques de modèles d'IA ou d'apprentissage automatique.** Hors du périmètre de cette spécification ; à réexaminer lorsque la taxonomie de l'AI Hub se stabilisera.
6. **Métriques à mesures multiples.** SDMX 3.0 autorise plusieurs Measures par DSD ; la conception initiale de PS ne cible que la publication à mesure unique. Ajouter une classe `MetricMeasure` dans la v0.2 si un cas d'utilisation réel se présente.

## Risques

Inventaire franc des dépendances et des lacunes de la spécification. Aucune n'est rédhibitoire ; chacune peut être construite.

1. **Monoculture de l'outillage VTL.** VTL est recommandé pour les métriques liées à SDMX, mais **un seul** moteur open source est actif ([`vpinna80/VTL` de la Banca d'Italia](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). Le moteur VTL d'Eurostat est abandonné depuis 2020. Atténuation : VTL n'est **jamais le seul langage du calcul primaire d'une métrique**. Les auteurs doivent livrer au moins l'un des langages {SQL, CQL} en plus de tout critère VTL, et l'émetteur SDMX doit accepter des équivalents traduits en SQL.
2. **Charge de nouveaux générateurs.** LinkML en amont dispose de `gen-jsonschema`, `gen-shacl` et `gen-jsonld-context`. Il ne dispose **pas** de `gen-csvw`, `gen-sdmx` ni `gen-datacube`. La proposition estimait à environ 1 500 lignes de code les générateurs dans `build/` pour la phase de fondation (CSVW, SDMX-CSV, messages structurels SDMX-ML, RDF Data Cube TTL). Le tableau des cibles d'émission marque chacun comme `existing` ou `to-build`. La contribution de `gen-csvw` en amont à LinkML figure dans la feuille de route de la v0.2.
3. **Un ModelInfo CQL non FHIR est rare en production.** CQL, en tant que *langage*, prend en charge un XML ModelInfo personnalisé ; les *moteurs* CQL sont pour la plupart livrés avec des liaisons FHIR uniquement. Le moteur de référence HL7 [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language) (Apache-2.0, v4.8.0) accepte un ModelInfo personnalisé. La proposition prévoit `PublicSchema-ModelInfo.xml`, conforme au schéma ModelInfo du moteur de référence HL7, dans la v0.2 ; prévoir une semaine avec un spécialiste de CQL.
4. **L'émetteur DHIS2 part de zéro.** Il n'existe aucune table de correspondance publique des définitions d'indicateurs externes vers DHIS2. Le schéma cible DHIS2 est stable ; la table de correspondance relève du travail de PS. Reporté à la v0.3.
5. **La boîte à outils HXL a un facteur bus de 1.** [`HXLStandard/libhxl-python`](https://github.com/HXLStandard/libhxl-python) est maintenu de façon sporadique par une seule personne. La suggestion de hashtags HXL reste un émetteur P3 au mieux dans la v0.3.

## Feuille de route de mise en œuvre

Il s'agit de la séquence proposée à l'origine. Ce n'est ni une liste de contrôle de mise en œuvre ni une déclaration selon laquelle ces livrables ont été livrés ; le périmètre actuellement pris en charge est indiqué au début de cette page.

- **v0.1 (fondation, cible : T3 2026).** [`schema/metrics.yaml`](https://github.com/PublicSchema/publicschema.org/blob/main/schema/metrics.yaml) portant les sept classes de catalogue plus les classes auxiliaires structurelles. De 10 à 15 Metrics d'amorçage couvrant l'ODD 1.3, la couverture / l'adéquation ASPIRE, les dépenses ESSPROS et les domaines de politique SOCX. Fichiers d'alignement externe pour SDMX, les ODD, ASPIRE, ESSPROS et SOCX. Générateurs P0 selon le tableau des cibles d'émission. JSON Schemas rédigés à la main dans `publicschema.org/schemas/v1/`. Une librairie CQL et une transformation VTL comme exemples détaillés pour l'ODD 1.3.1a. L'ADR-020 consigne ces décisions.
- **v0.2 (interopérabilité, cible : T1 2027).** Corpus d'amorçage complet d'environ 240 indicateurs, étendu à l'OCDE IDD et à EU-SILC d'Eurostat. Générateurs P1 / P2. Notation de cohorte. Hiérarchies de dimensions lorsque les consommateurs le demandent. `PublicSchema-ModelInfo.xml` testé avec `cqframework/clinical_quality_language`. Contribution de `gen-csvw` en amont à LinkML (clôt [linkml/linkml#86](https://github.com/linkml/linkml/issues/86)).
- **v0.3 (catalogue élargi, cible : T3 2027).** Générateurs P3 (DHIS2, HXL, IATI). De 30 à 50 Metrics supplémentaires couvrant la gestion de programme, l'inclusion et l'humanitaire. Forme `MetricConstraint` si l'émission vers les agences l'exige.

## Références

- W3C. [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). Recommandation, 2014. (Aucune liaison SDMX-RDF n'est maintenue par le SDMX-TWG en 2026 ; il s'agit de la correspondance RDF de fait, maintenue en dehors du TWG.)
- SDMX TWG. [Portail des normes SDMX 3.0](https://sdmx.org/standards-2/), et les dépôts canoniques du SDMX-TWG :
  - [sdmx-im](https://github.com/sdmx-twg/sdmx-im) : modèle d'information et structure des URN.
  - [sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) v3.1.0 (16 mai 2025) : format XML ; XSD sur [xml.sdmx.org](https://xml.sdmx.org).
  - [sdmx-json](https://github.com/sdmx-twg/sdmx-json) v2.1.0 (16 mai 2025) ; documentation sur [json.sdmx.org](https://json.sdmx.org).
  - [sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) v2.1.0 (27 août 2025).
  - [sdmx-rest](https://github.com/sdmx-twg/sdmx-rest) v2.2.2 (21 août 2025).
  - [vtl](https://github.com/sdmx-twg/vtl) v2.1 (11 avril 2025) ; documentation sur [sdmx-twg.github.io/vtl](https://sdmx-twg.github.io/vtl/).
  - [sdmx-registry](https://github.com/sdmx-twg/sdmx-registry), [sdmx-tck](https://github.com/sdmx-twg/sdmx-tck), [urn-resolver](https://github.com/sdmx-twg/urn-resolver) ([urn.sdmx.io](https://urn.sdmx.io)), [semver](https://github.com/sdmx-twg/semver).
- SDMX. [Cross-Domain Code Lists](https://sdmx.org/sdmx_cdcl/) ; [notes de version de CL_OBS_STATUS v2.3](https://sdmx.org/news/version-2-3-of-cl_obs_status-released/) (6 janvier 2026).
- BRI. [FMR (Fusion Metadata Registry)](https://www.sdmx.io/software/fmr/) : implémentation actuelle de registre SDMX ; [bis-med-it/fmr-public](https://github.com/bis-med-it/fmr-public) v12.0.0 (8 mai 2026).
- HL7. [Ressource FHIR R5 Measure](https://hl7.org/fhir/R5/measure.html) ; [CQF-Measures Implementation Guide v2.0.0](https://hl7.org/fhir/us/cqfmeasures/STU2/) (23 juillet 2020, ciblant R4 / R4B ; la 5.x sur build.fhir.org est une compilation continue non publiée).
- HL7. [Spécification CQL v1.5.3](https://cql.hl7.org/).
- [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language) : moteur CQL de référence HL7, Apache-2.0, v4.8.0 (8 mai 2026). Cible principale pour un ModelInfo non FHIR.
- [`vpinna80/VTL`](https://github.com/vpinna80/VTL) : moteur VTL de la Banca d'Italia, EUPL-1.2, v1.3.0 (24 septembre 2025). Implémentation VTL de référence de fait.
- OIT. [Outils SDMX d'ILOSTAT](https://ilostat.ilo.org/resources/sdmx-tools/) et [World Social Protection Database](https://www.social-protection.org/gimi/WSPDB.action) ; [métadonnées de l'ODD 1.3.1 (PDF)](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf).
- Banque mondiale. [ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire) ; [Poverty &amp; Inequality Platform](https://pip.worldbank.org/) ; [API Indicators de la Banque mondiale](https://api.worldbank.org/v2/indicator?format=json).
- Eurostat. [Méthodologie ESSPROS](https://ec.europa.eu/eurostat/web/social-protection/methodology) ; [métadonnées de référence ESMS](https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm).
- OCDE. [Base de données SOCX sur les dépenses sociales](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html) ; [DSD SOCX en service](https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.SPD/DSD_SOCX_AGG@DF_SOCX_AGG/1.0).
- UN Stats. [Métadonnées des indicateurs ODD](https://unstats.un.org/sdgs/metadata/) ; [API de métadonnées des ODD (UN LDS)](https://metadata.un.org/sdg/ontology).
- UNICEF. [MICS](https://mics.unicef.org/) et dictionnaires d'indicateurs.
- DHIS2. [Documentation sur les indicateurs](https://docs.dhis2.org/en/implement/database-design/aggregate-system-design/indicators.html).
- OCHA. [Hashtags et attributs HXL](https://centre.humdata.org/learning-path/hxl/hashtags-attributes/).
- IATI. [Norme d'activité : résultat / indicateur](https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/).
- LinkML. [linkml/linkml#86 générateur CSVW](https://github.com/linkml/linkml/issues/86) (ouvert, aucune PR) ; [linkml/linkml#901 exploration DataCube](https://github.com/linkml/linkml/issues/901) (fermé sans résolution).
- VLDB. [SDG-KG: Indicator Workflows as a Knowledge Graph](https://dl.acm.org/doi/10.14778/3750601.3750673), 2025.
