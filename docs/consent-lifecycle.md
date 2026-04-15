# Consent Lifecycle Guide

This guide covers operational decisions for programs that adopt `ConsentRecord` and `PrivacyNotice`. It is aimed at program implementers and MIS designers, not legal counsel. Nothing here is legal advice.

---

## 1. Choosing a legal basis: when consent is the wrong answer

`ConsentRecord` stores the lawful basis for processing personal data. Consent (`legal_basis = consent`) is only one of six options. Most social protection programs reach for consent by default and then find themselves holding records that do not survive a regulatory audit or a beneficiary complaint.

Before setting `legal_basis = consent`, answer all three questions below honestly:

1. Can the beneficiary realistically refuse without losing access to the service?
2. Does the notice explicitly state that participation is voluntary?
3. Does withdrawal terminate the service?

If all three answers are yes, consent is the honest choice. If any answer is no, the processing is not genuinely voluntary, and a different legal basis applies.

### What to use instead

| Situation | Honest legal basis |
|---|---|
| Registration is a condition of receiving a benefit | `public_interest` (GDPR Art 6(1)(e)) |
| Data processing is required by a statute, regulation, or court order | `legal_obligation` (GDPR Art 6(1)(c)) |
| Processing is strictly necessary to protect someone's life | `vital_interest` (GDPR Art 6(1)(d)) |
| A contract with the beneficiary requires it | `contract` (GDPR Art 6(1)(b)) |
| The controller has a legitimate interest that is not overridden by the subject's rights | `legitimate_interest` (GDPR Art 6(1)(f)); use with care |

In practice, the majority of social protection enrollments use `public_interest` or `legal_obligation`. A ministry running a legal safety-net program almost never has genuine optional consent at the enrollment stage.

The `legal_basis` vocabulary codes correspond to `dpv-gdpr:A6-1-a` through `dpv-gdpr:A6-1-f`. Set `legal_basis_reference` to the local law citation that authorises the processing (for example, `"Kenya DPA 2019 s.30(1)(b)"`).

### Special categories

If any value in `personal_data_categories` is a subclass of `dpv:SpecialCategoryPersonalData` (health data, biometric data, ethnic origin, religious belief, etc.), you must also populate `special_category_basis`. The Art 6 legal basis and the Art 9 special-category basis are two separate requirements; both fields are needed.

---

## 2. State transitions for consent-status

The `consent-status` vocabulary defines nine values. Not all transitions are valid.

```
requested
  |-- (subject agrees) --> given
  |-- (subject refuses) --> refused [terminal]
  |-- (system timeout) --> invalidated [terminal]

given
  |-- (re-confirmation before expiry) --> renewed
  |-- (subject-initiated withdrawal) --> withdrawn [terminal]
  |-- (controller-initiated revocation) --> revoked [terminal]
  |-- (validity period ends) --> expired [terminal]

renewed
  |-- (subject-initiated withdrawal) --> withdrawn [terminal]
  |-- (controller-initiated revocation) --> revoked [terminal]
  |-- (validity period ends) --> expired [terminal]

unknown
  (legacy import where original status cannot be determined; treat as not-in-force)
```

Terminal states (`refused`, `withdrawn`, `revoked`, `expired`, `invalidated`) must not be changed back to an active state. A new `ConsentRecord` must be created instead.

When `status` transitions to `withdrawn`, populate `withdrawal_channel` and optionally `withdrawal_reason`. This satisfies GDPR Art 7(3) documentability: the controller can show not only that withdrawal was possible, but that it happened and through what channel.

---

## 3. Notice as boundary

The scope of a `ConsentRecord` must fall within the declared scope of the `PrivacyNotice` it references (via `notice_ref`). Scope means:

- The record's `purposes` must be a subset of the notice's `purposes`.
- The record's `personal_data_categories` must be a subset of the notice's `data_categories`.
- The record's `recipients` and `allowed_recipient_categories` must be within the notice's `recipient_categories` or `recipients_described`.

If the record needs to exceed the notice scope, the notice must be updated first, a new `notice_version` issued, and a new record taken from the data subject. You cannot retroactively expand the notice and claim the earlier record covers the new scope.

The `notice_version` field on the `ConsentRecord` is a snapshot of the version pinned at agreement time. Even if the notice is later corrected, the record continues to reference the version that was actually shown.

