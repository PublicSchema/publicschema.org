# Plan: Vocabulary Standards Alignment

Based on research into international standards, review by two domain experts (social protection delivery practitioner + standards/interoperability architect), and cross-domain design review.

**Governing principles:** `docs/vocabulary-design-principles.md`

## Background

- Research prompt: `docs/research-prompt-vocabulary-standards.md`
- 29 vocabularies total; 12 already reference a formal standard
- PublicSchema starts with social protection but is designed to extend to health, education, CRVS, humanitarian response, and land administration
- Concepts carry a `domain` field; vocabularies do not (they are shared infrastructure across domains)

## Design decisions

### 1. No structural splits

We will not split payment-status, eligibility-status, or delivery-channel into multiple vocabularies. A single clean lifecycle vocabulary works cross-domain when the values are domain-neutral and well-scoped. If a future domain surfaces a genuine semantic conflict that cannot be resolved with value-level annotations, the split can be introduced at trial-use maturity. (Principle 2: do not split prematurely.)

### 2. Universal by default, domain-scoped by exception

Per Principle 1, vocabularies live at the root unless the same name would carry different semantics in different domains.

**Moving to `schema/vocabularies/sp/`:** conditionality-type, targeting-approach (pure SP methodology with no cross-domain equivalent).

**Renaming for disambiguation:** certainty -> event-certainty, severity -> event-severity (the bare names would collide with health/education severity and certainty scales).

**Everything else stays universal**, with domain annotations on individual values where needed.

### 3. Domain annotations on values

Per Principle 4, values that only make sense in a specific domain are annotated rather than split into a separate vocabulary:
- `graduated` in enrollment-status: `domain: sp`
- `payment_proxy` in relationship-type: `domain: sp`
- `survivor` in relationship-type: `domain: sp`

### 4. `head_of_household` removal from relationship-type

The data model is clear: `Relationship` is person-to-person (`subject_person` to `object_person`), `GroupMembership` is person-to-group (`person` to `group` with `role`). `head_of_household` describes a group role, not a dyadic relationship. Systems that map HEAD here should map through GroupMembership instead.

### 5. RRULE-based custom frequency

Add `custom` code to benefit-frequency and a new `frequency_rule` property accepting RFC 5545 RRULE strings. Keeps simple cases simple; provides a standards-based escape hatch for complex schedules across all domains.

### 6. `references` field for vocabularies without a formal `standard`

Per Principle 3, every vocabulary should declare its relationship to the best available standard. Use a `references` list distinct from the existing `standard` field used for formal code systems with sync capability.

```yaml
references:
  - name: "ISO 20022 ExternalPaymentTransactionStatus1Code"
    uri: "https://www.iso20022.org/catalogue-messages/additional-content-messages/external-code-sets"
    relationship: superset  # superset | subset | partial_overlap | structural_pattern | prose_guidance
    machine_readable: true
    notes: "Optional clarification."
```

### 7. Expressiveness over minimalism

Per the project principle "everything is optional," vocabularies should offer the expressiveness that any adopting domain might need. Not all systems will use all values, and that's fine. A value that exists but goes unused is better than a gap that forces systems to overload another code. (Example: `rejected` in payment-status may not be used by SP systems that don't distinguish it from `cancelled`, but health insurance systems need it.)

## Open questions

- [ ] Should `service_point` stay in delivery-channel? It could be seen as a location type rather than a delivery mechanism. **Current decision: keep it.** Revisit when more system mappings validate or challenge it.
- [ ] Should we add `public_works` / `workfare` to benefit-modality? SPDCI maps "Work Opportunity" to `service`. **Current decision: no**, document as a known mapping compromise.
- [ ] Should `enrolled` replace `active` in enrollment-status? **Current decision: keep `active`** (more generic cross-domain; DHIS2, openIMIS, SPDCI all use "active").

---

## Phase 0: Structural changes

### 0.1 Rename certainty and severity for disambiguation

Per Principle 5, bare names that would collide across domains must be disambiguated.

