"""Tests for external matching.yaml validation.

Each external/<system>/matching.yaml must conform to
build/schemas/matching.schema.json. The validator returns a list of
ValidationError objects (empty means valid) so failures are surfaced the
same way as the rest of the build pipeline.
"""

from pathlib import Path

import pytest
import yaml

from build.validate_matchings import validate_matchings_dir


@pytest.fixture
def tmp_external(tmp_path):
    """Create an empty external/ tree to populate per test."""
    ext = tmp_path / "external"
    ext.mkdir()
    return ext


def write_matching(ext_dir: Path, system: str, data: dict) -> Path:
    sys_dir = ext_dir / system
    sys_dir.mkdir(parents=True, exist_ok=True)
    path = sys_dir / "matching.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
    return path


def minimal_matching(system: str = "test_system") -> dict:
    return {
        "system": system,
        "concept_matches": [],
        "matches": [],
        "no_match": [],
        "external_excess": [],
    }


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

class TestValidMatchings:
    def test_empty_external_dir_passes(self, tmp_external):
        assert validate_matchings_dir(tmp_external) == []

    def test_minimal_matching_passes(self, tmp_external):
        write_matching(tmp_external, "demo", minimal_matching("demo"))
        assert validate_matchings_dir(tmp_external) == []

    def test_concept_match_passes(self, tmp_external):
        data = minimal_matching("demo")
        data["concept_matches"] = [{
            "v2_concept": "Person",
            "external_entity": "Individual",
            "match": "exact",
        }]
        write_matching(tmp_external, "demo", data)
        assert validate_matchings_dir(tmp_external) == []

    def test_match_with_v2_property_passes(self, tmp_external):
        data = minimal_matching("demo")
        data["matches"] = [{
            "v2_property": "given_name",
            "external_field": "firstName",
        }]
        write_matching(tmp_external, "demo", data)
        assert validate_matchings_dir(tmp_external) == []

    def test_no_match_with_v2_concept_passes(self, tmp_external):
        data = minimal_matching("demo")
        data["no_match"] = [{
            "v2_concept": "Group",
            "reason": "Not modeled in this system.",
        }]
        write_matching(tmp_external, "demo", data)
        assert validate_matchings_dir(tmp_external) == []

    def test_external_excess_passes(self, tmp_external):
        data = minimal_matching("demo")
        data["external_excess"] = [{
            "external_field": "tenant_id",
            "reason": "Multi-tenancy is out of PublicSchema scope.",
        }]
        write_matching(tmp_external, "demo", data)
        assert validate_matchings_dir(tmp_external) == []

    def test_repo_matchings_pass(self):
        """All committed external/<system>/matching.yaml files validate."""
        repo_external = Path(__file__).parent.parent / "external"
        errors = validate_matchings_dir(repo_external)
        assert errors == [], "\n".join(str(e) for e in errors)


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

class TestInvalidMatchings:
    def test_missing_required_section_fails(self, tmp_external):
        data = minimal_matching("demo")
        del data["matches"]
        write_matching(tmp_external, "demo", data)
        errors = validate_matchings_dir(tmp_external)
        assert any("matches" in str(e) for e in errors)

    def test_invalid_match_level_fails(self, tmp_external):
        data = minimal_matching("demo")
        data["concept_matches"] = [{
            "v2_concept": "Person",
            "external_entity": "Individual",
            "match": "perfect",  # not in the enum
        }]
        write_matching(tmp_external, "demo", data)
        errors = validate_matchings_dir(tmp_external)
        assert errors
        assert any("perfect" in str(e) or "enum" in str(e) for e in errors)

    def test_no_match_without_v2_ref_fails(self, tmp_external):
        data = minimal_matching("demo")
        data["no_match"] = [{
            "external_field": "tenant_id",  # belongs in external_excess
            "reason": "wrong section",
        }]
        write_matching(tmp_external, "demo", data)
        errors = validate_matchings_dir(tmp_external)
        assert errors

    def test_external_excess_without_external_ref_fails(self, tmp_external):
        data = minimal_matching("demo")
        data["external_excess"] = [{
            "v2_concept": "Person",  # belongs in no_match
            "reason": "wrong section",
        }]
        write_matching(tmp_external, "demo", data)
        errors = validate_matchings_dir(tmp_external)
        assert errors

    def test_invalid_system_id_fails(self, tmp_external):
        data = minimal_matching("Bad-Name")  # uppercase + hyphen, snake_case required
        write_matching(tmp_external, "Bad-Name", data)
        errors = validate_matchings_dir(tmp_external)
        assert errors

    def test_unknown_top_level_key_fails(self, tmp_external):
        data = minimal_matching("demo")
        data["bogus_section"] = []
        write_matching(tmp_external, "demo", data)
        errors = validate_matchings_dir(tmp_external)
        assert errors
