# ADR-006: Extract observation-shaped data into a Profile hierarchy

**Status:** Accepted

## Context

Three structural problems bundled together on the v2 schema:

1. Person carried about 45 Washington Group / UNICEF Child Functioning Module items and about 7 anthropometric measurements as if they were attributes of identity. They are not: they are point-in-time observations, age-gated by instrument, often caregiver-reported. Washington Group analytic guidance treats them as survey instrument outputs, not person labels.
2. Household carried about 13 socio-economic and dwelling properties (dwelling type, floor/wall/roof material, water source, sanitation, cooking fuel, electricity, assets, ICT access, income source, food security, settlement type) as if they were attributes of household identity. They are survey responses at a point in time.
3. `AssessmentFramework` and `AssessmentEvent` conflated two distinct acts. `AssessmentEvent` was defined as "a subject's data is processed through a framework to generate a score" (`raw_score`, `assessment_band`), but it was also used as a home for instrument administration that does not produce a score. Peer projects (FHIR, CCCEV, HL7 v3 RIM) separate instrument administration from scoring.

Three independent expert reviews (`reviews/person-refactor/schema-expert.md`, `practitioner-expert.md`, `methodology-expert.md`) agreed on the shape of the fix. The practitioner review confirmed that operational MIS systems (UNHCR proGres, Brazil Cadastro Unico, Philippines Listahanan, Kenya SR-NIS, Indonesia DTKS, CommCare CMAM) already separate summary flags on the person record from item-level evidence on separate survey or measurement records. Keeping the item-level columns on Person and Household misaligned with how those systems actually work.

## Decision

1. Introduce an **`Instrument`** registry at the root namespace. `Instrument` catalogs data-collection tools (WG-SS, WG-ES, CFM 2-4, CFM 5-17, SMART anthropometry protocol, PMT questionnaires, national registration forms). Properties: `name`, `version`, `publisher`, `publication_url`, `item_set`, `language_of_administration`.
2. Introduce an abstract **`Profile`** concept under `Event`, with three concrete subtypes: **`SocioEconomicProfile`**, **`FunctioningProfile`**, and **`AnthropometricProfile`**. Profile carries shared administrative context (`subject`, `observation_date`, `performed_by`, `instrument_used`, `administration_mode`, `respondent`, `respondent_relationship`, `items_asked`).
3. **Rename `AssessmentFramework` to `ScoringRule`** and narrow its definition to scoring methodologies (PMT formulas, PPI, multidimensional poverty indices, WG cutoffs, WHO growth-standard thresholds). **Rename `AssessmentEvent` to `ScoringEvent`** and narrow it to applying a rule to inputs that may be one or more Profile records or inline data. Rename associated properties: `framework_used` to `rule_applied`, `assessed_entity` to `subject`, `assessment_date` to `evaluation_date`, `assessor` to `evaluator`. Add an `inputs` property on ScoringEvent for Profile references.
4. **Trim Person and Household** to their identity-shaped properties. Keep a named set of current-state categorical summaries: `functioning_status` (new), `nutrition_status` (new), `pregnancy_status`, `displacement_status` on Person; `food_security_level` on Household. Summary flags are pragmatic denormalizations for targeting and reporting workflows, not classifications. Each flag's property definition states this caveat inline.
5. Place the Profile hierarchy, Instrument, ScoringRule, and ScoringEvent at the **root URI namespace** (`publicschema.org/Profile`, etc.). The instruments covered are cross-domain (SP, health, humanitarian, CRVS, census, DHS, MICS, SMART). `EligibilityDecision` stays under `/sp/` because program eligibility is domain-specific.
6. Add four new vocabularies: `administration-mode` (self/proxy/assisted/mixed), `growth-reference` (who_2006/who_2007/cdc_2000/nchs_1977/other), `cutoff-rule` (who_unicef_6_59m/who_2007_school_age/sphere_pregnant/humanitarian_adult/national_protocol), `measurement-type` (recumbent/standing).
7. **No backward-compatibility shims.** No adopters are on the v2 schema yet. Deleted concepts are deleted cleanly.

## Alternatives considered

