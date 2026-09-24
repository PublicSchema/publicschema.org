# Converting source relationship dates

The relationships named below use `start_date` and `end_date`, following the
[relationship convention](/docs/schema-design/#5-temporal-context). Source records
that carry a `valid_from` and `valid_to` pair for them usually describe
inclusive calendar validity. Renaming the keys without changing the end boundary would change the last effective day.

The published definitions use whole calendar days: `start_date` is included and
`end_date` is the first inactive day ([ADR-027](../decisions/027-end-date-boundary.md)).
These fields are not timestamps and do not describe the time a source recorded a fact.

## Relationships that use start and end dates

| Relationship | What the dates bound |
| --- | --- |
| HoldingParcelLink | The period during which a holding uses a parcel. |
| AnimalResidence | The period during which an animal or group is kept at the identified agricultural site. |
| AnimalResponsibility | The period of the stated keeper, owner or other responsibility. |
| AgriculturalServiceRole | The period of acting as the described service provider. |
| IdentifierAssignment | The period of an identifier's assignment to the subject. |
| NameUsage | The period of using the name for the subject in its stated context. |
| ContactPoint | The period of using the communication channel to reach the subject. |
| AssetPartyRole | The period of the stated responsibility for a physical asset. |
| AssetAddressAssignment | The period during which the address applies to the asset for its stated purpose. |

RegistryEntry and Registration keep inclusive `valid_from`/`valid_to`, including
registration and authorization specializations. AgriculturalParcel keeps its
description validity; Certification and LandTenureAssertion keep
their certification or substantive legal validity. Do not convert these
because a relationship concerning the same subject is converted. `recorded_at` also stays unchanged.

## Preserve every effective day

Only after establishing that the source uses inclusive whole calendar days:

1. Copy a present `valid_from` unchanged to `start_date`.
2. Convert a present `valid_to` to the following calendar day as `end_date`.
3. Remove the source keys. Preserve each omitted bound as omitted.

For example:

```json
{"@type":"AgriculturalServiceRole","valid_from":"2026-12-31","valid_to":"2026-12-31"}
```

becomes:

```json
{"@type":"AgriculturalServiceRole","start_date":"2026-12-31","end_date":"2027-01-01"}
```

Both describe one effective day. Likewise, an inclusive leap-day end of
29 February 2024 becomes cessation on 1 March 2024. A missing end remains unknown;
it is not replaced with a maximum date or treated as proof of perpetual validity.
Unknown precision, partial dates, timestamps and unspecified boundary conventions
require source clarification. `9999-12-31` has no representable following day in
the supported calendar and must not silently become a missing end.

## Interpret source facility assignments

Source records often say only that an organization manages a facility, without
distinguishing running the premises from their upkeep or ownership. Inspect the
source evidence before selecting a role code, with its scheme, for AssetPartyRole.
Map the facility to `subject_uri` and the organization to `asset_actor`, with an
explicit `asset_role_type`. Preserve the physical subject identity. If the
evidence establishes several responsibilities, represent distinct assertions and
retain their source links. Do not invent those responsibilities or claim that a
generic management statement proves them.

For a source record assigning an address to a facility:

| Source fact | AssetAddressAssignment |
| --- | --- |
| The facility | `subject_uri`, referring to the physical facility |
| The address | `assigned_address`, preserving the Address |
| A position or geometry on the assignment | No field on the assignment; record a position on the Address `location` or the asset's `spatial_geometry` |
| No explicit purpose | Add source-supported `address_purpose` as a CodedValue, retaining its scheme. |

Choosing the role or address purpose is a semantic step that the helper does not
perform. It converts the dates on an AssetPartyRole or AssetAddressAssignment only
after the asset, its party or address, and a scheme-qualified role or purpose
code are present. A code's presence does not prove its source evidence; that
remains the implementer's responsibility.

For medical facts already represented in native FHIR, preserve that selected
representation. A shared estate assertion has a purpose only when consumers
independently need it. See [facility responsibilities and addresses](/docs/facility-roles/).

## Use the bounded helper

The standard-library helper reads one JSON document and writes a complete result
to standard output. It does not rewrite its input or use the vocabulary build as
a conversion framework. It expects records already mapped to the PublicSchema
types above that still carry the source's `valid_from`/`valid_to`. First inspect
the source contract, then run from the repository root:

```bash
uv run --locked python examples/relationship-date-migration/migrate.py \
  --source-boundary inclusive-calendar-days \
  examples/relationship-date-migration/source-records.json
```

Compare the result with `examples/relationship-date-migration/records.json`.
When saving your own result, select a different output file from the input. The
input carries source date keys and must not be validated as a PublicSchema
relationship payload before conversion.

The Python entry point is
`migrate_relationship_dates(document, source_boundary="inclusive-calendar-days")`.
It returns a deep copy. Passing the result through again is idempotent and does
not require a source-boundary declaration when no source validity dates remain. Any
diagnostic raises MigrationError; the CLI emits JSON diagnostics on standard
error, exits with status 2 and emits no partial document on standard output.
Paths use JSON Pointer escaping. The original argument and input file remain
unchanged on both success and failure.

The helper accepts each relationship's compact `@type` alias and its exact
PublicSchema identifier, as a `publicschema:` compact IRI or absolute URI.
HoldingParcelLink, AnimalResidence and AgriculturalServiceRole are in the `agri/`
domain; the other relationships are at root. Type identifiers are preserved. An
arbitrary namespace with the same local name is rejected, as are multiple types
involving these relationships. Context alias interpretation and expanded JSON-LD
require a separate adapter. Other classes, including source record types not yet
mapped to PublicSchema, keep their original dates.

Mixed source and current date pairs are rejected even when they appear to agree.
Reconcile them from the source. Exact impossible dates, reversed or empty
effective intervals, unsupported precision and end-date overflow have distinct,
deterministic field diagnostics.

Run the focused checks:

```bash
uv run --locked pytest tests/test_relationship_date_migration.py
```

Tests compare effective-day membership across conversion, including month, year,
leap-day and single-day cases. They cover unknown boundaries, unsupported class
identifiers, facility assignment meaning, omitted bounds, idempotence and
atomic failure. Converted fixtures are also checked against the real generated
JSON Schema and context-expanded SHACL outputs. The generated class hierarchy is
checked for descendants of every converted relationship, so an affected subtype
cannot silently fall outside the helper's admitted types. The vocabulary's optional fields
do not by themselves enforce every profile rule.
