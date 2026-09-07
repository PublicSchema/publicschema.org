"""Native FHIR examples, official structural artifacts, and local identity links."""

import copy
import importlib.util
import json
import socket
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from build.build import build_vocabulary

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/fhir-registry"
SPEC = importlib.util.spec_from_file_location("fhir_registry", EXAMPLE / "validate.py")
integration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integration)
OFFICIAL_SPEC = importlib.util.spec_from_file_location("fhir_official", EXAMPLE / "official_validate.py")
official = importlib.util.module_from_spec(OFFICIAL_SPEC)
OFFICIAL_SPEC.loader.exec_module(official)


@pytest.fixture
def inputs():
    return (json.loads((EXAMPLE / "bundle.fhir.json").read_text()),
            json.loads((EXAMPLE / "registry-links.json").read_text()))


def resource(bundle, identifier):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["id"] == identifier)


def binding(envelope, identifier):
    return next(row for row in envelope["records"] if row["fhir_full_url"].endswith("/" + identifier))


def reference(row):
    return {"@type": "RecordReference", **{key: row["entry"][key] for key in
            ("register_uri", "record_id", "subject_uri")}}


def test_official_artifacts_and_entire_native_journey(inputs):
    bundle, envelope = inputs
    before = copy.deepcopy(inputs)
    assert integration.validate_integration(bundle, envelope) == {
        "fhir_resources": 19, "registry_entries": 19,
        "local_fhir_references": 20, "consumer_links": 5,
    }
    assert inputs == before
    schema, profiles = integration.artifacts()
    assert schema["$schema"] == "http://json-schema.org/draft-06/schema#"
    assert {profile["version"] for profile in profiles.values()} == {"5.0.0"}
    assert integration.reference_targets("HealthcareService")["HealthcareService.providedBy"] == {"Organization"}


def test_publicschema_sidecar_uses_real_generated_native_contracts(inputs):
    _, envelope = inputs
    built = build_vocabulary(ROOT / "schema")
    registry = Registry().with_resources((schema["$id"], Resource.from_contents(schema))
                                         for schema in built["concept_schemas"].values())
    instances = [*envelope["subjects"], *(row["entry"] for row in envelope["records"]),
                 *(link["record"] for link in envelope["links"]),
                 *(outcome["source_record"] for outcome in envelope["migration_outcomes"])]
    for instance in instances:
        Draft202012Validator(built["concept_schemas"][instance["@type"]], registry=registry).validate(instance)


def test_resolved_medical_content_is_native_without_subject_record_collapse(inputs):
    bundle, envelope = inputs
    row = binding(envelope, "veterinary-product")
    resources = integration.resource_index(bundle)
    resolved = integration.resolve_record(reference(row), "MedicinalProductDefinition",
                                          integration.registry_index(envelope), resources)
    assert resolved["resource"] is resources[row["fhir_full_url"]]
    assert resolved["subject_uri"] != row["fhir_full_url"]
    assert row["entry"]["record_id"] != resolved["resource"]["id"]
    assert row["business_identifier"]["value"] != row["entry"]["record_id"]
    assert "subject_type" not in row["entry"]


def test_human_veterinary_and_authorization_distinctions(inputs):
    bundle, _ = inputs
    human = resource(bundle, "human-product")
    veterinary = resource(bundle, "veterinary-product")
    assert human["resourceType"] == veterinary["resourceType"] == "MedicinalProductDefinition"
    assert human["domain"]["text"] == "Human use"
    assert veterinary["domain"]["text"] == "Veterinary use"
    assert human["id"] != veterinary["id"]
    form = resource(bundle, "veterinary-form")
    species = form["routeOfAdministration"][0]["targetSpecies"][0]
    assert species["code"]["text"] == "Cattle"
    assert [(period["tissue"]["text"], period["value"]["value"]) for period in species["withdrawalPeriod"]] == [
        ("Meat", 7), ("Milk", 0),
    ]
    authorization = resource(bundle, "veterinary-authorization")
    assert authorization["subject"][0]["reference"] == "MedicinalProductDefinition/veterinary-product"
    assert resource(bundle, "veterinary-package")["packageFor"] == authorization["subject"]
    assert len({veterinary["id"], form["id"], authorization["id"], "veterinary-package"}) == 4


