# Conception du schéma

## 1. Conventions de nommage

La casse encode le type d'élément :

| Type d'élément | Convention | Exemples |
|---|---|---|
| Concepts | PascalCase | Person, Enrollment, GroupMembership |
| Propriétés | snake_case | given_name, date_of_birth |
| Codes de valeurs de vocabulaire | snake_case | never_married, bank_transfer |
| Identifiants de vocabulaire | kebab-case | gender-type, enrollment-status |

Ces conventions sont appliquées par des validateurs d'expression régulière dans les schémas JSON. Une fois qu'un nom est publié en usage expérimental ou au-dessus, il ne peut plus être modifié.

## 2. URI scoped par domaine

Certains concepts partagent un nom entre domaines mais portent une sémantique différente ("Enrollment" en protection sociale et en éducation). Les éléments spécifiques à un domaine obtiennent un segment de domaine dans leur URI ; les éléments universels se trouvent à la racine :

- `publicschema.org/sp/Enrollment` (protection sociale)
- `publicschema.org/Person` (universel)

Le test : un élément est universel si la même définition porte le même sens quel que soit le domaine. Dans le cas contraire, il appartient à un espace de noms de domaine.

Le même test s'applique en principe aux propriétés et aux vocabulaires, mais son application relève du jugement. Un vocabulaire contrôlé dont les valeurs sont étroitement liées à un flux de travail de domaine (`sp/grievance-type`, `sp/grievance-status`, `sp/enrollment-status`) est clairement à portée de domaine. Une propriété qui référence un tel vocabulaire (`grievance_type`, `grievance_status`) peut toutefois rester dans l'espace de noms racine lorsque la forme primitive de la propriété (une valeur codée, une date ISO, une référence d'identifiant) est portable même si son ensemble de valeurs ne l'est pas. Plusieurs paires « propriété à la racine, vocabulaire à portée de domaine » existent dans le schéma actuel. Ce découpage est délibéré : il maintient l'URI de la propriété stable si le concept est renommé ou généralisé à d'autres domaines par la suite, tandis que le vocabulaire porte la sémantique spécifique au domaine.

Les noms ne sont jamais préfixés par une abréviation de domaine. C'est `Enrollment`, pas `SPEnrollment`. La structure des URI gère la désambiguïsation. Une exception nommée existe : `CRVSPerson`, documentée dans [ADR-014](../../decisions/014-crvs-person-naming.md). Ce n'est pas un précédent ; toute exception supplémentaire nécessite son propre ADR.

| Code | Domaine | Statut |
|---|---|---|
| `sp` | Protection sociale | Actif |
| `edu` | Éducation | Futur |
| `health` | Santé | Futur |
| `crvs` | Enregistrement des faits d'état civil et statistiques de l'état civil | Actif |

ServicePoint et ses sous-types (HealthFacility, School, WaterPoint, RegistrationOffice) restent à la racine plutôt que sous des segments de domaine. Ils sont classifiés par secteur au moyen du vocabulaire des types de points de service, et non par domaine d'URI. Cela permet aux enregistrements de points de service d'être utilisables de manière transversale dans les flux de travail de protection sociale, d'éducation, de santé et de CRVS, sans introduire de supertypes spécifiques à un domaine.

## 3. Persistance des URI

Chaque élément obtient un URI stable. Une fois publié en usage expérimental ou au-dessus, un URI ne sera pas supprimé. Les termes dépréciés continuent de se résoudre avec des métadonnées indiquant le remplacement. Consultez [Versionnement et maturité](../versioning-and-maturity/) pour le modèle complet.

## 4. Concept, propriété ou vocabulaire

Utilisez cet arbre de décision pour déterminer quel type d'élément créer.

![Arbre de décision : identité propre, ensemble de valeurs fermé, la valeur a une identité](/images/decision-tree.svg)

**Étape 1 : A-t-il sa propre identité ?** Cette chose existe-t-elle de manière indépendante, est-elle référencée depuis plusieurs endroits et a-t-elle son propre cycle de vie ? Si oui, c'est un **concept**.

*Exemple :* GroupMembership est un concept, pas une propriété sur Personne ou Groupe. Il porte ses propres données (rôle, dates), a son propre cycle de vie, et est référencé des deux côtés.

**Étape 2 : Est-ce un attribut d'un concept ?** Un fait sur un concept spécifique, sans identité indépendante ? Si oui, c'est une **propriété**. Plusieurs valeurs (par exemple, des numéros de téléphone) en font quand même une propriété avec une cardinalité `many`.

**Étape 3 : La valeur est-elle tirée d'un ensemble fermé ?** Si la propriété accepte une réponse parmi une liste définie avec des significations stables, l'ensemble de valeurs est un **vocabulaire**.

**Étape 4 : Référence ou en ligne ?** Si la valeur a sa propre identité et ses propres propriétés, référencez un concept (`concept: Location`). Si c'est un scalaire simple, utilisez un primitif en ligne.

*Exemple :* `latitude` est un `decimal` en ligne sur Location. Il n'a pas d'identité indépendante ni de sous-propriétés. C'est un nombre.

| Situation | Type d'élément |
|---|---|
| Cycle de vie propre, référencé depuis plusieurs concepts | Concept |
| Attribut d'un concept, sans identité indépendante | Propriété |
| Valeur tirée d'un ensemble fermé d'options | Vocabulaire |
| La valeur a sa propre identité et des sous-propriétés | Propriété référençant un concept |
| Scalaire simple | Type primitif en ligne |

## 4a. Concepts de type groupe

Trois concepts de PublicSchema décrivent des regroupements de personnes mais ont des sémantiques distinctes. Choisir le bon concept est important pour la qualité des données et l'interopérabilité.

**Household (Ménage)** est une unité économique corésidente. Les membres partagent un logement et, en général, de la nourriture et des ressources. La définition opérationnelle varie selon les pays et les programmes (combinant des critères de corésidence, de budget partagé, de cuisine commune et de parenté), mais le critère central reste toujours la colocalisation physique et les moyens de subsistance partagés. Household est le concept approprié pour l'enregistrement des unités bénéficiaires dans les programmes de protection sociale.

**Family (Famille)** est un réseau de parenté. Les membres sont liés par le sang, le mariage ou l'adoption, indépendamment de leur lieu de résidence. Une famille peut s'étendre sur plusieurs ménages et zones géographiques. Les liens de parenté entre membres sont modélisés par des enregistrements Relationship entre instances Person ; Family elle-même ne porte pas de propriétés de parenté dédiées à ce stade. Family est le concept approprié lorsque l'unité d'intérêt est un réseau relationnel plutôt qu'un arrangement corésident.

**FamilyRegister (Registre de famille)** est un document administratif, et non un groupe. C'est un acte d'état civil qui suit une unité familiale dans le temps à mesure que surviennent des événements vitaux (naissances, décès, mariages). Il référence une Family pour exposer la composition actuelle. FamilyRegister est le concept approprié pour modéliser des instruments administratifs de type koseki, hukou ou livret de famille.

### Quand utiliser chaque concept

| Vous souhaitez enregistrer... | Utilisez |
|---|---|
| Une unité bénéficiaire partageant un logement et des ressources | Household |
| Un réseau de personnes liées par le sang, le mariage ou l'adoption | Family |
| Un document administratif d'état civil suivant une famille | FamilyRegister |

### Pont d'interopérabilité

De nombreux systèmes utilisent le terme « famille » de façon familière pour désigner l'unité corésidente. Lors d'échanges de données avec de tels systèmes, définissez `group_type: family` sur l'enregistrement Household. Cela indique aux consommateurs que le ménage est représenté comme une famille à des fins d'interopérabilité, sans dénaturer la sémantique de PublicSchema.

## 5. Contexte temporel

Presque tout dans la prestation de services publics est borné dans le temps. Un instantané de statut sans période de validité est incomplet. Lors de la conception d'un concept ou d'une propriété, demandez-vous : cette valeur changera-t-elle au fil du temps ? Si oui, modélisez explicitement le contexte temporel (dates de début/fin, périodes de validité).

### Conventions pour les propriétés de date

Les concepts à cycle de vie utilisent des noms de dates spécifiques au domaine qui décrivent l'événement du domaine. Les concepts de relation et d'appartenance utilisent les dates génériques `start_date` / `end_date`.

| Type de concept | Modèle de date | Exemples |
|---|---|---|
| Cycle de vie (Inscription) | Dates nommées spécifiques au domaine | `enrollment_date`, `exit_date` |
| Cycle de vie (Droit) | Période spécifique au domaine | `coverage_period_start`, `coverage_period_end` |
| Cycle de vie (Réclamation) | Dates d'événements spécifiques au domaine | `submission_date`, `resolution_date` |
| Événement unique (PaymentEvent) | Date d'événement unique | `payment_date` |
| Relation (GroupMembership, Relationship) | Dates génériques | `start_date`, `end_date` |

Ne combinez pas les deux modèles sur un même concept. Un concept à cycle de vie ne doit pas porter à la fois `enrollment_date` et `start_date`.

## 6. Indépendance des propriétés

Une propriété comme `start_date` est définie une seule fois et réutilisée pour l'ensemble des concepts. Lorsqu'une propriété partagée nécessite des ensembles de valeurs spécifiques à un concept (par exemple, `status` sur Inscription et Réclamation), elle se spécialise via des références de vocabulaire différentes plutôt que de prétendre que les différences n'existent pas.

### Réutilisation d'une propriété entre concepts

L'indépendance des propriétés ne se limite pas aux champs structurels répétés. Des observables substantiels peuvent aussi être réutilisés entre concepts. `water_source`, `sanitation_facility` et `dwelling_type` apparaissent à la fois sur `SocioEconomicProfile` (contexte d'enregistrement de base) et sur `DwellingDamageProfile` (évaluation post-choc). Dans chaque cas, la propriété est déclarée une seule fois et figure dans la liste `properties` de chaque concept.

