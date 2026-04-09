# ADR-001: CC-BY-4.0 for vocabulary, Apache-2.0 for code

**Status:** Accepted

## Context

PublicSchema needs a license model. Vocabulary definitions (concepts, properties, vocabularies in `schema/`) are reference content that should be freely adoptable by governments, NGOs, and private implementers. Build tooling and tests are software.

## Decision

CC-BY-4.0 for vocabulary content, Apache-2.0 for code.

## Alternatives considered

- **CC0 (public domain dedication):** Removes attribution entirely. We lose the ability to track adoption, provenance, or credit contributions from domain experts.
- **CC-BY-SA (share-alike):** The SA clause scares corporate adopters who embed vocabulary terms in proprietary systems. Government agencies may also avoid SA due to procurement policy constraints that require clean IP chains.
- **Single Apache-2.0 for everything:** Apache is a software license and is an awkward fit for reference data. It is designed around source code distribution, not conceptual definitions.

## Consequences

Adopters can embed vocabulary terms freely as long as they credit PublicSchema. Attribution is lightweight: embedding the JSON-LD context URL in a credential or dataset satisfies the requirement. Code contributions (build scripts, validators, site) are covered by a well-understood OSS license with patent termination provisions.
