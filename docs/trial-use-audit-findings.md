# Trial-Use Audit Findings

Audit date: 2026-04-12. Scope: 14 trial-use concepts, 98 properties, 19 vocabularies.

Severity key: **FAIL** = violates a trial-use gate or design principle. **WARN** = suspicious, worth fixing. **INFO** = observation, may not need action.

---

## Theme 1: Definition content diverges across languages

### FAIL

- [x] **Enrollment EN vs FR/ES second sentence says different things.** EN: "Enrollment activates benefit delivery and creates the link between the beneficiary and the program." FR: "Les contraintes budgetaires signifient que l'eligibilite ne garantit pas l'inscription." (Budget constraints mean eligibility does not guarantee enrollment.) ES says the same as FR. These are not translations of each other. (`schema/concepts/enrollment.yaml`)

- [x] **Enrollment FR uses two different words for "enrollment" in consecutive sentences.** Sentence 1: "integration"; sentence 2: "inscription." The vocabulary files consistently use "inscription." (`schema/concepts/enrollment.yaml`)

- [x] **Enrollment EN says "individual or household," FR/ES say "sujet"/"sujeto" (subject).** Semantically inequivalent: English names two concrete types, French/Spanish use an abstract legal term. (`schema/concepts/enrollment.yaml`)

### WARN

- [x] **FR "sujet" in Enrollment breaks French terminology consistency.** Every other French definition uses "personne" or "individu" to refer to an individual human. Enrollment introduces "sujet" (legal/administrative register). Spanish parallel: "sujeto" vs "persona." (`schema/concepts/enrollment.yaml`)

### INFO

- [x] **FR "programme" usage is consistent across all French definitions.** No action needed.

---

## Theme 2: French accent and encoding issues

### FAIL

- [x] **"beneficiaire" missing accent in Entitlement FR definition.** Should be "beneficiaire" with accent (e acute). (`schema/concepts/entitlement.yaml`)

- [x] **"beneficiaire" missing accent in PaymentEvent FR definition.** Same issue. (`schema/concepts/payment-event.yaml`)

### WARN

- [x] **Systematic accent stripping in group.yaml FR.** "Menage" should be "Menage" (e acute), "lies" should be "lies" (e acute). (`schema/concepts/group.yaml`)

- [x] **Systematic accent stripping in group-membership.yaml FR.** "role" should be "role" (o circumflex), "dependant" should be "dependant" (e acute), "simultanement" should be "simultanement" (e acute). (`schema/concepts/group-membership.yaml`)

- [x] **Systematic accent stripping in group-membership.yaml ES.** "vinculo" should be "vinculo" (i acute). (`schema/concepts/group-membership.yaml`)

- [x] **Systematic accent stripping in identifier.yaml FR.** "alphanumerique," "systeme," "numero" all missing accents throughout. (`schema/concepts/identifier.yaml`)

- [x] **Systematic accent stripping in party.yaml FR.** "etre," "prestations," "inscrit" scattered missing accents. (`schema/concepts/party.yaml`)

### INFO

- [x] **Vocabulary files generally have correct accents (UTF-8).** The issue is concentrated in concept YAML files, suggesting different authoring pipelines.

---

## Theme 3: Terminology inconsistency across concepts

### FAIL

- [x] **Grievance uses "participant," a term not used anywhere else.** EN: "A record of a participant's or applicant's formal expression of dissatisfaction." Every other lifecycle concept uses "beneficiary." "Participant" is undefined in the schema. (`schema/concepts/grievance.yaml`)

- [x] **Enrollment EN uses "individual," which appears in no other concept definition.** All other English definitions use "person." "Individual or household" should be "person or household" for consistency. (`schema/concepts/enrollment.yaml`)

### WARN

- [x] **"recipient" vs "beneficiary" on PaymentEvent.** The concept definition says "from a program to a beneficiary," but the property is named `recipient` ("the person or group that received or is intended to receive the payment"). The distinction (enrollment-time actor vs. payment-time actor) is not documented. (`schema/concepts/payment-event.yaml`, `schema/properties/recipient.yaml`)

- [x] **"delivery chain" appears only in Grievance.** All other concepts use "program" as the delivering entity. "Delivery chain" is broader (covers payment agents, case workers, etc.) but the term is introduced without explanation. (`schema/concepts/grievance.yaml`)