---

## 4. Re-consent triggers

| Change type | Re-consent required? | Action |
|---|---|---|
| New purpose added to the notice | Yes | Update notice, increment version, take new record |
| New recipient organisation added | Yes | Update notice, increment version, take new record |
| New category of personal data collected | Yes | Update notice, increment version, take new record |
| Translation update or typo correction | No | Increment notice version; existing records valid |
| DPO or complaint-authority contact change | No | Increment notice version; existing records valid |
| Retention description update (no change to actual retention) | No | Increment notice version; existing records valid |
| Jurisdiction re-labelled but same legal scope | No | Increment notice version; existing records valid |

The test is semantic, not textual: if the data subject would have a right to object to the change under the applicable law, re-consent is required.

See section 11 on the operational cost of re-consent campaigns before planning an update that triggers this path.

---

## 5. Age-of-majority transitions

For a minor whose consent was given by a parent or guardian (`delegation_type ∈ {parent, legal-guardian}`), set `expiry_date` to the date the data subject reaches the age of majority in the relevant `jurisdiction`.

Before that date, contact the now-adult data subject, present the notice again, and take a new record with `delegation_type = self`. The expired parental record is not valid for continued processing after majority.

This is a v1 workaround. ADR-017 will introduce a formal `capacity_basis` field for age-of-majority and legal-capacity transitions, at which point this procedure will be replaced.

Keep a record of the outreach attempt. If the person cannot be reached, the processing should cease or rely on a non-consent legal basis (`legal_obligation`, `public_interest`) that does not require a refreshed individual agreement.

---

## 6. Consent versus eligibility

These are separate concerns and separate records.

A `ConsentRecord` documents the lawful basis for processing personal data. An `EligibilityDecision` documents whether a person qualifies for a program. They are independent artefacts:

- A person may be eligible but has not yet consented. Enrolment should not proceed until a valid record exists.
- A consented person may be assessed and found ineligible. The `ConsentRecord` remains valid; the processing that was consented to happened lawfully even if the outcome was a rejection.
- A person may withdraw consent after being enrolled. Withdrawal does not reverse the enrollment; it governs future processing. Erasure is a separate process (see the follow-on ADR-010 on `DataSubjectRightsRequest`).

Do not conflate these. Systems that tie consent status directly to enrollment status create records that neither concept can correctly represent.

---

## 7. Performance and indexing

For any system managing more than a few thousand records, two practices reduce query cost significantly:

**Index on `(status, expiry_date)`.** Expiry sweeps (finding all records that have passed their `expiry_date` and are still showing `given`) are among the most frequent batch jobs. A composite index on these two fields makes the sweep a range scan rather than a full table scan.

**Maintain summary caches for common aggregations.** Queries such as "how many active consent records does this program have?" or "what is the consent coverage rate by community?" hit frequently in monitoring and reporting. Computing these on demand from the full record set is expensive. A summary table updated by a batch job (hourly or daily depending on volume) serves reporting without touching the live record store.

The schema does not dictate storage architecture, but these two points recur consistently in field deployments.

---

## 8. Verbal consent without a witness

When `collection_medium = verbal` or `consent_expression` is `opt-in-witnessed` or `opt-in-biometric`, at least one entry in `witnessed_by` should be populated.

This is an adopter-enforced invariant. The schema does not validate it. The reason it is not enforced at the schema level is that enforcement would block valid records from systems that cannot always identify a witness at digitisation time (for example, paper-to-digital backlogs). However, an absent `witnessed_by` on a verbal or biometric record weakens the legal evidentiary value of the record considerably.

Practical guidance:

- Train enumerators to record the witness's name and role at the time of collection, not at digitisation.
- Include a `witnessed_by` entry even if the witness is the enumerator themselves (this is weaker evidence but better than none).
- For verbal consent over the phone, record the call reference in `evidence_ref` and the call-centre agent in `witnessed_by`.

---

## 9. Biometric consent: two orthogonal axes

Biometrics appear in two places on a `ConsentRecord`. These are different things and must not be conflated.

**Axis 1: how consent was expressed.** `consent_expression = opt-in-biometric` means the data subject used a biometric (typically a thumbprint or iris scan) as the act of signature. This is about the capture method. The record may or may not involve processing biometric data as personal data.

