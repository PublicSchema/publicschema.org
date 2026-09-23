# Registry foundations

A register, its record and the subject of that record have different identities. `RegistryEntry` uses a register URI and local record ID as its qualified key and an explicit `subject_uri` for the described thing. `Registration` records administrative recognition; `Authorization` adds permission for a stated activity. Neither is the Person, Organization, facility, product or Farm receiving it. These terms are optional reference vocabulary at draft maturity. They are not a registry submission format, a full-domain model or a normative specification.

See the [government families](government-registry.md), [biology](agriculture-biology.md), [agricultural operations](agriculture-operations.md), [facility responsibilities and addresses](facility-roles.md), and [relationship date migration](relationship-date-migration.md) for neighboring concepts. [ADR-020](../decisions/020-registry-foundations.md) records the common choices and alternatives.

## Evidence and design judgment

Definitions are original PublicSchema wording informed by these sources. No source requires these class names, optionality, public URIs or serialization, and none is claimed as a complete interchange mapping.

| Question | Evidence and decision |
| --- | --- |
| Record versus subject | [DCAT 3 Recommendation, 22 August 2024, §§5.6 and 6.5](https://www.w3.org/TR/2024/REC-vocab-dcat-3-20240822/) distinguishes a catalog record from its primary topic. Administrative register records are a broader design application, not exact DCAT CatalogRecord equivalents. `Register`, `RegistryEntry`, and `RecordReference` retain those separate identities. `subject_uri` is close to `foaf:primaryTopic`. |
| Register responsibility and lifecycle | [INSPIRE register guidance, v1.0, 31 May 2017](https://knowledge-base.inspire.ec.europa.eu/publications/best-practices-registers-and-registries-technical-guidelines-inspire-register-federation_en), §§4.2.1 to 4.2.2, printed pp. 10 to 12, distinguishes owner and manager responsibilities and persistent register and item identifiers; §§4.2.4 to 4.2.5, pp. 13 to 14, describes invalidation, retirement, supersession and retention. PublicSchema applies those precedents to administrative records. `register_owner` names the organization that establishes and answers for a register; it is not an exact mapping of every governance role. |
| Provenance and time | [PROV-O Recommendation, 30 April 2013, §§3.1 to 3.3](https://www.w3.org/TR/2013/REC-prov-o-20130430/) distinguishes entities, activities, attribution and qualified influence. `EvidenceAssertion`, `RecordLifecycleEvent`, and `SubjectMatchAssertion` make a source's role, effective time, recording time and reconciliation explicit, and `assertion_authority` is close to `prov:wasAttributedTo`. They do not establish truth, perform a merge or implement an audit log. |
| Identifier and assignment | [ADMS Note, 1 August 2013, §5.2.6](https://www.w3.org/TR/2013/NOTE-vocab-adms-20130801/) supplies a historical scheme and agency distinction. The W3C note was retired in 2023 and ADMS is now maintained by SEMIC. Reuse `Identifier` for the value and scheme; `IdentifierAssignment` records issuer, subject and period. |
| Names and contact channels | [vCard Ontology Note, 22 May 2014, §§2.3 to 2.5](https://www.w3.org/TR/vcard-rdf/) distinguishes names, addresses (§2.4) and communications. `NameUsage` and `ContactPoint` retain purpose, subject and dates without modifying personal name or household-address contracts. `contact_channel` uses the seven FHIR ContactPoint system codes. |
| Codes and quantities | `CodedValue` preserves the original scheme and code and supplies a meaning URI only when known. A code is not an entity identifier. `QuantityValue` preserves the amount, the unit code and the unit system. In the [UCUM specification](https://ucum.org/ucum), square metre `m2` uses the exponent syntax of §9 and hectare `har` is the prefix `h` applied to the atom `ar`, as §31 notes. The vocabulary does not certify code membership or dimensional validity. |
| Feature versus geometry | [GeoSPARQL 1.1, OGC 22-047r1, §§8 and 10](https://docs.ogc.org/is/22-047r1/22-047r1.html) distinguishes a spatial feature and its geometric representation. `SpatialGeometry` carries encoding, literal and reference system, and `spatial_geometry` is close to `geo:hasGeometry` and `locn:geometry`. The executable pilot supports only two-dimensional [RFC 7946 §§3.1.1, 3.1.6 and 4](https://datatracker.ietf.org/doc/html/rfc7946) Point and Polygon geometry with CRS84 longitude then latitude. This is not a GeoSPARQL query or topology implementation. |
| Health facility, operator and service | Native [FHIR R5 5.0.0 HealthcareService](https://hl7.org/fhir/R5/healthcareservice.html) fields `providedBy`, `location` and `endpoint`, and [Location](https://hl7.org/fhir/R5/location.html) `managingOrganization`, separate neighbouring identities. `health/HealthFacility`, Organization, Address and named Location remain distinct. `AssetPartyRole` and `AssetAddressAssignment` describe independently needed dated estate responsibility and address facts. Root `ServiceCapacityObservation` remains an SOSA/UCUM-informed cross-sector observation, with no automatic FHIR mapping. Accreditation is a conformity assertion, not facility identity. |
| Agricultural versus cadastral land | [FAO WCA 2020 Volume 1, 2017, §§6.2 to 6.21](https://www.fao.org/4/i4913e/i4913e.pdf) informs holding and parcel use. [UNECE Guidelines on Real Property Units and Identifiers, 2004](https://unece.org/DAM/hlm/documents/Publications/guidelines.real.property.e.pdf) distinguishes parcel identification and property administration units. `AgriculturalParcel`, `LandSpatialUnit` and `LandAdministrativeUnit` therefore remain distinct. This does not claim full LADM or cadastral interchange conformance. |
| Tenure and boundary claims | [FAO VGGT, endorsed 11 May 2012](https://www.fao.org/tenure/voluntary-guidelines/en/) includes customary and informal tenure. `LandTenureAssertion` permits competing claims rather than reducing tenure to one owner. `LandBoundaryAssertion` separates geometry from recognition and evidence. National adjudication, priority and title validity require their own rules. |

PublicSchema chooses a register URI plus an unchanged local string as its record key.
Its optional `register_jurisdiction` is a named area, and its supersession links replace
records without asserting replacement of their subjects. These are PublicSchema design
choices, not an exact external register-model mapping. The vocabulary and example do not require
HTTP resolution or implement register governance. DCAT provides background for the
record and subject boundary; it does not define administrative recognition, permission,
the Authorization hierarchy or the complete CodedValue structure.

`register_uri` and `registered_subject` are marked sensitive: knowing that a person
appears in a particular register can reveal their circumstances. `subject_uri` alone is not.

## Statements about a subject

`IdentifierAssignment`, `NameUsage`, `ContactPoint`, `AssetPartyRole`,
`AssetAddressAssignment`, `RegistryEntry` and `RecordReference` all use `subject_uri` for the
thing they describe. The class of the statement says what kind of statement it is; the
subject slot does not repeat it. `registered_subject` and `matched_subject` keep their own
names because they mean something narrower: the recipient of recognition, and the subject a
record is proposed to describe.

`EvidenceAssertion` and `SubjectMatchAssertion` use `assertion_authority` for the
organization accountable for the statement. `RecordLifecycleEvent`, like the other events,
uses `authority` for the organization responsible for the change. Organizations with other
roles keep their own slots: `register_owner` on `Register`, `registration_authority` on
`Registration`, and `identifier_issuer` on `IdentifierAssignment`.

`RecordReference` has the same shape as an `Identifier` whose scheme is the register, but it
also carries the subject it resolves to. The published `Identifier` definition mentions
records within a registry; use `RecordReference` when the register record, rather than the
subject, is what the statement is about.

## Record lifecycle events

`RecordLifecycleEvent` is an `Event` about a register record. `affected_record` names the
record as a `RecordReference`, and `record_change_kind` says what happened to it:

| Code | Meaning |
| --- | --- |
| `invalidation` | The record was found to be wrong and is no longer to be relied on. |
| `retirement` | The record is kept for reference but no longer in current use. |
| `supersession` | The record was replaced by another record, named in `supersedes_record` on the replacement. |

`effective_at` may precede `recorded_at`. A change to the organization itself, such as a
merger or succession, is an `OrganizationalChangeEvent`, not a record lifecycle event.

## Closed code lists

Where a standard fixes a short list, the slot uses a closed vocabulary instead of a
`CodedValue`:

| Slot | Codes | Source |
| --- | --- | --- |
| `evidence_role` | `supports`, `contradicts` | PROV-O qualified influence |
| `contact_channel` | `phone`, `fax`, `email`, `pager`, `url`, `sms`, `other` | FHIR ContactPoint system |
| `geometry_encoding` | `geojson`, `wkt`, `gml`, `kml` | GeoSPARQL 1.1 serialization literals |
| `unit_scheme` | `ucum`, `unece_rec20` | UCUM and UN/ECE Recommendation 20 |
| `match_outcome` | `match`, `possible_match`, `non_match` | SSSOM mapping predicates and record-linkage practice |
| `record_change_kind` | `invalidation`, `retirement`, `supersession` | INSPIRE register guidance |

Lists that are local policy, such as asset roles, address purposes, name uses and building
uses, stay `CodedValue` so the source scheme and its unknown or retired codes are retained.

## Geometry and Location

`spatial_geometry` gives a building, parcel or other feature one or more
`SpatialGeometry` values, each with an explicit encoding, literal and coordinate reference
system. The `geometry` slot on `Location` holds a GeoJSON geometry object for a named place.
Both are close to `locn:geometry`. A `SpatialGeometry` with `geometry_encoding` `geojson` and
no `coordinate_reference_system` carries the same shape as a `Location.geometry` value,
serialized as a string in `geometry_literal`; moving between the two is a parse or
serialization step. Geometries in other encodings or reference systems have no lossless
`Location.geometry` form. An address position belongs on the `Address` `location`, not on the
assignment that links an address to an asset.

## Reference and profile contract

`RecordReference` is an assertion about `(register_uri, record_id)`. The optional `subject_uri` and `subject_type` must agree with the locally supplied entry before expansion to a subject. Missing records and unavailable registers remain `missing-record`; a known entry without local subject data remains `missing-subject`. Wrong type or conflicting explicit subject identity is an error in the illustrative profile. Two registers with local ID `001` do not become one record. The example never fetches a URI, performs a remote lookup or concatenates identifiers ambiguously.

The [local example profile](../examples/registry-pilots/profile.py) demonstrates submission rules separately from the vocabulary. It requires register, record and subject identity and a timezone-bearing recording timestamp, checks date ordering, converts only the two supported UCUM area units without rounding, and validates the chosen geometry subset. An empty Farm can still be vocabulary-valid. Kilograms fail the area profile; unknown units are retained as source values but cannot be converted. Missing dates are not fabricated. A RecordLifecycleEvent can take effect before it is recorded. Supersession links replace records, not necessarily their subjects.

For an issued registration or licence number, use an `Identifier` with its issuing scheme
and an `IdentifierAssignment` whose `subject_uri` is the recognition or permission
it identifies. Use `RegistryEntry.record_id` for the register's own entry key. A register
may use the issued number as that key, but the vocabulary does not assume it does. The
pilot includes a trade permission numbered `LIC-2026-0081` stored as record `row-104`;
the permission, its entry and the licensed cooperative retain separate identities.

`Authorization` inherits `Registration` because permission is a specific form of
administrative recognition. A registration is not simply a database entry.
ADR-020 records the alternative
of sibling recognition and permission concepts under an administrative-act supertype,
and the evidence that would justify changing this choice.

The pilot's `valid_from` / `valid_to` dates include the first and last applicable calendar
days. Relationship classes use `start_date` / `end_date`, where `end_date` is the date on
which the relationship ceased to be effective. They must not be converted by simply
renaming fields; [relationship date migration](relationship-date-migration.md) lists the
affected classes and preserves registration, tenure, parcel and certification validity
semantics. Neither pair is a recording timestamp.

Typed vocabulary references provide more information than arbitrary URI ranges. For general subjects, the example profile checks the locally resolved type. JSON Schema's accepted string reference alone proves neither existence nor identity. Source-local class strings and semantic type URIs are not silently interchanged, and no lossless projection or national compliance is claimed.

## Worked pilots and counterexamples

[The synthetic pilot records](../examples/registry-pilots/records.json) describe one clinic, dated estate-role and address assertions, a separate registration record, a cooperative and a person without a national identifier. `AssetPartyRole` keeps operator, upkeep and owner roles separate; its `asset_actor` can be a person, an organization or a group. The pilot profile narrows it to Person or Organization. A change of role or address retains the clinic URI. The detailed synthetic estate journeys are in [facility responsibilities and addresses](facility-roles.md).

The holding pilot uses two parcels, one shared by two holdings, and overlapping customary-use and disputed-lease claims. It also includes a landless livestock holding. Those records do not establish ownership, eligibility or beneficiary enrollment. The agricultural terms use their explicit `agri/` or `land/` namespaces, while shared biological identities remain root concepts where their meanings are cross-sector. [Mixed-crop components](../examples/agriculture-biology/records.json) exercise seasonal production semantics; one primary crop would lose the second component and its dates. No such lossy projection is offered.

`tests/test_registry_pilots.py` validates the same records with actual generated JSON Schemas and context-expanded production SHACL. It exercises qualified references, unknown records, wrong targets, quantities, dates and geometry. This is local semantic and export evidence, not a tested live registry importer. Run it with `uv run --locked pytest tests/test_registry_pilots.py`; `just check` and `just site-build` cover the integrated source and site.

The local resolver expects full semantic type URIs. Its `subject_index(records, type_uris)` helper normalizes the supplied synthetic compact types using the caller's locally built catalog before resolution; the golden-fixture test exercises this path. No remote context is required.

## Boundaries

Dataset containers from source registry models are exchange packaging, not independently meaningful vocabulary classes. Executable role and purpose selectors belong to an application's authorization configuration; sensitivity metadata and explanatory authorization conditions do not enforce access. A universal permission engine, or a source registry's mandatory ID, status and version fields, would cross the vocabulary boundary.

Address structure reuses Address without replacing its named Location with geometry. `AssetAddressAssignment` supplies an explicit address purpose and address identity for a physical asset. `health/HealthFacility` and `edu/School` specialize root `ServicePoint`; root `RegistrationOffice` remains wider than CRVS, and root `WaterPoint` is a disclosed exception to the sector namespace pattern. Service endpoints remain URI descriptions, capacity is dated and uses root `ServiceCapacityObservation` with SOSA/UCUM provenance, and accreditation requires the selected native FHIR or other domain profile. Land parties retain actual Person, Organization or InformalGroup identities; there is no need for a duplicate person record called LandParty. Agricultural beneficiary status remains a separate program decision.

AgriculturalParcel is deliberately a broader agricultural-use unit than FAO's census parcel, whose tenure-homogeneous boundary rules may be stricter. A profile needing that census unit must state and check those boundaries; no exact parcel equivalence is claimed.

## Medical reuse boundary

For medical exchange, use the selected native FHIR R5 5.0.0 resources and profiles,
including [Organization, Location and HealthcareService](https://hl7.org/fhir/R5/healthcareservice.html).
The [FHIR registry integration guide](fhir-registry-integration.md) provides synthetic
native resources and separate PublicSchema registry links. It documents the official
artifact-based shape checks and their limits; it does not claim clinical, jurisdictional or
implementation-guide conformance. FHIR's provider and premises relationships retain their
precise meanings: [Location.managingOrganization](https://hl7.org/fhir/R5/location-definitions.html#Location.managingOrganization)
concerns provisioning and upkeep.

PublicSchema has no native classes for healthcare service offerings, facility management
assignments or healthcare accreditation. A source fact about a health facility is a native
FHIR fact, a dated `AssetPartyRole`, an `AssetAddressAssignment`, or an unmapped fact that
retains its source evidence. A premises-only accreditation, historical responsibility,
service effective period and capacity measure each need an explicit mapping decision. Root
`ServiceCapacityObservation` has no automatic FHIR mapping.
