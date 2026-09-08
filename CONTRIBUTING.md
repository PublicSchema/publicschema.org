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

This installs both Python (`uv sync --locked`) and Node (`npm install`) dependencies.

### Common commands

Run these from the repository root:

```bash
just build               # regenerate exports, metric catalog, and site public artifacts
just validate            # validate the composite LinkML schema
just validate-crosswalks # validate authored value crosswalks and standard metadata
just lint                # check content quality and maturity rules
just check-translations  # check schema, documentation, and UI translations
just test                # run the Python test suite
just dev                 # regenerate data and start the site dev server
just site-build          # validate, regenerate data, and build the production site
just check               # validate, lint, check translations, test, and regenerate data
```

`just check` does not build the production site or assert a clean Git working tree. Inspect the diff after generation; use `just site-build` to verify rendered site compilation.

## How the build works

The authored schema is modular LinkML. `schema/publicschema.yaml` imports the modules containing concepts (`classes`), reusable properties (`slots`), and controlled vocabularies (`enums`). Supporting sources include authored `schema/value_crosswalks/` and `schema/metric_catalog/` files.

1. `build.validate` validates the composite schema with LinkML metamodel validation. Content lint, translation checks, and crosswalk validation are separate commands.
2. `build.build` reads the LinkML source and supporting data, then generates the vocabulary read model, JSON Schemas, JSON-LD, RDF, SHACL, and CSV/Excel downloads under `dist/`.
3. `just build` also prepares the metric catalog and public artifacts consumed by the Astro site. The build uses tools in this repository; no sibling build repository is required.

Edit source files rather than `dist/` or generated artifacts in `site/public/`. Not everything in `site/public/` is generated: it also contains maintained static assets.

Keep browser logs, screenshots, local API caches and generated downloads out of commits. Catalog refresh scripts may populate `build/cache/`; ordinary builds use the checked-in catalog YAML and do not need that cache. Put temporary screenshots and experiments in the ignored `.work/` directory. Keep intentional offline reference artifacts, such as the pinned FHIR validation archives and their provenance, with the examples that require them.

## Adding vocabulary entries

Use [Authoring PublicSchema in LinkML](docs/authoring-linkml.md) for examples and annotation conventions. Add entries to an existing module with related content; when adding a module, import it from `schema/publicschema.yaml` and declare the imports its references need.

### Adding a concept

Add a PascalCase class under `classes:` in a module such as `schema/identity.yaml` or `schema/program.yaml`. Reuse slots through its `slots:` list. Use `is_a` for its primary supertype and `mixins` for additional supertypes. Preserve stable `class_uri` values when changing existing concepts.

Write plain-language `title` and `description` values. Maturity is expressed with `status`: `bibo:draft` (draft), `bibo:status/forthcoming` (candidate), or `bibo:status/published` (normative). French and Spanish labels and definitions use `annotations.label_fr`, `label_es`, `description_fr`, and `description_es`. Candidate and normative entries must meet the translation checks. Use `annotations.featured: true` for featured concepts and native `abstract: true` for concepts that should not be instantiated.

#### Abstract supertypes and registry concepts

Some concepts serve as abstract supertypes rather than directly instantiated records. Profile is an example: it is an abstract concept with five subtypes: SocioEconomicProfile, FunctioningProfile, AnthropometricProfile, FoodSecurityProfile, and DwellingDamageProfile. When adding a concept that represents a point-in-time observation record, consider whether it belongs as a Profile subtype. See `decisions/006-profile-hierarchy.md` (ADR-006) for the rationale.

Agent and Party are the two actor/receiver abstract supertypes. Party groups entities that receive services (Person, Group). Agent groups entities that perform services (Person, Organization, SoftwareAgent). Person belongs to both. When adding a concept that represents an institutional body that acts within delivery (an agency, ministry, NGO, registry office, standards publisher), model it as a subtype of Agent (typically by extending Organization) rather than by adding a new top-level concept. See `decisions/008-agent-organization.md` (ADR-008).

Instrument and SoftwareAgent are registry concepts. Instrument describes a data-collection tool (for example, the WG-SS questionnaire); SoftwareAgent records the software that ran a scoring or eligibility step. New concepts in these categories should follow the same pattern rather than introducing a parallel structure.

### Adding a property

Add a snake_case entry under `slots:` in the appropriate LinkML module and reference it from each class that uses it. Its `range` names a primitive (`string`, `integer`, `date`, etc.), a class, or an enum; `multivalued` controls whether it accepts a list. Use the same title, description, maturity, and translation conventions as classes.

Set `annotations.category` to a key in the `Category` enum in `schema/categories.yaml`. Add a category there before referencing a new key. Structured annotations use JSON strings, for example `annotations.age_applicability_json: '["adult"]'` for instrument-gated Person properties. See [schema-design.md](docs/schema-design.md) for age applicability and cardinality guidance.

