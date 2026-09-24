"""Government domain fixtures through the production exporters and a named example profile."""

import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml
from pyshacl import validate
from rdflib import Namespace, URIRef
from rdflib.namespace import OWL, RDF, SH

from build.linkml_rdf_export import DEFAULT_CONTEXT_URL
from tests.conftest import jsonld_graph, load_example

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace("https://publicschema.org/")
RECORDS = json.loads((ROOT / "examples/government-domains/records.json").read_text())
PROFILE = load_example("government-domains/profile.py")
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


@pytest.fixture(scope="module")
def exports(built_vocabulary, shacl_graph, owl_graph, schema_registry):
    return built_vocabulary, shacl_graph, owl_graph, schema_registry


def validator(exports, kind):
    built, _, _, registry = exports
    return jsonschema.Draft202012Validator(
        built["concept_schemas"][kind], registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )


def context_uri(context, term):
    value = context[term]
    return URIRef(value["@id"] if isinstance(value, dict) else value)


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
        for slot in definition.get("slots", []):
            assert slot in built["concept_schemas"][class_key]["properties"], (name, slot)
            assert context_uri(context, slot) in paths, (name, slot)
    for name in AUTHORED["slots"]:
        assert name in built["properties"]
        property_uri = context_uri(context, name)
        assert (property_uri, RDF.type, OWL.ObjectProperty) in ontology or (
            property_uri, RDF.type, OWL.DatatypeProperty
        ) in ontology


def test_same_synthetic_records_validate_json_schema_and_context_shacl(exports, subclass_hierarchy):
    built, shapes, _, _ = exports
    for record in RECORDS:
        validator(exports, record["@type"]).validate(record)
    graph = jsonld_graph(RECORDS, built["context"])
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=subclass_hierarchy)
    assert conforms, report
    assert not PROFILE.profile_errors(RECORDS)
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
def test_invalid_public_shapes_fail_both_formats(exports, subclass_hierarchy, kind, changes):
    built, shapes, _, _ = exports
    invalid = copy.deepcopy(next(record for record in RECORDS if record["@type"] == kind))
    invalid.update(changes)
    assert list(validator(exports, kind).iter_errors(invalid))
    graph = jsonld_graph([record for record in RECORDS if record["@id"] != invalid["@id"]] + [invalid], built["context"])
    conforms, _, _ = validate(graph, shacl_graph=shapes, ont_graph=subclass_hierarchy)
    assert not conforms


@pytest.mark.parametrize("suffix,changes,message", [
    ("facility-operator", {"asset_actor": "https://example.org/vehicle"}, "wrong actor kind"),
    ("facility-operator", {"asset_actor": "https://example.org/unavailable"}, "missing actor"),
    ("tax-representative", {"represented": "https://example.org/vehicle"}, "invalid represented party"),
    ("voter", {"registered_subject": "https://example.org/company"}, "wrong actor kind"),
    ("drive-B", {"registered_subject": "https://example.org/unavailable"}, "missing actor"),
    ("professional-license", {"valid_to": "2024-01-01"}, "empty or reversed period"),
    # end_date is the first inactive day, so a role ending on its start day is empty.
    ("facility-operator", {"end_date": "2024-06-01"}, "empty or reversed period"),
    ("professional-license", {"valid_from": "20250101"}, "valid_from: expected an exact YYYY-MM-DD calendar date"),
    ("interest-person", {"start_date": "2025-02-30"}, "start_date: impossible calendar date"),
    ("interest-person", {"interest_percentage": 101}, "percentage outside zero to one hundred"),
])
def test_example_profile_rejects_semantic_counterexamples(suffix, changes, message):
    records = copy.deepcopy(RECORDS)
    target = next(record for record in records if record["@id"] == "https://example.org/" + suffix)
    target.update(changes)
    assert message in PROFILE.profile_errors(records)


def test_inclusive_validity_allows_a_single_day():
    records = copy.deepcopy(RECORDS)
    license_ = next(record for record in records if record["@id"] == "https://example.org/professional-license")
    license_["valid_to"] = license_["valid_from"]
    assert not PROFILE.profile_errors(records)


def test_example_profile_rejects_a_repeated_record_identity():
    # A flat record list cannot say which of two records for one URI is current.
    records = copy.deepcopy(RECORDS)
    records.append({**records[0], "name": "Another record"})
    assert f"{records[0]['@id']}: duplicate record identity" in PROFILE.profile_errors(records)


def test_partial_vocabulary_record_is_valid_but_not_complete_example_profile(exports):
    partial = {"@context": DEFAULT_CONTEXT_URL, "@id": "https://example.org/partial",
               "@type": "transport/DrivingEntitlement"}
    validator(exports, "transport/DrivingEntitlement").validate(partial)
    assert "missing actor" in PROFILE.profile_errors([partial])


