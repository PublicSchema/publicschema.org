# Schema Design

## 1. Naming conventions

Casing encodes element type:

| Element type | Convention | Examples |
|---|---|---|
| Concepts | PascalCase | Person, Enrollment, GroupMembership |
| Properties | snake_case | given_name, date_of_birth |
| Vocabulary value codes | snake_case | never_married, bank_transfer |
| Vocabulary identifiers | kebab-case | gender-type, enrollment-status |

Enforced by JSON Schema regex validators. Once a name is published at candidate or above, it cannot be changed.

## 2. Domain-scoped URIs

Some concepts share a name across domains but carry different semantics ("Enrollment" in social protection vs. education). Domain-specific elements get a domain segment in their URI; universal elements live at the root:

- `publicschema.org/sp/Enrollment` (social protection)
- `publicschema.org/Person` (universal)

The test: an element is universal if the same definition carries the same meaning regardless of domain. If not, it belongs in a domain namespace.

Names are never prefixed with a domain abbreviation. It is `Enrollment`, not `SPEnrollment`. The URI structure handles disambiguation.

| Code | Domain | Status |
|---|---|---|
| `sp` | Social protection | Active |
| `edu` | Education | Future |
| `health` | Health | Future |
| `crvs` | Civil registration and vital statistics | Active |

## 3. URI persistence

Every element gets a stable URI. Once published at candidate or above, a URI will not be removed. Deprecated terms continue to resolve with metadata indicating the replacement. See [Versioning and Maturity](../versioning-and-maturity/) for the full model.

## 4. Concept, property, or vocabulary

Use this decision tree to determine what kind of element to create.

![Decision tree: own identity, closed value set, value has identity](/images/decision-tree.svg)

**Step 1: Does it have its own identity?** Does this thing exist independently, get referenced from multiple places, and have its own lifecycle? If yes, it is a **concept**.

*Example:* GroupMembership is a concept, not a property on Person or Group. It carries its own data (role, dates), has its own lifecycle, and is referenced from both sides.

**Step 2: Is it an attribute of a concept?** A fact about a specific concept, with no independent identity? If yes, it is a **property**. Multiple values (e.g., phone numbers) still make it a property with cardinality `many`.

**Step 3: Is the value drawn from a closed set?** If the property accepts one answer from a defined list with stable meanings, the value set is a **vocabulary**.

**Step 4: Reference or inline?** If the value has its own identity and properties, reference a concept (`concept: Location`). If it is a simple scalar, use an inline primitive.

*Example:* `latitude` is an inline `decimal` on Location. It has no independent identity, no sub-properties. It is a number.

| Situation | Element type |
|---|---|
| Own lifecycle, referenced from multiple concepts | Concept |
| Attribute of a concept, no independent identity | Property |
| Value from a closed set of options | Vocabulary |
| Value has its own identity and sub-properties | Property referencing a concept |
| Simple scalar | Inline primitive type |

### Actor vs. receiver supertypes

`Agent` and `Party` are two abstract supertypes that carry different semantics.

- `Party` is the **receiver side**: the persons and organised groups of persons (Household, Family, Farm) that can be identified, enrolled in programs, and receive benefits or services. Beneficiary-side references (`beneficiary`, `recipient`, `subject`, `redeemable_by`, `issued_to`) range over `Party`.
- `Agent` is the **actor side**: the persons, organisations, and software that perform, publish, evaluate, decide, or execute. Actor-side references (`performed_by`, `evaluator`, `publisher`) range over `Agent`.

`Person` is the only concept that belongs to both hierarchies. A person can both receive services and perform them. `Organization` is an `Agent` only (it is not modelled as a receiver today). `SoftwareAgent` is an `Agent` only. See [ADR-008](../decisions/008-agent-organization.md).

## 5. Temporal context

Almost everything in public service delivery is time-bounded. A status snapshot without a validity period is incomplete. When designing a concept or property, ask: will this value change over time? If yes, model the temporal context explicitly (start/end dates, validity periods).

### Date property conventions

Lifecycle concepts use domain-specific named dates that describe the domain event. Relationship and membership concepts use generic `start_date` / `end_date`.

| Concept type | Date pattern | Examples |
|---|---|---|
| Lifecycle (Enrollment) | Domain-specific named dates | `enrollment_date`, `exit_date` |
| Lifecycle (Entitlement) | Domain-specific period | `coverage_period_start`, `coverage_period_end` |
| Lifecycle (Grievance) | Domain-specific event dates | `submission_date`, `resolution_date` |
| Single event (PaymentEvent) | Single event date | `payment_date` |
| Relationship (GroupMembership, Relationship) | Generic dates | `start_date`, `end_date` |

Do not mix both patterns on the same concept. A lifecycle concept should not carry both `enrollment_date` and `start_date`.

## 6. Property independence

A property like `start_date` is defined once and reused across concepts. When a shared property needs concept-specific value sets (e.g., `status` on Enrollment vs. Grievance), it specializes via different vocabulary references rather than pretending the differences don't exist.

### Cross-concept property reuse

Property independence is not limited to repeated structural fields. Substantive observables can be reused across concepts too. `water_source`, `sanitation_facility`, and `dwelling_type` appear on both `SocioEconomicProfile` (baseline registration context) and `DwellingDamageProfile` in a sibling schema (post-shock assessment). In each case the property is declared once and listed in each concept's `properties`; the pattern also illustrates how PublicSchema properties can be reused by domain-specific profile subtypes vendored in a sibling schema.

