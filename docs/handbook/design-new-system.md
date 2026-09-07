# Design a New System

Use this path when PublicSchema can influence a system before it is built, procured, replaced, or substantially redesigned.

PublicSchema-compatible design does not mean copying PublicSchema's structure into your database. It means the system can clearly export, exchange, or validate the shared concepts, properties, and vocabulary values needed by other systems.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A layered product architecture sketch. Reader task: help a product owner distinguish internal product design from the external PublicSchema-compatible boundary. The bottom layer is the local database and workflow model. The middle layer is a PublicSchema-compatible export/API model. The top layer shows partner systems, dashboards, credentials, and reporting consumers.
</aside>

## User story

As a product owner designing a new public service delivery system, I want to use PublicSchema as a reference while defining entities, fields, vocabularies, and exports, so that the system can interoperate from the start.

## When to use this path

Use this path when:

- A new social registry, MIS, benefits platform, civil registration integration, or case management system is being designed.
- A ministry is writing procurement requirements.
- A vendor needs concrete interoperability acceptance criteria.
- A product team is replacing a legacy system.
- A multi-country platform needs a shared semantic baseline.
- A new API or export contract is being designed together with the internal model.

If the system already exists and cannot change, use [Map Existing Systems](/handbook/map-existing-systems/) instead.

## Outputs

At the end of this path, you should have:

| Output | Purpose |
|---|---|
| Adoption scope | The use cases and PublicSchema concepts the system will support. |
| Concept selection | The PublicSchema concepts relevant to the product. |
| Property checklist | The properties the system will store, derive, import, or export. |
| Vocabulary decision log | Which canonical vocabularies are adopted directly and which need local mappings. |
| Extension namespace | Local fields and concepts that are outside PublicSchema. |
| Export or API contract | The boundary format that external systems can use. |
| Validation examples | Sample records that demonstrate compatibility. |
| Procurement language | Testable requirements for vendors or internal teams. |

## Step 1: Define the adoption scope

Start from workflows and integrations, not from the full PublicSchema catalog.

Ask:

- Which data must be exchanged with other systems?
- Which data must be reported to external stakeholders?
- Which records may become credentials?
- Which concepts must be compared across programs?
- Which data will remain entirely internal?

Scope should be small enough to implement and broad enough to solve the interoperability need.

## Step 2: Select concepts

Choose the concepts the system needs.

Examples:

| System type | Common concepts |
|---|---|
| Social registry | `Person`, `Household`, `Group`, `GroupMembership`, `Identifier`, `Address`, `Location`, `SocioEconomicProfile` |
| Benefits management | `Program`, `Enrollment`, `EligibilityDecision`, `Entitlement`, `PaymentEvent` |
| Grievance system | `Person`, `Program`, `Enrollment`, `Grievance`, `Case`, `Location` |
| Civil registration bridge | `Person`, `Identifier`, `IdentityDocument`, `Location`, relationship concepts |
| Payment platform | `PaymentEvent`, `Entitlement`, `Person`, `Identifier`, `delivery-channel`, `payment-status` |

Not every system needs every concept. PublicSchema is a reference model, not an implementation checklist.

## Step 3: Review properties

For each selected concept, review its property list.

Classify each property:

| Decision | Meaning |
|---|---|
| Store | The system will store the property internally. |
| Derive | The system can compute the property from other data. |
| Import | The system receives the property from another source. |
| Export | The system will expose the property externally. |
| Not used | The property is not needed for the product scope. |
| Extension | The product needs a local property not yet in PublicSchema. |

Everything in PublicSchema is optional from the viewpoint of a local implementation. Compatibility is about clear meaning and exportability, not universal adoption.

Example property checklist:

| Concept | Property | Local decision | Boundary decision | Notes |
|---|---|---|---|---|
| `Person` | `date_of_birth` | store | export only when required | Prefer age band for routine reports |
| `Enrollment` | `enrollment_status` | store canonical code | export | Use PublicSchema vocabulary directly |
| `PaymentEvent` | `payment_amount` | store | export to finance feed | Include currency and period |
| `Location` | `administrative_area_code` | import | export | Align to national location code list |

