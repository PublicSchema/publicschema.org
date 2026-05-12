"""Validate ``schema/value_crosswalks/*.yaml`` for build.

Checks (in order):
1. Every file parses as YAML.
2. Every doc validates against
   ``build/schemas/value_crosswalk.schema.json`` (vendored byte-identical
   from publicschema-build, also used by publicschema.com/apps/core).
3. No ``standard:`` field equals the literal string ``"TODO"`` — option
   (a) from the LinkML cutover design: until every standard is sourced
   (custodian, license, version, retrieved_at, source_sha256, etc.),
   the build refuses to ship.
4. Every crosswalk's ``source_value_set.id`` matches a known
   vocabulary or property in the LinkML composite. This prevents
   crosswalks from silently shadowing renames of the source resource.

Run via ``uv run python -m build.validate_crosswalks`` or the
``just validate-crosswalks`` recipe. Exit code is non-zero on any
issue.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "build" / "schemas" / "value_crosswalk.schema.json"
CROSSWALKS_DIR = ROOT / "schema" / "value_crosswalks"


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _known_sources(schema_dir: Path) -> tuple[set[str], set[str]]:
    """Return (known_vocab_ids, known_property_ids) by running the build
    pipeline far enough to know what sources are valid crosswalk targets.

    We piggyback on ``build_vocabulary`` rather than re-implementing
    composite-key derivation: that function is the single source of
    truth for how vocab ``<domain>/<id>`` keys are formed.
    """
    from build.build import build_vocabulary

    # crosswalks_dir explicitly None so we don't recursively load the
    # crosswalks we're about to validate.
    result = build_vocabulary(schema_dir, crosswalks_dir=Path("/nonexistent"))
    return set(result["vocabularies"].keys()), set(result["properties"].keys())


def validate_all(
    crosswalks_dir: Path = CROSSWALKS_DIR,
    schema_dir: Path = ROOT / "schema",
) -> list[str]:
    """Return a list of error messages; empty means clean."""
    errors: list[str] = []
    if not crosswalks_dir.is_dir():
        return [f"crosswalks directory missing: {crosswalks_dir}"]

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    known_vocabs, known_properties = _known_sources(schema_dir)

    for path in sorted(crosswalks_dir.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            errors.append(f"{path.name}: yaml parse error: {e}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{path.name}: top-level document is not a mapping")
            continue

        for err in validator.iter_errors(doc):
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(f"{path.name}: schema violation at {loc}: {err.message}")

        std = doc.get("standard") or {}
        if isinstance(std, dict):
            todo_fields = sorted(k for k, v in std.items() if v == "TODO")
            if todo_fields:
                errors.append(
                    f"{path.name}: standard metadata has TODO placeholders for "
                    f"{', '.join(todo_fields)}. Populate "
                    f"schema/external_references/<system>.yaml or set these "
                    f"fields directly."
                )

        src = doc.get("source_value_set") or {}
        kind = src.get("kind")
        sid = src.get("id")
        if kind == "vocabulary" and isinstance(sid, str) and sid not in known_vocabs:
            errors.append(
                f"{path.name}: source_value_set.id {sid!r} is not a known "
                f"vocabulary key in the LinkML composite."
            )
        elif kind == "property" and isinstance(sid, str) and sid not in known_properties:
            errors.append(
                f"{path.name}: source_value_set.id {sid!r} is not a known "
                f"property key in the LinkML composite."
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    errors = validate_all()
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(
            f"\n{len(errors)} crosswalk validation error(s). "
            f"Build refuses to ship until resolved.",
            file=sys.stderr,
        )
        return 1
    print("All value_crosswalks valid.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
