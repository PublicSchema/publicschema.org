"""Structural invariants of the registry foundation, value type and physical asset terms."""
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULES = ("value_types", "registry", "physical_assets")


@pytest.fixture(scope="module")
def result(built_vocabulary):
    return built_vocabulary


@pytest.fixture(scope="module")
def registry(schema_registry):
    return schema_registry


CLOSED_ENUMS = {
    "evidence_role": ("evidence-role", {"supports", "contradicts"}),
    "contact_channel": ("contact-channel", {"phone", "fax", "email", "pager", "url", "sms", "other"}),
    "geometry_encoding": ("geometry-encoding", {"geojson", "wkt", "gml", "kml"}),
    "unit_scheme": ("unit-system", {"ucum", "unece_rec20"}),
    "match_outcome": ("match-outcome", {"match", "possible_match", "non_match"}),
    "record_change_kind": ("record-change-kind", {"invalidation", "retirement", "supersession"}),
}


@pytest.mark.parametrize("slot", sorted(CLOSED_ENUMS))
def test_small_standard_lists_are_closed_vocabularies(result, slot):
    vocabulary, codes = CLOSED_ENUMS[slot]
    prop = result["properties"][slot]
    assert prop["vocabulary"] == vocabulary
    assert prop["type"] == "string"
    assert {value["code"] for value in result["vocabularies"][vocabulary]["values"]} == codes
    assert result["vocabularies"][vocabulary]["domain"] is None


@pytest.mark.parametrize("class_name,slot,valid,invalid", [
    ("EvidenceAssertion", "evidence_role", "supports", "refutes"),
    ("ContactPoint", "contact_channel", "sms", "telephone"),
    ("SpatialGeometry", "geometry_encoding", "geojson", "application/geo+json"),
    ("QuantityValue", "unit_scheme", "ucum", "http://unitsofmeasure.org"),
    ("SubjectMatchAssertion", "match_outcome", "possible_match", "maybe"),
    ("RecordLifecycleEvent", "record_change_kind", "retirement", "deletion"),
])
def test_closed_vocabularies_reject_unlisted_codes(result, registry, class_name, slot, valid, invalid):
    validator = jsonschema.Draft202012Validator(result["concept_schemas"][class_name], registry=registry)
    validator.validate({slot: valid})
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({slot: invalid})


@pytest.mark.parametrize("slot", [
    "asset_subject", "named_subject", "contact_subject", "identifier_subject",
    "evidence_authority", "match_authority", "maintaining_authority",
    "address_geometry", "building_addresses",
])
def test_merged_and_dropped_slots_stay_removed(result, slot):
    assert slot not in result["properties"]
    assert slot not in result["context"]["@context"]


def test_statements_about_a_subject_share_subject_uri(result):
    prop = result["properties"]["subject_uri"]
    assert prop["type"] == "uri"
    assert prop["sensitivity"] is None
    assert {
        "RegistryEntry", "RecordReference", "IdentifierAssignment", "NameUsage",
        "ContactPoint", "AssetPartyRole", "AssetAddressAssignment",
    } <= set(prop["used_by"])
    assert "RecordLifecycleEvent" not in prop["used_by"]


def test_accountable_organization_is_one_attribution_slot(result):
    prop = result["properties"]["assertion_authority"]
    assert prop["type"] == "concept:Organization"
    assert set(prop["used_by"]) == {"EvidenceAssertion", "SubjectMatchAssertion"}
    assert prop["external_equivalents"]["prov"]["uri"] == "http://www.w3.org/ns/prov#wasAttributedTo"
    owner = result["properties"]["register_owner"]
    assert owner["type"] == "concept:Organization"
    assert owner["used_by"] == ["Register"]


def test_record_lifecycle_event_is_an_event_about_a_record(result):
    concept = result["concepts"]["RecordLifecycleEvent"]
    assert concept["supertypes"] == ["Event"]
    slots = {entry["id"] for entry in concept["properties"]}
    assert {"affected_record", "record_change_kind", "authority"} <= slots
    assert not {"subject_uri", "lifecycle_kind", "event_authority", "assertion_authority"} & slots
    assert result["properties"]["affected_record"]["type"] == "concept:RecordReference"


def test_register_references_carry_the_sensitive_signal(result):
    for slot in ("register_uri", "registered_subject"):
        assert result["properties"][slot]["sensitivity"] == "sensitive"


def test_asset_actor_admits_groups_by_definition(result):
    prop = result["properties"]["asset_actor"]
    assert prop["type"] == "uri"
    assert "group" in prop["definition"]["en"]


def test_spatial_geometry_aligns_with_geosparql_and_core_location(result):
    equivalents = result["properties"]["spatial_geometry"]["external_equivalents"]
    uris = {entry["uri"] for entry in equivalents.values()}
    assert {"http://www.opengis.net/ont/geosparql#hasGeometry", "http://www.w3.org/ns/locn#geometry"} <= uris


BANNED_PHRASES = (
    "scheme-qualified", "consuming profile", "draft covers", "review brief", "starter",
    "registrystack", "registry stack", "this branch", "array position",
)


@pytest.mark.parametrize("module", MODULES)
def test_definitions_contain_no_process_language(module):
    authored = yaml.safe_load((ROOT / f"schema/{module}.yaml").read_text())
    texts = [authored.get("description", "")]
    for section in ("classes", "slots"):
        for definition in (authored.get(section) or {}).values():
            texts.append(definition.get("description", ""))
            alignments = (definition.get("annotations") or {}).get("external_alignments_json")
            if alignments:
                texts.extend(item.get("note", "") for item in json.loads(alignments))
    for text in texts:
        lowered = text.lower()
        assert not [phrase for phrase in BANNED_PHRASES if phrase in lowered], text
        assert "—" not in text


@pytest.mark.parametrize("module", MODULES)
def test_native_mappings_and_rich_alignments_agree(module):
    authored = yaml.safe_load((ROOT / f"schema/{module}.yaml").read_text())
    prefixes = authored["prefixes"]
    for section in ("classes", "slots"):
        for name, definition in (authored.get(section) or {}).items():
            native = set()
            for key in ("exact_mappings", "close_mappings"):
                for curie in definition.get(key) or []:
                    prefix, local = curie.split(":", 1)
                    native.add((key.split("_")[0], prefixes[prefix] + local))
            raw = (definition.get("annotations") or {}).get("external_alignments_json")
            rich = {(item["match"], item["uri"]) for item in json.loads(raw)} if raw else set()
            assert native == rich, name


@pytest.mark.parametrize("enum", [
    "EvidenceRole", "ContactChannel", "GeometryEncoding", "UnitSystem", "MatchOutcome", "RecordChangeKind",
])
def test_vocabulary_mappings_and_rich_alignments_agree(enum):
    definition = yaml.safe_load((ROOT / "schema/vocabularies.yaml").read_text())["enums"][enum]
    native = {
        (key.split("_")[0], uri)
        for key in ("exact_mappings", "close_mappings")
        for uri in definition.get(key) or []
    }
    raw = (definition.get("annotations") or {}).get("external_alignments_json")
    rich = {(item["match"], item["uri"]) for item in json.loads(raw)} if raw else set()
    assert native == rich