- [x] **"complainant" in property vs "participant/applicant" in Grievance concept definition.** The `complainant` property uses a third term for the person filing the grievance. (`schema/properties/complainant.yaml`, `schema/concepts/grievance.yaml`)

### INFO

- [x] **FR cross-concept terminology for "beneficiary" is "beneficiaire" everywhere (when accents are correct).** Consistent apart from the accent issues in Theme 2.

- [x] **"case worker or review body" is consistent across grievance-status and eligibility-status vocabularies.** No action needed.

---

## Theme 4: Developer jargon in practitioner-facing definitions

### FAIL

- [x] **"join record" in GroupMembership EN definition.** "This join record allows a person to belong to multiple groups simultaneously." Database jargon. Suggested: "This link allows a person to belong to multiple groups at the same time." (`schema/concepts/group-membership.yaml`)

- [x] **"enregistrement de jointure" in GroupMembership FR definition.** French translation of "join record," equally jargon-laden. (`schema/concepts/group-membership.yaml`)

- [x] **"GroupMembership records" in Group EN definition.** "Groups are linked to their members via GroupMembership records." Structural model language. (`schema/concepts/group.yaml`)

- [x] **"enregistrements GroupMembership" in Group FR definition.** French translation preserves the structural jargon. (`schema/concepts/group.yaml`)

- [x] **"registros GroupMembership" in Group ES definition.** Spanish translation preserves the structural jargon. (`schema/concepts/group.yaml`)

- [x] **"entity" in Person EN definition.** "...not properties of the Person entity itself." ER-diagram language. Suggested: "not attributes of the person themselves." (`schema/concepts/person.yaml`)

- [x] **"record or relationship" in start_date definition.** "The date on which this record or relationship became effective." "Record" here means database row. (`schema/properties/start_date.yaml`)

### WARN

- [x] **"atomic" in Person EN definition.** "Person is the persistent, atomic unit of identity." CS/physics term. Practitioners would say "indivisible" or "core." (`schema/concepts/person.yaml`)

- [x] **"subject of record" in Person EN definition.** Acceptable legal/administrative language but slightly formal for the target audience. (`schema/concepts/person.yaml`) D19: Keep as-is.

- [x] **"record" in GroupMembership EN used in database sense.** "This join record allows..." The exception for "record" (acceptable when meaning "entry in a registry") does not apply here; this is a database row. (`schema/concepts/group-membership.yaml`)

- [x] **"records" in Group EN used in database sense.** "via GroupMembership records." Same issue. (`schema/concepts/group.yaml`)

- [x] **"membership records" in memberships property definition.** "The membership records linking persons to this group." Should be "membership links." (`schema/properties/memberships.yaml`)

- [x] **"many-to-many join" in memberships convergence note.** "the person-to-group many-to-many join via GroupMembership records." Pure developer jargon in a convergence note. (`schema/properties/memberships.yaml`)

- [x] **"record or relationship" in end_date definition.** Same issue as start_date. (`schema/properties/end_date.yaml`)

- [x] **"record or relationship" in is_active definition.** "Whether this record or relationship is currently active." (`schema/properties/is_active.yaml`)

- [x] **"associated with this record" in amount definition.** "The monetary or quantitative value associated with this record." (`schema/properties/amount.yaml`)

- [x] **"subsumes" in Grievance EN definition.** "Grievance subsumes appeals... and complaints." Logical/philosophical term. Suggested: "covers" or "includes." (`schema/concepts/grievance.yaml`)

- [x] **"instantiates" in schedule_ref property definition.** "Reference to the benefit schedule that this entitlement instantiates." OOP jargon. Suggested: "corresponds to" or "draws from." (`schema/properties/schedule_ref.yaml`)

### INFO

- [x] **"redeemable" in benefit-modality voucher value.** Mildly technical but well-understood in social protection. Acceptable. (`schema/vocabularies/benefit-modality.yaml`)

---

## Theme 5: Date property patterns are inconsistent

### FAIL

- [x] **Enrollment has 4 overlapping date fields with no documented distinction.** `enrollment_date` ("formally activated"), `start_date` ("record or relationship became effective"), `exit_date` ("closed, graduated, or suspended"), `end_date` ("record or relationship ceased to be effective"). No definition explains the difference between `enrollment_date` and `start_date`, or between `exit_date` and `end_date`. (`schema/concepts/enrollment.yaml`)

