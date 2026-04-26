"""One-off normalizer that brings each external/<system>/matching.yaml into
conformance with build/schemas/matching.schema.json.

Transformations applied:
  * Rename ocha-cods sections: concepts -> concept_matches,
    properties -> matches, unmapped_v2_properties -> no_match.
  * Ensure concept_matches, matches, no_match, external_excess sections
    exist (empty list if missing).
  * Split each existing no_match list: entries with v2_* refs stay in
    no_match; entries with external_* refs move to external_excess.
  * Drop ``match: None`` from match entries (the YAML literal None,
    surfacing as Python None, indicates the field was unset). The match
    field is optional on `matches`; required only on `concept_matches`.
  * Preserve all other keys and free-text fields verbatim.

Run once, then delete (or keep around as documentation of the migration).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = REPO_ROOT / "external"

V2_KEYS = ("v2_concept", "v2_vocabulary", "v2_property")
EXTERNAL_KEYS = ("external_vocabulary", "external_field", "external_entity")


def normalize(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict):
        raise SystemExit(f"{path}: top-level is not a mapping")

    # Rename ocha-cods-style sections.
    if "concepts" in raw and "concept_matches" not in raw:
        raw["concept_matches"] = raw.pop("concepts")
    if "properties" in raw and "matches" not in raw:
        # ocha-cods uses 'properties' as its matches list (property-level mappings).
        raw["matches"] = raw.pop("properties")
    if "unmapped_v2_properties" in raw and "no_match" not in raw:
        raw["no_match"] = raw.pop("unmapped_v2_properties")

    # Ensure all required sections exist as lists.
    for section in ("concept_matches", "matches", "no_match", "external_excess"):
        raw.setdefault(section, [])
        if raw[section] is None:
            raw[section] = []

    # ocha-cods used `property:` as the inner ref key on no_match entries;
    # normalize to v2_property. Idempotent: safe to re-run.
    for entry in raw["no_match"]:
        if isinstance(entry, dict) and "property" in entry and "v2_property" not in entry:
            entry["v2_property"] = entry.pop("property")

    # Split no_match by ref direction.
    new_no_match = []
    moved_to_excess = []
    for entry in raw["no_match"]:
        if not isinstance(entry, dict):
            new_no_match.append(entry)
            continue
        has_v2 = any(entry.get(k) for k in V2_KEYS)
        has_external = any(entry.get(k) for k in EXTERNAL_KEYS)
        if has_v2:
            new_no_match.append(entry)
        elif has_external:
            moved_to_excess.append(entry)
        else:
            # No ref of either kind. Leave in no_match for the validator to flag;
            # better to surface than to silently drop.
            new_no_match.append(entry)
    raw["no_match"] = new_no_match
    raw["external_excess"] = list(raw["external_excess"]) + moved_to_excess

    # Split matches: entries describing an external-only field with no v2
    # counterpart belong in external_excess, not matches. Promote `notes` to
    # `reason` since external_excess requires `reason`.
    new_matches = []
    promoted_to_excess = []
    for entry in raw["matches"]:
        if not isinstance(entry, dict):
            new_matches.append(entry)
            continue
        has_v2 = any(entry.get(k) for k in V2_KEYS)
        has_external = any(entry.get(k) for k in EXTERNAL_KEYS)
        if has_v2:
            new_matches.append(entry)
        elif has_external:
            promoted = {k: v for k, v in entry.items() if k != "notes"}
            promoted["reason"] = entry.get("notes") or entry.get("reason") or ""
            # external_excess additionalProperties: false; strip non-allowed keys.
            allowed = {"external_vocabulary", "external_field", "external_entity",
                       "external_source", "reason"}
            promoted = {k: v for k, v in promoted.items() if k in allowed}
            promoted_to_excess.append(promoted)
        else:
            new_matches.append(entry)
    raw["matches"] = new_matches
    raw["external_excess"] = list(raw["external_excess"]) + promoted_to_excess

    # Drop top-level null fields on each match-like entry (YAML missing-field
    # artifacts). Nested nulls are preserved (e.g. `value_mapping: {"02": ~}`
    # legitimately means "external code 02 has no PublicSchema equivalent").
    for section in ("concept_matches", "matches"):
        for entry in raw[section]:
            if not isinstance(entry, dict):
                continue
            for k in [k for k, v in entry.items() if v is None]:
                del entry[k]

    # Stable section order in the output.
    ordered: dict[str, Any] = {}
    head_keys = (
        "system",
        "system_version",
        "source_repository",
        "source_branch",
        "fhir_repository",
        "fhir_branch",
        "country_config_reference",
        "last_reviewed",
    )
    for k in head_keys:
        if k in raw:
            ordered[k] = raw[k]
    for section in ("concept_matches", "matches", "no_match", "external_excess"):
        ordered[section] = raw[section]
    # Preserve any unexpected leftovers so we don't silently drop data.
    for k, v in raw.items():
        if k not in ordered:
            ordered[k] = v

    return ordered


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )
    path.write_text(text)


def main() -> None:
    matching_files = sorted(EXTERNAL_DIR.glob("*/matching.yaml"))
    if not matching_files:
        print("No matching.yaml files found", file=sys.stderr)
        raise SystemExit(1)
    for path in matching_files:
        before = yaml.safe_load(path.read_text())
        after = normalize(path)
        write_yaml(path, after)
        moved = len(after["external_excess"]) - len(
            before.get("external_excess") or []
        )
        print(
            f"{path.relative_to(REPO_ROOT)}: "
            f"concept_matches={len(after['concept_matches'])} "
            f"matches={len(after['matches'])} "
            f"no_match={len(after['no_match'])} "
            f"external_excess={len(after['external_excess'])} "
            f"(moved {moved} from no_match)"
        )


if __name__ == "__main__":
    main()
