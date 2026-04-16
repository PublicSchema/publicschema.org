# ADR-015: Scalar `identifier` on consent and notice records alongside `identifiers`

**Status:** Accepted

## Context

ADR-005 established `identifiers: Identifier[]` as the single mechanism for record and business references on record-bearing concepts. It explicitly rejected a second scalar row-id slot: "Introduce a distinct concept for row ids (e.g., RecordId) separate from Identifier. Rejected."

ADR-009 introduced `ConsentRecord` and `PrivacyNotice`. Both concepts carry a scalar `identifier: string` property in addition to the multi-valued `identifiers: Identifier[]` list (and, on ConsentRecord, an `external_id`). That scalar `identifier` duplicates the mechanism ADR-005 set as exclusive for record references, so on a plain reading ADR-009 drifts from ADR-005.

The drift was not accidental. The relevant standards for consent and notice artefacts, W3C Data Privacy Vocabulary (DPV) and ISO/IEC TS 27560:2023 (Consent Receipt structure), serialise each receipt with a single top-level identifier. DPV's `dpv:hasIdentifier` predicate expects a single object per artefact; ISO/IEC TS 27560 requires exactly one `consentReceiptID`. A wallet or verifier that deserialises a Consent Receipt VC reads that identifier directly, without scanning a list for the "the receipt id" entry.

Two paths could reconcile the drift:

1. **Migrate ConsentRecord and PrivacyNotice to `identifiers: Identifier[]` only,** introducing a new `identifier-type` value (for example `consent_receipt_id`, `notice_id`) and asking consumers to dereference by type. This is consistent with ADR-005 but mismatches DPV and ISO/IEC TS 27560 serialisation, forcing every consumer that integrates with those standards to wrap and unwrap a one-entry list.
2. **Permit scalar `identifier` on these two concepts** as a named exception justified by standards alignment, while leaving ADR-005 otherwise in force.

## Decision

ADR-005 is amended to permit a scalar `identifier` property on concepts whose canonical external standard requires a single top-level identifier at the root of the serialised artefact. `ConsentRecord` and `PrivacyNotice` qualify under this exception; their scalar `identifier` is retained and is documented as the receipt or notice id as consumed by DPV and ISO/IEC TS 27560 tooling.

The exception is scoped and narrow:

- Applies only when an external standard the concept is designed to serialise into prescribes a single scalar identifier at the artefact root.
- Does not license scalar `identifier` on record-bearing concepts without such a standard.
- `identifiers: Identifier[]` remains available on these concepts for additional scheme-qualified references (for example, internal row ids, replication keys). Scalar `identifier` holds the one reference that maps directly to the standard's serialised field.

## Rationale

DPV and ISO/IEC TS 27560 converge on a single top-level identifier for consent and notice receipts. Forcing a list-wrapped representation in the internal schema and unwrapping it at the serialisation boundary would push the same translation cost into every adopter; keeping the shape the standards expect keeps adopter friction low.

The alternatives have real costs:

- **List-only** (migrate to `identifiers`): every integration must dereference by type, and the standards they integrate with produce a scalar. The indirection adds no information.
- **Scalar only** (remove `identifiers` from these concepts): loses the ability to carry secondary references (internal row ids, replication keys) that adopters have asked for. Rejected.

## Alternatives considered

- **Hold the ADR-005 line and migrate.** Covered above. Rejected on standards-alignment grounds.
- **Scalar `identifier` universally on record-bearing concepts.** Would reintroduce the per-concept row-id slot ADR-005 explicitly rejected. Rejected.
- **Use `identifiers[?identifier_type == 'consent_receipt_id'].identifier_value` everywhere.** Equivalent to option 1. Rejected.

## Consequences

- `schema/concepts/consent-record.yaml` retains `identifier` and `identifiers` side by side; `schema/concepts/privacy-notice.yaml` retains the same pair.
- ADR-005 decision 1 is narrowed: `identifiers` remains the default single mechanism for record and business references, with scalar `identifier` permitted only where a target standard requires it at the root.
- Future record-bearing concepts introduced without a corresponding standards constraint default to `identifiers` only. Adopting a scalar `identifier` on a new concept requires citing the standard it aligns to, either in the concept's definition or in a follow-up ADR.
