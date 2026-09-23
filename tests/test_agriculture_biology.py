"""Biological identities and representative production-export boundaries."""
import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")
AGRI = Namespace("https://publicschema.org/agri/")
PROFILE_SPEC = importlib.util.spec_from_file_location(
    "movement_profile", ROOT / "examples/agriculture-biology/validate_movement_profile.py",
)
movement_profile = importlib.util.module_from_spec(PROFILE_SPEC)
PROFILE_SPEC.loader.exec_module(movement_profile)


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


def graph_for(records, result):
    graph = Graph().parse(data=json.dumps(jsonld.expand({
        "@context": result["context"]["@context"], "@graph": records,
    })), format="json-ld")
    # SHACL class ranges need the export's subclass hierarchy alongside the data.
    for concept in result["concepts"].values():
        for parent in concept.get("supertypes", []):
            graph.add((URIRef(concept["uri"]), RDFS.subClassOf, URIRef(result["concepts"][parent]["uri"])))
    return graph


LINKED_TARGETS = [
    {"@id": "https://example.org/farms/1", "@type": "agri/Farm"},
    {"@id": "https://example.org/parcels/1", "@type": "agri/AgriculturalParcel"},
    {"@id": "https://example.org/facilities/1", "@type": "agri/AgriculturalFacility"},
    {"@id": "https://example.org/organizations/bank", "@type": "Organization"},
    {"@id": "https://example.org/organizations/breed-society", "@type": "Organization"},
    {"@id": "https://example.org/people/keeper-a", "@type": "Person"},
    {"@id": "https://example.org/people/keeper-b", "@type": "Person"},
    {"@id": "https://example.org/people/owner", "@type": "Person"},
]


@pytest.fixture(scope="module")
def movement_records():
    return json.loads((ROOT / "examples/agriculture-biology/movement-records.json").read_text())


def test_all_families_export_and_keep_distinct_identity(biology):
    result, shapes, records, registry = biology
    for record in records:
        jsonschema.Draft202012Validator(result["concept_schemas"][record["@type"]], registry=registry).validate(record)
    for concept in {r["@type"] for r in records}:
        assert result["concepts"][concept]["maturity"] == "draft"
    linked_records = records + LINKED_TARGETS
    data = graph_for(linked_records, result)
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
    assert len(set(data.subjects(RDF.type, PS.SeedLot))) == 2
    assert len(set(data.subjects(RDF.type, PS.GeneticResourceAccession))) == 1
    assert len(set(data.subjects(RDF.type, PS.PlantVariety))) == 1
    assert len(list(data.triples((None, AGRI.planting_components, None)))) == 2
    assert len(list(data.triples((None, PS.known_animal_members, None)))) == 1
    assert (None, PS.animal_count, Literal(12)) in data
    # Reduced-precision dates keep only their known parts.
    assert (None, PS.animal_birth_date, Literal("2021")) in data
    assert (None, PS.accession_collection_date, Literal("1990")) in data


def test_primitive_counterexample_and_partial_vocabulary(biology):
    result, _, _, _ = biology
    schema = result["concept_schemas"]["AnimalGroupCount"]
    jsonschema.validate({}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"animal_count": "twelve"}, schema)
    jsonschema.validate({"animal_count": 0}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"animal_count": -1}, schema)


def test_count_submission_profile_is_separate_from_optional_vocabulary():
    profile = {"type": "object", "required": ["animal_count", "animal_count_date"], "properties": {
        "animal_count": {"type": "integer", "minimum": 0},
        "animal_count_date": {"type": "string", "format": "date"},
    }}
    validator = jsonschema.Draft202012Validator(profile, format_checker=jsonschema.FormatChecker())
    validator.validate({"animal_count": 0, "animal_count_date": "2026-08-01"})
    for invalid in ({"animal_count": -1, "animal_count_date": "2026-08-01"}, {"animal_count": 12},
                    {"animal_count": 12, "animal_count_date": "2026-99-99"}):
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(invalid)


def test_shacl_rejects_variety_used_as_accession(biology):
    result, shapes, records, _ = biology
    selected = [copy.deepcopy(r) for r in records if r["@type"] in {"SeedLot", "PlantVariety", "GeneticResourceAccession"}]
    selected.append({"@id": "https://example.org/organizations/bank", "@type": "Organization"})
    data = graph_for(selected, result)
    assert validate(data, shacl_graph=shapes, inference="rdfs")[0]
    next(r for r in selected if r["@type"] == "SeedLot")["seed_lot_accessions"] = ["https://example.org/varieties/1"]
    assert not validate(graph_for(selected, result), shacl_graph=shapes, inference="rdfs")[0]