## Step 4: Decide vocabulary strategy

For each vocabulary-backed property, decide whether the system will use PublicSchema codes directly.

Prefer direct adoption when possible:

- It reduces future mapping.
- It makes reports immediately comparable.
- It simplifies API consumers.
- It prevents local code drift.

Use local codes only when there is a strong reason, such as existing legislation, a vendor constraint, a national standard, or a legacy compatibility requirement. If local codes are used, design the PublicSchema mapping from the start.

## Step 5: Design local extensions

Most real systems need local fields. That is expected.

Good extensions:

- Use a local namespace.
- Do not collide with PublicSchema names.
- Include definitions.
- Include data types and cardinality.
- State whether the field is internal, exportable, or proposed for upstream contribution.

Bad extensions:

- Reuse a PublicSchema name with a different meaning.
- Hide a common concept behind a local-only field.
- Store a controlled value as free text without a code list.
- Depend on undocumented workflow state.

Use [Extend PublicSchema](/handbook/extend-publicschema/) when a field is not simply local. If several programs, countries, vendors, or standards need the same concept, treat it as a candidate upstream contribution.

## Step 6: Define the boundary contract

Even if the internal database is local, the external boundary should be clear.

Boundary options include:

| Boundary | Best for |
|---|---|
| PublicSchema-aligned CSV export | Reporting, data warehouse ingestion, low-friction data sharing. |
| JSON API response | System integration and federation. |
| Event payload | Event-driven workflows. |
| Template Excel | Field collection and procurement testing. |
| Credential payload | Portable holder-controlled proof. |
| JSON-LD | Linked data publication and semantic web tooling. |

The boundary contract should state:

- Concept represented.
- Property names.
- Vocabulary values.
- Required and optional fields for this local use case.
- Data types.
- Validation artifacts.
- Examples.

## Step 7: Validate sample records

Before implementation is complete, create representative sample records and validate them against PublicSchema artifacts.

Use:

- JSON Schema for JSON exports and APIs.
- SHACL for RDF or linked data workflows.
- Template Excel for spreadsheet-based testing.
- Vocabulary CSVs for code validation.
- Definition Excel for human review.

Validation should happen before procurement acceptance, before production integration, and before public publication.

## Procurement language

PublicSchema makes interoperability requirements testable.

Example:

> The system must export Person records using PublicSchema-compatible field meanings for given name, family name, date of birth, identifiers, and relevant status fields. Vocabulary-backed fields must use PublicSchema canonical codes directly or provide a documented mapping table. The supplier must provide sample exports that validate against the agreed PublicSchema JSON Schemas.

Better procurement language names the concepts, properties, vocabularies, file formats, validation tests, and acceptance examples.

Minimum vendor acceptance criteria:

| Criterion | Evidence |
|---|---|
| Concept support | Product entities mapped to PublicSchema concepts |
| Property support | Property checklist with store, derive, import, export, or not used decisions |
| Vocabulary support | Direct canonical values or documented crosswalks |
| Boundary contract | API, export, event, or template specification |
| Examples | Synthetic sample records for normal and edge cases |
| Validation | Report showing shape, vocabulary, and privacy checks |

For a full procurement workflow, use [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/).

## Done means

A new system design is PublicSchema-compatible when:

- The adoption scope is explicit.
- Relevant concepts are selected.
- Properties are classified by local use.
- Canonical vocabularies are adopted or mapped.
- Extensions are documented in a local namespace.
- A boundary contract is defined.
- Sample records validate or known gaps are documented.

## Next

- Use [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/) if this design will become tender or acceptance language.
- Use [Publish Exchanges and APIs](/handbook/publish-exchanges/) to turn the boundary into an interface.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) before handover.
