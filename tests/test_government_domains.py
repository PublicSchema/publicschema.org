"""Government domain fixtures through the production exporters and a named example profile."""

import copy
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
from build.linkml_rdf_export import DEFAULT_CONTEXT_URL, write_shacl, write_turtle

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")
RECORDS = json.loads((ROOT / "examples/government-domains/records.json").read_text())
AUTHORED = yaml.safe_load((ROOT / "schema/government.yaml").read_text())


def expand_graph(records, context):
    def loader(url, options=None):
        assert url == DEFAULT_CONTEXT_URL
        return {"contextUrl": None, "documentUrl": url, "document": context}

    expanded = jsonld.expand(records, options={"documentLoader": loader})
    return Graph().parse(data=jsonld.to_rdf(expanded, {"format": "application/n-quads"}), format="nquads")


@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    built = build_vocabulary(ROOT / "schema")
    path = tmp_path_factory.mktemp("government-exports")
    composite = ROOT / "schema/publicschema.yaml"
    shapes = Graph().parse(write_shacl(path / "shapes.ttl", composite=composite), format="turtle")
    ontology = Graph().parse(write_turtle(path / "vocabulary.ttl", composite=composite), format="turtle")
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


def example_profile_errors(records):
    """Deliberately local profile, not reference-vocabulary or runtime enforcement.

    Complete typed subjects must be present; same-URI references do not mint new
    actors. Dates, ownership percentage and strength pairing are application rules.
    """
    index = {record["@id"]: record for record in records}
    errors = []
    organization_types = {"Organization", "PublicOrganization", "LegalEntity", "EducationProvider"}
    for record in records:
        kind = record["@type"]
        for begin, end in [("valid_from", "valid_to"), ("start_date", "end_date")]:
            if begin in record and end in record and record[begin] > record[end]:
                errors.append("reversed period")
        field = None
        allowed = set()
        if kind in {"ProfessionalLicense", "DrivingEntitlement", "VoterRegistration"}:
            field, allowed = "registered_subject", {"Person"}
        elif kind == "TaxRegistration":
            field, allowed = "registered_subject", organization_types | {"Person"}
        elif kind in {"OwnershipInterest", "InstitutionalRole"}:
            field = "interest_holder" if kind == "OwnershipInterest" else "role_actor"
            allowed = organization_types | {"Person"}
        if kind == "AssetPartyRole":
            field, allowed = "asset_actor", organization_types | {"Person"}
        if kind == "RepresentationRole":
            field, allowed = "representative_actor", organization_types | {"Person"}
            represented = index.get(record.get("represented_subject"))
            if represented is None or represented["@type"] not in allowed:
                errors.append("invalid represented subject")
        if kind == "RoadRestriction":
            target = index.get(record.get("restricted_road_element"))
            if target is None or target["@type"] not in {"Road", "RoadSegment", "RoadNode"}:
                errors.append("invalid restricted road element")
        if field:
            target = index.get(record.get(field))
            if target is None:
                errors.append("missing actor")
            elif target["@type"] not in allowed:
                errors.append("wrong actor kind")
        if kind == "OwnershipInterest" and "interest_percentage" in record:
            if not 0 <= record["interest_percentage"] <= 100:
                errors.append("percentage outside zero to one hundred")
        if kind == "MedicinalIngredient":
            if ("strength_numerator" in record) != ("strength_denominator" in record):
                errors.append("incomplete strength ratio")
            if record.get("strength_denominator", {}).get("quantity_value", 1) <= 0:
                errors.append("nonpositive strength denominator")
    return errors


def test_every_government_term_survives_actual_exports(exports):
    built, shapes, ontology, _ = exports
    example_types = {record["@type"] for record in RECORDS}
    for name, definition in AUTHORED["classes"].items():
        assert name in example_types
        assert name in built["concepts"]
        assert (PS[name], RDF.type, OWL.Class) in ontology
        targets = list(shapes.subjects(SH.targetClass, PS[name]))
        assert targets, name
        paths = {
            path for target in targets
            for shape in shapes.objects(target, SH.property)
            for path in shapes.objects(shape, SH.path)
        }
        for slot in definition["slots"]:
            assert slot in built["concept_schemas"][name]["properties"], (name, slot)
            assert PS[slot] in paths, (name, slot)
    for name in AUTHORED["slots"]:
        assert name in built["properties"]
        assert (PS[name], RDF.type, OWL.ObjectProperty) in ontology or (
            PS[name], RDF.type, OWL.DatatypeProperty
        ) in ontology


