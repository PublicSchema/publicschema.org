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


COMPLETE_VALUES = {
    "SpatialGeometry": {"geometry_literal": "POINT (1 2)", "geometry_encoding": "wkt"},
    "QuantityValue": {"quantity_value": 2, "unit_code": "ha", "unit_scheme": "unece_rec20"},
}


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
    base = COMPLETE_VALUES.get(class_name, {})
    validator.validate({**base, slot: valid})
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({**base, slot: invalid})


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


@pytest.mark.parametrize("slot", [
    "holder_person", "work_person", "role_actor", "asset_actor", "interest_holder",
    "tenure_holder", "animal_responsible_actor", "matched_subject", "registered_subject",
])
def test_links_naming_the_party_behind_a_role_or_match_are_sensitive(result, slot):
    # Each of these ties a person to a holding, job, asset, interest or record.
    assert result["properties"][slot]["sensitivity"] == "sensitive"


def test_asset_actor_admits_groups_by_definition(result):
    prop = result["properties"]["asset_actor"]
    assert prop["type"] == "uri"
    assert "group" in prop["definition"]["en"]


def test_spatial_geometry_aligns_with_geosparql_and_core_location(result):
    equivalents = result["properties"]["spatial_geometry"]["external_equivalents"]
    uris = {entry["uri"] for entry in equivalents.values()}
    assert {"http://www.opengis.net/ont/geosparql#hasGeometry", "http://www.w3.org/ns/locn#geometry"} <= uris


@pytest.mark.parametrize("language,literal,agree", [
    ("en", "geometry literal", "must agree"),
    ("fr", "littéral géométrique", "concorder"),
    ("es", "literal geométrico", "coincidir"),
])
def test_an_absent_crs_defers_to_the_literal_before_crs84(result, language, literal, agree):
    # A WKT literal can state its own reference system; CRS84 applies only when neither does.
    definition = result["properties"]["coordinate_reference_system"]["definition"][language]
    assert literal in definition and agree in definition
    assert definition.index(literal) < definition.index("CRS84")


def test_building_aligns_with_the_inspire_feature_concept(result):
    equivalents = result["concepts"]["Building"]["external_equivalents"]
    assert "http://inspire.ec.europa.eu/featureconcept/Building" in {entry["uri"] for entry in equivalents.values()}

@pytest.mark.parametrize("slot", ["registration_purpose", "authorized_activity", "contact_purpose"])
def test_free_text_purposes_say_they_are_text(result, slot):
    prop = result["properties"][slot]
    assert prop["type"] == "string"
    assert "stated as text" in prop["definition"]["en"]

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
                    uri = curie if local.startswith("//") else prefixes[prefix] + local
                    native.add((key.split("_")[0], uri))
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


@pytest.mark.parametrize("section,term,counterpart", [
    ("properties", "authority", "issuing_authority"),
    ("properties", "effective_at", "effective_date"),
    ("properties", "legal_resources", "legal_basis"),
    ("properties", "service_applicant", "applicant"),
    ("concepts", "ContactPoint", "phone_number"),
    ("concepts", "NameUsage", "given_name"),
    ("concepts", "AdministrativeDecision", "EligibilityDecision"),
    ("concepts", "AdministrativeAppeal", "Grievance"),
])
def test_terms_near_an_existing_term_point_to_it(result, section, term, counterpart):
    definition = result[section][term]["definition"]
    for language in ("en", "fr", "es"):
        assert counterpart in definition[language], language


def test_legal_resources_align_with_cpsv_ap(result):
    uris = {entry["uri"] for entry in result["properties"]["legal_resources"]["external_equivalents"].values()}
    assert "http://data.europa.eu/m8g/hasLegalResource" in uris


VALUE_TYPES = {
    "CodedValue": {"code_value", "code_scheme"},
    "QuantityValue": {"quantity_value", "unit_code", "unit_scheme"},
    "SpatialGeometry": {"geometry_literal", "geometry_encoding"},
}


@pytest.mark.parametrize("class_name", sorted(VALUE_TYPES))
def test_value_types_require_the_fields_that_define_them(result, registry, class_name):
    # A code without its scheme, or an amount without its unit, has no meaning.
    schema = result["concept_schemas"][class_name]
    assert set(schema["required"]) == VALUE_TYPES[class_name]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema, registry=registry).validate({})


@pytest.mark.parametrize("slot,class_name", [("decision_outcome", "CodedValue"), ("capacity_quantity", "QuantityValue")])
def test_codes_and_quantities_are_inline_only_in_json_schema(result, slot, class_name):
    # A code or an amount has no identity of its own, so a reference string cannot stand for it.
    item = result["concept_schemas"][result["properties"][slot]["used_by"][0]]["properties"][slot]
    item = item.get("items", item)
    assert "oneOf" not in item and item["$ref"].endswith(f"/{class_name}.schema.json")


@pytest.mark.parametrize("class_name", ["CodedValue", "QuantityValue"])
def test_codes_and_quantities_are_checked_as_nodes_in_shacl(shacl_graph, class_name):
    from rdflib import URIRef
    from rdflib.namespace import SH
    target = URIRef(f"https://publicschema.org/{class_name}")
    assert not list(shacl_graph.subjects(SH["class"], target))
    assert list(shacl_graph.subjects(SH.node, target))


def test_a_geometry_can_be_an_identified_shared_resource(result):
    # As in GeoSPARQL, one identified geometry can represent several features.
    item = result["concept_schemas"]["Building"]["properties"]["spatial_geometry"]["items"]
    assert item["oneOf"][1]["type"] == "string"
