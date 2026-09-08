# ADR-003: Domain-scoped URIs, not prefixed names

**Status:** Accepted (content merged into `docs/schema-design.md`)

## Context

PublicSchema covers multiple domains (social protection, education, health). Some concepts share a name across domains but carry different semantics. "Enrollment" in social protection means admission to a benefit program; in education it means registration at a school. These are related but not the same concept and should not share a URI.

## Decision

Domain-specific concepts get a domain segment in their URI (`publicschema.org/sp/Enrollment`), not a prefixed name (`SPEnrollment`). Universal concepts that are the same across domains live at the root (`publicschema.org/Person`).

## Alternatives considered

- **Prefixed names (`SPEnrollment`, `EduEnrollment`):** Pollutes the name with infrastructure concerns. Policy officers reading a credential see `SPEnrollment` and wonder what "SP" means. It also makes names verbose without adding information for the reader.
- **Separate schemas per domain:** Duplicates universal concepts (Person, Location) across schemas. Every domain would define its own Person, and those definitions would diverge over time, creating interoperability problems across domains.
- **Flat namespace with collision resolution:** Works until two domains need the same name with different semantics, then breaks in ways that are hard to fix after publication.

## Consequences

Concept names stay clean and human-readable. The URI structure handles disambiguation. Adding a new domain does not require renaming existing shared concepts.

[ADR-025](025-domain-and-external-model-boundaries.md) clarifies the authoring rule: choose property and vocabulary namespaces by meaning, not by current concept usage. Their public identities must not move when another domain reuses them. Explicit authored property URIs own renderer placement; usage-based inference remains only a compatibility fallback for older sources without those URIs. Candidate and normative identities are preserved.
