"""Tests for build.extract_glossary."""

import json
from pathlib import Path

import yaml

from build import extract_glossary as eg
from build.loader import load_yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True))


def _make_concept(id: str = "Person", **kwargs) -> dict:
    data = {
        "id": id,
        "definition": {
            "en": f"A {id}.",
            "fr": f"Un {id}.",
            "es": f"Un {id}.",
        },
    }
    data.update(kwargs)
    return data


def _make_property(id: str = "name", **kwargs) -> dict:
    data = {
        "id": id,
        "definition": {
            "en": f"The {id} field.",
            "fr": f"Le champ {id}.",
            "es": f"El campo {id}.",
        },
    }
    data.update(kwargs)
    return data


def _make_vocabulary(id: str = "sex", values: list | None = None, **kwargs) -> dict:
    data = {
        "id": id,
        "definition": {
            "en": "A vocabulary.",
            "fr": "Un vocabulaire.",
            "es": "Un vocabulario.",
        },
        "values": values or [],
    }
    data.update(kwargs)
    return data


# ---------------------------------------------------------------------------
# _pick_labels / _pick_definition
# ---------------------------------------------------------------------------


class TestPickLabels:
    def test_returns_id_for_all_locales(self):
        entry = {"id": "Person"}
        result = eg._pick_labels(entry)
        assert result == {"en": "Person", "fr": "Person", "es": "Person"}


class TestPickDefinition:
    def test_extracts_all_locales(self):
        entry = {
            "definition": {"en": "A person.", "fr": "Une personne.", "es": "Una persona."}
        }
        result = eg._pick_definition(entry)
        assert result == {"en": "A person.", "fr": "Une personne.", "es": "Una persona."}

    def test_missing_locale_returns_empty_string(self):
        entry = {"definition": {"en": "A person."}}
        result = eg._pick_definition(entry)
        assert result["en"] == "A person."
        assert result["fr"] == ""
        assert result["es"] == ""

    def test_missing_definition_returns_empty_strings(self):
        result = eg._pick_definition({})
        assert result == {"en": "", "fr": "", "es": ""}

    def test_strips_whitespace(self):
        entry = {"definition": {"en": "  padded  ", "fr": "", "es": ""}}
        result = eg._pick_definition(entry)
        assert result["en"] == "padded"


# ---------------------------------------------------------------------------
# load_yaml / _load_all_yaml_with_paths
# ---------------------------------------------------------------------------


class TestLoadYaml:
    def test_loads_valid_yaml(self, tmp_path: Path):
        path = tmp_path / "test.yaml"
        _write_yaml(path, {"id": "hello", "value": 42})
        result = load_yaml(path)
        assert result == {"id": "hello", "value": 42}

    def test_empty_file_returns_empty_dict(self, tmp_path: Path):
        path = tmp_path / "empty.yaml"
        path.write_text("")
        result = load_yaml(path)
        assert result == {}


