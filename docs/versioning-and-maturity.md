# Versioning and Maturity

## Why stability matters

Stable URIs are essential for Verifiable Credential compatibility. A credential issued today must remain verifiable years from now. If a URI changes or disappears, every credential that references it becomes unresolvable.

## Two versioning axes

"Is this element safe to use?" and "which snapshot am I building against?" are different questions. PublicSchema answers them independently.

![A release is a heterogeneous snapshot containing entities at different maturity levels](/images/versioning-axes.svg)

### Per-entity maturity

Every concept, property, and vocabulary value carries a maturity level:

| Level | Meaning | What can change |
|---|---|---|
| **Draft** | Proposed, open for feedback. | May be renamed, restructured, or removed. |
| **Candidate** | Stable enough for early adopters. | Breaking changes require advance notice. |
| **Normative** | Locked. Production-safe. | Changes require a new URI. |

Maturity progresses in one direction. A concept at candidate will not regress to draft. Three levels (not five, as in FHIR's FMM 0-5) map to a clear mental model: experimental, early adopter, stable.

Maturity applies to individual vocabulary values, not just vocabularies. A normative vocabulary can contain a draft value. Draft values should not appear in production credentials.

### Release versioning

Semver on `_meta.yaml`:

- **Patch** (0.1.1): fix definitions, add translations, fix system mappings.
- **Minor** (0.2.0): add concepts, properties, or vocabularies. Promote maturity levels.
- **Major** (1.0.0): breaking changes to candidate or normative entities.

A release is a heterogeneous snapshot: version 0.3.0 may contain normative, candidate, and draft entities. The release version says nothing about individual entity stability; the maturity field does.

## How things evolve

**Adding values is safe.** Existing consumers that don't recognize a new code will ignore it.

**Renaming or removing values is breaking.** At draft: acceptable with notice. At candidate: requires deprecation period. At normative: requires a new vocabulary version.

**When a new domain is added:**

1. Review universal vocabularies for values that would mean something different in the new domain.
2. Create domain-scoped vocabularies only when needed, not preemptively.

## Context versioning

The JSON-LD context is versioned: `ctx/draft.jsonld` during pre-release, then `ctx/v0.1.jsonld`, `ctx/v1.jsonld`, etc. Older versions remain resolvable indefinitely. Within a version, only additive changes are made. Removing or renaming a term requires a new context version.

## URI persistence

Every element gets a stable URI:

- Concepts: `https://publicschema.org/Person`, `https://publicschema.org/sp/Enrollment`
- Properties: `https://publicschema.org/given_name`
- Vocabularies: `https://publicschema.org/vocab/gender-type`

Once published at candidate or above, a URI will not be removed. Deprecated terms continue to resolve with metadata indicating the replacement.

## Licensing

The reference model in `schema/` is licensed under **CC-BY-4.0**. Build tooling and tests under **Apache-2.0**.

CC-BY-4.0 was chosen over CC0 (loses attribution tracking) and CC-BY-SA (share-alike clause discourages adoption by governments and corporate integrators). Embedding the JSON-LD context URL satisfies the attribution requirement.
