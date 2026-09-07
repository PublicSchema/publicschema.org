# Build scripts after the LinkML cutover

PublicSchema authors its reference model in modular LinkML under `schema/`. The migration is complete for the default read/build path. This page records current script boundaries; use [Contributing](../CONTRIBUTING.md) for the normal contribution workflow.

## Validation and content checks

`just validate` runs `build.validate`, which delegates to `linkml-lint --validate --ignore-warnings` on `schema/publicschema.yaml`. This checks the LinkML metamodel. It does not run the former bespoke JSON Schema and referential-integrity validation suite against the current source. Stock `linkml-validate` validates data instances, not the schema itself.

`just lint` runs PublicSchema content rules against the LinkML read model, including definition quality and maturity gates. `just check-translations` checks candidate/normative schema translations as well as documentation and UI coverage. The reader maps English `title` and `description`, and `annotations.label_fr/es` and `description_fr/es`, into the multilingual read model.

`just validate-crosswalks` separately checks authored `schema/value_crosswalks/*.yaml` against the crosswalk schema, verifies known source IDs, and rejects incomplete standard metadata. Use these files for system value mappings; migrated per-value annotations are not their source of truth.

Explicit legacy-source options remain for old-format fixtures and historical trees. They are not needed for contributions to the current schema.

## Generation and site preparation

`just build` uses repository-local Python tools to generate `dist/` exports and `dist/metrics_catalog.json`, then prepare generated artifacts in `site/public/`. It requires no sibling build repository. `just metrics-data` regenerates only the metric catalog from `schema/metric_catalog/`.

For direct invocation, use `uv run --locked python -m build.build --site-public-dir site/public`. Without `--site-public-dir`, the canonical build generates `dist/` but does not copy site public artifacts. Astro also serves context, RDF, JSON-LD, and manifest routes from `dist/` through its endpoints.

`just check` runs validation, crosswalk validation, content lint, translation checks, tests, and generation. It does not check Git cleanliness or compile Astro. Use `just site-build` for a production site build and inspect the diff after generation.

## Standards refresh limitation

`build/sync_standards.py` still writes the legacy `schema/vocabularies/**/*.yaml` format. `just sync-standards` intentionally refuses the current LinkML tree, even with the script's `--dry-run` option. It is outside the supported contribution workflow until a LinkML enum writer exists.

Refresh a standard by reviewing its authoritative release and editing the relevant LinkML enum and provenance annotations, preserving stable meanings and local translations. Review related external partial schemas and authored value crosswalks, then run the normal checks. See [Refreshing external standards](../CONTRIBUTING.md#refreshing-external-standards).