def test_keeper_change_preserves_animal_residence_and_owner(biology):
    result, _, records, registry = biology
    data = graph_for(records, result)
    residences = [r for r in records if r["@type"] == "agri/AnimalResidence"]
    responsibilities = [r for r in records if r["@type"] == "AnimalResponsibility"]
    assert len(residences) == 1
    keepers = [r for r in responsibilities if r["animal_responsibility_role"]["code_value"] == "keeper"]
    owners = [r for r in responsibilities if r["animal_responsibility_role"]["code_value"] == "owner"]
    assert len(keepers) == 2 and len(owners) == 1
    assert keepers[0]["animal_responsible_actor"] != keepers[1]["animal_responsible_actor"]
    assert keepers[0]["end_date"] == keepers[1]["start_date"]
    assert len({r["animal_subject"] for r in responsibilities + residences}) == 1
    assert "end_date" not in residences[0] and "end_date" not in owners[0]
    assert len(list(data.triples((None, AGRI.animal_residence_site, None)))) == 1
    assert not list(data.subjects(RDF.type, PS.AnimalMovement))
    # Residence is neither a keeper assignment nor an ownership assertion.
    assert not list(data.triples((URIRef(residences[0]["@id"]), PS.animal_responsible_actor, None)))
    invalid = copy.deepcopy(keepers[0])
    invalid["animal_responsibility_role"] = 42
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            result["concept_schemas"]["AnimalResponsibility"], registry=registry,
        ).validate(invalid)


def test_movement_exports_keep_population_participants_and_residence_distinct(biology, movement_records):
    result, shapes, _, registry = biology
    for record in movement_records:
        jsonschema.Draft202012Validator(
            result["concept_schemas"][record["@type"]], registry=registry,
            format_checker=jsonschema.FormatChecker(),
        ).validate(record)
    assert result["concepts"]["AnimalMovement"]["maturity"] == "draft"
    data = graph_for(movement_records, result)
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
    movement = URIRef("https://example.org/movements/partial-herd")
    moving = URIRef("https://example.org/animals/moving-cow")
    staying = URIRef("https://example.org/animals/staying-cow")
    source_group = URIRef("https://example.org/herds/source")
    transit_sites = {
        URIRef("https://example.org/facilities/transit-market"),
        URIRef("https://example.org/facilities/transit-centre"),
    }
    assert set(data.objects(source_group, PS.known_animal_members)) == {moving, staying}
    assert set(data.objects(movement, PS.moved_animals)) == {moving}
    assert (movement, PS.movement_source_group, source_group) in data
    assert (movement, PS.moved_animal_count, Literal(3)) in data
    assert (None, PS.animal_count, Literal(12)) in data
    # Both transit values are direct IRI relationships, not an ordered RDF list.
    assert set(data.objects(movement, PS.movement_transit_sites)) == transit_sites
    assert not any(list(data.subjects(PS.animal_residence_site, site)) for site in transit_sites)
    assert not list(data.objects(movement, PS.animal_responsible_actor))
    residences = [r for r in movement_records if r["@type"] == "agri/AnimalResidence"]
    moving_residences = [r for r in residences if r["animal_subject"] == str(moving)]
    assert len(moving_residences) == 2
    owner = next(r for r in movement_records if r["@type"] == "AnimalResponsibility")
    assert owner["animal_subject"] == str(moving) and "end_date" not in owner
    # Differing residence sites are valid assertions without a movement assertion.
    no_movement = [r for r in movement_records if r["@type"] != "AnimalMovement"]
    data = graph_for(no_movement, result)
    assert validate(data, shacl_graph=shapes, inference="rdfs")[0]
    assert not list(data.subjects(RDF.type, PS.AnimalMovement))


