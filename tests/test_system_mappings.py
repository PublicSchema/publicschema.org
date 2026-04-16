"""Tests for enriched system_mappings format.

Validates that all vocabulary YAML files with system_mappings use the
structured format (code + label + maps_to) and that mappings are
consistent with the vocabulary's canonical values.
"""


import pytest
import yaml

from build.build import build_vocabulary
from tests.conftest import SCHEMA_DIR

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_result():
    return build_vocabulary(SCHEMA_DIR)


@pytest.fixture(scope="module")
def all_vocabs():
    """Load all vocabulary YAML files that have system_mappings."""
    vocabs_dir = SCHEMA_DIR / "vocabularies"
    result = {}
    for path in sorted(vocabs_dir.rglob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data.get("system_mappings"):
            result[data["id"]] = data
    return result


# ---------------------------------------------------------------------------
# Format validation: every system_mappings entry uses enriched format
# ---------------------------------------------------------------------------

class TestEnrichedFormat:
    """All system_mappings must use the enriched format."""

    def test_all_mappings_have_values_list(self, all_vocabs):
        """Each system mapping must have a 'values' list, not a flat dict."""
        flat_mappings = []
        for vocab_id, data in all_vocabs.items():
            for sys_id, mapping in data["system_mappings"].items():
                if not isinstance(mapping, dict) or "values" not in mapping:
                    flat_mappings.append(f"{vocab_id}/{sys_id}")
        assert flat_mappings == [], (
            f"These system mappings still use flat format: {flat_mappings}"
        )

    def test_values_have_required_fields(self, all_vocabs):
        """Each value entry must have code, label, and maps_to."""
        missing = []
        for vocab_id, data in all_vocabs.items():
            for sys_id, mapping in data["system_mappings"].items():
                for i, v in enumerate(mapping.get("values", [])):
                    for field in ["code", "label", "maps_to"]:
                        if field not in v:
                            missing.append(f"{vocab_id}/{sys_id}[{i}] missing '{field}'")
        assert missing == [], (
            "Values missing required fields:\n" + "\n".join(missing)
        )

    def test_maps_to_is_string_or_null(self, all_vocabs):
        """maps_to must be a string (canonical code) or null."""
        bad = []
        for vocab_id, data in all_vocabs.items():
            for sys_id, mapping in data["system_mappings"].items():
                for v in mapping.get("values", []):
                    mt = v.get("maps_to")
                    if mt is not None and not isinstance(mt, str):
                        bad.append(f"{vocab_id}/{sys_id}: maps_to={mt!r} (type {type(mt).__name__})")
        assert bad == [], "Invalid maps_to types:\n" + "\n".join(bad)

    def test_labels_not_empty(self, all_vocabs):
        """Labels should not be empty strings."""
        empty = []
        for vocab_id, data in all_vocabs.items():
            for sys_id, mapping in data["system_mappings"].items():
                for v in mapping.get("values", []):
                    if not str(v.get("label", "")).strip():
                        empty.append(f"{vocab_id}/{sys_id}: code={v['code']} has empty label")
        assert empty == [], "Empty labels:\n" + "\n".join(empty)


# ---------------------------------------------------------------------------
# Referential integrity: maps_to targets exist as canonical codes
# ---------------------------------------------------------------------------

class TestMappingIntegrity:
    """maps_to values must reference valid canonical codes."""

    def test_maps_to_references_canonical_codes(self, all_vocabs):
        """Every non-null maps_to must be a code in the vocabulary's values list."""
        bad = []
        for vocab_id, data in all_vocabs.items():
            canonical_codes = {v["code"] for v in data.get("values", [])}
            for sys_id, mapping in data["system_mappings"].items():
                for v in mapping.get("values", []):
                    mt = v.get("maps_to")
                    if mt is not None and mt not in canonical_codes:
                        bad.append(f"{vocab_id}/{sys_id}: '{v['code']}' maps to '{mt}' which is not a canonical code")
        assert bad == [], (
            "Invalid maps_to targets:\n" + "\n".join(bad)
        )

    def test_unmapped_canonical_references_canonical_codes(self, all_vocabs):
        """Every code in unmapped_canonical must be a valid canonical code."""
        bad = []
        for vocab_id, data in all_vocabs.items():
            canonical_codes = {v["code"] for v in data.get("values", [])}
            for sys_id, mapping in data["system_mappings"].items():
                for code in mapping.get("unmapped_canonical", []):
                    if code not in canonical_codes:
                        bad.append(f"{vocab_id}/{sys_id}: unmapped_canonical '{code}' is not a canonical code")
        assert bad == [], (
            "Invalid unmapped_canonical entries:\n" + "\n".join(bad)
        )


# ---------------------------------------------------------------------------
# Build pipeline: enriched format flows through to vocabulary.json
# ---------------------------------------------------------------------------

class TestBuildPassthrough:
    """The build pipeline preserves enriched system_mappings structure."""

    def test_gender_type_has_enriched_mappings(self, real_result):
        """gender-type should have structured values in the built output."""
        vocab = real_result["vocabularies"]["gender-type"]
        sm = vocab["system_mappings"]
        assert sm is not None

        openspp = sm["openspp"]
        assert "values" in openspp
        assert isinstance(openspp["values"], list)
        assert len(openspp["values"]) > 0

        first = openspp["values"][0]
        assert "code" in first
        assert "label" in first
        assert "maps_to" in first

    def test_marital_status_uses_un_standard(self, real_result):
        """marital-status should reference the UN census framework, not FHIR."""
        vocab = real_result["vocabularies"]["marital-status"]
        assert vocab["standard"]["name"] == (
            "UN Principles and Recommendations for Population and Housing Censuses, Revision 3"
        )

    def test_marital_status_has_consensual_union(self, real_result):
        """marital-status should have consensual_union (renamed from common_law)."""
        vocab = real_result["vocabularies"]["marital-status"]
        codes = [v["code"] for v in vocab["values"]]
        assert "consensual_union" in codes
        assert "common_law" not in codes

    def test_marital_status_dropped_fhir_values(self, real_result):
        """marital-status should not have FHIR-only values."""
        vocab = real_result["vocabularies"]["marital-status"]
        codes = [v["code"] for v in vocab["values"]]
        for dropped in ["annulled", "interlocutory", "polygamous", "domestic_partner", "unmarried"]:
            assert dropped not in codes, f"{dropped} should have been dropped"


# ---------------------------------------------------------------------------
# Known bug regressions
# ---------------------------------------------------------------------------

class TestKnownBugFixes:
    """Regressions for bugs fixed during enrichment."""

    def test_openspp_gender_uses_numeric_codes(self, all_vocabs):
        """OpenSPP gender should use ISO 5218 numeric codes, not labels."""
        gender = all_vocabs["gender-type"]
        openspp = gender["system_mappings"]["openspp"]
        codes = [v["code"] for v in openspp["values"]]
        # Should be numeric ISO 5218 codes, not "male"/"female"/"other"
        assert "male" not in codes, "OpenSPP gender should use numeric codes, not 'male'"
        assert "1" in codes, "OpenSPP gender should have ISO 5218 code '1' for Male"

    def test_education_level_openimis_no_invalid_other(self, all_vocabs):
        """openIMIS education code 7 should not map to 'other' (not a canonical code)."""
        edu = all_vocabs["education-level"]
        openimis = edu["system_mappings"]["openimis"]
        code7 = [v for v in openimis["values"] if v["code"] == "7"]
        assert len(code7) == 1
        assert code7[0]["maps_to"] is None, (
            f"openIMIS education code 7 maps to '{code7[0]['maps_to']}' "
            "but should be null (no canonical equivalent)"
        )
