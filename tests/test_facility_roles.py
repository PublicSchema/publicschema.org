"""Physical facility responsibilities and address changes survive production exports."""
import copy
import importlib.util
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
EX = "https://example.org/facility-roles/"
PS = Namespace("https://publicschema.org/")
_spec = importlib.util.spec_from_file_location("facility_profile", ROOT / "examples/facility-roles/validate_profile.py")
profile = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(profile)


@pytest.fixture(scope="module")
def records():
    return json.loads((ROOT / "examples/facility-roles/records.json").read_text())


@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    result = build_vocabulary(ROOT / "schema")
    shapes = Graph().parse(write_shacl(tmp_path_factory.mktemp("facility") / "shapes.ttl"), format="turtle")
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in result["concept_schemas"].values()
    )
    return result, shapes, registry


def graph_for(records, result):
    # Match the other quantity fixtures: PyLD converts numeric xsd:decimal values
    # to RDF lexical forms; RDFLib's direct JSON-LD parser retains Python int/float.
    quads = jsonld.to_rdf({"@context": result["context"]["@context"], "@graph": records},
                          {"format": "application/n-quads"})
    graph = Graph().parse(data=quads, format="nquads")
    for concept in result["concepts"].values():
        for parent in concept.get("supertypes", []):
            graph.add((URIRef(concept["uri"]), RDFS.subClassOf, URIRef(result["concepts"][parent]["uri"])))
    return graph


def schema_for(result, type_name):
    uri = result["context"]["@context"][type_name]
    return next(schema for schema in result["concept_schemas"].values() if schema["$id"] == uri + ".schema.json")


