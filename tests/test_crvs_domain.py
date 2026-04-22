"""Tests for the CRVS domain: concepts, vocabularies, and event subtyping."""

from pathlib import Path

import pytest
import yaml

from build.build import build_vocabulary
from build.validate import validate_schema_dir
from tests.conftest import SCHEMA_DIR

CRVS_CONCEPTS = [
    "VitalEvent",
    "Birth",
    "Death",
    "FetalDeath",
    "Marriage",
    "MarriageTermination",
    "Adoption",
    "PaternityRecognition",
    "Legitimation",
    "CivilStatusRecord",
    "CivilStatusAnnotation",
    "Parent",
    "Person",
    "Certificate",
    "FamilyRegister",
]

CRVS_VOCABULARIES = [
    "registration-status",
    "registration-type",
    "parental-role",
    "parent-establishment-basis",
    "birth-type",
    "birth-attendant",
    "manner-of-death",
    "cause-of-death-method",
    "marriage-type",
    "marriage-termination-type",
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
# crvs/Person lives in crvs-person.yaml to avoid filesystem collision with
# the root person.yaml.
_KEBAB_OVERRIDES = {
    "Person": "crvs-person",
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
        # CRVS concepts are keyed by composite key (crvs/<id>) in build output.
        for concept_id in CRVS_CONCEPTS:
            composite = f"crvs/{concept_id}"
            assert composite in result["concepts"], (
                f"Concept {composite} missing from build output"
            )

    def test_crvs_scoped_concepts_have_domain_crvs(self):
        """CRVS concepts carry domain=crvs and produce /crvs/... URIs."""
        result = build_vocabulary(SCHEMA_DIR)
        # CRVS concepts are keyed by composite key (crvs/<id>) in build output.
        for concept_id in CRVS_CONCEPTS:
            concept = result["concepts"][f"crvs/{concept_id}"]
            assert concept["domain"] == "crvs", (
                f"{concept_id} should have domain=crvs, got {concept['domain']}"
            )
            assert f"/crvs/{concept_id}" in concept["uri"], (
                f"{concept_id} URI should contain /crvs/, got {concept['uri']}"
            )
            assert concept["path"] == f"/crvs/{concept_id}"

    def test_crvs_concept_maturity_matches_release_plan(self):
        """Each CRVS concept carries the maturity declared for the 0.3.0 release.

        The expected values track the 'Maturity promotions' section of the
        CHANGELOG. If a promotion is added or reverted, update both the
        CHANGELOG and this map so we have one authoritative record of what is
        locked at which maturity at release time.
        """
        expected_maturity = {
            # Draft -> candidate (0.3.0)
            "VitalEvent": "candidate",
            "Birth": "candidate",
            "Death": "candidate",
            "Marriage": "candidate",
            "MarriageTermination": "candidate",
            "Person": "candidate",
            # Holding at draft
            "FetalDeath": "draft",
            "Adoption": "draft",
            "PaternityRecognition": "draft",
            "Legitimation": "draft",
            "CivilStatusRecord": "draft",
            "CivilStatusAnnotation": "draft",
            "Parent": "draft",
            "Certificate": "draft",
            "FamilyRegister": "draft",
        }
        # Every concept in CRVS_CONCEPTS has an expected value; this guards
        # against a concept being added to the list without also being added
        # here, which would let a silent maturity regression slip through.
        missing = [c for c in CRVS_CONCEPTS if c not in expected_maturity]
        assert not missing, (
            f"CRVS concept(s) {missing} have no expected maturity in this test; "
            f"add them to expected_maturity before promoting or demoting them."
        )
        for concept_id, expected in expected_maturity.items():
            kebab = _concept_id_to_kebab(concept_id)
            path = SCHEMA_DIR / "concepts" / f"{kebab}.yaml"
            data = _load_yaml(path)
            actual = data.get("maturity")
            assert actual == expected, (
                f"{concept_id} expected maturity '{expected}', got '{actual}'. "
                f"If this is intentional, update both the CHANGELOG and this test."
            )


class TestSupertypeSubtypeSymmetry:
    def test_event_has_vital_event_subtype(self):
        """Event.subtypes must list crvs/VitalEvent (composite ref to the CRVS concept)."""
        event = _load_yaml(SCHEMA_DIR / "concepts" / "event.yaml")
        assert "crvs/VitalEvent" in event["subtypes"], (
            "Event.subtypes should include crvs/VitalEvent"
        )

    def test_vital_event_supertype_is_event(self):
        """VitalEvent lists Event as its only supertype."""
        vital_event = _load_yaml(SCHEMA_DIR / "concepts" / "vital-event.yaml")
        assert vital_event["supertypes"] == ["Event"]

    def test_vital_event_subtypes(self):
        """VitalEvent subtypes include all concrete vital event records, composite-qualified."""
        vital_event = _load_yaml(SCHEMA_DIR / "concepts" / "vital-event.yaml")
        expected = {
            "crvs/Birth",
            "crvs/Death",
            "crvs/FetalDeath",
            "crvs/Marriage",
            "crvs/MarriageTermination",
            "crvs/Adoption",
            "crvs/PaternityRecognition",
            "crvs/Legitimation",
        }
        assert set(vital_event["subtypes"]) == expected

    @pytest.mark.parametrize(
        "concept_file,expected_supertype",
        [
            ("birth.yaml", "crvs/VitalEvent"),
            ("death.yaml", "crvs/VitalEvent"),
            ("fetal-death.yaml", "crvs/VitalEvent"),
            ("marriage.yaml", "crvs/VitalEvent"),
            ("marriage-termination.yaml", "crvs/VitalEvent"),
            ("adoption.yaml", "crvs/VitalEvent"),
            ("paternity-recognition.yaml", "crvs/VitalEvent"),
            ("legitimation.yaml", "crvs/VitalEvent"),
        ],
    )
    def test_supertype_chain(self, concept_file, expected_supertype):
        """Concepts list the expected (composite) supertype ref."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / concept_file)
        assert expected_supertype in data["supertypes"], (
            f"{concept_file}: expected {expected_supertype} in supertypes, "
            f"got {data['supertypes']}"
        )

    def test_marriage_termination_has_no_subtypes(self):
        """MarriageTermination is concrete and has no subtypes."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "marriage-termination.yaml")
        assert data["subtypes"] == []


class TestAbstractConcepts:
    @pytest.mark.parametrize("concept_id", ["VitalEvent"])
    def test_abstract_flag_true_in_yaml(self, concept_id):
        """Abstract supertypes declare abstract: true in their YAML."""
        kebab = _concept_id_to_kebab(concept_id)
        data = _load_yaml(SCHEMA_DIR / "concepts" / f"{kebab}.yaml")
        assert data.get("abstract") is True, (
            f"{concept_id} should be marked abstract"
        )

    def test_marriage_termination_is_not_abstract(self):
        """MarriageTermination is a concrete concept, not abstract."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "marriage-termination.yaml")
        assert data.get("abstract") is not True, (
            "MarriageTermination should not be marked abstract"
        )

    def test_abstract_flag_propagates_to_build_output(self):
        """Build output carries the abstract flag for abstract concepts."""
        result = build_vocabulary(SCHEMA_DIR)
        # CRVS concepts are keyed by composite key (crvs/<id>) in build output.
        assert result["concepts"]["crvs/VitalEvent"]["abstract"] is True
        assert result["concepts"]["crvs/MarriageTermination"]["abstract"] is False
        # Other concrete concepts also default to False
        assert result["concepts"]["crvs/Birth"]["abstract"] is False


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
                {"biological", "gestational", "legal", "adoptive"},
            ),
            (
                "parent-establishment-basis",
                {
                    "marital_presumption",
                    "voluntary_recognition",
                    "judicial_declaration",
                    "adoption_order",
                    "surrogacy_order",
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
            ("marriage-termination-type", {"divorce", "annulment"}),
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
            "dependent_contractor",
            "contributing_family_worker",
            "cooperative_member",
        }


class TestEventPropertyReferences:
    """Event properties that reference crvs/Person."""

    @pytest.mark.parametrize("prop_id", ["deceased", "party_1", "party_2"])
    def test_property_references_crvs_person(self, prop_id):
        """deceased, party_1, party_2 reference crvs/Person by composite ref."""
        data = _load_yaml(SCHEMA_DIR / "properties" / f"{prop_id}.yaml")
        assert data["type"] == "concept:crvs/Person"
        assert data["references"] == "crvs/Person"

    def test_birth_does_not_have_place_of_usual_residence(self):
        """Birth no longer lists place_of_usual_residence directly."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "birth.yaml")
        assert "place_of_usual_residence" not in data["properties"]

    def test_death_does_not_have_place_of_usual_residence(self):
        """Death no longer lists place_of_usual_residence directly."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "death.yaml")
        assert "place_of_usual_residence" not in data["properties"]

    def test_fetal_death_does_not_have_place_of_usual_residence(self):
        """FetalDeath no longer lists place_of_usual_residence directly."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "fetal-death.yaml")
        assert "place_of_usual_residence" not in data["properties"]


class TestCRVSPerson:
    """crvs/Person is a temporal snapshot of a Person at the time of a vital event."""

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
        """crvs/Person concept lives in crvs-person.yaml (preserves filename to avoid collision with root person.yaml)."""
        path = SCHEMA_DIR / "concepts" / "crvs-person.yaml"
        assert path.exists()

    def test_crvs_person_domain_is_crvs(self):
        """crvs/Person belongs to the CRVS domain."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        assert data["domain"] == "crvs"

    def test_crvs_person_id_is_person(self):
        """crvs-person.yaml declares id: Person (not CRVSPerson)."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        assert data["id"] == "Person"

    def test_crvs_person_has_all_snapshot_properties(self):
        """crvs/Person carries all demographic snapshot properties."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        for prop in self.CRVS_PERSON_PROPERTIES:
            assert prop in data["properties"], (
                f"crvs/Person should have property '{prop}'"
            )

    def test_crvs_person_subtypes_include_parent(self):
        """crvs/Person lists crvs/Parent as a subtype (composite ref)."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "crvs-person.yaml")
        assert "crvs/Parent" in data["subtypes"]

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
        """crvs/Person appears in the build output under the composite key crvs/Person."""
        result = build_vocabulary(SCHEMA_DIR)
        # CRVS concepts are keyed by composite key (crvs/<id>) in build output.
        assert "crvs/Person" in result["concepts"]
        crvs_person = result["concepts"]["crvs/Person"]
        assert crvs_person["domain"] == "crvs"


class TestParentLinkEntity:
    def test_parent_has_parental_role(self):
        """Parent carries parental_role as its own property."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "parental_role" in data["properties"]

    def test_parent_inherits_from_crvs_person(self):
        """Parent is a subtype of crvs/Person (composite ref)."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "crvs/Person" in data["supertypes"]

    def test_parent_does_not_directly_list_person(self):
        """person is inherited from crvs/Person, not listed directly on Parent."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "person" not in data["properties"]

    def test_parent_has_establishment_basis(self):
        """Parent carries establishment_basis as a direct property."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "establishment_basis" in data["properties"]

    def test_parent_has_certificate_label(self):
        """Parent carries certificate_label as a direct property."""
        data = _load_yaml(SCHEMA_DIR / "concepts" / "parent.yaml")
        assert "certificate_label" in data["properties"]

    def test_parental_role_definition_has_no_gendered_language(self):
        """parental_role definition does not mention mother, father, etc."""
        data = _load_yaml(SCHEMA_DIR / "properties" / "parental_role.yaml")
        definition_en = data["definition"]["en"].lower()
        for gendered_term in ("mother", "father", "biological_mother", "biological_father"):
            assert gendered_term not in definition_en, (
                f"parental_role definition should not contain '{gendered_term}'"
            )

    def test_parental_role_vocabulary_is_gender_neutral(self):
        """parental-role vocabulary codes contain no gendered terms."""
        data = _load_yaml(
            SCHEMA_DIR / "vocabularies" / "crvs" / "parental-role.yaml"
        )
        codes = {v["code"] for v in data["values"]}
        for code in codes:
            assert "mother" not in code and "father" not in code, (
                f"parental-role code '{code}' contains gendered language"
            )