**Files:**
- Rename `schema/vocabularies/certainty.yaml` to `schema/vocabularies/event-certainty.yaml`, change `id: certainty` to `id: event-certainty`
- Rename `schema/vocabularies/severity.yaml` to `schema/vocabularies/event-severity.yaml`, change `id: severity` to `id: event-severity`
- Update `schema/properties/certainty.yaml`: change `vocabulary: certainty` to `vocabulary: event-certainty`
- Update `schema/properties/severity.yaml`: change `vocabulary: severity` to `vocabulary: event-severity`
- Property names (`certainty`, `severity`) and their usage on HazardEvent stay unchanged. The property describes what it captures; the vocabulary describes the value set.

### 0.2 Move SP-specific vocabularies to domain subfolder

**Files:**
- Move `schema/vocabularies/conditionality-type.yaml` to `schema/vocabularies/sp/conditionality-type.yaml`
- Move `schema/vocabularies/targeting-approach.yaml` to `schema/vocabularies/sp/targeting-approach.yaml`
- Update any property files that reference these vocabulary IDs (check `conditionality_type.yaml` and `targeting_approach.yaml` in properties)
- Update build pipeline if vocabulary paths are hardcoded

### 0.3 Make vocabulary definitions domain-neutral

7 universal vocabularies currently say "social protection" in their definitions. Since they are shared across all domains, generalize. (The 2 vocabularies moving to `sp/` can keep domain-specific language.)

| File | Current phrasing (en) | Proposed phrasing (en) |
|---|---|---|
| `eligibility-status.yaml` | "...for a social protection program" | "...for a program or service" |
| `enrollment-status.yaml` | "...in a social protection program" | "...in a program" |
| `grievance-status.yaml` | "...in a social protection program" | "...in a program or service" |
| `grievance-type.yaml` | "...against a social protection program or its delivery process" | "...against a program or its delivery process" |
| `gender-type.yaml` | "...in a social protection or identity system" | "...in an identity or administrative system" |
| `group-type.yaml` | "...in a social protection system" | "...in an administrative system" |
| `identifier-type.yaml` | "...in social protection systems" | "...in administrative and service delivery systems" |

Also update fr and es translations to match, and update individual value definitions that reference "social protection" where the value is universal (e.g., `program_id` in identifier-type).

### 0.4 Generalize grievance-type value definitions

`exclusion_error` and `inclusion_error` use SP-flavored language but the concepts are universal (wrongly denied a service, wrongly given a service). Make the definitions domain-neutral.

---

## Phase 1: Bug fixes

### 1.1 Fix SPDCI relationship-type null mappings

**File:** `schema/vocabularies/relationship-type.yaml`

Many SPDCI codes map to `null` when they should map to a broader canonical code. Fix after Phase 2 adds `in_law` and `extended_family`:

- Map to `child`: DAUADOPT, SONADOPT, DAUFOST, SONFOST, DAU, SON, STPDAU, STPSON, STPCHILD, NCHILD
- Map to `parent`: ADOPTF, ADOPTM, NMTH, NFTH, STPFTH, STPMTH, FTHFOST, NPRN, STPPRN, GESTM, NMTHF, NFTHF
- Map to `sibling`: HBRO, NBRO, NSIS, HSIS, STPBRO, NSIB, HSIB, TWINBRO, TWINSIS, TWIN, FTWINBRO, ITWINBRO, FTWINSIS, ITWINSIS, FTWIN, ITWIN
- Map to `grandparent`: GGRPRN, GGRFTH, GGRMTH, MGGRFTH, PGGRFTH, PGGRMTH, MGGRPRN, PGGRPRN, MGRFTH, PGRFTH, MGRMTH, PGRMTH, MGRPRN, PGRPRN
- Map to `in_law`: CHLDINLAW, DAUINLAW, SONINLAW, PRNINLAW, FTHINLAW, MTHINLAW, SIBINLAW, BROINLAW, SISINLAW
- Map to `extended_family`: AUNT, MAUNT, PAUNT, UNCLE, MUNCLE, PUNCLE, COUSN, MCOUSN, PCOUSN, NIENEPH, NEPHEW, NEICE
- Map to `spouse`: SIGOTHR (significant other)
- Map to `other`: FRMSPS (former spouse), FAMMEMB (family member)
- Keep as `null`: SELF (self-reference), PRIMSPOUS (unclear without polygamy modeling)

