"""Tests for the CRVS domain: concepts, vocabularies, and event subtyping."""

from pathlib import Path

import pytest
import yaml

from tests.conftest import SCHEMA_DIR

from build.build import build_vocabulary
from build.validate import validate_schema_dir


CRVS_CONCEPTS = [
    "VitalEvent",
    "Birth",
    "Death",
    "FetalDeath",
    "Marriage",
    "MarriageTermination",
    "Divorce",
    "Annulment",
    "Adoption",
    "PaternityRecognition",
    "Legitimation",
    "CivilStatusRecord",
    "CivilStatusAnnotation",
    "Parent",
    "Certificate",
    "FamilyRegister",
]

CRVS_VOCABULARIES = [
    "registration-status",
    "registration-type",
    "parental-role",
    "birth-type",
    "birth-attendant",
    "manner-of-death",
    "cause-of-death-method",
    "marriage-type",
    "adoption-type",
    "annotation-type",
    "civil-status-record-type",
    "certificate-document-type",
    "certificate-format",
    "place-type",
    "family-register-status",
]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


class TestCrvsSchemaValidation:
    def test_schema_validates_with_crvs_domain(self):
        """Adding the CRVS domain should not introduce validation errors."""
        issues = validate_schema_dir(SCHEMA_DIR)
        errors = [e for e in issues if e.severity == "error"]
        assert errors == [], (
            f"Validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )


class TestCrvsConcepts:
    @pytest.mark.parametrize("concept_id", CRVS_CONCEPTS)
    def test_concept_file_exists(self, concept_id):
        """Each CRVS concept has a YAML file on disk."""
        # Kebab-case filename from PascalCase id.
        kebab = "".join(
            ("-" + c.lower() if c.isupper() and i > 0 else c.lower())
            for i, c in enumerate(concept_id)
        )
        path = SCHEMA_DIR / "concepts" / f"{kebab}.yaml"
        assert path.exists(), f"Missing concept file: {path}"

    def test_concepts_load_in_build(self):
        """All CRVS concepts appear in the build output."""
        result = build_vocabulary(SCHEMA_DIR)
        for concept_id in CRVS_CONCEPTS:
            assert concept_id in result["concepts"], (
                f"Concept {concept_id} missing from build output"
            )

    def test_crvs_scoped_concepts_have_domain_crvs(self):
        """CRVS concepts carry domain=crvs and produce /crvs/... URIs."""
        result = build_vocabulary(SCHEMA_DIR)
        for concept_id in CRVS_CONCEPTS:
            concept = result["concepts"][concept_id]
            assert concept["domain"] == "crvs", (
                f"{concept_id} should have domain=crvs, got {concept['domain']}"
            )
            assert f"/crvs/{concept_id}" in concept["uri"], (
                f"{concept_id} URI should contain /crvs/, got {concept['uri']}"
            )
            assert concept["path"] == f"/crvs/{concept_id}"

    def test_all_crvs_concepts_draft_maturity(self):
        """New CRVS concepts start at draft maturity."""
        for concept_id in CRVS_CONCEPTS:
            kebab = "".join(
                ("-" + c.lower() if c.isupper() and i > 0 else c.lower())
                for i, c in enumerate(concept_id)
            )
            path = SCHEMA_DIR / "concepts" / f"{kebab}.yaml"
            data = _load_yaml(path)
            assert data["maturity"] == "draft", (
                f"{concept_id} should start at maturity=draft"
            )


class TestSupertypeSubtypeSymmetry:
    def test_event_has_vital_event_subtype(self):
        """Event.subtypes must include VitalEvent after the update."""
        event = _load_yaml(SCHEMA_DIR / "concepts" / "event.yaml")
        assert "VitalEvent" in event["subtypes"], (
            "Event.subtypes should include VitalEvent"
        )

    def test_vital_event_supertype_is_event(self):
        """VitalEvent lists Event as its only supertype."""
        vital_event = _load_yaml(SCHEMA_DIR / "concepts" / "vital-event.yaml")
        assert vital_event["supertypes"] == ["Event"]

    def test_vital_event_subtypes(self):
        """VitalEvent subtypes include all concrete vital event records."""
        vital_event = _load_yaml(SCHEMA_DIR / "concepts" / "vital-event.yaml")
        expected = {
            "Birth",
            "Death",
            "FetalDeath",
            "Marriage",
            "MarriageTermination",
            "Adoption",
            "PaternityRecognition",
            "Legitimation",
        }
        assert set(vital_event["subtypes"]) == expected

    @pytest.mark.parametrize(
        "concept_file,expected_supertype",
        [
            ("birth.yaml", "VitalEvent"),
            ("death.yaml", "VitalEvent"),
            ("fetal-death.yaml", "VitalEvent"),
            ("marriage.yaml", "VitalEvent"),
            ("marriage-termination.yaml", "VitalEvent"),
            ("adoption.yaml", "VitalEvent"),
            ("paternity-recognition.yaml", "VitalEvent"),
            ("legitimation.yaml", "VitalEvent"),
            ("divorce.yaml", "MarriageTermination"),
            ("annulment.yaml", "MarriageTermination"),
        ],
    )
    def test_supertype_chain(self, concept_file, expected_supertype):
        """Concepts list the expected supertype."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / concept_file)
        assert expected_supertype in data["supertypes"], (
            f"{concept_file}: expected {expected_supertype} in supertypes, "
            f"got {data['supertypes']}"
        )

    def test_marriage_termination_subtypes(self):
        """MarriageTermination lists Divorce and Annulment as subtypes."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "marriage-termination.yaml")
        assert set(data["subtypes"]) == {"Divorce", "Annulment"}


class TestAbstractConcepts:
    @pytest.mark.parametrize("concept_id", ["VitalEvent", "MarriageTermination"])
    def test_abstract_flag_true_in_yaml(self, concept_id):
        """Abstract supertypes declare abstract: true in their YAML."""
        kebab = "".join(
            ("-" + c.lower() if c.isupper() and i > 0 else c.lower())
            for i, c in enumerate(concept_id)
        )
        data = _load_yaml(SCHEMA_DIR / "concepts" / f"{kebab}.yaml")
        assert data.get("abstract") is True, (
            f"{concept_id} should be marked abstract"
        )

    def test_abstract_flag_propagates_to_build_output(self):
        """Build output carries the abstract flag for abstract concepts."""
        result = build_vocabulary(SCHEMA_DIR)
        assert result["concepts"]["VitalEvent"]["abstract"] is True
        assert result["concepts"]["MarriageTermination"]["abstract"] is True
        # Concrete subtypes default to False
        assert result["concepts"]["Birth"]["abstract"] is False
        assert result["concepts"]["Divorce"]["abstract"] is False


class TestCrvsVocabularies:
    @pytest.mark.parametrize("vocab_id", CRVS_VOCABULARIES)
    def test_vocabulary_file_exists(self, vocab_id):
        """Each CRVS vocabulary has a YAML file under vocabularies/crvs/."""
        path = SCHEMA_DIR / "vocabularies" / "crvs" / f"{vocab_id}.yaml"
        assert path.exists(), f"Missing vocabulary file: {path}"

    def test_vocabularies_load_in_build(self):
        """All CRVS vocabularies appear in build output keyed as crvs/<id>."""
        result = build_vocabulary(SCHEMA_DIR)
        for vocab_id in CRVS_VOCABULARIES:
            key = f"crvs/{vocab_id}"
            assert key in result["vocabularies"], (
                f"Vocabulary {key} missing from build output"
            )
            assert result["vocabularies"][key]["id"] == vocab_id
            assert result["vocabularies"][key]["domain"] == "crvs"
            assert result["vocabularies"][key]["path"] == f"/vocab/{key}"

    def test_vocabularies_have_domain_crvs(self):
        """CRVS vocabularies carry domain=crvs."""
        for vocab_id in CRVS_VOCABULARIES:
            path = SCHEMA_DIR / "vocabularies" / "crvs" / f"{vocab_id}.yaml"
            data = _load_yaml(path)
            assert data.get("domain") == "crvs", (
                f"{vocab_id} should have domain=crvs"
            )

    @pytest.mark.parametrize(
        "vocab_id,expected_codes",
        [
            (
                "registration-status",
                {
                    "declared",
                    "pending_validation",
                    "registered",
                    "rejected",
                    "cancelled",
                    "corrected",
                    "archived",
                },
            ),
            (
                "registration-type",
                {"current", "late", "court_ordered", "reconstruction"},
            ),
            (
                "parental-role",
                {
                    "biological_mother",
                    "biological_father",
                    "legal_mother",
                    "legal_father",
                    "adoptive_mother",
                    "adoptive_father",
                    "surrogate_mother",
                },
            ),
            (
                "birth-type",
                {"single", "twin", "triplet", "quadruplet", "quintuplet", "higher_order"},
            ),
            (
                "birth-attendant",
                {"physician", "midwife", "nurse", "traditional_birth_attendant", "other", "none"},
            ),
            (
                "manner-of-death",
                {
                    "natural",
                    "accident",
                    "intentional_self_harm",
                    "assault",
                    "legal_intervention",
                    "war",
                    "pending_investigation",
                    "could_not_be_determined",
                },
            ),
            (
                "cause-of-death-method",
                {"physician_certified", "verbal_autopsy", "coroner", "lay_reporting", "other"},
            ),
            ("marriage-type", {"civil", "religious", "customary", "common_law"}),
            ("adoption-type", {"full", "simple"}),
            (
                "annotation-type",
                {
                    "court_ordered_correction",
                    "nationality_change",
                    "name_change",
                    "gender_marker_change",
                },
            ),
            (
                "civil-status-record-type",
                {
                    "birth",
                    "marriage",
                    "death",
                    "paternity_recognition",
                    "supplementary_judgment",
                    "court_ordered_substitute",
                },
            ),
            (
                "certificate-document-type",
                {
                    "birth_certificate",
                    "death_certificate",
                    "marriage_certificate",
                    "divorce_certificate",
                    "adoption_certificate",
                    "annulment_certificate",
                },
            ),
            ("certificate-format", {"full_copy", "extract", "multilingual_extract"}),
            ("place-type", {"health_facility", "home", "en_route", "other", "unknown"}),
            ("family-register-status", {"active", "closed", "split", "merged"}),
        ],
    )
    def test_vocabulary_codes(self, vocab_id, expected_codes):
        """Each vocabulary contains the expected set of codes."""
        path = SCHEMA_DIR / "vocabularies" / "crvs" / f"{vocab_id}.yaml"
        data = _load_yaml(path)
        codes = {v["code"] for v in data["values"]}
        assert codes == expected_codes, (
            f"{vocab_id}: expected {expected_codes}, got {codes}"
        )


class TestParentLinkEntity:
    def test_parent_has_person_and_role(self):
        """Parent is a link entity combining person and parental_role."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "person" in data["properties"]
        assert "parental_role" in data["properties"]

    def test_parent_has_no_supertypes(self):
        """Parent stands alone; it is not a subtype of Event or anything else."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert data["supertypes"] == []
