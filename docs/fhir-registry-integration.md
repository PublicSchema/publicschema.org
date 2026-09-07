# Native FHIR records in a PublicSchema registry

Use native FHIR resources for medicinal definitions and healthcare directory content. PublicSchema supplies the cross-sector subject identity and qualified registry record links. It does not reproduce the medical resource model or require a FHIR server for this file-based integration.

The [runnable example](../examples/fhir-registry/) contains two separate documents:

- `bundle.fhir.json` is a native FHIR R5 collection Bundle with 19 resources. Its media type is `application/fhir+json`.
- `registry-links.json` is an ordinary JSON adapter envelope containing PublicSchema subjects, RegistryEntry records, RecordReference links, explicit resource bindings, and unmapped source facts. Its envelope fields are example application configuration, not new PublicSchema vocabulary terms or a published FHIR profile.

Run from the repository root after the [normal development setup](../CONTRIBUTING.md):

```bash
uv run --locked python examples/fhir-registry/validate.py
uv run --locked pytest tests/test_fhir_registry.py -q
```

These commands use the existing Python dependencies and local artifacts. They require no network connection, Java installation, terminology service, or running registry. The checker reports 19 resources, 19 registry entries, 20 local FHIR references, and five consumer links. For another supplied extract, pass `--bundle PATH --links PATH`.

## Release and resource selection

This example pins **FHIR R5 5.0.0** and the published base profiles `http://hl7.org/fhir/StructureDefinition/{ResourceType}|5.0.0`, including Bundle. Each resource declares that exact profile in `meta.profile`. These base profiles do not establish compliance with a jurisdictional implementation guide, EMA UPD, ISO IDMP, or a clinical exchange contract. Several medicinal definition resources are Trial Use with different maturity levels.

