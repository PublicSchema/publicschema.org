"""Schema content linter for PublicSchema.

Checks content quality and style beyond structural validation.
Complements build.validate (which checks structure and referential integrity)
with semantic rules about definition quality, naming style, and maturity gates.

Rules:
  W001  Jargon in English definition
  W002  English definition too short
  W003  Circular definition (starts with the concept's own name)
  W004  English definition missing terminal punctuation
  S001  Em dash (U+2014) in text
  S002  English label ends with a period
  S003  Unknown ALL CAPS word in English definition
  E001  Malformed URI in external_equivalents
  E002  Match (not none) without URI in external_equivalents
  E003  URI without match in external_equivalents
  V001  Vocabulary has only one value
  V002  Large vocabulary (>50 values) without sync block
  M001  Candidate/normative concept without external_equivalents
  M002  Normative non-abstract concept without property_groups
  M003  Normative concept without convergence data
  X001  Category defined but never used by any concept

Sources
-------
Default ``--source bespoke`` reads schema/**/*.yaml in the historical
PublicSchema shape (label/definition as multilingual dicts, sync block at
the top level, external_equivalents nested under each concept).

``--source linkml`` reads dist/linkml/**/*.yaml (LinkML output from
build/migrate_to_linkml.py). The LinkML shape stores the English label as
``title``, English description as ``description``, and other locales under
``annotations.label_fr`` / ``annotations.label_es`` /
``annotations.description_fr`` / ``annotations.description_es``. The
external alignments live under ``annotations.external_alignments_json``
(a JSON string), the convergence summary under
``annotations.convergence_json``, and the sync block under
``annotations.sync_json``. The LinkML reader normalises these back to the
bespoke shape so the same lint rules apply unchanged.

The LinkML reader is a thin adapter; it is intentionally limited to the
fields the rule set needs, not a full LinkML-to-PublicSchema round-trip.
"""

import json
import re
import sys
from pathlib import Path

import yaml

from build.loader import load_all_yaml, load_yaml

# ---------------------------------------------------------------------------
# LintIssue
# ---------------------------------------------------------------------------


class LintIssue:
    """A single lint finding with rule code and context."""

    def __init__(self, file: str, message: str, rule: str, severity: str = "warning"):
        self.file = file
        self.message = message
        self.rule = rule
        self.severity = severity

    def __str__(self):
        return f"[{self.rule}] {self.file}: {self.message}"

    def __repr__(self):
        return (
            f"LintIssue({self.file!r}, {self.message!r}, "
            f"rule={self.rule!r}, severity={self.severity!r})"
        )


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# W001: developer jargon that should not appear in definitions aimed at
# policy officers. Word-boundary matching (\b) avoids partial matches.
# "field" excluded (legitimate non-technical uses, e.g. "football field").
# "schema" excluded (appears in the project's own name).
JARGON_WORDS = [
    "fk", "foreign key", "database", "table", "column",
    "payload", "endpoint", "nullable", "sql", "orm",
    "backend", "frontend", "json", "xml", "csv", "api",
]
JARGON_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in JARGON_WORDS) + r")\b",
    re.IGNORECASE,
)

# W003: PascalCase to words (e.g. GroupMembership -> group membership)
_PASCAL_SPLIT = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

# S003: known acronyms and emphasis words allowed in ALL CAPS.
# Includes: international standards bodies, domain abbreviations,
# measurement acronyms, and RFC-style emphasis words.
KNOWN_ACRONYMS = {
    # Standards and interop
    "ISO", "UN", "FHIR", "SEMIC", "DCI", "EBSI", "SKOS", "RDF",
    "HTTP", "HTTPS", "URI", "URL", "JWT", "VC", "RFC", "PDF", "MIME",
    # Organizations
    "UNHCR", "UNICEF", "WFP", "FAO", "OCHA", "WHO", "ILO", "IMF",
    "UNSD", "CDC", "NCHS",
    # Domain-specific
    "WG", "CFM", "PMT", "PPI", "DHS", "JMP",
    "ICD", "ICCS", "CIEC", "ISIC", "ISCO", "ISCED", "RRULE",
    "OASIS", "CAP", "COD", "FIPS", "CLDR",
    # Measurement and health
    "DNA", "RNA", "BMI", "MUAC", "HIV", "BAZ", "HAZ", "WAZ", "WHZ",
    "SMART", "CMAM",
    # Technology
    "WASH", "ICT", "SMS", "PDA", "GIS", "GPS", "GPC", "SSN", "TIC",
    # RFC-style emphasis (used in definitions for clarity)
    "NOT", "OPTIONAL", "MUST", "SHALL",
    # Other
    "SD",
}

