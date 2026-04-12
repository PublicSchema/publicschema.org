# Trial-Use Audit: Design Decisions

Decisions needed before fixing findings from the 2026-04-12 audit.

---

## Decision 1: Date property pattern on lifecycle concepts

**Problem:** Enrollment has 4 overlapping date fields (`enrollment_date`, `start_date`, `exit_date`, `end_date`). Other lifecycle concepts each use a different pattern. No consistent design.

**Decision: Option C + narrow exit_date.**

- Lifecycle concepts use domain-specific named dates only.
- Relationship concepts (GroupMembership, Relationship) use generic `start_date` / `end_date`.
- Remove `start_date` and `end_date` from Enrollment.
- Narrow `exit_date` definition to permanent exits only: "The date the enrollment ceased to be active." Suspension is a status transition, not an exit.

Resulting patterns:

| Concept | Dates | Rationale |
|---|---|---|
| Enrollment | `enrollment_date`, `exit_date` | Domain-specific lifecycle dates |
| Entitlement | `coverage_period_start`, `coverage_period_end` | Domain-specific period |
| Grievance | `submission_date`, `resolution_date` | Domain-specific lifecycle events |
| PaymentEvent | `payment_date` | Single event date |
| GroupMembership | `start_date`, `end_date` | Generic relationship dates |
| Relationship | `start_date`, `end_date` | Generic relationship dates |

Convention to document: "Lifecycle concepts use named dates that describe the domain event. Relationship and membership concepts use generic `start_date` / `end_date`."

### Changes required

- [x] Remove `start_date` from Enrollment `properties` list
- [x] Remove `end_date` from Enrollment `properties` list
- [x] Rewrite `exit_date` definition to: "The date the enrollment ceased to be active, whether through closure or graduation. Does not apply to temporary suspension."
- [x] Document the date convention in schema-design.md under "Temporal context"

---

## Decision 2: Vocabulary domain scoping

**Problem:** 7 vocabularies used exclusively by SP-domain concepts have no `domain` field, resolving to root URIs.

**Decision: Keep universal.** Each vocabulary was tested against the universality criterion: "would the same codes carry different meanings in another domain?"

| Vocabulary | Universal because | Domain-specific values |
|---|---|---|
| enrollment-status | Active, suspended, closed, pending_verification, waitlisted apply to education enrollment, health enrollment, etc. | `graduated` already carries `domain: sp` (1 of 6 values, under threshold) |
| entitlement-status | Pending, approved, fulfilled, expired, suspended, cancelled describe any benefit entitlement lifecycle (health insurance claims, education grants) | None |
| payment-status | Payment processing states (pending, processing, paid, failed, returned, rejected, cancelled) are financial infrastructure, not domain-specific | None |
| delivery-channel | Bank transfer, mobile money, cash, agent network, prepaid card are payment delivery mechanisms in any domain | None |
| benefit-modality | Cash, voucher, in-kind, service, fee waiver, insurance describe benefit forms across SP, education (scholarships, school feeding, fee waivers), and health (insurance, medicine) | None |
| grievance-status | Submitted, under_review, resolved, closed, withdrawn, escalated describe any public service complaint lifecycle | None |
| grievance-type | Exclusion error, inclusion error, payment complaint, data correction, appeal, service quality, misconduct, information request apply to any means-tested public program. Definitions already say "program, benefit, or service" (not SP-specific) | None |

**Key reasoning:** These vocabularies describe processes (enrollment lifecycle, payment processing, complaint handling) and delivery mechanisms (channels, modalities), not domain content. Education enrollment goes through the same states as SP enrollment. A health insurance payment uses the same channels as a cash transfer.

If a future domain needs a value that does not exist, it is added to the universal vocabulary (with a `domain` annotation if it only applies to one domain). This is the existing pattern: `graduated` on enrollment-status has `domain: sp`.

**Risk assessment:** The cost of being wrong (a future domain needs incompatible values) is manageable: add the domain-specific vocabulary then, deprecate the universal one with a migration path. The cost of scoping to `sp/` now when they are actually universal is worse: every future domain importing `sp/enrollment-status` is semantically wrong, and moving to root later is also a URI-breaking change.

### Changes required

