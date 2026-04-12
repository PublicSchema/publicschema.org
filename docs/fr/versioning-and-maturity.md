# Versionnement et maturité

## Pourquoi la stabilité est importante

Les URI stables sont essentiels pour la compatibilité des attestations vérifiables. Une attestation émise aujourd'hui doit rester vérifiable des années plus tard. Si un URI change ou disparaît, toute attestation qui le référence devient non résolvable.

## Deux axes de versionnement

"Cet élément est-il sûr à utiliser ?" et "Contre quel instantané est-ce que je construis ?" sont des questions différentes. PublicSchema y répond indépendamment.

![Une version est un instantané hétérogène contenant des entités à différents niveaux de maturité](/images/versioning-axes.svg)

### Maturité par entité

Chaque concept, propriété et valeur de vocabulaire porte un niveau de maturité :

| Niveau | Signification | Ce qui peut changer |
|---|---|---|
| **Brouillon** | Proposé, ouvert aux retours. | Peut être renommé, restructuré ou supprimé. |
| **Usage expérimental** | Suffisamment stable pour les premiers adoptants. | Les changements incompatibles nécessitent un préavis. |
| **Normatif** | Verrouillé. Sûr pour la production. | Les changements nécessitent un nouvel URI. |

La maturité progresse dans un seul sens. Un concept en usage expérimental ne régressera pas au stade de brouillon. Trois niveaux (pas cinq, comme dans le FMM 0-5 de FHIR) correspondent à un modèle mental clair : expérimental, premier adoptant, stable.

La maturité s'applique aux valeurs de vocabulaire individuelles, pas seulement aux vocabulaires. Un vocabulaire normatif peut contenir une valeur en brouillon. Les valeurs en brouillon ne doivent pas apparaître dans les attestations de production.

### Versionnement des versions

Semver sur `_meta.yaml` :

- **Correctif** (0.1.1) : corriger des définitions, ajouter des traductions, corriger des correspondances de systèmes.
- **Mineur** (0.2.0) : ajouter des concepts, des propriétés ou des vocabulaires. Promouvoir des niveaux de maturité.
- **Majeur** (1.0.0) : changements incompatibles pour des entités en usage expérimental ou normatives.

Une version est un instantané hétérogène : la version 0.3.0 peut contenir des entités normatives, en usage expérimental et en brouillon. La version ne dit rien sur la stabilité des entités individuelles ; c'est le champ de maturité qui le fait.

## Comment les éléments évoluent

**L'ajout de valeurs est sûr.** Les consommateurs existants qui ne reconnaissent pas un nouveau code l'ignoreront.

**Renommer ou supprimer des valeurs est une rupture.** Au stade du brouillon : acceptable avec préavis. En usage expérimental : nécessite une période de dépréciation. Au stade normatif : nécessite une nouvelle version du vocabulaire.

**Lors de l'ajout d'un nouveau domaine :**

1. Examinez les vocabulaires universels pour les valeurs qui auraient un sens différent dans le nouveau domaine.
2. Créez des vocabulaires scoped au domaine seulement si nécessaire, pas préventivement.

## Versionnement du contexte

Le contexte JSON-LD est versionné : `ctx/draft.jsonld` pendant la pré-version, puis `ctx/v0.1.jsonld`, `ctx/v1.jsonld`, etc. Les versions antérieures restent résolvables indéfiniment. Dans une version, seuls des changements additifs sont effectués. La suppression ou le renommage d'un terme nécessite une nouvelle version du contexte.

## Persistance des URI

Chaque élément obtient un URI stable :

- Concepts : `https://publicschema.org/Person`, `https://publicschema.org/sp/Enrollment`
- Propriétés : `https://publicschema.org/given_name`
- Vocabulaires : `https://publicschema.org/vocab/gender-type`

Une fois publié en usage expérimental ou au-dessus, un URI ne sera pas supprimé. Les termes dépréciés continuent de se résoudre avec des métadonnées indiquant le remplacement.

## Licence

Le modèle de référence dans `schema/` est sous licence **CC-BY-4.0**. Les outils de construction et les tests sont sous licence **Apache-2.0**.

CC-BY-4.0 a été choisi plutôt que CC0 (qui perd le suivi d'attribution) et CC-BY-SA (dont la clause de partage à l'identique décourage l'adoption par les gouvernements et les intégrateurs commerciaux). L'intégration de l'URL du contexte JSON-LD satisfait à l'exigence d'attribution.