def test_real_json_schema_jsonld_and_shacl_exports(records, exports):
    result, shapes, registry = exports
    for record in records:
        jsonschema.Draft202012Validator(
            schema_for(result, record["@type"]), registry=registry,
            format_checker=jsonschema.FormatChecker(),
        ).validate(record)
    profile.validate_profile(records)
    graph = graph_for(records, result)
    conforms, _, report = validate(graph, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
    assert len(set(graph.subjects(RDF.type, PS.AssetPartyRole))) == 12
    assert len(set(graph.subjects(RDF.type, PS.AssetAddressAssignment))) == 5
    assert len(set(graph.subjects(RDF.type, PS.ServiceCapacityObservation))) == 2
    for subject, kind, measure, amount, observed_at in (
        ("school", "School", "staffed-learning-places", 160, "2026-09-01T08:00:00Z"),
        ("hospital", "HealthFacility", "staffed-beds", 42, "2026-09-01T09:00:00Z"),
    ):
        observation = URIRef(EX + subject + "-capacity")
        assert graph.value(observation, PS.capacity_subject) == URIRef(EX + subject)
        assert (URIRef(EX + subject), RDF.type, URIRef(result["context"]["@context"][kind])) in graph
        measure_node = graph.value(observation, PS.capacity_measure)
        assert graph.value(measure_node, PS.code_scheme) == URIRef(EX + "capacity-measures")
        assert graph.value(measure_node, PS.code_value) == Literal(measure)
        quantity_node = graph.value(observation, PS.capacity_quantity)
        assert graph.value(quantity_node, PS.quantity_value).toPython() == amount
        assert graph.value(quantity_node, PS.unit_code) == Literal("1")
        assert graph.value(quantity_node, PS.unit_scheme) == URIRef("http://unitsofmeasure.org")
        assert graph.value(observation, PS.capacity_observed_at).toPython() == datetime.fromisoformat(observed_at)
    for name in ("AssetPartyRole", "AssetAddressAssignment"):
        properties = result["concept_schemas"][name]["properties"]
        assert {"asset_subject", "start_date", "end_date"} <= properties.keys()
        assert not {"valid_from", "valid_to"} & properties.keys()
        assert result["concepts"][name]["maturity"] == "draft"
    assert result["properties"]["asset_actor"]["type"] == "uri"
    assert result["concepts"]["Organization"]["supertypes"] == ["Agent"]


@pytest.mark.parametrize("prefix,change_day", [
    ("school-operator", date(2026, 7, 1)),
    ("warehouse-operator", date(2026, 3, 1)),
    ("hospital-upkeep", date(2026, 9, 1)),
])
def test_responsibility_handoffs_preserve_one_physical_identity(records, prefix, change_day):
    index = {record["@id"]: record for record in records}
    before, after = (index[EX + prefix + suffix] for suffix in ("-before", "-after"))
    assert before["asset_subject"] == after["asset_subject"]
    assert before["asset_actor"] != after["asset_actor"]
    assert before["asset_role_type"] == after["asset_role_type"]
    assert before["end_date"] == after["start_date"] == change_day.isoformat()
    assert profile.effective_on(before, change_day - timedelta(days=1)) is True
    assert profile.effective_on(after, change_day - timedelta(days=1)) is False
    assert profile.effective_on(before, change_day) is False
    assert profile.effective_on(after, change_day) is True
    owners = [record for record in records if record.get("asset_subject") == before["asset_subject"]
              and record.get("asset_role_type", {}).get("code_value") == "owner"]
    assert len(owners) == 1 and "end_date" not in owners[0]


def test_owner_operator_upkeep_provider_and_holder_remain_independent(records):
    index = {record["@id"]: record for record in records}
    assert index[EX + "school-site"]["physical_service_point"] == EX + "school"
    assert index[EX + "school-site"]["education_provider"] == EX + "replacement-provider"
    assert "physical_service_point" not in index[EX + "online-site"]
    assert index[EX + "warehouse-owner"]["asset_actor"] == index[EX + "warehouse-upkeep"]["asset_actor"]
    assert index[EX + "warehouse-owner"]["@id"] != index[EX + "warehouse-upkeep"]["@id"]
    assert index[EX + "holder-role"]["operated_holding"] == EX + "holding"
    assert index[EX + "holder-role"]["holding_operator_person"] not in {
        index[EX + "warehouse-operator-before"]["asset_actor"],
        index[EX + "warehouse-operator-after"]["asset_actor"],
    }
    assert len({index[EX + name]["asset_actor"] for name in (
        "hospital-owner", "hospital-operator", "hospital-upkeep-after",
    )}) == 3
    # A simultaneous additional operator is representable; exclusivity needs source rules.
    concurrent = copy.deepcopy(index[EX + "hospital-operator"])
    concurrent.update({"@id": EX + "hospital-joint-operator", "asset_actor": EX + "replacement-provider"})
    profile.validate_profile(records + [concurrent])


def test_postal_changes_do_not_move_school_geometry_or_change_operator(records):
    index = {record["@id"]: record for record in records}
    physical = index[EX + "school-physical"]
    assert physical["address_geometry"] == EX + "school-position"
    for asset in ("school", "warehouse"):
        before, after = (index[EX + asset + suffix] for suffix in ("-postal-before", "-postal-after"))
        assert before["asset_subject"] == after["asset_subject"] == EX + asset
        assert before["assigned_address"] != after["assigned_address"]
        assert before["end_date"] == after["start_date"]
        assert before["address_purpose"] == after["address_purpose"]
        assert before["address_purpose"]["code_value"] == "postal"
        assert "address_geometry" not in before and "address_geometry" not in after
    assert index[EX + "school-postal-after"]["start_date"] != index[EX + "school-operator-after"]["start_date"]


@pytest.mark.parametrize("record_id,field,value,error", [
    ("school-owner", "asset_actor", EX + "online-site", "asset_actor"),
    ("school-owner", "asset_actor", EX + "nursery-group", "asset_actor"),
    ("school-owner", "asset_actor", EX + "absent", "unresolved"),
    ("school-owner", "asset_actor", "relative/person", "absolute"),
    ("school-owner", "asset_subject", EX + "online-site", "asset_subject"),
    ("school-owner", "asset_subject", EX + "school-provider", "asset_subject"),
    ("warehouse-owner", "asset_subject", EX + "holding", "asset_subject"),
    ("school-operator-before", "end_date", "2020-01-01", "at least one"),
    ("school-operator-before", "end_date", "2019-12-31", "at least one"),
    ("school-operator-before", "end_date", "2026-02-30", "impossible"),
    ("school-operator-before", "end_date", "2026-06", "YYYY-MM-DD"),
    ("school-operator-before", "valid_to", "2026-06-30", "legacy validity"),
    ("school-physical", "assigned_address", EX + "school-position", "assigned_address"),
    ("school-physical", "address_geometry", EX + "school-physical-address", "address_geometry"),
    ("school-physical", "asset_subject", EX + "online-site", "asset_subject"),
])
def test_profile_rejects_wrong_endpoints_and_periods(records, record_id, field, value, error):
    changed = copy.deepcopy(records)
    next(record for record in changed if record["@id"] == EX + record_id)[field] = value
    with pytest.raises(ValueError, match=error):
        profile.validate_profile(changed)


@pytest.mark.parametrize("record_id,field", [
    ("school-owner", "asset_actor"), ("school-owner", "asset_subject"),
    ("school-owner", "asset_role_type"), ("school-physical", "assigned_address"),
    ("school-physical", "address_purpose"),
])
def test_profile_requires_an_interpretable_assignment(records, record_id, field):
    changed = copy.deepcopy(records)
    del next(record for record in changed if record["@id"] == EX + record_id)[field]
    with pytest.raises(ValueError, match=field):
        profile.validate_profile(changed)


@pytest.mark.parametrize("record_id,field,part,value", [
    ("school-owner", "asset_role_type", "code_scheme", "https://example.org/unknown-scheme"),
    ("school-owner", "asset_role_type", "code_value", "manager"),
    ("school-physical", "address_purpose", "code_value", "unknown"),
    ("school-physical", "address_purpose", "code_scheme", "https://example.org/unknown-scheme"),
])
def test_role_and_address_codes_require_the_declared_meaning(records, record_id, field, part, value):
    changed = copy.deepcopy(records)
    next(record for record in changed if record["@id"] == EX + record_id)[field][part] = value
    with pytest.raises(ValueError, match=field):
        profile.validate_profile(changed)


def test_group_snapshot_does_not_widen_asset_actor_and_missing_dates_stay_unknown(records):
    index = {record["@id"]: record for record in records}
    assert index[EX + "nursery"]["facility_operator"] == EX + "nursery-group"
    profile.validate_profile(records)
    assert profile.effective_on(index[EX + "school-owner"], date(2026, 7, 1)) is None
    assert profile.effective_on({"end_date": "2026-07-01"}, date(2026, 7, 1)) is False
    assert profile.effective_on({"end_date": "2026-07-01"}, date(2026, 6, 30)) is None
    assert profile.effective_on({}, date(2026, 7, 1)) is None


def test_software_agent_cannot_take_a_facility_responsibility(records):
    changed = copy.deepcopy(records)
    next(record for record in changed if record["@id"] == EX + "maintenance")["@type"] = "SoftwareAgent"
    with pytest.raises(ValueError, match="asset_actor"):
        profile.validate_profile(changed)


def test_uri_shape_does_not_prove_subject_kind(records, exports):
    result, shapes, registry = exports
    changed = copy.deepcopy(records)
    role = next(record for record in changed if record["@id"] == EX + "school-owner")
    role["asset_actor"] = EX + "nursery-group"
    jsonschema.Draft202012Validator(result["concept_schemas"]["AssetPartyRole"], registry=registry).validate(role)
    assert validate(graph_for(changed, result), shacl_graph=shapes, inference="rdfs")[0]
    with pytest.raises(ValueError, match="asset_actor"):
        profile.validate_profile(changed)


def test_production_shacl_enforces_address_and_geometry_types(records, exports):
    result, shapes, _ = exports
    changed = copy.deepcopy(records)
    address = next(record for record in changed if record["@id"] == EX + "school-physical")
    address["assigned_address"] = EX + "school-position"
    assert not validate(graph_for(changed, result), shacl_graph=shapes, inference="rdfs")[0]
