"""Invariants for the education, work and health facility reference terms."""

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDUCATION = yaml.safe_load((ROOT / "schema/education.yaml").read_text())
WORK = yaml.safe_load((ROOT / "schema/work.yaml").read_text())
IDENTITY = yaml.safe_load((ROOT / "schema/identity.yaml").read_text())
VOCABULARIES = yaml.safe_load((ROOT / "schema/vocabularies.yaml").read_text())
FORMS_OF_WORK = ["own_use_production_work", "employment_work", "unpaid_trainee_work",
                 "volunteer_work", "other_work_activities"]
PROCESS_WORDING = ("draft covers", "review brief", "starter", "scheme-qualified", "consuming profile",
                   "registrystack", "array position", "an example profile", "this branch", "review")


@pytest.fixture(scope="module")
def built(built_vocabulary):
    return built_vocabulary


def schema_validator(built, registry, kind):
    return jsonschema.Draft202012Validator(built["concept_schemas"][kind], registry=registry)


def alignments(definition):
    return {record["uri"]: record for record in json.loads(definition["annotations"]["external_alignments_json"])}


def test_form_of_work_is_the_closed_19th_icls_list():
    enum = VOCABULARIES["enums"]["FormOfWork"]
    assert enum["enum_uri"] == "publicschema:FormOfWork"
    assert list(enum["permissible_values"]) == FORMS_OF_WORK
    assert WORK["slots"]["work_form"]["range"] == "FormOfWork"
    assert WORK["slots"]["work_status"]["range"] == "CodedValue"


def test_work_form_accepts_only_a_form_of_work(built, schema_registry):
    validator = schema_validator(built, schema_registry, "WorkRelationship")
    for value in FORMS_OF_WORK:
        validator.validate({"work_form": value})
    coded = {"@type": "CodedValue", "code_value": "employment_work", "code_scheme": "https://example.org/forms"}
    for value in ("employment", coded):
        with pytest.raises(jsonschema.ValidationError):
            validator.validate({"work_form": value})


def test_work_classes_stay_distinct():
    assert {"WorkRelationship", "ProfessionalLicense", "PracticeRole"} == set(WORK["classes"])
    assert "person" in WORK["classes"]["PracticeRole"]["slots"]
    # Agricultural work functions belong to the holding work assignment, not to general work.
    assert "work_functions" not in WORK["classes"]["WorkRelationship"]["slots"]


def test_education_programs_use_split_classifications_and_one_qualification_slot():
    classes, slots = EDUCATION["classes"], EDUCATION["slots"]
    assert classes["EducationProgram"]["class_uri"] == "publicschema:edu/EducationProgram"
    for name in ("program_level", "program_field"):
        assert slots[name]["range"] == "CodedValue" and slots[name]["multivalued"] is True
        assert name in classes["EducationProgram"]["slots"]
    awarded = slots["qualification_awarded"]
    assert awarded["range"] == "uri" and awarded["multivalued"] is True
    assert awarded["slot_uri"] == "publicschema:edu/qualification_awarded"
    for owner in ("EducationProgram", "EducationOffering"):
        assert "qualification_awarded" in classes[owner]["slots"]
    assert "offering_program" in classes["EducationOffering"]["slots"]
    assert slots["offering_program"]["range"] == "EducationProgram"
    assert not classes["EducationProvider"].get("slots")


def test_awarded_qualification_is_a_root_term_with_joint_awarders():
    qualification = EDUCATION["classes"]["AwardedQualification"]
    assert qualification["class_uri"] == "publicschema:AwardedQualification"
    assert "source_domain" not in qualification["annotations"]
    awarder = EDUCATION["slots"]["qualification_awarder"]
    assert awarder["range"] == "Organization" and awarder["multivalued"] is True


def test_a_work_relationship_can_name_its_legal_employer_apart_from_the_economic_unit(built):
    # With an agency or a group employer, the unit the work is for is not the party bound by the contract.
    assert "legal_employer" in WORK["classes"]["WorkRelationship"]["slots"]
    prop = built["properties"]["legal_employer"]
    assert prop["type"] == "uri"
    assert "person or organization" in prop["definition"]["en"]
    assert "agency" in prop["definition"]["en"]


def test_an_awarded_qualification_can_name_the_qualification_it_awards(built):
    # A title string cannot be matched to a qualifications register entry or to a program's qualification_awarded.
    assert "qualification_definition" in EDUCATION["classes"]["AwardedQualification"]["slots"]
    prop = built["properties"]["qualification_definition"]
    assert prop["type"] == "uri"
    assert prop["sensitivity"] == "sensitive"
    assert "qualification_awarded" in prop["definition"]["en"]
    assert "http://data.europa.eu/snb/model/elm/specifiedBy" in alignments(EDUCATION["slots"]["qualification_definition"])


@pytest.mark.parametrize("name", ["EducationProgramme", "ProfessionalQualification", "provider_programmes",
                                  "programme_award", "offering_award", "programme_classification",
                                  "offering_programme"])
def test_replaced_education_terms_stay_removed(name):
    for module in sorted((ROOT / "schema").glob("*.yaml")):
        authored = yaml.safe_load(module.read_text()) or {}
        assert name not in (authored.get("classes") or {}), module.name
        assert name not in (authored.get("slots") or {}), module.name


def test_health_facility_aligns_with_fhir_location_not_an_organization():
    facility = IDENTITY["classes"]["HealthFacility"]
    assert facility["class_uri"] == "publicschema:health/HealthFacility"
    assert facility["close_mappings"] == ["fhir:Location"]
    assert facility["related_mappings"] == ["schema:MedicalOrganization"]
    records = alignments(facility)
    assert records["http://hl7.org/fhir/Location"]["match"] == "close"
    assert "managingOrganization" in records["http://hl7.org/fhir/Location"]["note"]
    assert records["https://schema.org/MedicalOrganization"]["match"] == "related"


def test_definitions_carry_no_process_wording():
    texts = []
    for module in (EDUCATION, WORK):
        for section in ("classes", "slots"):
            for name, definition in module[section].items():
                texts.append((name, definition.get("description", "")))
    for name, value in VOCABULARIES["enums"]["FormOfWork"]["permissible_values"].items():
        texts.append((name, value["description"]))
    for name, text in texts:
        assert not any(phrase in text.lower() for phrase in PROCESS_WORDING), name
        assert "—" not in text, name


@pytest.mark.parametrize("slot,counterparts", [
    ("work_status", ("status_in_employment", "employment_status")),
    ("profession_code", ("occupation",)),
    ("program_level", ("education_level", "school_level_served")),
])
def test_coded_work_and_education_slots_point_to_the_person_level_enums(built, slot, counterparts):
    definition = built["properties"][slot]["definition"]
    for language in ("en", "fr", "es"):
        assert all(name in definition[language] for name in counterparts), language
