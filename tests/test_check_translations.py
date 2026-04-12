"""Tests for build.check_translations."""

import subprocess
import textwrap
from pathlib import Path

import pytest

from build import check_translations as ct


# ---------------------------------------------------------------------------
# UI dictionary parsing
# ---------------------------------------------------------------------------


class TestExtractUiKeys:
    def test_extracts_keys_from_top_level_en(self):
        src = textwrap.dedent(
            """\
            const en = {
              'nav.concepts': 'Concepts',
              'nav.docs': 'Docs',
            };

            export const ui: Record<Locale, Partial<Dict>> = {
              en,
              fr: {
                'nav.concepts': 'Concepts',
                'nav.docs': 'Documentation',
              },
              es: {
                'nav.concepts': 'Conceptos',
                'nav.docs': 'Documentación',
              },
            };
            """
        )
        keys = ct._extract_ui_keys(src)
        assert keys["en"] == {"nav.concepts", "nav.docs"}
        assert keys["fr"] == {"nav.concepts", "nav.docs"}
        assert keys["es"] == {"nav.concepts", "nav.docs"}

    def test_detects_missing_keys(self, tmp_path: Path):
        src = textwrap.dedent(
            """\
            const en = {
              'a.b': 'A',
              'c.d': 'C',
            };
            export const ui = {
              en,
              fr: {
                'a.b': 'Ax',
              },
              es: {
                'a.b': 'As',
                'c.d': 'Cs',
              },
            };
            """
        )
        ui_file = tmp_path / "ui.ts"
        ui_file.write_text(src)
        report = ct.check_ui_dictionary(ui_file)
        assert not report.ok
        assert any("fr is missing" in e and "c.d" in e for e in report.errors)
        # es is complete, so no error for it
        assert not any("es is missing" in e for e in report.errors)

    def test_warns_on_extra_keys(self, tmp_path: Path):
        src = textwrap.dedent(
            """\
            const en = {
              'a.b': 'A',
            };
            export const ui = {
              en,
              fr: {
                'a.b': 'A',
                'z.old': 'Z',
              },
              es: {
                'a.b': 'As',
              },
            };
            """
        )
        ui_file = tmp_path / "ui.ts"
        ui_file.write_text(src)
        report = ct.check_ui_dictionary(ui_file)
        assert any("not present in en" in w and "z.old" in w for w in report.warnings)

    def test_errors_when_ui_file_missing(self, tmp_path: Path):
        report = ct.check_ui_dictionary(tmp_path / "missing.ts")
        assert not report.ok
        assert "not found" in report.errors[0]


# ---------------------------------------------------------------------------
# Schema definition completeness
# ---------------------------------------------------------------------------


class TestCheckSchema:
    def test_requires_fr_es_for_trial_use_concept(self, tmp_path: Path):
        (tmp_path / "concepts").mkdir()
        path = tmp_path / "concepts" / "person.yaml"
        path.write_text(textwrap.dedent(
            """\
            id: Person
            maturity: trial-use
            definition:
              en: A person.
            """
        ))
        report = ct.check_schema(tmp_path)
        assert not report.ok
        assert any("definition.fr" in e for e in report.errors)
        assert any("definition.es" in e for e in report.errors)

    def test_skips_draft_entries(self, tmp_path: Path):
        (tmp_path / "concepts").mkdir()
        path = tmp_path / "concepts" / "new.yaml"
        path.write_text(textwrap.dedent(
            """\
            id: New
            maturity: draft
            definition:
              en: A draft concept.
            """
        ))
        report = ct.check_schema(tmp_path)
        assert report.ok

    def test_accepts_trial_use_with_translations(self, tmp_path: Path):
        (tmp_path / "properties").mkdir()
        path = tmp_path / "properties" / "name.yaml"
        path.write_text(textwrap.dedent(
            """\
            id: name
            maturity: trial-use
            definition:
              en: A name.
              fr: Un nom.
              es: Un nombre.
            """
        ))
        report = ct.check_schema(tmp_path)
        assert report.ok

    def test_rejects_empty_string_translation(self, tmp_path: Path):
        (tmp_path / "vocabularies").mkdir()
        path = tmp_path / "vocabularies" / "sex.yaml"
        path.write_text(textwrap.dedent(
            """\
            id: sex
            maturity: stable
            definition:
              en: Sex.
              fr: ""
              es: Sexo.
            """
        ))
        report = ct.check_schema(tmp_path)
        assert not report.ok
        assert any("definition.fr" in e for e in report.errors)


