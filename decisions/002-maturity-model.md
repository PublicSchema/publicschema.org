# ADR-002: FHIR maturity levels, not semver

**Status:** Accepted

## Context

Schema elements (concepts, properties, vocabularies) evolve at different rates. `Person` might be stable while `AssessmentFramework` is still experimental. A single version number for the whole schema would force everything to the same stability guarantee and make it impossible to signal which parts are safe for production use.

## Decision

Three per-entity maturity levels (draft, trial-use, normative), inspired by FHIR's maturity model.

- **draft:** Experimental. Interface may change without notice.
- **trial-use:** Stable enough for early adopters. Breaking changes require a deprecation notice.
- **normative:** Stable. Breaking changes require a new URI.

## Alternatives considered

- **Semver per release:** Treats the schema as a monolith. Adding a draft concept would bump a minor version, implying stability guarantees the new concept does not deserve. Adopters would have no way to know which parts of a release are solid.
- **Five levels (FHIR FMM 0-5):** More granular but harder for non-technical contributors to reason about. Three levels maps to a clear mental model: experimental, early adopter, stable.

## Consequences

Each entity carries its own stability promise. Draft items can be added without affecting normative items. Credential issuers can select only normative elements for production use while still exploring draft elements in staging.
