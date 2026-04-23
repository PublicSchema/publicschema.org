# OpenIMIS external mapping

Vocabulary mapping between PublicSchema v2 and [openIMIS](https://github.com/openimis/openimis-be_py).

## What's here

- `matching.yaml`: the curated mapping, with `matches:` (vocabularies) and `no_match:` (v2 vocabularies with no OpenIMIS equivalent and OpenIMIS vocabularies with no v2 equivalent).
- `extracted/`: raw schema snapshots committed so the mapping is reproducible offline.
- `repo/`: shallow clone of the openIMIS meta-repo (`openimis-be_py`, gitignored at repo root). Used for build infrastructure; the social-protection modules referenced in `matching.yaml` are separate pip packages (see below).
- `repo-fhir/`: shallow clone of the openIMIS FHIR R4 module (`openimis-be-api_fhir_r4_py`, gitignored). Used to cite exact serializer and converter file paths.

PublicSchema-side value mappings (canonical codes to external codes) live on the vocabulary YAMLs under `schema/vocabularies/*.yaml system_mappings.openimis`. The `matching.yaml` here is the editorial prose companion: prose notes, gaps, confidence levels, and citations back to the FHIR module or the internal Django model.

## Mapping target: hybrid FHIR R4 + internal Django models

`matching.yaml` uses a hybrid strategy:

- **FHIR R4 surface** (`surface: fhir_r4`): concepts the openIMIS FHIR R4 module (`openimis-be-api_fhir_r4_py`) exposes. Citations point at converter and mapping files within that module. FHIR is the external integration contract for health and registry data in openIMIS.
- **Internal model** (`surface: internal_model`, `api_coverage: none`): social-protection concepts (enrollment status, payroll, benefit consumption, group roles) that live in separate Django modules with no FHIR surface. The Django model file is the canonical machine-readable source for these; they are not accessible via the FHIR API.

Rationale: openIMIS uses FHIR R4 as its primary interoperability layer for patient, group, coverage, claim, organization, location, and practitioner data. The social-protection module (`openimis-be-social_protection_py`), payroll module (`openimis-be-payroll_py`), and individual module (`openimis-be-individual_py`) were added later and expose their data through a separate GraphQL API rather than FHIR. No REST/FHIR surface exists for those concepts at this time.

Per-entry fields:

| Field | Meaning |
|---|---|
| `surface` | `fhir_r4` (exposed through the FHIR R4 module) or `internal_model` (no FHIR surface) |
| `fhir_resource` | FHIR resource type (Patient, Group, Coverage, Claim, Organization, Location, Practitioner) |
| `external_source` | For `fhir_r4` entries: path relative to `fhir_repository/fhir_branch/`. For `internal_model` entries: path within the relevant Django module repo (e.g. `social_protection/models.py`). |
| `api_coverage: none` | Flag on `internal_model` entries indicating no FHIR surface exposes this vocabulary |
| `confidence` | `high`, `medium`, or `low` |

## FHIR R4 entries

FHIR-covered concepts and which FHIR resources/converters they map to:

| PublicSchema concept/vocab | FHIR resource | Key converter file |
|---|---|---|
| Person / Insuree | Patient | `api_fhir_r4/converters/patientConverter.py` |
| Family | Group | `api_fhir_r4/converters/groupConverter.py` |
| Policy / Coverage | Coverage | `api_fhir_r4/converters/coverageConverter.py` |
| Claim | Claim + ClaimResponse | `api_fhir_r4/converters/claimConverter.py` + `claimResponseConverter.py` |
| HealthFacility / Organization | Organization | `api_fhir_r4/converters/healthFacilityOrganisationConverter.py` |
| Location | Location | `api_fhir_r4/converters/locationConverter.py` |
| ClaimAdmin / Practitioner | Practitioner + PractitionerRole | `api_fhir_r4/converters/claimAdminPractitionerConverter.py` + `claimAdminPractitionerRoleConverter.py` |
| Officer / Practitioner | Practitioner + PractitionerRole | `api_fhir_r4/converters/enrolmentOfficerPractitionerConverter.py` + `enrolmentOfficerPractitionerRoleConverter.py` |
| gender-type | Patient.gender | `api_fhir_r4/mapping/patientMapping.py#PatientCategoryMapping` |

Gender is emitted on `Patient.gender` using the FHIR `administrative-gender` CodeSystem (male/female/other/unknown), not the raw OpenIMIS tblGender codes (M/F/O).

## Internal model entries

These concepts/vocabularies have no FHIR surface in the current openIMIS release:

| PublicSchema vocab | Django source repo | Model file |
|---|---|---|
| `enrollment-status` (BeneficiaryStatus) | `openimis-be-social_protection_py` | `social_protection/models.py` |
| `group-role` (GroupIndividual.Role) | `openimis-be-individual_py` | `individual/models.py` |
| `payment-status` (BenefitConsumptionStatus) | `openimis-be-payroll_py` | `payroll/models.py` |
| `delivery-channel` (PayTypeChoices) | `openimis-be-contribution_py` | `contribution/models.py` |
| `grievance-status` (TicketStatus) | `openimis-be-grievance_social_protection_py` | `grievance/migrations/0004_auto_20230425_1638.py` |
| `event-severity` (TicketPriority) | `openimis-be-grievance_social_protection_py` | `grievance/migrations/0004_auto_20230425_1638.py` |

Each internal-model entry carries `api_coverage: none` in `matching.yaml` to make the "no FHIR surface" intent explicit.

## Refreshing the clones

The FHIR module repo is cloned into `repo-fhir/` (gitignored at the project root). From the v2 root:

```bash
git clone --depth 1 --branch develop https://github.com/openimis/openimis-be-api_fhir_r4_py external/openimis/repo-fhir
git clone --depth 1 --branch develop https://github.com/openimis/openimis-be_py external/openimis/repo
```

The individual Django module repos (social_protection, payroll, individual, contribution, grievance) are not cloned locally; they are referenced by their public GitHub URLs in `matching.yaml`.

## Cross-references with the schema

Every vocabulary with `value_mapping` in `matching.yaml` has a corresponding `system_mappings.openimis` block on its vocabulary YAML (enforced by `tests/test_openimis_mapping.py`). The value mappings must agree in both places; the vocabulary YAMLs drive the build.

No `external_equivalents.openimis` URIs are emitted on schema YAMLs for openIMIS. OpenIMIS alignment is purely value-level (code-to-code) rather than URI-level.