def test_directory_preserves_provider_upkeep_and_organization_qualification(inputs):
    bundle, envelope = inputs
    service = resource(bundle, "outpatient-service")
    location = resource(bundle, "clinic-site")
    assert service["providedBy"]["reference"] != location["managingOrganization"]["reference"]
    assert location["address"]["period"]["start"] == "2026-01-01"
    assert "qualification" in resource(bundle, "clinic-provider")
    assert "qualification" not in location
    assert binding(envelope, "clinic-site")["entry"]["subject_type"] == "https://publicschema.org/health/HealthFacility"


@pytest.mark.parametrize("mode,form", [("kind", "si"), ("instance", "vi")])
def test_virtual_or_conceptual_fhir_location_is_not_a_physical_health_facility(inputs, mode, form):
    bundle, envelope = inputs
    location = resource(bundle, "clinic-site")
    location["mode"] = mode
    location["form"]["coding"][0]["code"] = form
    with pytest.raises(integration.ContractError, match="physical site or building"):
        integration.validate_integration(bundle, envelope)


@pytest.mark.parametrize("change", [
    lambda value: value.update(unsupportedMedicalField="not FHIR"),
    lambda value: value.update(name="wrong FHIR cardinality"),
    lambda value: value.pop("name"),
])
def test_published_json_schema_rejects_invalid_native_product(inputs, change):
    bundle, envelope = inputs
    change(resource(bundle, "human-product"))
    with pytest.raises(integration.ContractError):
        integration.validate_integration(bundle, envelope)


@pytest.mark.parametrize("target,declared_type,match", [
    ("Location/clinic-site", "Location", "wrong FHIR target type"),
    ("Organization/clinic-provider", "Location", "Reference.type disagrees"),
    ("Organization/missing", "Organization", "missing local FHIR target"),
    ("https://unavailable.example/Organization/absent", "Organization", "missing local FHIR target"),
])
def test_fhir_reference_type_and_missing_targets(inputs, target, declared_type, match, monkeypatch):
    bundle, envelope = inputs
    def no_network(*args, **kwargs):
        pytest.fail("local integration attempted a network connection")
    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(socket, "socket", no_network)
    resource(bundle, "outpatient-service")["providedBy"] = {"reference": target, "type": declared_type}
    with pytest.raises(integration.ContractError, match=match):
        integration.validate_integration(bundle, envelope)


def test_absolute_local_fhir_reference_and_inert_endpoint_address(inputs, monkeypatch):
    bundle, envelope = inputs
    def no_network(*args, **kwargs):
        pytest.fail("a listed URL is not authorization to connect")
    monkeypatch.setattr(socket, "socket", no_network)
    resource(bundle, "outpatient-service")["providedBy"]["reference"] = "https://example.org/fhir/Organization/clinic-provider"
    resource(bundle, "clinic-endpoint")["address"] = "https://unavailable.example/clinical-api"
    integration.validate_integration(bundle, envelope)


def test_identifier_only_fhir_reference_is_explicitly_unsupported(inputs):
    bundle, envelope = inputs
    resource(bundle, "outpatient-service")["providedBy"] = {
        "identifier": {"system": "https://example.org/organizations", "value": "001"},
    }
    with pytest.raises(integration.ContractError, match="literal reference required"):
        integration.validate_integration(bundle, envelope)


def test_reference_business_identifier_must_agree(inputs):
    bundle, envelope = inputs
    resource(bundle, "outpatient-service")["providedBy"]["identifier"] = {
        "system": "https://example.org/identifiers/Organization", "value": "WRONG",
    }
    with pytest.raises(integration.ContractError, match="Reference.identifier disagrees"):
        integration.validate_integration(bundle, envelope)


