"""Detect missing or stale translations across the codebase.

Runs four independent checks, each emitting warnings and/or errors:

1. **UI dictionary:** every key defined in the English block of
   ``site/src/i18n/ui.ts`` must also appear in ``fr`` and ``es``.
   A missing key is an error because the fallback path ships English
   copy on a non-English page.
2. **Docs:** for each Markdown file under ``docs/``, compare the git
   commit timestamp of the English original to the French and Spanish
   translations. A translation older than the English source is a
   staleness warning; a missing translated file is a "not yet
   translated" warning.
3. **Prose components:** same timestamp comparison for
   ``site/src/components/pages/content/*Content.{en,fr,es}.astro``.
4. **Schema definitions:** every trial-use or stable concept, property,
   and vocabulary YAML must carry a non-empty ``definition`` entry in
   ``fr`` and ``es``. Draft entries are skipped.

The script exits non-zero when any error surfaces; warnings are
informational only. Staleness is derived from git commit timestamps, so
rebasing a commit without touching content can produce a false positive.
This is acceptable for a warning-only signal and documented here.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


UI_TS_PATH = Path("site/src/i18n/ui.ts")
DOCS_DIR = Path("docs")
DOCS_MANIFEST_PATH = Path("site/src/data/docs.ts")
PROSE_DIR = Path("site/src/components/pages/content")
SCHEMA_DIR = Path("schema")
LOCALES: tuple[str, ...] = ("fr", "es")
MATURITY_REQUIRES_TRANSLATION: tuple[str, ...] = ("trial-use", "stable")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def merge(self, other: "Report") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# UI dictionary check
# ---------------------------------------------------------------------------


# Match the start of a locale block inside ui.ts, e.g. ``  fr: {``
_BLOCK_START_RE = re.compile(r"^\s*(en|fr|es):\s*\{", re.MULTILINE)
# Match quoted keys at the beginning of a line inside a block, e.g.
#   'nav.concepts': 'Concepts',
_KEY_RE = re.compile(r"^\s*'([^']+)':", re.MULTILINE)


def _extract_ui_keys(ui_ts: str) -> dict[str, set[str]]:
    """Return {locale: set_of_keys} parsed from ui.ts.

    Keys are detected by regex rather than a full TS parser, which keeps
    the check dependency-free. The shape of ui.ts (one key per line,
    single quotes, locales as nested object literals) is enforced by
    convention.
    """
    keys: dict[str, set[str]] = {"en": set(), "fr": set(), "es": set()}

    # Find each locale block and collect keys until the matching brace.
    matches = list(_BLOCK_START_RE.finditer(ui_ts))
    for idx, match in enumerate(matches):
        locale = match.group(1)
        block_start = match.end()
        block_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(ui_ts)
        block = ui_ts[block_start:block_end]
        # Stop at the closing brace of this block, so we don't pick up
        # keys from the next sibling block if the regex happens to miss.
        brace = block.find("};")
        if brace != -1:
            block = block[:brace]
        for km in _KEY_RE.finditer(block):
            keys[locale].add(km.group(1))

    # The top-level `const en = {` block is preceded by `const`, not a
    # locale-prefixed object key; handle it explicitly.
    top_en = re.search(r"const\s+en\s*=\s*\{", ui_ts)
    if top_en:
        block_end = ui_ts.find("\n};", top_en.end())
        block = ui_ts[top_en.end():block_end if block_end != -1 else len(ui_ts)]
        for km in _KEY_RE.finditer(block):
            keys["en"].add(km.group(1))

    return keys


def check_ui_dictionary(ui_ts_path: Path = UI_TS_PATH) -> Report:
    report = Report()
    if not ui_ts_path.exists():
        report.error(f"UI dictionary not found: {ui_ts_path}")
        return report

    keys = _extract_ui_keys(ui_ts_path.read_text(encoding="utf-8"))
    en_keys = keys["en"]
    if not en_keys:
        report.error(f"No keys parsed from {ui_ts_path}; parser may be out of date.")
        return report

    for locale in LOCALES:
        missing = sorted(en_keys - keys[locale])
        extra = sorted(keys[locale] - en_keys)
        if missing:
            report.error(
                f"UI dictionary: {locale} is missing {len(missing)} key(s): "
                + ", ".join(missing)
            )
        if extra:
            report.warn(
                f"UI dictionary: {locale} has {len(extra)} key(s) not present in en: "
                + ", ".join(extra)
            )
    return report


# ---------------------------------------------------------------------------
# File-timestamp check (docs and prose components)
# ---------------------------------------------------------------------------


def _git_last_commit_ts(path: Path) -> int | None:
    """Return the Unix timestamp of the last commit that touched `path`.

    Returns None if the path is untracked or git is unavailable. Callers
    must treat None as "cannot compare".
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    if not out:
        return None
    try:
        return int(out)
    except ValueError:
        return None


