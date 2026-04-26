"""Tests for the system_matchings projection.

`build_system_matchings(external_dir)` reads each
`external/<system>/matching.yaml` and returns a dict keyed by system id,
projected to the slim shape the site consumes:
  - top-level metadata (system, system_version, source_repository,
    source_branch, fhir_repository, fhir_branch, last_reviewed)
  - concept_matches: list (passthrough)
  - no_match: list (only entries with v2_* refs; external_excess is
    PublicSchema's coverage backlog, not a system page concern)
"""

from pathlib import Path

import pytest
import yaml

from build.system_matchings import build_system_matchings


@pytest.fixture
def tmp_external(tmp_path):
    ext = tmp_path / "external"
    ext.mkdir()
    return ext


def write_matching(ext_dir: Path, system: str, data: dict) -> Path:
    sys_dir = ext_dir / system
    sys_dir.mkdir(parents=True, exist_ok=True)
    path = sys_dir / "matching.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
    return path


def base(system: str = "demo") -> dict:
    return {
        "system": system,
        "concept_matches": [],
        "matches": [],
        "no_match": [],
        "external_excess": [],
    }


# ---------------------------------------------------------------------------
# Projection shape
# ---------------------------------------------------------------------------

class TestProjection:
    def test_empty_dir_returns_empty_dict(self, tmp_external):
        assert build_system_matchings(tmp_external) == {}

    def test_missing_dir_returns_empty_dict(self, tmp_path):
        assert build_system_matchings(tmp_path / "missing") == {}

    def test_single_system_keyed_by_id(self, tmp_external):
        write_matching(tmp_external, "demo", base("demo"))
        out = build_system_matchings(tmp_external)
        assert set(out.keys()) == {"demo"}
        assert out["demo"]["system"] == "demo"

    def test_concept_matches_passthrough(self, tmp_external):
        data = base("demo")
        data["concept_matches"] = [{
            "v2_concept": "Person",
            "external_entity": "Individual",
            "match": "exact",
            "notes": "1:1 mapping",
        }]
        write_matching(tmp_external, "demo", data)
        out = build_system_matchings(tmp_external)
        assert out["demo"]["concept_matches"] == data["concept_matches"]

    def test_no_match_passthrough(self, tmp_external):
        data = base("demo")
        data["no_match"] = [
            {"v2_concept": "Group", "reason": "not modeled"},
            {"v2_property": "iban", "reason": "no payment fields"},
        ]
        write_matching(tmp_external, "demo", data)
        out = build_system_matchings(tmp_external)
        assert out["demo"]["no_match"] == data["no_match"]

    def test_metadata_preserved(self, tmp_external):
        data = base("demo")
        data["system_version"] = "1.2.3"
        data["source_repository"] = "https://example.org/repo"
        data["source_branch"] = "main"
        data["last_reviewed"] = "2026-04-01"
        write_matching(tmp_external, "demo", data)
        out = build_system_matchings(tmp_external)
        d = out["demo"]
        assert d["system_version"] == "1.2.3"
        assert d["source_repository"] == "https://example.org/repo"
        assert d["source_branch"] == "main"
        assert d["last_reviewed"] == "2026-04-01"

    def test_external_excess_excluded(self, tmp_external):
        """external_excess is PublicSchema coverage backlog; site never sees it."""
        data = base("demo")
        data["external_excess"] = [
            {"external_field": "tenant_id", "reason": "out of scope"},
        ]
        write_matching(tmp_external, "demo", data)
        out = build_system_matchings(tmp_external)
        assert "external_excess" not in out["demo"]

    def test_matches_excluded_from_mvp(self, tmp_external):
        """Property-level matches table is not part of the MVP system page surface."""
        data = base("demo")
        data["matches"] = [
            {"v2_property": "given_name", "external_field": "firstName"},
        ]
        write_matching(tmp_external, "demo", data)
        out = build_system_matchings(tmp_external)
        assert "matches" not in out["demo"]


# ---------------------------------------------------------------------------
# Real repo smoke test
# ---------------------------------------------------------------------------

class TestRepo:
    def test_matching_system_ids_are_in_systemRegistry(self):
        """Per matching.schema.json, every YAML 'system' field must be a key
        in site/src/data/systems.ts systemRegistry; otherwise the system page
        cannot render meta (display name, URL, description)."""
        import re
        repo_root = Path(__file__).parent.parent
        registry_src = (repo_root / "site/src/data/systems.ts").read_text()
        # Match top-level entries inside `export const systemRegistry = { ... }`.
        # Each entry starts with `<id>: {` at indent level 2.
        registry_ids = set(re.findall(
            r"^\s{2}([a-z][a-z0-9_]*):\s*\{",
            registry_src,
            re.MULTILINE,
        ))
        out = build_system_matchings(repo_root / "external")
        unknown = sorted(set(out) - registry_ids)
        assert unknown == [], (
            f"matching.yaml uses system IDs not in systemRegistry: {unknown}. "
            f"Registry has: {sorted(registry_ids)}"
        )

    def test_repo_external_produces_six_systems(self):
        repo_external = Path(__file__).parent.parent / "external"
        out = build_system_matchings(repo_external)
        # All six committed systems should be present.
        # Keys come from the YAML 'system' field (snake_case),
        # not directory names (which use hyphens for some systems).
        for sys_id in ("dhis2", "govstack_payments", "ocha_cod_ab",
                       "opencrvs", "openimis", "openspp"):
            assert sys_id in out, f"missing {sys_id} in projection: {sorted(out)}"
            entry = out[sys_id]
            assert isinstance(entry["concept_matches"], list)
            assert isinstance(entry["no_match"], list)
