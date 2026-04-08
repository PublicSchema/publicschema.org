# Selective Disclosure Design for PublicSchema Credentials

## Overview

PublicSchema credentials are designed for use with SD-JWT VC (Selective Disclosure JWT Verifiable Credentials), enabling holders to reveal only the claims needed for a specific interaction.

## Data Classification Levels

Every property in PublicSchema carries a `data_classification` annotation that guides credential issuers and verifiers on disclosure expectations:

| Level | Meaning | SD-JWT Behavior | Traditional Data Handling | Example Properties |
|---|---|---|---|---|
| `non_personal` | Structural, non-PII. Program metadata, statuses, dates, program-level parameters. | Always in the clear (not wrapped in `_sd`) | No special handling required | enrollment_status, program_ref, payment_status, group_type, scoring_method, cutoff_score |
| `personal` | Identifies, relates to, or resolves to a natural person. Includes person references, person-specific record references, and group composition data. | Wrapped in `_sd` array (selectively disclosable) | Standard PII protections: access control, encryption at rest, retention limits | given_name, date_of_birth, address, applicant, beneficiary, enrollment_ref, role |
| `special_category` | Data whose value is inherently sensitive: individual assessment scores, vulnerability indices. | Wrapped in `_sd` array with additional access controls expected | Enhanced protections: audit logging, purpose limitation, breach notification triggers | raw_score, assessor |

## Credential Structure for SD-JWT VC

### IdentityCredential

Always disclosed:
- `type` (Person)

Selectively disclosable:
- `given_name`, `family_name`, `name`
- `date_of_birth`
- `gender`, `sex`
- `nationality`, `marital_status`, `education_level`
- `phone_number`
- `identifiers` (each identifier can be disclosed independently)

**Use case**: Age verification without revealing full identity. A verifier needs to confirm the holder is over 18. The holder discloses only `date_of_birth`, keeping `given_name`, `phone_number`, and other PII hidden.

### EnrollmentCredential

Always disclosed:
- `type` (Person + Enrollment)
- `enrollment_status`
- `program_ref`
- `enrollment_date`, `start_date`

Selectively disclosable:
- Person identity claims (given_name, family_name, date_of_birth)
- `beneficiary` reference

**Use case**: Proof of active enrollment for service access. A health clinic verifier needs to confirm the holder is enrolled in a nutrition program. The holder discloses enrollment_status (active) and program_ref, but not their name or date of birth.

### PaymentCredential

Always disclosed:
- `type` (Person + PaymentEvent)
- `payment_status`
- `payment_date`

Selectively disclosable:
- `payment_amount`, `payment_currency`
- `delivery_channel`
- `transaction_reference`
- Person identity claims

**Use case**: Proof of payment receipt. An auditor needs to verify payments were made. The holder discloses payment_amount, payment_date, and transaction_reference, but not their personal identity.

## SD-JWT VC Payload Structure

An SD-JWT VC separates always-disclosed claims from selectively disclosable ones using the `_sd` mechanism. Here is how an EnrollmentCredential maps:

```json
{
  "iss": "did:web:registry.example.gov.sn",
  "sub": "did:web:registry.example.gov.sn:persons:4421",
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
    "_sd": [
      "...hash(given_name)...",
      "...hash(family_name)...",
      "...hash(date_of_birth)...",
      "...hash(gender)..."
    ],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "program_ref": "https://example.gov.sn/programs/pnbsf",
      "enrollment_date": "2025-01-15",
      "start_date": "2025-02-01",
      "_sd": [
        "...hash(beneficiary)..."
      ]
    }
  }
}
```

Note: SD-JWT VC payloads do not include `@context` or `type` arrays at the top level. These are W3C VCDM properties; SD-JWT VC uses `vct` (verifiable credential type) instead. The `cnf` claim binds the credential to the holder's key for key binding proof.

The `_sd` array contains hashes of the disclosable claims. The actual values are provided separately as disclosures that the holder can choose to include or omit when presenting the credential.

## Traditional Data Handling Guidance

The `data_classification` field applies beyond Verifiable Credentials. It also guides how systems should handle data at rest and in transit.

`non_personal` data requires no special treatment. It can be stored, logged, and transmitted without data protection controls. `personal` data requires standard PII protections: access control, encryption at rest, defined retention periods, and compliance with applicable privacy regulations. `special_category` data requires enhanced protections on top of those: audit logging on every access, strict purpose limitation (data used only for the reason it was collected), and breach notification triggers in case of unauthorized disclosure.

| Classification | Access control | Encryption at rest | Retention limits | Audit logging | Breach notification |
|---|---|---|---|---|---|
| `non_personal` | No requirement | No requirement | No requirement | No requirement | No requirement |
| `personal` | Required | Required | Required | Recommended | Required |
| `special_category` | Required | Required | Required | Required | Required |

## Implementation Guidance

1. **Issuers** should consult the `data_classification` field on each property when constructing SD-JWT VCs. Properties marked `non_personal` go in the clear; `personal` and `special_category` properties go in `_sd`.

2. **Holders** (wallet applications) should present a disclosure selection UI grouping claims by data classification. Special category claims should require explicit confirmation.

3. **Verifiers** should request only the claims they need. A request for `special_category` claims should include a justification (e.g., audit authority reference).

4. **The build pipeline** outputs data classification values in `vocabulary.json` under each property's `data_classification` field. Wallet and verifier implementations can consume this programmatically to auto-configure disclosure policies.
