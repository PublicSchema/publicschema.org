# Normes connexes

PublicSchema s'inscrit dans un paysage d'initiatives connexes qui opèrent à différentes couches. Il est conçu pour compléter chacune d'elles, non pour les concurrencer.

## Où se situe PublicSchema

![Paysage des normes : PublicSchema comble la couche de vocabulaire du cycle de vie de la prestation](/images/standards-stack.svg)

| Couche | Ce qui existe | Ce qui manque |
|---|---|---|
| Confiance et transport | EBSI, OpenID4VC, W3C VC Data Model | Aucun vocabulaire de domaine dans les attestations |
| Attributs d'identité | EU Core Person Vocabulary, W3C Citizenship Vocabulary | Couvre uniquement nom/naissance/nationalité, pas les données de prestation |
| Catalogues de services | CPSV-AP (UE), HSDS/Open Referral, schema.org/GovernmentService | Décrit quels services existent, pas qui reçoit quoi |
| Interopérabilité des API | DCI, GovStack | Contrats d'interface entre systèmes, pas de vocabulaire sémantique |
| Mesure statistique | ILO/World Bank ASPIRE, ILOSTAT | Indicateurs et comptages, pas des modèles de données pour l'échange |
| **Vocabulaire du cycle de vie de la prestation** | **Rien** | **C'est la lacune que comble PublicSchema** |

## Initiatives spécifiques

### DCI

La Digital Convergence Initiative (initiative de convergence numérique) construit des normes d'interopérabilité des API entre les systèmes de protection sociale (interfaces de registre social, de paiement et d'enregistrement des faits d'état civil), co-pilotées par la GIZ, l'OIT et la Banque mondiale. PublicSchema est la couche de vocabulaire sémantique dont les normes d'API de DCI ont implicitement besoin mais qu'elles n'ont pas construite. DCI définit comment les données circulent entre les systèmes ; PublicSchema définit ce que les données signifient. Les deux sont complémentaires.

### Vocabulaires de base de l'UE (SEMIC / Interoperable Europe)

Le précédent technique le plus proche de la façon de construire un vocabulaire partagé. Le Core Person Vocabulary, le Core Location Vocabulary et le Core Public Service Vocabulary Application Profile (CPSV-AP) sont des vocabulaires RDF minimaux et réutilisables pour l'administration publique européenne, publiés avec des formes de validation SHACL sous CC-BY 4.0. PublicSchema s'aligne sur ceux-ci là où ils se chevauchent (personne, localisation, adresse) plutôt que de réinventer des définitions. Cependant, les Vocabulaires de base de l'UE couvrent l'identité et le catalogage des services, pas le cycle de vie de la prestation (inscription, droits à prestations, paiement, réclamation).

### GovStack

GovStack définit des spécifications de blocs de construction pour les services gouvernementaux numériques (identité, paiements, messagerie). PublicSchema est le pendant en termes de modèle de données : là où GovStack dit "vous avez besoin d'un bloc de construction de paiement", PublicSchema définit à quoi ressemblent les données de paiement entre les systèmes et comment les traduire entre eux. Les spécifications GovStack reconnaissent explicitement l'absence d'une couche sémantique transversale, ce qui est la lacune que comble PublicSchema.

### FHIR

La norme d'interopérabilité du secteur de la santé, combinant un modèle de données avec une spécification d'API. PublicSchema s'inspire de l'approche de FHIR (ressources, extensions, ensembles de valeurs, niveaux de maturité) mais cible l'espace des services gouvernementaux. Le modèle de gouvernance des vocabulaires de FHIR est une référence utile.

### Schema.org

Le modèle direct de la façon dont PublicSchema est structuré et publié. Schema.org a réussi car il était simple, optionnel et utile dès le premier jour. Ses types gouvernementaux (GovernmentService, GovernmentOrganization) sont extrêmement minces et orientés SEO ; ils ne modélisent pas les données de prestation.

### HSDS / Open Referral

La norme pour les répertoires de services ("quels services existent et où"). PublicSchema est destiné aux données de prestation ("qui reçoit quoi, quand, comment"). Un service décrit dans HSDS pourrait être le même service décrit par un Programme PublicSchema, mais les deux s'adressent aux extrémités opposées du cycle de vie.

### W3C Verifiable Credentials

Le W3C VC Data Model 2.0 fournit la couche de confiance. Le vocabulaire de PublicSchema, publié comme contexte JSON-LD avec des URI résolvables, sert de schéma qui rend les attestations de services gouvernementaux interopérables entre pays et systèmes. Les spécifications connexes incluent SD-JWT VC pour la divulgation sélective et OpenID4VCI/VP pour l'émission et la présentation d'attestations.

### EBSI

L'Infrastructure européenne de services blockchain (European Blockchain Services Infrastructure) opère au niveau de la couche de confiance et de transport, pas de la couche de vocabulaire de domaine. Cependant, ses schémas d'attestation pour l'identité des personnes (eIDAS PID), la coordination de la sécurité sociale (Document portable A1), l'assurance maladie (EHIC) et l'éducation (Europass EDC / ELM 3.2) modélisent beaucoup des mêmes entités que PublicSchema couvre. PublicSchema a utilisé les schémas EBSI comme contribution à la conception pour identifier les propriétés manquantes sur Personne, Adresse, Identifiant, Inscription et Droit.

### Registres de confiance

Une préoccupation complémentaire. Le vocabulaire définit ce que les termes signifient, mais les vérificateurs doivent également savoir quels émetteurs font autorité pour quelles affirmations. Cela est hors de portée pour le vocabulaire lui-même, mais tout déploiement aura besoin d'un registre de confiance à ses côtés. La fédération OpenID et le modèle de confiance EBSI sont des points de référence.