| Concern | Native resource and example |
| --- | --- |
| Human and veterinary product definitions | [MedicinalProductDefinition](https://hl7.org/fhir/R5/medicinalproductdefinition.html), using distinct product records and `domain`. Neither record denotes a physical batch, a prescription, or interchangeability with the other product. |
| Ingredient roles and substance detail | [Ingredient](https://hl7.org/fhir/R5/ingredient.html) points to its product through `for` and to [SubstanceDefinition](https://hl7.org/fhir/R5/substancedefinition.html) through `substance.code.reference`. The fixture retains a numerical strength ratio and unit systems. |
| Prepared form and veterinary use | [AdministrableProductDefinition](https://hl7.org/fhir/R5/administrableproductdefinition-definitions.html) uses `formOf`, route, target species, and tissue-qualified withdrawal periods. The synthetic zero-day milk interval is explicit; an unauthorized use must never be encoded as zero withdrawal. |
| Package configuration | [PackagedProductDefinition](https://hl7.org/fhir/R5/packagedproductdefinition-definitions.html) uses `packageFor`. A package configuration has its own identity; detailed manufactured contents and batches are outside this fixture. |
| Medical market permission | [RegulatedAuthorization](https://hl7.org/fhir/R5/regulatedauthorization-definitions.html) has a separate subject reference, jurisdiction, holder, regulator, and validity period. Permission is not product identity or availability. |
| Provider, premises, service | [Organization](https://hl7.org/fhir/R5/organization-definitions.html), [Location](https://hl7.org/fhir/R5/location-definitions.html), and [HealthcareService](https://hl7.org/fhir/R5/healthcareservice-definitions.html). `HealthcareService.providedBy` identifies the clinical provider, while `Location.managingOrganization` identifies the organization responsible for provisioning and upkeep. The fixture deliberately uses different organizations. |
| Organization accreditation | R5 [Organization.qualification](https://hl7.org/fhir/R5/organization-definitions.html#Organization.qualification), with code, issuer, identifier, and period. This does not turn a premises-only accreditation into an organization qualification. |
| Technical connectivity | [Endpoint](https://hl7.org/fhir/R5/endpoint-definitions.html) retains connection type, payload type, MIME type, and address. A listed endpoint is not contacted and grants no access. |

The clinical concepts are deliberately synthetic, often expressed with `CodeableConcept.text`. An adopter must select the actual source terminologies and applicable published profiles. The example does not introduce a new medical code system.

## Identity and local resolution contract

For each FHIR resource, a binding joins an existing `RegistryEntry` to an exact `fhir_full_url`, `resource_type`, pinned `profile`, and a business identifier `system`/`value` pair. These identify different things:

| Value | Meaning |
| --- | --- |
| `(register_uri, record_id)` | Qualified PublicSchema record key. `record_id` remains a string with leading zeros preserved. |
| `subject_uri` | Explicit identity assertion for the thing or definition described. It is not copied from the FHIR record URL. |
| FHIR `fullUrl` and resource `id` | Address and local logical identity of the source FHIR record. |
| FHIR `identifier.system` and `identifier.value` | A source business identifier. Matching this pair checks the declared correspondence; it does not prove the source's authority or merge identities. |

PublicSchema `Organization`, `Substance`, and `health/HealthFacility` provide independently useful cross-sector identities in the sidecar. Their medical detail stays in native FHIR. HealthFacility denotes physical premises and is not equivalent to every FHIR Location. This example requires its bound Location to have `mode: instance` and an explicit site/building classification (`si`/`bu` in `http://terminology.hl7.org/CodeSystem/location-physical-type`); conceptual and virtual locations are rejected. A shared Substance identity does not duplicate the pharmaceutical SubstanceDefinition model.

Medicinal records omit the optional PublicSchema `subject_type`: the example does not mint a replacement native medical class or use a FHIR resource class as proof of a real-world subject's type. Instead, every consumer link declares `expected_resource_type`, which is checked against the resolved native record. The returned value includes the unchanged FHIR resource and the separately asserted `subject_uri`.

All resources come from the supplied local Bundle. Absolute references must match an exact `fullUrl`; relative `ResourceType/id` references resolve against the source entry's base URL. Each fullUrl must agree with its actual resource type and id. Reference targets are checked against the published R5 StructureDefinition `targetProfile` constraints; an explicit `Reference.type` or `Reference.identifier` must also agree with the resolved record. A URL's spelling alone is insufficient.

Qualified record resolution returns `resolved`, `missing-record`, or `missing-resource`. Identity and type disagreement are errors. The example requires its five consumer links to resolve. `RegistryEntry.source_records` can retain an unresolved provenance pointer, but that pointer is not treated as a verified source. No record URL, endpoint, identifier system, context, or profile URL triggers a remote request.

This deliberately bounded contract rejects additional profiles, extensions, modifier extensions, implicit rules, contained resources, nested Bundles, version-specific references, identifier-only FHIR references, and reference paths not described by the loaded resource profiles. Supporting one of these requires an explicit adapter change and its applicable artifacts. Valid FHIR outside this contract is not thereby invalid FHIR.

Native FHIR JSON has its own serialization. Do not add the PublicSchema JSON-LD context, rename `resourceType` to `@type`, or describe this Bundle as JSON-LD. RDF consumers must use the separate [FHIR RDF representation](https://hl7.org/fhir/R5/rdf.html).

## Retired draft models and migration decisions

The earlier native medicine and health directory draft classes have been retired. The following are migration decisions, not a general converter or claims of exact equivalence. Preserve the original source and explicitly record any unmapped field before retiring an adopter's old data.

| Retired draft or field | Replacement and conditions |
| --- | --- |
| `MedicinalProduct`, `VeterinaryMedicinalProduct` | Use MedicinalProductDefinition. `name` corresponds to a product name, `identifiers` to business identifiers, and `medicinal_classification` to classification only after preserving scheme and code meaning. Select `combinedPharmaceuticalDoseForm` for `medicinal_dose_form` only when it describes the same product-level form. Veterinary domain does not itself determine target species or authorize use. |
| `MedicinalIngredient`, `medicinal_ingredients` | Use Ingredient and its `for` references. `ingredient_substance` can reference SubstanceDefinition. The draft `ingredient_function` mixed active/excipient roles with more precise functions; review whether the source belongs in FHIR `role` or `function`. Map `strength_numerator`/`strength_denominator` to the appropriate presentation or concentration ratio only when the measured basis is known. |
| `AdministrableProduct` | Use AdministrableProductDefinition. `presentation_of` maps to `formOf`, `administrable_dose_form` to `administrableDoseForm`, and `administration_routes` to route structures when their meanings match. There is no direct general `name` field. Its detailed ingredient relationships use Ingredient `for`; its coded `ingredient` is a different representation. Preserve an otherwise unmapped name or unsupported source link. |
| `PackagedMedicinalProduct` | Use PackagedProductDefinition. `name`, identifiers, and `package_description` can be retained there. Review `packaged_medicines` as `packageFor`, which identifies the associated product, separately from actual `packaging.containedItem` contents. `package_type` and `package_quantity` require review of packaging level and units; a quantity of substance is not a count of containers. |
| `HealthcareServiceOffering` | Use HealthcareService for `name`, `healthcare_provider`/`providedBy`, `service_facilities`/`location`, and the source's service classification. Select `category`, `type`, or `specialty` for `healthcare_service_kind` by meaning. A textual `service_channel` has no exact general field. For `service_endpoints`, distinguish an Endpoint record reference from its network `address`; require the missing connection and payload details before creating a native Endpoint. |
| Service `valid_from` and `valid_to` | Base R5 HealthcareService has no general effective period for the service offering. `active`, `availability`, and opening times cannot replace it. Retain both source dates as unmapped until an applicable published profile or justified extension carries that fact. |
| `FacilityManagementAssignment` | Retire the ambiguous health-only relationship. First determine whether the source asserts service operation, premises upkeep, ownership, or institutional governance. Location.managingOrganization may carry a current upkeep assertion only when that role is established. It has no management period, so the old `valid_from`/`valid_to` are not transferred into that bare reference. Independently needed dated physical-asset roles use `AssetPartyRole` with explicit role meaning. |
| `FacilityAddressAssignment` | Native Location can retain an Address with its period of use. The cross-sector replacement `AssetAddressAssignment` remains useful for school and agricultural premises history. Preserve physical/postal purpose. A separate arbitrary SpatialGeometry cannot be squeezed into `Location.position`, which is a point with latitude/longitude and optional altitude. Keep unsupported geometry through the cross-sector record and source links. |
| `HealthcareAccreditation` | An organization's qualification can use Organization.qualification, retaining identifier, qualification code, issuer, and applicable period. A premises-only subject, detailed `accreditation_standard`, or `accreditation_scope` has no automatically equivalent field here. Keep those assertions and evidence unmapped until an applicable profile is selected. Do not infer organization-wide accreditation from a site certificate. |
| Generic `Authorization`, `Registration`, `ServiceCapacityObservation` | Retained for their cross-sector meanings. Prefer RegulatedAuthorization for native medical authorization exchanges; this does not make all general authorization fields equivalent. No FHIR equivalence is claimed for the generic capacity observation. A healthcare reporting exchange needs a profile for its actual measure. |

Date boundaries require an explicit decision. Old `valid_to` meant the last applicable date. PublicSchema `end_date` identifies the date effectiveness ceased. FHIR [Period](https://hl7.org/fhir/R5/datatypes-definitions.html#Period) includes matching end date/time values and allows partial precision. A day-based conversion to an exclusive cessation date may require the following day; do not mechanically rename fields, invent timestamps, or copy a period onto another fact.

The sidecar demonstrates `migration_outcomes` with `state: unmapped`, the original RecordReference, source path, source value, and reason. Its examples retain a general service start date, an ambiguous management end date, and a premises-only accreditation subject. Use existing `source_records` and `EvidenceAssertion` relationships to retain provenance in a real registry. This example demonstrates reporting unresolved facts; it does not automatically convert legacy records or promise a lossless round trip.

## What the checks establish

`validate.py` uses the unmodified official JSON Schema archive and published base StructureDefinitions in [artifacts](../examples/fhir-registry/artifacts/). It checks their SHA-256 digests before use. The archives total about 650 KB compressed, add no dependency, and are not fetched at runtime. The Python tests also validate the PublicSchema sidecar instances against the actual generated PublicSchema schemas.

JSON Schema checks structure and the constraints encoded in that artifact. The adapter additionally checks the local identities, target types, expected profiles, and business identifiers described above. It does not evaluate FHIRPath invariants, all choice/cardinality rules, terminology bindings, narrative completeness, clinical correctness, or jurisdictional profiles. This distinction follows the [FHIR validation guidance](https://hl7.org/fhir/R5/validation.html).

For a separate authoring check, download the pinned [HL7 validator 6.9.12](https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/6.9.12) to temporary storage. It needs Java; the JAR is about 187 MB and is not a repository or runtime dependency. The wrapper verifies SHA-256 `0e53ab1d1a6f1e35f505255c0b8ce10a35fcf27e6e96b503640f784cd07e5ad6` before execution.

```bash
curl -fsSL https://github.com/hapifhir/org.hl7.fhir.core/releases/download/6.9.12/validator_cli.jar \
  -o /tmp/publicschema-fhir-validator-6.9.12.jar
uv run --locked python examples/fhir-registry/official_validate.py \
  --prepare-cache --cache-home /tmp/publicschema-fhir-cache
uv run --locked python examples/fhir-registry/official_validate.py \
  --jar /tmp/publicschema-fhir-validator-6.9.12.jar \
  --cache-home /tmp/publicschema-fhir-cache \
  --output /tmp/publicschema-fhir-outcome.json
```

Preparation explicitly downloads fixed releases from `https://packages2.fhir.org/packages/{name}/{version}`: `hl7.fhir.r5.core#5.0.0`, `hl7.fhir.xver-extensions#0.1.0`, `hl7.terminology.r5#6.2.0`, `hl7.fhir.uv.extensions.r5#5.2.0`, `hl7.terminology.r5#7.1.0`, `hl7.fhir.uv.extensions.r5#5.3.0`, and `hl7.terminology#7.3.0`. Use a dedicated cache. Existing packages are preserved; a different version set is reported for review. Package release versions and metadata are checked; unlike the vendored artifacts and JAR, these downloaded cache contents are not byte-pinned by the example.

Validation itself prohibits network access in the official tool settings, disables its resource fetcher, uses `-tx n/a`, pins R5 and a global jurisdiction, and enables reference checks. FHIR invariants remain enabled. The wrapper examines the returned OperationOutcome and exits with failure on error/fatal issues, even if the Java process returned zero. Pass `--bundle PATH` for another native Bundle.

Read warnings and information in the outcome. In this offline mode the example's UCUM quantities and FHIR MIME type cannot receive terminology-server validation, and the base organization-qualification code binding has no source to check. A clean error count therefore remains narrower than complete FHIR conformance. A real exchange still needs its chosen profiles, terminology policy, source authority, and consumer authorization checks.
