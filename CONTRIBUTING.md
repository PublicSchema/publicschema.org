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
schema/ (YAML) --> build pipeline --> dist/ (JSON, CSV, XLSX) --> site/ (Astro) --> static HTML
```

1. `build.validate` checks all YAML files against JSON Schemas and validates referential integrity.
2. `build.build` reads YAML sources and generates `dist/vocabulary.json`, `dist/context.jsonld`, JSON Schemas, and downloadable files (CSV, Excel).
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
- `data_classification`: `non_personal`, `personal`, or `special_category` (see rules below)
- `used_by`: list of concepts that use this property

### Adding a vocabulary

Create a YAML file in `schema/vocabularies/`.

For vocabularies that reference international standards, include `sync` metadata so the sync script can update values automatically. For domain-specific vocabularies, define values by hand with clear definitions.

### Data classification rules

Every property has a `data_classification` field. Follow these rules:

1. **Person references are personal.** Any property whose value identifies or points to a natural person is `personal`. This includes direct person references, references to person-specific records, and properties that reveal group composition.
2. **Program-level metadata is non_personal.** Thresholds, design parameters, statuses, and dates that apply uniformly to all participants are `non_personal`.
3. **Special_category is about inherent content sensitivity.** Reserve it for data whose value is itself sensitive: individual assessment scores, vulnerability indices. A reference to an assessment event is `personal`, not `special_category`.
4. **When in doubt, classify up.** Choose `personal` over `non_personal`. Implementers can relax handling; they cannot retroactively tighten it.

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

## External standard syncing

Vocabularies that reference international standards are synced from authoritative sources using `build/sync_standards.py`. Synced vocabularies have `sync: { source_url, format, last_synced }` in their YAML. The sync script updates the `values` list and `last_synced` timestamp but never overwrites hand-written fields.

Run `just sync-standards` to re-sync all external vocabularies.

## Submitting changes

1. Fork the repository and create a branch.
2. Make your changes and ensure `just check` passes.
3. Run `uv run pytest` to verify tests pass.
4. Submit a pull request with a clear description of what you changed and why.
