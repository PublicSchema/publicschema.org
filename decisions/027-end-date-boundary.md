# ADR-027: The end date is the last day a period applies

**Status:** Accepted

## Context

`start_date` and `end_date` are normative and are used by 26 classes, including GroupMembership, Relationship, the relationship classes added for government registries and `metrics/Period`. Release 0.3.0 defined `end_date` as "the date on which this ceased to be effective" and recorded it as an exact match to schema.org `endDate`. The definition does not say whether a period includes its end date.

The two readings differ by one day. A membership whose last day is 30 June has `end_date` 30 June under one reading and 1 July under the other. When datasets that use different readings are merged, periods overlap or leave gaps, and the RDF cannot show which reading a producer used.

Data exchange standards mostly include the end date:

- [FHIR `Period`](https://hl7.org/fhir/R5/datatypes-definitions.html#Period) says of its end: "The boundary is inclusive."
- [DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) describes temporal coverage as a closed interval, and its example quarter runs from 2011-07-01 to 2011-09-30.
- [GTFS](https://gtfs.org/documentation/schedule/reference/#calendartxt) says of a calendar `end_date`: "This service day is included in the interval."
- OCDS guidance completes a date-only end with the last second of that day.
- schema.org does not define the boundary of `endDate`, but its examples, such as a Role spanning 1979 to 1992, read as inclusive.

Calendar and database formats exclude it: [iCalendar `DTEND`](https://www.rfc-editor.org/rfc/rfc5545) is a "non-inclusive end", and PostgreSQL normalizes date ranges to `[start, end)`. Exclusive ends make adjacent periods share a date, which suits storage and arithmetic. Popolo, BODS and Wikidata use wording like the 0.3.0 definition and leave the boundary open.

Within PublicSchema, `valid_from` and `valid_to` already name the first and last applicable days. The example profiles, the relationship date conversion guide and its helper, added after 0.3.0 and not yet released, read `end_date` as exclusive and converted an inclusive `valid_to` by adding one day.

## Decision

1. **`end_date` is the last day on which the period applies.** A period includes both its `start_date` and its `end_date`, so a period that applies only on 30 June 2026 has `start_date` 2026-06-30 and `end_date` 2026-06-30. The definition states this in English, Spanish and French.
2. **This clarifies the existing definition; it does not replace it.** The URI stays `https://publicschema.org/end_date`. The inclusive reading agrees with the exact schema.org match published in 0.3.0 and with the standards adopters most often map to.
3. **schema.org `endDate` stays an exact match, and the context keeps its `endDate` alias.** `startDate` keeps its exact match and alias too.
4. **`metrics/Period` follows the same rule.** Calendar year 2024 runs from 2024-01-01 to 2024-12-31, as a FHIR `Period` or a DCAT temporal coverage states it.
5. **Both date pairs share one convention.** `start_date`/`end_date` and `valid_from`/`valid_to` include their end day. They stay distinct properties with different meanings, but converting an inclusive source `valid_to` to `end_date` keeps the date. The [relationship date conversion guide](../docs/relationship-date-migration.md) still requires confirming the source boundary first.

## Alternatives considered

- **Define `end_date` as the first day the period no longer applies.** Rejected. It matches iCalendar and database ranges, and adjacent periods share a date. But it disagrees with FHIR, DCAT, GTFS and common schema.org usage, would demote the published schema.org mapping to a close match and drop the `endDate` alias, and would make every conversion from an inclusive source add a day.
- **Keep the definition and document the reading only in guides.** Rejected. The published definition is what adopters read, and the ambiguity is the cause of the off-by-one merges.
- **Mint a new URI for an explicitly inclusive end date.** Rejected. The [versioning policy](../docs/versioning-and-maturity.md) requires a new URI when a normative meaning changes. This decision states the reading that the released schema.org mapping already implies, and a new URI would replace the property on every class, example and profile.

## Consequences

A producer that followed the unreleased exclusive guidance and recorded the first inactive day in `end_date` must subtract one day. The example profiles, data, helper and guides use the inclusive reading.

Adjacent periods do not share a date: a period ending on 30 June is followed by one starting on 1 July. A profile that checks for overlap compares whole days, so two periods overlap when one starts on or before the other's end date.

Mapping to FHIR, DCAT, GTFS or schema.org keeps the dates. Mapping to iCalendar or a database range with an exclusive end adds one day to the end.
