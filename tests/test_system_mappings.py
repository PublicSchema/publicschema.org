"""Tests for authored LinkML system_mappings metadata.

Validates that authored properties or vocabularies with system_mappings use
the structured format (code + label + maps_to) and that the build pipeline
preserves that structure.
"""


import pytest

from build.build import build_vocabulary
from tests.conftest import SCHEMA_DIR
from tests.schema_reader import raw_schema

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_result():
    return build_vocabulary(SCHEMA_DIR)


@pytest.fixture(scope="module")
def mapped_entities():
    """Load authored LinkML entities that have system_mappings."""
    result = {}
    schema = raw_schema()
    for group in ("properties", "vocabularies"):
        for key, data in schema[group].items():
            if data.get("system_mappings"):
                result[f"{group}/{key}"] = data
    return result


# ---------------------------------------------------------------------------
# Format validation: every system_mappings entry uses enriched format
# ---------------------------------------------------------------------------

class TestEnrichedFormat:
    """All system_mappings must use the enriched format."""

    def test_all_mappings_have_values_list(self, mapped_entities):
        """Each system mapping must have a 'values' list, not a flat dict."""
        flat_mappings = []
        for entity_id, data in mapped_entities.items():
            for sys_id, mapping in data["system_mappings"].items():
                if not isinstance(mapping, dict) or "values" not in mapping:
                    flat_mappings.append(f"{entity_id}/{sys_id}")
        assert flat_mappings == [], (
            f"These system mappings still use flat format: {flat_mappings}"
        )

    def test_values_have_required_fields(self, mapped_entities):
        """Each value entry must have code, label, and maps_to."""
        missing = []
        for entity_id, data in mapped_entities.items():
            for sys_id, mapping in data["system_mappings"].items():
                for i, v in enumerate(mapping.get("values", [])):
                    for field in ["code", "label", "maps_to"]:
                        if field not in v:
                            missing.append(f"{entity_id}/{sys_id}[{i}] missing '{field}'")
        assert missing == [], (
            "Values missing required fields:\n" + "\n".join(missing)
        )

    def test_maps_to_is_scalar_or_null(self, mapped_entities):
        """maps_to must be a scalar value or null."""
        bad = []
        allowed_types = (str, int, float, bool)
        for entity_id, data in mapped_entities.items():
            for sys_id, mapping in data["system_mappings"].items():
                for v in mapping.get("values", []):
                    mt = v.get("maps_to")
                    if mt is not None and not isinstance(mt, allowed_types):
                        bad.append(
                            f"{entity_id}/{sys_id}: maps_to={mt!r} "
                            f"(type {type(mt).__name__})"
                        )
        assert bad == [], "Invalid maps_to types:\n" + "\n".join(bad)

    def test_labels_not_empty(self, mapped_entities):
        """Labels should not be empty strings."""
        empty = []
        for entity_id, data in mapped_entities.items():
            for sys_id, mapping in data["system_mappings"].items():
                for v in mapping.get("values", []):
                    if not str(v.get("label", "")).strip():
                        empty.append(f"{entity_id}/{sys_id}: code={v['code']} has empty label")
        assert empty == [], "Empty labels:\n" + "\n".join(empty)


# ---------------------------------------------------------------------------
# Referential integrity: unmapped_canonical remains list-shaped
# ---------------------------------------------------------------------------

class TestMappingIntegrity:
    """Validate fields that are still meaningful in authored LinkML metadata."""

    def test_unmapped_canonical_is_a_list(self, mapped_entities):
        """unmapped_canonical, when present, must be a list."""
        bad = []
        for entity_id, data in mapped_entities.items():
            for sys_id, mapping in data["system_mappings"].items():
                unmapped = mapping.get("unmapped_canonical")
                if unmapped is not None and not isinstance(unmapped, list):
                    bad.append(f"{entity_id}/{sys_id}: unmapped_canonical is not a list")
        assert bad == [], "Invalid unmapped_canonical fields:\n" + "\n".join(bad)


# ---------------------------------------------------------------------------
# Build pipeline: enriched format flows through to vocabulary.json
# ---------------------------------------------------------------------------

class TestBuildPassthrough:
    """The build pipeline preserves enriched system_mappings structure."""

    def test_electricity_access_has_enriched_mappings(self, real_result):
        """electricity_access should have structured values in the built output."""
        prop = real_result["properties"]["electricity_access"]
        sm = prop["system_mappings"]
        assert sm is not None

        dhs = sm["dhs"]
        assert "values" in dhs
        assert isinstance(dhs["values"], list)
        assert len(dhs["values"]) > 0

        first = dhs["values"][0]
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