ALL_CAPS_PATTERN = re.compile(r"\b([A-Z]{3,})\b")

EM_DASH = "\u2014"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pascal_to_words(name: str) -> str:
    """Convert PascalCase to lowercase words (e.g. GroupMembership -> group membership)."""
    return _PASCAL_SPLIT.sub(" ", name).lower()


def _is_valid_http_uri(uri: str) -> bool:
    """Check if a string looks like a well-formed HTTP(S) URI."""
    return bool(re.match(r"^https?://[^\s]+$", uri))


def _check_em_dash(text: str, filename: str, field: str, maturity: str, is_note: bool) -> list[LintIssue]:
    """Check a text field for em dashes. Returns issues if found."""
    if EM_DASH not in text:
        return []
    # Notes are always warnings regardless of maturity
    if is_note:
        severity = "warning"
    elif maturity in ("candidate", "normative"):
        severity = "error"
    else:
        severity = "warning"
    return [LintIssue(
        filename,
        f"Em dash (U+2014) found in {field}",
        rule="S001",
        severity=severity,
    )]


def _check_external_equivalents(data: dict, filename: str) -> list[LintIssue]:
    """Check external_equivalents entries for URI/match issues (E001-E003)."""
    issues = []
    ext = data.get("external_equivalents")
    if not ext or not isinstance(ext, dict):
        return issues

    for system, entry in ext.items():
        if not isinstance(entry, dict):
            continue
        match = entry.get("match")
        uri = entry.get("uri")

        # Skip gap documentation entries (match: none)
        if match == "none":
            continue

        # E001: malformed URI
        if uri and not _is_valid_http_uri(uri):
            issues.append(LintIssue(
                filename,
                f"external_equivalents.{system}.uri is not a valid HTTP(S) URI: {uri!r}",
                rule="E001",
            ))

        # E002: match present but no URI
        if match and not uri:
            issues.append(LintIssue(
                filename,
                f"external_equivalents.{system} has match={match!r} but no uri",
                rule="E002",
            ))

        # E003: URI present but no match
        if uri and not match:
            issues.append(LintIssue(
                filename,
                f"external_equivalents.{system} has uri but no match",
                rule="E003",
            ))

    return issues


# ---------------------------------------------------------------------------
# LinkML -> bespoke-shape adapter
#
# Reads dist/linkml/*.yaml and returns three dicts (concepts, properties,
# vocabularies) plus a categories dict, in the same shape the bespoke
# loader produces, so the lint rules below run unchanged. Only the fields
# the rules actually inspect are filled in.
# ---------------------------------------------------------------------------


def _linkml_definition(entry: dict) -> dict:
    """Reconstruct a multilingual definition dict from a LinkML class/slot/enum."""
    ann = entry.get("annotations") or {}
    definition: dict[str, str] = {}
    if entry.get("description"):
        definition["en"] = entry["description"]
    for src_key, locale in (("description_fr", "fr"), ("description_es", "es")):
        if ann.get(src_key):
            definition[locale] = ann[src_key]
    return definition


def _linkml_label(entry: dict) -> dict:
    """Reconstruct a multilingual label dict from a LinkML class/slot/enum."""
    ann = entry.get("annotations") or {}
    label: dict[str, str] = {}
    if entry.get("title"):
        label["en"] = entry["title"]
    for src_key, locale in (("label_fr", "fr"), ("label_es", "es")):
        if ann.get(src_key):
            label[locale] = ann[src_key]
    return label


