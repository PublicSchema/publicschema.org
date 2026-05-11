# Bespoke YAML to LinkML cheatsheet

A field-by-field index of where each legacy PublicSchema YAML field lands in the LinkML output, keyed on the source field name. Use this when reading an old PR, translating a file manually, or auditing the migration. Companion to the broader [authoring guide](authoring-linkml.md). Citations refer to `build/migrate_to_linkml.py`.

The recognised source-field sets are listed at lines 142-202 (`KNOWN_CONCEPT_FIELDS`, `KNOWN_PROPERTY_FIELDS`, `KNOWN_VOCAB_FIELDS`, `PER_VALUE_KNOWN_FIELDS`, `SYSTEM_MAPPING_VALUE_KNOWN_FIELDS`). Anything outside these sets is reported under "Unmapped source fields" in `dist/linkml/_migration_report.md`.

## Common conventions

- English `label.en` → `title:`; non-English entries → `annotations.label_<lang>` (`i18n_annotations`, line 477).
- English `definition.en` → `description:`; non-English → `annotations.description_<lang>`.
- `maturity` (`draft` / `candidate` / `normative`) → `status:` as `bibo:draft` / `bibo:status/forthcoming` / `bibo:status/published` via `STATUS_MAP` (line 91).
- Structured (non-scalar) values are JSON-stringified into a `<name>_json` annotation via `json_annotation` (line 487).
- `external_equivalents.<vocab>` is split: bare CURIEs (resolved via `uri_to_curie`, line 545) land in `exact_mappings:` or `close_mappings:` keyed on the `match:` value; the full record (with `label`, `note`, `vocabulary`, `match`, plus any SEMIC alignment evidence) lands in `annotations.external_alignments_json` (line 498).
- Bibliography entries' `informs:` block is reverse-indexed into `annotations.bibliography_refs` on each target (concept, property, vocabulary, credential) — see line 373.

## Concept fields (`schema/concepts/*.yaml`)

