# Contributing to PublicSchema

## Development setup

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22.12+ (see `.node-version`)
- [just](https://just.systems/) command runner

### Install dependencies

```bash
just setup
```

This installs both Python (`uv sync`) and Node (`npm install`) dependencies.

### Common commands

```bash
just build          # generate vocabulary data from YAML sources
just validate       # validate all YAML source files
just dev            # start dev server (rebuilds data first)
just site-build     # full production build (validates + builds data + builds site)
just check          # validate + build, verify everything is clean
just sync-standards # re-sync external standard vocabularies
```

### Running tests

```bash
uv run pytest       # Python tests (schema validation, build pipeline, exports)
```

## How the build works

Data flows one direction:

```
schema/ (YAML) --> build pipeline --> dist/ (JSON, CSV, XLSX, TTL, SHACL) --> site/ (Astro) --> static HTML
```

1. `build.validate` checks all YAML files against JSON Schemas and validates referential integrity.
2. `build.build` reads YAML sources and generates `dist/vocabulary.json`, `dist/context.jsonld`, JSON Schemas, RDF exports (Turtle, JSON-LD, SHACL), and downloadable files (CSV, Excel).
3. The Astro site reads `dist/vocabulary.json` and renders the website.

## Adding vocabulary entries

### Adding a concept

Create a YAML file in `schema/concepts/`. Follow existing files as a template.

Key fields:
- `name`: PascalCase, no domain prefix (use `Enrollment`, not `SPEnrollment`)
- `definition`: plain language, written for a policy officer. 1-3 sentences.
- `domain`: set to `sp` for social-protection-specific concepts, omit for universal concepts
- `maturity`: one of `draft`, `stable`, `deprecated`
- `properties`: list of property references
- `translations`: definitions in `fr` and `es`

### Adding a property

Create a YAML file in `schema/properties/`. Properties are independent and reusable across concepts.

Key fields:
- `name`: snake_case
- `definition`: plain language
- `type`: the data type (string, date, integer, concept reference, vocabulary reference)
- `used_by`: list of concepts that use this property

#### Sensitivity annotations

Properties that reveal circumstances (health status, poverty, victimhood) in most contexts should include a `sensitivity` field:

- `standard` (default, can be omitted): no special handling beyond normal data protection
- `sensitive`: reveals circumstances in most contexts; requires justification to collect or disclose (e.g., `program_ref`, `grievance_type`, `education_level`)
- `restricted`: should not appear in credentials presented at routine service points; requires a data protection impact assessment (e.g., assessment scores, vulnerability indices)

This is a practitioner warning about the nature of the information, not a compliance label. See `docs/design-principles.md` section 12 for the full rationale.

### Adding a vocabulary

Create a YAML file in `schema/vocabularies/`.

For vocabularies that reference international standards, include `sync` metadata so the sync script can update values automatically. For domain-specific vocabularies, define values by hand with clear definitions.

## Domain namespacing

Concepts are namespaced by domain in their URI, not prefixed in their name.

- Domain-specific concepts get a domain segment: `publicschema.org/sp/Enrollment`
- Universal concepts live at the root: `publicschema.org/Person`
- The `domain` field in concept YAML drives this

Current domain codes:

| Code | Domain | Status |
|---|---|---|
| `sp` | Social protection | Active |
| `edu` | Education | Future |
| `health` | Health | Future |
| `crvs` | Civil registration and vital statistics | Future |

## Writing style

- Definitions and descriptions: plain language, no jargon. Written for a policy officer, not a developer.
- When researching vocabularies (e.g., marital status, gender), document which international standards exist and how systems diverge before proposing a canonical set.

## System mappings

System mappings show each external system's full vocabulary for a given concept: their code, their label, and the mapping to our canonical value. Gaps are explicit in both directions: system values with no PublicSchema equivalent appear as unmapped rows (`maps_to: null`), and PublicSchema values with no system equivalent are listed in `unmapped_canonical`.

This serves two audiences:
- **Integration developers** who need to know what codes a system sends and how to convert them
- **Domain experts** who need to see where vocabularies diverge across systems

When adding or updating system mappings:

1. Use the enriched format (code + label + maps_to), not the flat format
2. Get codes and labels from `enums.json` when available (see `docs/vocabulary-extraction-process.md`)
3. The `code` must be what the system stores in its database, not a human label
4. Show the full picture: include all system values, even those with no canonical equivalent
5. List all canonical values not covered by the system in `unmapped_canonical`
6. When `maps_to` is null, include `unmapped_reason` to explain why:
   - `no_equivalent`: the system code has no semantic match in our vocabulary
   - `not_yet_mapped`: a canonical value could exist but hasn't been added yet
   - `out_of_scope`: the code is from a domain we don't cover
   - `context_dependent`: the mapping varies by deployment

See `docs/vocabulary-extraction-process.md` Phase 4 for the complete format specification.

## External standard syncing

Vocabularies that reference international standards are synced from authoritative sources using `build/sync_standards.py`. Synced vocabularies have `sync: { source_url, format, last_synced }` in their YAML. The sync script updates the `values` list and `last_synced` timestamp but never overwrites hand-written fields.

Run `just sync-standards` to re-sync all external vocabularies.

## Submitting changes

1. Fork the repository and create a branch.
2. Make your changes and ensure `just check` passes.
3. Run `uv run pytest` to verify tests pass.
4. Submit a pull request with a clear description of what you changed and why.

By submitting a pull request, you agree that your contribution is licensed under CC-BY-4.0 (vocabulary content in `schema/`) and Apache-2.0 (code in `build/`, `tests/`, `site/`).