- [x] Fix gender-type definition to remove "social protection systems" reference (it is universal, definition should not anchor to SP)
- [x] Document this decision in vocabulary-design.md: "Vocabularies that describe processes (lifecycles, payment processing, complaint handling) and delivery mechanisms (channels, modalities) are universal by default, even if the first concept using them is domain-specific. Individual values that only apply to one domain use the `domain` annotation."

---

## Decision 3: System_mappings requirement for synced standard vocabularies

**Problem:** country, currency, language, occupation have `standard` + `sync` + `same_standard_systems` but no value-level `system_mappings`. The checklist requires system_mappings.

**Decision: Formalize `same_standard_systems` as a valid evidence path.**

When a vocabulary syncs from an international standard (ISO 3166, ISO 4217, ISO 639-3, ISCO-08) and systems use that standard's codes directly, value-level system_mappings are redundant. `same_standard_systems` documents which systems use the standard as-is.

### Changes required

- [x] Add to vocabulary-design.md section 3 (Reference existing standards): "When a vocabulary is synced from an international standard and systems use that standard's codes directly, `same_standard_systems` is sufficient in place of value-level `system_mappings`. This applies to large code lists (countries, currencies, languages) where the standard is the de facto interoperability layer."
- [x] Update review-checklist.md system_mappings gate to: "At least one `system_mappings` entry exists, OR the vocabulary has `standard` with `sync` metadata and `same_standard_systems` listing at least one system that uses the standard directly."

---

## Decision 4: Add exit_reason vocabulary to Enrollment

**Problem:** enrollment-status `closed` is too coarse. DHIS2 maps both COMPLETED and CANCELLED to it. Splitting `closed` into more status values mixes two orthogonal questions: "where in the lifecycle?" (status) vs. "why did this transition happen?" (reason).

**Decision: Add an `enrollment-exit-reason` vocabulary and `exit_reason` property.**

Status answers "what state is the enrollment in?" Reason answers "why did it leave the active state?" These are different questions (one-concept-per-vocabulary principle).

### enrollment-exit-reason vocabulary (draft)

| Code | Definition |
|---|---|
| `voluntary_withdrawal` | The beneficiary chose to leave the program. |
| `non_compliance` | The beneficiary did not meet ongoing program conditions. |
| `ineligibility` | The beneficiary was determined to be no longer eligible (income change, age-out, residency change). |
| `death` | The beneficiary died. |
| `program_end` | The program itself ended or the funding cycle closed. |
| `relocation` | The beneficiary moved out of the program's coverage area. |
| `duplicate` | The enrollment was identified as a duplicate of another record. |
| `administrative` | Closed for administrative reasons not covered by other codes. |

### What about `graduated`?

`graduated` stays as a status value, not an exit reason. Rationale:
- Graduation is a success outcome. Programs track graduation rates as a key metric.
- It is semantically distinct from all other exits: it means "met the program's criteria for positive exit."
- If graduated were an exit_reason under `closed`, you'd lose the ability to quickly distinguish success from failure in status-level queries.

`exit_reason` applies when enrollment_status is `closed` (not when `graduated`).

### Changes required

- [x] Create `schema/vocabularies/enrollment-exit-reason.yaml` (maturity: draft)
- [x] Create `schema/properties/exit_reason.yaml` (maturity: draft)
- [x] Add `exit_reason` to Enrollment concept's `properties` list
- [x] Update enrollment-status `closed` definition to reference exit_reason: "The enrollment has been permanently ended. The reason for closure is captured in exit_reason."
- [x] Update DHIS2 system_mappings notes: COMPLETED could map to `graduated` or `closed` + `exit_reason` depending on context; CANCELLED maps to `closed` + `exit_reason: administrative` or `voluntary_withdrawal`

---

## Decision 5: Separate reconciliation from payment-status

**Problem:** `reconciled` in payment-status mixes financial reconciliation (a post-payment bookkeeping process) with payment transmission states (pending, processing, paid, failed). These are orthogonal concerns.

**Decision: Add `is_reconciled` boolean property. Deprecate `reconciled` status value.**

Reconciliation is not a payment lifecycle state. It is a verification step that happens after the payment is complete. A payment can be `paid` and either reconciled or not. A payment can be `failed` and reconciled (confirmed as failed in the financial system).