def test_local_record_id_is_qualified_by_register(inputs):
    bundle, envelope = inputs
    first = binding(envelope, "human-product")
    second = binding(envelope, "veterinary-product")
    second["entry"]["record_id"] = first["entry"]["record_id"]
    second["entry"]["register_uri"] = "https://example.org/registers/another-source"
    records = integration.registry_index(envelope)
    resources = integration.resource_index(bundle)
    one = integration.resolve_record(reference(first), "MedicinalProductDefinition", records, resources)
    two = integration.resolve_record(reference(second), "MedicinalProductDefinition", records, resources)
    assert one["subject_uri"] != two["subject_uri"]


def test_unresolved_record_and_resource_have_explicit_states(inputs):
    bundle, envelope = inputs
    row = binding(envelope, "human-product")
    records = integration.registry_index(envelope)
    resources = integration.resource_index(bundle)
    assert integration.resolve_record(reference(row), "MedicinalProductDefinition", {}, resources) == {"state": "missing-record"}
    assert integration.resolve_record(reference(row), "MedicinalProductDefinition", records, {}) == {
        "state": "missing-resource", "subject_uri": row["entry"]["subject_uri"],
    }
    envelope["links"][0]["record"]["record_id"] = "missing"
    with pytest.raises(integration.ContractError, match="required consumer link is missing-record"):
        integration.validate_integration(bundle, envelope)


@pytest.mark.parametrize("field,value,match", [
    ("subject_uri", "https://example.org/other-subject", "disagree on subject_uri"),
    ("subject_type", "https://publicschema.org/Person", "disagree on subject_type"),
])
def test_record_reference_identity_assertions_must_match(inputs, field, value, match):
    bundle, envelope = inputs
    envelope["links"][3]["record"][field] = value
    with pytest.raises(integration.ContractError, match=match):
        integration.validate_integration(bundle, envelope)


def test_wrong_consumer_resource_type_is_rejected(inputs):
    bundle, envelope = inputs
    envelope["links"][0]["expected_resource_type"] = "Location"
    with pytest.raises(integration.ContractError, match="wrong expected FHIR resource type"):
        integration.validate_integration(bundle, envelope)


@pytest.mark.parametrize("field,value", [("value", "different-id"), ("system", "https://example.org/other-system")])
def test_registry_business_identifier_correspondence(inputs, field, value):
    bundle, envelope = inputs
    binding(envelope, "human-product")["business_identifier"][field] = value
    with pytest.raises(integration.ContractError, match="business identifier mismatch"):
        integration.validate_integration(bundle, envelope)


def test_subject_and_record_url_are_separate(inputs):
    bundle, envelope = inputs
    row = binding(envelope, "human-product")
    row["entry"]["subject_uri"] = row["fhir_full_url"]
    with pytest.raises(integration.ContractError, match="subject URI must be distinct"):
        integration.validate_integration(bundle, envelope)


def test_wrong_native_subject_type_and_missing_subject(inputs):
    bundle, envelope = inputs
    subject = next(subject for subject in envelope["subjects"] if subject["@type"] == "health/HealthFacility")
    subject["@type"] = "Organization"
    with pytest.raises(integration.ContractError, match="native subject has wrong type"):
        integration.validate_integration(bundle, envelope)
    envelope["subjects"].remove(subject)
    with pytest.raises(integration.ContractError, match="missing native subject"):
        integration.validate_integration(bundle, envelope)


def test_duplicate_record_keys_and_full_urls_are_rejected(inputs):
    bundle, envelope = inputs
    envelope["records"].append(copy.deepcopy(envelope["records"][0]))
    with pytest.raises(integration.ContractError, match="duplicate qualified registry record key"):
        integration.validate_integration(bundle, envelope)
    envelope["records"].pop()
    bundle["entry"].append(copy.deepcopy(bundle["entry"][0]))
    with pytest.raises(integration.ContractError, match="duplicate FHIR fullUrl"):
        integration.validate_integration(bundle, envelope)


