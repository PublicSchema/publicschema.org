# ADR-027: The end date is the first day a period no longer applies

**Status:** Accepted

## Context

`start_date` and `end_date` are normative and are used by 26 classes, including GroupMembership, Relationship, the relationship classes added for government registries and `metrics/Period`. `end_date` was defined as "the date on which this ceased to be effective" and recorded as an exact match to schema.org `endDate`. The definition does not say whether a period includes its end date.

The two readings differ by one day. A membership that ends on 30 June under one reading ends on 1 July under the other. When datasets that use different readings are merged, periods overlap or leave gaps, and the RDF cannot show which reading a producer used. FHIR `Period` defines its end as inclusive, and schema.org `endDate` is commonly used the same way.

The relationship date conversion guide, the schema design guide and the example profiles already use one reading: `start_date` is included and `end_date` is the first inactive day. Their conversion from inclusive `valid_to` adds one day. Until now that reading was stated only in those guides.

## Decision

1. **`end_date` is the first day on which the period no longer applies.** A period includes its `start_date` and ends before its `end_date`, so a period that applies only on 30 June 2026 has `start_date` 2026-06-30 and `end_date` 2026-07-01. The definition states this in English, Spanish and French.
2. **This clarifies the existing definition; it does not replace it.** A date on which something "ceased to be effective" is the first day it is no longer effective, just as the `start_date` it became effective is the first day it is. The URI stays `https://publicschema.org/end_date`. The release notes state the reading so that a producer who used the other one can correct its data.
3. **schema.org `endDate` is a close match, and the context no longer aliases it.** The context alias makes schema.org data using `endDate` expand to `end_date`, which is only safe for an exact match. `startDate` keeps its exact match and alias, because both vocabularies include the start day.
4. **`metrics/Period` follows the same rule.** Calendar year 2024 runs from 2024-01-01 to 2025-01-01. An adapter to a FHIR `Period` or another inclusive format subtracts one day from the end.
5. **`valid_from` and `valid_to` are unchanged.** They name the first and last applicable calendar dates and remain inclusive. The [relationship date conversion guide](../docs/relationship-date-migration.md) describes the conversion between the two pairs.

## Alternatives considered

- **Define `end_date` as the last day of the period.** Rejected. It matches FHIR and common schema.org usage, but it contradicts the guides, profiles and conversion tool already published. Adjacent periods would also need their start dates shifted by one day.
- **Keep the definition and document the reading only in guides.** Rejected. The published definition is what adopters read, and the ambiguity is the cause of the off-by-one merges.
- **Mint a new URI for an explicitly exclusive end date.** Rejected. The [versioning policy](../docs/versioning-and-maturity.md) requires a new URI when a normative meaning changes. This decision states the reading that the existing wording already gives, and a new URI would replace the property on every class, example and profile.
- **Record a close match but keep the `endDate` alias for compatibility.** Rejected. schema.org data would then be read with its end date one day early, without warning.
- **Keep the exact match to schema.org `endDate`.** Rejected. schema.org does not define the boundary, but an exact match would assert that the two properties mean the same, and common usage disagrees.

## Consequences

A producer that recorded the last effective day in `end_date` must add one day to be correct under this definition. The migration guide describes how to do so and when not to.

JSON-LD documents that use the `endDate` key no longer expand it to `end_date`. They must use `end_date`. A consumer mapping schema.org, FHIR or another format with an inclusive end must convert explicitly.

A new class that bounds a period with an inclusive last day uses `valid_from` and `valid_to` or its own named date, not `end_date`.
