# Comparison: PublicSchema and LinkML

PublicSchema and [LinkML](https://linkml.io/) both let schema authors attach RDF / linked-data semantics to data definitions, but they are independent projects with different vocabularies. This document audits the overlap field-by-field so that downstream LinkML consumers can map PublicSchema constructs to their LinkML equivalents and identify the places where the two diverge.

This is descriptive, not prescriptive. PublicSchema does not adopt LinkML's syntax and does not propose to.

## Heritage

PublicSchema is not derived from LinkML. The project's documented prior art is FHIR (resources, extensions, value sets, maturity ladder) and schema.org (publication model) — see [`docs/related-standards.md`](related-standards.md) and `decisions/002-maturity-model.md`. LinkML is referenced exactly once in the codebase, in `decisions/008-agent-organization.md:50`, only as a comparable technology that handles multiple inheritance the same way JSON-LD and OWL do.

PublicSchema independently solves an overlapping problem (semantic alignment with external vocabularies) using a different surface vocabulary: `external_equivalents`, `schema_org_equivalent`, `system_mappings`, `supertypes` / `subtypes`, `standard`, `convergence`, plus a `base_uri` + `id` URI scheme.

## 1. Project-level constructs

| LinkML | PublicSchema | Notes |
|---|---|---|
| `id`, `name`, `version` | `schema_project.id`, `schema_project.name`, `schema_project.version` (`schema/project.yaml:3-8`) | Direct correspondence. |
| `prefixes:` + `default_prefix:` | None | PublicSchema embeds full URIs in mapping fields. CURIE-shaped strings such as `schema:name` (`schema/properties/name.yaml:18`) are not formally declared. |
| `imports:` | None | One concept / property / vocabulary per file. Cross-references resolve by `id` string, not by namespaced import. |
| `default_range:` | `type:` per property (`schema/properties/name.yaml:13`) | LinkML defaults a range schema-wide; PublicSchema declares it per property. |
| — | `kind: core` (`schema/project.yaml:4`), `namespace`, `base_uri`, `languages.{primary,additional}`, `license`, `format_version`, `maturity` (`schema/_meta.yaml:4`) | PublicSchema-only. `kind` distinguishes the core vocabulary from extension modules; `maturity` is the FHIR-style ladder. |

## 2. Class- / concept-level constructs

Citations are from `schema/concepts/organization.yaml`.

| LinkML | PublicSchema | Notes |
|---|---|---|
| `class_uri:` | Implicit: `base_uri` + `id` (e.g. `https://publicschema.org/Organization`) | No explicit URI field on concepts. The canonical URI is built from `schema/_meta.yaml:2` (`base_uri`) and the file-level `id`. |
| `is_a:` / `mixins:` | `supertypes:` / `subtypes:` (lines 58-59) | PublicSchema allows multiple supertypes (see `decisions/008-agent-organization.md`). Both `is_a` and `mixins` collapse into the single `supertypes` list. |
| `exact_mappings:` / `close_mappings:` | `external_equivalents.<vocab>` with `match: exact \| close` (lines 61-91) | Same information, different shape: LinkML keys the bucket on strength; PublicSchema keys on vocabulary and stores strength as a field. PublicSchema additionally carries `label`, `vocabulary`, and `note` per mapping; LinkML has no per-mapping comment slot without using structured annotations. |
| `related_mappings:`, `broad_mappings:`, `narrow_mappings:` | None observed | PublicSchema's `match:` field is used only as `exact` or `close` in the audited files. See §5. |
| `title:`, `description:` | `label.{en,fr,es}` and `definition.{en,fr,es}` (lines 2-42) | PublicSchema treats labels and definitions as multilingual maps at every level. LinkML's `title:` and `description:` are single strings; multilingual content lives in annotations. |
| — | `convergence:` (lines 93-106) | Adoption signal: `system_count`, `total_systems`, prose `notes`. No LinkML equivalent. |
| — | `property_groups:` (lines 49-56) | UI / categorisation grouping. No LinkML equivalent. |

## 3. Slot- / property-level constructs

Citations are from `schema/properties/name.yaml`.

| LinkML | PublicSchema | Notes |
|---|---|---|
| `slot_uri:` | `schema_org_equivalent:` (line 18) | Narrower than `slot_uri`: only carries a schema.org CURIE. There is no general "this property is this RDF predicate" field; the canonical URI is implicit (`base_uri` + `id`). |
| `exact_mappings:` / `close_mappings:` (on slots) | `external_equivalents.<vocab>` (lines 20-32) | Same shape as the concept case. |
| `range:` | `type:` (line 13) | Primitive ranges (`string`, etc.) correspond directly; class-valued ranges in PublicSchema are expressed via `references:` (line 16) when used. |
| `multivalued:` (boolean) | `cardinality: single \| multiple` (line 14) | Equivalent information, different encoding. |
| `required:` | Not on the property file | Required-ness in PublicSchema is per concept, via the concept's `properties:` list and downstream credential schemas; properties do not declare global requiredness. |
| — | `category:` (line 17) | UI / grouping field. No LinkML equivalent. |
| — | `system_mappings:` | Per-system, per-value crosswalks. See §4. |

## 4. Enum / vocabulary / permissible-value constructs

Citations are from `schema/vocabularies/country.yaml` and `schema/properties/assessment_band.yaml`.

| LinkML | PublicSchema | Notes |
|---|---|---|
| `enum_uri:` | Implicit: `base_uri` + vocabulary `id` | No explicit URI field on vocabularies. |
| `permissible_values.<code>` | `values:` list with `code` and multilingual `label` (`country.yaml:31` onward) | One-line-per-value with `standard_code` (line 37) pointing into the vocabulary-level `standard:` block. |
| `permissible_values.<code>.meaning:` | Two partial substitutes (see below) | LinkML's `meaning:` carries a single canonical URI per value. PublicSchema splits this responsibility. |
| ... canonical external code per value | `values[].standard_code` (`country.yaml:37`) plus the vocabulary-level `standard.uri` (`country.yaml:11-13`) | URI is implicit, assembled from the standard's URI and the standard code. |
| ... per-system crosswalks per value | `system_mappings.<system>.values[].maps_to` (`assessment_band.yaml:18-37`) | No LinkML equivalent. LinkML's `meaning:` is a single URI; PublicSchema's `system_mappings` carries many-to-many crosswalks to specific delivery systems (DHS, OpenSPP, DHIS2, …), with `vocabulary_name`, per-value `maps_to`, and prose `note`. |
| — | `standard.{name,uri}` (`country.yaml:11-13`) | Vocabulary-level pointer to the authoritative standard. No LinkML equivalent. |
| — | `sync:` block (`country.yaml:14-18`) | Provenance for machine-readable mirror feeds (`source_url`, `format`, `last_synced`, `note`). No LinkML equivalent. |
| — | `same_standard_systems:` (`country.yaml:19-20`) | Lists implementing systems that already use the same standard verbatim. No LinkML equivalent. |
| — | `external_values: true` (`country.yaml:21`) | Marks the vocabulary as governed externally (codes change upstream). No LinkML equivalent. |

## 5. Mapping strength axes (SKOS)

LinkML exposes five SKOS-aligned predicates: `exact_mappings`, `close_mappings`, `related_mappings`, `broad_mappings`, `narrow_mappings`. PublicSchema's `match:` field is observed to take only `exact` and `close` values in the audited files; `related` / `broader` / `narrower` distinctions are not represented.

This is a documentation observation, not a recommendation. If finer-grained alignment is needed later — for instance to record that PublicSchema's `Organization` is *broader* than SEMIC's `PublicOrganisation` rather than merely *close* — the `match:` enumeration is the natural extension point. Today, the `note:` field on each `external_equivalents` entry carries that nuance in prose.

## 6. Build and export

LinkML ships generators (`gen-jsonld-context`, `gen-shacl`, `gen-owl`, `gen-json-schema`, etc.) that consume a LinkML schema and emit downstream artifacts. PublicSchema has its own build layer: `build/rdf_export.py` emits JSON-LD and Turtle from the YAML schemas, and `build/compare_semic.py` compares against external SHACL shapes. The generator ecosystems are not interchangeable, but the artifact shapes (JSON-LD, Turtle) are the same target.

A LinkML consumer that wants to import PublicSchema today would consume the JSON-LD / Turtle output of `build/rdf_export.py`, not the source YAML.

## 7. Summary table

| LinkML construct | PublicSchema equivalent |
|---|---|
| `imports:` | None — single-file-per-element model |
| `prefixes:`, `default_prefix:` | None — full URIs embedded |
| `class_uri:` | Implicit (`base_uri` + concept `id`) |
| `slot_uri:` | `schema_org_equivalent:` (schema.org-only) or implicit (`base_uri` + property `id`) |
| `enum_uri:` | Implicit (`base_uri` + vocabulary `id`) |
| `is_a:` / `mixins:` | `supertypes:` (multi-valued) / `subtypes:` |
| `exact_mappings:` | `external_equivalents.<vocab>` with `match: exact` |
| `close_mappings:` | `external_equivalents.<vocab>` with `match: close` |
| `broad_mappings:` / `narrow_mappings:` / `related_mappings:` | None observed; carried as prose in `note:` |
| `permissible_values.<code>.meaning:` | `values[].standard_code` + `standard.uri`, plus per-system `system_mappings.<system>.values[].maps_to` |
| `range:` | `type:` (plus `references:` for class-valued ranges) |
| `multivalued:` | `cardinality: single \| multiple` |
| `title:` / `description:` | `label.{en,fr,es}` / `definition.{en,fr,es}` (multilingual) |

## Caveats

- File-and-line citations are pinned to the versions read at the time of writing. After large refactors of `schema/_meta.yaml`, `schema/project.yaml`, or the canonical example files (`organization.yaml`, `name.yaml`, `assessment_band.yaml`, `country.yaml`), re-verify before quoting.
- This document does not propose adopting LinkML fields in PublicSchema source files. It is a translation reference for readers familiar with LinkML.