### Why a boolean, not a vocabulary?

A boolean (`is_reconciled`) is the right granularity for now:
- The question reconciliation answers is binary: "has this payment record been matched against financial system records?"
- Three systems currently map to reconciled (openspp, fhir_r4:cleared, openimis:RECONCILED). All treat it as a binary flag.
- If a future need arises for states like `disputed` or `reconciliation_failed`, the boolean can be promoted to a vocabulary. Starting simple avoids overengineering.

### Deprecation path

Since `reconciled` is a trial-use value, removing it requires advance notice (per versioning rules). The path:

1. Add `is_reconciled` boolean property to PaymentEvent.
2. Mark `reconciled` value in payment-status as deprecated, with a note: "Use the `is_reconciled` property instead. This value will be removed in a future major version."
3. Update system_mappings: openspp:reconciled, fhir_r4:cleared, and openimis:RECONCILED map to `is_reconciled: true` (property-level) + `payment_status: paid` (status-level).
4. Remove `reconciled` from payment-status in the next major version.

### Changes required

- [x] Create `schema/properties/is_reconciled.yaml` (maturity: draft)
- [x] Add `is_reconciled` to PaymentEvent concept's `properties` list
- [x] Mark `reconciled` in payment-status as deprecated (add `deprecated: true` and `deprecated_note`)
- [x] Update system_mappings for openspp, fhir_r4, openimis to map reconciliation codes to `is_reconciled: true` + `payment_status: paid`
- [x] Document the deprecation in the vocabulary's notes

---

## Decision 6: "recipient" vs "beneficiary" on PaymentEvent; "complainant" on Grievance

**Problem:** PaymentEvent concept says "transfer to a beneficiary" but the property is called `recipient`. Grievance concept says "beneficiary's or applicant's" but the property is called `complainant`.

**Decision: Keep both names, document the distinction.**

- `recipient` is correct because the person receiving a payment is not always the enrolled beneficiary (payment proxies, survivors, guardians). "Recipient" is the payment-time role; "beneficiary" is the enrollment-time role.
- `complainant` is correct because anyone can file a grievance, not just beneficiaries. A community member, a rejected applicant, or a caretaker could be the complainant.

### Changes required

- [x] Add a note to the `recipient` property definition explaining that recipient may differ from the enrolled beneficiary
- [x] Add a note to the `complainant` property definition explaining that the complainant need not be the enrolled beneficiary

---

## Decision 7: enrollment_date semantics

**Problem:** Enrollment definition says "registering" but `enrollment_date` says "formally activated." Pre-activation states (`pending_verification`, `waitlisted`) exist, so an enrollment record exists before activation. What does `enrollment_date` capture?

**Decision: enrollment_date = activation date.**

Most systems track a single enrollment date meaning "when did this person become an active beneficiary." Pre-activation states are short-lived administrative steps. The enrollment record may exist in `pending_verification` or `waitlisted` before `enrollment_date` is set.

### Changes required

- [x] Rewrite `enrollment_date` EN definition to: "The date on which the enrollment became active and benefit delivery was authorized."
- [x] Update FR/ES to match
- [x] Verify Enrollment concept definition is consistent (it now says "registering" which is fine, the concept covers the whole process, the property captures the activation event)

---

## Decision 8: resolution_date scope

**Problem:** `resolution_date` says "resolved or closed" but grievance-status distinguishes `resolved` (decision issued) from `closed` (process complete, record archived). Same pattern as exit_date (D1).

**Decision: Narrow to resolution only.** Consistent with D1 pattern.

### Changes required

- [x] Rewrite `resolution_date` EN definition to: "The date on which a resolution decision was issued for the grievance."
- [x] Update FR/ES to match

---

## Decision 9: is_active / is_enrolled / enrollment_status triple

**Problem:** Three ways to express "is this enrollment current" with no guidance.

**Decision: Remove is_active from Enrollment. Document is_enrolled's VC purpose.**

- `enrollment_status` is the authoritative source of lifecycle state.
- `is_active` is redundant on Enrollment (useful on GroupMembership where there is no status vocabulary).
- `is_enrolled` has a documented VC rationale: selective disclosure without revealing specific status.

### Changes required