def test_partial_movement_is_optional_vocabulary_but_incomplete_submission(biology):
    result, shapes, _, registry = biology
    partial = {"@id": "https://example.org/movements/partial", "@type": "AnimalMovement"}
    validator = jsonschema.Draft202012Validator(
        result["concept_schemas"]["AnimalMovement"], registry=registry,
    )
    validator.validate({})
    validator.validate(partial)
    assert validate(graph_for([partial], result), shacl_graph=shapes, inference="rdfs")[0]
    with pytest.raises(jsonschema.ValidationError):
        movement_profile.validate_profile([partial])


@pytest.mark.parametrize(("field", "value"), [
    ("moved_animal_count", "three"),
    ("moved_animals", "https://example.org/animals/moving-cow"),
    ("movement_source_group", 42),
    ("movement_origin_site", 42),
    ("movement_destination_site", ["https://example.org/facilities/destination-premises"]),
    ("movement_transit_sites", "https://example.org/facilities/transit-market"),
    ("movement_departure_date", "2026-02-30"),
    ("movement_arrival_date", "2026-02-30"),
    ("recorded_at", "tomorrow"),
])
def test_movement_json_schema_rejects_wrong_primitives_and_collections(biology, field, value):
    result, _, _, registry = biology
    validator = jsonschema.Draft202012Validator(
        result["concept_schemas"]["AnimalMovement"], registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({field: value})


@pytest.mark.parametrize(("field", "target"), [
    ("moved_animals", "https://example.org/herds/source"),
    ("movement_source_group", "https://example.org/animals/moving-cow"),
])
def test_movement_shacl_checks_resolved_animal_and_group_types(biology, movement_records, field, target):
    result, shapes, _, registry = biology
    records = copy.deepcopy(movement_records)
    movement = next(r for r in records if r["@type"] == "AnimalMovement")
    movement[field] = [target] if field == "moved_animals" else target
    # Native JSON Schema accepts URI references; SHACL checks the supplied RDF types.
    jsonschema.Draft202012Validator(
        result["concept_schemas"]["AnimalMovement"], registry=registry,
    ).validate(movement)
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]


@pytest.mark.parametrize(("field", "value"), [
    ("moved_animal_count", Literal("three")),
    ("movement_departure_date", Literal("2026-02-30", datatype=XSD.date)),
    ("movement_arrival_date", Literal("2026-02-30", datatype=XSD.date)),
    ("recorded_at", Literal("tomorrow")),
    ("movement_origin_site", Literal("https://example.org/facilities/origin-premises")),
    ("movement_transit_sites", Literal("https://example.org/facilities/transit-market")),
])
def test_movement_shacl_rejects_wrong_rdf_values(biology, movement_records, field, value):
    result, shapes, _, _ = biology
    data = graph_for(movement_records, result)
    movement = URIRef("https://example.org/movements/partial-herd")
    data.set((movement, PS[field], value))
    assert not validate(data, shacl_graph=shapes, inference="rdfs")[0]


def test_movement_shacl_rejects_multiple_origins(biology, movement_records):
    result, shapes, _, _ = biology
    data = graph_for(movement_records, result)
    data.add((URIRef("https://example.org/movements/partial-herd"), PS.movement_origin_site,
              URIRef("https://example.org/farms/another-origin")))
    assert not validate(data, shacl_graph=shapes, inference="rdfs")[0]


def test_movement_submission_accepts_partial_identification_and_no_inventory_inference(movement_records):
    movement_profile.validate_profile(movement_records)
    unidentified = copy.deepcopy(movement_records)
    next(r for r in unidentified if r["@type"] == "AnimalMovement").pop("moved_animals")
    movement_profile.validate_profile(unidentified)
    single = copy.deepcopy(movement_records)
    movement = next(r for r in single if r["@type"] == "AnimalMovement")
    movement.pop("movement_source_group")
    movement["moved_animal_count"] = 1
    movement_profile.validate_profile(single)
    # A previous count cannot bound this later event without all intervening events.
    earlier_zero = copy.deepcopy(movement_records)
    next(r for r in earlier_zero if r["@type"] == "AnimalGroupCount")["animal_count"] = 0
    movement_profile.validate_profile(earlier_zero)


@pytest.mark.parametrize("count", [0, -1])
def test_movement_of_no_animals_fails_every_check(biology, movement_records, count):
    result, shapes, _, registry = biology
    records = copy.deepcopy(movement_records)
    movement = next(r for r in records if r["@type"] == "AnimalMovement")
    movement["moved_animal_count"] = count
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            result["concept_schemas"]["AnimalMovement"], registry=registry,
        ).validate(movement)
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
    with pytest.raises(jsonschema.ValidationError):
        movement_profile.validate_profile(records)


