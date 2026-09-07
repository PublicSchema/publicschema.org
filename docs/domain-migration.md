# Domain placement and draft migration

PublicSchema uses domains when a definition has sector-specific meaning. Shared identities, relationships and observations remain reusable across domains. This draft revision adds agriculture, land administration, environment, transport, education, health, tax and elections to the existing social-protection and civil-registration namespaces.

All relocated or refactored elements remain **draft**. Candidate and normative definitions and URIs are preserved. Domain coverage is bounded: the presence of an elections namespace, for example, describes voter registration coverage and does not claim a complete electoral model.

## Choose by meaning

| Meaning | Placement and reason |
| --- | --- |
| An agricultural production holding | `agri/Farm`. A production unit has agricultural meaning even when social protection consumes its record. |
| A person, organization, work relationship or physical asset responsibility | Root. The same definition can apply in multiple sectors. |
| Agricultural land use versus legal tenure | `agri/AgriculturalParcel` and `land/LandTenureAssertion` remain distinct. A shared physical area does not equate cultivation with legal title. |
| A fishing vessel | `agri/FishingVessel` uses `transport/vessel_flag` and `transport/vessel_length`. Its defining purpose is fishing; flag-state and length-overall facts have general transport meaning. |
| Physical educational or healthcare premises | `edu/School` and `health/HealthFacility` inherit from shared ServicePoint. Moving the subtype does not duplicate the shared facility model. |
| Educational delivery | `edu/EducationOffering` joins a programme, provider and sites. A programme identity alone does not identify a particular offering. |
| Generic animal, plant-variety, accession or seed-lot identity | Root where the definition does not require agricultural use. Keep the meaning broader than the source module filename. |
| Tax and voter registration | `tax/TaxRegistration` and `elections/VoterRegistration`, inheriting the common registration contract. |
| Service application, decision and appeal | Root. These administrative relationships can describe services in several sectors without widening social-protection Program or Party. |

RegistrationOffice remains at root because its definition includes identity and refugee registration as well as civil registration. WaterPoint also retains its existing URI; a separate water and sanitation domain is outside this revision's assessed scope. These are explicit boundaries, not a rule that every ServicePoint subtype must stay at root.

The domain labels are authored in `schema/publicschema.yaml`. Navigation shows the domains actually represented by concepts, properties or vocabularies, with French and Spanish labels and English description fallback. Unrecognized codes remain visible. Domains do not grant permissions or require separate repositories, registries or datasets.

## What changes in payloads and exports

The [URI disposition file](../examples/domain-migration/uri-map.json) lists changed and retired draft URIs individually. It includes authored class, slot, enum and value identities, plus the catalog vocabulary and value URLs. The file is a review aid for this revision, not an executable migration or a second schema source. `new_uri: null` means that no automatic replacement is asserted.

For example:

| Earlier draft | Current draft |
| --- | --- |
| `https://publicschema.org/Farm` | `https://publicschema.org/agri/Farm` |
| `https://publicschema.org/School` | `https://publicschema.org/edu/School` |
| `https://publicschema.org/HealthFacility` | `https://publicschema.org/health/HealthFacility` |
| `https://publicschema.org/school_type` | `https://publicschema.org/edu/school_type` |
| `https://publicschema.org/vocab/school-level` | `https://publicschema.org/vocab/edu/school-level` |

Concept and property pages use the same domain segment as their public URI. JSON Schema files follow the concept path, such as `/agri/Farm.schema.json`. Vocabulary catalog routes keep `/vocab/` first, followed by the domain and kebab-case identifier. Authored LinkML enums and their `meaning` values retain the existing PascalCase convention, now with the matching domain segment. The disposition file distinguishes these two existing export conventions.

JSON property keys do not acquire prefixes: a school still has `school_type`, while the generated JSON-LD context expands it to the scoped property URI. Unambiguous short class aliases, such as `Farm`, continue to be available in that context. Prefer the explicit canonical type `agri/Farm` or its absolute URI when inspecting migrations. An old absolute URI is not silently rewritten by a new context, and no `owl:sameAs` assertion is made for a retired shape.

Keep an adopter's original context and source records while migrating. Review type URIs, schema references, RDF predicates, vocabulary references, saved catalog links and any profiles that name them. Changing a context can change the meaning of an unchanged compact payload, so record which context the source used. A generated JSON Schema validates structure; it does not establish that an old and a new type mean the same thing.

## Shared facility relationships and dates

Use [AssetPartyRole and AssetAddressAssignment](facility-roles.md) when consumers independently need physical asset responsibility or address history across sectors. Owner, operator and upkeep provider are separate coded responsibilities. A former FacilityManagementAssignment does not by itself prove which responsibility was intended. Former FacilityAddressAssignment records need an explicit physical or postal purpose as well as the new class and endpoint fields.

The [relationship date guide and helper](relationship-date-migration.md) cover the selected relationships changing from `valid_from`/`valid_to` to `start_date`/`end_date`. Under the helper's explicit inclusive-calendar-day source contract, an inclusive end of `2026-12-31` becomes the first inactive day `2027-01-01`. Missing dates stay missing. Legal validity, registration and certification intervals keep their existing contracts. Namespace migration and date conversion are separate reviewed steps.

ServiceCapacityObservation also remains shared: it records a scheme-qualified measure, quantity, subject and observation time. Its observation pattern is informed by SOSA and its units by UCUM. It can describe capacity at a school, an agricultural service or a healthcare facility; it does not prove current availability and has no automatic mapping to a FHIR resource.

## Native medical records

The [FHIR integration guide](fhir-registry-integration.md) replaces duplicate draft medicine and healthcare-directory shapes with native FHIR R5 resources. It accounts for each retired class and field, preserves separate subject and qualified source-record identities, and documents facts that require an adopter's profile or remain unmapped. Shared Substance and physical HealthFacility identities remain useful without reproducing pharmaceutical definitions.

Retirement is not a lossless conversion claim. Premises-only accreditation and historical service validity, for example, must not be forced into a superficially similar FHIR field. The synthetic example preserves its unmapped facts explicitly. Clinical encounters, patient records and a complete medical terminology are outside this revision.

## Review questions

Reviewers can improve this draft with cases where a domain assignment changes a term's intended meaning, a supposedly shared relationship has a sector-specific invariant, or a proposed FHIR mapping loses information. Supply a source edition and a concrete payload or counterexample. The [qualified government relationships](government-relationships-draft.md) and [public-service journeys](public-services-draft.md) describe the additional questions for those slices.

Changing a draft boundary remains possible when evidence supports it. Promotion to candidate or normative still requires the repository's maturity evidence, translations and review; local examples and agent review do not substitute for external adoption.