Les règles qui maintiennent la cohérence :

1. **Un fichier de propriété par concept nommé.** `water_source` est un unique fichier YAML référencé depuis les deux profils.
2. **Le cadrage contextuel vit sur le concept, pas sur la propriété.** La définition de la propriété nomme l'observable (« la source principale d'eau potable du ménage »). La définition de chaque concept nomme la façon dont cet observable est interprété dans ce concept (enregistrement de base ou post-choc).
3. **La réutilisation doit être annoncée dans la définition narrative des deux concepts.** Un lecteur sur l'une ou l'autre page doit pouvoir constater que le champ apparaît aussi ailleurs et pourquoi.
4. **La réutilisation ne rend pas les enregistrements compatibles en type.** Un enregistrement `SocioEconomicProfile` et un enregistrement `DwellingDamageProfile` sont des choses différentes même lorsque leurs valeurs de propriétés se recoupent. Les adoptants doivent consulter la page du concept, pas la liste des propriétés, pour sérialiser vers une forme fortement typée.
5. **Scindez lorsque la formulation diverge.** Si la définition propre à la propriété doit varier d'un contexte à l'autre, créez deux propriétés. `location` et `location_of_assessment` sont scindées ainsi : `location` est la localisation administrative ou par coordonnées enregistrée du ménage ; `location_of_assessment` est l'endroit où une évaluation des dégâts post-choc a effectivement été menée, qui peut différer après un déplacement.

