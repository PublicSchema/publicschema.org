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
    "CRVSPerson",
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


# Concept IDs whose kebab-case filename doesn't follow the naive
# "insert dash before each uppercase letter" algorithm.
_KEBAB_OVERRIDES = {
    "CRVSPerson": "crvs-person",
}


def _concept_id_to_kebab(concept_id: str) -> str:
    """Convert a PascalCase concept ID to a kebab-case filename stem."""
    if concept_id in _KEBAB_OVERRIDES:
        return _KEBAB_OVERRIDES[concept_id]
    return "".join(
        ("-" + c.lower() if c.isupper() and i > 0 else c.lower())
        for i, c in enumerate(concept_id)
    )


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
        kebab = _concept_id_to_kebab(concept_id)
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
            kebab = _concept_id_to_kebab(concept_id)
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
        kebab = _concept_id_to_kebab(concept_id)
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


class TestPersonDemographicProperties:
    """Person carries universal demographic properties used across domains."""

    DEMOGRAPHIC_PROPERTIES = [
        "literacy",
        "religion",
        "ethnic_group",
        "employment_status",
        "status_in_employment",
        "industry",
    ]

    def test_person_has_demographic_properties(self):
        """Person includes all universal demographic properties."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "person.yaml")
        for prop in self.DEMOGRAPHIC_PROPERTIES:
            assert prop in data["properties"], (
                f"Person should have property '{prop}'"
            )

    @pytest.mark.parametrize("prop_id", DEMOGRAPHIC_PROPERTIES)
    def test_demographic_property_file_exists(self, prop_id):
        """Each demographic property has a YAML file on disk."""
        path = SCHEMA_DIR / "properties" / f"{prop_id}.yaml"
        assert path.exists(), f"Missing property file: {path}"

    @pytest.mark.parametrize("prop_id", DEMOGRAPHIC_PROPERTIES)
    def test_demographic_property_has_trilingual_definition(self, prop_id):
        """Each demographic property has en, fr, es definitions."""
        data = _load_yaml(SCHEMA_DIR / "properties" / f"{prop_id}.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in data["definition"], (
                f"{prop_id} missing '{lang}' definition"
            )

    def test_demographic_properties_in_build(self):
        """All demographic properties appear in the build output for Person."""
        result = build_vocabulary(SCHEMA_DIR)
        person = result["concepts"]["Person"]
        prop_ids = {p["id"] for p in person["properties"]}
        for prop in self.DEMOGRAPHIC_PROPERTIES:
            assert prop in prop_ids, (
                f"Person build output should include '{prop}'"
            )

    def test_religion_has_no_vocabulary(self):
        """religion is free text (country-specific), no vocabulary."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "religion.yaml")
        assert data.get("vocabulary") is None

    def test_ethnic_group_has_no_vocabulary(self):
        """ethnic_group is free text (country-specific), no vocabulary."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "ethnic_group.yaml")
        assert data.get("vocabulary") is None

    def test_industry_has_no_vocabulary(self):
        """industry references ISIC Rev.4 but too large to enumerate."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "industry.yaml")
        assert data.get("vocabulary") is None

    def test_religion_is_restricted(self):
        """religion is GDPR Art.9 special category data."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "religion.yaml")
        assert data.get("sensitivity") == "restricted"

    def test_ethnic_group_is_restricted(self):
        """ethnic_group is GDPR Art.9 special category data."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "ethnic_group.yaml")
        assert data.get("sensitivity") == "restricted"


