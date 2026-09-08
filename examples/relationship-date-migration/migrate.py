"""Convert the named draft relationships from inclusive calendar validity dates.

This example helper returns a new JSON document and never rewrites its input file.
It is deliberately independent of the repository's vocabulary build machinery.
"""
import argparse
import copy
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

RELATIONSHIPS = {
    "HoldingParcelLink", "AnimalResidence", "AnimalResponsibility",
    "ProducerMembership", "AgriculturalServiceRole", "InputSupplierRole",
    "PesticideApplicatorRole", "SeedOperatorRole",
    "IdentifierAssignment", "NameUsage", "ContactPoint",
}
TRANSFORMED_ASSIGNMENTS = {"AssetPartyRole", "AssetAddressAssignment"}
RETIRED_ASSIGNMENTS = {"FacilityManagementAssignment", "FacilityAddressAssignment"}
AGRICULTURAL_RELATIONSHIPS = {
    "HoldingParcelLink", "AnimalResidence", "ProducerMembership",
    "AgriculturalServiceRole", "InputSupplierRole", "PesticideApplicatorRole", "SeedOperatorRole",
}
TYPE_ALIASES = {}
for _name in RELATIONSHIPS | TRANSFORMED_ASSIGNMENTS | RETIRED_ASSIGNMENTS:
    TYPE_ALIASES.update({value: _name for value in (
        _name, "publicschema:" + _name, "https://publicschema.org/" + _name,
    )})
    if _name in AGRICULTURAL_RELATIONSHIPS:
        TYPE_ALIASES.update({value: _name for value in (
            "agri/" + _name, "publicschema:agri/" + _name,
            "https://publicschema.org/agri/" + _name,
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
    legacy dates occur. Missing bounds stay missing. Exact authored class names,
    historical root URIs and the named new domain URIs are recognized. The helper
    preserves type identifiers; context expansion and URI migration are separate.
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
        if kind == "FacilityManagementAssignment":
            report(path, "ambiguous-facility-management", "Review the source responsibility before selecting an AssetPartyRole; management does not identify operator, upkeep or owner.")
            return
        if kind == "FacilityAddressAssignment":
            report(path, "address-purpose-review-required", "Review the source address purpose and transform the class and endpoint fields to AssetAddressAssignment before converting dates.")
            return
        legacy = any(field in record for field in OLD_DATES)
        if legacy and any(field in record for field in CURRENT_DATES):
            report(path, "mixed-date-pairs", "Both date pairs occur; reconcile them from the source before migration.")
            return
        if legacy and source_boundary != SOURCE_BOUNDARY:
            report(path, "unknown-source-boundary", "Confirm inclusive-calendar-days from the source contract before converting legacy dates.")
            return
        if legacy and kind in TRANSFORMED_ASSIGNMENTS:
            field = "asset_role_type" if kind == "AssetPartyRole" else "address_purpose"
            code = record.get(field)
            endpoints = ("asset_subject", "asset_actor" if kind == "AssetPartyRole" else "assigned_address")
            retired_fields = {"managed_facility", "managing_organization", "addressed_facility", "facility_address"}
            if any(key not in record for key in endpoints) or retired_fields & record.keys():
                report(path, "incomplete-assignment-transformation", "Transform the retired endpoint fields explicitly before converting this assignment's dates.")
                return
            if (not isinstance(code, dict) or not isinstance(code.get("code_value"), str)
                    or not code["code_value"] or not isinstance(code.get("code_scheme"), str)
                    or not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", code["code_scheme"])):
                report(f"{path}/{field}", "assignment-meaning-required", "Supply the source-reviewed role or address purpose as a scheme-qualified code before converting dates.")
                return
        fields = OLD_DATES if legacy else CURRENT_DATES
        before = len(diagnostics)
        start, end = (parse_day(record[field], f"{path}/{field}") if field in record else None for field in fields)
        if start and end and (end < start if legacy else end <= start):
            report(path, "invalid-period", "The period must contain at least one effective calendar day.")
        if legacy and end == date.max:
            report(f"{path}/valid_to", "unrepresentable-end-date", "The day after 9999-12-31 is outside the supported calendar; do not replace it with an unknown end.")
        if len(diagnostics) != before or not legacy:
            return
        if "valid_from" in record:
            record["start_date"] = record.pop("valid_from")
        if "valid_to" in record:
            record.pop("valid_to")
            record["end_date"] = (end + timedelta(days=1)).isoformat()

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
    except (OSError, json.JSONDecodeError):
        print(json.dumps({"errors": [{"path": "/", "code": "unreadable-json", "message": "The input could not be read as a JSON document."}]}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