- [x] **Lifecycle concepts use incompatible date patterns.** Enrollment: `enrollment_date` + `exit_date` + `start_date` + `end_date`. Entitlement: `coverage_period_start` + `coverage_period_end`. Grievance: `submission_date` + `resolution_date`. PaymentEvent: `payment_date` only. No common pattern or stated rationale for the divergence.

- [x] **Enrollment definition conflates "registering" with "activating."** The concept says enrollment is "the process of registering... Enrollment activates benefit delivery." The `enrollment_date` says "formally activated." But enrollment-status has `pending_verification` and `waitlisted` as pre-activation states, meaning an enrollment record exists before activation. It is unclear whether `enrollment_date` captures registration or activation. (`schema/concepts/enrollment.yaml`, `schema/properties/enrollment_date.yaml`)

### WARN

- [x] **exit_date conflates permanent exit with temporary pause.** Definition: "The date on which the enrollment was closed, graduated, or suspended." But the enrollment-status vocabulary distinguishes `closed` (permanent) from `suspended` (temporary, enrollment resumes). Capturing a suspension date as an "exit date" is misleading. (`schema/properties/exit_date.yaml`)

- [x] **resolution_date conflates resolution with closure.** "The date on which the grievance was resolved or closed." The grievance-status vocabulary distinguishes `resolved` (decision issued) from `closed` (process complete, record archived). These are different lifecycle events. (`schema/properties/resolution_date.yaml`)

### INFO

- [x] **GroupMembership and Relationship both use generic start_date/end_date consistently.** No inconsistency within this pair.

- [x] **Entitlement "fulfillment" vs "delivery."** entitlement-status uses "fulfilled"; the concept definition uses "delivered" loosely. Minor but could be tightened.

---

## Theme 6: Lifecycle and status modeling issues

### WARN

- [x] **Enrollment carries is_active, is_enrolled, AND enrollment_status.** Three ways to express "this enrollment is current" with no guidance on when to use which. The purpose of `is_enrolled` (VC-specific) is documented in the property definition but not in the concept definition or in `is_active`'s definition in the Enrollment context. (`schema/concepts/enrollment.yaml`)

- [x] **enrollment-status: DHIS2 maps both COMPLETED and CANCELLED to `closed`.** These are meaningfully different outcomes (successful completion vs. administrative cancellation). Consider splitting `closed` or adding `cancelled`. (`schema/vocabularies/enrollment-status.yaml`)

- [x] **payment-status: `reconciled` mixes financial reconciliation with payment lifecycle.** The notes field says "Systems may track both a payment status and a separate reconciliation flag." Including `reconciled` alongside `pending/processing/paid/failed` mixes orthogonal concerns (one-concept-per-vocabulary principle). (`schema/vocabularies/payment-status.yaml`)

- [x] **payment-status: opencrvs maps PARTIAL to `paid`.** A partial payment is semantically distinct from a completed payment. This is an imprecise mapping. (`schema/vocabularies/payment-status.yaml`)

- [x] **payment-status: 4+ system codes collapse to both `pending` and `processing`.** openspp:issued, openspp:notpaid, openimis:CREATED, openimis:PENDING_APPROVAL all map to `pending`. Suggests `pending` may need finer granularity. (`schema/vocabularies/payment-status.yaml`)

- [x] **grievance-status: 4 system codes collapse to `under_review`.** openspp:in_progress, openspp:waiting, openimis:Inprogress, openimis:Review. May conflate "assigned to case worker" with "under active investigation." (`schema/vocabularies/grievance-status.yaml`)

- [x] **relationship-type: 4 systems map to `other` for codes like `non_relative` and `NOT RELATED`.** This is a distinct concept worth promoting to a named code. (`schema/vocabularies/relationship-type.yaml`)

- [x] **group-type: openIMIS maps Nuclear, Extended, and Single Parent families all to `family`.** 5 system codes collapse to one canonical value. Consider whether `family` needs sub-types. (`schema/vocabularies/group-type.yaml`)

- [x] **gender-type: 4 systems map to `other`.** The `other` code is a legitimate concept (non-binary/third gender), but the definition should name these use cases explicitly rather than being a catch-all. (`schema/vocabularies/gender-type.yaml`)

---

## Theme 7: Vocabulary domain scoping and standards gaps

### FAIL (per checklist: "at least one system_mappings entry exists")

