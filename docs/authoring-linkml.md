# Authoring PublicSchema in LinkML

This guide is for contributors who add or modify schema content after PublicSchema cuts over to LinkML as source of truth. It assumes the [data model design guide](data-model-guide.md) and the [field-by-field translation](comparison-linkml.md) to LinkML. For translating an old PR, see the companion [migration cheatsheet](migration-cheatsheet.md).

## 1. Where things live

The LinkML tree under `dist/linkml/` is what consumers import. Until cutover it is regenerated from `schema/` by `build/migrate_to_linkml.py`; after cutover the same layout is the authored source.

| File | Holds |
|---|---|
| `publicschema.yaml` | Top-level composite. Prefixes, version, `imports:` for every domain and `external/<system>` partial. Generated; do not hand-edit (`build/migrate_to_linkml.py:1846`). |
| `publicschema-extensions.yaml` | Auxiliary metamodel (`ExternalAlignment`, `Convergence`, `MatchStrength`). Copied from `build/linkml_extensions.yaml` and imported by every domain file. |
| `core.yaml`, `identity.yaml`, `civil_status.yaml`, `program.yaml`, `payment.yaml`, `assessment.yaml`, `consent.yaml`, `document.yaml`, `biometric.yaml`, `common.yaml`, `misc.yaml`, `vocabularies.yaml` | The twelve domain files. Each holds its own `classes:`, `slots:`, `enums:`. Domain assignment is decided per element by the rules in `build/migrate_to_linkml.py:99-139`. |
| `credentials.yaml`, `bibliography.yaml`, `categories.yaml` | Sibling files for VC descriptors, citation records, and the UI category taxonomy. |
| `external/<system>.yaml` | Partial LinkML schemas for each implementing system (DHS, OpenSPP, DHIS2, OpenCRVS, SEMIC, FHIR, ...). They declare the enum permissible values that PublicSchema crosswalks reference. |
| `_inventory.md`, `_domain_split.md`, `_migration_report.md` | Generated reports — see §7. |

A new element goes into the file matching its domain. The rules in `assign_concept_domain`, `assign_property_domain`, `assign_vocab_domain` (`build/migrate_to_linkml.py:1030-1101`) prefer source-declared `domain:`, then a hand-curated map (`CONCEPT_DOMAINS`), then `misc`. Cross-domain references resolve into `imports:` automatically.

## 2. Adding a concept

A concept becomes a LinkML `ClassDefinition`. Suppose you are adding `School` as a `ServicePoint` subtype, into the domain file the assignment rules pick (typically `identity.yaml` for service points):

```yaml
School:
  class_uri: publicschema:School
  title: School
  description: A service point where formal or non-formal education is delivered ...
  is_a: ServicePoint
  slots: [school_level_served, school_type]
  status: bibo:draft
  close_mappings: [schema:School]
  annotations:
    label_fr: École
    label_es: Escuela
    description_fr: Un point de service ...
    source_domain: crvs
    external_alignments_json: '[{"label": "School", "match": "close", "note": "...", "uri": "https://schema.org/School", "vocabulary": "schema.org"}]'
    bibliography_refs: '["schema-org"]'
```

Rules that fall out of `convert_concept` (`build/migrate_to_linkml.py:929`):

- `class_uri` is always `publicschema:<Name>`; the local name is `PascalCase`.
- English `title` / `description` are first-class slots; other languages live under `annotations:` as `label_<lang>` / `description_<lang>` (`i18n_annotations`, line 477).
- First declared supertype → `is_a:`; the rest → `mixins:` (line 947-952). `Person` (Party + Agent) is the canonical multi-inheritance example.
- `status:` uses bibo CURIEs via the `STATUS_MAP` constant (line 91): `bibo:draft`, `bibo:status/forthcoming`, `bibo:status/published`.
- Bare-CURIE alignments go on `exact_mappings:` / `close_mappings:`; rich per-mapping records (with `label`, `note`, `vocabulary`, `match`) are JSON-stringified into `external_alignments_json`. The two should agree.
- `Agent`, `Party`, `Thing` are forced abstract; everything else honours an explicit `abstract: true` (line 1014-1016).

## 3. Adding a slot

A property becomes a LinkML `SlotDefinition`. For a new `school_type`:

```yaml
school_type:
  slot_uri: publicschema:school_type
  title: School type
  description: The management and funding classification of a school ...
  range: SchoolType
  multivalued: false
  status: bibo:draft
  annotations:
    label_fr: "Type d'école"
    category: classification
```

Range resolution is layered (`build/migrate_to_linkml.py:840-856`):

1. Legacy `references: <Concept>` → `range: <Concept>`.
2. Legacy `vocabulary: <id>` → `range: <PascalCase id>` (`school-type` ⇒ `SchoolType`).
3. Otherwise the primitive `type:` is mapped through `PRIMITIVE_TYPE_MAP` (line 806). Unknown primitives collapse to `string` and surface as unmapped.

Cardinality compiles to `multivalued: true | false`. Use a list slot only when the property genuinely accepts many values — see [`schema-design.md`](schema-design.md) for the decision tree.

