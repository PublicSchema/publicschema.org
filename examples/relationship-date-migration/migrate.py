"""Rename inclusive source validity dates on the named relationships to start_date/end_date.

This example helper returns a new JSON document and never rewrites its input file.
It is deliberately independent of the repository's vocabulary build machinery.
"""
import argparse
import copy
import json
import re
import sys
from datetime import date
from pathlib import Path

RELATIONSHIPS = {
    "HoldingParcelLink", "AnimalResidence", "AnimalResponsibility",
    "AgriculturalServiceRole", "IdentifierAssignment", "NameUsage", "ContactPoint",
}
QUALIFIED_ASSIGNMENTS = {"AssetPartyRole", "AssetAddressAssignment"}
AGRICULTURAL_RELATIONSHIPS = {"HoldingParcelLink", "AnimalResidence", "AgriculturalServiceRole"}
TYPE_ALIASES = {}
for _name in RELATIONSHIPS | QUALIFIED_ASSIGNMENTS:
    _path = "agri/" + _name if _name in AGRICULTURAL_RELATIONSHIPS else _name
    TYPE_ALIASES.update({value: _name for value in (
        _name, _path, "publicschema:" + _path, "https://publicschema.org/" + _path,
    )})
SOURCE_BOUNDARY = "inclusive-calendar-days"
OLD_DATES = ("valid_from", "valid_to")
CURRENT_DATES = ("start_date", "end_date")


class MigrationError(ValueError):
    """Field-addressed diagnostics for a document that cannot be migrated."""

    def __init__(self, diagnostics):
        self.diagnostics = diagnostics
        super().__init__("; ".join(f"{d['path']}: {d['message']}" for d in diagnostics))


def migrate_relationship_dates(document, *, source_boundary=None):
    """Return a copy with the named relationship dates converted, or fail as a whole.

    The caller must establish SOURCE_BOUNDARY from the source contract whenever
    source validity dates occur. Missing bounds stay missing. The compact class
    alias and the exact PublicSchema identifiers are recognized. The helper
    preserves type identifiers; mapping source record types and context expansion
    are separate steps.
    """
    result = copy.deepcopy(document)
    diagnostics = []

    def report(path, code, message):
        diagnostics.append({"path": path or "/", "code": code, "message": message})

    def parse_day(value, path):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            report(path, "invalid-calendar-date", "Expected an exact YYYY-MM-DD calendar date; no date was inferred.")
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            report(path, "invalid-calendar-date", "The value is not a possible calendar date.")
            return None

    def migrate(record, path):
        raw_kind = record.get("@type")
        kind = TYPE_ALIASES.get(raw_kind) if isinstance(raw_kind, str) else None
        if kind is None:
            candidates = raw_kind if isinstance(raw_kind, list) else [raw_kind]
            for candidate in candidates:
                if isinstance(candidate, str) and re.split(r"[/#:]", candidate)[-1] in TYPE_ALIASES:
                    report(f"{path}/@type", "unsupported-type-identifier", "Use one exact admitted type identifier; a matching local name or context alias does not establish class identity.")
                    break
            return
        source_dates = any(field in record for field in OLD_DATES)
        if source_dates and any(field in record for field in CURRENT_DATES):
            report(path, "mixed-date-pairs", "Both date pairs occur; reconcile them from the source before migration.")
            return
        if source_dates and source_boundary != SOURCE_BOUNDARY:
            report(path, "unknown-source-boundary", "Confirm inclusive-calendar-days from the source contract before converting source validity dates.")
            return
        if source_dates and kind in QUALIFIED_ASSIGNMENTS:
            field = "asset_role_type" if kind == "AssetPartyRole" else "address_purpose"
            code = record.get(field)
            endpoints = ("subject_uri", "asset_actor" if kind == "AssetPartyRole" else "assigned_address")
            if any(key not in record for key in endpoints):
                report(path, "incomplete-assignment-transformation", "Map the asset and its party or address explicitly before converting this assignment's dates.")
                return
            if (not isinstance(code, dict) or not isinstance(code.get("code_value"), str)
                    or not code["code_value"] or not isinstance(code.get("code_scheme"), str)
                    or not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", code["code_scheme"])):
                report(f"{path}/{field}", "assignment-meaning-required", "Supply the source-reviewed role or address purpose as a scheme-qualified code before converting dates.")
                return
        fields = OLD_DATES if source_dates else CURRENT_DATES
        before = len(diagnostics)
        start, end = (parse_day(record[field], f"{path}/{field}") if field in record else None for field in fields)
        if start and end and end < start:
            report(path, "invalid-period", "The period must contain at least one effective calendar day.")
        if len(diagnostics) != before or not source_dates:
            return
        if "valid_from" in record:
            record["start_date"] = record.pop("valid_from")
        # Both pairs include their end day, so the dates carry over unchanged.
        if "valid_to" in record:
            record["end_date"] = record.pop("valid_to")

    def visit(value, path):
        if isinstance(value, list):
            for position, item in enumerate(value):
                visit(item, f"{path}/{position}")
        elif isinstance(value, dict):
            migrate(value, path)
            for key in sorted(value):
                escaped = key.replace("~", "~0").replace("/", "~1")
                visit(value[key], f"{path}/{escaped}")

    visit(result, "")
    if diagnostics:
        raise MigrationError(diagnostics)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source JSON file; output is written only to stdout")
    parser.add_argument("--source-boundary", choices=[SOURCE_BOUNDARY], help="Use only after confirming the source dates include the entire last day")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text())
        result = migrate_relationship_dates(document, source_boundary=args.source_boundary)
    except MigrationError as error:
        print(json.dumps({"errors": error.diagnostics}, indent=2), file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as error:
        reason = error.strerror if isinstance(error, OSError) else str(error)
        message = f"The input could not be read as a JSON document: {reason}."
        print(json.dumps({"errors": [{"path": "/", "code": "unreadable-json", "message": message}]}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
