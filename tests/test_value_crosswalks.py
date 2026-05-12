"""Tests for build.value_crosswalks: loading authored value_crosswalk
YAMLs and synthesizing them back into the pre-cutover ``system_mappings``
shape that vocabulary.json and the site consume.

The synthesis is the inverse of extract_crosswalks_from_legacy: it takes
the value_crosswalk shape (declarative, normalised) and emits the legacy
``system_mappings: { <sysid>: {vocabulary_name, values, unmapped_canonical} }``
dict the renderer expects.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from build.value_crosswalks import (
    SourceKey,
    StandardTodoError,
    load_crosswalks,
    synthesize_system_mappings,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "build" / "schemas" / "value_crosswalk.schema.json"


@pytest.fixture(scope="module")
def crosswalk_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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
# Build overlay merge: authored crosswalks override on shared target_system_id,
# but reader-side entries for other target systems must survive.
# ---------------------------------------------------------------------------


class TestBuildOverlayMerge:
    def test_reader_entries_preserved_when_crosswalk_partial(self, tmp_path):
        """A crosswalk for one target system must not wipe reader entries for
        other target systems on the same source vocabulary."""
        from build.build import build_vocabulary

        crosswalks = tmp_path / "cw"
        crosswalks.mkdir()
        _write(crosswalks, "demo--openspp.yaml", {
            "id": "demo--openspp",
            "source_value_set": {"id": "demo", "kind": "vocabulary", "source_id": "publicschema"},
            "target_value_set": {"id": "ISO 5218: Gender", "source_id": "openspp"},
            "pairs": [
                {"source_value": "m", "target_value": "1",
                 "quality": "exact", "target_label": "Male"},
            ],
            "standard": _ok_standard("openspp"),
        })

        raws = {
            "meta": {"base_uri": "https://test.example/", "languages": ["en"]},
            "concepts": {},
            "properties": {},
            "vocabularies": {
                "demo": {
                    "id": "demo",
                    "values": [
                        {"code": "m", "label": {"en": "Male"},
                         "definition": {"en": "Male"}},
                    ],
                    "system_mappings": {
                        "openspp": {
                            "vocabulary_name": "stale-reader-name",
                            "values": [{"code": "OLD", "label": "Old", "maps_to": "m"}],
                        },
                        "reader_only_sys": {
                            "vocabulary_name": "ReaderOnly",
                            "values": [{"code": "X", "label": "X-only", "maps_to": "m"}],
                        },
                    },
                },
            },
        }

        result = build_vocabulary(raws=raws, crosswalks_dir=crosswalks)
        sm = result["vocabularies"]["demo"]["system_mappings"]

        # Crosswalk overrides reader on the shared target system.
        assert sm["openspp"]["vocabulary_name"] == "ISO 5218: Gender"
        # Reader-only target system is preserved.
        assert "reader_only_sys" in sm, (
            f"reader-only target system was dropped by overlay; "
            f"got keys: {sorted(sm.keys())}"
        )
        assert sm["reader_only_sys"]["vocabulary_name"] == "ReaderOnly"


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
# artifact_kind: none — documented "no canonical artifact" exception
#
# Some upstream standards (multi-repo assemblies, multi-country surveys,
# GitBook/wiki specs, country-configured enums) have no single fetchable
# artifact that a SHA-256 can represent. For those, the crosswalk file
# sets ``artifact_kind: none`` and provides a non-empty
# ``artifact_notes:`` explaining why. The schema then waives the
# ``source_sha256`` requirement for that file.
#
# This is distinct from a literal ``TODO`` value, which still signals
# "incomplete work" and is rejected by both the JSON schema (via
# conditional required-ness) and the strict loader.
# ---------------------------------------------------------------------------


def _crosswalk_doc(standard: dict) -> dict:
    return {
        "id": "demo--sys",
        "source_value_set": {
            "id": "demo", "kind": "vocabulary", "source_id": "publicschema",
        },
        "target_value_set": {"id": "Demo", "source_id": "sys"},
        "pairs": [
            {"source_value": "a", "target_value": "A",
             "quality": "exact", "target_label": "A"},
        ],
        "standard": standard,
    }


def _standard_without_sha(sysid: str, **overrides) -> dict:
    base = _ok_standard(sysid)
    del base["source_sha256"]
    base.update(overrides)
    return base


class TestArtifactKindContract:
    """The JSON schema is the single source of truth for the
    ``standard.artifact_kind`` enum and its required-field implications.
    """

    def test_artifact_kind_none_accepts_without_source_sha256(self, crosswalk_schema):
        doc = _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="none",
            artifact_notes="multi-repo assembly; no single canonical artifact",
        ))
        jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)

    def test_artifact_kind_none_requires_artifact_notes(self, crosswalk_schema):
        doc = _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="none",
        ))
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)
        assert "artifact_notes" in str(exc.value)

    def test_artifact_kind_none_rejects_empty_artifact_notes(self, crosswalk_schema):
        doc = _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="none", artifact_notes="",
        ))
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)

    def test_legacy_form_still_requires_source_sha256(self, crosswalk_schema):
        # No artifact_kind set, no source_sha256 → schema must reject.
        doc = _crosswalk_doc(_standard_without_sha("sys"))
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)
        assert "source_sha256" in str(exc.value)

    def test_artifact_kind_single_file_requires_source_sha256(self, crosswalk_schema):
        doc = _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="single_file",
        ))
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)
        assert "source_sha256" in str(exc.value)

    def test_artifact_kind_manifest_requires_source_sha256(self, crosswalk_schema):
        doc = _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="manifest",
        ))
        with pytest.raises(jsonschema.ValidationError) as exc:
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)
        assert "source_sha256" in str(exc.value)

    def test_artifact_kind_unknown_value_rejected(self, crosswalk_schema):
        doc = _crosswalk_doc({**_ok_standard("sys"), "artifact_kind": "bogus"})
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)

    def test_existing_form_with_source_sha256_still_accepted(self, crosswalk_schema):
        # Pre-existing 62 files don't carry artifact_kind; they must continue
        # to validate as-is so the conversion is non-breaking.
        doc = _crosswalk_doc(_ok_standard("sys"))
        jsonschema.Draft202012Validator(crosswalk_schema).validate(doc)

    def test_loader_accepts_artifact_kind_none_in_strict_mode(self, tmp_path):
        # The strict-loader gate rejects literal TODO. ``artifact_kind:
        # none`` + ``artifact_notes:`` carries no TODOs and must pass.
        d = tmp_path / "cw"
        d.mkdir()
        _write(d, "ok--sys.yaml", _crosswalk_doc(_standard_without_sha(
            "sys", artifact_kind="none",
            artifact_notes="multi-repo assembly; no single canonical artifact",
        )))
        # Should not raise:
        load_crosswalks(d, strict=True)

    def test_loader_still_rejects_todo_in_strict_mode_with_artifact_kind(self, tmp_path):
        # If a file declares artifact_kind: none but leaves some other field
        # as literal TODO, the strict gate must still catch it.
        d = tmp_path / "cw"
        d.mkdir()
        std = _standard_without_sha(
            "sys", artifact_kind="none", artifact_notes="reason",
        )
        std["custodian"] = "TODO"
        _write(d, "broken--sys.yaml", _crosswalk_doc(std))
        with pytest.raises(StandardTodoError):
            load_crosswalks(d, strict=True)


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
