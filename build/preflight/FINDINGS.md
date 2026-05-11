# Phase 0.5 Preflight Findings

Hand-authored a small LinkML slice (Organization, Person with multi-inheritance, AssessmentBand with DHS crosswalks) and ran the full toolchain to validate the migration approach before writing the 500+-line script.

## Files

- `publicschema-extensions.yaml` — auxiliary classes used by structured annotation values
- `core.yaml` — Agent, Party (abstract supertypes)
- `identity.yaml` — Organization, Person, name, identifiers, location
- `assessment.yaml` — AssessmentBand enum + assessment_band slot
- `external/dhs.yaml` — minimal DHS Recode 7 enum (`DHSWealthIndex`) with explicit `meaning:` URIs
- `publicschema.yaml` — top-level composite (imports everything)
- `_generated/` — generator outputs (gen-owl, gen-shacl, gen-jsonld-context, gen-json-schema)

## What works (confirmed empirically)

| Test | Result |
|---|---|
| `linkml-lint --validate` on every file | passes (only style warnings) |
| `gen-owl` | exit 0, valid Turtle |
| `gen-shacl` | exit 0, valid SHACL |
| `gen-jsonld-context` | exit 0 |
| `gen-json-schema` | exit 0, valid Draft-07 |
| `status: bibo:status/forthcoming` | becomes `bibo:status <http://purl.org/ontology/bibo/status/forthcoming>` in OWL |
| `is_a: Party` + `mixins: [Agent]` (Person) | emits both `rdfs:subClassOf publicschema:Party` and `rdfs:subClassOf publicschema:Agent` in OWL |
| `meaning:` URIs on permissible values | survive as IRIs in OWL |
| `exact_mappings: [dhs:DHSWealthIndex/1]` on AssessmentBand permissible value | resolves to `skos:exactMatch <https://dhsprogram.com/data/recode7/DHSWealthIndex/1>` |
| `exact_mappings` / `close_mappings` on classes and slots | become `skos:exactMatch` / `skos:closeMatch` triples |

## What breaks (and the workaround)

### Annotations cannot hold raw lists

```yaml
# BAD: linkml-runtime rejects compact-form dicts with unknown keys
annotations:
  external_alignments:
    entries:
      - vocabulary: FOAF
        ...
# Error: Annotation.__init__() got an unexpected keyword argument 'entries'
```

```yaml
# GOOD: explicit value: form
annotations:
  external_alignments:
    value:
      entries:
        - vocabulary: FOAF
          ...
```

But even this is degraded in OWL output (see next finding).

### Structured annotation values come out as Python JsonObj() repr in OWL

```turtle
# What gen-owl emits for { external_alignments: { value: { entries: [...] } } }:
publicschema:external_alignments "JsonObj(entries=[{'vocabulary': 'FOAF', 'uri': '...', 'match': 'exact'}, ...])" ;
```

Not parseable JSON. Useless for downstream consumers.

**Workaround**: structured annotation values are JSON-stringified in the LinkML source. The migration script will dump structured data as a JSON string before writing:

```yaml
# What the migration script will emit:
annotations:
  external_alignments_json: '[{"vocabulary":"FOAF","uri":"http://xmlns.com/foaf/0.1/Organization","match":"exact"}]'
```

```turtle
# OWL output (verified):
test:external_alignments_json "[{\"vocabulary\":\"FOAF\",\"uri\":\"...\",\"match\":\"exact\"}]" .
```

Properly escaped JSON in an RDF literal. PublicSchema consumers `json.loads(value)`.

### JSON Schema generator drops all annotations

`gen-json-schema` produces only the typed property structure; annotation values are not in the output at all. Acceptable: JSON Schema is consumed for data validation, not metadata.

### LinkML imports require .yaml extension, not .linkml.yaml

`imports: - external/dhs` resolves to `external/dhs.yaml`, not `external/dhs.linkml.yaml`. All emitted files use `.yaml` extension.

## Conversion rule changes implied for the migration script

1. **All structured annotation values are JSON-stringified.** Keys gain a `_json` suffix to make their encoding explicit:
   - `external_alignments_json` (was: `external_alignments`)
   - `convergence_json`
   - `property_groups_json`
   - `system_mappings_json` (NOTE: per the plan, system_mappings becomes `exact_mappings:` on permissible values; this annotation is for the per-system vocabulary_name / note / etc. that doesn't fit into the LinkML enum value)
   - `sync_json`
   - `standard_json`

2. **Scalar annotations stay as compact form**: `label_fr`, `label_es`, `description_fr`, `description_es`, `category`, `same_standard_systems` (single string), `external_values` (boolean).

3. **Status mapping**:
   - `draft` → `bibo:draft`
   - `candidate` → `bibo:status/forthcoming`
   - `normative` → `bibo:status/published`

4. **All output files use `.yaml` extension** (not `.linkml.yaml`).

5. **Multi-inheritance**: first `supertypes[]` entry → `is_a`, remainder → `mixins`. Per the plan's selection rule plus what `decisions/008-agent-organization.md` implies (Party is receiver-side primary; Agent is mixin for Person).

## Out-of-scope concerns surfaced (for follow-up cutover PR)

- Stock generators do not emit `external_alignments_json` content into JSON Schema. Website renderer cutover needs to read the LinkML YAML source for these, not rely on JSON Schema output.
- `canonical_prefixes` lint warns about `schema: https://schema.org/` (it expects `http://`) and about `semic` (it expects `cpov`). Cosmetic; leaving as is for now since the source uses `https://schema.org/` consistently.
- The DHS prefix URI (`https://dhsprogram.com/data/recode7/`) is site-anchored, not official. Documented in `build/external_system_prefixes.yaml` with `source: site-anchor`.