def _linkml_external_equivalents(entry: dict) -> dict:
    """Decode the external_alignments_json annotation into a system->entry dict.

    The bespoke shape keys by system (a free-form short id). The LinkML
    annotation is a JSON array of alignment entries; we collapse them by
    ``vocabulary_id`` (falling back to ``vocabulary``) to preserve a stable
    key for the E001-E003 rule set. We only emit the fields the rules
    inspect (match, uri, note).
    """
    ann = entry.get("annotations") or {}
    raw = ann.get("external_alignments_json")
    if not raw:
        return {}
    try:
        alignments = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    out: dict[str, dict] = {}
    for item in alignments:
        if not isinstance(item, dict):
            continue
        key = item.get("vocabulary_id") or item.get("vocabulary") or item.get("uri")
        if not key:
            continue
        entry_out = {}
        if "match" in item:
            entry_out["match"] = item["match"]
        if "uri" in item:
            entry_out["uri"] = item["uri"]
        if "note" in item:
            entry_out["note"] = item["note"]
        out[key] = entry_out
    return out


def _linkml_decode_json_ann(entry: dict, key: str):
    """Return a parsed JSON value from an annotation, or None if absent/invalid."""
    ann = entry.get("annotations") or {}
    raw = ann.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _linkml_status_to_maturity(status: str | None) -> str:
    """Map LinkML ``status`` (bibo:status/...) back to PublicSchema maturity."""
    if not status:
        return "draft"
    s = status.replace("bibo:status/", "").replace("bibo:", "")
    if s in ("published", "normative"):
        return "normative"
    if s in ("forthcoming", "candidate"):
        return "candidate"
    return "draft"


def _load_linkml_schema_files(linkml_dir: Path) -> list[dict]:
    """Load every *.yaml under dist/linkml/, recursing one level for external/.

    Skips the top-level composite (``publicschema.yaml``) and the
    hand-authored ``publicschema-extensions.yaml`` because they only carry
    prefixes and imports.
    """
    skip = {"publicschema.yaml", "publicschema-extensions.yaml"}
    results: list[dict] = []
    for path in sorted(linkml_dir.rglob("*.yaml")):
        if path.name in skip:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        results.append(data)
    return results


def load_linkml_as_bespoke(linkml_dir: Path) -> tuple[dict, dict, dict, dict]:
    """Read dist/linkml/ and return (concepts, properties, vocabularies, categories).

    Each return dict maps a filename-ish key (the LinkML class/slot/enum
    name) to a dict shaped like the bespoke YAML the lint rules expect.
    ``categories`` is reconstructed from the ``categories.yaml`` module if
    present (LinkML emits each category as a class under that module).
    """
    concepts: dict[str, dict] = {}
    properties: dict[str, dict] = {}
    vocabularies: dict[str, dict] = {}
    categories: dict[str, dict] = {}

    for module in _load_linkml_schema_files(linkml_dir):
        module_name = module.get("name", "")
        is_categories_module = module_name == "categories"

        for cname, cdef in (module.get("classes") or {}).items():
            if not isinstance(cdef, dict):
                continue
            if is_categories_module:
                categories[cname] = {
                    "label": _linkml_label(cdef),
                    "definition": _linkml_definition(cdef),
                }
                continue
            entry = {
                "id": cname,
                "maturity": _linkml_status_to_maturity(cdef.get("status")),
                "definition": _linkml_definition(cdef),
                "label": _linkml_label(cdef),
                "external_equivalents": _linkml_external_equivalents(cdef),
                "abstract": bool(cdef.get("abstract")),
            }
            convergence = _linkml_decode_json_ann(cdef, "convergence_json")
            if convergence:
                entry["convergence"] = convergence
            property_groups = _linkml_decode_json_ann(cdef, "property_groups_json")
            if property_groups:
                entry["property_groups"] = property_groups
            concepts[cname] = entry

        for sname, sdef in (module.get("slots") or {}).items():
            if not isinstance(sdef, dict):
                continue
            properties[sname] = {
                "id": sname,
                "maturity": _linkml_status_to_maturity(sdef.get("status")),
                "definition": _linkml_definition(sdef),
                "label": _linkml_label(sdef),
                "external_equivalents": _linkml_external_equivalents(sdef),
            }

        for ename, edef in (module.get("enums") or {}).items():
            if not isinstance(edef, dict):
                continue
            sync_block = _linkml_decode_json_ann(edef, "sync_json")
            values: list[dict] = []
            for code, vdef in (edef.get("permissible_values") or {}).items():
                if not isinstance(vdef, dict):
                    values.append({"code": code})
                    continue
                values.append({
                    "code": code,
                    "label": _linkml_label(vdef),
                    "definition": _linkml_definition(vdef),
                })
            entry = {
                "id": ename,
                "maturity": _linkml_status_to_maturity(edef.get("status")),
                "definition": _linkml_definition(edef),
                "label": _linkml_label(edef),
                "external_equivalents": _linkml_external_equivalents(edef),
                "values": values,
            }
            if sync_block:
                entry["sync"] = sync_block
            vocabularies[ename] = entry

    return concepts, properties, vocabularies, categories


