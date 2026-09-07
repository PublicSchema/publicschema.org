"""Public service history through production exports and the named synthetic profile."""

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
from rdflib.namespace import RDFS, SKOS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import DEFAULT_CONTEXT_URL, write_shacl, write_turtle
from build.rdf_export_legacy import build_turtle as build_legacy_turtle

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/public-services"
BASE = "https://example.org/public-services/"
PS = Namespace("https://publicschema.org/")
RECORDS = json.loads((EXAMPLES / "records.json").read_text())
CONFIG = json.loads((EXAMPLES / "profile.json").read_text())
spec = importlib.util.spec_from_file_location("public_services_profile", EXAMPLES / "profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


def record(records, suffix):
    return next(item for item in records if item["@id"] == BASE + suffix)


def ref(suffix, kind):
    return {"@id": BASE + suffix, "@type": kind}


def expand_graph(records, context):
    def loader(url, options=None):
        assert url == DEFAULT_CONTEXT_URL
        return {"contextUrl": None, "documentUrl": url, "document": context}

    expanded = jsonld.expand(records, options={"documentLoader": loader})
    quads = jsonld.to_rdf(expanded, {"format": "application/n-quads"})
    return Graph().parse(data=quads, format="nquads")


@pytest.fixture(scope="module")
def native_ontology(tmp_path_factory):
    path = tmp_path_factory.mktemp("public-services-ontology") / "vocabulary.ttl"
    composite = ROOT / "schema/publicschema.yaml"
    return Graph().parse(write_turtle(path, composite=composite), format="turtle")


@pytest.fixture(scope="module")
def exports(tmp_path_factory, native_ontology):
    built = build_vocabulary(ROOT / "schema")
    path = tmp_path_factory.mktemp("public-services-exports")
    composite = ROOT / "schema/publicschema.yaml"
    shapes = Graph().parse(write_shacl(path / "shapes.ttl", composite=composite), format="turtle")
    hierarchy = Graph()
    for triple in native_ontology.triples((None, RDFS.subClassOf, None)):
        hierarchy.add(triple)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema))
        for schema in built["concept_schemas"].values()
    )
    return built, shapes, hierarchy, registry


def test_catalogue_alignment_metadata_reaches_jsonld_and_both_rdf_projections(exports, native_ontology):
    built, _, _, _ = exports
    authored = yaml.safe_load((ROOT / "schema/public_services.yaml").read_text())
    expected = {
        "PublicService": ("classes", "concepts", "cpsv_ap", "http://purl.org/vocab/cpsv#PublicService"),
        "OrganizationalChangeEvent": ("classes", "concepts", "w3c_org", "http://www.w3.org/ns/org#ChangeEvent"),
        "service_competent_authorities": ("slots", "properties", "cpsv_ap", "http://data.europa.eu/m8g/hasCompetentAuthority"),
        "original_organizations": ("slots", "properties", "w3c_org", "http://www.w3.org/ns/org#originalOrganization"),
        "resulting_organizations": ("slots", "properties", "w3c_org", "http://www.w3.org/ns/org#resultingOrganization"),
    }
    # Exercise the compatibility RDF bridge with the actual five generated term
    # documents, without rebuilding unrelated exports or allowing lost alignments.
    docs = {f"{catalogue}/{name}.jsonld": built["jsonld_docs"][f"{catalogue}/{name}.jsonld"]
            for name, (_, catalogue, _, _) in expected.items()}
    legacy = Graph().parse(data=build_legacy_turtle({**built, "jsonld_docs": docs}), format="turtle")
    for name, (section, catalogue, vocabulary_id, uri) in expected.items():
        source = json.loads(authored[section][name]["annotations"]["external_alignments_json"])[0]
        alignment = built[catalogue][name]["external_equivalents"][vocabulary_id]
        assert alignment["uri"] == uri
        assert alignment["match"] == "close"
        assert alignment["note"] == source["note"]
        assert alignment["vocabulary"] == source["vocabulary"]
        assert "does not implement" in alignment["note"]
        triple = (PS[name], SKOS.closeMatch, URIRef(uri))
        document = {**docs[f"{catalogue}/{name}.jsonld"], "@context": built["context"]["@context"]}
        document_graph = Graph().parse(data=json.dumps(document), format="json-ld")
        assert triple in document_graph
        assert triple in legacy
        assert triple in native_ontology


