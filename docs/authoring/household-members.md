# Household Members

Household survey forms often need to enumerate household members and capture each member's role. PublicSchema models this through GroupMembership, the many-to-many join between Person and Group (including Household).

## Structure

```
Household (Group)
  └─ GroupMembership
       ├─ member: Person
       ├─ role: "head" | "spouse" | "child" | "dependent" | ...
       └─ relationship_type: (vocabulary: relationship-type)
```

Each person in the household gets one GroupMembership record linking them to the Household with a role.

## Key properties

| Property | On | Purpose |
|---|---|---|
| `role` | GroupMembership | The member's structural role in the group (head, spouse, child, dependent, other) |
| `relationship_type` | GroupMembership | The member's relationship to the household head (vocabulary: `relationship-type`) |
| `member` | GroupMembership | Reference to the Person record |

## Form authoring notes

- **Do not model members as a flat list on Household.** The GroupMembership join carries role and relationship data that a simple `members: Person[]` array cannot.
- **One GroupMembership per person per household.** If a person belongs to multiple groups (e.g., a Household and a Farm), they get separate GroupMembership records for each.
- **The head is a role, not a separate field.** There is no `household_head` property on Household. The head is the member whose GroupMembership has `role: head`.
- **Relationship is to the head.** The `relationship_type` property on GroupMembership describes the member's relationship to the household head (e.g., spouse, child, parent), following the convention used by DHS, MICS, and most national census instruments.

## See also

- [GroupMembership concept](../../schema/concepts/group-membership.yaml)
- [Household concept](../../schema/concepts/household.yaml)
- [relationship-type vocabulary](../../schema/vocabularies/relationship-type.yaml)
