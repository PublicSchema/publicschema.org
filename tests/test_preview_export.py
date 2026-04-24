"""Tests for preview.json generation (hover-card data source)."""

import pytest

from build.build import build_vocabulary
from build.preview_export import (
    LOCALE_EXCERPT_LIMIT,
    build_preview,
    truncate_excerpt,
)

from tests.conftest import make_concept, make_property, make_vocabulary


class TestTruncateExcerpt:
    def test_short_text_untruncated(self):
        text = "A short definition."
        assert truncate_excerpt(text, limit=220) == text

    def test_empty_text(self):
        assert truncate_excerpt("", limit=220) == ""

    def test_long_text_cut_at_word_boundary(self):
        text = "word " * 200  # 1000 chars
        result = truncate_excerpt(text, limit=50)
        assert len(result) <= 50 + 1  # +1 for ellipsis
        stripped = result.rstrip("…").strip()
        assert all(tok == "word" for tok in stripped.split())

    def test_ends_with_ellipsis_when_truncated(self):
        text = "A" * 500
        result = truncate_excerpt(text, limit=100)
        assert result.endswith("…")

    def test_cut_point_respects_word(self):
        text = "alpha beta gammalongword delta"
        result = truncate_excerpt(text, limit=15)
        # Must not cut "gammalongword" partway through.
        assert "gammalon" not in result.rstrip("…")

    def test_single_long_word_hard_cut(self):
        """A single word longer than the limit is hard-cut with ellipsis."""
        text = "supercalifragilisticexpialidocious"
        result = truncate_excerpt(text, limit=10)
        assert result.endswith("…")
        assert len(result) <= 11


