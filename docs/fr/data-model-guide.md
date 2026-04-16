# Guide de conception du modèle de données

Ce guide est destiné aux équipes qui construisent un nouveau système (un registre social, un système d'information de gestion, un outil de gestion de cas ou toute plateforme de prestation de services publics) et souhaitent qu'il soit interopérable dès le départ. Plutôt que d'intégrer la compatibilité après coup, vous concevez votre modèle de données en prenant PublicSchema comme référence.

## Sommaire

- [Quand utiliser cette approche](#quand-utiliser-cette-approche)
- [Ce que "compatible" signifie](#ce-que-compatible-signifie)
- [Étape 1 : Identifier les concepts dont vous avez besoin](#étape-1--identifier-les-concepts-dont-vous-avez-besoin)
- [Étape 2 : Examiner les propriétés de chaque concept](#étape-2--examiner-les-propriétés-de-chaque-concept)
- [Étape 3 : Adopter les vocabulaires canoniques](#étape-3--adopter-les-vocabulaires-canoniques)
- [Étape 4 : Ajouter vos propres champs](#étape-4--ajouter-vos-propres-champs)
- [Étape 5 : Valider votre conception](#étape-5--valider-votre-conception)
- [Utiliser PublicSchema dans les appels d'offres](#utiliser-publicschema-dans-les-appels-doffres)
- [Modèles de conception à connaître](#modèles-de-conception-à-connaître)
- [Téléchargements disponibles](#téléchargements-disponibles)
- [Prochaines étapes](#prochaines-étapes)

## Quand utiliser cette approche

Cette approche fonctionne bien lorsque :

- Vous construisez un nouveau système et souhaitez qu'il échange des données avec des plateformes existantes
- Vous rédigez un appel d'offres et avez besoin d'exigences d'interopérabilité concrètes
- Vous concevez un modèle de données pour un programme multi-pays ou multi-secteurs
- Vous remplacez un système existant et souhaitez que le nouveau soit plus facile à intégrer

Il ne s'agit pas d'importer PublicSchema dans votre système comme une dépendance. Il s'agit de l'utiliser comme référence pour que vos choix de conception soient compatibles avec le vocabulaire partagé.

## Ce que "compatible" signifie

Un modèle de données compatible avec PublicSchema :

1. **Utilise les mêmes concepts.** Votre table "bénéficiaire" correspond clairement au concept Personne de PublicSchema, même si vous l'appelez différemment en interne.
2. **Stocke les mêmes propriétés.** Vos champs couvrent les propriétés PublicSchema dont vous avez besoin, avec des types compatibles. Vous pouvez avoir des champs supplémentaires ; c'est parfaitement acceptable.
3. **Utilise les mêmes codes de vocabulaire.** Là où PublicSchema définit un ensemble de valeurs contrôlées (statut d'inscription, genre, canal de livraison), votre système utilise les mêmes codes ou peut les convertir sans effort.
4. **Peut exporter dans un format canonique.** Sur cette base, votre système peut produire des exports ou des réponses d'API alignés sur les noms de propriétés et les codes de vocabulaire PublicSchema.

Vous n'avez pas besoin d'utiliser les noms de champs exacts de PublicSchema en interne, d'adopter JSON-LD ou de changer votre moteur de base de données. La compatibilité est une question d'alignement sémantique, non de conformité de structure.

## Étape 1 : Identifier les concepts dont vous avez besoin

Parcourez la [page des concepts](/concepts/) et identifiez quels concepts s'appliquent à votre système. Tous les systèmes n'ont pas besoin de tous les concepts.

Un registre social a généralement besoin de : Personne, Ménage, GroupMembership, Identifiant, Adresse, Localisation.

Un système de gestion des prestations peut ajouter : Programme, Inscription, Droit, EligibilityDecision, PaymentEvent.

Un système de réclamations ajoute : Grievance.

Téléchargez le **classeur Excel de définition** pour chaque concept que vous prévoyez d'implémenter. Le classeur de définition inclut :

- Les métadonnées du concept (URI, domaine, niveau de maturité, définitions en FR/EN/ES)
- La liste complète des propriétés avec les types, la cardinalité et les définitions
- Les vocabulaires référencés avec tous les codes

Cela vous donne un document de référence autonome pour chaque concept.

## Étape 2 : Examiner les propriétés de chaque concept

Pour chaque concept, examinez la liste de propriétés et décidez lesquelles votre système a besoin. PublicSchema est descriptif, pas prescriptif : tout est optionnel. Adoptez les propriétés qui comptent pour votre cas d'utilisation.

Pour chaque propriété que vous adoptez, alignez-vous sur :

- **Le nom.** Votre nom de champ interne peut différer, mais documentez la correspondance. Si vous pouvez utiliser le nom PublicSchema directement (par exemple, `given_name`, `enrollment_status`), la correspondance est triviale.
- **Le type.** Respectez le type attendu. Si PublicSchema indique `date`, stockez une date, pas une chaîne de caractères. Si c'est `integer`, stockez un entier.
- **La cardinalité.** PublicSchema marque les propriétés comme à valeur unique ou multi-valuées. Si une propriété est multi-valuée (par exemple, une personne peut avoir plusieurs identifiants), concevez votre schéma pour le prendre en charge (par exemple, une table séparée ou un champ tableau).

Le **CSV** du concept est utile comme liste de contrôle lors de cette étape.

## Étape 3 : Adopter les vocabulaires canoniques

Pour toute propriété soutenue par un vocabulaire (codes de statut, genre, types de documents, etc.), utilisez les codes canoniques directement si vous le pouvez. C'est le choix de conception le plus rentable, car il élimine la nécessité de traduire les codes à chaque nouvelle intégration.

Si vous devez utiliser des codes internes différents (par exemple, votre base de données utilise des clés étrangères entières), maintenez une table de correspondance qui lie vos codes aux codes canoniques. Intégrez cette correspondance dans votre système dès le départ, et non en dernière minute.

Consultez le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/) pour plus de détails sur l'utilisation des vocabulaires.

## Étape 4 : Ajouter vos propres champs

Votre système aura presque certainement besoin de champs que PublicSchema ne définit pas. C'est attendu et tout à fait normal. PublicSchema couvre le terrain commun entre les systèmes, pas tous les champs possibles.

Lors de l'ajout de champs personnalisés :

- **Ne créez pas de collision avec les noms de propriétés PublicSchema.** Vérifiez la [page des propriétés](/properties/) pour vous assurer que votre nom de champ personnalisé n'est pas déjà défini avec une sémantique différente.
- **Réfléchissez si le champ pourrait être utile à d'autres.** S'il représente un concept commun que PublicSchema ne couvre pas encore, il peut être un candidat à la contribution. Consultez le [Mécanisme d'extension](/docs/extension-mechanism/) pour savoir comment définir des propriétés personnalisées dans votre propre espace de noms.
- **Documentez vos extensions.** Les futurs partenaires d'intégration devront savoir quels champs sont canoniques et lesquels sont personnalisés.

## Étape 5 : Valider votre conception

Utilisez les artefacts suivants pour vérifier votre conception par rapport à PublicSchema :

- **Schéma JSON :** Validez des exemples d'enregistrements par rapport au schéma JSON du concept. Si vos données exportées passent la validation, votre schéma est compatible.
- **Formes SHACL :** Si vous travaillez avec RDF, les formes SHACL fournissent une validation des contraintes pour tous les concepts.
- **Modèle Excel :** Saisissez des exemples de données dans le modèle Excel pour chaque concept. Si les données de votre système remplissent le modèle proprement, la correspondance est solide. Si des colonnes sont vides ou si des valeurs ne correspondent pas aux listes déroulantes, analysez les écarts.

## Utiliser PublicSchema dans les appels d'offres

Si vous rédigez un appel d'offres pour un nouveau système, PublicSchema vous donne un langage concret pour les exigences d'interopérabilité au lieu d'aspirations vagues.

Exemple de formulation d'exigence :

> Le système doit être capable d'exporter des enregistrements de Personne avec les propriétés suivantes telles que définies par PublicSchema (publicschema.org) : given_name, family_name, date_of_birth, sex, identifiers. Le statut d'inscription doit utiliser les codes du vocabulaire enrollment-status de PublicSchema. Le système doit prendre en charge l'export au format CSV avec les noms de propriétés PublicSchema comme en-têtes de colonnes.

C'est vérifiable. Lors de l'évaluation, vous pouvez remettre aux fournisseurs un modèle Excel et leur demander de démontrer que leur système peut produire un export conforme.

Vous pouvez également référencer directement les classeurs Excel de définition dans l'appel d'offres comme spécification faisant autorité pour chaque entité que le système doit prendre en charge.

## Modèles de conception à connaître

### La relation Personne-Groupe est plusieurs-à-plusieurs

PublicSchema modélise la relation entre les personnes et les groupes (ménages, familles, etc.) via un concept GroupMembership qui porte un rôle (chef, conjoint, enfant, dépendant). Ne modélisez pas cela comme une simple liste de membres sur le groupe. Une personne peut appartenir à plusieurs groupes, et le rôle compte.

### Les identifiants sont séparés de la Personne

PublicSchema modélise les identifiants (numéro d'identité nationale, numéro de passeport, numéro d'identifiant de programme) comme un concept Identifiant distinct lié à Personne, pas comme des champs directement sur Personne. Identifiant ne porte que la valeur codée et son schéma; les documents qui portent des identifiants (passeports, cartes d'identité nationale, cartes de bénéficiaire) sont modélisés comme IdentityDocument, qui porte l'autorité émettrice, la juridiction, la date de délivrance et l'expiration.

### La délimitation temporelle est un concept de premier plan

De nombreux concepts portent start_date et end_date. Une inscription n'est pas seulement un statut ; c'est une relation bornée dans le temps. Concevez votre schéma pour prendre en charge ce modèle plutôt que de ne stocker que l'état actuel.

### Espace de noms de domaine

Certains concepts sont universels (Personne, Localisation) et d'autres sont spécifiques à un domaine (Inscription est sous la protection sociale, `/sp/Enrollment`). Si vous construisez pour un secteur spécifique, vérifiez à quel domaine appartiennent vos concepts. Cela affecte les URI mais pas la façon dont vous utilisez les propriétés.

### Les données d'observation appartiennent à un Profile, pas à Person ou Household

Les items de fonctionnement du Washington Group (WG-SS, WG-ES, CFM) et les réponses aux enquêtes socio-économiques (type de logement, service WASH, actifs, TIC, revenus) sont des enregistrements ponctuels produits par un instrument défini. Ils sont modélisés comme des enregistrements `Profile` (`FunctioningProfile`, `SocioEconomicProfile`), et non comme des colonnes sur Person ou Household. Les sous-types de profil humanitaires (`AnthropometricProfile`, `FoodSecurityProfile`, `DwellingDamageProfile`) vivent dans un schéma frère en dehors de PublicSchema et suivent le même modèle, en étendant le `Profile` abstrait de PublicSchema comme supertype.

Un `Profile` porte l'information sur qui a été observé, quand, avec quel instrument, selon quel mode d'administration et par qui. Les Profiles peuvent aussi porter les résultats dérivés en appliquant la règle de notation canonique de l'instrument : par exemple, l'identifiant de handicap WG-SS sur `FunctioningProfile` ou un score PMT sur `SocioEconomicProfile`. Ces résultats canoniques sont directement sur le Profile car ils sont produits par une règle unique et bien définie, indissociable de l'instrument lui-même. Person conserve de petits indicateurs de synthèse (`functioning_status`, `nutrition_status`) pour que les systèmes opérationnels puissent interroger le ciblage et le reporting sans recalculer depuis chaque passation ; Household conserve de même `food_security_level`. Ces indicateurs sont des dénormalisations de commodité, pas des classifications. Le Profile reste la source de vérité. Voir [ADR-011](../decisions/011-humanitarian-profile-extraction.md).

### La notation non canonique est un acte distinct de la passation d'instrument

Les méthodologies de notation non canoniques (formules PMT, PPI, indices de pauvreté multidimensionnels, indices composites comme le CARI, seuils alternatifs ou seuils définis par des chercheurs) sont cataloguées comme des enregistrements `ScoringRule`. Appliquer une règle non canonique à un ou plusieurs Profiles ou données en ligne produit un `ScoringEvent`, qui porte le score brut et la bande. Séparer la notation non canonique du Profile permet de noter les mêmes données selon plusieurs règles sans re-collecter, tout en gardant les résultats canoniques proches des observations qui les ont produits. Voir [ADR-010](../decisions/010-profile-derived-outputs.md).

## Téléchargements disponibles

**Par concept :**

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **Classeur Excel de définition** | Classeur multi-feuilles avec métadonnées, propriétés et vocabulaires référencés en FR/EN/ES | Référence principale lors de la conception du modèle de données |
| **Modèle Excel** | Classeur de saisie de données avec validation par liste déroulante | Test de compatibilité, prototypage de formulaires, évaluation d'appels d'offres |
| **CSV** | Propriétés avec types et définitions | Liste de contrôle pour la revue de conception champ par champ |
| **JSON-LD** | Concept en données liées | Accès lisible par machine |

**Par vocabulaire :**

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **CSV** | Codes avec libellés et définitions multilingues | Initialisation des tables de correspondance dans votre base de données |
| **JSON-LD** | Vocabulaire en tant que SKOS ConceptScheme | Accès programmatique |

**Validation :**

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **Schéma JSON** (par concept) | Schéma JSON Draft 2020-12 | Validation des enregistrements exportés |
| **Formes SHACL** | Contraintes de validation RDF | Validation des données RDF |

## Prochaines étapes

- Pour aligner des codes de valeurs dans un système existant, consultez le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/).
- Pour connecter des systèmes existants en utilisant PublicSchema comme couche de traduction, consultez le [Guide d'interopérabilité et de correspondance](/docs/interoperability-guide/).
- Pour utiliser des contextes JSON-LD et émettre des attestations vérifiables, consultez le [Guide JSON-LD et VC](/docs/jsonld-vc-guide/).
