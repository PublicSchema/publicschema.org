# ADR-004: Naming conventions as type system

**Status:** Accepted (content merged into `docs/schema-design.md`)

## Context

PublicSchema has three entity types: concepts, properties, and vocabulary values. Contributors need to know which type they are looking at. Validators need to enforce correct naming before names are published and become stable URIs that cannot be changed.

## Decision

Enforce naming conventions via JSON Schema regex patterns:

- **Concepts:** PascalCase (`^[A-Z][a-zA-Z]*$`), e.g. `Person`, `Enrollment`
- **Properties:** snake_case (`^[a-z][a-z0-9_]*$`), e.g. `given_name`, `date_of_birth`
- **Vocabulary value codes:** snake_case (`^[a-z][a-z0-9_]*$`), e.g. `never_married`, `male`
- **Vocabulary identifiers:** kebab-case (`^[a-z][a-z0-9-]*$`), e.g. `gender-type`, `marital-status`

## Alternatives considered

- **Convention without enforcement:** Relies on code review to catch violations. Contributors will inevitably use inconsistent casing, and once a name is published at trial-use or normative, it cannot be changed without breaking adopters.
- **Prefix-based type system (`c_Person`, `p_given_name`):** Clutters names with type tags that add nothing for human readers. The casing convention is immediately recognizable without prefixes.

## Consequences

Names are self-documenting: seeing `Person` tells you it is a concept, `given_name` tells you it is a property, `gender-type` tells you it is a vocabulary identifier. Validators catch naming mistakes before merge. Contributors learn the convention once and apply it everywhere.
