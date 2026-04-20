# ADR-018: Rename CRVSPerson to crvs/Person

**Status:** Accepted

## Context

ADR-014 accepted `CRVSPerson` as a deliberate exception to ADR-003's no-prefix rule. The rationale rested on two claims:

1. CRVS practitioners use "CRVS Person" terminology, making the prefix recognisable.
2. When a CRVS person-of-record and a universal Person appear in the same credential, two identically-named concepts produce prose ambiguity that the URI alone cannot resolve for a human reader.

Both claims remain true, but a technical precondition that made the exception necessary has since been removed.

ADR-014 was authored before the build pipeline distinguished concepts by composite key `(domain, id)`. At that time, the pipeline keyed all concepts by bare `id`. Two concepts with `id: Person` would have silently overwritten each other in the internal vocabulary index. A distinct name (`CRVSPerson`) was therefore a practical necessity, not just a clarity preference.

ADR-003's Wave 0 build-keying refactor (merged prior to the 0.3.0 release cycle) changed the pipeline to key domain-scoped concepts as `{domain}/{id}` and universal concepts as bare `id`. Root `Person` (`publicschema.org/Person`) and `crvs/Person` (`publicschema.org/crvs/Person`) now coexist without collision anywhere in the build, validation, or export pipeline.

With the collision risk gone, the naming exception carries only costs:

- It violates the no-prefix rule that ADR-003 establishes as an explicit design principle.
- It creates an inconsistency visible to every contributor: CRVS domain concepts are `Birth`, `Death`, `Marriage`, `Parent` (clean, unprefixed), but the person-of-record is `CRVSPerson` (prefixed). Explaining why one concept is treated differently adds cognitive load.
- The concept is still `draft` maturity, so no external adopters are pinned to the old URI.
- The disambiguation concern from ADR-014 is addressed structurally: the build and site already render domain-scoped concepts with a `domain:` prefix in the heading and separate them into domain-specific sections in the index.

## Decision

Rename `id: CRVSPerson` to `id: Person` inside `schema/concepts/crvs-person.yaml`. The filename stays `crvs-person.yaml` to avoid a filesystem collision with the universal `schema/concepts/person.yaml`.

The resulting URI is `publicschema.org/crvs/Person`, consistent with how every other CRVS concept is named.

## Consequences

**Schema YAML changes:**

- `schema/concepts/crvs-person.yaml`: `id: CRVSPerson` becomes `id: Person`; label updated from "CRVS Person" to "Person".
- `schema/concepts/parent.yaml`: `supertypes: [CRVSPerson]` becomes `supertypes: [Person]`; trilingual definitions updated to reference `crvs/Person`.
- `schema/properties/party_1.yaml`, `party_2.yaml`, `deceased.yaml`: `type: concept:CRVSPerson` and `references: CRVSPerson` become `concept:Person` and `Person`.
- `schema/bibliography/un-vital-stats-rev3.yaml`: `informs.concepts` list updated.

**Validator change:**

The `build/validate.py` symmetry check was keying `concept_by_id` by bare `id`, causing a collision when both root `Person` and `crvs/Person` are present. The check is updated to use composite keys and resolve bare-id references across all matching concepts.

**Site changes:**

`ConceptsIndex.astro` and `HomePage.astro` add collision-aware label helpers: when a concept's bare `id` is shared by concepts in more than one domain, the domain prefix is shown in link labels and chips (e.g., "crvs: Person"). `ConceptDetail.astro` already shows the `domain:` prefix in the page heading for all domain-scoped concepts.

**Breaking change scope:**

Breaking at the id and URI level for any system that referenced `CRVSPerson` or `publicschema.org/crvs/CRVSPerson`. Because `CRVSPerson` is `draft` maturity (per ADR-002, breaking changes to draft items require no deprecation path), no migration notice is required.

**ADR-003 status:**

ADR-003 remains fully in force. This ADR removes the named exception introduced by ADR-014; it does not weaken or qualify the no-prefix rule. The rule is now consistent across all concepts, including CRVS.

## Supersedes

[ADR-014](014-crvs-person-naming.md)

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- [ADR-003: Domain-scoped URIs, not prefixed names](003-domain-namespacing.md)
- [ADR-014: CRVSPerson as a named exception to the domain-prefix rule](014-crvs-person-naming.md)