def test_negative_animal_count_fails_shacl(biology, movement_records):
    result, shapes, _, _ = biology
    data = graph_for(movement_records, result)
    data.set((URIRef("https://example.org/counts/before-movement"), PS.animal_count, Literal(-1)))
    assert not validate(data, shacl_graph=shapes, inference="rdfs")[0]


@pytest.mark.parametrize(("field", "value", "error"), [
    ("moved_animals", ["https://example.org/animals/missing"], "unresolved local target"),
    ("movement_source_group", "https://example.org/animals/moving-cow", "wrong resolved target type"),
    ("movement_origin_site", "https://example.org/people/continuing-owner", "wrong resolved target type"),
    ("movement_destination_site", "https://example.org/farms/missing", "unresolved local target"),
    ("movement_transit_sites", ["https://example.org/people/continuing-owner"], "wrong resolved target type"),
])
def test_movement_profile_resolves_subjects_and_sites_locally(movement_records, field, value, error):
    records = copy.deepcopy(movement_records)
    next(r for r in records if r["@type"] == "AnimalMovement")[field] = value
    with pytest.raises(ValueError, match=f"{field}: {error}"):
        movement_profile.validate_profile(records)


@pytest.mark.parametrize("wrong_site", [
    "https://example.org/people/continuing-owner",
    "https://example.org/farms/managed-holding",
])
def test_site_of_another_type_fails_shacl_and_profile(biology, movement_records, wrong_site):
    result, shapes, _, registry = biology
    records = copy.deepcopy(movement_records)
    movement = next(r for r in records if r["@type"] == "AnimalMovement")
    movement["movement_origin_site"] = wrong_site
    # Native JSON Schema accepts URI references; SHACL checks the supplied RDF types.
    jsonschema.Draft202012Validator(
        result["concept_schemas"]["AnimalMovement"], registry=registry,
    ).validate(movement)
    assert not validate(graph_for(records, result), shacl_graph=shapes, inference="rdfs")[0]
    with pytest.raises(ValueError, match="movement_origin_site: wrong resolved target type"):
        movement_profile.validate_profile(records)


def test_movement_profile_requires_evidence_and_consistent_participant_count(movement_records):
    records = copy.deepcopy(movement_records)
    movement = next(r for r in records if r["@type"] == "AnimalMovement")
    movement.pop("moved_animals")
    movement.pop("movement_source_group")
    with pytest.raises(jsonschema.ValidationError):
        movement_profile.validate_profile(records)
    movement["moved_animals"] = [
        "https://example.org/animals/moving-cow", "https://example.org/animals/staying-cow",
    ]
    movement["moved_animal_count"] = 1
    with pytest.raises(ValueError, match="fewer animals than identified participants"):
        movement_profile.validate_profile(records)
    movement["moved_animals"] = ["https://example.org/animals/moving-cow"] * 2
    with pytest.raises(jsonschema.ValidationError):
        movement_profile.validate_profile(records)


@pytest.mark.parametrize(("field", "value"), [
    ("movement_departure_date", "2026-02-30"),
    ("movement_arrival_date", "2026-02-30"),
    ("recorded_at", "2026-08-05T14:00:00"),
])
def test_movement_profile_checks_date_formats_without_inferred_timezone(movement_records, field, value):
    records = copy.deepcopy(movement_records)
    next(r for r in records if r["@type"] == "AnimalMovement")[field] = value
    with pytest.raises(jsonschema.ValidationError):
        movement_profile.validate_profile(records)


def test_movement_profile_rejects_arrival_before_departure(movement_records):
    records = copy.deepcopy(movement_records)
    movement = next(r for r in records if r["@type"] == "AnimalMovement")
    movement["movement_arrival_date"] = movement["movement_departure_date"]
    movement_profile.validate_profile(records)
    movement["movement_arrival_date"] = "2026-08-01"
    with pytest.raises(ValueError, match="movement_arrival_date: before departure"):
        movement_profile.validate_profile(records)


RETIRED_SLOTS = (
    "animal_identifiers", "animal_birth_year", "animal_group_counts", "breed_context",
    "breed_source", "count_date", "biological_dam", "biological_sire", "animal_movement_date",
    "seed_lot_identifiers", "variety_denomination", "holding_institute", "collection_date_text",
    "accession_collected_on", "seed_lot_produced_on", "component_planting_date",
)


