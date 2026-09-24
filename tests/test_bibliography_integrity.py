"""Integrity checks for the authored bibliography in schema/bibliography.yaml.

`build.validate` lints the LinkML source but does not check citation
annotation values, so these tests hold the bibliography to the contract in
build/schemas/bibliography.schema.json and to docs/authoring-linkml.md:
term-level `bibliography_refs` annotations and citation `informs_json` stay
consistent.
"""

from __future__ import annotations

import json
from collections import defaultdict

import yaml
from jsonschema import Draft202012Validator

from build.linkml_reader import _convert_class_to_concept, _convert_enum_to_vocabulary
from tests.conftest import SCHEMA_DIR
from tests.schema_reader import raw_schema

BIBLIOGRAPHY_SCHEMA = json.loads(
    (SCHEMA_DIR.parent / "build" / "schemas" / "bibliography.schema.json").read_text(
        encoding="utf-8"
    )
)

CITATION_ANNOTATIONS = {
    "citation_id",
    "title",
    "short_title",
    "standard_number",
    "publisher",
    "authors_json",
    "year",
    "version",
    "type",
    "domain",
    "uri",
    "access",
    "status",
    "note",
    "informs_json",
}


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _citation_classes() -> dict[str, dict]:
    doc = _load(SCHEMA_DIR / "bibliography.yaml")
    return {
        name: cls
        for name, cls in (doc.get("classes") or {}).items()
        if (cls or {}).get("is_a") == "Citation"
    }


def _authored_refs() -> dict[tuple[str, str], tuple[str, set[str]]]:
    """Map (kind, catalog key) to (source label, bibliography_refs) for every term."""
    refs: dict[tuple[str, str], tuple[str, set[str]]] = {}
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        if path.name == "bibliography.yaml":
            continue
        doc = _load(path)
        for section, kind in (
            ("classes", "concepts"),
            ("slots", "properties"),
            ("enums", "vocabularies"),
        ):
            for name, element in (doc.get(section) or {}).items():
                element = element or {}
                value = (element.get("annotations") or {}).get("bibliography_refs")
                if value is None:
                    continue
                if isinstance(value, dict):
                    value = value.get("value")
                if kind == "concepts":
                    converted = _convert_class_to_concept(name, element)
                elif kind == "vocabularies":
                    converted = _convert_enum_to_vocabulary(name, element)
                else:
                    converted = None
                key = converted[0] if converted else name
                refs[(kind, key)] = (f"{path.name}:{name}", set(json.loads(value)))
    return refs


def test_citation_annotations_use_known_keys():
    unknown = []
    for name, cls in _citation_classes().items():
        extra = set(cls.get("annotations") or {}) - CITATION_ANNOTATIONS
        if extra:
            unknown.append(f"{name}: {sorted(extra)}")
    assert not unknown, "Unknown citation annotations:\n" + "\n".join(unknown)


def test_citation_ids_match_class_uris():
    mismatched = []
    for name, cls in _citation_classes().items():
        citation_id = (cls.get("annotations") or {}).get("citation_id")
        if cls.get("class_uri") != f"publicschema:Citation/{citation_id}":
            mismatched.append(f"{name}: {cls.get('class_uri')} vs {citation_id}")
    assert not mismatched, "\n".join(mismatched)


def test_every_entry_matches_the_bibliography_schema():
    validator = Draft202012Validator(BIBLIOGRAPHY_SCHEMA)
    errors = []
    for bib_id, entry in raw_schema()["bibliography"].items():
        for error in validator.iter_errors({"id": bib_id, **entry}):
            errors.append(f"{bib_id}: {error.message}")
    assert not errors, "\n".join(errors)


def test_informs_targets_are_defined_terms():
    raw = raw_schema()
    stale = []
    for bib_id, entry in raw["bibliography"].items():
        for kind, targets in (entry.get("informs") or {}).items():
            for target in targets:
                if target not in raw[kind]:
                    stale.append(f"{bib_id} informs {kind} {target!r}")
    assert not stale, "\n".join(stale)


# General references that ground the site's documentation, credentials and
# serialization rather than a specific term. Every other entry must inform a term.
GENERAL_REFERENCES = {
    "ebsi-ehic",
    "ieee-7012",
    "ilo-aspire",
    "ilo-social-protection-floor",
    "iso-8601",
    "json-ld-1-1",
    "openid4vci",
    "openid4vp",
    "sd-jwt-vc",
    "w3c-data-integrity",
    "w3c-rdfc-1-0",
    "wb-id4d",
}


def test_every_entry_informs_at_least_one_term():
    bibliography = raw_schema()["bibliography"]
    uncited = [
        bib_id
        for bib_id, entry in bibliography.items()
        if bib_id not in GENERAL_REFERENCES and not any((entry.get("informs") or {}).values())
    ]
    assert not uncited, "Entries that inform no term: " + ", ".join(sorted(uncited))
    assert GENERAL_REFERENCES <= set(bibliography), sorted(GENERAL_REFERENCES - set(bibliography))


def test_bibliography_refs_name_existing_entries():
    known = set(raw_schema()["bibliography"])
    unknown = [
        f"{label}: {sorted(refs - known)}"
        for label, refs in _authored_refs().values()
        if refs - known
    ]
    assert not unknown, "\n".join(unknown)


def test_bibliography_refs_agree_with_informs():
    derived: dict[tuple[str, str], set[str]] = defaultdict(set)
    for bib_id, entry in raw_schema()["bibliography"].items():
        for kind, targets in (entry.get("informs") or {}).items():
            for target in targets:
                derived[(kind, target)].add(bib_id)
    authored = _authored_refs()
    mismatches = []
    for key in sorted(set(authored) | set(derived)):
        label, refs = authored.get(key, (f"{key[0]} {key[1]}", set()))
        expected = derived.get(key, set())
        if refs != expected:
            mismatches.append(
                f"{label}: annotation only {sorted(refs - expected)}, "
                f"informs only {sorted(expected - refs)}"
            )
    assert not mismatches, (
        "Term bibliography_refs annotations and citation informs_json disagree:\n"
        + "\n".join(mismatches)
    )
