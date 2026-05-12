"""Tests for build.extract_crosswalks_from_legacy.

TDD: these tests define the expected mapping from the pre-cutover
system_mappings shape to the value_crosswalk shape used across
publicschema-build and publicschema.com/apps/core. The schema lives at
build/schemas/value_crosswalk.schema.json (byte-identical to upstream).
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import jsonschema
import pytest

from build.extract_crosswalks_from_legacy import (
    crosswalk_filename,
    crosswalk_id,
    extract_crosswalk,
    main,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "build" / "schemas" / "value_crosswalk.schema.json"


@pytest.fixture(scope="module")
def crosswalk_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def system_registry() -> dict:
    """Minimal in-memory stand-in for build/external_system_prefixes.yaml."""
    return {
        "openspp": {
            "prefix": "openspp",
            "uri": "https://docs.openspp.org/",
            "label": "OpenSPP",
            "source": "official",
            "homepage": "https://openspp.org/",
        },
        "opencrvs": {
            "prefix": "opencrvs",
            "uri": "https://documentation.opencrvs.org/technology/event-service-v2/",
            "label": "OpenCRVS",
            "source": "official",
            "homepage": "https://opencrvs.org/",
        },
        "dhs": {
            "prefix": "dhs",
            "uri": "https://dhsprogram.com/data/recode7/",
            "label": "DHS Program Recode 7",
            "source": "site-anchor",
            "homepage": "https://dhsprogram.com/data/",
        },
    }


@pytest.fixture
def external_references() -> dict:
    """Stand-in for schema/external_references/<sys>.yaml docs. We seed
    one fully-populated entry (openspp) and leave others absent so the
    TODO-placeholder path is exercised."""
    return {
        "openspp": {
            "id": "openspp",
            "name": "OpenSPP",
            "custodian": "OpenSPP Community",
            "version": "1.3.0",
            "license": {
                "id": "Apache-2.0",
                "uri": "https://www.apache.org/licenses/LICENSE-2.0",
                "attribution_text": "Contains information from OpenSPP, licensed under Apache 2.0.",
                "redistribution": "embed-with-attribution",
            },
            "artifacts": [
                {
                    "sha256": "0123456789abcdef" * 4,
                    "retrieved_at": "2026-05-07T00:00:00Z",
                }
            ],
        },
    }


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------


class TestNaming:
    def test_crosswalk_id_bare_vocab(self):
        assert crosswalk_id("vocabulary", "sex", "openspp") == "sex--openspp"

    def test_crosswalk_id_domain_scoped_vocab(self):
        # crvs/registration-status -> crvs-registration-status (filesystem-safe)
        assert (
            crosswalk_id("vocabulary", "crvs/registration-status", "opencrvs")
            == "crvs-registration-status--opencrvs"
        )

    def test_crosswalk_id_property(self):
        # Properties have no slash; id is the bare property name.
        assert crosswalk_id("property", "electricity_access", "dhs") == "electricity-access--dhs"

    def test_crosswalk_id_system_with_hyphen(self):
        # dhs-8 has a hyphen in the system id; preserved in the suffix.
        assert crosswalk_id("vocabulary", "sex", "dhs-8") == "sex--dhs-8"

    def test_crosswalk_filename(self):
        assert crosswalk_filename("sex--openspp") == "sex--openspp.yaml"


# ---------------------------------------------------------------------------
# Extraction: shape
# ---------------------------------------------------------------------------


class TestExtractionShape:
    def test_simple_all_mapped(self, system_registry, external_references, crosswalk_schema):
        entry = {
            "vocabulary_name": "ISO 5218: Gender",
            "values": [
                {"code": "0", "label": "Not known", "maps_to": "not_known"},
                {"code": "1", "label": "Male", "maps_to": "male"},
                {"code": "2", "label": "Female", "maps_to": "female"},
                {"code": "9", "label": "Not applicable", "maps_to": "not_applicable"},
            ],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )

        # id and source/target metadata
        assert out["id"] == "sex--openspp"
        assert out["source_value_set"] == {
            "id": "sex",
            "kind": "vocabulary",
            "source_id": "publicschema",
        }
        assert out["target_value_set"] == {
            "id": "ISO 5218: Gender",
            "source_id": "openspp",
        }

        # pairs: 4 mapped, no unmapped
        assert len(out["pairs"]) == 4
        first = out["pairs"][0]
        assert first["source_value"] == "not_known"
        assert first["target_value"] == "0"
        assert first["quality"] == "exact"
        assert first["target_label"] == "Not known"

        # standard block sourced from external_references
        std = out["standard"]
        assert std["source_id"] == "openspp"
        assert std["uri"] == "https://docs.openspp.org/"
        assert std["custodian"] == "OpenSPP Community"
        assert std["license"] == "Apache-2.0"
        assert std["version"] == "1.3.0"
        assert std["source_sha256"] == "0123456789abcdef" * 4

        # validates against the vendored schema
        jsonschema.Draft202012Validator(crosswalk_schema).validate(out)

    def test_with_unmapped_canonical(self, system_registry, external_references):
        # crvs/registration-status sample (5 mapped, 4 unmapped canonical).
        entry = {
            "vocabulary_name": "EventStatus",
            "values": [
                {"code": "CREATED", "label": "Created", "maps_to": "declared",
                 "note": "Draft event created."},
                {"code": "REGISTERED", "label": "Registered", "maps_to": "registered"},
            ],
            "unmapped_canonical": ["cancelled", "corrected", "pending_validation", "rejected"],
            "note": "Top-level crosswalk note explaining the mapping rationale.",
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="crvs/registration-status",
            target_system_id="opencrvs",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )

        assert out["id"] == "crvs-registration-status--opencrvs"

        # 2 mapped + 4 unmapped-canonical = 6 pairs total
        assert len(out["pairs"]) == 6

        mapped = [p for p in out["pairs"] if p["target_value"] is not None]
        unmapped_canon = [p for p in out["pairs"] if p["target_value"] is None]
        assert len(mapped) == 2
        assert len(unmapped_canon) == 4
        for p in unmapped_canon:
            assert p["source_value"] in {
                "cancelled", "corrected", "pending_validation", "rejected"
            }
            assert p["quality"] == "unmapped"
            assert p["target_value"] is None

        # per-pair note round-trips
        created_pair = next(p for p in mapped if p["target_value"] == "CREATED")
        assert created_pair["note"] == "Draft event created."

        # top-level note surfaces as crosswalk-level notes
        assert out.get("notes") == "Top-level crosswalk note explaining the mapping rationale."

    def test_with_external_only_unmapped(self, system_registry, external_references):
        # A value with maps_to: null + unmapped_reason: the external code exists,
        # but no PublicSchema PV maps to it. Source side is null in the pair.
        entry = {
            "vocabulary_name": "Gender",
            "values": [
                {"code": "Male", "label": "Male", "maps_to": "male"},
                {
                    "code": "Other",
                    "label": "Others",
                    "maps_to": None,
                    "unmapped_reason": "no_equivalent",
                },
            ],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="opencrvs",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )
        assert len(out["pairs"]) == 2
        ext_only = next(p for p in out["pairs"] if p["target_value"] == "Other")
        assert ext_only["source_value"] is None
        assert ext_only["quality"] == "unmapped"
        assert ext_only["target_label"] == "Others"
        assert ext_only["unmapped_reason"] == "no_equivalent"

    def test_migration_note_roundtrip(self, system_registry, external_references):
        entry = {
            "vocabulary_name": "Anything",
            "values": [
                {
                    "code": "x",
                    "label": "X",
                    "maps_to": "x",
                    "migration_note": "Renamed in v2 from y to x.",
                },
            ],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="thing",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )
        assert out["pairs"][0]["migration_note"] == "Renamed in v2 from y to x."

    def test_from_property(self, system_registry, external_references):
        # Property-level system_mappings have the same nested shape.
        entry = {
            "vocabulary_name": "DHS hv206 (Electricity)",
            "values": [
                {"code": "0", "label": "No", "maps_to": "false"},
                {"code": "1", "label": "Yes", "maps_to": "true"},
            ],
            "note": "Binary; DHS-7 codes 8/9 (missing/refused) drop on import.",
        }
        out = extract_crosswalk(
            source_kind="property",
            source_id="electricity_access",
            target_system_id="dhs",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )
        assert out["id"] == "electricity-access--dhs"
        assert out["source_value_set"]["kind"] == "property"
        assert out["source_value_set"]["id"] == "electricity_access"


# ---------------------------------------------------------------------------
# Extraction: TODO placeholders (option (a) — strict)
# ---------------------------------------------------------------------------


class TestTodoPlaceholders:
    def test_missing_external_reference_yields_todo_placeholders(
        self, system_registry, external_references
    ):
        # `opencrvs` is not in external_references — every metadata field
        # in standard{} that we can't source must surface as the literal
        # string "TODO" so the build refuses to ship.
        entry = {
            "vocabulary_name": "EventStatus",
            "values": [{"code": "X", "label": "X", "maps_to": "x"}],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="opencrvs",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )
        std = out["standard"]
        # uri and source_id are always derivable from build/external_system_prefixes.yaml
        assert std["source_id"] == "opencrvs"
        assert std["uri"] == "https://documentation.opencrvs.org/technology/event-service-v2/"
        # The rest are TODO because no schema/external_references/opencrvs.yaml exists,
        # except the artifact fields: no external_reference means no artifacts, so
        # artifact_kind: none is emitted (not source_sha256: TODO).
        for k in (
            "custodian",
            "license",
            "license_uri",
            "version",
            "attribution_text",
            "redistribution",
            "retrieved_at",
        ):
            assert std[k] == "TODO", f"expected TODO placeholder at standard.{k}, got {std[k]!r}"
        # No artifacts available: emits artifact_kind: none, not source_sha256: TODO.
        assert std.get("artifact_kind") == "none"
        assert isinstance(std.get("artifact_notes"), str)
        assert "source_sha256" not in std

    def test_unknown_target_system_raises(self, system_registry, external_references):
        # A system id that isn't in the registry is a hard error — we
        # refuse to emit a crosswalk pointing at an unknown system.
        entry = {"vocabulary_name": "X", "values": [{"code": "a", "label": "A", "maps_to": "a"}]}
        with pytest.raises(KeyError):
            extract_crosswalk(
                source_kind="vocabulary",
                source_id="sex",
                target_system_id="nonexistent",
                entry=entry,
                system_registry=system_registry,
                external_references=external_references,
            )


# ---------------------------------------------------------------------------
# Part A: artifact_kind: none when no sha256 is available
# ---------------------------------------------------------------------------


class TestArtifactKindNone:
    def test_no_artifacts_block_emits_artifact_kind_none(self, system_registry):
        # external_references entry has no artifacts block at all.
        ext_refs_no_artifacts = {
            "openspp": {
                "id": "openspp",
                "name": "OpenSPP",
                "custodian": "OpenSPP Community",
                "version": "1.3.0",
                "license": {
                    "id": "Apache-2.0",
                    "uri": "https://www.apache.org/licenses/LICENSE-2.0",
                    "attribution_text": "Contains information from OpenSPP, licensed under Apache 2.0.",
                    "redistribution": "embed-with-attribution",
                },
                # No 'artifacts' key at all.
            },
        }
        entry = {
            "vocabulary_name": "ISO 5218: Gender",
            "values": [{"code": "1", "label": "Male", "maps_to": "male"}],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=ext_refs_no_artifacts,
        )
        std = out["standard"]
        assert std.get("artifact_kind") == "none"
        assert isinstance(std.get("artifact_notes"), str)
        assert std["artifact_notes"].strip()
        assert "source_sha256" not in std

    def test_empty_artifacts_list_emits_artifact_kind_none(self, system_registry):
        # artifacts: [] is present but empty.
        ext_refs_empty_artifacts = {
            "openspp": {
                "id": "openspp",
                "name": "OpenSPP",
                "custodian": "OpenSPP Community",
                "version": "1.3.0",
                "license": {
                    "id": "Apache-2.0",
                    "uri": "https://www.apache.org/licenses/LICENSE-2.0",
                    "attribution_text": "Contains information from OpenSPP, licensed under Apache 2.0.",
                    "redistribution": "embed-with-attribution",
                },
                "artifacts": [],
            },
        }
        entry = {
            "vocabulary_name": "ISO 5218: Gender",
            "values": [{"code": "1", "label": "Male", "maps_to": "male"}],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=ext_refs_empty_artifacts,
        )
        std = out["standard"]
        assert std.get("artifact_kind") == "none"
        assert isinstance(std.get("artifact_notes"), str)
        assert std["artifact_notes"].strip()
        assert "source_sha256" not in std

    def test_artifact_without_sha256_emits_artifact_kind_none(self, system_registry):
        # Artifact entry exists but has no sha256 key.
        ext_refs_no_sha256 = {
            "openspp": {
                "id": "openspp",
                "name": "OpenSPP",
                "custodian": "OpenSPP Community",
                "version": "1.3.0",
                "license": {
                    "id": "Apache-2.0",
                    "uri": "https://www.apache.org/licenses/LICENSE-2.0",
                    "attribution_text": "Contains information from OpenSPP, licensed under Apache 2.0.",
                    "redistribution": "embed-with-attribution",
                },
                "artifacts": [{"retrieved_at": "2026-05-07T00:00:00Z"}],
            },
        }
        entry = {
            "vocabulary_name": "ISO 5218: Gender",
            "values": [{"code": "1", "label": "Male", "maps_to": "male"}],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=ext_refs_no_sha256,
        )
        std = out["standard"]
        assert std.get("artifact_kind") == "none"
        assert isinstance(std.get("artifact_notes"), str)
        assert std["artifact_notes"].strip()
        assert "source_sha256" not in std

    def test_sha256_present_still_emits_source_sha256(self, system_registry, external_references):
        # Sanity: when sha256 IS present, the old field is still emitted.
        entry = {
            "vocabulary_name": "ISO 5218: Gender",
            "values": [{"code": "1", "label": "Male", "maps_to": "male"}],
        }
        out = extract_crosswalk(
            source_kind="vocabulary",
            source_id="sex",
            target_system_id="openspp",
            entry=entry,
            system_registry=system_registry,
            external_references=external_references,
        )
        std = out["standard"]
        assert "source_sha256" in std
        assert "artifact_kind" not in std


# ---------------------------------------------------------------------------
# Part B: --force guard against accidental re-runs
# ---------------------------------------------------------------------------


class TestForceFlag:
    """Integration tests for the --force / no-force write guard.

    These tests drive main() directly against a temp directory populated by
    a minimal stub of the git-history scan. To avoid network/git calls, we
    monkey-patch the two git helpers and the registry/reference loaders.
    """

    @pytest.fixture
    def _patch_main(self, monkeypatch, tmp_path):
        """Patch main()'s git and registry helpers to return one crosswalk's
        worth of data without touching the actual git repo."""
        import build.extract_crosswalks_from_legacy as mod

        fake_system_registry = {
            "openspp": {
                "prefix": "openspp",
                "uri": "https://docs.openspp.org/",
                "label": "OpenSPP",
                "source": "official",
                "homepage": "https://openspp.org/",
            }
        }
        fake_external_refs = {
            "openspp": {
                "id": "openspp",
                "custodian": "OpenSPP Community",
                "version": "1.0",
                "license": {
                    "id": "Apache-2.0",
                    "uri": "https://apache.org/",
                    "attribution_text": "OpenSPP",
                    "redistribution": "embed-with-attribution",
                },
                "artifacts": [
                    {
                        "sha256": "abc123" * 10 + "abcd",
                        "retrieved_at": "2026-01-01",
                    }
                ],
            }
        }
        # One vocabulary with one system_mapping
        fake_vocabs = [
            (
                "vocabulary",
                "sex",
                {
                    "system_mappings": {
                        "openspp": {
                            "vocabulary_name": "Gender",
                            "values": [{"code": "M", "label": "Male", "maps_to": "male"}],
                        }
                    }
                },
            )
        ]

        monkeypatch.setattr(mod, "_load_system_registry", lambda _root: fake_system_registry)
        monkeypatch.setattr(mod, "_load_external_references", lambda _root: fake_external_refs)
        monkeypatch.setattr(
            mod, "_load_legacy_resources", lambda _root, _rev: (fake_vocabs, [])
        )
        return tmp_path

    def test_second_run_without_force_skips_and_warns(self, _patch_main, capsys):
        out_dir = _patch_main
        expected_file = out_dir / "sex--openspp.yaml"

        # First run writes the file.
        rc = main(["--out", str(out_dir)])
        assert rc == 0
        assert expected_file.exists()

        # Write a sentinel so we can detect if the file was overwritten.
        sentinel = "SENTINEL_CONTENT_DO_NOT_OVERWRITE\n"
        expected_file.write_text(sentinel, encoding="utf-8")

        # Second run without --force should skip.
        rc = main(["--out", str(out_dir)])
        assert rc == 0

        # File must not have been overwritten.
        assert expected_file.read_text(encoding="utf-8") == sentinel

        # stderr must mention the skipped file and hint about --force.
        captured = capsys.readouterr()
        assert expected_file.name in captured.err
        assert "--force" in captured.err

    def test_second_run_with_force_overwrites(self, _patch_main, capsys):
        out_dir = _patch_main
        expected_file = out_dir / "sex--openspp.yaml"

        # First run.
        rc = main(["--out", str(out_dir)])
        assert rc == 0

        sentinel = "SENTINEL_CONTENT_DO_NOT_OVERWRITE\n"
        expected_file.write_text(sentinel, encoding="utf-8")

        # Second run with --force should overwrite.
        rc = main(["--out", str(out_dir), "--force"])
        assert rc == 0
        assert expected_file.read_text(encoding="utf-8") != sentinel
