# Conception du schéma

## 1. Conventions de nommage

La casse encode le type d'élément :

| Type d'élément | Convention | Exemples |
|---|---|---|
| Concepts | PascalCase | Person, Enrollment, GroupMembership |
| Propriétés | snake_case | given_name, date_of_birth |
| Codes de valeurs de vocabulaire | snake_case | never_married, bank_transfer |
| Identifiants de vocabulaire | kebab-case | gender-type, enrollment-status |

Appliqué par des validateurs regex dans les schémas JSON. Une fois qu'un nom est publié en usage expérimental ou au-dessus, il ne peut plus être modifié.

## 2. URI scoped par domaine

Certains concepts partagent un nom entre domaines mais portent une sémantique différente ("Enrollment" en protection sociale et en éducation). Les éléments spécifiques à un domaine obtiennent un segment de domaine dans leur URI ; les éléments universels se trouvent à la racine :

- `publicschema.org/sp/Enrollment` (protection sociale)
- `publicschema.org/Person` (universel)

Le test : un élément est universel si la même définition porte le même sens quel que soit le domaine. Dans le cas contraire, il appartient à un espace de noms de domaine.

Les noms ne sont jamais préfixés par une abréviation de domaine. C'est `Enrollment`, pas `SPEnrollment`. La structure des URI gère la désambiguïsation.

| Code | Domaine | Statut |
|---|---|---|
| `sp` | Protection sociale | Actif |
| `edu` | Éducation | Futur |
| `health` | Santé | Futur |
| `crvs` | Enregistrement des faits d'état civil et statistiques de l'état civil | Futur |

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

## 5. Contexte temporel

Presque tout dans la prestation de services publics est borné dans le temps. Un instantané de statut sans période de validité est incomplet. Lors de la conception d'un concept ou d'une propriété, demandez-vous : cette valeur changera-t-elle au fil du temps ? Si oui, modélisez explicitement le contexte temporel (dates de début/fin, périodes de validité).

## 6. Indépendance des propriétés

Une propriété comme `start_date` est définie une seule fois et réutilisée entre concepts. Lorsqu'une propriété partagée nécessite des ensembles de valeurs spécifiques à un concept (par exemple, `status` sur Inscription et Réclamation), elle se spécialise via des références de vocabulaire différentes plutôt que de prétendre que les différences n'existent pas.

## 7. Annotations de sensibilité

Certaines propriétés révèlent des circonstances sensibles que la personne soit identifiable ou non. `program_ref` révèle l'inscription à un programme spécifique (qui peut cibler le VIH, le handicap ou la pauvreté). `grievance_type` révèle que quelqu'un a déposé une réclamation.

| Niveau | Quand l'utiliser | Ce qu'il signale |
|---|---|---|
| `standard` | Par défaut. Aucun traitement spécial au-delà de la protection normale des données. | Peut être omis (supposé absent). |
| `sensitive` | Révèle des circonstances (santé, pauvreté, victimisation) dans la plupart des contextes. | Nécessite une justification pour collecter ou divulguer. |
| `restricted` | Ne devrait pas apparaître dans les attestations aux points de service courants. | Nécessite une analyse d'impact sur la protection des données. |

C'est un avertissement pour les praticiens, pas une étiquette de conformité. Le fait qu'une propriété constitue une donnée personnelle dépend de l'enregistrement dans lequel elle apparaît, pas de la propriété elle-même. Consultez [Divulgation sélective](../selective-disclosure/) pour la classification au niveau de l'attestation.