def test_counterexamples_preserve_neighboring_identities():
    # Protects the registry-foundations decision: each counterexample changes one fact, so neighbours stay distinct.
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert "physical_service_point" not in records["online-site"]
    assert records["drive-B"]["valid_to"] != records["drive-C"]["valid_to"]
    assert records["tax-company"]["registered_subject"] == records["company"]["@id"]
    assert records["vehicle-registration"]["registered_subject"] == records["inspection"]["subject_uri"]
    assert "interest_percentage" not in records["interest-organization"]


def test_revised_reference_distinctions_are_not_profile_only():
    # Protects the registry-foundations decision: asset roles and statements are separate records about one subject.
    records = {record["@id"].rsplit("/", 1)[-1]: record for record in RECORDS}
    assert records["unit"]["@type"] == "BuildingUnit"
    assert records["vehicle-keeper"]["asset_actor"] != records["vehicle-owner"]["asset_actor"]
    assert records["vehicle-keeper"]["subject_uri"] == records["vehicle-owner"]["subject_uri"]
    assert records["interest-statement"]["subject_uri"] == records["interest-person"]["@id"]
    assert records["interest-statement"]["recorded_at"][:10] > records["interest-person"]["start_date"]


@pytest.mark.parametrize("operator", ["person", "company", None])
def test_facility_operator_is_a_dated_asset_role_for_person_organization_or_unknown(
    exports, subclass_hierarchy, operator,
):
    records = copy.deepcopy(RECORDS)
    facility = next(record for record in records if record["@type"] == "environment/EnvironmentalFacility")
    role = next(record for record in records if record["@id"] == "https://example.org/facility-operator")
    assert role["@type"] == "AssetPartyRole"
    assert role["subject_uri"] == facility["@id"]
    assert "start_date" in role
    if operator is None:
        records.remove(role)
    else:
        role["asset_actor"] = "https://example.org/" + operator
    built, shapes, _, _ = exports
    graph = jsonld_graph(records, built["context"])
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=subclass_hierarchy)
    assert conforms, report
    assert not PROFILE.profile_errors(records)
    roles = set(graph.subjects(PS.subject_uri, URIRef(facility["@id"]))) & set(
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
    # A small district, such as a ward, can narrow where the voter lives.
    assert properties["electoral_districts"]["sensitivity"] == "sensitive"


def test_coded_and_textual_authorization_conditions_point_to_each_other(exports):
    built, _, _, _ = exports
    properties = built["properties"]
    assert "authorization_conditions" in properties["driving_condition_codes"]["definition"]["en"]
    assert "driving_condition_codes" in properties["authorization_conditions"]["definition"]["en"]


def test_legal_acts_are_cited_as_related_sources_not_as_matching_terms():
    # A directive or regulation is a whole document, not a class or property a term can match.
    legal_act = "https://eur-lex.europa.eu/eli/"
    for path in sorted((ROOT / "schema").glob("*.yaml")):
        authored = yaml.safe_load(path.read_text())
        for section in ("classes", "slots", "enums"):
            for name, entry in (authored.get(section) or {}).items():
                for key in ("exact_mappings", "close_mappings", "broad_mappings", "narrow_mappings"):
                    assert not any(uri.startswith(legal_act) for uri in entry.get(key) or []), (name, key)
                alignments = (entry.get("annotations") or {}).get("external_alignments_json") or "[]"
                for alignment in json.loads(alignments):
                    if alignment.get("uri", "").startswith(legal_act):
                        assert alignment["match"] == "related", name


@pytest.mark.parametrize("alias", [
    "about", "provider", "educationalCredentialAwarded", "courseMode", "issuedBy", "model", "productionDate",
])
def test_only_exact_schema_org_matches_become_context_aliases(exports, alias):
    # An alias makes schema.org data expand to a PublicSchema property, which is safe only for an exact match.
    context = exports[0]["context"]["@context"]
    assert alias not in context
    assert context["startDate"] == context["start_date"]


def test_schema_org_mappings_use_the_shared_prefix():
    # Every module maps schema: to http://schema.org/; an https IRI would be a different RDF term.
    for path in sorted((ROOT / "schema").glob("*.yaml")):
        authored = yaml.safe_load(path.read_text())
        for section in ("classes", "slots", "enums"):
            for name, entry in (authored.get(section) or {}).items():
                for key in ("exact_mappings", "close_mappings", "broad_mappings", "narrow_mappings", "related_mappings"):
                    for mapping in (entry or {}).get(key) or []:
                        assert "schema.org" not in mapping, (path.name, name, mapping)


def test_vehicle_is_narrower_than_the_schema_org_vehicle(exports):
    # schema.org Vehicle also covers aircraft, boats and vehicles offered for sale.
    vehicle = AUTHORED["classes"]["Vehicle"]
    assert vehicle["broad_mappings"] == ["schema:Vehicle"]
    assert "close_mappings" not in vehicle
    built, _, _, _ = exports
    assert built["concepts"]["transport/Vehicle"]["external_equivalents"]["schema-org"]["match"] == "broad"
