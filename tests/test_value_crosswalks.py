"""Tests for build.value_crosswalks: loading authored value_crosswalk
YAMLs and synthesizing them back into the pre-cutover ``system_mappings``
shape that vocabulary.json and the site consume.

The synthesis is the inverse of extract_crosswalks_from_legacy: it takes
the value_crosswalk shape (declarative, normalised) and emits the legacy
``system_mappings: { <sysid>: {vocabulary_name, values, unmapped_canonical} }``
dict the renderer expects.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from build.value_crosswalks import (
    SourceKey,
    StandardTodoError,
    load_crosswalks,
    synthesize_system_mappings,
)


def _write(tmp: Path, name: str, doc: dict) -> Path:
    p = tmp / name
    p.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return p


@pytest.fixture
def crosswalks_dir(tmp_path: Path) -> Path:
    d = tmp_path / "value_crosswalks"
    d.mkdir()
    _write(d, "sex--openspp.yaml", {
        "id": "sex--openspp",
        "source_value_set": {"id": "sex", "kind": "vocabulary", "source_id": "publicschema"},
        "target_value_set": {"id": "ISO 5218: Gender", "source_id": "openspp"},
        "pairs": [
            {"source_value": "not_known", "target_value": "0",
             "quality": "exact", "target_label": "Not known"},
            {"source_value": "male", "target_value": "1",
             "quality": "exact", "target_label": "Male"},
            {"source_value": "female", "target_value": "2",
             "quality": "exact", "target_label": "Female"},
        ],
        "standard": {
            "source_id": "openspp", "uri": "https://docs.openspp.org/",
            "custodian": "OpenSPP Community", "license": "Apache-2.0",
            "license_uri": "https://www.apache.org/licenses/LICENSE-2.0",
            "version": "1.3.0",
            "attribution_text": "x", "redistribution": "embed-with-attribution",
            "retrieved_at": "2026-05-07T00:00:00Z", "source_sha256": "f" * 64,
        },
    })
    _write(d, "crvs-registration-status--opencrvs.yaml", {
        "id": "crvs-registration-status--opencrvs",
        "source_value_set": {
            "id": "crvs/registration-status",
            "kind": "vocabulary",
            "source_id": "publicschema",
        },
        "target_value_set": {"id": "EventStatus", "source_id": "opencrvs"},
        "pairs": [
            {"source_value": "declared", "target_value": "CREATED",
             "quality": "exact", "target_label": "Created"},
            {"source_value": "registered", "target_value": "REGISTERED",
             "quality": "exact", "target_label": "Registered"},
            {"source_value": "cancelled", "target_value": None, "quality": "unmapped"},
            {"source_value": "corrected", "target_value": None, "quality": "unmapped"},
            {"source_value": None, "target_value": "EXTRA",
             "quality": "unmapped", "target_label": "Extra",
             "unmapped_reason": "no_equivalent"},
        ],
        "standard": {
            "source_id": "opencrvs",
            "uri": "https://documentation.opencrvs.org/",
            "custodian": "OpenCRVS Community", "license": "MPL-2.0",
            "license_uri": "https://www.mozilla.org/MPL/2.0/",
            "version": "2.0.0",
            "attribution_text": "x", "redistribution": "embed-with-attribution",
            "retrieved_at": "2026-05-07T00:00:00Z", "source_sha256": "a" * 64,
        },
    })
    _write(d, "electricity-access--dhs.yaml", {
        "id": "electricity-access--dhs",
        "source_value_set": {
            "id": "electricity_access", "kind": "property", "source_id": "publicschema",
        },
        "target_value_set": {"id": "DHS hv206", "source_id": "dhs"},
        "pairs": [
            {"source_value": "true", "target_value": "1", "quality": "exact",
             "target_label": "Yes"},
            {"source_value": "false", "target_value": "0", "quality": "exact",
             "target_label": "No"},
        ],
        "standard": {
            "source_id": "dhs", "uri": "https://dhsprogram.com/data/recode7/",
            "custodian": "DHS Program", "license": "DHS-Terms",
            "license_uri": "https://dhsprogram.com/Methodology/", "version": "DHS-7",
            "attribution_text": "x", "redistribution": "embed-with-attribution",
            "retrieved_at": "2026-05-07T00:00:00Z", "source_sha256": "b" * 64,
        },
    })
    return d


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


class TestLoad:
    def test_loads_and_keys_by_source(self, crosswalks_dir):
        index = load_crosswalks(crosswalks_dir)
        # Keyed by (source_kind, source_id) tuples; values are
        # {target_system_id: <crosswalk doc>} dicts.
        assert SourceKey("vocabulary", "sex") in index
        assert SourceKey("vocabulary", "crvs/registration-status") in index
        assert SourceKey("property", "electricity_access") in index
        assert "openspp" in index[SourceKey("vocabulary", "sex")]
        assert "opencrvs" in index[SourceKey("vocabulary", "crvs/registration-status")]
        assert "dhs" in index[SourceKey("property", "electricity_access")]

    def test_missing_dir_returns_empty(self, tmp_path):
        # The build should tolerate the directory not existing yet.
        assert load_crosswalks(tmp_path / "does-not-exist") == {}


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------


class TestSynthesize:
    def test_all_mapped_vocab(self, crosswalks_dir):
        index = load_crosswalks(crosswalks_dir)
        out = synthesize_system_mappings(index, "vocabulary", "sex")
        assert set(out.keys()) == {"openspp"}
        sm = out["openspp"]
        assert sm["vocabulary_name"] == "ISO 5218: Gender"
        assert "unmapped_canonical" not in sm
        assert sm["values"] == [
            {"code": "0", "label": "Not known", "maps_to": "not_known"},
            {"code": "1", "label": "Male", "maps_to": "male"},
            {"code": "2", "label": "Female", "maps_to": "female"},
        ]

    def test_with_unmapped_canonical_and_external_only(self, crosswalks_dir):
        index = load_crosswalks(crosswalks_dir)
        out = synthesize_system_mappings(
            index, "vocabulary", "crvs/registration-status",
        )
        sm = out["opencrvs"]
        # vocab name pulls from target_value_set.id
        assert sm["vocabulary_name"] == "EventStatus"
        # PublicSchema PVs with no external counterpart land in unmapped_canonical
        assert sm["unmapped_canonical"] == ["cancelled", "corrected"]
        # External codes with no PublicSchema PV (maps_to: null) appear in
        # `values` with maps_to: null and roundtripped unmapped_reason.
        codes = [v["code"] for v in sm["values"]]
        assert codes == ["CREATED", "REGISTERED", "EXTRA"]
        extra = next(v for v in sm["values"] if v["code"] == "EXTRA")
        assert extra["maps_to"] is None
        assert extra["label"] == "Extra"
        assert extra["unmapped_reason"] == "no_equivalent"

    def test_property_source(self, crosswalks_dir):
        index = load_crosswalks(crosswalks_dir)
        out = synthesize_system_mappings(
            index, "property", "electricity_access",
        )
        # Property crosswalks land in the property's system_mappings dict.
        assert "dhs" in out
        sm = out["dhs"]
        assert sm["vocabulary_name"] == "DHS hv206"
        assert sm["values"][0]["code"] == "1"
        assert sm["values"][0]["maps_to"] == "true"

    def test_unknown_source_returns_none(self, crosswalks_dir):
        index = load_crosswalks(crosswalks_dir)
        # Source with no crosswalks yields None (vs. an empty dict), so the
        # caller can distinguish "no crosswalks authored" from "authored but
        # empty" (the latter shouldn't happen but is unambiguous when it does).
        assert synthesize_system_mappings(index, "vocabulary", "nonexistent") is None

    def test_vocab_name_equal_to_system_id_is_dropped(self, tmp_path):
        # The extractor falls back to the target system id when legacy
        # authoring had no vocabulary_name (the schema requires a non-empty
        # target_value_set.id). Synthesis must recognise that fallback and
        # *not* emit a vocabulary_name, so the site doesn't render a
        # redundant "System vocabulary: <system_id>" line.
        d = tmp_path / "cw"
        d.mkdir()
        _write(d, "x--openspp.yaml", {
            "id": "x--openspp",
            "source_value_set": {"id": "x", "kind": "vocabulary", "source_id": "publicschema"},
            # id == source_id → "no name given" in legacy.
            "target_value_set": {"id": "openspp", "source_id": "openspp"},
            "pairs": [
                {"source_value": "a", "target_value": "A",
                 "quality": "exact", "target_label": "A"},
            ],
            "standard": _ok_standard("openspp"),
        })
        index = load_crosswalks(d)
        sm = synthesize_system_mappings(index, "vocabulary", "x")["openspp"]
        assert "vocabulary_name" not in sm

    def test_label_falls_back_to_code(self, tmp_path):
        d = tmp_path / "cw"
        d.mkdir()
        _write(d, "x--y.yaml", {
            "id": "x--y",
            "source_value_set": {"id": "x", "kind": "vocabulary", "source_id": "publicschema"},
            "target_value_set": {"id": "X", "source_id": "y"},
            # No target_label -> label falls back to target_value (the code).
            "pairs": [
                {"source_value": "a", "target_value": "A", "quality": "exact"},
            ],
            "standard": _ok_standard("y"),
        })
        index = load_crosswalks(d)
        sm = synthesize_system_mappings(index, "vocabulary", "x")["y"]
        assert sm["values"][0]["label"] == "A"


# ---------------------------------------------------------------------------
# Strict TODO option (a): the build refuses to ship TODO standards
# ---------------------------------------------------------------------------


class TestTodoStrict:
    def test_todo_in_standard_raises(self, tmp_path):
        d = tmp_path / "cw"
        d.mkdir()
        _write(d, "broken--sys.yaml", {
            "id": "broken--sys",
            "source_value_set": {"id": "broken", "kind": "vocabulary", "source_id": "publicschema"},
            "target_value_set": {"id": "Broken", "source_id": "sys"},
            "pairs": [
                {"source_value": "a", "target_value": "A",
                 "quality": "exact", "target_label": "A"},
            ],
            "standard": {
                "source_id": "sys", "uri": "https://example.org/",
                "custodian": "TODO",  # <-- the forbidden marker
                "license": "X", "license_uri": "https://x",
                "version": "1", "attribution_text": "x",
                "redistribution": "x", "retrieved_at": "2026-01-01T00:00:00Z",
                "source_sha256": "a" * 64,
            },
        })
        with pytest.raises(StandardTodoError) as excinfo:
            load_crosswalks(d, strict=True)
        assert "broken--sys" in str(excinfo.value)
        assert "custodian" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_standard(sysid: str) -> dict:
    return {
        "source_id": sysid, "uri": "https://example.org/",
        "custodian": "X", "license": "X", "license_uri": "https://x",
        "version": "1", "attribution_text": "x",
        "redistribution": "x", "retrieved_at": "2026-01-01T00:00:00Z",
        "source_sha256": "a" * 64,
    }
