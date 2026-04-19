# ADR-007: Cross-concept property reuse across Profile subtypes

**Status:** Accepted

## Context

ADR-006 established Profile as an abstract supertype whose subtypes each bundle the items of a single instrument family (FunctioningProfile, AnthropometricProfile, SocioEconomicProfile). The FunctioningProfile precedent settled intra-concept bundling: one concept may cover several instruments (WG-SS plus WG-ES, CFM 2-4 plus CFM 5-17) because those instruments share a domain and a shape, and the `valid_instruments` field on each item property marks which instruments legitimately populate it.

Adding humanitarian Profile subtypes raises a different question. A post-shock housing assessment (DwellingDamageProfile) and a baseline registration (SocioEconomicProfile) both want to record the household's water source, sanitation facility, electricity access, dwelling type, and wall/floor/roof material. A warning-response questionnaire (WarningResponseProfile, Batch 2) and SocioEconomicProfile both want to record settlement type and dwelling type. The values are drawn from the same closed sets, the definitions of the fields are the same, but the surrounding profile record frames them slightly differently: baseline context vs. post-shock status, reference-period registration vs. survey-moment observation.

The question is whether the same property file should appear on multiple Profile subtypes, or whether each subtype should get its own copy.

Precedent in this repo already points both ways. Shared administrative fields (`subject`, `observation_date`, `performed_by`, `instrument_used`, `administration_mode`, `respondent`, `respondent_relationship`, `items_asked`, `identifiers`) are declared on Profile and inherited by all subtypes. That is inheritance of universals, not cross-concept reuse. The question here concerns properties that are not universal to Profile but that appear on more than one subtype.

## Decision

Properties are the unit of reuse. Profiles are curated compositions of properties tied to an instrument family or a program moment.

1. **One property file per named concept.** `water_source` is one file. It appears in the `properties` list of SocioEconomicProfile and DwellingDamageProfile.
2. **Contextual interpretation lives on the concept, not the property.** The property's definition names the observable thing (what "water_source" is). Each concept's definition names how that observable is used on that concept (baseline registration vs. post-shock context).
3. **Property reuse must be disclosed in both concepts' definitions.** A reader of either concept page must be able to understand that the property also appears elsewhere and what the interpretation difference is. This is a narrative obligation, not a structural one. We do not add a machine-readable cross-concept annotation to properties; the reader locates the other concepts via the property's concept-usage index.
4. **Reuse does not imply type safety of records.** A DwellingDamageProfile record and a SocioEconomicProfile record, even if they carry the same property values, are not interchangeable. Adopters must not treat profiles as bags of fields; the concept carries semantic weight.
5. **When interpretation diverges enough that the field needs a different definition, split into two properties.** This is how `location` vs. `location_of_assessment` is handled in Batch 1: `location` is the household's registered administrative or coordinate location; `location_of_assessment` is the physical location where a damage assessment was carried out, which may differ if the household has relocated post-shock.

Reuse and split are choices on a continuum, not rules applied mechanically. The test is: does the property's own definition stay true across both concepts, or does it need different wording? If the wording changes, split.

## Alternatives considered

- **Duplicate every shared property.** Rejected: this fragments the data. A longitudinal analysis of water source over time would have to union across multiple property URIs. The RDF graph would carry parallel edges for the same observation.
- **Make shared properties abstract and let subtypes override.** Rejected: the schema has no override mechanism and introducing one contradicts the "properties are reusable" principle. It also pushes adopters toward treating profiles as type-safe record shapes, which they are not.
- **Put every reused property on Profile itself.** Rejected: Profile is abstract and the shared administrative shape it carries is genuinely universal. Housing material and WASH type are not universal across Profile subtypes (they are absent on FunctioningProfile and AnthropometricProfile), so pushing them up would make the supertype shape dishonest.
- **Introduce a mixin layer between Profile and its subtypes (e.g., `HouseholdObservationProfile`).** Rejected: the supertype chain is already `Event > Profile`. Adding another layer to encode "this subtype carries housing/WASH fields" encodes a structural promise that the schema does not enforce at the data level, and doubles the number of concept pages for a reader navigating the hierarchy. The lighter-weight answer is the narrative disclosure in each concept definition.

## Consequences

The `water_source`, `sanitation_facility`, `electricity_access`, `dwelling_type`, `wall_material`, `floor_material`, `roof_material` properties now each appear on two concept pages: SocioEconomicProfile and DwellingDamageProfile. Each concept's definition states how the property is used in that concept's framing, and names the other concept(s) where the property is reused.

`triggering_hazard_event` (on DwellingDamageProfile, referencing HazardEvent) and `triggering_vital_event` (on CivilStatusAnnotation, referencing VitalEvent) are split per decision 5. An earlier draft unified them into one `triggering_event` property whose type was widened to `concept:Event`, with the consuming concept's definition naming the expected subtype in prose. That was reversed: the expected subtype is load-bearing for validators and for practitioners reading the property page, so it belongs in the property's own `references:` field rather than in narrative constraint. The two properties share the same semantic role ("the event that triggered this record") but diverge on expected type, and the split makes that divergence structural rather than prose-only.

Adopters who serialize a profile record into a strongly typed structure (e.g., a FHIR QuestionnaireResponse or a Verifiable Credential schema) must consult the profile's concept page rather than relying on the property list as a guide to what shape the record has. The concept-level `external_equivalents` and selective-disclosure guidance are where cross-format serialization lives.

Site rendering: each property detail page lists the concepts that reference it. For reused properties, that list now shows more than one concept, which signals to readers that the property is not a private attribute of one concept but a reusable observable.

## References

- ADR-006: Extract observation-shaped data into a Profile hierarchy
- `docs/schema-design.md` section 6 (Property independence)
