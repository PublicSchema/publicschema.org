# Versioning and Maturity

## Why stability matters

Stable URIs are essential for Verifiable Credential compatibility. A credential issued today must remain verifiable years from now. If a URI changes or disappears, every credential that references it becomes unresolvable.

## Maturity levels

Every concept and property in PublicSchema carries a maturity level, inspired by FHIR's maturity model:

| Level | Meaning | What can change |
|---|---|---|
| **Draft** | Proposed, open for feedback. | May change significantly: renamed, restructured, or removed. |
| **Trial use** | Stable enough for early adopters. | Breaking changes are possible with advance notice. |
| **Normative** | Locked. Production-safe. | Changes require a new URI, not an edit to the existing one. |

Maturity progresses in one direction. A concept at "trial use" will not regress to "draft." It either advances to "normative" or is deprecated in favor of a replacement.

## Context versioning

The JSON-LD context is versioned: `https://publicschema.org/ctx/v0.1`, `https://publicschema.org/ctx/v1`, etc. Older versions remain resolvable indefinitely. A system that references `v0.1` will continue to work even after `v2` is published.

Within a context version, only additive changes are made (new terms). Removing or renaming a term requires a new context version.

## URI persistence

Every concept, property, and vocabulary value gets a stable URI. These URIs follow a predictable pattern:

- Concepts: `https://publicschema.org/Person`, `https://publicschema.org/sp/Enrollment`
- Properties: `https://publicschema.org/given_name`, `https://publicschema.org/sp/enrollment_status`
- Vocabularies: `https://publicschema.org/vocab/gender-type`

Once a URI is published at "trial use" or above, it will not be removed. Deprecated terms continue to resolve, with metadata indicating the replacement.
