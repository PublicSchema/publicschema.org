"""Syncs vocabulary values from authoritative external standard sources.

Downloads data from URLs specified in vocabulary YAML `sync` blocks,
parses it using format-specific handlers, and merges the results into
the existing vocabulary values.

Preserves hand-written fields (definitions, translations, system_mappings)
while adding/updating codes from the authoritative source.
"""

import csv
import io
import json
import sys
import xml.etree.ElementTree as ET
from datetime import date, timezone
from pathlib import Path
from urllib.request import urlopen

import yaml


# ---------------------------------------------------------------------------
# Format handlers
#
# Each handler takes raw data (str) and returns a list of parsed values:
#   [{"code": str, "label": {"en": str}, "standard_code": str | None}, ...]
# ---------------------------------------------------------------------------


def _to_snake_case(text: str) -> str:
    """Convert a display name to a snake_case code.

    Examples: "Married" -> "married", "Never Married" -> "never_married",
    "Domestic partner" -> "domestic_partner"
    """
    import re
    # Replace non-alphanumeric with spaces, collapse, strip, lower, join
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().lower()
    return "_".join(cleaned.split())


def parse_fhir_codesystem(data: str) -> list[dict]:
    """Parse a FHIR CodeSystem JSON resource.

    Derives snake_case codes from display names (for compatibility with
    our value code pattern). The original FHIR code is kept as standard_code.
    Recurses into nested concept hierarchies.
    """
    obj = json.loads(data)
    result = []

    def _walk_concepts(concepts: list[dict]) -> None:
        for concept in concepts:
            fhir_code = concept["code"]
            display = concept.get("display", fhir_code)
            result.append({
                "code": _to_snake_case(display),
                "label": {"en": display},
                "standard_code": fhir_code,
            })
            if "concept" in concept:
                _walk_concepts(concept["concept"])

    _walk_concepts(obj.get("concept", []))
    return result


def parse_github_json(data: str) -> list[dict]:
    """Parse ISO 3166 JSON from lukes/ISO-3166-Countries-with-Regional-Codes."""
    entries = json.loads(data)
    result = []
    for entry in entries:
        alpha2 = entry.get("alpha-2", "")
        name = entry.get("name", "")
        if alpha2:
            result.append({
                "code": alpha2.lower(),
                "label": {"en": name},
                "standard_code": alpha2,
            })
    return result


def parse_iso_xml(data: str) -> list[dict]:
    """Parse ISO 4217 currency XML from SIX Group."""
    root = ET.fromstring(data)
    seen = set()
    result = []
    for entry in root.iter("CcyNtry"):
        ccy_el = entry.find("Ccy")
        if ccy_el is None:
            continue
        ccy = ccy_el.text
        if ccy in seen:
            continue
        seen.add(ccy)
        ccy_name = entry.find("CcyNm").text
        result.append({
            "code": ccy.lower(),
            "label": {"en": ccy_name},
            "standard_code": ccy,
        })
    return result


def parse_tsv(data: str) -> list[dict]:
    """Parse ISO 639-3 TSV from SIL International."""
    result = []
    reader = csv.DictReader(io.StringIO(data), delimiter="\t")
    for row in reader:
        code = row.get("Id", "").strip()
        name = row.get("Ref_Name", "").strip()
        if code and name:
            result.append({
                "code": code,
                "label": {"en": name},
                "standard_code": code,
            })
    return result


def parse_semicolon_delimited(data: str) -> list[dict]:
    """Parse ISO 15924 semicolon-delimited script data from Unicode Consortium."""
    result = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(";")
        if len(parts) < 3:
            continue
        script_code = parts[0].strip()
        script_name = parts[2].strip()
        result.append({
            "code": script_code.lower(),
            "label": {"en": script_name},
            "standard_code": script_code,
        })
    return result


