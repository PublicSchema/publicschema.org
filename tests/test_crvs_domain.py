"""Tests for the CRVS domain: concepts, vocabularies, and event subtyping."""

import pytest

from build.build import build_vocabulary
from build.validate import validate_schema_dir
from tests.conftest import SCHEMA_DIR
from tests.schema_reader import concept, property_, raw_schema, subtypes_of, vocabulary

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
    def test_concept_exists_in_linkml_source(self, concept_id):
        """Each CRVS concept exists in the authored LinkML source."""
        assert f"crvs/{concept_id}" in raw_schema()["concepts"]

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
            data = concept(f"crvs/{concept_id}")
            actual = data.get("maturity")
            assert actual == expected, (
                f"{concept_id} expected maturity '{expected}', got '{actual}'. "
                f"If this is intentional, update both the CHANGELOG and this test."
            )


class TestSupertypeSubtypeSymmetry:
    def test_event_has_vital_event_subtype(self):
        """Event.subtypes must list crvs/VitalEvent (composite ref to the CRVS concept)."""
        assert "crvs/VitalEvent" in subtypes_of("Event"), (
            "Event.subtypes should include crvs/VitalEvent"
        )

    def test_vital_event_supertype_is_event(self):
        """VitalEvent lists Event as its only supertype."""
        vital_event = concept("crvs/VitalEvent")
        assert vital_event["supertypes"] == ["Event"]

    def test_vital_event_subtypes(self):
        """VitalEvent subtypes include all concrete vital event records, composite-qualified."""
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
        assert subtypes_of("crvs/VitalEvent") == expected

    @pytest.mark.parametrize(
        "concept_id,expected_supertype",
        [
            ("Birth", "crvs/VitalEvent"),
            ("Death", "crvs/VitalEvent"),
            ("FetalDeath", "crvs/VitalEvent"),
            ("Marriage", "crvs/VitalEvent"),
            ("MarriageTermination", "crvs/VitalEvent"),
            ("Adoption", "crvs/VitalEvent"),
            ("PaternityRecognition", "crvs/VitalEvent"),
            ("Legitimation", "crvs/VitalEvent"),
        ],
    )
    def test_supertype_chain(self, concept_id, expected_supertype):
        """Concepts list the expected (composite) supertype ref."""
        data = concept(f"crvs/{concept_id}")
        assert expected_supertype in data["supertypes"], (
            f"{concept_id}: expected {expected_supertype} in supertypes, "
            f"got {data['supertypes']}"
        )

    def test_marriage_termination_has_no_subtypes(self):
        """MarriageTermination is concrete and has no subtypes."""
        assert subtypes_of("crvs/MarriageTermination") == set()


class TestAbstractConcepts:
    @pytest.mark.parametrize("concept_id", ["VitalEvent"])
    def test_abstract_flag_true_in_linkml_source(self, concept_id):
        """Abstract supertypes declare abstract: true in authored LinkML."""
        data = concept(f"crvs/{concept_id}")
        assert data.get("abstract") is True, (
            f"{concept_id} should be marked abstract"
        )

    def test_marriage_termination_is_not_abstract(self):
        """MarriageTermination is a concrete concept, not abstract."""
        data = concept("crvs/MarriageTermination")
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
    def test_vocabulary_exists_in_linkml_source(self, vocab_id):
        """Each CRVS vocabulary exists in the authored LinkML source."""
        assert f"crvs/{vocab_id}" in raw_schema()["vocabularies"]

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
            data = vocabulary(f"crvs/{vocab_id}")
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
        data = vocabulary(f"crvs/{vocab_id}")
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
        data = concept("Person")
        for prop in self.DEMOGRAPHIC_PROPERTIES:
            assert prop in data["properties"], (
                f"Person should have property '{prop}'"
            )

    @pytest.mark.parametrize("prop_id", DEMOGRAPHIC_PROPERTIES)
    def test_demographic_property_exists_in_linkml_source(self, prop_id):
        """Each demographic property exists in the authored LinkML source."""
        assert prop_id in raw_schema()["properties"]

    @pytest.mark.parametrize("prop_id", DEMOGRAPHIC_PROPERTIES)
    def test_demographic_property_has_trilingual_definition(self, prop_id):
        """Each demographic property has en, fr, es definitions."""
        data = property_(prop_id)
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
        data = property_("religion")
        assert data.get("vocabulary") is None

    def test_ethnic_group_has_no_vocabulary(self):
        """ethnic_group is free text (country-specific), no vocabulary."""
        data = property_("ethnic_group")
        assert data.get("vocabulary") is None

    def test_industry_has_no_vocabulary(self):
        """industry references ISIC Rev.4 but too large to enumerate."""
        data = property_("industry")
        assert data.get("vocabulary") is None

    def test_religion_is_restricted(self):
        """religion is GDPR Art.9 special category data."""
        data = property_("religion")
        assert data.get("sensitivity") == "restricted"

    def test_ethnic_group_is_restricted(self):
        """ethnic_group is GDPR Art.9 special category data."""
        data = property_("ethnic_group")
        assert data.get("sensitivity") == "restricted"


