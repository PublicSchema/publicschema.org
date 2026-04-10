# Integration Patterns

PublicSchema defines what data means. It does not define how data moves. The same concepts, properties, and vocabulary codes work across any transport: REST APIs, event buses, verifiable credentials, file exchanges, and analytics pipelines.

## The semantic layer

![PublicSchema sits between your internal model and any transport](/images/integration-layer.svg)

Your system maps its fields and codes to PublicSchema once. From there, the same canonical representation flows through any channel.

The examples below use the same enrollment record in each pattern.

## REST APIs

Expose PublicSchema property names and vocabulary codes in your API surface. Consumers get a predictable contract without knowing your internal schema.

```json
GET /api/enrollments/4421

{
  "type": "Enrollment",
  "given_name": "Amina",
  "family_name": "Diallo",
  "enrollment_status": "active",
  "enrollment_date": "2025-01-15",
  "program_ref": "cash-transfer-2025"
}
```

Validate request and response payloads with PublicSchema JSON Schemas at the API boundary.

## Event-driven systems

Publish domain events with PublicSchema-shaped payloads. Subscribers from different systems consume them without bilateral field mapping.

```json
{
  "event": "enrollment.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "type": "Enrollment",
    "given_name": "Amina",
    "family_name": "Diallo",
    "enrollment_status": "active",
    "enrollment_date": "2025-01-15",
    "program_ref": "cash-transfer-2025"
  }
}
```

The event envelope (type, timestamp, routing metadata) is yours. The payload inside uses PublicSchema.

## Verifiable Credentials

Issue SD-JWT VCs using PublicSchema credential types. The holder controls which claims to disclose at each presentation.

```json
{
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "credentialSubject": {
    "type": "Person",
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

The same properties appear in both the API response and the credential. The difference is the trust model (cryptographic signatures, selective disclosure), not the vocabulary.

See [Selective Disclosure](/docs/selective-disclosure/) for credential type definitions and disclosure rules.

## Batch and file exchange

Export data as CSV or JSON files using PublicSchema property names as column headers. Any system with a PublicSchema mapping can import the file without custom parsing.

```csv
given_name,family_name,enrollment_status,enrollment_date,program_ref
Amina,Diallo,active,2025-01-15,cash-transfer-2025
```

No API, no infrastructure. A mapping table and a well-named CSV.

## Data warehouse and analytics

Use PublicSchema vocabulary codes as canonical dimension values. Cross-program queries work because `active` means the same thing in every source table.

```sql
SELECT program_ref, enrollment_status, COUNT(*)
FROM enrollment
WHERE enrollment_status = 'active'
GROUP BY program_ref, enrollment_status
```

Each source maps its codes to PublicSchema codes at load time. The warehouse speaks one vocabulary.

## Same data, any transport

| Layer | What PublicSchema provides |
|---|---|
| Concepts | Shared entity definitions (Person, Enrollment) |
| Properties | Canonical field names (given_name, enrollment_status) |
| Vocabularies | Canonical value codes (active, suspended, completed) |
| JSON Schemas | Payload validation for APIs, events, and credentials |
| JSON-LD context | Machine-readable URI resolution for linked data and VCs |

## Which guide to read next

- To align vocabulary codes without changing your data model: [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/)
- To map fields between existing systems: [Interoperability & Mapping Guide](/docs/interoperability-guide/)
- To design a new system for compatibility: [Data Model Design Guide](/docs/data-model-guide/)
- To use JSON-LD contexts and issue verifiable credentials: [JSON-LD & VC Guide](/docs/jsonld-vc-guide/)
- For concrete scenarios: [Use Cases](/docs/use-cases/)
