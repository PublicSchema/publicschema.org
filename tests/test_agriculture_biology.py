"""Biological identities and representative production-export boundaries."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")


@pytest.fixture(scope="module")
def biology(tmp_path_factory):
    result = build_vocabulary(ROOT / "schema")
    shapes = Graph().parse(write_shacl(tmp_path_factory.mktemp("biology") / "shapes.ttl"), format="turtle")
    records = json.loads((ROOT / "examples/agriculture-biology/records.json").read_text())
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema))
        for schema in result["concept_schemas"].values()
    )
    return result, shapes, records, registry


def graph_for(records, context):
    return Graph().parse(data=json.dumps(jsonld.expand({"@context": context["@context"], "@graph": records})), format="json-ld")


def test_all_families_export_and_keep_distinct_identity(biology):
    result, shapes, records, registry = biology
    for record in records:
        jsonschema.Draft202012Validator(result["concept_schemas"][record["@type"]], registry=registry).validate(record)
    for concept in {r["@type"] for r in records}:
        assert result["concepts"][concept]["maturity"] == "draft"
    linked_records = records + [
        {"@id": "https://example.org/farms/1", "@type": "Farm"},
        {"@id": "https://example.org/parcels/1", "@type": "AgriculturalParcel"},
        {"@id": "https://example.org/organizations/bank", "@type": "Organization"},
    ]
    data = graph_for(linked_records, result["context"])
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
    assert len(set(data.subjects(RDF.type, PS.SeedLot))) == 2
    assert len(set(data.subjects(RDF.type, PS.GeneticResourceAccession))) == 1
    assert len(set(data.subjects(RDF.type, PS.PlantVariety))) == 1
    assert len(list(data.triples((None, PS.planting_components, None)))) == 2
    assert len(list(data.triples((None, PS.known_animal_members, None)))) == 1
    assert (None, PS.animal_count, Literal(12)) in data
    assert not list(data.triples((None, PS.animal_birth_date, None)))
    assert not list(data.triples((None, PS.accession_collected_on, None)))
    assert (None, PS.collection_date_text, Literal("1990----")) in data


def test_primitive_counterexample_and_partial_vocabulary(biology):
    result, _, _, _ = biology
    schema = result["concept_schemas"]["AnimalGroupCount"]
    jsonschema.validate({}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"animal_count": "twelve"}, schema)


def test_count_submission_profile_is_separate_from_optional_vocabulary():
    profile = {"type": "object", "required": ["animal_count", "count_date"], "properties": {
        "animal_count": {"type": "integer", "minimum": 0},
        "count_date": {"type": "string", "format": "date"},
    }}
    validator = jsonschema.Draft202012Validator(profile, format_checker=jsonschema.FormatChecker())
    validator.validate({"animal_count": 0, "count_date": "2026-08-01"})
    for invalid in ({"animal_count": -1, "count_date": "2026-08-01"}, {"animal_count": 12},
                    {"animal_count": 12, "count_date": "2026-99-99"}):
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(invalid)


def test_shacl_rejects_variety_used_as_accession(biology):
    result, shapes, records, _ = biology
    selected = [copy.deepcopy(r) for r in records if r["@type"] in {"SeedLot", "PlantVariety", "GeneticResourceAccession"}]
    selected.append({"@id": "https://example.org/organizations/bank", "@type": "Organization"})
    data = graph_for(selected, result["context"])
    assert validate(data, shacl_graph=shapes, inference="rdfs")[0]
    next(r for r in selected if r["@type"] == "SeedLot")["seed_lot_accessions"] = ["https://example.org/varieties/1"]
    assert not validate(graph_for(selected, result["context"]), shacl_graph=shapes, inference="rdfs")[0]


def test_keeper_change_preserves_animal_residence_and_owner(biology):
    result, _, records, registry = biology
    data = graph_for(records, result["context"])
    residences = [r for r in records if r["@type"] == "AnimalResidence"]
    responsibilities = [r for r in records if r["@type"] == "AnimalResponsibility"]
    assert len(residences) == 1
    keepers = [r for r in responsibilities if r["animal_responsibility_role"]["code_value"] == "keeper"]
    owners = [r for r in responsibilities if r["animal_responsibility_role"]["code_value"] == "owner"]
    assert len(keepers) == 2 and len(owners) == 1
    assert keepers[0]["animal_responsible_actor"] != keepers[1]["animal_responsible_actor"]
    assert keepers[0]["valid_to"] < keepers[1]["valid_from"]
    assert len({r["animal_subject"] for r in responsibilities + residences}) == 1
    assert "valid_to" not in residences[0] and "valid_to" not in owners[0]
    assert len(list(data.triples((None, PS.animal_residence_site, None)))) == 1
    # Residence is neither a keeper assignment nor an ownership assertion.
    assert not list(data.triples((URIRef(residences[0]["@id"]), PS.animal_responsible_actor, None)))
    invalid = copy.deepcopy(keepers[0])
    invalid["animal_responsibility_role"] = 42
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            result["concept_schemas"]["AnimalResponsibility"], registry=registry,
        ).validate(invalid)
