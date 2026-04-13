# ADR-002: Per-entity maturity plus release versioning

**Status:** Accepted (content merged into `docs/versioning-and-maturity.md`)

## Context

Schema elements (concepts, properties, vocabularies) evolve at different rates. `Person` might be stable while `AssessmentFramework` is still experimental. A single version number for the whole schema would force everything to the same stability guarantee and make it impossible to signal which parts are safe for production use.

At the same time, adopters need to pin to a specific, citable snapshot of the vocabulary. "I'm using PublicSchema" is not precise enough; "I'm using PublicSchema 0.3.0" is.

These are two different questions: "is this concept safe to use?" (per-entity maturity) and "which snapshot am I building against?" (release version). Both schema.org and FHIR solve this by maintaining both axes independently.

## Decision

Two orthogonal versioning axes:

### 1. Per-entity maturity (what is safe?)

Three levels, inspired by FHIR's maturity model:

- **draft:** Experimental. May change without notice.
- **candidate:** Stable enough for early adopters. Breaking changes require a deprecation notice.
- **normative:** Locked. Breaking changes require a new URI.

### 2. Release versioning (what snapshot?)

Semver applied to the vocabulary as a whole (`_meta.yaml` version field):

- **Patch** (0.1.1): fix definitions, add translations, fix system mappings.
- **Minor** (0.2.0): add new concepts, properties, or vocabularies. Promote entity maturity levels.
- **Major** (1.0.0): reserved for when normative content exists. Breaking changes to candidate or normative entities require a major bump.

A release is a heterogeneous snapshot: version 0.3.0 may contain 5 normative concepts, 12 candidate, and 8 draft. The release version says nothing about individual entity stability; the maturity field does.

The JSON-LD context URL tracks releases: `ctx/draft.jsonld` during pre-release, then `ctx/v0.1.jsonld`, `ctx/v1.jsonld`, etc. Older context versions remain resolvable indefinitely.

## Alternatives considered

- **Semver only (no per-entity maturity):** Treats the schema as a monolith. Adding a draft concept bumps a minor version, implying stability guarantees the new concept does not deserve.
- **Maturity only (no release version):** Adopters cannot pin to a snapshot. "Use the latest" is not an integration strategy.
- **Five maturity levels (FHIR FMM 0-5):** More granular but harder for non-technical contributors to reason about. Three levels maps to a clear mental model: experimental, early adopter, stable.
- **Schema.org-style sequential labels (26.0, 27.0):** Schema.org's release numbers carry no semantic guarantees. Semver communicates breaking vs. non-breaking changes in the version number itself, which is more useful for integrators.

## Consequences

Each entity carries its own stability promise via maturity. Each release is a citable, pinnable snapshot via semver. Draft items can be added in a minor release without affecting normative items. Credential issuers can select only normative elements for production use. Integrators pin to a release version and upgrade deliberately.
