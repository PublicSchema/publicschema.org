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
GOVERNMENT_MODULES = ("organizations", "ownership", "regulation", "education", "work", "transport",
                      "environment", "tax", "elections", "physical_assets")
# Classes in the government modules whose examples belong to other fixture sets.
EXAMPLED_ELSEWHERE = {"LegalArrangement", "EducationOffering", "WorkRelationship",
                      "WaterUseAuthorization", "AssetAddressAssignment", "Certification"}
AUTHORED = {"classes": {}, "slots": {}}
for _module in GOVERNMENT_MODULES:
    _authored = yaml.safe_load((ROOT / f"schema/{_module}.yaml").read_text())
    for _section, _entries in AUTHORED.items():
        _entries.update(_authored.get(_section) or {})


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


def context_uri(context, term):
    value = context[term]
    return URIRef(value["@id"] if isinstance(value, dict) else value)


def example_profile_errors(records):
    """Deliberately local profile, not reference-vocabulary or runtime enforcement.

    Complete typed subjects must be present; same-URI references do not mint new
    actors. Dates and ownership percentage are application rules.
    """
    index = {record["@id"]: record for record in records}
    errors = []
    organization_types = {"Organization", "PublicOrganization", "edu/EducationProvider"}
    for record in records:
        kind = record["@type"]
        for begin, end in [("valid_from", "valid_to"), ("start_date", "end_date")]:
            if begin in record and end in record and record[begin] > record[end]:
                errors.append("reversed period")
        field = None
        allowed = set()
        if kind in {"ProfessionalLicense", "transport/DrivingEntitlement", "elections/VoterRegistration"}:
            field, allowed = "registered_subject", {"Person"}
        elif kind == "tax/TaxRegistration":
            field, allowed = "registered_subject", organization_types | {"Person"}
        elif kind in {"OwnershipInterest", "InstitutionalRole"}:
            field = "interest_holder" if kind == "OwnershipInterest" else "role_actor"
            allowed = organization_types | {"Person"}
        if kind == "AssetPartyRole":
            field, allowed = "asset_actor", organization_types | {"Person"}
        if kind == "RepresentationRole":
            field, allowed = "representative", organization_types | {"Person"}
            represented = index.get(record.get("represented"))
            if represented is None or represented["@type"] not in allowed:
                errors.append("invalid represented party")
        if field:
            target = index.get(record.get(field))
            if target is None:
                errors.append("missing actor")
            elif target["@type"] not in allowed:
                errors.append("wrong actor kind")
        if kind == "OwnershipInterest" and "interest_percentage" in record:
            if not 0 <= record["interest_percentage"] <= 100:
                errors.append("percentage outside zero to one hundred")
    return errors