def test_same_synthetic_records_validate_json_schema_and_context_shacl(exports):
    built, shapes, ontology, _ = exports
    for record in RECORDS:
        validator(exports, record["@type"]).validate(record)
    graph = expand_graph(RECORDS, built["context"])
    hierarchy = Graph()
    for triple in ontology.triples((None, RDFS.subClassOf, None)):
        hierarchy.add(triple)
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=hierarchy)
    assert conforms, report
    assert not example_profile_errors(RECORDS)
    # URI values remain object identities in RDF, including subclass subjects.
    assert (URIRef("https://example.org/tax-company"), PS.registered_subject,
            URIRef("https://example.org/company")) in graph
    assert (URIRef("https://example.org/ingredient"), PS.ingredient_substance,
            URIRef("https://example.org/substance")) in graph


@pytest.mark.parametrize("kind,changes", [
    ("OwnershipInterest", {"interest_directness": "not-a-code"}),
    ("OwnershipInterest", {"interest_percentage": "twenty"}),
    ("Vehicle", {"manufacture_year": "unknown"}),
    ("ProviderSite", {"virtual_site_url": ["https://example.org/learning", "https://example.org/second"]}),
    ("ComplianceAssessment", {"assessment_date": "yesterday"}),
])
def test_invalid_public_shapes_fail_both_formats(exports, kind, changes):
    built, shapes, ontology, _ = exports
    invalid = copy.deepcopy(next(record for record in RECORDS if record["@type"] == kind))
    invalid.update(changes)
    assert list(validator(exports, kind).iter_errors(invalid))
    graph = expand_graph([record for record in RECORDS if record["@id"] != invalid["@id"]] + [invalid], built["context"])
    hierarchy = Graph()
    for triple in ontology.triples((None, RDFS.subClassOf, None)):
        hierarchy.add(triple)
    conforms, _, _ = validate(graph, shacl_graph=shapes, ont_graph=hierarchy)
    assert not conforms


@pytest.mark.parametrize("suffix,changes,message", [
    ("road-restriction", {"restricted_road_element": "https://example.org/vehicle"}, "invalid restricted road element"),
    ("tax-representative", {"represented_subject": "https://example.org/road"}, "invalid represented subject"),
    ("voter", {"registered_subject": "https://example.org/company"}, "wrong actor kind"),
    ("drive-B", {"registered_subject": "https://example.org/unavailable"}, "missing actor"),
    ("professional-license", {"valid_to": "2024-01-01"}, "reversed period"),
    ("interest-person", {"interest_percentage": 101}, "percentage outside zero to one hundred"),
    ("ingredient", {"strength_denominator": {"quantity_value": 0}}, "nonpositive strength denominator"),
])
def test_example_profile_rejects_semantic_counterexamples(suffix, changes, message):
    records = copy.deepcopy(RECORDS)
    target = next(record for record in records if record["@id"] == "https://example.org/" + suffix)
    target.update(changes)
    assert message in example_profile_errors(records)


def test_partial_vocabulary_record_is_valid_but_not_complete_example_profile(exports):
    partial = {"@context": DEFAULT_CONTEXT_URL, "@id": "https://example.org/partial",
               "@type": "DrivingEntitlement"}
    validator(exports, "DrivingEntitlement").validate(partial)
    assert "missing actor" in example_profile_errors([partial])


def test_counterexamples_preserve_neighboring_identities():
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert "physical_service_point" not in records["online-site"]
    assert records["drive-B"]["valid_to"] != records["drive-C"]["valid_to"]
    assert records["tax-company"]["registered_subject"] == records["company"]["@id"]
    assert records["vehicle-registration"]["registered_subject"] == records["inspection"]["assessed_subject"]
    assert "interest_percentage" not in records["interest-organization"]
    assert records["medicine"]["@id"] != records["product-authorization"]["@id"]


def test_revised_reference_distinctions_are_not_profile_only():
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert records["building-wing"]["@type"] == "BuildingPart"
    assert records["unit"]["@type"] == "BuildingUnit"
    assert records["vehicle-keeper"]["asset_actor"] != records["vehicle-owner"]["asset_actor"]
    assert records["vehicle-keeper"]["asset_subject"] == records["vehicle-owner"]["asset_subject"]
    assert records["package"]["@id"] != records["administrable"]["@id"]
    assert records["interest-statement"]["subject_uri"] == records["interest-person"]["@id"]
    assert records["interest-statement"]["recorded_at"][:10] > records["interest-person"]["start_date"]