## 4. Adding a vocabulary

A vocabulary becomes a LinkML `EnumDefinition` whose permissible values carry an explicit `meaning:`. For a `school-level` enum:

```yaml
SchoolLevel:
  enum_uri: publicschema:SchoolLevel
  title: School Level
  description: The ISCED 2011 level of education served by a school ...
  status: bibo:draft
  permissible_values:
    isced_0:
      meaning: publicschema:SchoolLevel/isced_0
      title: Early childhood education (ISCED 0)
      annotations:
        label_fr: Éducation de la petite enfance (ISCED 0)
        standard_code: "0"
        level: 0
    isced_1:
      meaning: publicschema:SchoolLevel/isced_1
      title: Primary education (ISCED 1)
      annotations: {standard_code: "1", level: 1, parent_code: "isced_0"}
  annotations:
    standard_json: '{"name": "UNESCO ISCED 2011", "uri": "https://uis.unesco.org/..."}'
```

Permissible-value keys are slugified from the source code (line 436-449). Numeric codes (DHS 1..5, ISO 5218 0..9) are kept verbatim; anything that slugifies to `self` is suffixed with an underscore (`self_`) to avoid colliding with `jsonasobj2.ExtendedNamespace.__init__`. Per-value annotation keys are fixed: `standard_code`, `note`, `parent_code`, `level`, `source_domain`, `unmapped_reason`, `migration_note`, plus `group_type_applicability_json` for list constraints (line 622-662).

If the vocabulary carries system crosswalks, each value gets an `exact_mappings:` list pointing at the meaning URI in the corresponding `external/<system>.yaml`. The script wires these from the legacy `system_mappings:` blocks (line 731). Hand-authored after cutover, declare the external enum and value once under `external/<system>.yaml`, then reference its CURIE from `exact_mappings:`.

## 5. Annotation conventions

Stock LinkML annotations are scalar key/value pairs. PublicSchema overloads them with two conventions:

| Pattern | Used for | Source |
|---|---|---|
| `label_<lang>`, `description_<lang>` | Multilingual labels and definitions. English stays in `title:` / `description:`. | line 477-484 |
| `<name>_json` | Anything structured: alignment records, the `convergence` block, `property_groups`, `system_mappings`, `valid_instruments`, `age_applicability`, `tags`, `see_also`, the vocabulary-level `standard` / `sync` / `same_standard_systems`. JSON-encoded strings with sorted keys. | `json_annotation`, line 487-495 |

JSON-string encoding is deliberate: it survives `linkml-lint`'s scalar-annotation check and produces clean RDF literals downstream. Consumers call `json.loads(value)` on any `*_json` annotation to recover the structured form.

Bibliography is the one annotation computed by reverse-indexing: a bibliography entry whose `informs:` block lists a concept/property/vocabulary id contributes its own id to the target's `bibliography_refs` annotation (line 373-392). Author `informs:` on the citation, never `bibliography_refs:` on the target.

## 6. Cross-references

- **External alignments to a single vocabulary** (schema.org, FHIR, ...) — on the class/slot/enum via `exact_mappings:` / `close_mappings:` plus the matching `external_alignments_json` annotation for prose.
- **SEMIC-style alignments** — declare the vocabulary in `external_references/<vocab>.yaml` (provenance, license, retrieved-at, source SHA-256), the upstream terms in `external_terms/<vocab>.yaml` (`curie`, `iri`, `term_type`), and the per-subject mappings in `alignments/<vocab>.yaml`. The script merges these into the same `external_alignments` block on the subject (line 1290-1329); the `external/<system>.yaml` partial inherits provenance and license from the reference file (line 1714-1741).
- **Bibliography** — author the citation in `bibliography/<id>.yaml` with an `informs:` block listing every concept/property/vocabulary that cites it.

## 7. Validation

Local checks, in order:

1. `uv run python -m build.migrate_to_linkml` — regenerates `dist/linkml/` and the three reports. Non-zero exit on referential-integrity or lint failure. Read `dist/linkml/_migration_report.md` first: it lists every unmapped source field (target is zero), every is_a / mixins decision, every prefix, and any lint or integrity failure.
2. `linkml-lint --validate dist/linkml/<file>.yaml` — the same check the script runs internally (line 1879). Fast feedback on the file you touched.
3. `gen-owl`, `gen-shacl`, `gen-jsonld-context`, `gen-json-schema dist/linkml/publicschema.yaml` — the four stock generators. `build/test_migrate.py:64` asserts each succeeds on the composite.
4. `pytest build/test_migrate.py` — end-to-end. Asserts exit-code 0, the four generators, bibo status CURIEs, multi-inheritance round-tripping, and crosswalk referential integrity (every `exact_mappings:` CURIE in PublicSchema enums points at a `meaning:` URI declared in `external/<system>.yaml`).

`dist/linkml/_inventory.md` and `dist/linkml/_domain_split.md` give a per-element breakdown of what landed where and why — useful when a new concept ends up in an unexpected domain.