class TestDemographicVocabularies:
    """Vocabularies for literacy, employment-status, and status-in-employment."""

    @pytest.mark.parametrize("vocab_id", [
        "literacy",
        "employment-status",
        "status-in-employment",
    ])
    def test_vocabulary_exists_in_linkml_source(self, vocab_id):
        """Each demographic vocabulary exists in the authored LinkML source."""
        assert vocab_id in raw_schema()["vocabularies"]

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
        data = vocabulary("literacy")
        codes = {v["code"] for v in data["values"]}
        assert codes == {"literate", "illiterate"}

    def test_employment_status_codes(self):
        """Employment status uses ILO 19th ICLS tripartite classification."""
        data = vocabulary("employment-status")
        codes = {v["code"] for v in data["values"]}
        assert codes == {"employed", "unemployed", "outside_labour_force"}

    def test_status_in_employment_codes(self):
        """Status in employment uses ILO ICSE-18 categories."""
        data = vocabulary("status-in-employment")
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
    """CRVS event properties that reference Person."""

    @pytest.mark.parametrize("prop_id", ["deceased", "party_1", "party_2"])
    def test_property_references_person(self, prop_id):
        """deceased, party_1, party_2 reference the universal Person concept."""
        data = property_(prop_id)
        assert data["type"] == "concept:Person"
        assert data["references"] == "Person"
        assert data["domain_override"] == "crvs"

    def test_birth_does_not_have_place_of_usual_residence(self):
        """Birth no longer lists place_of_usual_residence directly."""
        data = concept("crvs/Birth")
        assert "place_of_usual_residence" not in data["properties"]

    def test_death_does_not_have_place_of_usual_residence(self):
        """Death no longer lists place_of_usual_residence directly."""
        data = concept("crvs/Death")
        assert "place_of_usual_residence" not in data["properties"]

    def test_fetal_death_does_not_have_place_of_usual_residence(self):
        """FetalDeath no longer lists place_of_usual_residence directly."""
        data = concept("crvs/FetalDeath")
        assert "place_of_usual_residence" not in data["properties"]


class TestCrvsPersonReferences:
    """CRVS uses universal Person references plus CRVS-scoped properties."""

    def test_crvs_person_concept_is_not_authored(self):
        """The LinkML source has no domain-scoped crvs/Person concept."""
        assert "crvs/Person" not in raw_schema()["concepts"]

    def test_parent_inherits_from_universal_person(self):
        """Parent is a CRVS-scoped subtype of universal Person."""
        data = concept("crvs/Parent")
        assert data["domain"] == "crvs"
        assert data["supertypes"] == ["Person"]

    def test_age_at_event_property_exists(self):
        """age_at_event exists in the authored LinkML source."""
        assert "age_at_event" in raw_schema()["properties"]

    def test_age_at_event_is_integer(self):
        """age_at_event is an integer property."""
        data = property_("age_at_event")
        assert data["type"] == "integer"

    def test_age_at_event_has_crvs_domain(self):
        """age_at_event is CRVS-specific."""
        data = property_("age_at_event")
        assert data.get("domain_override") == "crvs"

    def test_no_crvs_person_in_build(self):
        """Build output follows LinkML: only universal Person is authored."""
        result = build_vocabulary(SCHEMA_DIR)
        assert "Person" in result["concepts"]
        assert "crvs/Person" not in result["concepts"]


class TestParentLinkEntity:
    def test_parent_has_parental_role(self):
        """Parent carries parental_role as its own property."""
        data = concept("crvs/Parent")
        assert "parental_role" in data["properties"]

    def test_parent_inherits_from_person(self):
        """Parent is a CRVS-scoped subtype of universal Person."""
        data = concept("crvs/Parent")
        assert "Person" in data["supertypes"]

    def test_parent_does_not_directly_list_person(self):
        """Person identity fields are inherited from Person, not listed directly on Parent."""
        data = concept("crvs/Parent")
        assert "person" not in data["properties"]

    def test_parent_has_establishment_basis(self):
        """Parent carries establishment_basis as a direct property."""
        data = concept("crvs/Parent")
        assert "establishment_basis" in data["properties"]

    def test_parent_has_certificate_label(self):
        """Parent carries certificate_label as a direct property."""
        data = concept("crvs/Parent")
        assert "certificate_label" in data["properties"]

    def test_parental_role_definition_has_no_gendered_language(self):
        """parental_role definition does not mention mother, father, etc."""
        data = property_("parental_role")
        definition_en = data["definition"]["en"].lower()
        for gendered_term in ("mother", "father", "biological_mother", "biological_father"):
            assert gendered_term not in definition_en, (
                f"parental_role definition should not contain '{gendered_term}'"
            )

    def test_parental_role_vocabulary_is_gender_neutral(self):
        """parental-role vocabulary codes contain no gendered terms."""
        data = vocabulary("crvs/parental-role")
        codes = {v["code"] for v in data["values"]}
        for code in codes:
            assert "mother" not in code and "father" not in code, (
                f"parental-role code '{code}' contains gendered language"
            )
