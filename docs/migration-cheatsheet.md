# Bespoke YAML to LinkML cheatsheet

This is a historical field translation reference for reading pre-LinkML pull requests. Current contributions edit the LinkML modules under `schema/` directly, using the [authoring guide](authoring-linkml.md). The legacy `schema/concepts/`, `schema/properties/`, and `schema/vocabularies/` directories below no longer exist in the maintained source tree.

`build/migrate_to_linkml.py` records the original conversion. It is not a normal build or authoring step, and the normal build does not produce a migration report. The tables describe migration behavior, not a requirement to regenerate authored LinkML.

**Current mapping exception:** system value mappings now live in authored `schema/value_crosswalks/*.yaml`, with complete standard provenance. The legacy `system_mappings_json` and per-value alignment projections below are migration details, not the supported crosswalk authoring format. See [Contributing: system mappings](../CONTRIBUTING.md#system-mappings).

## Common conventions

- English `label.en` → `title:`; non-English entries → `annotations.label_<lang>` (`i18n_annotations`).
- English `definition.en` → `description:`; non-English → `annotations.description_<lang>`.
- `maturity` (`draft` / `candidate` / `normative`) → `status:` as `bibo:draft` / `bibo:status/forthcoming` / `bibo:status/published` via `STATUS_MAP`.
- Structured (non-scalar) values are JSON-stringified into a `<name>_json` annotation via `json_annotation`.
- `external_equivalents.<vocab>` is split: bare CURIEs (resolved via `uri_to_curie`) land in `exact_mappings:` or `close_mappings:` keyed on the `match:` value; the full record (with `label`, `note`, `vocabulary`, `match`, plus any SEMIC alignment evidence) lands in `annotations.external_alignments_json`.
- Bibliography entries' `informs:` block is reverse-indexed into `annotations.bibliography_refs` on each target (concept, property, vocabulary, credential).

## Legacy concept fields (`schema/concepts/*.yaml`)

| Bespoke field | LinkML output |
|---|---|
| `id` | Local class name (`PascalCase` already); also `class_uri: publicschema:<id>` |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` |
| `maturity` | `status:` via `STATUS_MAP` |
| `featured: true` | `annotations.featured` (bool) |
| `abstract: true` | `abstract: true` (also forced for `Agent`, `Party`, `Thing`) |
| `domain` | `annotations.source_domain`; also drives `concept_domain` assignment |
| `properties` (list of slot names) | `slots:` |
| `property_groups` | `annotations.property_groups_json` |
| `supertypes` (list) | First entry → `is_a:`; rest → `mixins:`; any `<domain>/Name` path prefix stripped |
| `subtypes` | Not emitted (implied by other concepts' `is_a` / `mixins`) |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` |
| `convergence` | `annotations.convergence_json` |
| `see_also` | `annotations.see_also_json` |
| `tags` | `annotations.tags_json` |
| `vc_guidance` | `annotations.vc_guidance_json` |

## Legacy property fields (`schema/properties/*.yaml`)

| Bespoke field | LinkML output |
|---|---|
| `id` | Local slot name (already `snake_case`); also `slot_uri: publicschema:<id>` |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` |
| `maturity` | `status:` via `STATUS_MAP` |
| `type` | `range:` via `PRIMITIVE_TYPE_MAP`; `concept:<X>` strips the `concept:` prefix; `geojson_geometry` collapses to `string` |
| `references: <Concept>` | `range: <Concept>` (takes precedence over `type`) |
| `vocabulary: <vocab-id>` | `range: <PascalCase vocab id>` (takes precedence over `type` when no `references`) |
| `cardinality: single` / `multiple` | `multivalued: false` / `true` |
| `schema_org_equivalent: <CURIE>` | Appended to `exact_mappings:` |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` (merged with SEMIC alignments from `schema/alignments/<vocab>.yaml`) |
| `category` | `annotations.category` (scalar) |
| `sensitivity` | `annotations.sensitivity` |
| `domain_override` | `annotations.domain_override` |
| `immutable_after_status` | `annotations.immutable_after_status` |
| `vc_guidance` | `annotations.vc_guidance` (scalar); concept-level uses `_json` |
| `convergence` | `annotations.convergence_json` |
| `system_mappings` | `annotations.system_mappings_json` + drives `external/<system>.yaml` enum emission |
| `valid_instruments` | `annotations.valid_instruments_json` |
| `age_applicability` | `annotations.age_applicability_json` |
| `see_also` | `annotations.see_also_json` |
| `tags` | `annotations.tags_json` |

## Legacy vocabulary fields (`schema/vocabularies/*.yaml`)

| Bespoke field | LinkML output |
|---|---|
| `id` | Local enum name (`PascalCase`); also `enum_uri: publicschema:<Name>` |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` |
| `maturity` | `status:` via `STATUS_MAP` |
| `standard` | `annotations.standard_json` |
| `sync` | `annotations.sync_json` |
| `same_standard_systems` | `annotations.same_standard_systems_json` |
| `external_values: true` | `annotations.external_values` (bool) |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` |
| `system_mappings.<system>` | Drives `external/<system>.yaml` emission; per-value `maps_to` → `exact_mappings:` on the source PV; per-system `note` / `unmapped_reason` / `migration_note` → annotations keyed `<name>__<system>` on the PV |
| `references` | `annotations.vocab_references_json` |
| `domain` | `annotations.source_domain` |
| `vc_guidance` | `annotations.vc_guidance_json` |
| `see_also`, `tags` | `annotations.see_also_json`, `annotations.tags_json` |
| `values[].code` | Permissible-value key (slugified; `self` becomes `self_`; numeric codes kept verbatim) |
| `values[].label` | PV `title:` (English) + `annotations.label_<lang>` |
| `values[].definition` | PV `description:` (English) + `annotations.description_<lang>` |
| `values[].standard_code` | PV `annotations.standard_code` |
| `values[].note` / `notes` | PV `annotations.note` (+ `note_<lang>` for multilingual `notes`) |
| `values[].parent_code` | PV `annotations.parent_code` |
| `values[].level` | PV `annotations.level` (int preserved) |
| `values[].domain` | PV `annotations.source_domain` |
| `values[].group_type_applicability` | PV `annotations.group_type_applicability_json` |
| `values[].unmapped_reason` / `migration_note` | PV `annotations.unmapped_reason` / `migration_note` |

Legacy bibliography and credential directories became the authored `schema/bibliography.yaml` and `schema/credentials.yaml` modules; categories live in `schema/categories.yaml`. For historical conversion details, see `emit_bibliography_file`, `emit_credentials_file`, and `emit_categories_file` for their field-by-field handling.