@pytest.mark.parametrize("field,value", [
    ("@context", "https://publicschema.org/context.jsonld"),
    ("extension", [{"url": "https://example.org/unknown", "valueString": "uninterpreted"}]),
    ("modifierExtension", [{"url": "https://example.org/negation", "valueBoolean": True}]),
    ("implicitRules", "https://example.org/rules"),
    ("contained", [{"resourceType": "Organization", "id": "inside"}]),
])
def test_unsupported_fhir_semantics_are_explicit_failures(inputs, field, value):
    bundle, envelope = inputs
    resource(bundle, "human-product")[field] = value
    with pytest.raises(integration.ContractError, match="JSON-LD|contract"):
        integration.validate_integration(bundle, envelope)


def test_release_and_profile_pins_are_enforced(inputs):
    bundle, envelope = inputs
    envelope["fhir_release"] = "4.0.1"
    with pytest.raises(integration.ContractError, match="release mismatch"):
        integration.validate_integration(bundle, envelope)
    envelope["fhir_release"] = "5.0.0"
    resource(bundle, "human-product")["meta"]["profile"] = ["http://hl7.org/fhir/StructureDefinition/MedicinalProductDefinition"]
    with pytest.raises(integration.ContractError, match="profile must be pinned"):
        integration.validate_integration(bundle, envelope)


def test_unmapped_source_facts_are_visible_and_keep_values(inputs):
    bundle, envelope = inputs
    outcomes = envelope["migration_outcomes"]
    assert {outcome["source_path"] for outcome in outcomes} == {
        "healthcare_service.valid_from", "management.valid_to", "accreditation.registered_subject",
    }
    assert all(outcome["state"] == "unmapped" and outcome["source_value"] for outcome in outcomes)
    assert binding(envelope, "outpatient-service")["entry"]["source_records"] == [outcomes[0]["source_record"]]
    del outcomes[0]["source_value"]
    with pytest.raises(integration.ContractError, match="unmapped outcome must retain"):
        integration.validate_integration(bundle, envelope)


def test_valid_fhir_reference_in_an_unreviewed_datatype_path_is_not_silently_skipped(inputs):
    bundle, envelope = inputs
    resource(bundle, "clinic-provider")["identifier"][0]["assigner"] = {
        "reference": "Organization/medicines-regulator", "type": "Organization",
    }
    with pytest.raises(integration.ContractError, match="reference path requires a reviewed contract addition"):
        integration.validate_integration(bundle, envelope)


def test_official_json_schema_does_not_claim_fhirpath_invariant_validation(inputs):
    bundle, _ = inputs
    organization = resource(bundle, "clinic-provider")
    organization["qualification"][0]["period"] = {
        "start": "2028-01-01T00:00:00Z", "end": "2020-01-01T00:00:00Z",
    }
    ingredient = resource(bundle, "human-ingredient")
    ingredient["substance"]["strength"][0]["presentationRatio"].pop("denominator")
    # These pass the published JSON Schema. The separate official Java authoring
    # check reports per-1 and rat-1; claiming this structural check proves them
    # would be a regression in the documented validation boundary.
    integration.validate_structure(organization)
    integration.validate_structure(ingredient)


def test_official_outcome_preserves_error_and_fatal_severities():
    outcome = {"resourceType": "OperationOutcome", "issue": [
        {"severity": "warning", "code": "business-rule"},
        {"severity": "error", "code": "invariant"},
        {"severity": "fatal", "code": "invalid"},
    ]}
    assert official.outcome_counts(outcome) == {"warning": 1, "error": 1, "fatal": 1}
    with pytest.raises(ValueError, match="OperationOutcome"):
        official.outcome_counts({"resourceType": "Bundle"})
