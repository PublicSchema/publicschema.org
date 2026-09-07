# Authoring PublicSchema in LinkML

This guide is for contributors who add or modify schema content now that PublicSchema uses LinkML as the source of truth. It assumes the [data model design guide](data-model-guide.md) and the [field-by-field translation](comparison-linkml.md) to LinkML. For translating an old PR, see the companion [migration cheatsheet](migration-cheatsheet.md).

## 1. Where things live

The LinkML tree under `schema/` is the authored source. Generated JSON, JSON-LD, RDF, SHACL, JSON Schema, downloads, and site data are emitted under `dist/`. `just build` also copies the public downloads, schemas, and data files that require static assets into `site/public/`; Astro endpoints serve other exports directly from `dist/`.

| File | Holds |
|---|---|
| `publicschema.yaml` | Top-level composite. Prefixes, version, `imports:` for every domain and `external/<system>` partial. |
| `publicschema-extensions.yaml` | Auxiliary metamodel (`ExternalAlignment`, `Convergence`, `MatchStrength`) imported by the schema modules. |
| `core.yaml`, `identity.yaml`, `civil_status.yaml`, `program.yaml`, `payment.yaml`, `assessment.yaml`, `consent.yaml`, `document.yaml`, `biometric.yaml`, `common.yaml`, `metrics.yaml`, `misc.yaml`, `vocabularies.yaml` | The domain files. Each holds its own `classes:`, `slots:`, `enums:`. |
| `credentials.yaml`, `bibliography.yaml`, `categories.yaml` | Sibling files for VC descriptors, citation records, and the UI category taxonomy. |
| `external/<system>.yaml` | Partial LinkML schemas for each implementing system (DHS, OpenSPP, DHIS2, OpenCRVS, SEMIC, FHIR, ...). They declare the enum permissible values that PublicSchema crosswalks reference. |
| `value_crosswalks/*.yaml` | Authored value mappings with external-system codes, gaps, and standard provenance. These are separate from LinkML modules. |
| `metric_catalog/*.yaml` | Metric catalog sources projected into `dist/metrics_catalog.json` for the site. |

A new element goes into the file matching its domain. Cross-domain references must be represented with LinkML `imports:` on the files that use them.

The renderer reads definitions in the composite itself and follows its local imports, including nested modules. Unimported sibling files do not become catalog entries. External partial schemas and LinkML metamodel imports support validation and RDF generation without becoming PublicSchema catalog entries. Product modules must use local file imports; remote product imports are not supported by the renderer.

## 2. Adding a concept

A concept becomes a LinkML `ClassDefinition`. `School` is an existing `ServicePoint` subtype in `identity.yaml`. This shortened example illustrates the fields to use for a similar concept:

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
    external_alignments_json: '[{"label": "School", "match": "close", "note": "...", "uri": "https://schema.org/School", "vocabulary": "schema.org"}]'
    bibliography_refs: '["schema-org"]'
```

Rules:

- Use a stable `class_uri`, following the surrounding module. Universal concepts use `publicschema:<Name>`. Domain-qualified concepts can use `publicschema:<domain>/<Name>`, with a distinct LinkML name such as `CrvsPerson` for `publicschema:crvs/Person`. Preserve existing URIs and `annotations.source_domain`; module filenames alone do not set public domains.
- English `title` / `description` are first-class slots; other languages live under `annotations:` as `label_<lang>` / `description_<lang>`.
- Use `is_a:` for the primary supertype and `mixins:` for additional supertypes. `Person` (Party + Agent) is the canonical multi-inheritance example.
- `status:` maps draft, candidate, and normative maturity to `bibo:draft`, `bibo:status/forthcoming`, and `bibo:status/published`, respectively. Candidate and normative terms require French and Spanish translations.
- Bare-CURIE alignments go on `exact_mappings:` / `close_mappings:`; rich per-mapping records (with `label`, `note`, `vocabulary`, `match`) are JSON-stringified into `external_alignments_json`. The two should agree.
- `Agent`, `Party`, and `Thing` are abstract; everything else should declare `abstract: true` only when it is intentionally not instantiated.

## 3. Adding a slot

A property becomes a LinkML `SlotDefinition`. This shortened `school_type` example shows the pattern:

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

Range resolution is direct:

1. Concept references use `range: <Concept>`.
2. Controlled vocabularies use `range: <EnumName>` (`school-type` becomes `SchoolType`).
3. Primitives use LinkML ranges such as `string`, `integer`, `decimal`, `date`, `datetime`, `boolean`, and `uri`.

Reference each reusable slot in the `slots:` lists of the classes that use it. Put the UI category in `annotations.category`, using a key from the `Category` enum in `schema/categories.yaml`. Use scalar `annotations.sensitivity` for sensitivity and JSON-encoded `annotations.age_applicability_json` for age bands.

Keep `slot_uri` aligned with the property's established public URI, including its domain segment when applicable. The JSON field name remains the slot name; the generated context uses the authored URI. Vocabulary-backed fields carry literal codes such as `male` or `self`, not the vocabulary value's `meaning` URI. The published SHACL shapes validate this same representation.

Cardinality compiles to `multivalued: true | false`. Use a list slot only when the property accepts many values; see [`schema-design.md`](schema-design.md) for the decision tree.

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
      annotations: {standard_code: "1", level: 1}
  annotations:
    standard_json: '{"name": "UNESCO ISCED 2011", "uri": "https://uis.unesco.org/..."}'
```