def _check_paired_files(
    source: Path,
    translations: dict[str, Path],
    label: str,
    report: Report,
) -> None:
    """Compare one English source to its translated siblings.

    `translations` maps locale -> path. A missing translated file is a
    "not yet translated" warning; an older translated file is a
    staleness warning.
    """
    source_ts = _git_last_commit_ts(source)
    for locale, translated in translations.items():
        if not translated.exists():
            report.warn(f"{label}: {source} is not yet translated to {locale} ({translated} missing)")
            continue
        translated_ts = _git_last_commit_ts(translated)
        if source_ts is None or translated_ts is None:
            continue
        if source_ts > translated_ts:
            report.warn(
                f"{label}: {translated} is older than {source} "
                f"(source: {source_ts}, translation: {translated_ts})"
            )


_DOC_FILE_RE = re.compile(r'''file:\s*["']([^"']+)["']''')


def _published_doc_files(manifest_path: Path) -> list[str]:
    """Read docs.ts and return the list of Markdown filenames it exposes.

    Research and working notes live alongside published docs in the same
    directory but are only translated on demand, so the staleness check
    scopes itself to whatever docs.ts lists.
    """
    if not manifest_path.exists():
        return []
    return _DOC_FILE_RE.findall(manifest_path.read_text(encoding="utf-8"))


def check_docs(
    docs_dir: Path = DOCS_DIR,
    manifest_path: Path = DOCS_MANIFEST_PATH,
) -> Report:
    report = Report()
    if not docs_dir.exists():
        return report
    published = _published_doc_files(manifest_path)
    if not published:
        report.warn(
            f"Docs manifest {manifest_path} is empty or unreadable; "
            "skipping doc staleness check."
        )
        return report
    for filename in sorted(published):
        source = docs_dir / filename
        if not source.exists():
            report.error(f"Docs: manifest lists {filename} but source is missing")
            continue
        translations = {loc: docs_dir / loc / filename for loc in LOCALES}
        _check_paired_files(source, translations, "Docs", report)
    return report


def check_prose_components(prose_dir: Path = PROSE_DIR) -> Report:
    report = Report()
    if not prose_dir.exists():
        return report
    for source in sorted(prose_dir.glob("*.en.astro")):
        stem = source.name[: -len(".en.astro")]
        translations = {loc: prose_dir / f"{stem}.{loc}.astro" for loc in LOCALES}
        _check_paired_files(source, translations, "Prose", report)
    return report


# ---------------------------------------------------------------------------
# Schema completeness check
# ---------------------------------------------------------------------------


def _check_definition(
    data: dict,
    path: Path,
    report: Report,
) -> None:
    """Validate that a concept/property/vocab YAML has FR/ES definitions.

    Only entries whose maturity triggers translation requirements are
    flagged. Drafts may leave translations blank during development.
    """
    maturity = data.get("maturity", "draft")
    if maturity not in MATURITY_REQUIRES_TRANSLATION:
        return
    definition = data.get("definition") or {}
    entity_id = data.get("id", path.stem)
    for locale in LOCALES:
        value = definition.get(locale)
        if not value or not str(value).strip():
            report.error(
                f"Schema: {path} ({entity_id}, {maturity}) is missing "
                f"definition.{locale}"
            )


def _iter_yaml_files(schema_dir: Path, subdir: str) -> Iterable[Path]:
    target = schema_dir / subdir
    if not target.exists():
        return []
    return sorted(target.rglob("*.yaml"))


def check_schema(schema_dir: Path = SCHEMA_DIR) -> Report:
    report = Report()
    for subdir in ("concepts", "properties", "vocabularies"):
        for path in _iter_yaml_files(schema_dir, subdir):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as e:
                report.error(f"Schema: failed to parse {path}: {e}")
                continue
            _check_definition(data, path, report)
    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_all() -> Report:
    combined = Report()
    combined.merge(check_ui_dictionary())
    combined.merge(check_schema())
    combined.merge(check_docs())
    combined.merge(check_prose_components())
    return combined


def main() -> int:
    report = run_all()
    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"ERROR {error}", file=sys.stderr)
    summary = f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)"
    if report.ok:
        print(f"OK    Translation check passed ({summary}).")
        return 0
    print(f"FAIL  Translation check failed: {summary}.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
