# Conception du vocabulaire

Règles pour les vocabulaires contrôlés. S'appuie sur [Conception du schéma](../schema-design/).

## 1. Universel par défaut, scoped par domaine par exception

Un vocabulaire se trouve à la racine sauf si les mêmes codes porteraient des significations différentes selon les domaines.

Exemples :

- `payment-status` est universel. "Paid" signifie la même chose en protection sociale, en santé et en éducation.
- `targeting-approach` est spécifique à un domaine. "Proxy means testing" est une méthodologie de protection sociale sans équivalent dans d'autres domaines.
- `severity` est ambigu. En alerte d'urgence, il désigne l'impact d'un danger ; en santé, il désigne la progression d'une maladie. Désambiguïsez en renommant (`event-severity`) ou en le scoping à un domaine.

Les définitions doivent correspondre à la portée. La définition d'un vocabulaire universel ne doit pas référencer un domaine spécifique. Écrivez "les états du cycle de vie d'une inscription à un programme", pas "...dans un programme de protection sociale."

## 2. Un concept par vocabulaire

Chaque vocabulaire répond à une seule question. Ne combinez pas des préoccupations orthogonales.

- Le statut et le résultat sont des questions différentes. "Où en est ce processus ?" vs "Quel a été le résultat ?"
- Le canal et la modalité sont des questions différentes. "Comment la prestation atteint-elle la personne ?" vs "Sous quelle forme se présente la prestation ?"

Ne divisez pas prématurément. Si un seul vocabulaire capture proprement le cycle de vie et que tous les systèmes mis en correspondance le traitent comme un seul champ, diviser ajoute de la complexité sans bénéfice prouvé.

## 3. Référencer les normes existantes

Si un système de codes formel existe, référencez-le. Trois niveaux :

| Niveau | Quand l'utiliser | Champ YAML |
|---|---|---|
| **Synchronisation** | La norme lisible par machine définit l'ensemble de valeurs faisant autorité. | `standard` + `sync` |
| **Référence** | La norme existe mais nous ne synchronisons pas (prose uniquement, chevauchement partiel, simplification délibérée). | `references` |
| **Aucun** | Aucune norme pertinente n'existe. | Aucun des deux champs |

Un vocabulaire sans `standard`, sans `references` et sans `system_mappings` n'est pas validé. Acceptable au niveau de maturité brouillon ; doit être résolu avant l'usage expérimental.

N'adoptez pas les codes d'une norme lorsqu'ils ne servent pas le public cible. Les codes ISO 20022 (RCVD, ACTC, ACSP) sont destinés aux messages interbancaires. Utilisez des codes lisibles ; effectuez la correspondance vers la norme.

Préférez les normes lisibles par machine aux normes en prose uniquement. Les normes lisibles par machine peuvent être synchronisées automatiquement ; les normes en prose dérivent.

## 4. Annotations de domaine sur les valeurs individuelles

Lorsqu'un vocabulaire universel contient des valeurs qui ne s'appliquent qu'à un domaine, annotez la valeur plutôt que de diviser le vocabulaire :

```yaml
- code: graduated
  domain: sp
  label:
    en: Graduated
  definition:
    en: The beneficiary has exited through program-defined graduation criteria.
```

À utiliser avec parcimonie. Si plus d'un tiers des valeurs portent des annotations de domaine, le vocabulaire devrait être déplacé vers un espace de noms de domaine.

## 5. Désambiguïser les noms sujets à collision

Avant de nommer un vocabulaire, demandez-vous : un autre domaine pourrait-il définir un vocabulaire avec ce nom mais des valeurs différentes ?

- `severity` -> `event-severity`
- `certainty` -> `event-certainty`
- N'utilisez jamais un `status` nu ; qualifiez-le toujours (`enrollment-status`, `payment-status`)

## 6. Le code `other` et les correspondances de systèmes

`other` est acceptable au niveau de maturité brouillon. Suivez ce qui lui correspond dans les déploiements réels. Lorsque la même valeur non correspondante apparaît dans 2 systèmes ou plus, promouvez-la en code nommé.

Les correspondances de systèmes sont le principal mécanisme de validation :

- 3 systèmes ou plus effectuant leur correspondance vers `other` = lacune dans le vocabulaire. Promouvez en code nommé.
- 4 codes système ou plus effectuant leur correspondance vers une seule valeur canonique = le vocabulaire peut être trop grossier.
- Code système effectuant sa correspondance vers `null` alors qu'un code canonique plus large existe = bogue de correspondance.

Un vocabulaire sans correspondances de systèmes n'est pas validé. Ajoutez des correspondances avant de faire progresser la maturité.
