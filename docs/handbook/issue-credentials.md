# Issue Credentials

PublicSchema can support verifiable credentials when a person, household, organization, provider, or service relationship needs portable proof.

Credentials are not the right starting point for every adoption. Use them when offline verification, selective disclosure, holder control, or cross-border portability matters.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A credential flow showing issuer, holder, and verifier. Reader task: help a credential team separate schema validation, cryptographic verification, issuer trust, status checks, and disclosure policy. The issuer creates a PublicSchema-compatible credential, the holder stores it, and the verifier checks signature, schema, status, and selected claims.
</aside>

## User story

As a credential issuer, I want credential payloads to use PublicSchema-compatible fields and validation rules, so that verifiers can understand claims without bespoke data agreements for every issuer.

## When to use this path

Use credentials when:

- A person needs to prove eligibility without live access to a central system.
- A displaced person needs portable evidence across jurisdictions.
- A verifier needs only a subset of a record.
- Offline or low-connectivity verification is important.
- A program wants to reduce repeated document collection.
- A holder should control when claims are presented.

Do not use credentials just because they are technically possible. If the verifier always has online access to the issuing system and the person does not need portable proof, an API may be simpler.

## Credential types

Common credential patterns include:

| Credential | Typical purpose |
|---|---|
| Identity credential | Proves identity-related claims such as name, date of birth, identifiers, and documents. |
| Enrollment credential | Proves enrollment in a program or service. |
| Eligibility credential | Proves eligibility result, validity period, or category. |
| Entitlement credential | Proves a benefit, service, voucher, or right to receive support. |
| Payment credential | Proves a payment event or payment status. |
| Profile credential | Proves selected observations or derived profile outputs where appropriate. |

## Step 1: Define the claim

Start with the verifier's need.

Ask:

- What decision will the verifier make?
- Which claims are necessary for that decision?
- Which claims are not necessary and should be excluded?
- Does the verifier need a current status, historical fact, or time-bounded relationship?
- Does the credential need revocation or status checking?
- What privacy risks are created by presenting this credential?

Do not put the whole source record into a credential. A credential should carry the minimum useful claim set.

## Step 2: Select PublicSchema fields

For each claim, identify the PublicSchema concept and property.

Example for an enrollment credential:

| Claim | PublicSchema concept or property |
|---|---|
| Holder name | `Person.given_name`, `Person.family_name` |
| Date of birth | `Person.date_of_birth` |
| Program | `Program` identifier or name fields |
| Enrollment status | `Enrollment.enrollment_status` |
| Valid from | `start_date` |
| Valid until | `end_date` |

If no PublicSchema field exists, define a local extension and document it.

## Step 3: Validate payload shape

Use JSON Schema to validate the credential subject payload.

Validation should check:

- Required fields for this credential type.
- Data types.
- Date formats.
- Vocabulary values.
- Identifier structure where applicable.
- Local extension fields.

PublicSchema validation does not replace cryptographic verification. It answers a different question: does the payload mean what it claims to mean?

Keep these checks separate:

| Check | Question answered |
|---|---|
| Schema validation | Is the payload shaped correctly? |
| Vocabulary validation | Are controlled values canonical and allowed? |
| Cryptographic verification | Was the credential signed and presented correctly? |
| Issuer trust | Is this issuer allowed to make this claim? |
| Status or revocation | Is the credential still current and valid? |
| Presentation policy | Did the verifier request only claims needed for the decision? |

Minimal credential subject example:

```json
{
  "credentialSubject": {
    "person_id": "holder-subject-123",
    "program_id": "cash-transfer",
    "enrollment_status": "active",
    "valid_from": "2026-01-01",
    "valid_until": "2026-12-31"
  }
}
```

## Step 4: Use vocabulary codes carefully

Vocabulary-backed claims should use canonical values.

For example, if a credential says `enrollment_status: active`, the verifier should be able to interpret `active` through the PublicSchema vocabulary. If the issuer uses local values internally, the credential issuance process should translate them before signing.

## Step 5: Design selective disclosure

Selective disclosure should be designed before issuance.

Classify fields:

| Field class | Disclosure guidance |
|---|---|
| Essential claim | Usually disclosed for the target use case. |
| Context claim | Disclosed only when needed to interpret the essential claim. |
| Sensitive claim | Hidden unless the verifier has a strong need and lawful basis. |
| Correlation risk | Avoid stable identifiers unless necessary. |
| Internal claim | Do not include in the credential. |

Example: a verifier may need to know that someone is actively enrolled, but not their full household composition or case notes.

## Step 6: Define verifier checks

A verifier should check:

- Issuer signature.
- Issuer authorization or trust status.
- Credential status, revocation, or expiration.
- Credential schema.
- PublicSchema vocabulary values.
- Required claims for the decision.
- Presentation freshness, if relevant.
- Selective disclosure integrity.

Schema validation alone is never enough. A perfectly shaped credential from an untrusted issuer should not be accepted.

## Step 7: Govern credential lifecycle

Credential governance should define:

- Who may issue.
- Who may verify.
- How claims are updated.
- How expiration works.
- How revocation or status checking works.
- What happens when the source record changes.
- Which PublicSchema version was used.
- How local extensions are documented.

## Done means

A PublicSchema-compatible credential design is complete when:

- The verifier decision is clear.
- The credential includes only necessary claims.
- PublicSchema fields and vocabularies are identified.
- Local extensions are documented.
- JSON Schema validation passes for examples.
- Selective disclosure has been reviewed.
- Trust, status, expiration, and revocation are defined.

## Next

- Use [Privacy and Data Protection](/handbook/privacy-data-protection/) before deciding which claims belong in a credential.
- Use [Publish Exchanges and APIs](/handbook/publish-exchanges/) if an API check is safer or simpler than a credential.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) to record schema, trust, status, and disclosure decisions.
