# Membres du ménage

Les formulaires d'enquête auprès des ménages doivent souvent énumérer les membres du ménage et capturer le rôle de chaque membre. PublicSchema modélise cela via GroupMembership, la jointure plusieurs-à-plusieurs entre Person et Group (y compris Household).

## Structure

```
Household (Group)
  └─ GroupMembership
       ├─ member: Person
       ├─ role: "head" | "spouse" | "child" | "dependent" | ...
       └─ relationship_type: (vocabulaire : relationship-type)
```

Chaque personne du ménage a un enregistrement GroupMembership la reliant au Household avec un rôle.

## Propriétés clés

| Propriété | Sur | Objectif |
|---|---|---|
| `role` | GroupMembership | Le rôle structurel du membre dans le groupe (chef, conjoint, enfant, personne à charge, autre) |
| `relationship_type` | GroupMembership | La relation du membre avec le chef de ménage (vocabulaire : `relationship-type`) |
| `member` | GroupMembership | Référence à l'enregistrement Person |

## Notes pour les auteurs de formulaires

- **Ne pas modéliser les membres comme une liste plate sur Household.** La jointure GroupMembership porte les données de rôle et de relation qu'un simple tableau `members: Person[]` ne peut pas porter.
- **Un GroupMembership par personne par ménage.** Si une personne appartient à plusieurs groupes (par ex. un Household et une Farm), elle a des enregistrements GroupMembership distincts pour chacun.
- **Le chef est un rôle, pas un champ séparé.** Il n'y a pas de propriété `household_head` sur Household. Le chef est le membre dont le GroupMembership a `role: head`.
- **La relation est par rapport au chef.** La propriété `relationship_type` sur GroupMembership décrit la relation du membre avec le chef de ménage (par ex. conjoint, enfant, parent), suivant la convention des EDS, MICS et de la plupart des instruments de recensement nationaux.

## Voir aussi

- [Concept GroupMembership](../../schema/concepts/group-membership.yaml)
- [Concept Household](../../schema/concepts/household.yaml)
- [Vocabulaire relationship-type](../../schema/vocabularies/relationship-type.yaml)