def validator(exports, kind):
    built, _, _, registry = exports
    return jsonschema.Draft202012Validator(
        built["concept_schemas"][kind], registry=registry,
        format_checker=jsonschema.FormatChecker(),
    )


def test_permit_history_validates_in_both_export_formats_and_local_profile(exports):
    built, shapes, hierarchy, _ = exports
    before = copy.deepcopy(RECORDS)
    for item in RECORDS:
        validator(exports, item["@type"]).validate(item)
    graph = expand_graph(RECORDS, built["context"])
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=hierarchy)
    assert conforms, report
    profile.validate_journey(RECORDS, CONFIG)
    assert RECORDS == before
    for source, predicate, target in (
        ("grant-decision", "decision_authorizations", "business-permit"),
        ("permit-suspension", "action_subject", "business-permit"),
        ("business-appeal", "challenged_decision", "suspension-decision"),
        ("review-decision", "resolves_appeal", "business-appeal"),
        ("authority-succession", "original_organizations", "former-office"),
        ("authority-succession", "resulting_organizations", "successor-agency"),
    ):
        assert (URIRef(BASE + source), PS[predicate], URIRef(BASE + target)) in graph


@pytest.mark.parametrize("suffix,field,bad", [
    ("business-application", "submitted_at", "yesterday"),
    ("business-application", "public_service", [ref("permit-service", "PublicService")]),
    ("grant-decision", "decision_outcome", 7),
    ("grant-decision", "decision_authorizations", ref("business-permit", "Authorization")),
    ("business-appeal", "challenged_decision", [ref("suspension-decision", "AdministrativeDecision")]),
    ("authority-succession", "effective_at", "2026-08-01"),
])
def test_malformed_shapes_are_rejected_by_actual_json_schema(exports, suffix, field, bad):
    invalid = copy.deepcopy(record(RECORDS, suffix))
    invalid[field] = bad
    assert list(validator(exports, invalid["@type"]).iter_errors(invalid))


def test_wrong_decision_output_type_fails_shacl_even_with_an_existing_identity(exports):
    built, shapes, hierarchy, _ = exports
    invalid = copy.deepcopy(RECORDS)
    record(invalid, "grant-decision")["decision_authorizations"] = [ref("business", "LegalEntity")]
    conforms, _, _ = validate(expand_graph(invalid, built["context"]), shacl_graph=shapes, ont_graph=hierarchy)
    assert not conforms


@pytest.mark.parametrize("suffix,changes,message", [
    ("business-application", {"service_applicant": BASE + "missing"}, "missing referenced record"),
    ("business-representation", {"represented_subject": BASE + "resident"}, "represented subject mismatch"),
    ("business-representation", {"representative_actor": BASE + "resident"}, "actor or represented subject mismatch"),
    ("business-representation", {"end_date": "2026-04-30"}, "outside representation period"),
    ("business-permit", {"registered_subject": BASE + "resident"}, "permit subject differs"),
    ("business-permit", {"registration_authority": ref("successor-agency", "PublicOrganization")}, "permit issuer differs"),
    ("permit-suspension", {"action_subject": BASE + "business"}, "action subject differs"),
    ("business-appeal", {"challenged_decision": ref("business-permit", "Authorization")}, "wrong referenced type"),
    ("business-appeal", {"submitted_at": "2026-08-30T10:00:00Z"}, "appeal precedes challenged decision"),
    ("review-decision", {"decision_subject": BASE + "resident"}, "differs from challenged decision subject"),
    ("review-decision", {"decision_authority": ref("former-office", "PublicOrganization")}, "differs from reviewing authority"),
    ("authority-succession", {"resulting_organizations": [ref("former-office", "PublicOrganization")]}, "distinct resulting identity"),
])
def test_profile_rejects_semantic_counterexamples(suffix, changes, message):
    invalid = copy.deepcopy(RECORDS)
    record(invalid, suffix).update(changes)
    with pytest.raises(profile.ProfileError, match=message):
        profile.validate_journey(invalid, CONFIG)