class TestBuildPreviewConcepts:
    def test_universal_concept_keyed_by_path(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)

        path = result["concepts"]["Person"]["path"]
        assert path == "/Person"
        assert path in preview
        entry = preview[path]
        assert set(entry.keys()) == {"en", "fr", "es"}
        assert entry["en"]["kind"] == "concept"
        assert entry["en"]["href"] == path
        assert entry["en"]["maturity"] == "draft"

    def test_domain_concept_carries_domain_field(
        self, tmp_schema, write_concept
    ):
        write_concept("enrollment.yaml", make_concept(id="Enrollment", domain="sp"))
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)

        path = result["concepts"]["sp/Enrollment"]["path"]
        assert path == "/sp/Enrollment"
        assert preview[path]["en"]["domain"] == "sp"
        assert preview[path]["en"]["kind"] == "concept"

    def test_universal_concept_has_null_domain(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        entry = preview[result["concepts"]["Person"]["path"]]["en"]
        assert entry["domain"] is None

    def test_abstract_flag_propagated(self, tmp_schema, write_concept):
        write_concept(
            "agent.yaml", make_concept(id="Agent", abstract=True)
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        entry = preview[result["concepts"]["Agent"]["path"]]["en"]
        assert entry["abstract"] is True

    def test_non_abstract_flag_defaults_false(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        entry = preview[result["concepts"]["Person"]["path"]]["en"]
        assert entry["abstract"] is False


class TestBuildPreviewProperties:
    def test_property_has_type_and_vocabulary(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        write_vocabulary(
            "severity.yaml", make_vocabulary(id="severity")
        )
        write_property(
            "sev.yaml",
            make_property(id="sev", type="string", vocabulary="severity"),
        )
        write_concept(
            "test.yaml", make_concept(id="Test", properties=["sev"])
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        path = result["properties"]["sev"]["path"]
        entry = preview[path]["en"]
        assert entry["kind"] == "property"
        assert entry["type"] == "string"
        assert entry["vocabulary"] == "severity"

    def test_property_without_vocabulary_has_null(
        self, tmp_schema, write_concept, write_property
    ):
        write_property(
            "count.yaml", make_property(id="count", type="integer")
        )
        write_concept(
            "test.yaml", make_concept(id="Test", properties=["count"])
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        entry = preview[result["properties"]["count"]["path"]]["en"]
        assert entry["vocabulary"] is None
        assert entry["type"] == "integer"


class TestBuildPreviewVocabularies:
    def test_vocabulary_entry_present(self, tmp_schema, write_vocabulary):
        write_vocabulary(
            "severity.yaml", make_vocabulary(id="severity")
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        path = result["vocabularies"]["severity"]["path"]
        assert path == "/vocab/severity"
        assert path in preview
        entry = preview[path]["en"]
        assert entry["kind"] == "vocabulary"
        assert entry["href"] == path


class TestBuildPreviewLocales:
    def test_locale_fallback_marked(
        self, tmp_schema, write_concept, write_property
    ):
        """Property with only English text flags fr/es entries as fallback."""
        en_only = make_property(id="en_only", type="string")
        en_only["label"] = {"en": "English only"}
        en_only["definition"] = {"en": "Only in English."}
        write_property("en_only.yaml", en_only)
        write_concept(
            "test.yaml", make_concept(id="Test", properties=["en_only"])
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        path = result["properties"]["en_only"]["path"]
        entry = preview[path]
        assert entry["en"]["locale_used"] == "en"
        assert entry["fr"]["locale_used"] == "en"
        assert entry["es"]["locale_used"] == "en"
        assert entry["fr"]["definition_excerpt"] == "Only in English."

    def test_excerpt_respects_locale_limits(
        self, tmp_schema, write_concept, write_property
    ):
        prop = make_property(id="wordy", type="string")
        prop["definition"] = {
            "en": "word " * 100,
            "fr": "mot " * 100,
            "es": "palabra " * 100,
        }
        write_property("wordy.yaml", prop)
        write_concept(
            "test.yaml", make_concept(id="Test", properties=["wordy"])
        )
        result = build_vocabulary(tmp_schema)

        preview = build_preview(result)
        path = result["properties"]["wordy"]["path"]
        entry = preview[path]
        assert (
            len(entry["en"]["definition_excerpt"])
            <= LOCALE_EXCERPT_LIMIT["en"] + 1
        )
        assert (
            len(entry["fr"]["definition_excerpt"])
            <= LOCALE_EXCERPT_LIMIT["fr"] + 1
        )
        assert (
            len(entry["es"]["definition_excerpt"])
            <= LOCALE_EXCERPT_LIMIT["es"] + 1
        )


class TestBuildPreviewCoverage:
    def test_every_concept_property_and_vocabulary_has_entry(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        write_vocabulary("v1.yaml", make_vocabulary(id="v1"))
        write_property("p1.yaml", make_property(id="p1", type="string"))
        write_property("p2.yaml", make_property(id="p2", type="integer"))
        write_concept(
            "c.yaml",
            make_concept(id="C", properties=["p1", "p2"]),
        )
        result = build_vocabulary(tmp_schema)
        preview = build_preview(result)

        for concept in result["concepts"].values():
            assert concept["path"] in preview
        for prop in result["properties"].values():
            assert prop["path"] in preview
        for vocab in result["vocabularies"].values():
            assert vocab["path"] in preview

    def test_no_system_entries(
        self, tmp_schema, write_concept, write_property
    ):
        """Scope guard: preview should not contain system-keyed entries."""
        write_property("p.yaml", make_property(id="p", type="string"))
        write_concept("c.yaml", make_concept(id="C", properties=["p"]))
        result = build_vocabulary(tmp_schema)
        preview = build_preview(result)

        # System entries would typically use /systems/* keys.
        assert not any(
            k.startswith("/systems/") for k in preview
        )
        # Every kind in the preview is concept/property/vocabulary only.
        kinds = {
            locale_entry["kind"]
            for per_locale in preview.values()
            for locale_entry in per_locale.values()
        }
        assert kinds <= {"concept", "property", "vocabulary"}