**Axis 2: what data is being processed.** If `personal_data_categories` includes a URI that is a subclass of `dpv:BiometricData` (for example, `dpv-pd:Fingerprint`, `dpv-pd:IrisScan`, or `dpv-pd:FacialImage`), then biometric data is within scope of the processing. This is about data categories. The consent may or may not have been expressed biometrically.

A record may have one, the other, both, or neither:

| consent_expression | personal_data_categories includes biometric | Situation |
|---|---|---|
| `opt-in-biometric` | No | Thumbprint used as signature; no biometric data collected |
| Not biometric | Yes | Facial image collected; consent signed on paper |
| `opt-in-biometric` | Yes | Thumbprint as signature AND fingerprint data collected |
| Not biometric | No | No biometric involvement at all |

When biometric data is processed as a special category, ensure `special_category_basis` is also populated (see section 1).

---

## 10. Immutability of terms fields

The following properties are immutable once `status` reaches `given`. They are annotated `ps:immutableAfterStatus "given"` in the schema's RDF output:

`data_subject`, `controllers`, `recipients`, `recipient_role`, `allowed_recipient_categories`, `purposes`, `personal_data_categories`, `processing_operations`, `legal_basis`, `special_category_basis`, `notice_ref`, `notice_version`, `effective_date`, `jurisdiction`, `collection_medium`, `consent_expression`

This is not a UX preference or a design choice made for convenience. It is a legal requirement. GDPR Art 7(1) requires controllers to be able to demonstrate that consent was given. If the terms of the consent can be changed after the fact, the record cannot serve as evidence. The same principle applies under Kenya DPA s.29(2), LGPD Art 8(3), and equivalent provisions in other jurisdictions.

The schema emits `ps:immutableAfterStatus "given"` as a machine-readable annotation on each of these properties, and a plain-language `rdfs:comment` in the Turtle output. It does not currently emit a SHACL constraint, because a comment-only SHACL shape would misrepresent enforcement. Adopters must enforce this invariant at the application layer. A future ADR will promote this to a SHACL SPARQL constraint once the dependency on `pyshacl` becomes acceptable.

Fields that remain mutable after `given`:

- `status` (must change to record withdrawal, expiry, etc.)
- `withdrawal_channel`, `withdrawal_reason`, `refusal_reason` (populated as the lifecycle progresses)
- `evidence_ref` (additive only: new attachments may be added, existing ones not deleted)
- `verified_by`, `verified_date` (data-entry verification may happen after digitisation)
- `collection_session_ref` (operational correlation, not a term of the agreement)

---

## 11. Operational cost of re-consent campaigns

When a substantive change triggers re-consent (see section 4), be aware that a re-consent campaign in a field program is a multi-month operation, not a database transaction.

What this typically involves:

- Updating the notice and all its localised versions
- Printing or distributing updated notice materials
- Training community workers and enumerators on the change and why it matters
- Revisiting communities, sometimes multiple times to reach mobile or absent beneficiaries
- Collecting new consent (paper or electronic)
- Digitising paper forms and matching them to existing records
- Managing a reconciliation period where some records are updated and others are not yet

Programs have experienced 6-to-12-month re-consent cycles in large-scale deployments. Plan for this before making a change that triggers re-consent. If the change can be framed as editorial (a translation improvement, a contact update) rather than substantive, verify that it genuinely is editorial before taking the easier path.

The operational cost is one reason why the decision tree in section 1 matters: a program that originally claimed consent but would have been better served by `public_interest` may now face a re-consent campaign to correct the legal basis on every existing record, whereas updating the legal basis on a notice referencing `public_interest` requires no re-consent at all.

---

## 12. Reference implementation

OpenSPP's `spp_consent` module is a production-grade implementation of the consent record pattern, aligned with W3C DPV v2 and ISO/IEC TS 27560:2023. It includes JSON-LD export and OpenSPP's own state-machine enforcement of the status lifecycle.

Documentation: https://docs.openspp.org/en/latest/

The `spp_consent` module does not cover all fields in PublicSchema's `ConsentRecord` (for example, paper-workflow fields and multi-language notice presentation are PublicSchema extensions), but it is the closest reference for runtime enforcement logic and serialisation patterns.