def test_every_government_term_survives_actual_exports(exports):
    built, shapes, ontology, _ = exports
    example_types = {record["@type"] for record in RECORDS}
    context = built["context"]["@context"]
    for name, definition in AUTHORED["classes"].items():
        class_uri = context_uri(context, name)
        class_key = str(class_uri).removeprefix(str(PS))
        if name not in EXAMPLED_ELSEWHERE:
            assert class_key in example_types
        assert class_key in built["concepts"]
        assert (class_uri, RDF.type, OWL.Class) in ontology
        targets = list(shapes.subjects(SH.targetClass, class_uri))
        assert targets, name
        paths = {
            path for target in targets
            for shape in shapes.objects(target, SH.property)
            for path in shapes.objects(shape, SH.path)
        }
        for slot in definition["slots"]:
            assert slot in built["concept_schemas"][class_key]["properties"], (name, slot)
            assert context_uri(context, slot) in paths, (name, slot)
    for name in AUTHORED["slots"]:
        assert name in built["properties"]
        property_uri = context_uri(context, name)
        assert (property_uri, RDF.type, OWL.ObjectProperty) in ontology or (
            property_uri, RDF.type, OWL.DatatypeProperty
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


@pytest.mark.parametrize("kind,changes", [
    ("environment/EnvironmentalFacility", {"environmental_activities": "processing"}),
    ("OwnershipInterest", {"interest_directness": "not-a-code"}),
    ("OwnershipInterest", {"interest_percentage": "twenty"}),
    ("transport/Vehicle", {"manufacture_year": "unknown"}),
    ("edu/ProviderSite", {"virtual_site_url": ["https://example.org/learning", "https://example.org/second"]}),
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
    ("facility-operator", {"asset_actor": "https://example.org/vehicle"}, "wrong actor kind"),
    ("facility-operator", {"asset_actor": "https://example.org/unavailable"}, "missing actor"),
    ("tax-representative", {"represented": "https://example.org/vehicle"}, "invalid represented party"),
    ("voter", {"registered_subject": "https://example.org/company"}, "wrong actor kind"),
    ("drive-B", {"registered_subject": "https://example.org/unavailable"}, "missing actor"),
    ("professional-license", {"valid_to": "2024-01-01"}, "reversed period"),
    ("interest-person", {"interest_percentage": 101}, "percentage outside zero to one hundred"),
])
def test_example_profile_rejects_semantic_counterexamples(suffix, changes, message):
    records = copy.deepcopy(RECORDS)
    target = next(record for record in records if record["@id"] == "https://example.org/" + suffix)
    target.update(changes)
    assert message in example_profile_errors(records)


def test_partial_vocabulary_record_is_valid_but_not_complete_example_profile(exports):
    partial = {"@context": DEFAULT_CONTEXT_URL, "@id": "https://example.org/partial",
               "@type": "transport/DrivingEntitlement"}
    validator(exports, "transport/DrivingEntitlement").validate(partial)
    assert "missing actor" in example_profile_errors([partial])


def test_counterexamples_preserve_neighboring_identities():
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert "physical_service_point" not in records["online-site"]
    assert records["drive-B"]["valid_to"] != records["drive-C"]["valid_to"]
    assert records["tax-company"]["registered_subject"] == records["company"]["@id"]
    assert records["vehicle-registration"]["registered_subject"] == records["inspection"]["subject_uri"]
    assert "interest_percentage" not in records["interest-organization"]


def test_revised_reference_distinctions_are_not_profile_only():
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert records["unit"]["@type"] == "BuildingUnit"
    assert records["vehicle-keeper"]["asset_actor"] != records["vehicle-owner"]["asset_actor"]
    assert records["vehicle-keeper"]["subject_uri"] == records["vehicle-owner"]["subject_uri"]
    assert records["interest-statement"]["subject_uri"] == records["interest-person"]["@id"]
    assert records["interest-statement"]["recorded_at"][:10] > records["interest-person"]["start_date"]


@pytest.mark.parametrize("operator", ["person", "company", None])
def test_facility_operator_is_a_dated_asset_role_for_person_organization_or_unknown(exports, operator):
    records = copy.deepcopy(RECORDS)
    facility = next(record for record in records if record["@type"] == "environment/EnvironmentalFacility")
    role = next(record for record in records if record["@id"] == "https://example.org/facility-operator")
    assert role["@type"] == "AssetPartyRole"
    assert role["asset_subject"] == facility["@id"]
    assert "start_date" in role
    if operator is None:
        records.remove(role)
    else:
        role["asset_actor"] = "https://example.org/" + operator
    built, shapes, ontology, _ = exports
    graph = expand_graph(records, built["context"])
    hierarchy = Graph()
    for triple in ontology.triples((None, RDFS.subClassOf, None)):
        hierarchy.add(triple)
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=hierarchy)
    assert conforms, report
    assert not example_profile_errors(records)
    roles = set(graph.subjects(PS.asset_subject, URIRef(facility["@id"]))) & set(
        graph.subjects(RDF.type, PS.AssetPartyRole))
    if operator is not None:
        assert roles == {URIRef(role["@id"])}
        assert (URIRef(role["@id"]), PS.asset_actor, URIRef(role["asset_actor"])) in graph
    else:
        assert not roles
    # The facility record itself carries no operator or address slot.
    assert not set(facility) & {"environmental_operator", "facility_addresses"}


def test_retired_draft_slots_stay_removed(exports):
    built, _, _, _ = exports
    context = built["context"]["@context"]
    for name in ("environmental_operator", "facility_addresses", "entitlement_conditions", "tax_regime",
                 "water_quantity_period"):
        assert name not in built["properties"], name
        assert name not in context, name
    facility_slots = built["concept_schemas"]["environment/EnvironmentalFacility"]["properties"]
    assert "environmental_operator" not in facility_slots
    assert "facility_addresses" not in facility_slots
    assert "tax_type" in built["concept_schemas"]["tax/TaxRegistration"]["properties"]
    assert "driving_condition_codes" in built["concept_schemas"]["transport/DrivingEntitlement"]["properties"]


def test_disclosure_sensitive_government_slots(exports):
    built, _, _, _ = exports
    properties = built["properties"]
    assert properties["driving_condition_codes"]["sensitivity"] == "sensitive"
    assert properties["polling_service_point"]["sensitivity"] == "sensitive"
    assert properties["electoral_districts"].get("sensitivity") in {None, "standard"}


def test_coded_and_textual_authorization_conditions_point_to_each_other(exports):
    built, _, _, _ = exports
    properties = built["properties"]
    assert "authorization_conditions" in properties["driving_condition_codes"]["definition"]["en"]
    assert "driving_condition_codes" in properties["authorization_conditions"]["definition"]["en"]
