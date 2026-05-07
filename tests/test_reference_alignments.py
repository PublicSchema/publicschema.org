"""Tests for first-class external reference and alignment seed data."""

from pathlib import Path

import yaml

from tests.conftest import SCHEMA_DIR


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_semic_core_person_reference_is_pinned() -> None:
    ref = _load_yaml(SCHEMA_DIR / "external_references" / "semic-core-person.yaml")

    assert ref["id"] == "semic-core-person"
    assert ref["version"] == "2.1.1"
    assert ref["license"]["id"] == "CC-BY-4.0"
    assert ref["license"]["redistribution"] == "embed-with-attribution"
    artifacts = ref["artifacts"]
    assert artifacts
    assert all(item.get("sha256") for item in artifacts)
    assert all(item.get("retrieved_at") for item in artifacts)


def test_semic_core_business_and_location_references_are_pinned() -> None:
    expected = {
        "semic-core-business": {
            "version": "2.2.0",
            "sha256": "01c25a325e25843d616989c035c438695ea25e85790a3a6b058e471455a52069",
        },
        "semic-core-location": {
            "version": "2.1.1",
            "sha256": "adf51f8052ca3e12fee2cc57284b3671c413d49c4fd1a0d333c9ec1bb3f55a0c",
        },
    }

    for source_id, metadata in expected.items():
        ref = _load_yaml(SCHEMA_DIR / "external_references" / f"{source_id}.yaml")

        assert ref["id"] == source_id
        assert ref["version"] == metadata["version"]
        assert ref["license"]["id"] == "CC-BY-4.0"
        assert ref["base_eligibility"] == "base_eligible"
        assert ref["artifacts"][0]["sha256"] == metadata["sha256"]
        assert ref["artifacts"][0]["retrieved_at"] == "2026-05-07T00:00:00Z"


def test_publicschema_declares_explicit_native_base() -> None:
    base = _load_yaml(SCHEMA_DIR / "bases" / "active-base.yaml")

    assert base["base_strategy"] == "publicschema-native"
    assert base["primary_base"] == {
        "id": "publicschema",
        "reference_type": "local_project",
        "source_project_id": "publicschema",
    }
    assert base["base_pack"]["adoption_behavior"] == "adopt_all_owned_resources"


def test_semic_person_alignment_has_publicschema_assertion_owner() -> None:
    alignment_set = _load_yaml(SCHEMA_DIR / "alignments" / "semic-core-person.yaml")

    assert alignment_set["source_id"] == "semic-core-person"
    assert alignment_set["alignment_set_owner"] == "publicschema"
    assert alignment_set["maintainer"] == "publicschema-core-maintainers"
    assert alignment_set["standard"]["source_id"] == "semic-core-person"
    assert alignment_set["standard"]["source_sha256"]
    assert alignment_set["standard"]["retrieved_at"]

    by_id = {item["id"]: item for item in alignment_set["alignments"]}
    person = by_id["publicschema.Person--skos.exactMatch--person.Person"]
    assert person["subject"]["source_project_id"] == "publicschema"
    assert person["object"]["iri"] == "http://www.w3.org/ns/person#Person"
    assert person["predicate"] == "http://www.w3.org/2004/02/skos/core#exactMatch"
    assert person["quality"] == "exact"
    assert person["review_status"] == "accepted"
    assert person["license_snapshot"]["id"] == "CC-BY-4.0"


def test_semic_gender_alignment_is_property_only_not_value_crosswalk() -> None:
    alignment_set = _load_yaml(SCHEMA_DIR / "alignments" / "semic-core-person.yaml")
    by_id = {item["id"]: item for item in alignment_set["alignments"]}

    gender = by_id["publicschema.gender--skos.exactMatch--cv.gender"]
    assert gender["subject"]["id"] == "gender"
    assert gender["subject"]["kind"] == "property"
    assert gender["object"]["kind"] == "property"
    assert gender["mapping_level"] == "property"
    assert not any("gender-type" in item["id"] for item in alignment_set["alignments"])


def test_semic_external_terms_preserve_namespace_distinction() -> None:
    terms_doc = _load_yaml(SCHEMA_DIR / "external_terms" / "semic-core-person.yaml")
    by_id = {item["id"]: item for item in terms_doc["terms"]}

    person = by_id["person.Person"]
    assert person["source_module"] == "Core Person"
    assert person["namespace"] == "http://www.w3.org/ns/person#"
    assert person["prefix"] == "person"
    assert person["canonical_identity"] == {
        "iri": "http://www.w3.org/ns/person#Person",
        "defining_namespace": "http://www.w3.org/ns/person#",
        "namespace_owner": "W3C",
        "term_custodian": "W3C",
    }
    assert person["discovery"]["source_id"] == "semic-core-person"
    assert person["curation_source"]["custodian"] == "European Commission, SEMIC"
    assert person["term_custodian"] == "W3C"

    gender = by_id["cv.gender"]
    assert gender["namespace"] == "http://data.europa.eu/m8g/"
    assert gender["prefix"] == "cv"
    assert gender["canonical_identity"]["namespace_owner"] == "European Commission, SEMIC"
    assert gender["discovery"]["source_artifact_sha256"]


def test_semic_core_business_and_location_terms_preserve_authority_distinction() -> None:
    business = _load_yaml(SCHEMA_DIR / "external_terms" / "semic-core-business.yaml")
    business_terms = {item["id"]: item for item in business["terms"]}
    legal_entity = business_terms["legal.LegalEntity"]
    assert legal_entity["canonical_identity"]["namespace_owner"] == "European Commission, SEMIC"
    assert legal_entity["discovery"]["source_id"] == "semic-core-business"

    location = _load_yaml(SCHEMA_DIR / "external_terms" / "semic-core-location.yaml")
    location_terms = {item["id"]: item for item in location["terms"]}
    address = location_terms["locn.Address"]
    assert address["canonical_identity"]["namespace_owner"] == "W3C"
    assert address["discovery"]["source_id"] == "semic-core-location"


def test_semic_core_business_and_location_alignments_are_first_class() -> None:
    business = _load_yaml(SCHEMA_DIR / "alignments" / "semic-core-business.yaml")
    business_by_id = {item["id"]: item for item in business["alignments"]}
    assert business["source_id"] == "semic-core-business"
    assert business["standard"]["source_sha256"]
    assert business_by_id["publicschema.Organization--skos.closeMatch--legal.LegalEntity"][
        "object"
    ]["iri"] == "http://www.w3.org/ns/legal#LegalEntity"

    location = _load_yaml(SCHEMA_DIR / "alignments" / "semic-core-location.yaml")
    location_by_id = {item["id"]: item for item in location["alignments"]}
    assert location["source_id"] == "semic-core-location"
    assert location["standard"]["source_sha256"]
    assert location_by_id["publicschema.Address--skos.exactMatch--locn.Address"][
        "object"
    ]["iri"] == "http://www.w3.org/ns/locn#Address"