def test_correspondence_role_text_cannot_grant_application_or_appeal_authority():
    changed = copy.deepcopy(RECORDS)
    role = record(changed, "business-representation")
    role["representation_scope"] = "Correspondence only."
    correspondence = copy.deepcopy(CONFIG)
    correspondence["representation_grants"][0]["allowed_submission_types"] = ["Correspondence"]
    with pytest.raises(profile.ProfileError, match="no bound grant"):
        profile.validate_journey(changed, correspondence)
    # Changing prose cannot promote a correspondence grant into application authority.
    role["representation_scope"] = "All applications and appeals are allowed."
    with pytest.raises(profile.ProfileError, match="no bound grant"):
        profile.validate_journey(changed, correspondence)
    # Only the explicit bound profile grant changes the synthetic authorization result.
    profile.validate_journey(changed, CONFIG)
    applications_only = copy.deepcopy(CONFIG)
    applications_only["representation_grants"][0]["allowed_submission_types"] = ["ServiceApplication"]
    with pytest.raises(profile.ProfileError, match="business-appeal.*no bound grant"):
        profile.validate_journey(changed, applications_only)
    wrong_service = copy.deepcopy(CONFIG)
    wrong_service["representation_grants"][0]["service_uri"] = BASE + "another-service"
    with pytest.raises(profile.ProfileError, match="no bound grant"):
        profile.validate_journey(changed, wrong_service)


@pytest.mark.parametrize("end_date,appeal_time,message", [
    ("2026-09-04", "2026-09-03T10:00:00Z", None),
    ("2026-09-03", "2026-09-02T23:59:59Z", None),
    ("2026-09-03", "2026-09-03T10:00:00Z", "outside representation period"),
    ("2026-09-03", "2026-09-02T23:30:00-01:00", "outside representation period"),
])
def test_representation_covers_start_day_and_stops_before_first_inactive_utc_day(
    end_date, appeal_time, message,
):
    changed = copy.deepcopy(RECORDS)
    # The application is filed on May 2, which remains an included start day.
    record(changed, "business-representation").update(start_date="2026-05-02", end_date=end_date)
    record(changed, "business-appeal")["submitted_at"] = appeal_time
    if message:
        with pytest.raises(profile.ProfileError, match=message):
            profile.validate_journey(changed, CONFIG)
    else:
        profile.validate_journey(changed, CONFIG)


def test_empty_representation_interval_is_rejected_but_one_day_permission_remains_valid():
    changed = copy.deepcopy(RECORDS)
    record(changed, "business-permit").update(valid_from="2026-05-11", valid_to="2026-05-11")
    profile.validate_journey(changed, CONFIG)
    record(changed, "business-representation").update(start_date="2026-05-02", end_date="2026-05-02")
    with pytest.raises(profile.ProfileError, match="empty or reversed representation period"):
        profile.validate_journey(changed, CONFIG)


