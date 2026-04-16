# Principes de conception

## 1. Le sens avant la structure

Les concepts portent une signification. Une Personne n'est pas un simple ensemble de champs ; c'est une entité nommée avec une définition rédigée pour les praticiens du domaine. Le problème d'interopérabilité est la divergence de vocabulaire : les systèmes utilisent des noms différents pour les mêmes entités du monde réel, et lorsque ces noms expriment des choix sémantiques différents, les correspondances entre eux perdent de l'information. PublicSchema fournit des définitions partagées qui rendent les équivalences explicites et préservent le sens entre les systèmes.

## 2. Descriptif, pas prescriptif

Rien n'est obligatoire. Les systèmes adoptent les concepts, propriétés et vocabulaires qui leur sont applicables. PublicSchema décrit ce à quoi ressemblent les données de prestation entre les systèmes ; il n'impose pas ce que tout système doit collecter.

## 3. Fondé sur des données probantes et incrémental

Les données de convergence orientent les priorités. Une propriété présente dans 6 systèmes sur 6 mérite d'être normalisée avant une propriété présente dans 2 systèmes sur 6. Commencer par ce qui est confirmé, étendre lorsque l'adoption révèle un besoin réel.

## 4. Langage clair pour les praticiens

Les définitions sont rédigées pour les agents de politique publique et les gestionnaires de programme, pas pour les développeurs. "Les états du cycle de vie d'une inscription à un programme" est préférable à "une énumération de codes de statut applicables à l'entité d'enregistrement des bénéficiaires."

## 5. Supertypes abstraits

Certains concepts n'existent que comme fondations partagées pour des sous-types plus spécifiques. Agent, Event, Party et Profile portent `abstract: true`, ce qui signifie qu'ils définissent des propriétés communes mais ne sont jamais instanciés directement. Les sous-types (par exemple FunctioningProfile, ScoringEvent, Organization) héritent de ces propriétés et ajoutent les leurs. Agent est le supertype côté acteur (Person, Organization, SoftwareAgent) ; Party est le supertype côté bénéficiaire (Person, Group). Person appartient aux deux. Voir [ADR-006](../decisions/006-profile-hierarchy.md) et [ADR-008](../decisions/008-agent-organization.md).

## 6. Séparation observation et notation

La collecte et la notation des données sont des étapes distinctes, avec des acteurs, des horodatages et des pistes d'audit différents. Les sous-types de Profile enregistrent les réponses structurées d'une passation unique d'instrument et peuvent aussi porter les résultats dérivés en appliquant la règle de notation canonique de l'instrument (par exemple, l'identifiant de handicap WG-SS sur FunctioningProfile, ou un score PMT sur SocioEconomicProfile). ScoringEvent enregistre l'acte d'appliquer une règle non standard, un seuil alternatif ou de recalculer un score après une révision de règle. Cette séparation permet aux systèmes de recalculer les scores sans re-collecter les données, tout en gardant les résultats canoniques proches des observations qui les ont produits. Des sous-types de Profile spécifiques à un domaine publiés dans des schémas frères suivent le même modèle. Voir [ADR-006](../decisions/006-profile-hierarchy.md), [ADR-010](../decisions/010-profile-derived-outputs.md) et [ADR-011](../decisions/011-humanitarian-profile-extraction.md).

## 7. Catégories de propriétés

Les propriétés sont regroupées par catégorie thématique (par exemple fonctionnement, nutrition, logement) plutôt que listées à plat. Les catégories sont définies dans `schema/categories.yaml` et rendues comme regroupements visuels sur les pages de détail des concepts. Cela aide les praticiens à localiser les propriétés pertinentes sur les concepts qui en portent beaucoup.

## 8. Métadonnées d'instrument

Les propriétés qui enregistrent le contexte de collecte (mode d'administration, répondant, relation avec le répondant, applicabilité par âge) accompagnent les données d'observation, sans fichier de métadonnées séparé. Cela garantit qu'un enregistrement de Profile est auto-descriptif : un consommateur peut déterminer comment les données ont été collectées sans consulter un registre externe. Voir [schema-design.md section 7](schema-design.md#7-age-applicability) pour les détails d'applicabilité par âge.

## Voir aussi

- [Conception du schéma](../schema-design/) -- nommage, portée et modélisation
- [Conception du vocabulaire](../vocabulary-design/) -- ensembles de valeurs contrôlées et correspondances de systèmes
- [Versionnement et maturité](../versioning-and-maturity/) -- garanties de stabilité et règles d'évolution
- [Divulgation sélective](../selective-disclosure/) -- conception de la confidentialité des attestations