The rules that keep this honest:

1. **One property file per named concept.** `water_source` is a single YAML file referenced from both profiles.
2. **Contextual framing lives on the concept, not the property.** The property definition names the observable ("the household's primary source of drinking water"). Each concept definition names how that observable is interpreted in that concept (baseline vs. post-shock).
3. **Reuse must be disclosed in both concepts' narrative definitions.** A reader on either page must be able to see that the field also appears elsewhere and why.
4. **Reuse does not make records type-compatible.** A `SocioEconomicProfile` record and a `DwellingDamageProfile` record are different things even when their property values overlap. Adopters should consult the concept page, not the property list, when serialising into a strongly typed shape.
5. **Split when wording diverges.** If the property's own definition needs different text in each context, create two properties. `location` and `location_of_assessment` are split this way: `location` is the concept-agnostic geographic location of the record's subject (the household's site for a Household record, the organisation's primary site for an Organization record); `location_of_assessment` is where a post-shock damage assessment was physically carried out, which may differ after displacement.

`triggering_hazard_event` (on `DwellingDamageProfile`) and `triggering_vital_event` (on `CivilStatusAnnotation`) follow the same split. Both were originally unified as one `triggering_event` whose type was widened to `concept:Event`, but the expected subtype carries meaning for validators and practitioners, so each consumer now declares its own typed reference. See [ADR-007](../decisions/007-profile-property-reuse.md) for the full argument.

## 7. Age applicability

Some Person-scoped properties are only meaningful for specific age groups. The Washington Group Short Set and Extended Set apply to adults; the Child Functioning Module applies to children ages 2-4 and 5-17. WHO growth standards apply to under-5s. Rather than encoding these rules in definition prose alone (which machines cannot parse), properties carry an optional `age_applicability` array of controlled tags.

| Tag | Numeric range | Source of the band |
|---|---|---|
| `infant_0_1` | 0-23 months | General infancy (covers MICS infant modules, early WHO growth) |
| `child_2_4` | 2-4 years (24-59 months) | CFM 2-4 variant; WHO Child Growth Standards |
| `child_5_17` | 5-17 years | CFM 5-17 variant; also CRC definition of "child" |
| `adolescent` | 10-19 years | WHO definition (deliberately crosscutting with child_5_17 and adult) |
| `adult` | 18+ years | WG-SS / WG-ES |

### Topical relevance, not eligibility

`age_applicability` answers "which age groups does this property concern?" It is **not** a filter primitive for eligibility. Age-based filtering is the consumer's job, computed from `date_of_birth`. Under this framing, overlap between tags is a feature, not a bug: a property about adolescent reproductive health carries both `child_5_17` and `adolescent` because the topic genuinely concerns both the under-18 bracket and the WHO 10-19 bracket.

A consumer asking "is this field relevant for a 15-year-old?" evaluates the child's age against all of the property's bands and asks whether any match. A consumer asking "is this topic adolescence-specific?" checks for the `adolescent` tag specifically.

### Population rules

- Only populate on properties that attach to `Person`. Age-applicability is meaningless on concepts without an age.
- Not required. Absence means the property applies broadly to any age.
- Validator enforces bibliography-implied coverage: properties cited by `washington-group-ss` or `washington-group-es` must include `adult`; properties cited by `washington-group-cfm` must include at least one of the child bands (`child_2_4` or `child_5_17`). Properties may narrow CFM coverage where the definition text explains which variant they map to.

## 8. External equivalents vs. serialisation bindings

The `external_equivalents` field on properties was originally intended for equivalents in other *ontologies* (SEMIC Core Vocabularies, DCI Core): a property like `given_name` maps exactly to `http://www.w3.org/ns/person#firstName`. The match is semantic: both describe the same concept in an alternate ontology.

The same field is also used for **serialisation bindings** such as FHIR R4 Observation with LOINC codes. These are not equivalents in the semic/dci sense; they are instructions for how to serialise this property into a specific interop format. The distinction matters when reading a property detail page: a SEMIC row says "this concept exists in another ontology"; a FHIR/LOINC row says "when you serialise this data into FHIR, use this code."

Convention:
- Per-item LOINC codes belong on the **property** (each WG item has its own LOINC code).
- Whole-vocabulary LOINC answer-list references belong on the **vocabulary** (`standard.uri`). Example: `pregnancy-status` carries one LOINC answer-list URI for the whole value set.

## 9. Sensitivity annotations

Some properties reveal sensitive circumstances regardless of whether they identify a specific person. `program_ref` reveals enrollment in a specific program (which may target HIV, disability, or poverty). `grievance_type` reveals that someone filed a complaint.

| Level | When to use | What it signals |
|---|---|---|
| `standard` | Default. No special handling beyond normal data protection. | Can be omitted (assumed if absent). |
| `sensitive` | Reveals circumstances (health, poverty, victimhood) in most contexts. | Requires justification to collect or disclose. |
| `restricted` | Should not appear in credentials at routine service points. | Requires a Data Protection Impact Assessment. |

This is a practitioner warning, not a compliance label. Whether a property constitutes personal data depends on the record it appears in, not the property itself. See [Selective Disclosure](../selective-disclosure/) for credential-level classification.
