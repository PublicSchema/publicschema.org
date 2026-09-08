"""Farm is a production unit; holder responsibilities preserve typed subjects."""
import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")
AGRI = Namespace("https://publicschema.org/agri/")
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
            graph.add((URIRef(concept["uri"]), RDFS.subClassOf, URIRef(result["concepts"][parent]["uri"])))
    return graph


def test_farm_hierarchy_and_locked_membership_contracts(farm):
    result, _, _, _ = farm
    assert result["concepts"]["agri/Farm"]["supertypes"] == []
    properties = result["concept_schemas"]["agri/Farm"]["properties"]
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
    assert (AGRI.Farm, RDFS.subClassOf, PS.Group) not in graph


def test_optional_vocabulary_does_not_imply_complete_role(farm):
    result, _, _, registry = farm
    for kind in ("agri/Farm", "agri/PersonHoldingOperatorRole"):
        jsonschema.Draft202012Validator(result["concept_schemas"][kind], registry=registry).validate({})
    with pytest.raises(ValueError):
        _profile.validate_profile([{"@type": "agri/PersonHoldingOperatorRole"}])
    _profile.validate_profile([{"@type": "agri/Farm"}])


@pytest.mark.parametrize("case", ["software", "wrong_holding", "missing_target", "mixed_endpoints", "no_operator", "base_only", "reversed_dates"])
def test_profile_counterexamples(farm, case):
    _, _, original, _ = farm
    records = copy.deepcopy(original)
    role = next(r for r in records if r["@type"] == "agri/PersonHoldingOperatorRole")
    if case == "software":
        next(r for r in records if r["@id"] == role["holding_operator_person"])["@type"] = "SoftwareAgent"
    elif case == "wrong_holding":
        records.append({"@id": EX + "other", "@type": "agri/Farm"})
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
    role = next(r for r in records if r["@type"] == "agri/PersonHoldingOperatorRole")
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


@pytest.fixture(scope="module")
def workforce():
    return json.loads((ROOT / "examples/farm-operators/work-records.json").read_text())


