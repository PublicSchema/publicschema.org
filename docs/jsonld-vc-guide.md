# JSON-LD & Verifiable Credentials Guide

This guide covers how to use PublicSchema with JSON-LD contexts and SD-JWT Verifiable Credentials. This is one of several ways to use PublicSchema. See [Use Cases](/docs/use-cases/) for a broader overview of integration patterns, many of which do not require JSON-LD or VCs.

## What this path uses

This integration path builds on the following PublicSchema artifacts:

- **JSON-LD context**: maps property names to stable URIs with type information
- **JSON Schemas**: per-concept and per-credential validation schemas
- **Credential types**: SD-JWT VC schemas for IdentityCredential, EnrollmentCredential, PaymentCredential

For the full list of available artifacts, see [Available artifacts](#available-artifacts) below.

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

Use PublicSchema credential types to issue SD-JWT VCs:

```json
{
  "iss": "did:web:your-system.example.gov",
  "sub": "did:web:your-system.example.gov:persons:4421",
  "iat": 1706745600,
  "nbf": 1706745600,
  "exp": 1738435200,
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "_sd_alg": "sha-256",
  "cnf": {
    "jwk": { "kty": "EC", "crv": "P-256", "x": "...", "y": "..." }
  },
  "credentialSubject": {
    "type": "Person",
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

### 5. Implement selective disclosure

Consult the credential type definitions in the [Selective Disclosure](/docs/selective-disclosure/) guide to determine which claims should be selectively disclosable in SD-JWT VCs. Each credential type specifies which claims are always disclosed and which are wrapped in `_sd` (revealed only when needed).

## System mapping

If your system uses different field names or codes, use the `system_mappings` in vocabulary YAML files to translate. Each system entry lists its values with the original code, human-readable label, and the canonical value it maps to. For example, the gender-type vocabulary includes:

```yaml
system_mappings:
  openimis:
    vocabulary_name: Gender
    values:
      - code: "M"
        label: Male
        maps_to: male
      - code: "F"
        label: Female
        maps_to: female
      - code: "O"
        label: Other
        maps_to: other
    unmapped_canonical: [not_stated]
  dci:
    vocabulary_name: GenderCode
    values:
      - code: "1"
        label: Male
        maps_to: male
      - code: "2"
        label: Female
        maps_to: female
      - code: "0"
        label: Not stated
        maps_to: not_stated
```

The `unmapped_canonical` list shows which PublicSchema values have no equivalent in that system, making gaps explicit in both directions. See [Mapping Example](/docs/mapping-example/) for a full walkthrough.

## Available artifacts

| Artifact | URL | Description |
|---|---|---|
| JSON-LD Context | [`/ctx/draft.jsonld`](/ctx/draft.jsonld) | Map property names to URIs |
| Full Vocabulary (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) | Complete vocabulary as a single JSON-LD @graph |
| Full Vocabulary (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) | Complete vocabulary as RDF/Turtle |
| SHACL Shapes | [`/v/draft/publicschema.shacl.ttl`](/v/draft/publicschema.shacl.ttl) | Validation shapes for all concepts |
| Vocabulary JSON | [`/vocabulary.json`](/vocabulary.json) | Full vocabulary with all concepts, properties, vocabularies |
| Concept Schemas | `/schemas/{Concept}.schema.json` | JSON Schema per concept |
| Credential Schemas | `/schemas/credentials/{Type}.schema.json` | SD-JWT VC JSON Schema per credential type |

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

See the [Extension Mechanism](/docs/extension-mechanism/) for how to add custom properties, vocabulary values, and concepts using your own namespace alongside PublicSchema terms.

## Next steps

- For a lighter approach that does not require JSON-LD, see the [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/).
- To map fields between existing systems, see the [Interoperability & Mapping Guide](/docs/interoperability-guide/).
- To design a new system for compatibility, see the [Data Model Design Guide](/docs/data-model-guide/).
- For concrete scenarios showing how PublicSchema is used, see [Use Cases](/docs/use-cases/).
