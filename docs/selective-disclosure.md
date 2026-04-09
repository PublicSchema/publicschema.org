# Selective Disclosure Design for PublicSchema Credentials

## Overview

PublicSchema credentials are designed for use with SD-JWT VC (Selective Disclosure JWT Verifiable Credentials), enabling holders to reveal only the claims needed for a specific interaction.

## Data Classification Approach

PublicSchema does not assign a fixed data classification to individual properties. Whether a property is personal data depends on the record it appears in, not the property itself. For example, `date_of_birth` on a Person record is personal data; the same field in an aggregate statistical table is not.

Instead, disclosure behavior is defined at the **credential level**. Each credential type below specifies which claims are always disclosed and which are selectively disclosable.

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
- `is_enrolled`
- `enrollment_date`, `start_date`

Selectively disclosable:
- `program_ref`
- Person identity claims (given_name, family_name, date_of_birth)
- `beneficiary` reference

**Use case**: Proof of active enrollment for service access. A health clinic verifier needs to confirm the holder is enrolled in a program. The holder discloses enrollment_status (active) and is_enrolled (true), keeping program identity and personal details hidden.

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
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "start_date": "2025-02-01",
      "_sd": [
        "...hash(program_ref)...",
        "...hash(beneficiary)..."
      ]
    }
  }
}
```

Note: SD-JWT VC payloads do not include `@context` or `type` arrays at the top level. These are W3C VCDM properties; SD-JWT VC uses `vct` (verifiable credential type) instead. The `cnf` claim binds the credential to the holder's key for key binding proof.

The `_sd` array contains hashes of the disclosable claims. The actual values are provided separately as disclosures that the holder can choose to include or omit when presenting the credential.

## Traditional Data Handling Guidance

Data handling requirements depend on the credential or dataset context, not on individual property definitions. Implementers should assess each deployment and apply protections based on whether the data, in that context, identifies or relates to a natural person.

General guidance:
- **Structural metadata** (program parameters, statuses, dates) typically requires no special handling.
- **Person-linked data** (identity claims, person-specific records) requires standard PII protections: access control, encryption at rest, defined retention periods.
- **Inherently sensitive data** (assessment scores, vulnerability indices) requires enhanced protections: audit logging, purpose limitation, breach notification triggers.

## Implementation Guidance

1. **Issuers** should consult the credential type definitions above when constructing SD-JWT VCs. Claims listed as "always disclosed" go in the clear; "selectively disclosable" claims go in `_sd`. For properties not covered by a defined credential type, the issuer determines disclosure behavior based on credential context.

2. **Holders** (wallet applications) should present a disclosure selection UI distinguishing always-disclosed claims from selectively disclosable ones. Inherently sensitive claims (assessment scores, vulnerability indices) should require explicit confirmation. When in doubt, default to selectively disclosable to err on the side of privacy.

3. **Verifiers** should request only the claims they need. A request for inherently sensitive claims should include a justification (e.g., audit authority reference).

4. **The build pipeline** outputs property metadata in `vocabulary.json`. Wallet and verifier implementations should use the credential type definitions in this document to configure disclosure policies.
