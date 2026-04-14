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
"""

import re
import sys
from pathlib import Path

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
# Main linting function
# ---------------------------------------------------------------------------


def lint_schema_dir(schema_dir: Path) -> list[LintIssue]:
    """Lint all YAML source files for content quality and style.

    Returns a list of LintIssue objects. Empty list means clean.
    """
    issues: list[LintIssue] = []

    # Load all files
    concepts = load_all_yaml(schema_dir / "concepts")
    properties = load_all_yaml(schema_dir / "properties")
    vocabularies = load_all_yaml(schema_dir / "vocabularies")

    # Load categories (optional)
    categories_path = schema_dir / "categories.yaml"
    categories = load_yaml(categories_path) if categories_path.exists() else {}

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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    """CLI entry point for the linter."""
    schema_dir = Path("schema")
    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])

    issues = lint_schema_dir(schema_dir)
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