`triggering_hazard_event` (sur `DwellingDamageProfile`) et `triggering_vital_event` (sur `CivilStatusAnnotation`) suivent le même principe. Initialement unifiés dans une propriété unique `triggering_event` dont le type avait été élargi à `concept:Event`, ils ont été scindés parce que le sous-type attendu porte un sens pour les validateurs et les praticiens ; chaque consommateur déclare désormais sa propre référence typée. Voir [ADR-007](../../decisions/007-profile-property-reuse.md) pour l'argumentaire complet.

## 7. Applicabilité par âge

Certaines propriétés portant sur la personne ne sont significatives que pour des tranches d'âge spécifiques. Le module court et le module étendu du Washington Group s'appliquent aux adultes ; le module de fonctionnement de l'enfant (CFM) s'applique aux enfants de 2-4 ans et de 5-17 ans. Les normes de croissance de l'OMS s'appliquent aux enfants de moins de 5 ans. Plutôt que d'encoder ces règles uniquement dans le texte de définition (que les machines ne peuvent pas interpréter), les propriétés portent un tableau optionnel `age_applicability` de balises contrôlées.

| Balise | Plage numérique | Source de la tranche |
|---|---|---|
| `infant_0_1` | 0-23 mois | Petite enfance générale (couvre les modules nourrissons MICS, la croissance OMS précoce) |
| `child_2_4` | 2-4 ans (24-59 mois) | Variante CFM 2-4 ; normes de croissance de l'enfant OMS |
| `child_5_17` | 5-17 ans | Variante CFM 5-17 ; également la définition CRC de « enfant » |
| `adolescent` | 10-19 ans | Définition de l'OMS (délibérément transversale avec child_5_17 et adult) |
| `adult` | 18 ans et plus | WG-SS / WG-ES |