# ---------------------------------------------------------------------------
# File-timestamp staleness
# ---------------------------------------------------------------------------


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=root, check=True)


def _git_commit(root: Path, message: str, env: dict | None = None) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", message],
        cwd=root,
        check=True,
        env={**subprocess.os.environ, **(env or {})},
    )


class TestCheckDocs:
    def test_flags_translation_older_than_source(self, tmp_path: Path, monkeypatch):
        docs = tmp_path / "docs"
        (docs / "fr").mkdir(parents=True)
        (docs / "es").mkdir()
        (docs / "foo.md").write_text("# Foo\n")
        (docs / "fr" / "foo.md").write_text("# Foo FR\n")
        (docs / "es" / "foo.md").write_text("# Foo ES\n")

        _init_git_repo(tmp_path)
        _git_commit(tmp_path, "initial translations", {"GIT_COMMITTER_DATE": "2025-01-01T00:00:00", "GIT_AUTHOR_DATE": "2025-01-01T00:00:00"})

        # Update only the EN source with a later timestamp.
        (docs / "foo.md").write_text("# Foo updated\n")
        _git_commit(tmp_path, "update en only", {"GIT_COMMITTER_DATE": "2026-01-01T00:00:00", "GIT_AUTHOR_DATE": "2026-01-01T00:00:00"})

        manifest = tmp_path / "docs-manifest.ts"
        manifest.write_text('file: "foo.md",')
        monkeypatch.chdir(tmp_path)
        report = ct.check_docs(Path("docs"), manifest)
        assert any("older than" in w and "fr/foo.md" in w for w in report.warnings)
        assert any("older than" in w and "es/foo.md" in w for w in report.warnings)

    def test_reports_missing_translation(self, tmp_path: Path, monkeypatch):
        docs = tmp_path / "docs"
        (docs / "fr").mkdir(parents=True)
        (docs / "es").mkdir()
        (docs / "foo.md").write_text("# Foo\n")
        (docs / "fr" / "foo.md").write_text("# Foo FR\n")
        # es translation missing

        _init_git_repo(tmp_path)
        _git_commit(tmp_path, "partial")

        manifest = tmp_path / "docs-manifest.ts"
        manifest.write_text('file: "foo.md",')
        monkeypatch.chdir(tmp_path)
        report = ct.check_docs(Path("docs"), manifest)
        assert any("not yet translated to es" in w for w in report.warnings)

    def test_fresh_translations_pass(self, tmp_path: Path, monkeypatch):
        docs = tmp_path / "docs"
        (docs / "fr").mkdir(parents=True)
        (docs / "es").mkdir()
        (docs / "foo.md").write_text("# Foo\n")
        (docs / "fr" / "foo.md").write_text("# Foo FR\n")
        (docs / "es" / "foo.md").write_text("# Foo ES\n")

        _init_git_repo(tmp_path)
        _git_commit(tmp_path, "all fresh")

        manifest = tmp_path / "docs-manifest.ts"
        manifest.write_text('file: "foo.md",')
        monkeypatch.chdir(tmp_path)
        report = ct.check_docs(Path("docs"), manifest)
        # Same commit = same timestamp; no staleness warnings.
        assert not any("older than" in w for w in report.warnings)


# ---------------------------------------------------------------------------
# End-to-end against the real repo
# ---------------------------------------------------------------------------


class TestRunAllOnRepo:
    def test_ui_dictionary_is_complete(self):
        # The real repo's ui.ts must pass the UI check; the CI relies on it.
        report = ct.check_ui_dictionary()
        assert report.ok, "UI dictionary has missing keys: " + "; ".join(report.errors)

    def test_schema_definitions_complete_for_trial_use(self):
        report = ct.check_schema()
        assert report.ok, (
            "Schema definitions incomplete:\n"
            + "\n".join(report.errors[:20])
        )
