# DHIS2 external mapping

Meta-model mapping between PublicSchema and DHIS2's tracker + metadata API.

## What's here

- `convert.py` — dual-source converter (OpenAPI + metadata API). Runs offline on the files in `extracted/`, or can refresh them via `--fetch`.
- `matching.yaml` — the curated mapping: `concept_matches:`, `matches:` (vocabularies), and `no_match:` covering every v2 concept and vocabulary.
- `extracted/` — raw sources and generated outputs. Committed (see `.gitignore` exception) so the mapping is reproducible offline.

### Files under `extracted/`

| File | Source | Purpose |
|---|---|---|
| `openapi.json` | `/api/openapi.json` on demo | Structural schemas for tracker + metadata entities |
| `tracked-entity-types.json` | `/api/trackedEntityTypes.json` | TET definitions with base attributes |
| `programs.json` | `/api/programs.json` | Programs with their TEAs |
| `option-sets.json` | `/api/optionSets.json` | Option-set values referenced by attributes |
| `entities.json` | generated | 17 distilled entities (Person from metadata, 16 from OpenAPI) |
| `enums.json` | generated | 9 distilled enums (7 OpenAPI enums + 2 demo option sets) |

## Scope

- **In scope**: DHIS2 meta-model — tracker operational types (TrackerEnrollment, TrackerEvent, TrackerRelationship, TrackerDataValue, TrackerNote) and configuration types (Program, ProgramStage, TrackedEntityType, TrackedEntityAttribute, OrganisationUnit, RelationshipType, DataElement).
- **Out of scope**: the aggregate analytics layer (DataSet, indicators, category option combos), and the metadata-packages catalogue (HIV tracker, WHO HMIS, etc.), which is deployment configuration content rather than meta-model.

## Refreshing the data

From the repo root:

```bash
uv run python external/dhis2/convert.py --fetch
```

This downloads `openapi.json` and the three metadata endpoints from the DHIS2 demo server using Basic auth `admin:district`, then regenerates `entities.json` and `enums.json`.

To point at a different demo version:

```bash
uv run python external/dhis2/convert.py --fetch --version stable-2-42-4
```

To re-convert without re-fetching (e.g., after tweaking the allowlists):

```bash
uv run python external/dhis2/convert.py
```

Current pinned version: `stable-2-42-4` on `play.im.dhis2.org`.

## Instance-variability caveat

DHIS2 is a platform. Most domain vocabularies (gender, marital status, occupation, education levels, identifier types, facility types) are configured per-deployment as TrackedEntityAttributes bound to option sets, not as fixed core enums. The option sets captured in `extracted/option-sets.json` and surfaced in `extracted/enums.json` are demo content. The demo's `Gender` option set has only Male/Female; `Civil status` has only 2 values. Production deployments configure richer vocabularies.

The value mappings in `matching.yaml` and in `schema/vocabularies/*.yaml system_mappings.dhis2` are anchored to:

- Core OpenAPI enums (stable across deployments): `EnrollmentStatus`, `EventStatus`, `ProgramType`, `ValueType`, `FeatureType`, `AccessLevel`, `RelationshipEntity`.
- Demo option sets (instance-specific): `Gender`, `Civil status`.

Use the OpenAPI-enum mappings with medium confidence; use the option-set mappings with low confidence.

## Vocabulary-mapping truth

The build-time truth for vocabulary value mappings lives in:

- `schema/vocabularies/gender-type.yaml` — `system_mappings.dhis2`
- `schema/vocabularies/marital-status.yaml` — `system_mappings.dhis2`
- `schema/vocabularies/sp/enrollment-status.yaml` — `system_mappings.dhis2`

The `matches:` entries in this directory's `matching.yaml` are the editorial prose version. They must agree with the vocabulary files above; the vocabulary files drive the build.
