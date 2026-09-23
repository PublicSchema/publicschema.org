# Examples

Each directory holds synthetic records for one draft area, and some hold a small
script that checks them. The guides under `docs/` explain what each example
shows. The JSON files at this level are credential examples.

## Running a script

Run scripts from the repository root with the locked project environment:

```bash
uv run --locked python examples/farm-operators/validate_profile.py
```

A profile script prints a line saying it passed, or exits nonzero naming the
failed rule. The FHIR check and the date migration also print their JSON result.
`tests/test_example_commands.py` runs every documented command; the focused
tests for each example are in `tests/`.

## Profiles are local rules

A profile script is an example of rules one application might add on top of the
vocabulary: required fields, which kind of record a reference must point to,
date order, or percentage bounds. The vocabulary, its JSON Schemas and its SHACL
shapes do not enforce these rules, and neither does any Registry Stack runtime.
Copy and change a profile to suit your own data exchange.

## Shared helpers

`shared/profile_support.py` holds the checks every profile needs in the same form:

- `parse_day` accepts only an exact `YYYY-MM-DD` calendar date.
- `check_period` applies the two date conventions. `start_date` and `end_date`
  are end-exclusive: `end_date` is the first day the record no longer applies,
  so the end must fall after the start. `valid_from` and `valid_to` are
  inclusive: `valid_to` is the last valid day, so a one-day validity is allowed.
- `absolute_uri` and `coded_value` check references and classifications.

Scripts import it by adding `examples/shared` to `sys.path`, so each one still
runs as a single file without installing a package.

## Duplicate records

Most profiles take a flat list of records and reject a repeated `@id`. The
farm-operators profile accepts a record that appears again with identical
content, because JSON-LD may embed a record where it is referenced. It still
rejects two different records with the same `@id`.
