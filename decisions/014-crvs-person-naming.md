# ADR-014: CRVSPerson as a named exception to the domain-prefix rule

**Status:** Superseded by ADR-018

## Context

ADR-003 states that concept names are never prefixed with a domain abbreviation: a social-protection concept is `Enrollment`, not `SPEnrollment`, because the URI (`publicschema.org/sp/Enrollment`) already carries the domain segment. Adding a domain prefix to the name itself duplicates information and pushes infrastructure concerns into the human-readable identifier.

The CRVS domain adds a concept that subtypes the universal `Person` with vital-registration-specific properties (legal status, civil-status annotations, parent structure). The natural unprefixed name for this subtype is `Person`, but the universal `Person` concept already occupies `publicschema.org/Person`. Candidates considered for the CRVS subtype:

- `Person` (same name, different URI `/crvs/Person`): collides with the root-namespace `Person` when two concepts from different namespaces are referenced in the same context (for example, a CRVS system that also maintains a general Person registry). Two concepts with the same name are ambiguous in prose and in UI.
- `RegisteredPerson`, `CivilPerson`, `VitalSubject`, `PersonSnapshot`: unambiguous unprefixed names, but each introduces a new term not grounded in CRVS practitioner vocabulary.
- `CRVSPerson`: carries the domain abbreviation in the name. Violates ADR-003 for the Person-subtype case specifically.

## Decision

`CRVSPerson` is accepted as a deliberate exception to ADR-003's no-prefix rule, limited to this single case. The full URI remains `publicschema.org/crvs/CRVSPerson`, so the domain segment and the prefixed name coexist.

## Rationale

The exception is acceptable here for three reasons specific to the Person/CRVSPerson pair:

1. **Practitioner recognition.** CRVS systems (OpenCRVS, civil-registration software in multiple countries) already use "CRVS Person" or equivalent phrasing in their data models and documentation. The prefix is not novel in this domain.
2. **Name collision in practice, not just in URI.** Unlike `Enrollment` (where `SPEnrollment` vs `EduEnrollment` coexist only at the URI level and never appear together in a single document), a CRVS record and a universal Person record frequently appear in the same credential (e.g., a civil-status credential that also embeds Person identity claims). Two concepts named `Person` in such a document produce ambiguity that the URI alone cannot resolve for a human reader.
3. **Not a precedent.** The exception is scoped to Person/CRVSPerson; it does not license domain prefixes on any other concept. Future CRVS additions (Birth, Death, Marriage, Parent, etc.) follow ADR-003 unchanged.

ADR-003 otherwise remains in force. Any future proposal to prefix a concept name with a domain abbreviation requires a new ADR citing reasons comparable to those above.

## Alternatives considered

- **Rename the CRVS subtype to an unprefixed term** (`RegisteredPerson`, `VitalSubject`, `PersonSnapshot`): avoids the prefix but introduces terminology that CRVS practitioners do not already use. The readability cost is larger than the cost of the documented exception.
- **Merge CRVSPerson into Person via subtype properties**: collapses two concepts that carry genuinely different property sets (CRVSPerson adds legal_status, civil_status_annotations, parent references, etc. which are meaningless on a non-registered Person) and forces CRVS-only properties onto the universal Person. Rejected.
- **Split CRVS Person-related properties across Person and named CRVS event concepts** (Birth, Death, Marriage): already how vital events are modelled, but the subject of those events still needs a record type that carries registration-specific state distinct from Person. Rejected as insufficient on its own.

## Consequences

- `schema/concepts/crvs-person.yaml` keeps `id: CRVSPerson` and `domain: crvs`, producing URI `publicschema.org/crvs/CRVSPerson`.
- ADR-003 is not superseded; this ADR is a named exception to its no-prefix rule.
- `docs/schema-design.md` and `CLAUDE.md` should cite this ADR at any point that enumerates domain-prefix exceptions, so future contributors do not misread CRVSPerson as a general precedent.