- **Keep `AssessmentFramework` name, widen it to include instruments.** Rejected: recreates the conflation this refactor removes.
- **Replace with FHIR 1:1 (`Questionnaire` / `QuestionnaireResponse` / `RiskAssessment`).** Rejected: higher naming blast radius, less aligned with vocabulary social protection adopters recognize.
- **No Profile supertype, three unrelated Event subtypes.** Rejected once three siblings existed: the shared administrative shape (subject, date, instrument, respondent, administration mode) is load-bearing for downstream validators, renderers, and credential schemas.
- **`InstrumentAdministration` or `Observation` as supertype name.** Rejected: the first is jargon, the second carries clinical flavor that social protection readers misread. `Profile` aligns with DCI's `SocioEconomicProfile` naming precedent.
- **Per-instrument concepts** (`WGSSAssessment`, `CFMAssessment`). Rejected: explodes the catalog and duplicates overlapping item sets across concept pages. Disambiguation by `instrument_used` matches FHIR's `QuestionnaireResponse` plus `Questionnaire` split and LOINC panel conventions.
- **Delete derived anthropometric status fields and compute on read.** Rejected: many programs inherit a band without the raw z-score and need to store it. Required context fields (`growth_reference`, `age_at_measurement_months`, `oedema_present`, `cutoff_rule`) fix the citation problem without requiring raw data.

## Consequences

Person and Household property lists now match their definitions as persistent identity records. Observation data has explicit time, subject, instrument, and administration context, which makes Washington Group-compliant tabulation possible (which items were asked, which respondent, which administration mode, which instrument version) and makes anthropometric data WHO-standard-citable (the growth reference used, age at measurement, and oedema status are captured).

Scoring becomes a distinct act (`ScoringEvent` + `ScoringRule`), separate from instrument administration. The same FunctioningProfile can be scored against multiple WG cutoffs without re-collecting data; a SocioEconomicProfile can be scored against multiple PMT formulas.

Because Profile subtypes may carry sensitive data (health, nutrition, poverty), selective-disclosure guidance distinguishes two credential patterns: Profile-as-subject (the holder presents evidence of a specific administration with item-level answers as disclosable claims) and Profile-as-evidence (the Person holds a derived credential whose evidence points at the Profile held by the issuer). See `docs/selective-disclosure.md`.

The existing `convergence` system_count of 1-2 (FHIR and DHIS2) reflects that most v1 MIS systems flatten observation data into the subject record. This mismatch is deliberate: the refactor is informed more by standards bodies (Washington Group, WHO, UNICEF MICS, SMART) and domain tools (CommCare CMAM, DHS, MICS) than by the v1 mapped-system set.

## Follow-on work

- A `SoftwareAgent` concept and `software_used` property, tracked separately, extend ScoringEvent and EligibilityDecision to record the software that executed a scoring or decision step. The distinction is deliberate: `evaluator` and `performed_by` carry the party accountable for the result (a human or organisation); `software_used` carries the tool that ran the computation, for reproducibility and audit. This ADR defines the Profile and scoring concepts; `software_used` is layered on top and does not change the shapes here.
- Four data-level validators remain to be implemented on top of this schema, all of which operate on sample Profile records rather than the schema itself: enforce `valid_instruments` (reject an item populated on a Profile whose `instrument_used` is not in the item's list), require `growth_reference` when any anthropometric status band is set, require `cutoff_rule` on `acute_malnutrition_status`, and require `administration_mode: proxy` when `instrument_used` is CFM 2-4 or CFM 5-17. The `valid_instruments` field on each WG/CFM/anthropometric item property is populated; the engine that consumes it is not yet in this repo.

## References

- Expert reviews: `reviews/person-refactor/schema-expert.md`, `practitioner-expert.md`, `methodology-expert.md`
- Implementation plan: `plans/profile-refactor.md`
- Washington Group Analytic Guidelines for the Creation of Disability Identifiers
- WHO Child Growth Standards (2006), WHO Growth Reference (2007), SMART Methodology
- DCI Social Registry Data Standard (`SocioEconomicProfile` peer)