# ---------------------------------------------------------------------------
# Main linting function
# ---------------------------------------------------------------------------


def lint_schema_dir(schema_dir: Path) -> list[LintIssue]:
    """Lint all YAML source files for content quality and style.

    Returns a list of LintIssue objects. Empty list means clean.
    """
    # Load all files
    concepts = load_all_yaml(schema_dir / "concepts")
    properties = load_all_yaml(schema_dir / "properties")
    vocabularies = load_all_yaml(schema_dir / "vocabularies")

    # Load categories (optional)
    categories_path = schema_dir / "categories.yaml"
    categories = load_yaml(categories_path) if categories_path.exists() else {}

    return _lint_loaded(concepts, properties, vocabularies, categories)


def _lint_loaded(
    concepts: dict,
    properties: dict,
    vocabularies: dict,
    categories: dict,
) -> list[LintIssue]:
    """Run lint rules against already-loaded concept/property/vocabulary dicts.

    Shared between the bespoke and LinkML entry points so the rule set lives
    in one place. Both readers normalise to ``{filename_key: {id, maturity,
    definition, label, ...}}`` before calling here.
    """
    issues: list[LintIssue] = []

    # Collect all category references from concepts' property_groups
    used_categories: set[str] = set()

    # --- Lint concepts ---
    for filename, data in concepts.items():
        concept_id = data.get("id", filename)
        maturity = data.get("maturity", "draft")
        definition = data.get("definition", {})
        en_def = definition.get("en", "") if isinstance(definition, dict) else ""
        en_def_stripped = en_def.strip() if en_def else ""

        # W001: jargon
        if en_def_stripped and JARGON_PATTERN.search(en_def_stripped):
            match = JARGON_PATTERN.search(en_def_stripped)
            issues.append(LintIssue(
                filename,
                f"Definition contains developer jargon: {match.group()!r}",
                rule="W001",
            ))

        # W002: short definition (concepts: <8 words)
        if en_def_stripped and len(en_def_stripped.split()) < 8:
            issues.append(LintIssue(
                filename,
                f"Concept definition is very short ({len(en_def_stripped.split())} words)",
                rule="W002",
            ))

        # W003: circular definition
        if en_def_stripped and concept_id:
            name_words = _pascal_to_words(concept_id)
            pattern = rf"^(a|an|the)\s+{re.escape(name_words)}\s+(is|are)\b"
            if re.match(pattern, en_def_stripped, re.IGNORECASE):
                issues.append(LintIssue(
                    filename,
                    f"Definition appears circular (starts with '{concept_id}' name)",
                    rule="W003",
                ))

        # W004: terminal punctuation
        if en_def_stripped and en_def_stripped[-1] not in ".?)\"'":
            issues.append(LintIssue(
                filename,
                "English definition does not end with terminal punctuation",
                rule="W004",
            ))

        # S001: em dash in definitions
        if isinstance(definition, dict):
            for lang, text in definition.items():
                if text and EM_DASH in str(text):
                    issues.extend(_check_em_dash(
                        str(text), filename, f"definition.{lang}", maturity, is_note=False,
                    ))

        # S001: em dash in labels
        label = data.get("label", {})
        if isinstance(label, dict):
            for lang, text in label.items():
                if text and EM_DASH in str(text):
                    issues.extend(_check_em_dash(
                        str(text), filename, f"label.{lang}", maturity, is_note=False,
                    ))

        # S001: em dash in convergence notes (always warning)
        convergence = data.get("convergence", {})
        if isinstance(convergence, dict):
            notes = convergence.get("notes", "")
            if notes and EM_DASH in str(notes):
                issues.extend(_check_em_dash(
                    str(notes), filename, "convergence.notes", maturity, is_note=True,
                ))

        # S001: em dash in external_equivalents notes (always warning)
        ext = data.get("external_equivalents", {})
        if isinstance(ext, dict):
            for system, entry in ext.items():
                if isinstance(entry, dict):
                    note = entry.get("note", "")
                    if note and EM_DASH in str(note):
                        issues.extend(_check_em_dash(
                            str(note), filename,
                            f"external_equivalents.{system}.note",
                            maturity, is_note=True,
                        ))

        # S002: label ends with period
        if isinstance(label, dict):
            en_label = label.get("en", "")
            if en_label and str(en_label).strip().endswith("."):
                issues.append(LintIssue(
                    filename,
                    "English label ends with a period (labels are not sentences)",
                    rule="S002",
                ))

        # S003: unexplained ALL CAPS
        if en_def_stripped:
            for match in ALL_CAPS_PATTERN.finditer(en_def_stripped):
                word = match.group(1)
                if word not in KNOWN_ACRONYMS:
                    issues.append(LintIssue(
                        filename,
                        f"Unknown ALL CAPS word in definition: {word!r}",
                        rule="S003",
                    ))

        # E001-E003: external equivalents
        issues.extend(_check_external_equivalents(data, filename))

        # M001: candidate+ without external_equivalents
        if maturity in ("candidate", "normative") and not data.get("external_equivalents"):
            issues.append(LintIssue(
                filename,
                f"Concept at {maturity!r} maturity has no external_equivalents",
                rule="M001",
            ))

        # M002: normative without property_groups (exempt abstract)
        if maturity == "normative" and not data.get("abstract") and not data.get("property_groups"):
            issues.append(LintIssue(
                filename,
                "Normative concept has no property_groups",
                rule="M002",
            ))

        # M003: normative without convergence
        if maturity == "normative" and not data.get("convergence"):
            issues.append(LintIssue(
                filename,
                "Normative concept has no convergence data",
                rule="M003",
            ))

        # Collect used categories for X001
        for group in data.get("property_groups") or []:
            cat = group.get("category", "")
            if cat:
                used_categories.add(cat)

    # --- Lint properties ---
    for filename, data in properties.items():
        maturity = data.get("maturity", "draft")
        definition = data.get("definition", {})
        en_def = definition.get("en", "") if isinstance(definition, dict) else ""
        en_def_stripped = en_def.strip() if en_def else ""

        # W001: jargon
        if en_def_stripped and JARGON_PATTERN.search(en_def_stripped):
            match = JARGON_PATTERN.search(en_def_stripped)
            issues.append(LintIssue(
                filename,
                f"Definition contains developer jargon: {match.group()!r}",
                rule="W001",
            ))

        # W002: short definition (properties: <6 words)
        if en_def_stripped and len(en_def_stripped.split()) < 6:
            issues.append(LintIssue(
                filename,
                f"Property definition is very short ({len(en_def_stripped.split())} words)",
                rule="W002",
            ))

        # W004: terminal punctuation
        if en_def_stripped and en_def_stripped[-1] not in ".?)\"'":
            issues.append(LintIssue(
                filename,
                "English definition does not end with terminal punctuation",
                rule="W004",
            ))

        # S001: em dash in definitions
        if isinstance(definition, dict):
            for lang, text in definition.items():
                if text and EM_DASH in str(text):
                    issues.extend(_check_em_dash(
                        str(text), filename, f"definition.{lang}", maturity, is_note=False,
                    ))

        # S003: unexplained ALL CAPS
        if en_def_stripped:
            for caps_match in ALL_CAPS_PATTERN.finditer(en_def_stripped):
                word = caps_match.group(1)
                if word not in KNOWN_ACRONYMS:
                    issues.append(LintIssue(
                        filename,
                        f"Unknown ALL CAPS word in definition: {word!r}",
                        rule="S003",
                    ))

        # E001-E003: external equivalents
        issues.extend(_check_external_equivalents(data, filename))

    # --- Lint vocabularies ---
    for filename, data in vocabularies.items():
        maturity = data.get("maturity", "draft")
        definition = data.get("definition", {})
        en_def = definition.get("en", "") if isinstance(definition, dict) else ""
        en_def_stripped = en_def.strip() if en_def else ""

        # W001: jargon
        if en_def_stripped and JARGON_PATTERN.search(en_def_stripped):
            match = JARGON_PATTERN.search(en_def_stripped)
            issues.append(LintIssue(
                filename,
                f"Definition contains developer jargon: {match.group()!r}",
                rule="W001",
            ))

        # W002: short definition (vocabularies: <6 words)
        if en_def_stripped and len(en_def_stripped.split()) < 6:
            issues.append(LintIssue(
                filename,
                f"Vocabulary definition is very short ({len(en_def_stripped.split())} words)",
                rule="W002",
            ))

        # W004: terminal punctuation
        if en_def_stripped and en_def_stripped[-1] not in ".?)\"'":
            issues.append(LintIssue(
                filename,
                "English definition does not end with terminal punctuation",
                rule="W004",
            ))

        # S001: em dash in definitions
        if isinstance(definition, dict):
            for lang, text in definition.items():
                if text and EM_DASH in str(text):
                    issues.extend(_check_em_dash(
                        str(text), filename, f"definition.{lang}", maturity, is_note=False,
                    ))

        # V001: single-value vocabulary
        values = data.get("values", [])
        if len(values) == 1:
            issues.append(LintIssue(
                filename,
                "Vocabulary has only 1 value (possibly incomplete)",
                rule="V001",
            ))

        # V002: large unsynced vocabulary
        if len(values) > 50 and not data.get("sync"):
            issues.append(LintIssue(
                filename,
                f"Vocabulary has {len(values)} values but no sync block",
                rule="V002",
            ))

        # E001-E003: external equivalents
        issues.extend(_check_external_equivalents(data, filename))

    # --- Cross-file checks ---

    # X001: unused categories
    if categories:
        for cat_id in categories:
            if cat_id not in used_categories:
                issues.append(LintIssue(
                    "categories.yaml",
                    f"Category {cat_id!r} is defined but never used by any concept's property_groups",
                    rule="X001",
                ))

    return issues