- [x] **country: no system_mappings.** Uses `same_standard_systems: [openspp]` instead. Trial-use readiness gate satisfied by `standard: ISO 3166-1`, but checklist requires system_mappings. (`schema/vocabularies/country.yaml`)

- [x] **currency: no system_mappings.** Same pattern as country. Gate satisfied by `standard: ISO 4217`. (`schema/vocabularies/currency.yaml`)

- [x] **language: no system_mappings.** Same pattern. Gate satisfied by `standard: ISO 639-3`. (`schema/vocabularies/language.yaml`)

- [x] **occupation: no system_mappings.** Same pattern. Gate satisfied by `standard: ISCO-08`. (`schema/vocabularies/occupation.yaml`)

- [x] **grievance-type: no system_mappings and weakest evidence base.** Only `references` (ISO 10002, World Bank Sourcebook) satisfies the readiness gate. Zero system validation of canonical codes. (`schema/vocabularies/grievance-type.yaml`)

### WARN (systematic domain scoping gap)

- [x] **enrollment-status: no `domain` field.** Used exclusively by Enrollment (`domain: sp`). Should carry `domain: sp` per design rule. (`schema/vocabularies/enrollment-status.yaml`)

- [x] **entitlement-status: no `domain` field.** Used exclusively by Entitlement (`domain: sp`). (`schema/vocabularies/entitlement-status.yaml`)

- [x] **grievance-status: no `domain` field.** Used exclusively by Grievance (`domain: sp`). (`schema/vocabularies/grievance-status.yaml`)

- [x] **grievance-type: no `domain` field.** Used exclusively by Grievance (`domain: sp`). (`schema/vocabularies/grievance-type.yaml`)

- [x] **delivery-channel: no `domain` field.** SP-specific vocabulary with no cross-domain application. (`schema/vocabularies/delivery-channel.yaml`)

- [x] **payment-status: no `domain` field.** SP-specific vocabulary. (`schema/vocabularies/payment-status.yaml`)

- [x] **benefit-modality: no `domain` field.** SP-specific vocabulary. (`schema/vocabularies/benefit-modality.yaml`)

### WARN (other standards/mapping gaps)

- [x] **gender-type: no `standard` or `references` field.** Only system_mappings satisfies the gate. The YAML comment mentions FHIR R5 Gender Harmony and SEMIC Core Person 2.1.1 but these are not in machine-readable `references` fields. (`schema/vocabularies/gender-type.yaml`)

- [x] **gender-type: definition references "social protection systems" but vocabulary is universal.** "...based on what social protection systems actually record." Universal vocabularies should not anchor to a specific domain. (`schema/vocabularies/gender-type.yaml`)

- [ ] **entitlement-status: only 1 system in system_mappings (openspp).** Thin evidence base for 6 canonical values. DHIS2, openIMIS, and DCI all handle entitlement states but none are mapped. (`schema/vocabularies/entitlement-status.yaml`)

- [ ] **group-role: only 2 systems mapped, openspp has only 1 code (head).** Thin evidence for 10 canonical values. (`schema/vocabularies/group-role.yaml`)

- [x] **marital-status: `standard.uri` is a synthetic URN that does not resolve.** `urn:un:unsd:pop-census:marital-status` has no published document at this path. Should be replaced with the actual publication URL. (`schema/vocabularies/marital-status.yaml`)

- [ ] **identifier-type: FHIR R4 JHN (Jurisdictional Health Number) has `unmapped_reason: not_yet_mapped`.** Incomplete mapping that should be resolved. (`schema/vocabularies/identifier-type.yaml`)

- [x] **marital-status: FHIR R4 P (Polygamous) unmapped.** Polygamy is recognized in many target countries. Should be resolved (add canonical value or justify `no_equivalent`). (`schema/vocabularies/marital-status.yaml`)

- [x] **delivery-channel: openimis F (Funding) maps to `other`.** Funding is semantically distinct (program-to-program transfer, not beneficiary delivery). `no_equivalent` may be more appropriate. (`schema/vocabularies/delivery-channel.yaml`)

---

## Theme 8: Missing trilingual definitions on vocabulary values

### WARN

- [x] **marital-status: all 6 values missing `definition.fr` and `definition.es`.** Only English definitions present. (`schema/vocabularies/marital-status.yaml`)

- [x] **sex: all 4 values missing `definition.fr` and `definition.es`.** Only English definitions present. (`schema/vocabularies/sex.yaml`)

