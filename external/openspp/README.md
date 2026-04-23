# OpenSPP external mapping

Vocabulary mapping between PublicSchema v2 and [OpenSPP](https://github.com/OpenSPP/OpenSPP2) 19.0.

## What's here

- `matching.yaml`: the curated mapping, with `matches:` (vocabularies) and `no_match:` (v2 vocabularies with no OpenSPP equivalent and OpenSPP vocabularies with no v2 equivalent).
- `extracted/`: raw Odoo vocabulary XML snapshots and selection-field inventories, committed so the mapping is reproducible offline.

PublicSchema-side value mappings (canonical → external codes) live on the vocabulary YAMLs under `schema/vocabularies/*.yaml system_mappings.openspp`. The `matching.yaml` here is the editorial prose companion: prose notes, gaps, confidence, and citations back to the API or internal model.

## Mapping target: OpenSPP REST API v2

`matching.yaml` targets the public REST API v2 surface (`/api/v2/spp/...`), not internal Odoo models. The API is documented as `development_status: Production/Stable` with OAuth 2.0 auth and an auto-generated OpenAPI schema; Pydantic schemas live under `spp_api_v2*/schemas/`.

Rationale:
- The API is the external integration contract; internal Odoo models are implementation detail and can change between releases.
- For most vocabularies, the API passes the XML source through verbatim via `GET /api/v2/spp/Vocabulary/{uri}`, so the mapping is effectively the same as the internal vocabulary but with an API-addressable endpoint.
- For Pass-B enumerations (ProgramMembership.status, Entitlement.entitlementType, etc.), the Pydantic schema's `Literal` pattern is a stricter contract than the underlying Odoo selection field.

Per-entry fields:

| Field | Meaning |
|---|---|
| `surface` | `rest_api_v2` (exposed through the API) or `internal_model` (no API surface) |
| `external_source` | Path relative to `source_repository/source_branch/`. For passthroughs this is the XML file; for Pass-B enums this is the Pydantic schema (`ClassName.field`); for internal-model entries this is the Odoo model file. |
| `api_endpoint` | REST path integrators consume (vocabulary passthroughs) |
| `api_field` | Pydantic schema attribute (Pass-B enums and typed fields) |
| `api_coverage: none` | Flag on `internal_model` entries indicating no API surface exposes this vocabulary |
| `confidence` | `high`, `medium`, or `low` |
| `same_standard` | True when both sides reference the same international standard (ISO, UNESCO, ILO, etc.) |

## Entries flagged `internal_model`

A handful of OpenSPP vocabularies have no API surface in the current v2 API:

- `gender-type` (res.partner.gender text enum): the API projects partner gender into `Individual.gender` as a CodeableConcept using ISO 5218 numeric codes. The internal-model entry is retained to document the text-enum shape; integrators consuming the API should use the `sex` mapping instead.
- `grievance-status` (GRMTicketStageType): the GRM module is not exposed through REST API v2.
- `event-severity` (GRMTicketSeverity and HazardIncidentSeverity): GRM and hazard modules are not exposed through REST API v2.

These are mapped against internal Odoo models so the semantic alignment is preserved for the next API iteration.

## Refreshing the data

The OpenSPP source tree is cloned on demand into `repo/` (gitignored). From the repo root:

```bash
git clone --depth 1 --branch 19.0 https://github.com/OpenSPP/OpenSPP2 external/openspp/repo
```

Extractor scripts that pull vocabulary XML and Pydantic schemas into `extracted/` are a planned follow-up. Today, `extracted/` holds manually captured snapshots.

## Cross-references with the schema

Every vocabulary with `value_mapping` in `matching.yaml` has a corresponding `system_mappings.openspp` block on its vocabulary YAML (enforced by `tests/test_openspp_mapping.py`). The value mappings must agree in both places; the vocabulary YAMLs drive the build.

No `external_equivalents.openspp` URIs are emitted on schema YAMLs for OpenSPP. OpenSPP alignment is purely value-level (code-to-code) rather than URI-level.