def lint_linkml_dir(linkml_dir: Path) -> list[LintIssue]:
    """Lint a dist/linkml/ tree by reusing :func:`_lint_loaded` after
    normalising LinkML output back to bespoke shape.
    """
    concepts, properties, vocabularies, categories = load_linkml_as_bespoke(linkml_dir)
    return _lint_loaded(concepts, properties, vocabularies, categories)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    """CLI entry point for the linter."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lint PublicSchema YAML for content quality and style.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Schema directory. Defaults to schema/ (bespoke) or dist/linkml/ (linkml).",
    )
    parser.add_argument(
        "--source",
        choices=("bespoke", "linkml"),
        default="bespoke",
        help="Which source tree to lint. During the LinkML cutover the default "
             "stays 'bespoke'; 'linkml' lints dist/linkml/ output instead.",
    )
    args = parser.parse_args()

    if args.path:
        target = Path(args.path)
    elif args.source == "linkml":
        target = Path("dist/linkml")
    else:
        target = Path("schema")

    if args.source == "linkml":
        issues = lint_linkml_dir(target)
    else:
        issues = lint_schema_dir(target)
    warnings = [i for i in issues if i.severity == "warning"]
    errors = [i for i in issues if i.severity == "error"]

    if warnings:
        print(f"\n{len(warnings)} warning(s):", file=sys.stderr)
        for w in warnings:
            print(f"  {w}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    elif warnings:
        print(f"\nLint completed with {len(warnings)} warning(s), 0 errors.")
        sys.exit(0)
    else:
        print("Lint passed (no issues).")
        sys.exit(0)


if __name__ == "__main__":
    main()
