# Changelog

All notable changes to PublicSchema are recorded here. The project follows
semver on `schema/_meta.yaml`. Per-entity maturity (draft / candidate /
normative) is tracked independently; see `docs/versioning-and-maturity.md`.

## 0.3.0 (2026-04-20)

### Structural changes

- **CRVSPerson renamed to `crvs/Person`** (ADR-018). The build pipeline now
  keys concepts by composite `(domain, id)`, so the ADR-014 naming exception
  is no longer needed. Filename stays `crvs-person.yaml` to avoid filesystem
  collision with root `person.yaml`. Site components show a domain prefix
  when the short id collides across domains.
- **MarriageTermination collapsed** from abstract supertype plus Divorce and
  Annulment subtypes into a single concrete `MarriageTermination` concept
  with a `termination_type` vocabulary (`divorce`, `annulment`). Divorce and
  Annulment concept YAMLs are deleted.
- **`CivilStatusDocument`** added as a new abstract intermediate categoriser
  under the `crvs` domain. `FamilyRegister` and `Certificate` now declare it
  as their supertype and inherit shared `issuing_authority` and `issue_date`.
- **Parental role decoupled from gender** (ADR-019). The `parental-role`
  vocabulary is rewritten to four gender-neutral values: `biological`,
  `gestational`, `legal`, `adoptive`. A new `parent-establishment-basis`
  vocabulary captures the legal route by which parentage was established.
  Two new properties land on `Parent`: `establishment_basis` (vocab-backed)
  and `certificate_label` (free text for jurisdictions that still require
  gendered or positional labels on printed certificates).
- **ServicePoint siblings** added at root: `School`, `WaterPoint`,
  `RegistrationOffice`, each with their own type vocabulary. ServicePoint
  and its subtypes intentionally stay at root rather than being split across
  domains; they are classified by service-point type, not URI domain.
- **Vocabulary renames** for clarity (no semantic change):
  - `cognition-frequency-3pt` &rarr; `cognition-remembering-frequency`
  - `functional-intensity-3pt` &rarr; `functional-intensity`
  - `past-3-months-frequency` &rarr; `symptom-period-frequency`
  - `symptom-frequency` &rarr; `cfm-symptom-frequency`
  - `instrument-id` &rarr; `instrument-code`

### Maturity promotions

**Draft &rarr; candidate (concepts):** `VitalEvent`, `Birth`, `Death`,
`Marriage`, `MarriageTermination`, `crvs/Person`, `IdentityDocument`,
`Profile`, `FunctioningProfile`, `SocioEconomicProfile`, `Family`.

**Draft &rarr; candidate (vocabularies):** `acute-malnutrition-severity`,
`status-in-employment`, `wg-ss-domain`, `hazard-type`, `employment-status`,
`literacy`, `document-status`, `document-type`, `cooking-fuel`,
`floor-material`, `roof-material`, `wall-material`, `water-source`,
`water-service-level`, `sanitation-facility`, `sanitation-service-level`,
`dwelling-type`, `occupancy-arrangement`.

**Candidate &rarr; normative (concepts):** `Agent`, `Party`, `Event`, `Group`,
`GroupMembership`, `Address`, `Location`.

**Draft &rarr; normative (vocabularies):** `script` (ISO 15924), `region`
(UN M49). Both externally synced, value sets closed by source standards.

**Candidate &rarr; normative (vocabularies):** `legal-basis` (GDPR Art 6(1)),
`special-category-basis` (GDPR Art 9).

### Breaking changes at draft level

Every breaking change below affects draft-maturity entities only, where
breaking changes are permitted per ADR-002.

- Renaming `CRVSPerson` to `Person` (under `crvs`) changes the URI for
  every reference.
- Collapsing Divorce and Annulment into `MarriageTermination` removes both
  concept URIs; data keyed on them must move to `MarriageTermination` with
  a `termination_type` discriminator.
- The `parental-role` vocabulary replaces its gendered codes (`biological_mother`,
  `biological_father`, `legal_mother`, `legal_father`, `adoptive_mother`,
  `adoptive_father`, `surrogate_mother`) with four gender-neutral codes.
  Systems that relied on the old codes must migrate to the combination of
  `parental_role` + `establishment_basis` + optional `certificate_label`.
- Five vocabulary renames listed above change vocabulary URIs.

### New ADRs

- ADR-018: CRVSPerson renamed to crvs/Person (supersedes ADR-014).
- ADR-019: Parental role vocabulary decoupled from gender.

### Known technical debt

- OpenIMIS FamilyType codes `N` / `E` / `S` currently map to `group-type: family`
  but may more accurately map to `household`. An audit is deferred to a
  post-0.3.0 release.
- FHIR v3 RoleCode has no gender-neutral "gestational parent" code; `GESTM`
  is female-coded. The `gestational` value in our `parental-role` vocabulary
  fills the gap at the schema level; systems mapping to FHIR emit `GESTM`
  when the gestational parent is female and use `PRN` with a local extension
  otherwise. Documented in ADR-019.
- `FamilyRegister` declares both the inherited `issuing_authority` /
  `issue_date` (from its `CivilStatusDocument` supertype) and its own
  `register_authority` / `creation_date`. The register book and a register
  extract may legitimately carry different authorities and dates, but the
  semantic split is not yet documented. A post-0.3.0 audit will either
  consolidate the pair or clarify the distinction in the property definitions.
