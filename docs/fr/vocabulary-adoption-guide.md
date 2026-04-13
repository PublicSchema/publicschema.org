# Guide d'adoption du vocabulaire

C'est l'approche la plus simple pour utiliser PublicSchema. Vous alignez les codes et les valeurs de champs de votre système avec le vocabulaire canonique de PublicSchema, sans modifier votre modèle de données, adopter JSON-LD ou émettre des attestations. Le bénéfice : vos données deviennent comparables avec tout autre système qui fait de même.

## Sommaire

- [Quand utiliser cette approche](#quand-utiliser-cette-approche)
- [Étape 1 : Identifier les vocabulaires dont vous avez besoin](#étape-1--identifier-les-vocabulaires-dont-vous-avez-besoin)
- [Étape 2 : Télécharger le vocabulaire](#étape-2--télécharger-le-vocabulaire)
- [Étape 3 : Construire une table de correspondance](#étape-3--construire-une-table-de-correspondance)
- [Étape 4 : Appliquer la correspondance](#étape-4--appliquer-la-correspondance)
- [Ce que vous obtenez](#ce-que-vous-obtenez)
- [Conseils](#conseils)
- [Téléchargements disponibles](#téléchargements-disponibles)
- [Prochaines étapes](#prochaines-étapes)

## Quand utiliser cette approche

Cette approche fonctionne bien lorsque :

- Vous avez besoin d'un rapportage comparable entre programmes, pays ou donateurs
- Vous souhaitez normaliser les codes de réponse des API entre agences
- Vous harmonisez des exports de données provenant de plusieurs systèmes
- Vous souhaitez obtenir des résultats concrets rapidement avant de vous engager dans une intégration plus approfondie

Vous n'avez pas besoin de modifier votre schéma de base de données, vos noms de champs internes ni votre code d'application. Vous n'avez besoin que d'une couche de traduction entre vos codes et les codes canoniques.

## Étape 1 : Identifier les vocabulaires dont vous avez besoin

Parcourez la [page des vocabulaires](/vocab/) pour voir tous les ensembles de valeurs contrôlées disponibles. Points de départ courants :

| Si votre système stocke... | Consultez le vocabulaire... |
|---|---|
| Statut d'inscription (actif, suspendu, etc.) | [enrollment-status](/vocab/enrollment-status/) |
| Statut de paiement (complété, échoué, etc.) | [payment-status](/vocab/payment-status/) |
| Genre | [gender-type](/vocab/gender-type/) |
| Canal de livraison (banque, mobile, espèces) | [delivery-channel](/vocab/delivery-channel/) |
| Type de numéro d'identifiant (numéro d'identité nationale, numéro de passeport, P-code, etc.) | [identifier-type](/vocab/identifier-type/) |
| Type de document d'identité (passeport, carte d'identité nationale, carte de bénéficiaire, etc.) | [document-type](/vocab/document-type/) |
| Pays | [country](/vocab/country/) |
| Devise | [currency](/vocab/currency/) |

Chaque page de vocabulaire affiche les codes canoniques, leurs définitions en anglais, français et espagnol, et la norme internationale qu'ils référencent (ISO, FHIR, etc.).

## Étape 2 : Télécharger le vocabulaire

Chaque page de vocabulaire dispose d'un bouton de téléchargement **CSV**. Le CSV comprend :

| Colonne | Ce qu'elle contient |
|---|---|
| `code` | Le code canonique PublicSchema |
| `label_en` | Libellé en anglais |
| `label_fr` | Libellé en français |
| `label_es` | Libellé en espagnol |
| `standard_code` | Code issu de la norme internationale référencée (le cas échéant) |
| `uri` | URI stable pour la valeur |
| `definition_en` | Définition en anglais |

Vous pouvez également télécharger le vocabulaire en **JSON-LD** pour un accès lisible par machine.

## Étape 3 : Construire une table de correspondance

Comparez les codes de votre système aux codes canoniques et construisez une table de correspondance. Par exemple, si votre système utilise des codes numériques pour le genre :

| Code de votre système | Votre libellé | Code PublicSchema |
|---|---|---|
| `1` | Masculin | `male` |
| `2` | Féminin | `female` |
| `3` | Autre | `other` |
| `9` | Inconnu | `not_stated` |

Quelques points à surveiller :

- **Correspondances un-à-plusieurs.** Votre système peut avoir un seul code là où PublicSchema en a plusieurs. Par exemple, votre système peut utiliser "inactive" à la fois pour les inscriptions "suspendues" et "terminées". Documentez ces cas et décidez comment les traiter.
- **Valeurs non correspondues.** Votre système peut avoir des valeurs sans équivalent canonique, ou vice versa. Documentez les lacunes ; c'est une information utile même si vous ne pouvez pas les résoudre immédiatement.
- **Différences sémantiques.** Deux codes peuvent sembler identiques mais signifier des choses différentes. Lisez les définitions, pas seulement les libellés. Par exemple, "pending" dans votre système peut signifier "en attente d'approbation" tandis que le code de référence "pending" signifie "en attente de paiement".

## Étape 4 : Appliquer la correspondance

La façon d'appliquer la correspondance dépend de ce que vous cherchez à faire :

**Pour le rapportage :** Ajoutez une colonne à votre export qui traduit les codes internes en codes de référence. Votre modèle de rapport utilise la colonne de référence.

**Pour les réponses d'API :** Ajoutez une couche de traduction qui convertit les codes internes en codes canoniques dans la réponse. Votre base de données interne reste inchangée.

**Pour l'échange de données :** Lors de l'export de données vers un autre système, faites passer les valeurs par votre table de correspondance. Lors de l'import, appliquez la correspondance inverse.

**Pour les tableaux de bord :** Effectuez la correspondance des codes au niveau de la couche de visualisation. Vos requêtes renvoient des codes internes ; le tableau de bord les traduit pour l'affichage.

Dans tous les cas, votre système interne continue d'utiliser ses propres codes. La correspondance est appliquée à la frontière.

## Ce que vous obtenez

Une fois vos codes alignés :

- **Des chiffres comparables entre systèmes.** "Combien d'inscriptions actives ?" signifie la même chose partout.
- **Un échange de données simplifié.** Deux systèmes qui effectuent tous les deux la correspondance vers les codes PublicSchema peuvent échanger des données sans traduction bilatérale de codes.
- **Des lacunes explicites.** Là où les codes de votre système ne correspondent pas à l'ensemble de référence, l'écart est visible et documenté plutôt que masqué dans des traductions improvisées.
- **Une base pour une intégration plus approfondie.** Si vous souhaitez ultérieurement aligner les noms de champs, adopter des schémas JSON ou émettre des attestations, la correspondance de vocabulaire est déjà faite.

## Conseils

- Commencez par un ou deux vocabulaires, pas par tous. Le statut d'inscription et le statut de paiement sont des points de départ courants.
- Si votre système utilise déjà des codes d'une norme internationale (par exemple, ISO 3166 pour les pays), vérifiez si PublicSchema renvoie à la même norme. Si c'est le cas, votre correspondance peut déjà être triviale.
- Les vocabulaires PublicSchema qui référencent des normes internationales incluent le `standard_code` dans le CSV. Vous pouvez effectuer la correspondance via le code de norme si c'est plus facile que via les libellés.
- Certains vocabulaires incluent des correspondances spécifiques à des systèmes dans leurs fichiers source YAML. Consultez la [page des vocabulaires](/vocab/) pour voir si votre système est déjà mis en correspondance.

## Téléchargements disponibles

Chaque page de vocabulaire propose :

| Format | Ce que c'est | Idéal pour |
|---|---|---|
| **CSV** | Fichier plat avec codes, libellés, définitions | Tableurs, pipelines de données, référence rapide |
| **JSON-LD** | Données liées lisibles par machine | Accès programmatique, chaînes d'outils RDF |

Pour le vocabulaire complet (tous les concepts, propriétés et vocabulaires en un seul fichier) :

| Format | URL |
|---|---|
| Vocabulaire complet (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) |
| Vocabulaire complet (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) |

## Prochaines étapes

- Pour aligner les noms de champs (pas seulement les codes), consultez le [Guide d'interopérabilité et de correspondance](/docs/interoperability-guide/).
- Pour concevoir un nouveau système compatible, consultez le [Guide de conception du modèle de données](/docs/data-model-guide/).
- Pour utiliser les contextes JSON-LD et émettre des attestations vérifiables, consultez le [Guide JSON-LD et VC](/docs/jsonld-vc-guide/).
