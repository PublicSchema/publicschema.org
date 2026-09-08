# Registry foundations and the health/land pilots

A register, its record and the subject of that record have different identities. `RegistryEntry` uses a register URI and local record ID as its qualified key and an explicit `subject_uri` for the described thing. `Registration` records administrative recognition; `Authorization` adds permission for a stated activity. Neither is the Person, Organization, facility, product or Farm receiving it. All additions are draft, optional reference vocabulary. They are not an operational registry submission format, full-domain model or normative specification.

See the [government families](government-registry-draft.md), [biology](agriculture-biology-draft.md), [agricultural operations](agriculture-operations-draft.md), [facility responsibilities and addresses](facility-roles.md), and [relationship date migration](relationship-date-migration.md) for neighboring concepts. ADR-020 records the common choices and alternatives.

## Evidence and design judgment

Sources were consulted on 7–8 September 2026. Definitions are original PublicSchema wording informed by these sources. No source requires these class names, optionality, public URIs or serialization, and none is claimed as a complete interchange mapping.

| Question | Evidence and decision |
| --- | --- |
| Record versus subject | [DCAT 3 Recommendation, 22 August 2024, §§5.6 and 6.5](https://www.w3.org/TR/2024/REC-vocab-dcat-3-20240822/) distinguishes a catalog record from its primary topic. Administrative register records are a broader design application, not exact DCAT CatalogRecord equivalents. `Register`, `RegistryEntry`, and `RecordReference` retain those separate identities. |
| Register responsibility and lifecycle | [INSPIRE register guidance, v1.0, 31 May 2017](https://knowledge-base.inspire.ec.europa.eu/publications/best-practices-registers-and-registries-technical-guidelines-inspire-register-federation_en), §§4.2.1–4.2.2, printed pp. 10–12, distinguishes owner/manager responsibilities and persistent register/item identifiers; §§4.2.4–4.2.5, pp. 13–14, describes supersession, retirement and retention. PublicSchema applies those precedents to administrative records. Its single maintaining-authority field is not an exact mapping of every governance role. |
| Provenance and time | [PROV-O Recommendation, 30 April 2013, §§3.2–3.3](https://www.w3.org/TR/2013/REC-prov-o-20130430/) distinguishes entities, activities and qualified influence. `EvidenceAssertion`, `RecordLifecycleEvent`, and `SubjectMatchAssertion` make a source's role, effective time, recording time and reconciliation explicit. They do not establish truth, perform a merge or implement an audit log. |
| Identifier and assignment | [ADMS Note, 1 August 2013, §5.2.6](https://www.w3.org/TR/2013/NOTE-vocab-adms-20130801/) supplies a historical scheme/agency distinction. The W3C note was retired in 2023 and ADMS is now maintained by SEMIC. Reuse existing `Identifier` for the value and scheme; `IdentifierAssignment` records issuer, subject and period. No exact property mapping to starter IdentifierType strings is asserted. |
| Names and contact channels | [vCard Ontology Note, 22 May 2014, §§2.3 and 2.5](https://www.w3.org/TR/vcard-rdf/) distinguishes names and communications. `NameUsage` and `ContactPoint` retain purpose, subject and dates without modifying personal name or household-address contracts. |
| Codes and quantities | `CodedValue` preserves the original scheme/code and only supplies a meaning URI when known. A code is not an entity identifier. `QuantityValue` preserves magnitude and unit scheme. The [UCUM specification](https://ucum.org/ucum), unit tables, supports the pilot's square metre (`m2`) and hectare (`har`) conversion. The open value model does not certify code membership or dimensional validity. |
| Feature versus geometry | [GeoSPARQL 1.1, OGC 22-047r1, §§8 and 10](https://docs.ogc.org/is/22-047r1/22-047r1.html) distinguishes a spatial feature and its geometric representation. `SpatialGeometry` carries encoding, literal and reference system. The executable pilot supports only two-dimensional [RFC 7946 §§3.1.1, 3.1.6 and 4](https://datatracker.ietf.org/doc/html/rfc7946) Point/Polygon geometry with CRS84 longitude then latitude. This is not a GeoSPARQL query or topology implementation. |
| Health facility, operator and service | Native [FHIR R5 5.0.0 HealthcareService](https://hl7.org/fhir/R5/healthcareservice.html) fields `providedBy`, `location` and `endpoint`, and [Location](https://hl7.org/fhir/R5/location.html) `managingOrganization`, separate neighbouring identities. `health/HealthFacility`, Organization, Address and named Location remain distinct. `AssetPartyRole` and `AssetAddressAssignment` describe independently needed dated estate responsibility and address facts. Root `ServiceCapacityObservation` remains an SOSA/UCUM-informed cross-sector observation, with no automatic FHIR mapping. Accreditation is a conformity assertion, not facility identity. |
| Agricultural versus cadastral land | [FAO WCA 2020 Volume 1, 2017, §§6.2–6.21](https://www.fao.org/4/i4913e/i4913e.pdf) informs holding and parcel use. [UNECE Guidelines on Real Property Units and Identifiers, 2004](https://unece.org/DAM/hlm/documents/Publications/guidelines.real.property.e.pdf) distinguishes parcel identification and property administration units. `AgriculturalParcel`, `LandSpatialUnit` and `LandAdministrativeUnit` therefore remain distinct. This does not claim full LADM or cadastral interchange conformance. |
| Tenure and boundary claims | [FAO VGGT, endorsed 11 May 2012](https://www.fao.org/tenure/voluntary-guidelines/en/) includes customary and informal tenure. `LandTenureAssertion` permits competing claims rather than reducing tenure to one owner. `LandBoundaryAssertion` separates geometry from recognition and evidence. National adjudication, priority and title validity require their own rules. |

PublicSchema chooses a register URI plus an unchanged local string as its record key.
Its optional jurisdiction is a named area, and its supersession links replace records
without asserting replacement of their subjects. These are draft design choices, not
an exact external register-model mapping. The vocabulary and example do not require
HTTP resolution or implement register governance. DCAT provides background for the
record/subject boundary; it does not define administrative recognition, permission,
the Authorization hierarchy or the complete CodedValue structure.

## Reference and profile contract

`RecordReference` is an assertion about `(register_uri, record_id)`. The optional `subject_uri` and `subject_type` must agree with the locally supplied entry before expansion to a subject. Missing records and unavailable registers remain `missing-record`; a known entry without local subject data remains `missing-subject`. Wrong type or conflicting explicit subject identity is an error in the illustrative profile. Two registers with local ID `001` do not become one record. The example never fetches a URI, performs a remote lookup or concatenates identifiers ambiguously.

The [local example profile](../examples/registry-pilots/profile.py) demonstrates submission rules separately from the vocabulary. It requires register, record and subject identity and a timezone-bearing recording timestamp, checks date ordering, converts only the two supported area units without rounding, and validates the chosen geometry subset. An empty Farm can still be vocabulary-valid. Kilograms fail the area profile; unknown units are retained as source values but cannot be converted. Missing dates are not fabricated. RecordLifecycleEvent permits a change to take effect before it is recorded. Supersession links replace records, not necessarily their subjects.

For an issued registration or licence number, use an `Identifier` with its issuing scheme
and an `IdentifierAssignment` whose `identifier_subject` is the recognition or permission
it identifies. Use `RegistryEntry.record_id` for the register's own entry key. A register
may use the issued number as that key, but the vocabulary does not assume it does. The
pilot includes a trade permission numbered `LIC-2026-0081` stored as record `row-104`;
the permission, its entry and the licensed cooperative retain separate identities.

`Authorization` inherits `Registration` because permission is a specific form of
administrative recognition in this draft. A registration is not simply a database entry.
ADR-020 records the alternative
of sibling recognition and permission concepts under an administrative-act supertype,
and the evidence that would justify changing this choice.

The pilot's `valid_from` / `valid_to` dates include the first and last applicable calendar
days. Migrated relationship classes use `start_date` / `end_date` for the beginning and
first inactive day of effectiveness. They must not be converted by simply renaming
fields; [relationship date migration](relationship-date-migration.md) lists the affected
classes and preserves registration, tenure, parcel and certification validity semantics.
Neither pair is a recording timestamp.

Typed vocabulary references provide more information than arbitrary URI ranges. For general subjects, the example profile checks the locally resolved type. JSON Schema's accepted string reference alone proves neither existence nor identity. No v0.3/v0.4 starter adapter is claimed, so source-local class strings and semantic type URIs are not silently interchanged. No whole-kit lossless projection, national compliance or RegistryStack compatibility is claimed.

## Worked pilots and counterexamples

[The synthetic pilot records](../examples/registry-pilots/records.json) describe one clinic, dated estate-role and address assertions, a separate registration record, a cooperative and a person without a national identifier. `AssetPartyRole` keeps operator, upkeep and owner roles separate, and admits only Person or Organization actors. A change of role or address retains the clinic URI. The detailed synthetic estate journeys are in [facility responsibilities and addresses](facility-roles.md).

The holding pilot uses two parcels, one shared by two holdings, and overlapping customary-use and disputed-lease claims. It also includes a landless livestock holding. Those records do not establish ownership, eligibility or beneficiary enrollment. The agricultural terms use their explicit `agri/` or `land/` namespaces, while shared biological identities remain root concepts where their meanings are cross-sector. [Mixed-crop components](../examples/agriculture-biology/records.json) exercise seasonal production semantics; one primary crop would lose the second component and its dates. No such lossy projection is offered.

`tests/test_registry_pilots.py` validates the same records with actual generated JSON Schemas and context-expanded production SHACL. It exercises qualified references, unknown records, wrong targets, quantities, dates and geometry. This is local semantic/export evidence, not a tested live registry importer. Run the documented `just check` and `just site-build` for the integrated source and site.

## Source-family dispositions and contribution brief

Both starter kernels are design inputs. Shared record/source/evidence/name/contact/classification families are represented above. Their dataset containers are exchange packaging, not independently meaningful vocabulary classes. AccessPolicy's executable role/purpose selectors belong to an application's authorization configuration; existing sensitivity metadata and explanatory authorization conditions do not enforce access. Adding a universal permission engine or mirroring a source registry's mandatory ID/status/version fields would cross the vocabulary boundary. The starter lifecycle and classification enums are unverified local policy choices, so their codes can be retained in CodedValue but are not promoted into global closed lists.

Address structure reuses normative Address without replacing its named Location with geometry. `AssetAddressAssignment` supplies an explicit address purpose and address identity for a physical asset. `health/HealthFacility` and `edu/School` specialize root `ServicePoint`; root `RegistrationOffice` remains wider than CRVS, and root `WaterPoint` is a disclosed exception to the newer sector namespace pattern. Service endpoints remain URI descriptions, capacity is dated and uses root `ServiceCapacityObservation` with SOSA/UCUM provenance, and accreditation requires the selected native FHIR or other domain profile. Land parties retain actual Person, Organization or InformalGroup identities; there is no need for a duplicate person record called LandParty. Agricultural beneficiary status remains a separate program decision.

Please contribute contradictory examples for register/subject continuity, revoked versus expired recognition, unenumerated collectives, overlapping land units, disputed boundaries, unit precision and virtual healthcare. A contribution should name the affected URI, source edition/locator, alternative definition and a synthetic fixture. Draft translations use the site's normal English fallback; reviewed French and Spanish and stronger domain/adopter evidence are required before promotion. No maturity promotion follows from agent review alone.

The local resolver expects full semantic type URIs. Its `subject_index(records, type_uris)` helper normalizes the supplied synthetic compact types using the caller's locally built catalog before resolution; the golden-fixture test exercises this path. No remote context is required.

AgriculturalParcel is deliberately a broader agricultural-use unit than FAO's census parcel, whose tenure-homogeneous boundary rules may be stricter. A profile needing that census unit must state and check those boundaries; no exact parcel equivalence is claimed.

## Medical reuse boundary

For medical exchange, use the selected native FHIR R5 5.0.0 resources and profiles,
including [Organization, Location and HealthcareService](https://hl7.org/fhir/R5/healthcareservice.html).
The [FHIR registry integration guide](fhir-registry-integration.md) provides 19 synthetic
native resources and separate PublicSchema registry links. It documents the official
artifact-based shape checks and their limits; it does not claim clinical, jurisdictional or
implementation-guide conformance. FHIR's provider and premises relationships retain their
precise meanings: [Location.managingOrganization](https://hl7.org/fhir/R5/location-definitions.html#Location.managingOrganization)
concerns provisioning and upkeep.

`FacilityManagementAssignment`, `FacilityAddressAssignment`, `HealthcareServiceOffering`
and `HealthcareAccreditation` are retired draft classes. Determine whether a former source
fact is a native FHIR fact, a dated `AssetPartyRole`, an `AssetAddressAssignment`, or an
unmapped fact that must retain its source evidence. A premises-only accreditation, historical
responsibility, service effective period, and capacity measure still require explicit mapping
decisions. Root `ServiceCapacityObservation` has no automatic FHIR mapping.