class TestLoadAllYaml:
    def test_loads_all_yaml_with_id(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        _write_yaml(tmp_path / "a.yaml", {"id": "alpha"})
        _write_yaml(tmp_path / "b.yaml", {"id": "beta"})
        result = eg._load_all_yaml_with_paths(tmp_path)
        assert len(result) == 2
        ids = {r["id"] for r in result}
        assert ids == {"alpha", "beta"}

    def test_skips_yaml_without_id(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        _write_yaml(tmp_path / "meta.yaml", {"name": "no-id"})
        _write_yaml(tmp_path / "good.yaml", {"id": "good"})
        result = eg._load_all_yaml_with_paths(tmp_path)
        assert len(result) == 1
        assert result[0]["id"] == "good"

    def test_nonexistent_directory_returns_empty(self, tmp_path: Path):
        result = eg._load_all_yaml_with_paths(tmp_path / "nope")
        assert result == []

    def test_adds_source_path(self, tmp_path: Path, monkeypatch):
        _write_yaml(tmp_path / "x.yaml", {"id": "x"})
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        result = eg._load_all_yaml_with_paths(tmp_path)
        assert result[0]["_source_path"] == "x.yaml"


# ---------------------------------------------------------------------------
# _extract_domain_terms
# ---------------------------------------------------------------------------


class TestExtractDomainTerms:
    def test_extracts_concept(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        _write_yaml(tmp_path / "concepts" / "person.yaml", _make_concept("Person"))
        (tmp_path / "properties").mkdir()
        (tmp_path / "vocabularies").mkdir()

        terms = eg._extract_domain_terms()
        concepts = [t for t in terms if t["kind"] == "concept"]
        assert len(concepts) == 1
        assert concepts[0]["id"] == "Person"
        assert concepts[0]["labels"]["en"] == "Person"

    def test_extracts_property(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        (tmp_path / "concepts").mkdir()
        _write_yaml(tmp_path / "properties" / "name.yaml", _make_property("name"))
        (tmp_path / "vocabularies").mkdir()

        terms = eg._extract_domain_terms()
        props = [t for t in terms if t["kind"] == "property"]
        assert len(props) == 1
        assert props[0]["id"] == "name"

    def test_extracts_vocabulary_and_values(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        (tmp_path / "concepts").mkdir()
        (tmp_path / "properties").mkdir()
        vocab = _make_vocabulary("sex", values=[
            {
                "code": "male",
                "label": {"en": "Male", "fr": "Masculin", "es": "Masculino"},
                "definition": {"en": "Male sex.", "fr": "Sexe masculin.", "es": "Sexo masculino."},
            },
        ])
        _write_yaml(tmp_path / "vocabularies" / "sex.yaml", vocab)

        terms = eg._extract_domain_terms()
        vocabs = [t for t in terms if t["kind"] == "vocabulary"]
        values = [t for t in terms if t["kind"] == "vocabulary_value"]
        assert len(vocabs) == 1
        assert vocabs[0]["id"] == "sex"
        assert len(values) == 1
        assert values[0]["id"] == "sex/male"
        assert values[0]["labels"]["fr"] == "Masculin"
        assert values[0]["definition"]["es"] == "Sexo masculino."

    def test_empty_schema_returns_empty(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        (tmp_path / "concepts").mkdir()
        (tmp_path / "properties").mkdir()
        (tmp_path / "vocabularies").mkdir()

        terms = eg._extract_domain_terms()
        assert terms == []


# ---------------------------------------------------------------------------
# OpenSPP glossary helpers
# ---------------------------------------------------------------------------


class TestOpensppLookup:
    def test_finds_in_terms(self):
        glossary = {"terms": {"cancel": {"en": "Cancel", "fr": "Annuler"}}}
        result = eg._openspp_lookup(glossary, "cancel")
        assert result == {"en": "Cancel", "fr": "Annuler"}

    def test_finds_in_ui_labels(self):
        glossary = {"ui_labels": {"search": {"en": "Search"}}}
        result = eg._openspp_lookup(glossary, "search")
        assert result["en"] == "Search"

    def test_finds_in_status_labels(self):
        glossary = {"status_labels": {"active": {"en": "Active"}}}
        result = eg._openspp_lookup(glossary, "active")
        assert result["en"] == "Active"

    def test_returns_none_when_missing(self):
        glossary = {"terms": {}}
        assert eg._openspp_lookup(glossary, "missing") is None

    def test_handles_empty_glossary(self):
        assert eg._openspp_lookup({}, "anything") is None


class TestLoadOpensppGlossary:
    def test_returns_empty_when_file_missing(self, monkeypatch):
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        result = eg._load_openspp_glossary()
        assert result == {}

    def test_loads_json_when_present(self, tmp_path: Path, monkeypatch):
        path = tmp_path / "glossary.json"
        path.write_text(json.dumps({"terms": {"hello": {"en": "Hello"}}}))
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", path)
        result = eg._load_openspp_glossary()
        assert result["terms"]["hello"]["en"] == "Hello"


# ---------------------------------------------------------------------------
# _build_ui_terms / _merge_ui_terms
# ---------------------------------------------------------------------------


class TestBuildUiTerms:
    def test_applies_overrides(self, monkeypatch):
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        terms = eg._build_ui_terms()
        by_key = {t["key"]: t for t in terms}
        # "home" has an override for fr and es
        assert by_key["home"]["fr"] == "Accueil"
        assert by_key["home"]["es"] == "Inicio"

    def test_uses_seed_en_when_no_override(self, monkeypatch):
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        terms = eg._build_ui_terms()
        by_key = {t["key"]: t for t in terms}
        assert by_key["search"]["en"] == "Search"

    def test_all_seed_keys_present(self, monkeypatch):
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        terms = eg._build_ui_terms()
        keys = {t["key"] for t in terms}
        assert keys == set(eg.UI_SEED_KEYS.keys())


class TestMergeUiTerms:
    def test_existing_translations_win(self):
        seeded = [{"key": "cancel", "en": "Cancel", "fr": "", "es": "", "context": ""}]
        existing = [{"key": "cancel", "en": "Cancel", "fr": "Annuler", "es": "Cancelar", "context": ""}]
        merged = eg._merge_ui_terms(seeded, existing)
        assert len(merged) == 1
        assert merged[0]["fr"] == "Annuler"
        assert merged[0]["es"] == "Cancelar"

    def test_seeded_fills_gaps(self):
        seeded = [{"key": "new_key", "en": "New", "fr": "Nouveau", "es": "Nuevo", "context": "test"}]
        existing = []
        merged = eg._merge_ui_terms(seeded, existing)
        assert len(merged) == 1
        assert merged[0]["key"] == "new_key"
        assert merged[0]["fr"] == "Nouveau"

    def test_preserves_hand_added_keys(self):
        seeded = [{"key": "a", "en": "A", "fr": "", "es": "", "context": ""}]
        existing = [
            {"key": "a", "en": "A", "fr": "Ax", "es": "As", "context": ""},
            {"key": "custom", "en": "Custom", "fr": "Perso", "es": "Pers", "context": "Hand-added"},
        ]
        merged = eg._merge_ui_terms(seeded, existing)
        keys = [m["key"] for m in merged]
        assert "a" in keys
        assert "custom" in keys
        assert len(merged) == 2


# ---------------------------------------------------------------------------
# build_glossary / write_glossary
# ---------------------------------------------------------------------------


class TestBuildGlossary:
    def test_output_structure(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        monkeypatch.setattr(eg, "GLOSSARY_PATH", tmp_path / "glossary.yaml")
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        (tmp_path / "concepts").mkdir()
        (tmp_path / "properties").mkdir()
        (tmp_path / "vocabularies").mkdir()

        result = eg.build_glossary()
        assert "_meta" in result
        assert "ui_terms" in result
        assert "domain_terms" in result
        assert result["_meta"]["locales"] == ["en", "fr", "es"]
        assert isinstance(result["_meta"]["domain_term_count"], int)
        assert isinstance(result["_meta"]["ui_term_count"], int)

    def test_counts_match_lists(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(eg, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(eg, "SCHEMA_DIR", tmp_path)
        monkeypatch.setattr(eg, "GLOSSARY_PATH", tmp_path / "glossary.yaml")
        monkeypatch.setattr(eg, "OPENSPP_GLOSSARY", None)
        (tmp_path / "concepts").mkdir()
        _write_yaml(tmp_path / "concepts" / "person.yaml", _make_concept("Person"))
        (tmp_path / "properties").mkdir()
        (tmp_path / "vocabularies").mkdir()

        result = eg.build_glossary()
        assert result["_meta"]["domain_term_count"] == len(result["domain_terms"])
        assert result["_meta"]["ui_term_count"] == len(result["ui_terms"])


class TestWriteGlossary:
    def test_creates_file(self, tmp_path: Path):
        data = {"_meta": {"test": True}, "ui_terms": [], "domain_terms": []}
        out = tmp_path / "out" / "glossary.yaml"
        eg.write_glossary(data, out)
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        assert loaded["_meta"]["test"] is True

    def test_creates_parent_dirs(self, tmp_path: Path):
        out = tmp_path / "deep" / "nested" / "glossary.yaml"
        eg.write_glossary({"_meta": {}}, out)
        assert out.exists()

    def test_roundtrip_unicode(self, tmp_path: Path):
        data = {"ui_terms": [{"key": "test", "fr": "Définition", "es": "Definición"}]}
        out = tmp_path / "glossary.yaml"
        eg.write_glossary(data, out)
        loaded = yaml.safe_load(out.read_text())
        assert loaded["ui_terms"][0]["fr"] == "Définition"
        assert loaded["ui_terms"][0]["es"] == "Definición"
