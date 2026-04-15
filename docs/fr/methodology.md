# Méthodologie

## Pourquoi cette page existe

PublicSchema formule des affirmations sur le sens des données de prestation de services publics. Ces affirmations doivent être dignes de confiance. La confiance dépend de la compréhension de la façon dont le schéma est construit, de ce qui est accéléré par l'outillage et de ce qui est examiné par des humains. Cette page documente les deux.

## Ce que PublicSchema synthétise

Le modèle de référence est le fruit d'une revue de littérature étendue, d'une analyse systématique de systèmes de prestation open source et d'un alignement avec les normes internationales.

Les sources comprennent :

- **Systèmes open source** : openIMIS (assurance maladie sociale), OpenSPP (protection sociale), OpenCRVS (état civil), SEMIC (interopérabilité sémantique de l'UE), GovStack (blocs fonctionnels pour le gouvernement numérique). Les scripts de téléchargement et de conversion résident dans `external/`.
- **Normes internationales** : ISO (3166 pays, 4217 devises, 639-3 langues, 15924 écritures, 5218 codes de sexe), FHIR R4, régions UN M49, niveaux d'éducation ISCED, attestations vérifiables W3C, SD-JWT VC.
- **Initiatives sectorielles** : DCI (Digital Convergence Initiative) pour l'échange de données de protection sociale, EU Core Person Vocabulary, CPSV-AP et HSDS/Open Referral pour les catalogues de services, ILO et World Bank ASPIRE pour les indicateurs.
- **Littérature** : littérature académique et grise sur la prestation de protection sociale, l'identité et les modèles de données de services publics.

## Où l'IA apporte de la valeur

L'outillage IA accélère la recherche et la rédaction :

- **Lecture à grande échelle.** Comparer des modèles de données à travers six systèmes et plus, des dizaines de normes et une vaste littérature serait un travail long pour une petite équipe.
- **Mise en évidence de motifs et de divergences.** Identifier les points sur lesquels les systèmes s'accordent, ceux sur lesquels ils divergent et les lacunes à combler.
- **Premières ébauches.** Premières versions des définitions, listes de propriétés, ensembles de valeurs de vocabulaire et correspondances entre systèmes. Les ébauches sont des points de départ pour un examen humain, pas le produit final.

## Ce que les humains décident

Chaque définition de concept, propriété, entrée de vocabulaire et correspondance entre systèmes est examinée par un humain avant publication :

- **Définitions.** Réécrites pour une clarté en langage courant. Les définitions sont le produit, pas un sous-produit.
- **Correspondances.** Vérifiées par rapport aux schémas sources et à la documentation. Chaque correspondance porte un niveau de confiance et un commentaire signalant les incertitudes.
- **Décisions de conception.** Les choix architecturaux (supertypes abstraits, séparation entre observation et notation, espaces de noms par domaine) sont consignés dans des Architecture Decision Records dans `decisions/`. Chaque ADR énonce la question, les options envisagées et la justification du choix.
- **Domaines sensibles.** Les sujets qui requièrent une expertise métier (définitions juridiques, catégories protégées, variations culturelles) font l'objet d'un examen supplémentaire avant de sortir du stade brouillon.

## Couches de vérification

Les affirmations sont vérifiables, pas seulement énoncées :

- **Indicateurs de maturité.** Chaque concept, propriété et valeur de vocabulaire porte un niveau de maturité : brouillon, usage expérimental ou normatif. Voir [Versionnement et maturité](../versioning-and-maturity/). Le contenu en brouillon est explicitement signalé afin que les lecteurs sachent ce qui reste ouvert.
- **Registres de décisions publics.** Tout choix architectural non trivial fait l'objet d'un ADR dans `decisions/` documentant ce qui a été envisagé et pourquoi.
- **Tests automatisés.** Le pipeline de construction valide la structure YAML, l'intégrité référentielle, la complétude des traductions, les invariants du graphe RDF, l'exactitude des exports et la précision des correspondances avec les énumérations externes. Les tests résident dans `tests/`.
- **Open source de bout en bout.** Les sources YAML, les scripts de construction, les schémas externes convertis, les tests et le site sont tous publics. Toute personne peut reproduire la construction, auditer une correspondance ou proposer un changement.
- **Retours de la communauté.** Les retours des experts du domaine et des intégrateurs de systèmes orientent ce qui passe du stade brouillon à celui d'usage expérimental, puis à celui de normatif.

## Ce pour quoi l'IA n'est pas utilisée

- Accepter des contributions sans examen humain.
- Promouvoir des concepts au statut normatif. Les engagements de stabilité sont pris par des humains.
- Les décisions qui requièrent un jugement expert : définitions juridiques, classification de catégories protégées, variations culturelles, sensibilité des données.
- Ignorer les retours de la communauté ou les préoccupations des adoptants en aval.

## Limites connues

- Certaines parties du schéma sont encore au stade brouillon et attendent explicitement un examen par des experts. Elles sont signalées individuellement sur chaque page de concept, de propriété et de vocabulaire.
- Certaines correspondances entre systèmes ont été rédigées à partir de la documentation publique plutôt que d'une expérience pratique du système. Les retours des intégrateurs sont activement sollicités.
- La couverture bibliographique s'améliore de façon itérative.

Si quelque chose semble incorrect, merci d'ouvrir une issue ou de proposer un changement.

## Voir aussi

- [Principes de conception](../design-principles/) -- la philosophie que suit le schéma
- [Versionnement et maturité](../versioning-and-maturity/) -- comment la stabilité se gagne
- [Conception du schéma](../schema-design/) -- règles de nommage, de délimitation et de modélisation