def parse_isco_json(data: str) -> list[dict]:
    """Parse ISCO-08 hierarchical JSON from pgmyrek/ISCO_08_Structure.

    Extracts all four levels of the classification hierarchy:
    1-digit major groups, 2-digit sub-major groups, 3-digit minor groups,
    and 4-digit unit groups. Each entry includes ``level`` and
    ``parent_code`` fields to preserve the tree structure.

    Each node has {"name": "CODE - Title", "children": [...]}.
    """
    tree = json.loads(data)
    result = []

    def _parse_name(name: str) -> tuple[str, str]:
        """Split "01 - Commissioned armed forces officers" into ("01", "Commissioned armed forces officers")."""
        parts = name.split(" - ", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return "", name.strip()

    def _walk(node: dict, parent_code: str | None) -> None:
        name = node.get("name", "")
        code, title = _parse_name(name)
        if code and title:
            level = len(code)
            # Append standard_code to ensure uniqueness: ISCO-08 reuses
            # titles across hierarchy levels (e.g., "Commissioned armed
            # forces officers" appears at 2-digit, 3-digit, and 4-digit).
            entry = {
                "code": f"{_to_snake_case(title)}_{code}",
                "label": {"en": title},
                "standard_code": code,
                "level": level,
            }
            if parent_code is not None:
                entry["parent_code"] = parent_code
            result.append(entry)
            # Children use this node's code as their parent
            for child in node.get("children", []):
                _walk(child, code)
        else:
            for child in node.get("children", []):
                _walk(child, parent_code)

    if isinstance(tree, list):
        for node in tree:
            _walk(node, None)
    else:
        _walk(tree, None)

    return result


def parse_csv(data: str) -> list[dict]:
    """Parse UN M49 region CSV from datasets/country-codes.

    Tries multiple columns for the English display name, since CLDR
    display name may use a non-English locale in some versions of the CSV.
    """
    result = []
    reader = csv.DictReader(io.StringIO(data))
    for row in reader:
        alpha2 = row.get("ISO3166-1-Alpha-2", "").strip()
        # Prefer official English names over CLDR display names
        display_name = (
            row.get("UNTERM English Short", "").strip()
            or row.get("official_name_en", "").strip()
            or row.get("CLDR display name", "").strip()
        )
        m49_code = row.get("ISO3166-1-numeric", "").strip()
        if alpha2 and display_name:
            result.append({
                "code": alpha2.lower(),
                "label": {"en": display_name},
                "standard_code": m49_code or alpha2,
            })
    return result


# ---------------------------------------------------------------------------
# Format handler registry
# ---------------------------------------------------------------------------


FORMAT_HANDLERS = {
    "fhir-codesystem": parse_fhir_codesystem,
    "github-json": parse_github_json,
    "iso-xml": parse_iso_xml,
    "tsv": parse_tsv,
    "semicolon-delimited": parse_semicolon_delimited,
    "csv": parse_csv,
    "isco-json": parse_isco_json,
}


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------


def merge_values(
    existing: list[dict],
    parsed: list[dict],
) -> tuple[list[dict], dict]:
    """Merge parsed values into existing vocabulary values.

    Preserves hand-written fields (definition, translations) on existing values.
    Adds new values with a placeholder en-only definition.
    Reports codes that were removed upstream (present in existing, absent in parsed).

    Returns (merged_values, report) where report has keys:
        added: list of new code strings
        removed: list of code strings present in existing but absent in parsed
        updated: list of code strings whose labels or standard_code changed
    """
    existing_by_code = {v["code"]: v for v in existing}
    parsed_by_code = {v["code"]: v for v in parsed}

    report = {"added": [], "removed": [], "updated": []}

    # Identify removed codes (in existing but not in parsed)
    for code in existing_by_code:
        if code not in parsed_by_code:
            report["removed"].append(code)

    merged = []
    for pv in parsed:
        code = pv["code"]
        if code in existing_by_code:
            # Update existing value, preserving hand-written fields
            ev = dict(existing_by_code[code])
            changed = False

            # Update English label if changed
            if pv["label"].get("en") and pv["label"]["en"] != ev.get("label", {}).get("en"):
                ev.setdefault("label", {})["en"] = pv["label"]["en"]
                changed = True

            # Preserve non-English labels (translations)
            # (don't overwrite fr, es, etc. from existing)

            # Update standard_code
            if pv.get("standard_code") and pv["standard_code"] != ev.get("standard_code"):
                ev["standard_code"] = pv["standard_code"]
                changed = True

            # Update hierarchy fields (level, parent_code)
            if pv.get("level") and pv["level"] != ev.get("level"):
                ev["level"] = pv["level"]
                changed = True
            if pv.get("parent_code") and pv["parent_code"] != ev.get("parent_code"):
                ev["parent_code"] = pv["parent_code"]
                changed = True

            if changed:
                report["updated"].append(code)

            merged.append(ev)
        else:
            # New value from sync
            new_value = {
                "code": code,
                "label": dict(pv["label"]),
                "standard_code": pv.get("standard_code"),
            }
            if pv.get("level") is not None:
                new_value["level"] = pv["level"]
            if pv.get("parent_code") is not None:
                new_value["parent_code"] = pv["parent_code"]
            merged.append(new_value)
            report["added"].append(code)

    return merged, report


# ---------------------------------------------------------------------------
# Sync orchestration
# ---------------------------------------------------------------------------


def _download(url: str) -> str:
    """Download data from a URL and return as string."""
    from urllib.request import Request
    req = Request(url, headers={"User-Agent": "PublicSchema-Sync/0.1"})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8")


def sync_vocabulary(
    vocab_path: Path,
    dry_run: bool = False,
) -> dict:
    """Sync a single vocabulary file from its external source.

    Returns a report dict with keys: vocab_id, added, removed, updated, error.
    """
    data = yaml.safe_load(vocab_path.read_text())
    vocab_id = data.get("id", vocab_path.stem)
    sync_config = data.get("sync")

    if not sync_config:
        return {"vocab_id": vocab_id, "skipped": True, "reason": "no sync block"}

    source_url = sync_config["source_url"]
    fmt = sync_config["format"]

    handler = FORMAT_HANDLERS.get(fmt)
    if not handler:
        return {"vocab_id": vocab_id, "error": f"unknown format: {fmt}"}

    try:
        raw_data = _download(source_url)
    except Exception as e:
        return {"vocab_id": vocab_id, "error": f"download failed: {e}"}

    parsed = handler(raw_data)
    existing = data.get("values", [])
    merged, report = merge_values(existing, parsed)

    result = {
        "vocab_id": vocab_id,
        "added": report["added"],
        "removed": report["removed"],
        "updated": report["updated"],
        "total": len(merged),
    }

    if not dry_run:
        data["values"] = merged
        data["sync"]["last_synced"] = date.today().isoformat()
        vocab_path.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False, width=120)
        )

    return result


