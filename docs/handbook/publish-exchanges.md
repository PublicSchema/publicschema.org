# Publish Exchanges and APIs

PublicSchema is most useful when it appears at system boundaries: API responses, event payloads, file exchanges, warehouse feeds, reporting extracts, and canonical exports.

The internal system can keep its own database design. The boundary should make shared meaning clear.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A hub-and-spoke exchange diagram. Reader task: help an integration team choose the right boundary artifact for each consumer. Internal systems publish PublicSchema-compatible APIs, events, CSV exports, and analytics feeds. Consumers include a dashboard, registry, credential issuer, and partner system.
</aside>

## User story

As an integration engineer, I want my system's external interface to use PublicSchema-compatible field meanings and vocabulary codes, so that other systems can consume data without custom semantic interpretation.

## When to use this path

Use this path when:

- A system needs a public or partner API.
- Multiple agencies publish data into a federation layer.
- A program exports data to a warehouse or dashboard.
- Partners exchange files through secure transfer.
- Events need a shared payload structure.
- A canonical export is required for procurement, audit, or handover.

## Boundary patterns

| Pattern | Description | PublicSchema role |
|---|---|---|
| REST API | A system exposes resources through endpoints. | Response fields and values align to PublicSchema. |
| Event stream | A system publishes change events. | Event payloads use shared concepts and vocabulary codes. |
| Batch file | A system produces CSV, JSON, or Excel exports. | Columns or object fields use PublicSchema property meanings. |
| ETL pipeline | Data is transformed into a warehouse or lakehouse. | PublicSchema is the canonical intermediate model. |
| Analytics feed | Aggregated or disaggregated data powers dashboards. | Dimensions, statuses, and metrics use shared definitions. |
| Credential issue | A system creates verifiable claims. | Credential payloads use PublicSchema-compatible schemas. |

## Step 1: Pick the concept boundary

Do not start by designing endpoints. Start by naming the concept being exchanged.

Examples:

- `Person` record export.
- `Enrollment` API resource.
- `PaymentEvent` event payload.
- `Household` data collection template.
- `EligibilityDecision` exchange file.
- `IdentityCredential` credential payload.

Some boundaries contain more than one concept. That is fine, but the structure should say which concept each field belongs to.

## Step 2: Select fields

For each boundary, list:

- PublicSchema property.
- Local source field.
- Data type.
- Cardinality.
- Required or optional status for this boundary.
- Vocabulary, if applicable.
- Transformation rule, if applicable.
- Sensitivity classification.

PublicSchema itself is broadly optional. A specific exchange can make a subset required. Keep that distinction clear.

## Step 3: Use canonical vocabulary values

Every vocabulary-backed field should either:

1. Use PublicSchema canonical values directly, or
2. Include a documented crosswalk from local values to PublicSchema values.

For external interfaces, direct canonical values are usually better. Consumers should not need to know the local code table.

## Step 4: Define validation

Validation should happen at the boundary.

Use:

- JSON Schema for JSON APIs, JSON files, and credential payloads.
- CSV column checks for tabular exports.
- Vocabulary validation for controlled values.
- SHACL for RDF data.
- Sample payloads for human review.
- Contract tests for API consumers.

Validation should produce useful failure messages. "Invalid payload" is not enough. Teams need to know which field or value failed and why.

Example validation error shape:

```json
{
  "path": "/enrollment_status",
  "code": "invalid_vocabulary_value",
  "message": "Value 'enabled' is not in the PublicSchema enrollment-status vocabulary.",
  "expected": ["active", "pending", "suspended", "completed"]
}
```

## Step 5: Publish examples

Every exchange should include examples.

Include:

- A minimal valid example.
- A realistic example.
- An edge-case example.
- An example showing multi-valued fields.
- An example showing missing optional fields.
- An invalid example, if useful for implementers.

Examples are often more effective than long prose. They also become regression tests.

## Step 6: Manage compatibility

Boundary contracts need versioning.

Record:

- PublicSchema version used.
- Local API or export version.
- Breaking change policy.
- Deprecation policy.
- Consumer notification process.
- Contact or owner.

Avoid changing field meanings silently. A renamed field is inconvenient. A field with the same name and a new meaning is dangerous.

## API design guidance

Use PublicSchema property names at the external boundary when possible. This makes mappings visible and reduces documentation burden.

PublicSchema does not replace OpenAPI. Use OpenAPI to describe endpoints, parameters, authentication, pagination, errors, and transport behavior. Use PublicSchema to describe the meaning of payload fields and vocabulary values. A generated or hand-written OpenAPI component can reference JSON Schema fragments for the concept payloads.

For example:

```json
{
  "given_name": "Amina",
  "family_name": "Diallo",
  "date_of_birth": "1988-03-15",
  "enrollment_status": "active"
}
```

If local API naming conventions require different names, document the mapping explicitly.

State required and optional fields for the boundary:

| Field | Requirement | Notes |
|---|---|---|
| `person_id` | required | Boundary identifier, not necessarily a national identifier |
| `enrollment_status` | required | Must use canonical vocabulary value |
| `status_date` | recommended | Required when status can change over time |
| `payment_amount` | optional | Required only for payment exports |

## Event design guidance

Events should distinguish the event wrapper from the concept payload.

Example:

```json
{
  "event_type": "enrollment.status_changed",
  "event_time": "2026-05-19T08:15:00Z",
  "source_system": "benefits-platform",
  "payload": {
    "person_id": "P-100145",
    "program_id": "cash-transfer",
    "enrollment_status": "suspended",
    "status_date": "2026-05-19"
  }
}
```

PublicSchema describes the payload semantics. The event envelope can follow local platform conventions.

## File exchange guidance

For CSV exports:

- Use PublicSchema property names as column headers when possible.
- Include a data dictionary.
- Include the PublicSchema version.
- Include code crosswalks for any local values.
- Validate controlled values before delivery.

For Excel templates:

- Use Template Excel downloads for data collection and procurement checks.
- Keep comments and dropdown validation intact when possible.
- Do not treat spreadsheets as a substitute for governance.

## Artifact selection

| Artifact | Use when | Source |
|---|---|---|
| Concept JSON Schema | Validating JSON payloads, APIs, files, and credential subjects | Concept pages and generated schema files |
| Vocabulary CSV | Reviewing values in spreadsheets and code tables | Vocabulary pages |
| Definition Excel | Human review of a concept, properties, and vocabularies | Concept pages |
| Template Excel | Data collection, prototyping, procurement tests | Concept pages |
| `vocabulary.json` | Programmatic access to the full site vocabulary | Site public artifact |
| `system_matchings.json` | Reviewing authored external system mappings | Site public artifact |
| OpenAPI fragment | Profile or product API boundary documentation | Generated by `publicschema-build` for profile packages |
| Validator package | Repeatable validation in JS or Python pipelines | Generated by `publicschema-build` for profile packages |

## Done means

An exchange or API is PublicSchema-compatible when:

- The concept boundary is named.
- Fields and values are mapped.
- Canonical vocabulary values are used or crosswalked.
- Sample payloads are published.
- Validation is automated where practical.
- Version and ownership are clear.

## Next

- Use [Privacy and Data Protection](/handbook/privacy-data-protection/) to minimize fields before publication.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) for a boundary contract checklist.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) before sharing an interface with consumers.
