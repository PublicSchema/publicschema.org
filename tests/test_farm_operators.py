"""Farm is a production unit; holder responsibilities preserve typed subjects."""
import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")
EX = "https://example.org/farm-pilot/"
_spec = importlib.util.spec_from_file_location("farm_profile", ROOT / "examples/farm-operators/validate_profile.py")
_profile = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_profile)


@pytest.fixture(scope="module")
def farm(tmp_path_factory):
    result = build_vocabulary(ROOT / "schema")
    shapes = Graph().parse(write_shacl(tmp_path_factory.mktemp("farm") / "shapes.ttl"), format="turtle")
    records = json.loads((ROOT / "examples/farm-operators/records.json").read_text())
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in result["concept_schemas"].values())
    return result, shapes, records, registry


def graph_for(records, result):
    graph = Graph().parse(data=json.dumps(jsonld.expand({"@context": result["context"]["@context"], "@graph": records})), format="json-ld")
    # Supply the authored hierarchy for references to abstract ranges.
    for concept in result["concepts"].values():
        for parent in concept.get("supertypes", []):
            graph.add((PS[concept["id"]], RDFS.subClassOf, PS[parent]))
    return graph


def test_farm_hierarchy_and_locked_membership_contracts(farm):
    result, _, _, _ = farm
    assert result["concepts"]["Farm"]["supertypes"] == []
    properties = result["concept_schemas"]["Farm"]["properties"]
    assert {"name", "identifiers", "holding_operator_roles"} <= properties.keys()
    assert not {"group_type", "memberships", "member_count", "identity_documents"} & properties.keys()
    assert result["properties"]["group"]["type"] == "concept:Group"
    assert result["properties"]["beneficiary"]["type"] == "concept:Party"
    assert result["concepts"]["Organization"]["supertypes"] == ["Agent"]


def test_real_exports_and_example_profile(farm):
    result, shapes, records, registry = farm
    for record in records:
        jsonschema.Draft202012Validator(result["concept_schemas"][record["@type"]], registry=registry).validate(record)
    _profile.validate_profile(records)
    graph = graph_for(records, result)
    assert validate(graph, shacl_graph=shapes, inference="rdfs")[0]
    assert not list(graph.triples((None, PS.beneficiary, None)))
    assert not list(graph.triples((None, PS.recipient, None)))
    person = next(r for r in records if r["@id"] == EX + "person")
    assert "identifiers" not in person
    assert (PS.Farm, RDFS.subClassOf, PS.Group) not in graph


def test_optional_vocabulary_does_not_imply_complete_role(farm):
    result, _, _, registry = farm
    for kind in ("Farm", "PersonHoldingOperatorRole"):
        jsonschema.Draft202012Validator(result["concept_schemas"][kind], registry=registry).validate({})
    with pytest.raises(ValueError):
        _profile.validate_profile([{"@type": "PersonHoldingOperatorRole"}])
    _profile.validate_profile([{"@type": "Farm"}])


@pytest.mark.parametrize("case", ["software", "wrong_holding", "missing_target", "mixed_endpoints", "no_operator", "base_only", "reversed_dates"])
def test_profile_counterexamples(farm, case):
    _, _, original, _ = farm
    records = copy.deepcopy(original)
    role = next(r for r in records if r["@type"] == "PersonHoldingOperatorRole")
    if case == "software":
        next(r for r in records if r["@id"] == role["holding_operator_person"])["@type"] = "SoftwareAgent"
    elif case == "wrong_holding":
        records.append({"@id": EX + "other", "@type": "Farm"})
        role["operated_holding"] = EX + "other"
    elif case == "missing_target":
        role["holding_operator_person"] = EX + "missing"
    elif case == "mixed_endpoints":
        role["holding_operator_organization"] = EX + "cooperative"
    elif case == "no_operator":
        del role["holding_operator_person"]
    elif case == "base_only":
        role["@type"] = "HoldingOperatorRole"
    else:
        role["end_date"] = "2020-01-01"
    with pytest.raises(ValueError):
        _profile.validate_profile(records)


def test_embedded_role_dispatch_and_partial_inverse(farm):
    _, _, original, _ = farm
    records = copy.deepcopy(original)
    holding = records[0]
    role = next(r for r in records if r["@type"] == "PersonHoldingOperatorRole")
    holding["holding_operator_roles"] = [role]
    records.remove(role)
    _profile.validate_profile(records)  # Other roles need not appear in the inverse list.
    role["holding_operator_person"] = {"@type": "Person", "name": "Local person"}
    _profile.validate_profile(records)
    role["holding_operator_person"] = {"@type": "SoftwareAgent", "name": "Scheduler"}
    with pytest.raises(ValueError):
        _profile.validate_profile(records)


def test_production_shacl_rejects_software_as_person(farm):
    result, shapes, original, _ = farm
    records = copy.deepcopy(original)
    next(r for r in records if r["@id"] == EX + "person")["@type"] = "SoftwareAgent"
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