def find_syncable_vocabularies(schema_dir: Path) -> list[Path]:
    """Find all vocabulary YAML files that have a sync block."""
    vocab_dir = schema_dir / "vocabularies"
    if not vocab_dir.exists():
        return []
    result = []
    for path in sorted(vocab_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        if data and data.get("sync"):
            result.append(path)
    return result


def main():
    """CLI entry point for sync."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync vocabulary values from external standard sources.",
    )
    parser.add_argument(
        "vocab_id",
        nargs="?",
        help="Sync a single vocabulary by ID (e.g., gender-type). Omit to sync all.",
    )
    parser.add_argument(
        "--schema-dir",
        default="schema",
        help="Path to schema directory (default: schema)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    args = parser.parse_args()

    schema_dir = Path(args.schema_dir)

    if args.vocab_id:
        vocab_path = schema_dir / "vocabularies" / f"{args.vocab_id}.yaml"
        if not vocab_path.exists():
            print(f"Error: {vocab_path} not found.", file=sys.stderr)
            sys.exit(1)
        paths = [vocab_path]
    else:
        paths = find_syncable_vocabularies(schema_dir)

    if not paths:
        print("No vocabularies with sync blocks found.")
        return

    prefix = "[DRY RUN] " if args.dry_run else ""
    for path in paths:
        report = sync_vocabulary(path, dry_run=args.dry_run)
        vid = report["vocab_id"]

        if report.get("skipped"):
            print(f"  {vid}: skipped ({report['reason']})")
            continue
        if report.get("error"):
            print(f"  {vid}: ERROR - {report['error']}")
            continue

        added = len(report["added"])
        removed = len(report["removed"])
        updated = len(report["updated"])
        total = report["total"]
        print(f"{prefix}{vid}: {total} values ({added} added, {updated} updated, {removed} removed upstream)")

        if report["removed"]:
            for code in report["removed"]:
                print(f"  WARNING: '{code}' present in YAML but absent from source")


if __name__ == "__main__":
    main()
