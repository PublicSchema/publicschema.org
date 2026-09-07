"""Qualified relationship examples through the real public exporters and local profile."""

import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
import yaml
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SH
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl, write_turtle

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/government-relationships"
EX = "https://example.org/government-relationships/"
PS = Namespace("https://publicschema.org/")
EDU = Namespace("https://publicschema.org/edu/")
ENVIRONMENT = Namespace("https://publicschema.org/environment/")
RECORDS = json.loads((EXAMPLES / "records.json").read_text())
CASES = json.loads((EXAMPLES / "negative-cases.json").read_text())
AUTHORED = yaml.safe_load((ROOT / "schema/government_relationships.yaml").read_text())
SPEC = importlib.util.spec_from_file_location("government_relationship_profile", EXAMPLES / "validate_profile.py")
PROFILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROFILE)


@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    built = build_vocabulary(ROOT / "schema")
    path = tmp_path_factory.mktemp("government-relationships")
    shapes = Graph().parse(write_shacl(path / "shapes.ttl"), format="turtle")
    ontology = Graph().parse(write_turtle(path / "vocabulary.ttl"), format="turtle")
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema))
        for schema in built["concept_schemas"].values()
    )
    return built, shapes, ontology, registry


def validator(exports, kind):
    built, _, _, registry = exports
    return jsonschema.Draft202012Validator(
        built["concept_schemas"][kind], registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )


def graph_for(records, exports):
    built, _, _, _ = exports
    expanded = jsonld.expand({"@context": built["context"]["@context"], "@graph": records})
    nquads = jsonld.to_rdf(expanded, {"format": "application/n-quads"})
    return Graph().parse(data=nquads, format="nquads")


def conforms(records, exports):
    _, shapes, ontology, _ = exports
    hierarchy = Graph()
    for triple in ontology.triples((None, RDFS.subClassOf, None)):
        hierarchy.add(triple)
    return validate(graph_for(records, exports), shacl_graph=shapes, ont_graph=hierarchy)


def record(records, suffix):
    return next(item for item in records if item["@id"] == EX + suffix)


def test_real_exports_preserve_qualified_relationships(exports):
    built, shapes, ontology, _ = exports
    for item in RECORDS:
        validator(exports, item["@type"]).validate(item)
    valid, _, report = conforms(RECORDS, exports)
    assert valid, report
    PROFILE.validate_profile(RECORDS)

    graph = graph_for(RECORDS, exports)
    assert (URIRef(EX + "north-offering"), EDU.offering_programme, URIRef(EX + "programme")) in graph
    assert (URIRef(EX + "boiler-release"), ENVIRONMENT.release_installation, URIRef(EX + "boiler")) in graph
    assert (URIRef(EX + "trust-control"), PS.interest_entity, URIRef(EX + "trust")) in graph
    assert (PS.LegalArrangement, RDFS.subClassOf, PS.Organization) not in ontology
    assert (PS.LegalArrangement, RDFS.subClassOf, PS.Party) not in ontology

    for definition in AUTHORED["classes"].values():
        uri = URIRef(definition["class_uri"].replace("publicschema:", str(PS)))
        assert (uri, RDF.type, OWL.Class) in ontology
        key = str(uri).removeprefix(str(PS))
        assert built["concepts"][key]["maturity"] == "draft"
        targets = list(shapes.subjects(SH.targetClass, uri))
        paths = {path for target in targets
                 for shape in shapes.objects(target, SH.property)
                 for path in shapes.objects(shape, SH.path)}
        for slot in definition["slots"]:
            assert slot in built["concept_schemas"][key]["properties"]
            assert URIRef(built["properties"][slot]["uri"]) in paths


@pytest.mark.parametrize("suffix,changes,rdf_conforms", [
    ("holding-shares", {"interest_exclusive_minimum_percentage": "more than twenty-five"}, False),
    ("north-offering", {"offering_sites": EX + "north-site"}, True),
    ("boiler-release", {"release_installation": True}, False),
])
def test_malformed_relationship_values_respect_each_public_format(exports, suffix, changes, rdf_conforms):
    records = copy.deepcopy(RECORDS)
    changed = record(records, suffix)
    changed.update(changes)
    assert list(validator(exports, changed["@type"]).iter_errors(changed))
    assert conforms(records, exports)[0] is rdf_conforms
    if rdf_conforms:
        # JSON array form is a serialization rule. RDF preserves the same single
        # site relationship and cannot distinguish a scalar from a one-item array.
        assert (URIRef(EX + suffix), EDU.offering_sites, URIRef(EX + "north-site")) in graph_for(records, exports)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_documented_profile_counterexamples(case):
    with pytest.raises(ValueError, match=case["expected"]):
        PROFILE.validate_profile(PROFILE.apply_case(RECORDS, case))


