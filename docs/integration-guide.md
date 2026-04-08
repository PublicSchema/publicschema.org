# PublicSchema Integration Guide

## What PublicSchema provides

PublicSchema is a shared vocabulary for public service delivery data. It provides:

1. **Concepts**: semantic entities (Person, Enrollment, PaymentEvent, etc.) with multilingual definitions
2. **Properties**: typed, reusable fields that apply across concepts (given_name, start_date, amount)
3. **Vocabularies**: controlled value sets, referencing international standards where they exist
4. **JSON-LD context**: maps property names to stable URIs with type information
5. **JSON Schemas**: per-concept and per-credential validation schemas
6. **Credential types**: VerifiableCredential schemas for IdentityCredential, EnrollmentCredential, PaymentCredential

## Quick start

### 1. Reference the context

Add the PublicSchema context to your JSON-LD documents:

```json
{
  "@context": "https://publicschema.org/ctx/draft.jsonld",
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "date_of_birth": "1988-03-15"
}
```

This makes your data machine-readable. Any system that understands the PublicSchema context can process it.

### 2. Validate your data

Use the generated JSON Schemas to validate data at runtime:

```python
import json
import jsonschema

# Load the schema for the concept you're using
schema = json.load(open("person.schema.json"))

# Validate your data
data = {"given_name": "Amina", "date_of_birth": "1988-03-15", "gender": "female"}
jsonschema.validate(data, schema)
```

Schemas are available at `https://publicschema.org/schemas/{Concept}.schema.json`.

### 3. Use canonical vocabulary codes

When your system stores enrollment status, payment status, gender, etc., map your internal codes to PublicSchema's canonical codes:

| Your system | PublicSchema | Vocabulary |
|---|---|---|
| `ACTV` | `active` | enrollment-status |
| `M` | `male` | gender-type |
| `BANK` | `bank_transfer` | delivery-channel |

The `vocabulary.json` file contains the full list of vocabularies with all codes, definitions, and system mappings.

### 4. Issue Verifiable Credentials

Use PublicSchema credential types to issue VCs:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://publicschema.org/ctx/draft.jsonld"
  ],
  "id": "urn:uuid:b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "type": ["VerifiableCredential", "EnrollmentCredential"],
  "issuer": "did:web:your-system.example.gov",
  "validFrom": "2025-01-15T00:00:00Z",
  "validUntil": "2026-01-15T00:00:00Z",
  "credentialSchema": {
    "id": "https://publicschema.org/schemas/credentials/EnrollmentCredential.schema.json",
    "type": "JsonSchema"
  },
  "credentialStatus": {
    "id": "https://your-system.example.gov/credentials/status/1#42",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "revocation",
    "statusListIndex": "42",
    "statusListCredential": "https://your-system.example.gov/credentials/status/1"
  },
  "credentialSubject": {
    "id": "did:web:your-system.example.gov:persons:4421",
    "type": "Person",
    "given_name": "Amina",
    "family_name": "Diallo",
    "enrollment": {
      "type": "Enrollment",
      "program_ref": "https://your-system.example.gov/programs/cash-transfer",
      "enrollment_status": "active",
      "enrollment_date": "2025-01-15"
    }
  }
}
```

### 5. Implement selective disclosure

Consult the credential type definitions in `docs/selective-disclosure.md` to determine which claims should be selectively disclosable in SD-JWT VCs. Each credential type specifies which claims are always disclosed and which are wrapped in `_sd` (revealed only when needed).

## System mapping

If your system uses different field names or codes, use the `system_mappings` in vocabulary YAML files to translate. For example, the gender-type vocabulary includes:

```yaml
system_mappings:
  openimis:
    "M": male
    "F": female
    "O": other
  spdci:
    "1": male
    "2": female
    "0": not_stated
```

## Available artifacts

| Artifact | URL | Description |
|---|---|---|
| JSON-LD Context | [`/ctx/draft.jsonld`](/ctx/draft.jsonld) | Map property names to URIs |
| Full Vocabulary (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) | Complete vocabulary as a single JSON-LD @graph |
| Full Vocabulary (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) | Complete vocabulary as RDF/Turtle |
| SHACL Shapes | [`/v/draft/publicschema.shacl.ttl`](/v/draft/publicschema.shacl.ttl) | Validation shapes for all concepts |
| Vocabulary JSON | [`/vocabulary.json`](/vocabulary.json) | Full vocabulary with all concepts, properties, vocabularies |
| Concept Schemas | `/schemas/{Concept}.schema.json` | JSON Schema per concept |
| Credential Schemas | `/schemas/credentials/{Type}.schema.json` | VC-envelope JSON Schema per credential type |

## schema.org interoperability

PublicSchema declares equivalences with schema.org for overlapping properties. The JSON-LD context includes camelCase aliases:

- `given_name` and `givenName` both resolve to `https://publicschema.org/given_name`
- `date_of_birth` and `birthDate` both resolve to `https://publicschema.org/date_of_birth`
- `start_date` and `startDate` both resolve to `https://publicschema.org/start_date`

Use whichever naming convention your system prefers. Both are valid in the context.

## `@vocab` fallback behavior

The PublicSchema context declares `"@vocab": "https://publicschema.org/"`. This means any JSON key that is not explicitly defined in the context will silently expand to `https://publicschema.org/{key}`. For example, a typo like `"givn_name"` would expand to `https://publicschema.org/givn_name` instead of raising an error.

JSON-LD processors will not flag this. To catch typos and undeclared properties, validate your data against the JSON Schema for the concept you are using. The JSON Schema only allows declared properties, so `"givn_name"` would fail validation.

## schema.org `alternateName` mapping

The PublicSchema property `preferred_name` maps to schema.org's `alternateName` as a `broadMatch`, not an `exactMatch`. schema.org's `alternateName` covers any alternate name (nicknames, former names, abbreviations), while `preferred_name` is specifically the name the person prefers to be addressed by. If your system uses `alternateName` from schema.org, be aware that it is semantically broader.

## Extending PublicSchema

See `docs/extension-mechanism.md` for how to add custom properties, vocabulary values, and concepts using your own namespace alongside PublicSchema terms.