class TestDemographicVocabularies:
    """Vocabularies for literacy, employment-status, and status-in-employment."""

    @pytest.mark.parametrize("vocab_id", [
        "literacy",
        "employment-status",
        "status-in-employment",
    ])
    def test_vocabulary_file_exists(self, vocab_id):
        """Each new demographic vocabulary has a YAML file."""
        path = SCHEMA_DIR / "vocabularies" / f"{vocab_id}.yaml"
        assert path.exists(), f"Missing vocabulary file: {path}"

    @pytest.mark.parametrize("vocab_id", [
        "literacy",
        "employment-status",
        "status-in-employment",
    ])
    def test_vocabulary_loads_in_build(self, vocab_id):
        """New universal vocabularies appear in build output."""
        result = build_vocabulary(SCHEMA_DIR)
        assert vocab_id in result["vocabularies"], (
            f"Vocabulary {vocab_id} missing from build output"
        )

    def test_literacy_codes(self):
        """Literacy uses UNSD binary: literate / illiterate."""
        data = _load_yaml(SCHEMA_DIR / "vocabularies" / "literacy.yaml")
        codes = {v["code"] for v in data["values"]}
        assert codes == {"literate", "illiterate"}

    def test_employment_status_codes(self):
        """Employment status uses ILO 19th ICLS tripartite classification."""
        data = _load_yaml(SCHEMA_DIR / "vocabularies" / "employment-status.yaml")
        codes = {v["code"] for v in data["values"]}
        assert codes == {"employed", "unemployed", "outside_labour_force"}

    def test_status_in_employment_codes(self):
        """Status in employment uses ILO ICSE-18 categories."""
        data = _load_yaml(
            SCHEMA_DIR / "vocabularies" / "status-in-employment.yaml"
        )
        codes = {v["code"] for v in data["values"]}
        assert codes == {
            "employee",
            "employer",
            "own_account_worker",
            "contributing_family_worker",
            "cooperative_member",
        }


class TestCRVSPerson:
    """CRVSPerson is a temporal snapshot of a Person at the time of a vital event."""

    CRVS_PERSON_PROPERTIES = [
        "person",
        "nationality",
        "occupation",
        "education_level",
        "marital_status",
        "literacy",
        "religion",
        "ethnic_group",
        "employment_status",
        "status_in_employment",
        "industry",
        "place_of_usual_residence",
        "age_at_event",
    ]

    def test_crvs_person_file_exists(self):
        """CRVSPerson concept has a YAML file on disk."""
        path = SCHEMA_DIR / "concepts" / "crvs-person.yaml"
        assert path.exists()

    def test_crvs_person_domain_is_crvs(self):
        """CRVSPerson belongs to the CRVS domain."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        assert data["domain"] == "crvs"

    def test_crvs_person_has_all_snapshot_properties(self):
        """CRVSPerson carries all demographic snapshot properties."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        for prop in self.CRVS_PERSON_PROPERTIES:
            assert prop in data["properties"], (
                f"CRVSPerson should have property '{prop}'"
            )

    def test_crvs_person_subtypes_include_parent(self):
        """CRVSPerson lists Parent as a subtype."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        assert "Parent" in data["subtypes"]

    def test_age_at_event_property_exists(self):
        """age_at_event property has a YAML file."""
        path = SCHEMA_DIR / "properties" / "age_at_event.yaml"
        assert path.exists()

    def test_age_at_event_is_integer(self):
        """age_at_event is an integer property."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "age_at_event.yaml")
        assert data["type"] == "integer"

    def test_age_at_event_has_crvs_domain(self):
        """age_at_event is CRVS-specific."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "age_at_event.yaml")
        assert data.get("domain_override") == "crvs"

    def test_crvs_person_in_build(self):
        """CRVSPerson appears in the build output."""
        result = build_vocabulary(SCHEMA_DIR)
        assert "CRVSPerson" in result["concepts"]
        crvs_person = result["concepts"]["CRVSPerson"]
        assert crvs_person["domain"] == "crvs"


class TestParentLinkEntity:
    def test_parent_has_parental_role(self):
        """Parent carries parental_role as its own property."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "parental_role" in data["properties"]

    def test_parent_inherits_from_crvs_person(self):
        """Parent is a subtype of CRVSPerson."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "CRVSPerson" in data["supertypes"]

    def test_parent_does_not_directly_list_person(self):
        """person is inherited from CRVSPerson, not listed directly on Parent."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "person" not in data["properties"]