### Pertinence thématique, pas éligibilité

`age_applicability` répond à la question : « quels groupes d'âge cette propriété concerne-t-elle ? » Ce n'est **pas** un filtre primitif d'éligibilité. Le filtrage par âge est la responsabilité du consommateur, calculé à partir de `date_of_birth`. Dans cette optique, le chevauchement entre balises est une fonctionnalité, non un défaut : une propriété portant sur la santé reproductive des adolescents porte à la fois `child_5_17` et `adolescent` parce que le sujet concerne réellement la tranche des moins de 18 ans et la tranche OMS des 10-19 ans.

Un consommateur demandant « ce champ est-il pertinent pour un enfant de 15 ans ? » évalue l'âge de l'enfant par rapport à toutes les tranches de la propriété et vérifie si l'une d'elles correspond. Un consommateur demandant « ce sujet est-il spécifique à l'adolescence ? » vérifie la présence de la balise `adolescent`.

### Règles de population

- Ne remplir que pour les propriétés qui s'attachent à `Person`. L'applicabilité par âge n'a pas de sens sur les concepts sans âge.
- Non obligatoire. L'absence signifie que la propriété s'applique de manière générale à tout âge.
- Le validateur impose la couverture impliquée par la bibliographie : les propriétés citées par `washington-group-ss` ou `washington-group-es` doivent inclure `adult` ; les propriétés citées par `washington-group-cfm` doivent inclure au moins l'une des tranches enfants (`child_2_4` ou `child_5_17`). Les propriétés peuvent restreindre la couverture CFM lorsque le texte de définition explique la variante à laquelle elles correspondent.

## 8. Équivalents externes et liaisons de sérialisation

Le champ `external_equivalents` sur les propriétés était initialement prévu pour les équivalents dans d'autres *ontologies* (vocabulaires de base SEMIC, DCI Core) : une propriété comme `given_name` correspond exactement à `http://www.w3.org/ns/person#firstName`. La correspondance est sémantique : les deux décrivent le même concept dans une ontologie alternative.

Le même champ est également utilisé pour les **liaisons de sérialisation** telles que FHIR R4 Observation avec des codes LOINC. Ce ne sont pas des équivalents au sens SEMIC/DCI ; ce sont des instructions indiquant comment sérialiser cette propriété dans un format d'interopérabilité spécifique. La distinction est importante lors de la lecture d'une page de détail de propriété : une ligne SEMIC indique « ce concept existe dans une autre ontologie » ; une ligne FHIR/LOINC indique « lorsque vous sérialisez ces données en FHIR, utilisez ce code. »

Convention :
- Les codes LOINC par élément appartiennent à la **propriété** (chaque élément WG a son propre code LOINC).
- Les références à une liste de réponses LOINC pour un vocabulaire entier appartiennent au **vocabulaire** (`standard.uri`). Exemple : `pregnancy-status` porte un URI de liste de réponses LOINC pour l'ensemble des valeurs.

## 9. Annotations de sensibilité

Certaines propriétés révèlent des circonstances sensibles que la personne soit identifiable ou non. `program_ref` révèle l'inscription à un programme spécifique (qui peut cibler le VIH, le handicap ou la pauvreté). `grievance_type` révèle que quelqu'un a déposé une plainte.

| Niveau | Quand l'utiliser | Ce qu'il signale |
|---|---|---|
| `standard` | Par défaut. Aucun traitement spécial au-delà de la protection normale des données. | Peut être omis (supposé absent). |
| `sensitive` | Révèle des circonstances (santé, pauvreté, victimisation) dans la plupart des contextes. | Nécessite une justification pour collecter ou divulguer. |
| `restricted` | Ne devrait pas apparaître dans les attestations aux points de service courants. | Nécessite une analyse d'impact sur la protection des données. |

C'est un avertissement pour les praticiens, pas une étiquette de conformité. Le fait qu'une propriété constitue une donnée personnelle dépend de l'enregistrement dans lequel elle apparaît, pas de la propriété elle-même. Consultez [Divulgation sélective](../selective-disclosure/) pour la classification au niveau de l'attestation.