- [x] Remove `is_active` from Enrollment's `properties` list
- [x] Add a note to the Enrollment concept or `is_enrolled` property clarifying its VC-specific purpose

---

## Decision 10: Vocabulary granularity

Four vocabulary coarseness warnings. Decided per item:

**payment-status `partial`:** Add a `partial` value. Three systems distinguish partial from complete payments. A partial payment is not "paid" (the beneficiary has not received the full amount).

**payment-status `pending` coarseness:** Keep coarse. Pre-transmission details (issued vs. not-yet-issued, created vs. pending-approval) are system-internal workflow states, not interoperable payment lifecycle states.

**grievance-status `under_review` coarseness:** Keep coarse. The assigned/investigating distinction is workflow, not status. Systems vary too much in how they subdivide review.

**group-type `family` coarseness:** Keep coarse. Family sub-types (nuclear, extended, single-parent) are a domain question, not a group-type question. If needed later, Family can get its own `family-type` vocabulary.

### Changes required

- [x] Add `partial` value to payment-status vocabulary
- [x] Update opencrvs system_mapping to map PARTIAL to `partial` instead of `paid`

---

## Decision 11: Promote non_relative to relationship-type

**Problem:** 4 systems map codes like `non_relative`, `NOT RELATED` to `other`. Distinct concept: person is known to the household but has no family or legal tie.

**Decision: Add `non_relative` code.** 4 systems independently named this. Passes the promotion threshold.

### Changes required

- [x] Add `non_relative` value to relationship-type vocabulary
- [x] Update system_mappings that currently map non-relative codes to `other`

---

## Decision 12: gender-type `other` definition

**Problem:** Definition just says "not captured by male or female." Vague.

**Decision: Rewrite explicitly.** Name the use cases while keeping an escape hatch.

### Changes required

- [x] Rewrite `other` value definition to: "A gender identity that is not exclusively male or female, including but not limited to non-binary, third gender, or gender-diverse identities as recognized by the recording system."
- [x] Update FR/ES to match

---

## Decision 13: grievance-type at trial-use with zero system mappings

**Problem:** Weakest evidence base of any trial-use vocabulary. No system_mappings, only literature references.

**Decision: Keep at trial-use. Add mappings where possible.** The codes are well-grounded in World Bank and ISO 10002 literature. The gap is in our mapping work, not in the concepts.

### Changes required

- [x] Research openspp, openimis grievance type equivalents and add system_mappings
- [x] If no system equivalents found, add a note explaining the literature-only evidence base

---

## Decision 14: 7 vocabularies missing domain field

**Problem:** D2 decided these are universal. Should we explicitly set `domain: null`?

**Decision: Omit is sufficient.** Per design rules, omitting `domain` means universal. The decision is documented in vocabulary-design.md.

### Changes required

None.

---

## Decision 15: Thin evidence bases (entitlement-status, group-role)

**Problem:** entitlement-status has 1 system mapping, group-role has 2.

**Decision: Keep at trial-use. Add mappings.** The gap is in our mapping work, not in the concepts.

### Changes required

- [ ] Research DHIS2, openIMIS, DCI for entitlement status equivalents (deferred: requires per-system investigation)
- [ ] Research additional systems for group role equivalents (deferred: requires per-system investigation)

---

## Decision 16: marital-status FHIR Polygamous

**Problem:** FHIR R4 has P (Polygamous) mapped as `not_yet_mapped`. Polygamy is legally recognized in many target countries.

**Decision: Under discussion.** See research findings below.

### Research findings

The UN census framework (Rev. 3 and 4) does NOT include "polygamous" as a core marital status category. All parties in a polygamous marriage are classified as "married." Polygamy is captured (if at all) via a supplementary variable recording the number of spouses. No international standard distinguishes first wife from subsequent wives.

| Framework | Has polygamous code? | Distinguishes wife rank? |
|---|---|---|
| UN Census (Rev. 3, 4) | No (optional supplement only) | No |
| FHIR R4 / HL7 v3 | Yes: code P = "more than 1 current spouse" | No |
| IPUMS International | Yes: code 217 under "Married" | No |
| DHS surveys | No in marital status; separate v505 = co-wife count | No |
| Senegal, Mali, Nigeria, Kenya, Indonesia, Pakistan | No: all parties are "married" | No |