For properties revealing circumstances such as health status or poverty, use `annotations.sensitivity`:

- `standard` (default): no special handling beyond normal data protection.
- `sensitive`: reveals circumstances in most contexts and needs justification to collect or disclose.
- `restricted`: should not appear in credentials presented at routine service points.

This annotation warns practitioners about the information; it is not a compliance label. See the sensitivity section of [schema-design.md](docs/schema-design.md) for the rationale.

### Adding a vocabulary

Add a PascalCase entry under `enums:` with stable keys under `permissible_values:`. Each value has an explicit `meaning` URI and a `title`; translations and upstream codes use annotations. Put standard provenance in `annotations.standard_json`. Follow an existing enum in the relevant module or `schema/vocabularies.yaml`.

For external standards, review the authoritative source and update LinkML values by hand using the workflow below. Automatic standards refresh does not yet support the current source format.

## Domain namespacing

Module filenames organize authoring; they do not set a public domain. Choose a domain by the element's meaning, independently of who consumes it. Use consistent explicit `class_uri`, `slot_uri`, `enum_uri`, permissible-value `meaning` and `annotations.source_domain`. A shared property keeps its root URI when a domain concept reuses it. Candidate and normative URIs and meanings remain stable; intentional draft changes require a migration disposition.

A domain-qualified `class_uri`, such as `publicschema:crvs/Person`, distinguishes a term from universal `publicschema:Person`; its LinkML class name is `CrvsPerson` so both can coexist. See [ADR-018](decisions/018-crvs-person-rename.md). Add domain labels to `annotations.domains_json` in the composite when introducing a researched domain; the site discovers represented domains from generated entries. Review the [current domain boundaries and migration guide](docs/domain-migration.md) before adding terms, including native FHIR reuse for medical content.

## Writing style

- Definitions and descriptions: plain language, no jargon. Written for a policy officer, not a developer.
- When researching vocabularies (e.g., marital status, gender), document which international standards exist and how systems diverge before proposing a canonical set.

## System mappings

Author value mappings in `schema/value_crosswalks/*.yaml`. These files are the source of truth for the system mappings displayed by the site, including property mappings where PublicSchema uses a typed value and the external system uses codes. LinkML `exact_mappings` and `close_mappings` still describe term alignments; they do not replace an authored value crosswalk.

Start from an existing crosswalk for the same system, such as `schema/value_crosswalks/marital-status--openspp.yaml`, and follow `build/schemas/value_crosswalk.schema.json`:

1. Identify the PublicSchema vocabulary or property in `source_value_set` and the external system and value set in `target_value_set`.
2. Add `pairs` using canonical `source_value`, actual upstream `target_value` codes, their `target_label`, and mapping `quality`.
3. Record gaps as pairs with `quality: unmapped`: set `source_value: null` for an external code without a canonical equivalent, or `target_value: null` for a canonical value without an external equivalent. Include `unmapped_reason` for unmapped external codes. Do not silently omit values that lack an equivalent.
4. Complete the `standard` provenance and license metadata. For sources without a single canonical artifact, use `artifact_kind: none` with an explanation in `artifact_notes`; otherwise supply the artifact checksum required by the schema.
5. Run `just validate-crosswalks` and regenerate outputs with `just build`.

Keep external terms and provenance consistent with `schema/external/<system>.yaml` and bibliography citations.

## Refreshing external standards

`build/sync_standards.py` supports legacy `schema/vocabularies/**/*.yaml` trees only. `just sync-standards` intentionally exits with an error on the current LinkML tree, including in dry-run mode. Do not use it to refresh this repository or recreate the removed directories to bypass the guard.

Until a LinkML enum writer is implemented, compare the authoritative release with the relevant enum, review additions and removals, and edit its `permissible_values` directly. Preserve stable meanings, translations, and local notes; update `annotations.standard_json` and any `sync_json` provenance to describe the reviewed source. Review affected crosswalks and external partial schemas, then run the checks below. The normal build does not fetch upstream standards.

## Submitting changes

1. Fork the repository and create a branch.
2. Edit the authored LinkML or supporting source, including translations and crosswalks affected by the change.
3. Run `just check`, then `just site-build` for the production site. Resolve errors and inspect warnings rather than assuming generation validates every content rule.
4. Inspect `git diff` and `git status --short`. Review generated changes alongside the source; do not commit build caches or unrelated work.
5. Submit a pull request explaining the semantic change, its sources, and the checks run.

By submitting a pull request, you agree that your contribution is licensed under CC-BY-4.0 (reference model content in `schema/`) and Apache-2.0 (code in `build/`, `tests/`, `site/`).
