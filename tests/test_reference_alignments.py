"""Tests for SEMIC reference metadata in the authored LinkML source."""

import yaml

from tests.conftest import SCHEMA_DIR
from tests.schema_reader import bibliography, concept, property_, vocabulary


def _load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_composite_imports_semic_reference_schemas() -> None:
    composite = _load_yaml(SCHEMA_DIR / "publicschema.yaml")

    assert "external/semic" in composite["imports"]
    assert "external/semic-core-person" in composite["imports"]
    assert "external/semic-core-business" in composite["imports"]
    assert "external/semic-core-location" in composite["imports"]


def test_semic_bibliography_entries_are_active_eu_vocabularies() -> None:
    expected = {
        "semic-core-person": "v2.1.1",
        "semic-core-business": "v2.2.0",
        "semic-core-location": "v2.1.1",
    }

    for source_id, version in expected.items():
        ref = bibliography(source_id)
        assert ref["version"] == version
        assert ref["type"] == "eu_vocabulary"
        assert ref["access"] == "open"
        assert ref["status"] == "active"
        assert ref["uri"].startswith("https://semiceu.github.io/")


def test_semic_person_alignment_is_authored_on_person_concept() -> None:
    ext = concept("Person")["external_equivalents"]["semic"]

    assert ext["label"] == "Person"
    assert ext["uri"] == "http://www.w3.org/ns/person#Person"
    assert ext["match"] == "exact"
    assert ext["vocabulary"] == "Core Person"


def test_semic_gender_alignment_is_property_alignment() -> None:
    ext = property_("gender")["external_equivalents"]["semic"]

    assert ext["label"] == "gender"
    assert ext["uri"] == "http://data.europa.eu/m8g/gender"
    assert ext["match"] == "exact"
    assert ext["vocabulary"] == "Core Person"


def test_semic_gender_type_remains_vocabulary_level_only() -> None:
    ext = vocabulary("gender-type")["external_equivalents"]["semic"]

    assert ext["label"] == "Gender"
    assert ext["uri"] == "http://data.europa.eu/m8g/gender"
    assert ext["match"] == "broad"
    assert "leaving the choice to implementers" in ext["note"]


def test_semic_business_and_location_alignments_are_authored() -> None:
    organization = concept("Organization")["external_equivalents"]["semic"]
    address = concept("Address")["external_equivalents"]["semic"]

    assert organization["label"] == "Public Organisation"
    assert organization["uri"] == "http://data.europa.eu/m8g/PublicOrganisation"
    assert organization["match"] == "close"

    assert address["label"] == "Address"
    assert address["uri"] == "http://www.w3.org/ns/locn#Address"
    assert address["match"] == "exact"