| Bespoke field | LinkML output | Code |
|---|---|---|
| `id` | Local class name (`PascalCase` already); also `class_uri: publicschema:<id>` | line 931, 936 |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` | line 932, 985 |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` | line 933, 985 |
| `maturity` | `status:` via `STATUS_MAP` | line 965-967 |
| `featured: true` | `annotations.featured` (bool) | line 986 |
| `abstract: true` | `abstract: true` (also forced for `Agent`, `Party`, `Thing`) | line 1015 |
| `domain` | `annotations.source_domain`; also drives `concept_domain` assignment (line 1030) | line 988 |
| `properties` (list of slot names) | `slots:` | line 960 |
| `property_groups` | `annotations.property_groups_json` | line 996 |
| `supertypes` (list) | First entry → `is_a:`; rest → `mixins:`; any `<domain>/Name` path prefix stripped | line 943-952 |
| `subtypes` | Not emitted (implied by other concepts' `is_a` / `mixins`) | — |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` | line 971, 994 |
| `convergence` | `annotations.convergence_json` | line 995 |
| `see_also` | `annotations.see_also_json` | line 997 |
| `tags` | `annotations.tags_json` | line 998 |
| `vc_guidance` | `annotations.vc_guidance_json` | line 999 |

## Property fields (`schema/properties/*.yaml`)

| Bespoke field | LinkML output | Code |
|---|---|---|
| `id` | Local slot name (already `snake_case`); also `slot_uri: publicschema:<id>` | line 827, 832 |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` | line 828, 888 |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` | line 829, 888 |
| `maturity` | `status:` via `STATUS_MAP` | line 866-868 |
| `type` | `range:` via `PRIMITIVE_TYPE_MAP` (line 806); `concept:<X>` strips the `concept:` prefix; `geojson_geometry` collapses to `string` | line 840-856 |
| `references: <Concept>` | `range: <Concept>` (takes precedence over `type`) | line 843 |
| `vocabulary: <vocab-id>` | `range: <PascalCase vocab id>` (takes precedence over `type` when no `references`) | line 845-846 |
| `cardinality: single` / `multiple` | `multivalued: false` / `true` | line 858-863 |
| `schema_org_equivalent: <CURIE>` | Appended to `exact_mappings:` | line 872-874 |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` (merged with SEMIC alignments from `schema/alignments/<vocab>.yaml`) | line 871, 875-881 |
| `category` | `annotations.category` (scalar) | line 889 |
| `sensitivity` | `annotations.sensitivity` | line 889 |
| `domain_override` | `annotations.domain_override` | line 889 |
| `immutable_after_status` | `annotations.immutable_after_status` | line 889 |
| `vc_guidance` | `annotations.vc_guidance` (scalar) — concept-level uses `_json` | line 889 |
| `convergence` | `annotations.convergence_json` | line 897 |
| `system_mappings` | `annotations.system_mappings_json` + drives `external/<system>.yaml` enum emission | line 898; line 1604 |
| `valid_instruments` | `annotations.valid_instruments_json` | line 899 |
| `age_applicability` | `annotations.age_applicability_json` | line 900 |
| `see_also` | `annotations.see_also_json` | line 901 |
| `tags` | `annotations.tags_json` | line 902 |

## Vocabulary fields (`schema/vocabularies/*.yaml`)

| Bespoke field | LinkML output | Code |
|---|---|---|
| `id` | Local enum name (`PascalCase`); also `enum_uri: publicschema:<Name>` | line 576, 581 |
| `label.en` / `label.<lang>` | `title:` / `annotations.label_<lang>` | line 577, 687 |
| `definition.en` / `definition.<lang>` | `description:` / `annotations.description_<lang>` | line 578, 687 |
| `maturity` | `status:` via `STATUS_MAP` | line 589-591 |
| `standard` | `annotations.standard_json` | line 694 |
| `sync` | `annotations.sync_json` | line 695 |
| `same_standard_systems` | `annotations.same_standard_systems_json` | line 696 |
| `external_values: true` | `annotations.external_values` (bool) | line 705 |
| `external_equivalents` | `exact_mappings:` / `close_mappings:` + `annotations.external_alignments_json` | line 680, 693 |
| `system_mappings.<system>` | Drives `external/<system>.yaml` emission; per-value `maps_to` → `exact_mappings:` on the source PV; per-system `note` / `unmapped_reason` / `migration_note` → annotations keyed `<name>__<system>` on the PV | line 719, 731 |
| `references` | `annotations.vocab_references_json` | line 698 |
| `domain` | `annotations.source_domain` | line 688 |
| `vc_guidance` | `annotations.vc_guidance_json` | line 699 |
| `see_also`, `tags` | `annotations.see_also_json`, `annotations.tags_json` | line 700-701 |
| `values[].code` | Permissible-value key (slugified; `self` becomes `self_`; numeric codes kept verbatim) | line 436-449 |
| `values[].label` | PV `title:` (English) + `annotations.label_<lang>` | line 604-606, 614 |
| `values[].definition` | PV `description:` (English) + `annotations.description_<lang>` | line 608-610, 616 |
| `values[].standard_code` | PV `annotations.standard_code` | line 622 |
| `values[].note` / `notes` | PV `annotations.note` (+ `note_<lang>` for multilingual `notes`) | line 626-639 |
| `values[].parent_code` | PV `annotations.parent_code` | line 642 |
| `values[].level` | PV `annotations.level` (int preserved) | line 644 |
| `values[].domain` | PV `annotations.source_domain` | line 648 |
| `values[].group_type_applicability` | PV `annotations.group_type_applicability_json` | line 652 |
| `values[].unmapped_reason` / `migration_note` | PV `annotations.unmapped_reason` / `migration_note` | line 659-662 |

Bibliography (`schema/bibliography/*.yaml`), credentials (`schema/credentials/*.yaml`), and categories (`schema/categories.yaml`) are sibling files with their own emitters: see `emit_bibliography_file` (line 1443), `emit_credentials_file` (line 1401), and `emit_categories_file` (line 1511) for their field-by-field handling.