@pytest.mark.parametrize("form", ["uri", "id"])
def test_class_reference_forms_preserve_the_complete_permit_journey(exports, form):
    def convert(value):
        if isinstance(value, dict):
            if "@id" in value and set(value) <= {"@id", "@type"}:
                return value["@id"] if form == "uri" else {"@id": value["@id"]}
            return {key: convert(item) for key, item in value.items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        return value

    changed = convert(RECORDS)
    for item in changed:
        validator(exports, item["@type"]).validate(item)
    profile.validate_journey(changed, CONFIG)
    built, shapes, hierarchy, _ = exports
    graph = expand_graph(changed, built["context"])
    conforms, _, report = validate(graph, shacl_graph=shapes, ont_graph=hierarchy)
    assert conforms, report
    assert (URIRef(BASE + "grant-decision"), PS.decision_authorizations, URIRef(BASE + "business-permit")) in graph
    assert (URIRef(BASE + "suspension-decision"), PS.decision_regulatory_actions, URIRef(BASE + "permit-suspension")) in graph


@pytest.mark.parametrize("form", ["uri", "id"])
@pytest.mark.parametrize("suffix,field,target,message", [
    ("grant-decision", "decision_authorizations", "missing", "missing referenced record"),
    ("grant-decision", "decision_authorizations", "business", "wrong referenced type"),
    ("suspension-decision", "decision_regulatory_actions", "missing", "missing referenced record"),
    ("suspension-decision", "decision_regulatory_actions", "business-permit", "wrong referenced type"),
])
def test_decision_output_reference_failures_are_addressed_profile_errors(
    exports, form, suffix, field, target, message,
):
    changed = copy.deepcopy(RECORDS)
    value = BASE + target
    record(changed, suffix)[field] = [value if form == "uri" else {"@id": value}]
    validator(exports, "AdministrativeDecision").validate(record(changed, suffix))
    with pytest.raises(profile.ProfileError, match=message):
        profile.validate_journey(changed, CONFIG)


@pytest.mark.parametrize("form", ["uri", "id"])
def test_evidence_and_outcome_values_can_resolve_local_identified_records(exports, form):
    changed = copy.deepcopy(RECORDS)
    decision = record(changed, "grant-decision")
    evidence = {"@context": DEFAULT_CONTEXT_URL, "@id": BASE + "grant-evidence", **decision["evidence_assertions"][0]}
    outcome = {"@context": DEFAULT_CONTEXT_URL, "@id": BASE + "grant-outcome", **decision["decision_outcome"]}
    changed.extend([evidence, outcome])
    decision["evidence_assertions"] = [evidence["@id"] if form == "uri" else {"@id": evidence["@id"]}]
    decision["decision_outcome"] = outcome["@id"] if form == "uri" else {"@id": outcome["@id"]}
    for item in changed:
        validator(exports, item["@type"]).validate(item)
    profile.validate_journey(changed, CONFIG)
    evidence["assertion_uri"] = BASE + "review-decision"
    with pytest.raises(profile.ProfileError, match="evidence is about a different assertion"):
        profile.validate_journey(changed, CONFIG)


@pytest.mark.parametrize("field,target,message", [
    ("evidence_assertions", "missing", "missing referenced record"),
    ("evidence_assertions", "business", "wrong referenced type"),
    ("decision_outcome", "missing", "missing referenced record"),
    ("decision_outcome", "business", "wrong referenced type"),
])
def test_structured_value_uri_failures_are_addressed_profile_errors(field, target, message):
    changed = copy.deepcopy(RECORDS)
    value = BASE + target
    record(changed, "grant-decision")[field] = [value] if field == "evidence_assertions" else value
    with pytest.raises(profile.ProfileError, match=message):
        profile.validate_journey(changed, CONFIG)


def test_individuals_and_businesses_share_application_shape_without_software_applicants(exports):
    for suffix in ("business-application", "resident-application"):
        validator(exports, "ServiceApplication").validate(record(RECORDS, suffix))
    profile.validate_journey(RECORDS, CONFIG)
    invalid = copy.deepcopy(RECORDS)
    record(invalid, "resident")["@type"] = "SoftwareAgent"
    with pytest.raises(profile.ProfileError, match="wrong referenced type SoftwareAgent"):
        profile.validate_journey(invalid, CONFIG)


def test_shared_applications_preserve_the_existing_social_protection_receiver_boundary(exports):
    built, _, hierarchy, _ = exports
    assert PS.Party not in set(hierarchy.transitive_objects(PS.Organization, RDFS.subClassOf))
    assert (PS.ServiceApplication, RDFS.subClassOf, PS.Event) in hierarchy
    program_uri = URIRef(built["concepts"]["sp/Program"]["uri"])
    enrollment_uri = URIRef(built["concepts"]["sp/Enrollment"]["uri"])
    assert program_uri not in set(hierarchy.transitive_objects(PS.PublicService, RDFS.subClassOf))
    assert enrollment_uri not in set(hierarchy.transitive_objects(PS.ServiceApplication, RDFS.subClassOf))


def test_a_suspension_cannot_be_made_person_or_business_wide_by_matching_both_links():
    invalid = copy.deepcopy(RECORDS)
    record(invalid, "suspension-decision")["decision_subject"] = BASE + "business"
    record(invalid, "permit-suspension")["action_subject"] = BASE + "business"
    with pytest.raises(profile.ProfileError, match="suspension must target a permission"):
        profile.validate_journey(invalid, CONFIG)


def test_successor_does_not_rewrite_historical_authorities_or_permission():
    profile.validate_journey(RECORDS, CONFIG)
    grant = record(RECORDS, "grant-decision")
    permit = record(RECORDS, "business-permit")
    service = record(RECORDS, "permit-service")
    assert grant["decision_authority"]["@id"] == permit["registration_authority"]["@id"]
    assert grant["decision_authority"] not in service["service_competent_authorities"]
    assert record(RECORDS, "office-name-correction")["subject_uri"] == BASE + "former-office"
    changed = copy.deepcopy(RECORDS)
    record(changed, "grant-decision")["decision_authority"] = ref("successor-agency", "PublicOrganization")
    record(changed, "business-permit")["registration_authority"] = ref("successor-agency", "PublicOrganization")
    with pytest.raises(profile.ProfileError, match="authority predates its creation"):
        profile.validate_journey(changed, CONFIG)
    # A filed appeal and a later determination leave the original grant intact.
    assert permit["valid_to"] == "2026-12-31"
    assert "decision_authorizations" not in record(RECORDS, "review-decision")
    assert record(RECORDS, "authority-succession")["effective_at"] < record(RECORDS, "authority-succession")["recorded_at"]


def test_partial_reference_description_is_not_a_complete_local_submission(exports):
    partial = {"@context": DEFAULT_CONTEXT_URL, **ref("partial", "ServiceApplication")}
    validator(exports, "ServiceApplication").validate(partial)
    with pytest.raises(profile.ProfileError, match="public_service: required"):
        profile.validate_journey([partial], CONFIG)
    local = copy.deepcopy(record(RECORDS, "grant-decision"))
    local["decision_outcome"]["code_value"] = "jurisdiction-specific-unmapped"
    validator(exports, "AdministrativeDecision").validate(local)
    invalid = [item for item in RECORDS if item["@id"] != local["@id"]] + [local]
    with pytest.raises(profile.ProfileError, match="unsupported local outcome code"):
        profile.validate_journey(invalid, CONFIG)


def test_bare_outcome_reference_is_not_interpreted_as_a_local_code(exports):
    invalid = copy.deepcopy(RECORDS)
    decision = record(invalid, "grant-decision")
    decision["decision_outcome"] = "granted"
    # Existing class-valued JSON fields accept string identifier references.
    # The string must resolve to a CodedValue; a bare label is not a code scheme.
    validator(exports, "AdministrativeDecision").validate(decision)
    with pytest.raises(profile.ProfileError, match="missing referenced record granted"):
        profile.validate_journey(invalid, CONFIG)


def test_declared_reference_type_does_not_override_resolved_record_type():
    invalid = copy.deepcopy(RECORDS)
    record(invalid, "grant-decision")["decision_authorizations"] = [ref("business", "Authorization")]
    with pytest.raises(profile.ProfileError, match="declared type disagrees"):
        profile.validate_journey(invalid, CONFIG)


def test_duplicate_identifiers_do_not_silently_replace_historical_records():
    with pytest.raises(profile.ProfileError, match="duplicate record identity"):
        profile.validate_journey(RECORDS + [copy.deepcopy(record(RECORDS, "grant-decision"))], CONFIG)