def test_scope_queries_do_not_infer_approval_or_beneficial_ownership():
    PROFILE.validate_profile(RECORDS)
    index = PROFILE.index_records(RECORDS)
    ordered = PROFILE.ownership_route(record(RECORDS, "claimed-route"), index)
    assert ordered == [EX + "trust-control", EX + "trust-shares", EX + "holding-shares"]
    indirect = record(RECORDS, "indirect-control")
    assert "interest_percentage" not in indirect
    assert not any(key in indirect for key in PROFILE.BOUNDS)

    offerings = [item for item in RECORDS if item["@type"] == "edu/EducationOffering"
                 and item["offering_programme"] == EX + "programme"]
    recognized = {item["registered_subject"] for item in RECORDS if item["@type"] == "Registration"}
    assert len(offerings) == 2
    assert {item["@id"] for item in offerings} & recognized == {EX + "north-offering"}
    assert record(RECORDS, "north-offering")["offering_award"] == record(RECORDS, "online-offering")["offering_award"]
    releases = {item["release_installation"]: item["release_quantity"]["quantity_value"]
                for item in RECORDS if item["@type"] == "environment/EnvironmentalRelease"}
    assert releases == {EX + "boiler": 12, EX + "furnace": 7}


@pytest.mark.parametrize("changes", [
    {"interest_minimum_percentage": 0},
    {"interest_maximum_percentage": 100},
    {"interest_exclusive_maximum_percentage": 50},
    {"interest_minimum_percentage": 25, "interest_maximum_percentage": 25},
    {"interest_percentage": 0},
    {},
])
def test_unknown_one_sided_exact_and_inclusive_bounds_are_preserved(changes):
    records = copy.deepcopy(RECORDS)
    changed = record(records, "holding-shares")
    for key in PROFILE.BOUNDS:
        changed.pop(key, None)
    changed.update(changes)
    before = copy.deepcopy(records)
    PROFILE.validate_profile(records)
    assert records == before
    assert {key for key in PROFILE.BOUNDS if key in changed} == set(changes) - {"interest_percentage"}


@pytest.mark.parametrize("changes", [
    {"interest_minimum_percentage": -1},
    {"interest_maximum_percentage": 101},
    {"interest_exclusive_minimum_percentage": 100},
    {"interest_exclusive_maximum_percentage": 0},
    {"interest_percentage": True},
    {"interest_percentage": float("nan")},
])
def test_impossible_percentages_fail_the_profile(changes):
    records = copy.deepcopy(RECORDS)
    changed = record(records, "holding-shares")
    for key in PROFILE.BOUNDS:
        changed.pop(key, None)
    changed.update(changes)
    with pytest.raises(ValueError):
        PROFILE.validate_profile(records)


def test_components_with_unknown_primary_dates_still_need_a_common_day():
    records = copy.deepcopy(RECORDS)
    primary = record(records, "indirect-control")
    primary.pop("start_date")
    primary.pop("end_date")
    record(records, "trust-control")["end_date"] = "2026-01-01"
    record(records, "holding-shares")["start_date"] = "2026-01-01"
    with pytest.raises(ValueError, match="no common effective day"):
        PROFILE.validate_profile(records)


@pytest.mark.parametrize("case,expected", [
    ("cycle", "contain a cycle"),
    ("duplicate", "duplicate components"),
    ("primary", "primary interest"),
])
def test_route_components_cannot_repeat_or_refer_to_the_primary(case, expected):
    records = copy.deepcopy(RECORDS)
    chain = record(records, "claimed-route")
    if case == "cycle":
        record(records, "holding-shares")["interest_entity"] = EX + "trust"
    elif case == "duplicate":
        chain["component_interests"].append(chain["component_interests"][0])
    else:
        chain["component_interests"].append(chain["indirect_interest"])
    with pytest.raises(ValueError, match=expected):
        PROFILE.validate_profile(records)


def test_facility_total_and_installation_only_release_both_preserve_source_granularity():
    for removed in ("release_installation", "release_facility"):
        records = copy.deepcopy(RECORDS)
        record(records, "boiler-release").pop(removed)
        PROFILE.validate_profile(records)
        assert removed not in record(records, "boiler-release")


def test_optional_reference_shapes_do_not_assert_complete_exchange(exports):
    for kind in ("LegalArrangement", "OwnershipChainAssertion", "edu/EducationOffering"):
        partial = {"@id": EX + "partial", "@type": kind}
        validator(exports, kind).validate(partial)
        with pytest.raises(ValueError):
            PROFILE.validate_profile([partial])
