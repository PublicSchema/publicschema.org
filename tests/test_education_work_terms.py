"""Invariants for the education, work and health facility reference terms."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDUCATION = yaml.safe_load((ROOT / "schema/education.yaml").read_text())
PROCESS_WORDING = ("draft covers", "review brief", "starter", "scheme-qualified", "consuming profile",
                   "registrystack", "array position", "an example profile", "this branch", "review")


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


@pytest.mark.parametrize("name", ["EducationProgramme", "ProfessionalQualification", "provider_programmes",
                                  "programme_award", "offering_award", "programme_classification",
                                  "offering_programme"])
def test_replaced_education_terms_stay_removed(name):
    for module in sorted((ROOT / "schema").glob("*.yaml")):
        authored = yaml.safe_load(module.read_text()) or {}
        assert name not in (authored.get("classes") or {}), module.name
        assert name not in (authored.get("slots") or {}), module.name


def test_definitions_carry_no_process_wording():
    texts = []
    for module in (EDUCATION,):
        for section in ("classes", "slots"):
            for name, definition in module[section].items():
                texts.append((name, definition.get("description", "")))
    for name, text in texts:
        assert not any(phrase in text.lower() for phrase in PROCESS_WORDING), name
        assert "—" not in text, name