@pytest.mark.parametrize("slot", RETIRED_SLOTS)
def test_merged_and_renamed_slots_stay_retired(biology, slot):
    result, _, _, _ = biology
    assert slot not in result["properties"]


@pytest.mark.parametrize(("concept", "slot"), [
    ("IndividualAnimal", "identifiers"),
    ("AnimalGroup", "identifiers"),
    ("agri/AnimalBreed", "identifiers"),
    ("GeneticResourceAccession", "identifiers"),
    ("SeedLot", "identifiers"),
    ("agri/CropPlantingComponent", "planting_date"),
])
def test_shared_slots_replace_family_specific_ones(biology, concept, slot):
    result, _, _, _ = biology
    assert slot in result["concept_schemas"][concept]["properties"]


@pytest.mark.parametrize(("slot", "target"), [
    ("animal_subject", "IdentifiedAnimalUnit"),
    ("animal_residence_site", "agri/AgriculturalFacility"),
    ("animal_responsible_actor", "Agent"),
    ("movement_origin_site", "agri/AgriculturalFacility"),
    ("movement_destination_site", "agri/AgriculturalFacility"),
    ("movement_transit_sites", "agri/AgriculturalFacility"),
    ("breed_recognized_by", "Organization"),
    ("maintaining_institute", "Organization"),
])
def test_relationship_slots_have_typed_ranges(biology, slot, target):
    result, _, _, _ = biology
    assert result["properties"][slot]["references"] == target


def test_identified_animal_unit_is_the_abstract_parent_of_animals_and_groups(biology):
    result, _, _, _ = biology
    assert result["concepts"]["IdentifiedAnimalUnit"]["abstract"] is True
    for concept in ("IndividualAnimal", "AnimalGroup"):
        assert "IdentifiedAnimalUnit" in result["concepts"][concept]["supertypes"]


def test_responsible_actor_is_sensitive(biology):
    result, _, _, _ = biology
    assert result["properties"]["animal_responsible_actor"]["sensitivity"] == "sensitive"


def test_count_bounds_are_vocabulary_constraints(biology):
    result, _, _, _ = biology
    assert result["properties"]["animal_count"]["minimum"] == 0
    assert result["properties"]["moved_animal_count"]["minimum"] == 1


@pytest.mark.parametrize(("concept", "slot"), [
    ("IndividualAnimal", "animal_birth_date"),
    ("GeneticResourceAccession", "accession_collection_date"),
])
@pytest.mark.parametrize(("value", "valid"), [
    ("1990", True), ("1990-07", True), ("1990-07-15", True),
    ("1990----", False), ("19900715", False), ("1990-13", False), ("1990-07-32", False), ("90", False),
])
def test_partial_dates_accept_reduced_precision_only(biology, concept, slot, value, valid):
    result, shapes, _, registry = biology
    validator = jsonschema.Draft202012Validator(result["concept_schemas"][concept], registry=registry)
    record = {"@id": "https://example.org/partial-date", "@type": concept, slot: value}
    assert validator.is_valid(record) is valid
    assert validate(graph_for([record], result), shacl_graph=shapes, inference="rdfs")[0] is valid


@pytest.mark.parametrize("subject", ["https://example.org/animals/1", "https://example.org/herds/1"])
def test_residence_and_responsibility_accept_animal_or_group(biology, subject):
    result, shapes, records, _ = biology
    selected = copy.deepcopy(records)
    for record in selected:
        if "animal_subject" in record:
            record["animal_subject"] = subject
    data = graph_for(selected + LINKED_TARGETS, result)
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs")
    assert conforms, report


@pytest.mark.parametrize(("field", "target"), [
    ("animal_subject", "https://example.org/people/owner"),
    ("animal_responsible_actor", "https://example.org/animals/1"),
    ("animal_residence_site", "https://example.org/farms/1"),
])
def test_relationship_targets_of_another_type_fail_shacl(biology, field, target):
    result, shapes, records, _ = biology
    selected = copy.deepcopy(records)
    record = next(r for r in selected if field in r)
    record[field] = target
    assert not validate(graph_for(selected + LINKED_TARGETS, result), shacl_graph=shapes, inference="rdfs")[0]
