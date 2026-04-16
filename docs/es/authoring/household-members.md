# Miembros del hogar

Los formularios de encuestas de hogares a menudo necesitan enumerar a los miembros del hogar y capturar el rol de cada miembro. PublicSchema modela esto a través de GroupMembership, la unión muchos-a-muchos entre Person y Group (incluyendo Household).

## Estructura

```
Household (Group)
  └─ GroupMembership
       ├─ member: Person
       ├─ role: "head" | "spouse" | "child" | "dependent" | ...
       └─ relationship_type: (vocabulario: relationship-type)
```

Cada persona en el hogar tiene un registro GroupMembership que la vincula al Household con un rol.

## Propiedades clave

| Propiedad | En | Propósito |
|---|---|---|
| `role` | GroupMembership | El rol estructural del miembro en el grupo (jefe, cónyuge, hijo/a, dependiente, otro) |
| `relationship_type` | GroupMembership | La relación del miembro con el jefe del hogar (vocabulario: `relationship-type`) |
| `member` | GroupMembership | Referencia al registro Person |

## Notas para autores de formularios

- **No modelar los miembros como una lista plana en Household.** La unión GroupMembership lleva datos de rol y relación que un simple arreglo `members: Person[]` no puede llevar.
- **Un GroupMembership por persona por hogar.** Si una persona pertenece a múltiples grupos (por ej. un Household y una Farm), tiene registros GroupMembership separados para cada uno.
- **El jefe es un rol, no un campo separado.** No hay propiedad `household_head` en Household. El jefe es el miembro cuyo GroupMembership tiene `role: head`.
- **La relación es con respecto al jefe.** La propiedad `relationship_type` en GroupMembership describe la relación del miembro con el jefe del hogar (por ej. cónyuge, hijo/a, padre/madre), siguiendo la convención utilizada por DHS, MICS y la mayoría de los instrumentos censales nacionales.

## Véase también

- [Concepto GroupMembership](../../schema/concepts/group-membership.yaml)
- [Concepto Household](../../schema/concepts/household.yaml)
- [Vocabulario relationship-type](../../schema/vocabularies/relationship-type.yaml)