### 1.2 Fix openIMIS group-role mappings

**File:** `schema/vocabularies/group-role.yaml`

Do after Phase 2 adds `grandparent`, `grandchild`, `sibling`:
- GRANDFATHER, GRANDMOTHER: remap from `parent` to `grandparent`
- GRANDSON, GRANDDAUGHTER: remap from `dependent` to `grandchild`
- BROTHER, SISTER: remap from `other_relative` to `sibling`

### 1.3 Fix French translation of `graduated` in enrollment-status

**File:** `schema/vocabularies/enrollment-status.yaml`

Current French label "Diplome" means "graduated from school." Change to "Sorti avec succes" and update the French definition.

---

## Phase 2: Value changes

### 2.1 payment-status: add `processing` and `rejected`

**File:** `schema/vocabularies/payment-status.yaml`

Add `processing` between `pending` and `paid`:
- en: "The payment instruction has been accepted by the financial intermediary and is being executed."

Add `rejected` after `failed`:
- en: "The payment was evaluated and denied based on a business or policy decision, such as a failed eligibility check or a disputed claim."

This gives a clean three-way distinction:
- `cancelled`: withdrawn before transmission (sender's proactive decision)
- `rejected`: evaluated and denied (business/policy decision)
- `failed`: attempted but technically unsuccessful

Update system mappings:
- openIMIS: remap ACCEPTED and APPROVE_FOR_PAYMENT from `pending` to `processing`. Remap REJECTED from `cancelled` to `rejected`.
- OpenSPP: remap `sent` from `pending` to `processing`

### 2.2 enrollment-status: add `waitlisted`, annotate `graduated`

**File:** `schema/vocabularies/enrollment-status.yaml`

Add `waitlisted`:
- en: "The applicant has been verified as eligible but is awaiting an available program slot due to capacity or budget constraints."

Annotate `graduated` with `domain: sp`.

Tighten `closed` definition:
- en: "The enrollment has been permanently ended for administrative reasons such as ineligibility, non-compliance, voluntary withdrawal, or death. Use `graduated` when exit is through program-defined criteria."

### 2.3 eligibility-status: remove `appealing` and `expired`, add `under_review`

**File:** `schema/vocabularies/eligibility-status.yaml`

Remove `appealing` (process state, not eligibility outcome; model as Grievance or appeal sub-process).

Remove `expired` (temporal metadata derivable from `valid_until` on EligibilityDecision; embeds SP-specific temporal logic into a cross-domain vocabulary).

Add `under_review`:
- en: "The eligibility assessment is actively being evaluated by a case worker or review body."

Resulting vocabulary (5 values): `pending`, `under_review`, `eligible`, `conditional`, `ineligible`

### 2.4 group-role: add `sibling`, `grandparent`, `grandchild`

**File:** `schema/vocabularies/group-role.yaml`

- `sibling`: "A brother or sister of the group head or their spouse."
- `grandparent`: "A parent of the group head's parent, living in the same group."
- `grandchild`: "A child of the group head's child, living in the same group."

Add to vocabulary-level definition: "Roles are defined relative to the group's reference person (head)."

### 2.5 identifier-type: add `tax_id`, `drivers_license`, `marriage_certificate`, `death_certificate`

**File:** `schema/vocabularies/identifier-type.yaml`

- `tax_id`: "A tax identification number assigned by a revenue or fiscal authority."
- `drivers_license`: "A government-issued permit to operate motor vehicles, commonly used as identification."
- `marriage_certificate`: "An official record of a marriage issued by a civil registry or religious authority."
- `death_certificate`: "An official record of a death issued by a civil registry or health authority."

Update system mappings:
- OpenSPP: remap `tax_id` from `other` to `tax_id`
- openIMIS: remap D from `other` to `drivers_license`
- FHIR R4: remap TAX to `tax_id`, DL to `drivers_license`
- SPDCI: remap MRN to `marriage_certificate`, DRN to `death_certificate`

### 2.6 benefit-modality: add `insurance`

**File:** `schema/vocabularies/benefit-modality.yaml`

- `insurance`: "Enrollment in or subsidization of an insurance scheme (health, crop, social) as the benefit provided to the beneficiary."

Update SPDCI mapping: remap code 6 ("Insurance") from `null` to `insurance`.

### 2.7 delivery-channel: remove `direct_distribution`, rename `cash_in_hand`

**File:** `schema/vocabularies/delivery-channel.yaml`

- Remove `direct_distribution` (conflates channel with modality; use `service_point` + `in_kind` instead)
- Rename `cash_in_hand` to `cash`
- Update openIMIS mapping: code C maps to `cash`

### 2.8 benefit-frequency: add `custom`, rename `biweekly`

**File:** `schema/vocabularies/benefit-frequency.yaml`

- Rename `biweekly` to `every_two_weeks` (English ambiguity)
- Add `custom`: "A recurrence schedule not covered by the predefined frequencies, specified as an iCalendar RRULE (RFC 5545) in the frequency_rule property."

### 2.9 relationship-type: remove `head_of_household`, add `in_law` and `extended_family`, annotate SP values

**File:** `schema/vocabularies/relationship-type.yaml`

Remove `head_of_household` (group-role, not person-to-person relationship).

Add:
- `in_law`: "A person related through marriage rather than by blood, such as a parent-in-law, child-in-law, or sibling-in-law."
- `extended_family`: "A family member beyond the immediate kinship categories (e.g. aunt, uncle, cousin, niece, nephew) where the specific type is not recorded."

Annotate with `domain: sp`: `payment_proxy`, `survivor`.

Update system mappings:
- OpenSPP: remap `child_in_law`, `parent_in_law` to `in_law`. Remove `head` (belongs in GroupMembership).
- openIMIS: remove `HEAD` (belongs in GroupMembership).
- SPDCI: remap all in-law codes to `in_law`, `EXT` to `extended_family`, aunt/uncle/cousin/niece/nephew to `extended_family`.

### 2.10 grievance-status: add `withdrawn`

**File:** `schema/vocabularies/grievance-status.yaml`

- `withdrawn`: "The complainant has voluntarily withdrawn the grievance before resolution."

---

## Phase 3: New property for custom frequency

### 3.1 Create `frequency_rule` property

**File:** `schema/properties/frequency_rule.yaml` (new)

```yaml
id: frequency_rule
maturity: draft

definition:
  en: "An iCalendar recurrence rule (RFC 5545 RRULE) specifying a custom schedule. Used when the frequency property is set to 'custom'."
  fr: "Une regle de recurrence iCalendar (RRULE RFC 5545) specifiant un calendrier personnalise. Utilisee lorsque la propriete frequency est definie sur 'custom'."
  es: "Una regla de recurrencia iCalendar (RRULE RFC 5545) que especifica un calendario personalizado. Se utiliza cuando la propiedad frequency se establece en 'custom'."

type: string
cardinality: single
vocabulary: null
references:
  - name: "RFC 5545 - Internet Calendaring and Scheduling (iCalendar)"
    uri: "https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10"
domain_override: null

convergence:
  system_count: 0
  total_systems: 5
```

### 3.2 Add `frequency_rule` to Entitlement concept

**File:** `schema/concepts/entitlement.yaml`

Add `frequency_rule` to the properties list, alongside `frequency`.

---

## Phase 4: Add `references` metadata

### 4.1 payment-status
```yaml
references:
  - name: "ISO 20022 ExternalPaymentTransactionStatus1Code"
    uri: "https://www.iso20022.org/catalogue-messages/additional-content-messages/external-code-sets"
    relationship: superset
    machine_readable: true
    notes: "ISO 20022 defines granular interbank processing states. This vocabulary is a deliberate high-level simplification. May split into processing and settlement dimensions at trial-use maturity as cross-domain use cases require finer granularity."
  - name: "Mojaloop FSPIOP TransferState"
    uri: "https://docs.mojaloop.io/technical/api/fspiop/logical-data-model.html"
    relationship: partial_overlap
    machine_readable: true
```

### 4.2 enrollment-status
```yaml
references:
  - name: "HL7 FHIR EpisodeOfCare.status"
    uri: "https://build.fhir.org/codesystem-episode-of-care-status.json.html"
    relationship: structural_pattern
    machine_readable: true
    notes: "FHIR's episode lifecycle informed the structure."
  - name: "World Bank Social Protection Delivery Systems Framework"
    uri: "https://thedocs.worldbank.org/en/doc/147511529959939838-0160022017/original/11amMarch9DeliverySystemsFrameworkCORECOURSEWITHCLICKERSSENT8March2017.pdf"
    relationship: prose_guidance
    machine_readable: false
```

### 4.3 eligibility-status
```yaml
references:
  - name: "HL7 FHIR CoverageEligibilityResponse"
    uri: "https://build.fhir.org/coverageeligibilityresponse-definitions.html"
    relationship: structural_pattern
    machine_readable: true
    notes: "FHIR separates eligibility outcome from processing status. This vocabulary keeps both in a single lifecycle. If cross-domain adoption surfaces a genuine conflict, the split can be introduced."
```

### 4.4 delivery-channel
```yaml
references:
  - name: "GovStack Payments Building Block"
    uri: "https://specs.govstack.global/payments/2-description"
    relationship: structural_pattern
    machine_readable: false
    notes: "GovStack distinguishes origin channel from delivery instrument. This vocabulary focuses on delivery instrument only."
  - name: "GSMA Mobile Money API"
    uri: "https://developer.mobilemoneyapi.io/"
    relationship: partial_overlap
    machine_readable: true
```

### 4.5 benefit-modality
```yaml
references:
  - name: "CaLP Network Glossary"
    uri: "https://www.calpnetwork.org/resources/glossary-of-terms/"
    relationship: partial_overlap
    machine_readable: false
  - name: "WFP Transfer Modality Framework"
    uri: "https://executiveboard.wfp.org/document_download/WFP-0000148946"
    relationship: partial_overlap
    machine_readable: false
```

### 4.6 benefit-frequency
```yaml
references:
  - name: "ISO 20022 EventFrequency1Code"
    uri: "https://www.iso20022.org/catalogue-messages/additional-content-messages/external-code-sets"
    relationship: partial_overlap
    machine_readable: true
    notes: "ISO 20022 frequency codes map to monthly, quarterly, semi_annually, annually. This vocabulary includes additional values not in ISO 20022."
  - name: "RFC 5545 - iCalendar RRULE"
    uri: "https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10"
    relationship: structural_pattern
    machine_readable: true
    notes: "The 'custom' code uses RRULE format."
```

### 4.7 group-role
```yaml
references:
  - name: "UN Principles and Recommendations for Population and Housing Censuses (Rev.3)"
    uri: "https://unstats.un.org/unsd/demographic-social/Standards-and-Methods/files/Principles_and_Recommendations/Population-and-Housing-Censuses/Series_M67rev3-E.pdf"
    relationship: partial_overlap
    machine_readable: false
    notes: "UN census guidance defines household composition using a reference-person model."
```

### 4.8 identifier-type
```yaml
references:
  - name: "HL7 FHIR Identifier Type Codes (v2-0203)"
    uri: "https://build.fhir.org/valueset-identifier-type.html"
    relationship: partial_overlap
    machine_readable: true
  - name: "ICAO Doc 9303 - Machine Readable Travel Documents"
    uri: "https://www.icao.int/publications/pages/publication.aspx?docnum=9303"
    relationship: partial_overlap
    machine_readable: false
    notes: "Covers passport, visa, and card document classes."
  - name: "MOSIP Identity Schema"
    uri: "https://docs.mosip.io/1.2.0/id-lifecycle-management/identity-management/id-schema"
    relationship: structural_pattern
    machine_readable: true
    notes: "Country-configurable document categories. This vocabulary provides a base set; implementations extend per country."
```

### 4.9 grievance-status
```yaml
references:
  - name: "ISO 10002 - Quality management, Complaints handling"
    uri: "https://www.iso.org/standard/71580.html"
    relationship: prose_guidance
    machine_readable: false
  - name: "World Bank Grievance Redress Mechanism (GRM) Guidance"
    uri: "https://openknowledge.worldbank.org/bitstreams/b4a57d20-24bf-518a-93b1-1a5db3bdbae1/download"
    relationship: prose_guidance
    machine_readable: false
```

### 4.10 relationship-type
```yaml
references:
  - name: "HL7 v3 RoleCode (PersonalRelationshipRoleType)"
    uri: "https://terminology.hl7.org/3.0.0/ValueSet-v3-PersonalRelationshipRoleType.html"
    relationship: superset
    machine_readable: true
    notes: "HL7 defines granular kinship codes (70+). This vocabulary uses broader categories."
```

### 4.11 event-severity (add standard reference)

The renamed vocabulary should keep its existing `standard` field (OASIS CAP v1.2) and system_mappings.

### 4.12 event-certainty (add standard reference)

Same as above. Keep existing `standard` field.

---

## Phase 5: Cross-references and documentation

### 5.1 Add `see_also` between overlapping vocabularies

- `group-role` <-> `relationship-type`: explain person-to-group vs person-to-person
- `delivery-channel` <-> `benefit-modality`: explain how vs what

### 5.2 Add note to `reconciled` in payment-status

Note that this is an operational state that typically follows `paid`, and systems may track both a payment status and a reconciliation flag.

### 5.3 Document identifier-type VC guidance

"For Verifiable Credential use, the identifier type alone is insufficient. Credentials must also specify the issuing jurisdiction and identifier scheme."

### 5.4 Document eligibility-status VC guidance

"For Verifiable Credential use, only terminal states (eligible, ineligible, conditional) should appear in credentials. Process states (pending, under_review) are transient."

---

## Task checklist

### Phase 0: Structural changes
- [x] Rename `certainty.yaml` to `event-certainty.yaml`, update id
- [x] Rename `severity.yaml` to `event-severity.yaml`, update id
- [x] Update `properties/certainty.yaml` vocabulary reference
- [x] Update `properties/severity.yaml` vocabulary reference
- [x] Create `schema/vocabularies/sp/` directory
- [x] Move `conditionality-type.yaml` to `sp/`
- [x] Move `targeting-approach.yaml` to `sp/`
- [x] Update property files that reference moved vocabularies
- [x] Update 7 vocabulary definitions to remove "social protection" (en, fr, es)
- [x] Update universal value definitions that reference "social protection"
- [x] Generalize `exclusion_error` and `inclusion_error` definitions in grievance-type

### Phase 1: Bug fixes
- [x] Fix SPDCI relationship-type null mappings (remap ~60 codes)
- [x] Fix openIMIS group-role mappings (grandparent, grandchild, sibling)
- [x] Fix French translation of `graduated` in enrollment-status

### Phase 2: Value changes
- [x] payment-status: add `processing` and `rejected`, update mappings
- [x] enrollment-status: add `waitlisted`, annotate `graduated` with `domain: sp`, tighten `closed`
- [x] eligibility-status: remove `appealing` and `expired`, add `under_review`
- [x] group-role: add `sibling`, `grandparent`, `grandchild`
- [x] identifier-type: add `tax_id`, `drivers_license`, `marriage_certificate`, `death_certificate`, update mappings
- [x] benefit-modality: add `insurance`, update SPDCI mapping
- [x] delivery-channel: remove `direct_distribution`, rename `cash_in_hand` to `cash`, update mapping
- [x] benefit-frequency: rename `biweekly` to `every_two_weeks`, add `custom`
- [x] relationship-type: remove `head_of_household`, add `in_law` and `extended_family`, annotate SP values, update all mappings
- [x] grievance-status: add `withdrawn`

### Phase 3: New property
- [ ] Create `frequency_rule` property (`schema/properties/frequency_rule.yaml`)
- [ ] Add `frequency_rule` to Entitlement concept

### Phase 4: References metadata
- [ ] Add `references` to payment-status
- [ ] Add `references` to enrollment-status
- [ ] Add `references` to eligibility-status
- [ ] Add `references` to delivery-channel
- [ ] Add `references` to benefit-modality
- [ ] Add `references` to benefit-frequency
- [ ] Add `references` to group-role
- [ ] Add `references` to identifier-type
- [ ] Add `references` to grievance-status
- [ ] Add `references` to relationship-type

### Phase 5: Cross-references and documentation
- [ ] Add `see_also` cross-references (group-role <-> relationship-type, delivery-channel <-> benefit-modality)
- [ ] Add note to `reconciled` in payment-status
- [ ] Add VC note to identifier-type
- [ ] Add VC guidance to eligibility-status
