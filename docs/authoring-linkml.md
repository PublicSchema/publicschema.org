# Authoring PublicSchema in LinkML

This guide is for contributors who add or modify schema content now that PublicSchema uses LinkML as the source of truth. It assumes the [data model design guide](data-model-guide.md) and the [field-by-field translation](comparison-linkml.md) to LinkML. For translating an old PR, see the companion [migration cheatsheet](migration-cheatsheet.md).

## 1. Where things live

The LinkML tree under `schema/` is the authored source. Generated JSON, JSON-LD, RDF, SHACL, JSON Schema, downloads, and site data are emitted under `dist/` and copied into `site/public/` by `just build`.

| File | Holds |
|---|---|
| `publicschema.yaml` | Top-level composite. Prefixes, version, `imports:` for every domain and `external/<system>` partial. |
| `publicschema-extensions.yaml` | Auxiliary metamodel (`ExternalAlignment`, `Convergence`, `MatchStrength`). Copied from `build/linkml_extensions.yaml` and imported by every domain file. |
| `core.yaml`, `identity.yaml`, `civil_status.yaml`, `program.yaml`, `payment.yaml`, `assessment.yaml`, `consent.yaml`, `document.yaml`, `biometric.yaml`, `common.yaml`, `misc.yaml`, `vocabularies.yaml` | The domain files. Each holds its own `classes:`, `slots:`, `enums:`. |
| `credentials.yaml`, `bibliography.yaml`, `categories.yaml` | Sibling files for VC descriptors, citation records, and the UI category taxonomy. |
| `external/<system>.yaml` | Partial LinkML schemas for each implementing system (DHS, OpenSPP, DHIS2, OpenCRVS, SEMIC, FHIR, ...). They declare the enum permissible values that PublicSchema crosswalks reference. |
A new element goes into the file matching its domain. Cross-domain references must be represented with LinkML `imports:` on the files that use them.

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

Rules:

- `class_uri` is always `publicschema:<Name>`; the local name is `PascalCase`.
- English `title` / `description` are first-class slots; other languages live under `annotations:` as `label_<lang>` / `description_<lang>`.
- Use `is_a:` for the primary supertype and `mixins:` for additional supertypes. `Person` (Party + Agent) is the canonical multi-inheritance example.
- `status:` uses bibo CURIEs: `bibo:draft`, `bibo:status/forthcoming`, `bibo:status/published`.
- Bare-CURIE alignments go on `exact_mappings:` / `close_mappings:`; rich per-mapping records (with `label`, `note`, `vocabulary`, `match`) are JSON-stringified into `external_alignments_json`. The two should agree.
- `Agent`, `Party`, and `Thing` are abstract; everything else should declare `abstract: true` only when it is intentionally not instantiated.

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

Range resolution is direct:

1. Concept references use `range: <Concept>`.
2. Controlled vocabularies use `range: <EnumName>` (`school-type` becomes `SchoolType`).
3. Primitives use LinkML ranges such as `string`, `integer`, `decimal`, `date`, `datetime`, `boolean`, and `uri`.

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

Permissible-value keys should be stable slug identifiers. Keep upstream display or numeric codes in `annotations.standard_code` when the canonical upstream code differs from the LinkML-safe key. Per-value annotation keys include `standard_code`, `note`, `parent_code`, `level`, `source_domain`, `unmapped_reason`, `migration_note`, and `group_type_applicability_json` for list constraints.

If the vocabulary carries system crosswalks, each value gets an `exact_mappings:` list pointing at the meaning URI in the corresponding `external/<system>.yaml`. Declare the external enum and value once under `external/<system>.yaml`, then reference its CURIE from `exact_mappings:`.

## 5. Annotation conventions

Stock LinkML annotations are scalar key/value pairs. PublicSchema overloads them with two conventions:

| Pattern | Used for | Source |
|---|---|---|
| `label_<lang>`, `description_<lang>` | Multilingual labels and definitions. English stays in `title:` / `description:`. | Author directly on the LinkML element. |
| `<name>_json` | Anything structured: alignment records, the `convergence` block, `property_groups`, `system_mappings`, `valid_instruments`, `age_applicability`, `tags`, `see_also`, the vocabulary-level `standard` / `sync` / `same_standard_systems`. | JSON-encoded annotation value. |

JSON-string encoding is deliberate: it survives `linkml-lint`'s scalar-annotation check and produces clean RDF literals downstream. Consumers call `json.loads(value)` on any `*_json` annotation to recover the structured form.

Bibliography is represented as citation classes in `bibliography.yaml`. The build reader exposes `bibliography_refs` on the target terms for site rendering.

## 6. Cross-references

- **External alignments to a single vocabulary** (schema.org, FHIR, ...) — on the class/slot/enum via `exact_mappings:` / `close_mappings:` plus the matching `external_alignments_json` annotation for prose.
- **SEMIC-style alignments** — use `external/<system>.yaml` partial schemas for upstream terms and `exact_mappings:` / `close_mappings:` plus `external_alignments_json` on PublicSchema classes, slots, and enums. Keep provenance in bibliography and external partial metadata.
- **Bibliography** — author citation classes in `bibliography.yaml`; keep target references in `annotations.bibliography_refs`.

## 7. Validation

Local checks, in order:

1. `uv run python -m build.validate` — validates `schema/publicschema.yaml` with LinkML validation.
2. `uv run python -m build.lint` — runs PublicSchema content lint against the LinkML read model.
3. `uv run python -m build.check_translations` — checks schema, docs, and UI translation coverage.
4. `uv run pytest` — runs semantic, mapping, RDF, JSON-LD, and build tests against the LinkML source.
5. `just build` — regenerates `dist/` and site public data.