def test_workforce_golden_json_schema_shacl_and_profile(farm, workforce):
    result, shapes, _, registry = farm
    for record in workforce:
        jsonschema.Draft202012Validator(
            result["concept_schemas"][record["@type"]], registry=registry,
            format_checker=jsonschema.FormatChecker(),
        ).validate(record)
    _profile.validate_profile(workforce)
    graph = graph_for(workforce, result)
    conforms, _, report = validate(graph, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
    for kind, endpoint in (("WorkRelationship", "work_economic_unit"),
                           ("agri/HoldingWorkAssignment", "assigned_holding")):
        properties = result["concept_schemas"][kind]["properties"]
        assert {endpoint, "work_person", "start_date", "end_date", "work_functions",
                "work_form", "work_status", "work_remuneration", "work_seasonality"} <= properties.keys()
        assert result["concepts"][kind]["maturity"] == "draft"
    for predicate in (PS.beneficiary, PS.recipient, PS.group):
        assert not list(graph.triples((None, predicate, None)))


def test_paid_unpaid_family_and_holder_management_are_independent(workforce):
    index = {r["@id"]: r for r in workforce}
    paid = index[EX + "amina-management"]
    assert paid["work_functions"][0]["code_value"] == "daily_management"
    assert paid["work_status"]["code_value"] == "employee"
    unpaid = index[EX + "unpaid-management"]
    assert unpaid["work_functions"][0]["code_value"] == "daily_management"
    assert unpaid["work_remuneration"]["code_value"] == "unpaid"
    assert "work_form" not in unpaid and "work_status" not in unpaid
    own_use = index[EX + "own-use-family-work"]
    market = index[EX + "market-family-work"]
    assert own_use["work_form"]["code_value"] == "own_use_production"
    assert market["work_form"]["code_value"] == "employment"
    assert market["work_status"]["code_value"] == "contributing_family_worker"
    assert market["work_remuneration"]["code_value"] == "no_regular_wage"
    assert market["work_seasonality"]["code_value"] == "seasonal"
    for record in (paid, unpaid, own_use, market):
        assert "assignment_work_relationship" not in record  # One participation record suffices.
    holder = index[EX + "person-role"]
    manager = index[EX + "holder-management"]
    assert holder["holding_operator_person"] == manager["work_person"]
    assert holder["operated_holding"] == manager["assigned_holding"]
    assert holder["start_date"] == "2025-01-01" and "end_date" not in holder
    assert "identifiers" not in index[manager["work_person"]]


def test_manager_handoff_uses_first_inactive_day_without_closing_holder(workforce):
    index = {r["@id"]: r for r in workforce}
    former = index[EX + "amina-management"]
    replacement = index[EX + "unpaid-management"]
    holder = copy.deepcopy(index[EX + "person-role"])
    assert former["end_date"] == replacement["start_date"] == "2025-07-01"

    def active(record, day):
        return record.get("start_date", day) <= day < record.get("end_date", "9999-12-31")

    assert active(former, "2025-06-30") and not active(replacement, "2025-06-30")
    assert not active(former, "2025-07-01") and active(replacement, "2025-07-01")
    _profile.validate_profile(workforce)
    assert index[EX + "person-role"] == holder
    assert all("valid_to" not in r and "valid_from" not in r for r in workforce)


def test_agency_and_contractor_keep_one_economic_relationship_across_two_holdings(workforce):
    for relationship_id, unit in (("agency-employment", "agency"),
                                  ("contractor-work", "contractor-enterprise")):
        relationships = [r for r in workforce if r["@id"] == EX + relationship_id]
        assert len(relationships) == 1
        relationship = relationships[0]
        assignments = [r for r in workforce if r.get("assignment_work_relationship") == relationship["@id"]]
        assert len(assignments) == 2
        assert {r["assigned_holding"] for r in assignments} == {EX + "holding", EX + "second-holding"}
        assert {r["work_person"] for r in assignments} == {relationship["work_person"]}
        assert relationship["work_economic_unit"] == EX + unit


@pytest.mark.parametrize("case", ["missing_person", "software_person", "missing_holding", "wrong_holding",
    "missing_relationship", "wrong_relationship", "different_person", "missing_unit", "wrong_unit",
    "missing_unit_field", "reversed_dates", "empty_interval", "invalid_date", "before_relationship",
    "after_relationship", "starts_on_cessation", "code_without_scheme"])
def test_work_profile_rejects_inconsistent_assertions(workforce, case):
    records = copy.deepcopy(workforce)
    assignment = next(r for r in records if r["@id"] == EX + "agency-river")
    relationship = next(r for r in records if r["@id"] == EX + "agency-employment")
    if case == "missing_person":
        del assignment["work_person"]
    elif case == "software_person":
        next(r for r in records if r["@id"] == assignment["work_person"])["@type"] = "SoftwareAgent"
    elif case == "missing_holding":
        assignment["assigned_holding"] = EX + "absent"
    elif case == "wrong_holding":
        assignment["assigned_holding"] = EX + "agency"
    elif case == "missing_relationship":
        assignment["assignment_work_relationship"] = EX + "absent"
    elif case == "wrong_relationship":
        assignment["assignment_work_relationship"] = EX + "person-role"
    elif case == "different_person":
        assignment["work_person"] = EX + "person"
    elif case == "missing_unit":
        relationship["work_economic_unit"] = EX + "absent"
    elif case == "wrong_unit":
        relationship["work_economic_unit"] = EX + "person"
    elif case == "missing_unit_field":
        del relationship["work_economic_unit"]
    elif case == "reversed_dates":
        assignment["end_date"] = "2025-04-01"
    elif case == "empty_interval":
        assignment["end_date"] = assignment["start_date"]
    elif case == "invalid_date":
        assignment["start_date"] = "2025-02-30"
    elif case == "before_relationship":
        assignment["start_date"] = "2024-12-31"
    elif case == "after_relationship":
        assignment["end_date"] = "2026-02-01"
    elif case == "starts_on_cessation":
        assignment["start_date"] = relationship["end_date"]
        del assignment["end_date"]
    else:
        del assignment["work_functions"][0]["code_scheme"]
    with pytest.raises(ValueError):
        _profile.validate_profile(records)


def test_partial_work_vocabulary_and_minimal_participation(farm):
    result, _, _, registry = farm
    for kind in ("WorkRelationship", "agri/HoldingWorkAssignment"):
        jsonschema.Draft202012Validator(result["concept_schemas"][kind], registry=registry).validate({})
        with pytest.raises(ValueError):
            _profile.validate_profile([{"@type": kind}])
    records = [{"@id": EX + "p", "@type": "Person"}, {"@id": EX + "h", "@type": "agri/Farm"},
               {"@type": "agri/HoldingWorkAssignment", "work_person": EX + "p", "assigned_holding": EX + "h"}]
    _profile.validate_profile(records)  # No classifications, dates, ID or second relationship required.


@pytest.mark.parametrize("field,target", [("work_person", "agency"), ("assigned_holding", "person"),
                                           ("assignment_work_relationship", "holding")])
def test_work_shacl_checks_typed_references(farm, workforce, field, target):
    result, shapes, _, _ = farm
    records = copy.deepcopy(workforce)
    next(r for r in records if r["@id"] == EX + "agency-river")[field] = EX + target
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]


def test_work_json_schema_rejects_non_uri_economic_unit_and_wrong_function_shape(farm):
    result, _, _, registry = farm
    for kind, record in (("WorkRelationship", {"work_economic_unit": {"@type": "Organization"}}),
                         ("agri/HoldingWorkAssignment", {"work_functions": "daily_management"})):
        validator = jsonschema.Draft202012Validator(result["concept_schemas"][kind], registry=registry)
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(record)


def test_farm_cannot_return_to_normative_membership(farm):
    result, shapes, original, _ = farm
    records = copy.deepcopy(original)
    membership = {"@type": "GroupMembership", "person": EX + "person", "group": EX + "holding", "role": "worker"}
    records.append(membership)
    with pytest.raises(ValueError):
        _profile.validate_profile(records)
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
    records.append({"@id": EX + "family", "@type": "Family"})
    membership["group"] = EX + "family"
    membership["role"] = "head"
    _profile.validate_profile(records)
    assert validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
    person_properties = result["concept_schemas"]["Person"]["properties"]
    assert "work_status" not in person_properties
    assert "employment_status" in person_properties and "status_in_employment" in person_properties


@pytest.mark.parametrize("unit_type", ["Household", "agri/Farm"])
def test_work_relationship_does_not_require_a_legal_employer(farm, unit_type):
    result, shapes, _, registry = farm
    records = [{"@id": EX + "p", "@type": "Person"},
               {"@id": EX + "unit", "@type": unit_type},
               {"@type": "WorkRelationship", "work_person": EX + "p", "work_economic_unit": EX + "unit"}]
    _profile.validate_profile(records)
    for record in records:
        jsonschema.Draft202012Validator(result["concept_schemas"][record["@type"]], registry=registry).validate(record)
    assert validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
