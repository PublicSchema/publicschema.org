# Build-scripts cutover plan

The PublicSchema build pipeline now reads authored LinkML from `schema/`.
This note records how the main scripts behave after the cutover and what
still needs follow-up.

## `ps-validate` (`build/validate.py`) — adapted

Today the script runs JSON Schema validation, referential integrity,
multilingual completeness, age_applicability cross-checks against
bibliography citations, and property_groups completeness. The full rule
set has no direct equivalent in stock LinkML tooling: `linkml-validate`
validates *data instances*, and `linkml-lint --validate` only covers
the metamodel.

Current behavior: LinkML is the CLI default. `uv run python -m build.validate`
delegates to `linkml-lint --validate --ignore-warnings` on
`schema/publicschema.yaml`. The historical bespoke validator remains available
for synthetic legacy tests and explicitly requested legacy trees.

## `ps-lint` (`build/lint.py`) — adapted

Custom content linter (jargon, definition quality, em-dash, maturity
gates, external_equivalents URI checks). Stock `linkml-lint` does not
replace any of these rules.

Current behavior: the linter defaults to the LinkML reader and projects
classes, slots, and enums into the site/build read model before running the
same content rules. Explicit bespoke paths are still supported for old-format
unit fixtures.

## `ps-check-translations` (`build/check_translations.py`) — adapted

The schema check requires every candidate/normative entity to carry FR
and ES `definition` (and `label`, when present). The UI/docs/prose
checks are independent of schema source.

Current behavior: LinkML is the default source. The reader
maps LinkML `title` → `label.en`, `description` → `definition.en`,
`annotations.label_fr/es` → `label.fr/es`, `annotations.description_fr/
es` → `definition.fr/es`, then runs the same `_check_definition` /
`_check_label` helpers. Both paths report zero schema errors today.

## `ps-sync` (`build/sync_standards.py`) — kept (with TODO)

Pulls vocabulary values from authoritative external sources (FHIR, ISO,
SIL, etc.). This is the remaining script with old write assumptions: it still
expects `schema/vocabularies/**/*.yaml`. Keep it out of the default v1 path
until it is either rewritten to update LinkML enums directly or replaced by a
separate standards-refresh workflow.
