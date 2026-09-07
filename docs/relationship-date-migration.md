# Migrating draft relationship dates

The named draft relationships now use `start_date` and `end_date`, following the
[relationship convention](/docs/schema-design/#5-temporal-context). Their former
`valid_from` and `valid_to` pair described inclusive calendar validity. Changing
the keys without changing the end boundary would change the last effective day.

This migration leaves the existing normative date-property definitions intact.
For these migrated draft relationships, the agreed convention is whole calendar
days: `start_date` is included and `end_date` is the first inactive day. These
fields are not timestamps and do not describe the time a source recorded a fact.

## Which concepts change

| Draft relationships or usages | Date change |
| --- | --- |
| HoldingParcelLink | The period during which a holding uses a parcel. |
| AnimalResidence | The period during which an animal or group is kept at the identified agricultural site. |
| AnimalResponsibility | The period of the stated keeper, owner or other responsibility. |
| ProducerMembership | The period of producer-organization membership. Allowed member kinds stay unchanged. |
| AgriculturalServiceRole and its InputSupplierRole, PesticideApplicatorRole and SeedOperatorRole subtypes | The period of acting as the described service provider; every subtype inherits the same date change. |
| IdentifierAssignment | The period of an identifier's assignment to the subject. |
| NameUsage | The period of using the name for the subject in its stated context. |
| ContactPoint | The period of using the communication channel to reach the subject. |

RegistryEntry and Registration retain inclusive `valid_from`/`valid_to`, including
registration and authorization specializations. AgriculturalParcel retains its
description validity; AgriculturalCertification, LandTenureAssertion and
RoadRestriction retain their certification or substantive legal validity. These
are not silently converted when another relationship concerning the same subject
changes. `recorded_at` also stays unchanged.

AssetPartyRole already used `start_date`/`end_date`. AssetAddressAssignment uses
them from its creation. The retired health-only facility assignments need the
semantic review below before their dates can be converted.

## Preserve every effective day

Only after establishing that the source uses inclusive whole calendar days:

1. Copy a present `valid_from` unchanged to `start_date`.
2. Convert a present `valid_to` to the following calendar day as `end_date`.
3. Remove the old keys. Preserve each omitted bound as omitted.

For example:

```json
{"@type":"ProducerMembership","valid_from":"2026-12-31","valid_to":"2026-12-31"}
```

becomes:

```json
{"@type":"ProducerMembership","start_date":"2026-12-31","end_date":"2027-01-01"}
```

Both describe one effective day. Likewise, an inclusive leap-day end of
29 February 2024 becomes cessation on 1 March 2024. A missing end remains unknown;
it is not replaced with a maximum date or treated as proof of perpetual validity.
Unknown precision, partial dates, timestamps and unspecified boundary conventions
require source clarification. `9999-12-31` has no representable following day in
the supported calendar and must not silently become a missing end.

## Review the retired facility meanings

`FacilityManagementAssignment` did not distinguish running premises from their
upkeep. Inspect its source evidence before selecting a scheme-qualified role for
AssetPartyRole. Transform `managed_facility` to `asset_subject` and
`managing_organization` to `asset_actor`, with an explicit `asset_role_type`.
Preserve the physical subject identity. If the evidence establishes several
responsibilities, represent distinct assertions and retain their source links.
Do not invent those responsibilities or claim that the old generic management
assertion proves them.

For an independently needed former FacilityAddressAssignment:

| Former field or class | Reviewed replacement |
| --- | --- |
| `FacilityAddressAssignment` | `AssetAddressAssignment` |
| `addressed_facility` | `asset_subject`, referring to the same physical facility |
| `facility_address` | `assigned_address`, preserving the Address |
| `address_geometry` | Unchanged reference and property URI |
| No explicit purpose | Add source-supported `address_purpose` as a CodedValue, retaining its scheme. |

Choosing the role or address purpose is a semantic step. The helper refuses both
retired class names and does not perform this step. After an implementer has
explicitly transformed the class and endpoint fields and supplied the reviewed
code, it can convert the remaining legacy dates on AssetPartyRole or
AssetAddressAssignment. A code's presence does not prove its source evidence;
that remains the implementer's responsibility.

For medical facts already represented in native FHIR, preserve that selected
representation. A shared estate assertion has a purpose only when consumers
independently need it. See [facility responsibilities and addresses](/docs/facility-roles/).

## Use the bounded helper

The standard-library helper reads one JSON document and writes a complete result
to standard output. It does not rewrite its input or use the vocabulary build as
a migration framework. First inspect the source contract, then run from the
repository root:

```bash
uv run --locked python examples/relationship-date-migration/migrate.py \
  --source-boundary inclusive-calendar-days \
  examples/relationship-date-migration/legacy-records.json
```

Compare the result with `examples/relationship-date-migration/records.json`.
When saving your own result, select a different output file from the input. The
input is a historical fixture and must not be validated as a current relationship
payload before migration.

The Python entry point is
`migrate_relationship_dates(document, source_boundary="inclusive-calendar-days")`.
It returns a deep copy. Passing the result through again is idempotent and does
not require a source-boundary declaration when no legacy dates remain. Any
diagnostic raises MigrationError; the CLI emits JSON diagnostics on standard
error, exits with status 2 and emits no partial document on standard output.
Paths use JSON Pointer escaping. The original argument and input file remain
unchanged on both success and failure.

The helper accepts the named compact authored `@type` values, their historical
root PublicSchema URI forms and the exact new `agri/` catalog identifiers and URIs for
HoldingParcelLink, AnimalResidence, ProducerMembership, AgriculturalServiceRole,
InputSupplierRole, PesticideApplicatorRole and SeedOperatorRole. AnimalResponsibility and the registry assignments remain
at root. Type identifiers are preserved; this tool does not perform namespace
migration. An arbitrary namespace with the same local name is rejected, as are
multiple types involving these concepts. Context alias interpretation and
expanded JSON-LD require a separately reviewed adapter. Unrelated classes retain
their original dates.

Mixed old and current date pairs are rejected even when they appear to agree.
Reconcile them from the source. Exact impossible dates, reversed or empty
effective intervals, unsupported precision and end-date overflow have distinct,
deterministic field diagnostics.

Run the focused checks:

```bash
uv run --locked pytest tests/test_relationship_date_migration.py
```

Tests compare effective-day membership across conversion, including month, year,
leap-day and single-day cases. They cover unknown boundaries, unsupported class
identifiers, explicit facility transformation, omitted bounds, idempotence and
atomic failure. Migrated fixtures are also checked against the real generated
JSON Schema and context-expanded SHACL outputs. The generated class hierarchy is
checked for descendants of every migrated relationship, so an affected subtype
cannot silently fall outside the helper's admitted types. The vocabulary's optional fields
do not by themselves enforce every profile rule.
