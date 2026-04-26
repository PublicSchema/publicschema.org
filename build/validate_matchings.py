"""Validates external/<system>/matching.yaml files.

Each matching file documents how an external system's concepts, vocabularies,
and properties align with PublicSchema. The canonical shape lives at
build/schemas/matching.schema.json. This validator returns a list of
ValidationError objects (empty means valid), matching the conventions of
build/validate.py so failures surface through the same pipeline.
"""

import json
import sys
from pathlib import Path

import jsonschema
import yaml

from build.validate import ValidationError

SCHEMA_PATH = Path(__file__).parent / "schemas" / "matching.schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_matchings_dir(external_dir: Path) -> list[ValidationError]:
    """Validate every external/<system>/matching.yaml under ``external_dir``.

    Returns a list of ValidationError objects; empty list means valid.
    Missing ``external_dir`` and absent matching.yaml files are not errors.
    """
    if not external_dir.exists():
        return []

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[ValidationError] = []

    for path in sorted(external_dir.glob("*/matching.yaml")):
        rel = path.relative_to(external_dir.parent) if external_dir.parent.exists() else path
        filename = str(rel)
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            errors.append(ValidationError(filename, f"YAML parse error: {exc}"))
            continue
        if not isinstance(data, dict):
            errors.append(ValidationError(filename, "Top-level YAML is not a mapping"))
            continue
        for error in validator.iter_errors(data):
            location = "/".join(str(p) for p in error.absolute_path)
            loc = f" at {location}" if location else ""
            errors.append(ValidationError(filename, f"{error.message}{loc}"))

    return errors


def main() -> None:
    """CLI entry point."""
    external_dir = Path("external")
    if len(sys.argv) > 1:
        external_dir = Path(sys.argv[1])

    issues = validate_matchings_dir(external_dir)
    if issues:
        print(f"Matching validation failed with {len(issues)} error(s):")
        for e in issues:
            print(f"  - {e}")
        sys.exit(1)
    print("Matching validation passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
