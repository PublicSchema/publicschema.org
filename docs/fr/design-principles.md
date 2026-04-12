# Principes de conception

## 1. Le sens avant la structure

Les concepts portent une signification. Une Personne n'est pas un simple ensemble de champs ; c'est une entité nommée avec une définition rédigée pour les praticiens du domaine. Le problème d'interopérabilité est la divergence de vocabulaire : les systèmes utilisent des noms différents pour les mêmes entités du monde réel, et lorsque ces noms expriment des choix sémantiques différents, les correspondances entre eux perdent de l'information. PublicSchema fournit des définitions partagées qui rendent les équivalences explicites et préservent le sens entre les systèmes.

## 2. Descriptif, pas prescriptif

Rien n'est obligatoire. Les systèmes adoptent les concepts, propriétés et vocabulaires qui leur sont applicables. PublicSchema décrit ce à quoi ressemblent les données de prestation entre les systèmes ; il n'impose pas ce que tout système doit collecter.

## 3. Fondé sur des données probantes et incrémental

Les données de convergence orientent les priorités. Une propriété présente dans 6 systèmes sur 6 mérite d'être normalisée avant une propriété présente dans 2 systèmes sur 6. Commencer par ce qui est confirmé, étendre lorsque l'adoption révèle un besoin réel.

## 4. Langage clair pour les praticiens

Les définitions sont rédigées pour les agents de politique publique et les gestionnaires de programme, pas pour les développeurs. "Les états du cycle de vie d'une inscription à un programme" est préférable à "une énumération de codes de statut applicables à l'entité d'enregistrement des bénéficiaires."

## Voir aussi

- [Conception du schéma](../schema-design/) -- nommage, portée et modélisation
- [Conception du vocabulaire](../vocabulary-design/) -- ensembles de valeurs contrôlées et correspondances de systèmes
- [Versionnement et maturité](../versioning-and-maturity/) -- garanties de stabilité et règles d'évolution
- [Divulgation sélective](../selective-disclosure/) -- conception de la confidentialité des attestations
