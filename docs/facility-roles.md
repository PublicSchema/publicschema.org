# Facility responsibilities and addresses

Use `AssetPartyRole` for an independently needed assertion about who owns, operates
or maintains physical premises. Keep the facility's identity separate from each
actor and from its institutional provider. A school campus can change operator
without becoming another campus; the same applies to agricultural premises and a
hospital estate.

This is a draft cross-sector use of the existing physical-asset relationship.
`School`, `HealthFacility` and `AgriculturalFacility` retain their distinct
meanings. A `Farm` is an economic production unit, and a `ProviderSite` can be
virtual. Neither becomes a physical asset merely because it has an operator or
an address.

## State the responsibility

The example binds `asset_role_type` to the synthetic scheme
`https://example.org/facility-roles/role-types`:

| Code | Meaning in this example | Does not establish |
| --- | --- | --- |
| `owner` | The actor holds ownership of the identified physical asset. | Land title, ownership of the institutional provider, or facility operation. |
| `operator` | The actor runs the identified premises for their operational purpose. | Ownership, premises upkeep, school governance, or agricultural holder responsibility. |
| `upkeep` | The actor is responsible for provisioning and maintaining the premises. | The identity of the service provider or owner. |

Use a separate assertion for each responsibility even when one actor has several.
The example's codes are local profile content, not a new universal closed
vocabulary. An implementing scheme must publish its meanings and keep its URI
with the code. An unqualified word such as `manager` does not resolve these
distinctions.

`asset_actor` retains its Person or Organization meaning, including appropriate
institutional subtypes. It does not acquire every subtype of Agent or Party.
An agricultural facility's existing `facility_operator` snapshot also permits a
group. The example therefore preserves an InformalGroup-operated nursery using
that snapshot and rejects the group as an AssetPartyRole actor. A dated group
asset responsibility needs an explicit draft refinement or another scoped
relationship; do not recast the group as an Organization to pass this profile.

## Keep addresses separate

`AssetAddressAssignment` associates a physical asset with an Address during a
period. It uses `asset_subject`, `assigned_address`, optional `address_geometry`,
`address_purpose`, `start_date` and `end_date`. Address, geometry, named geographic
Location and the physical facility remain separately identified subjects.

The example uses `physical` and `postal` in the synthetic scheme
`https://example.org/facility-roles/address-purposes`. A postal change does not
assert that the facility moved. Geometry is optional and remains an explicit
SpatialGeometry, including its encoding and coordinate reference system. The
example's school keeps its physical address and geometry while its mailing box
changes a month after its operator changes.

The former health-only `FacilityAddressAssignment` is replaced by this shared
assignment. It requires a reviewed address purpose when migrating an old
exchange. The [relationship date migration guide](/docs/relationship-date-migration/)
describes the field and date changes. It does not infer physical versus postal
purpose from address text.

## Read the synthetic journeys

`examples/facility-roles/records.json` contains three estate histories:

| Journey | Change | Independently preserved assertions |
| --- | --- | --- |
| Riverside school campus | One EducationProvider replaces another as premises operator on 1 July 2026. Its postal address changes on 1 August. | The campus, public owner, maintenance organization, physical address and geometry retain their identities. A separate ProviderSite links educational delivery to the campus; another ProviderSite is entirely virtual. |
| Grain drying and storage premises | One Person replaces another as warehouse operator on 1 March 2026. The postal address changes on 1 April. | The premises retain their identity. A ProducerOrganization has separately identified owner and upkeep assertions. The Farm and its holder responsibility remain separate. |
| East hospital premises | The organization maintaining the estate changes on 1 September 2026. | The physical HealthFacility, institutional hospital operator and public estates owner remain separate and unchanged. |

Two ServiceCapacityObservation records also describe 160 staffed learning places
at the school and 42 staffed beds at the hospital, each at an explicit observation
time. Both retain their local measure scheme and a QuantityValue with UCUM unit
`1`. The observations refer to the separately identified physical facilities,
not their provider organizations. These dated counts do not establish current
availability, accreditation or a mapping to a FHIR resource.

The hospital example answers a cross-sector estate question. Medical exchange
should preserve the selected native FHIR resources and their source identities.
FHIR R5 `Location.managingOrganization` identifies the organization responsible
for premises provisioning and upkeep. It is a single optional reference, without
a responsibility period on that element. A dated AssetPartyRole is therefore
not an exact substitute. An operator or owner code must not be mapped there by
its label alone. See the [FHIR R5 Location definition](https://hl7.org/fhir/R5/location-definitions.html#Location.managingOrganization)
and [FHIR integration guidance](/docs/fhir-registry-integration/).

FHIR addresses already have a period of use. An independently needed asset
address assertion does not require duplicating a native medical address fact,
and the assignment itself is not a FHIR Address. Preserve the selected source
representation and compare interval semantics explicitly before projecting
dates. See [FHIR R5 Address.period](https://hl7.org/fhir/R5/datatypes-definitions.html#Address.period).

## Run the example

From the repository root:

```bash
uv run --locked python examples/facility-roles/validate_profile.py
uv run --locked pytest tests/test_facility_roles.py
```

This submission profile requires locally resolved facility and actor URIs and a
declared role or address-purpose code. It deliberately admits the concrete
facility and actor types listed in `validate_profile.py`. Additional types and
source schemes require a profile decision; URI syntax alone cannot establish
that a target is a physical facility or an allowed actor. The example uses
identified, top-level records for references and does not fetch remote URIs.

For the example, `start_date` includes its calendar day and `end_date` is the
first inactive day. A former role ending on 1 July and its replacement starting
on 1 July do not overlap. A nonempty interval is required when both dates are
known. Missing dates remain unknown, and `effective_on` returns an unknown result
where those missing bounds prevent an affirmative answer. No uniqueness rule is
imposed on simultaneous actors or roles; exclusivity needs an applicable source
rule.

The tests validate the same records through generated JSON Schema and
context-expanded SHACL, then apply the example profile. They also show that a
well-formed URI pointing to an InformalGroup passes the vocabulary's URI-shaped
asset actor field but fails the profile's Person/Organization rule. Typed address
and geometry references have separate SHACL checks. These are local executable
examples, not Registry Stack runtime enforcement or an adopter conformance claim.