Key insights:
- The DHS architecture is instructive: marital status and union type are separate variables. v501 = marital status (married), v505 = number of co-wives.
- In countries like Senegal, the marriage regime (monogamous vs. polygamous) is a contractual election recorded at the time of first marriage, not a marital status of the individuals.
- No civil registration system assigns a different code to the first wife vs. subsequent wives.
- FHIR's "P" is under-specified: it means "more than 1 current spouse" but does not define who gets the code.
- Polyandry has no distinct code in any system.

**Decision: Option C. Map FHIR P to `married` + add `number_of_spouses` property.**

Follows the UN census standard: all parties in a polygamous union are "married." Polygamy is a union characteristic, not a marital status. The DHS approach (separate variable for co-wife count) is the cleanest design and matches the one-concept-per-vocabulary principle.

### Changes required

- [x] Map FHIR R4 P (Polygamous) to `married` in marital-status.yaml, with a note explaining the rationale
- [x] Create `schema/properties/number_of_spouses.yaml` (maturity: draft, type: integer) on Person
- [x] Add `number_of_spouses` to Person concept's `properties` list

---

## Decision 17: Event concept thinness + missing external_equivalents

**Problem:** Event has only `identifiers`. Four concepts lack `external_equivalents`.

**Decision: Leave Event thin. Document "no close equivalent" on the 4 concepts.**

Event is an abstract marker. Subtypes define their own domain-specific dates (per D1 convention). Adding `occurred_at` would recreate the duplication we just removed from Enrollment.

For Household, Event, PaymentEvent, Grievance: these genuinely lack strong matches in SEMIC or DCI. Document as verified rather than leaving blank.

### Changes required

- [x] Add `external_equivalents` to Household, Event, PaymentEvent, Grievance with notes explaining why no close match exists (or add the closest match if one exists)

---

## Decision 18: Orphan vocabularies (region, script)

**Problem:** `region.yaml` and `script.yaml` exist but no property references them.

**Decision: Keep.** Both are draft, synced from ISO standards (UN M49, ISO 15924), and may be needed by future properties. They cost nothing.

### Changes required

None.

---

## Decision 19: "subject of record" in Person

**Problem:** Slightly formal language.

**Decision: Leave as-is.** Accurate and commonly used in identity management contexts. The practitioners reading this (registry managers, policy officers) will understand it.

### Changes required

None.

---

## Summary

| # | Decision | New artifacts | Scope |
|---|---|---|---|
| 1 | Domain-specific dates on lifecycle concepts; generic on relationships | None (remove 2 properties from Enrollment, update definitions) | Enrollment only |
| 2 | Keep all 7 vocabularies universal; fix gender-type definition | None | Documentation + 1 text fix |
| 3 | Formalize `same_standard_systems` as valid evidence | None (update checklist + vocab design doc) | Documentation |
| 4 | Add exit_reason vocabulary + property | `enrollment-exit-reason.yaml`, `exit_reason.yaml` | Enrollment + new vocab |
| 5 | Add `is_reconciled` boolean, deprecate `reconciled` status | `is_reconciled.yaml` | PaymentEvent + payment-status |
| 6 | Keep recipient/complainant names, document distinction | None | Property definitions |
| 7 | enrollment_date = activation date | None | Property definition |
| 8 | Narrow resolution_date to resolution only | None | Property definition |
| 9 | Remove is_active from Enrollment, document is_enrolled | None | Enrollment properties |
| 10 | Add `partial` to payment-status; keep others coarse | None | payment-status vocab |
| 11 | Promote `non_relative` to relationship-type | None | relationship-type vocab |
| 12 | Rewrite gender-type `other` definition | None | gender-type vocab |
| 13 | Keep grievance-type trial-use, add mappings | None | Research task |
| 14 | Omit domain field (universal by default) | None | No change |
| 15 | Keep thin-evidence vocabs, add mappings | None | Research task |
| 16 | Map FHIR P to `married`, add `number_of_spouses` property | `number_of_spouses.yaml` | marital-status + Person |
| 17 | Leave Event thin, document missing equivalents | None | 4 concept files |
| 18 | Keep orphan vocabularies | None | No change |
| 19 | Leave "subject of record" | None | No change |