### INFO

- [x] **country: 248 of 249 values missing `label.fr` and `label.es`.** Expected for a synced vocabulary where ISO 3166-1 does not supply translations. (`schema/vocabularies/country.yaml`)

- [x] **currency: 177 of 178 values missing `label.fr` and `label.es`.** Expected for a synced vocabulary. (`schema/vocabularies/currency.yaml`)

- [x] **language: 7,926 of 7,927 values missing `label.fr` and `label.es`.** Expected for a synced vocabulary of this scale. (`schema/vocabularies/language.yaml`)

- [x] **occupation: all 619 values missing `label.fr` and `label.es`.** ISCO-08 is published in English only. (`schema/vocabularies/occupation.yaml`)

---

## Theme 9: Structural and reference integrity

### FAIL

- [x] **conditionality_type property: broken vocabulary path.** References `conditionality-type` (root-level), actual file at `schema/vocabularies/sp/conditionality-type.yaml`. Affects draft Program concept only, not the 14 trial-use concepts. (`schema/properties/conditionality_type.yaml`)

- [x] **targeting_approach property: broken vocabulary path.** References `targeting-approach` (root-level), actual file at `schema/vocabularies/sp/targeting-approach.yaml`. Same scope as above. (`schema/properties/targeting_approach.yaml`)

### WARN

- [x] **Event concept has only 1 property (`identifiers`).** Abstract supertype with 7 subtypes but no shared temporal or provenance properties to inherit. If Event is meant to carry common properties (occurred_at, event_type), they are missing. (`schema/concepts/event.yaml`)

### INFO

- [x] **4 concepts lack `external_equivalents`.** Household, Event, PaymentEvent, Grievance. May be legitimate (no relevant external standard), but worth verifying.

- [x] **2 orphan vocabularies unreferenced by any property.** `region.yaml` and `script.yaml` exist in `schema/vocabularies/` but no property declares `vocabulary: region` or `vocabulary: script`. Both are draft, likely added during standard syncing for future use.

- [x] **Subtype/supertype symmetry passes.** Full bidirectional check across all 28 concepts found no asymmetry. No action needed.

- [x] **All property references resolve.** Every property ID in every concept's `properties` array has a corresponding file. No action needed.

---

## Theme 10: Shared property definitions too generic for context

### WARN

- [x] **`name` property says "of the person" but appears on Party (which includes Group).** Should say "of the person or group." (`schema/properties/name.yaml`)

- [x] **`identifiers` property says "assigned to this person" but appears on Party.** Should say "assigned to this person or group." (`schema/properties/identifiers.yaml`)

- [x] **`amount` definition is too generic.** "The monetary or quantitative value associated with this record." On Entitlement, `amount` is always monetary (confirmed by companion `currency` property). "Associated with this record" is database jargon. (`schema/properties/amount.yaml`)

### INFO

- [x] **relationship-type: very high many-to-one collapse ratios.** child (17 codes), parent (20), grandparent (20), sibling (22), in_law (12). Driven by DCI's granular gendered codes. This is a documented, intentional design choice (broad canonical categories). (`schema/vocabularies/relationship-type.yaml`)

- [x] **relationship-type: `payment_proxy` and `survivor` have `domain: sp` annotations (2 of 14 values).** Within the 1/3 threshold. (`schema/vocabularies/relationship-type.yaml`)

- [x] **enrollment-status: `graduated` has `domain: sp` annotation (1 of 6 values).** Within the 1/3 threshold. (`schema/vocabularies/enrollment-status.yaml`)

- [x] **PaymentEvent concept: "retries after failure" is informal.** Groups retries (corrective) with split payments and multi-tranche (planned) as equivalent patterns. Minor semantic issue. (`schema/concepts/payment-event.yaml`)

---

## Summary

| Severity | Count |
|----------|-------|
| FAIL | 25 |
| WARN | 43 |
| INFO | 18 |
| **Total** | **86** |

### FAIL by theme

| Theme | Count |
|-------|-------|
| 1. Definition content diverges across languages | 3 |
| 2. French accent and encoding issues | 2 |
| 3. Terminology inconsistency across concepts | 2 |
| 4. Developer jargon in definitions | 7 |
| 5. Date property patterns inconsistent | 3 |
| 7. Vocabulary domain scoping and standards gaps | 5 |
| 9. Structural and reference integrity | 2 |
| Other themes | 1 |