Permissible-value keys should be stable slug identifiers. Keep upstream display or numeric codes in `annotations.standard_code` when the canonical upstream code differs from the LinkML-safe key. Per-value annotation keys include `standard_code`, `note`, `parent_code`, `level`, `source_domain`, `unmapped_reason`, `migration_note`, and `group_type_applicability_json` for list constraints.

Author system value crosswalks in `schema/value_crosswalks/*.yaml`; these files supply the mappings displayed by the site. Use `source_value_set`, `target_value_set`, `pairs`, and complete `standard` provenance, following an existing file and `build/schemas/value_crosswalk.schema.json`. Mapping pairs use PublicSchema `source_value` and external `target_value`; express gaps with `quality: unmapped` and a null value on the missing side. See [Contributing: system mappings](../CONTRIBUTING.md#system-mappings) for the contribution sequence.

Maintain the corresponding external enum and values in `external/<system>.yaml`. Per-value `exact_mappings` can express URI alignments, but do not replace authored crosswalks. The standards sync command currently refuses the LinkML tree; review and edit upstream enum changes manually as described in [Refreshing external standards](../CONTRIBUTING.md#refreshing-external-standards).

## 5. Annotation conventions

Stock LinkML annotations are scalar key/value pairs. PublicSchema overloads them with two conventions:

| Pattern | Used for | Source |
|---|---|---|
| `label_<lang>`, `description_<lang>` | Multilingual labels and definitions. English stays in `title:` / `description:`. | Author directly on the LinkML element. |
| `<name>_json` | Anything structured: alignment records, the `convergence` block, `property_groups`, `valid_instruments`, `age_applicability`, `tags`, `see_also`, the vocabulary-level `standard` / `sync` / `same_standard_systems`. | JSON-encoded annotation value. |

JSON-string encoding is deliberate: it survives `linkml-lint`'s scalar-annotation check and produces clean RDF literals downstream. Consumers call `json.loads(value)` on any `*_json` annotation to recover the structured form.

`system_mappings_json` may appear in migrated data, but current system value mappings belong in `schema/value_crosswalks/`. Do not author new mappings in that compatibility annotation.

Bibliography is represented as citation classes in `bibliography.yaml`. The build reader exposes `bibliography_refs` on the target terms for site rendering.

## 6. Cross-references

- **External alignments to a single vocabulary** (schema.org, FHIR, ...): on the class/slot/enum via `exact_mappings:` / `close_mappings:` plus the matching `external_alignments_json` annotation for prose.
- **SEMIC-style alignments**: use `external/<system>.yaml` partial schemas for upstream terms and `exact_mappings:` / `close_mappings:` plus `external_alignments_json` on PublicSchema classes, slots, and enums. Keep provenance in bibliography and external partial metadata.
- **Bibliography**: author citation classes in `bibliography.yaml`; keep target references in `annotations.bibliography_refs`.

## 7. Validation

Run from the repository root after `just setup`:

1. `just validate` validates the composite LinkML metamodel; it does not replace content checks.
2. `just validate-crosswalks` checks authored crosswalk structure and standard metadata.
3. `just lint` checks content and maturity rules; `just check-translations` checks schema, documentation, and UI translations.
4. `just test` runs the Python tests.
5. `just build` regenerates `dist/`, including the metric catalog, and prepares site public artifacts.
6. `just site-build` verifies production site compilation after validation and regeneration.

`just check` combines steps 1 through 5. Inspect `git diff` and `git status --short` afterward; the command does not assert a clean working tree. Review the source and generated changes together. The historical migration script is not part of this workflow: the LinkML modules are authored source, not disposable migration output.
