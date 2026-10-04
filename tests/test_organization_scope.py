"""Organizations of any sector, as actors and as receivers (ADR-028).

These tests guard the decisions in ADR-028:
- Organization covers public and private bodies, including companies.
- Organization is a Party as well as an Agent, so beneficiary-side slots
  admit it.
- Organization carries economic activities and a dissolution date.
- Sole proprietorships follow the jurisdiction: the definitions say how
  either pattern is recorded.
"""

from __future__ import annotations

import jsonschema
import pytest
from pyshacl import validate
from rdflib import Namespace
from rdflib.namespace import RDFS

from tests.conftest import jsonld_graph
from tests.schema_reader import concept, property_

PS = Namespace("https://publicschema.org/")

RECEIVER_SLOTS = ["beneficiary", "recipient", "redeemable_by", "issued_to"]
ORGANIZATION_WORD = {"en": "organization", "fr": "organisation", "es": "organización"}


class TestOrganizationDefinition:
    def test_definition_names_private_bodies(self):
        definition = concept("Organization")["definition"]
        for lang, words in (
            ("en", ("company", "cooperative")),
            ("fr", ("entreprise", "coopérative")),
            ("es", ("empresa", "cooperativa")),
        ):
            for word in words:
                assert word in definition[lang].lower(), (lang, word)

    def test_definition_is_not_limited_to_public_delivery(self):
        definition = concept("Organization")["definition"]["en"]
        assert "public or private" in definition

    def test_definition_explains_sole_proprietorships(self):
        definition = concept("Organization")["definition"]
        for lang, term in (
            ("en", "sole proprietorship"),
            ("fr", "entreprise individuelle"),
            ("es", "empresa individual"),
        ):
            assert term in definition[lang].lower(), lang


class TestOrganizationIsParty:
    def test_organization_has_party_supertype(self):
        assert "Party" in concept("Organization")["supertypes"]

    def test_party_definition_covers_organizations(self):
        definition = concept("Party")["definition"]
        for lang, term in ORGANIZATION_WORD.items():
            assert term in definition[lang].lower(), lang

    @pytest.mark.parametrize("slot", RECEIVER_SLOTS)
    def test_receiver_slot_definitions_admit_organizations(self, slot):
        prop = property_(slot)
        assert prop["references"] == "Party"
        for lang, term in ORGANIZATION_WORD.items():
            assert term in prop["definition"][lang].lower(), (slot, lang)

    def test_data_subject_excludes_organizations(self):
        definition = property_("data_subject")["definition"]
        for lang, term in (
            ("en", "an organization"),
            ("fr", "une organisation"),
            ("es", "una organización"),
        ):
            assert term in definition[lang].lower(), lang

    def test_identity_documents_cover_organizations(self):
        definition = property_("identity_documents")["definition"]
        for lang, term in ORGANIZATION_WORD.items():
            assert term in definition[lang].lower(), lang


class TestBusinessRegisterProperties:
    def test_organization_lists_economic_activity_and_dissolution_date(self):
        assert {"economic_activities", "dissolution_date"} <= set(
            concept("Organization")["properties"]
        )

    def test_economic_activities_are_coded_and_repeatable(self):
        prop = property_("economic_activities")
        assert prop["cardinality"] == "multiple"
        assert prop["references"] == "CodedValue"
        assert prop.get("vocabulary") is None

    def test_dissolution_date_is_a_date(self):
        assert property_("dissolution_date")["type"] == "date"

    def test_new_properties_are_translated(self):
        for key in ("economic_activities", "dissolution_date"):
            prop = property_(key)
            for lang in ("en", "fr", "es"):
                assert prop["definition"][lang].strip(), (key, lang)
                assert prop["label"][lang].strip(), (key, lang)


def company_enrollment() -> dict:
    return {
        "@type": "sp/Enrollment",
        "@id": "https://example.org/enrollment/company-1",
        "beneficiary": {
            "@type": "Organization",
            "@id": "https://example.org/organization/dairy-company",
            "name": "Example Dairy Company",
            "legal_form": {
                "@type": "CodedValue",
                "code_value": "private-limited-company",
                "code_scheme": "https://example.org/codes/legal-form",
            },
            "economic_activities": [
                {
                    "@type": "CodedValue",
                    "code_value": "0141",
                    "code_scheme": "https://unstats.un.org/unsd/classifications/Econ/isic",
                },
            ],
            "formation_date": "2012-03-01",
            "dissolution_date": "2026-06-30",
        },
        "enrollment_date": "2024-01-15",
    }


class TestCompanyAsBeneficiaryAcrossExports:
    def test_owl_export_places_organization_under_party(self, owl_graph):
        assert (PS["Organization"], RDFS.subClassOf, PS["Party"]) in owl_graph
        assert (PS["Organization"], RDFS.subClassOf, PS["Agent"]) in owl_graph

    def test_company_enrollment_validates(
        self, built_vocabulary, schema_registry, shacl_graph, subclass_hierarchy
    ):
        record = company_enrollment()
        schema = built_vocabulary["concept_schemas"][record["@type"]]
        jsonschema.Draft202012Validator(schema, registry=schema_registry).validate(record)
        graph = jsonld_graph(record, built_vocabulary["context"], subclass_hierarchy)
        conforms, _, report = validate(graph, shacl_graph=shacl_graph)
        assert conforms, report

    def test_dissolution_date_must_be_a_date(self, built_vocabulary, schema_registry, shacl_graph):
        record = company_enrollment()
        record["beneficiary"]["dissolution_date"] = "last summer"
        schema = built_vocabulary["concept_schemas"]["Organization"]
        validator = jsonschema.Draft202012Validator(
            schema,
            registry=schema_registry,
            format_checker=jsonschema.FormatChecker(),
        )
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(record["beneficiary"])
        conforms, _, _ = validate(
            jsonld_graph(record, built_vocabulary["context"]), shacl_graph=shacl_graph
        )
        assert not conforms


class TestRelatedDefinitionsStayConsistent:
    def test_organization_holder_role_does_not_require_legal_personality(self):
        # ADR-025: an organization without legal personality is still an Organization.
        definition = concept("agri/OrganizationAgriculturalHolderRole")["definition"]
        for lang, term in (
            ("en", "legal personality"),
            ("fr", "personnalité juridique"),
            ("es", "personalidad jurídica"),
        ):
            assert term not in definition[lang].lower(), lang

    def test_data_subject_lists_current_party_subtypes(self):
        definition = property_("data_subject")["definition"]
        for lang in ("en", "fr", "es"):
            assert "Farm" not in definition[lang], lang
            assert "Person, Group" in definition[lang], lang
            assert "Organization" in definition[lang], lang

    def test_organization_convergence_note_defers_only_what_is_still_deferred(self):
        notes = concept("Organization")["convergence"]["notes"]
        deferred = [s for s in notes.split(". ") if "deferred" in s]
        assert deferred
        for sentence in deferred:
            for added in ("parent_organization", "legal_form", "contact points"):
                assert added not in sentence, added

    def test_person_definition_is_not_limited_to_social_protection(self):
        definition = concept("Person")["definition"]
        for lang, term in (
            ("en", "social protection"),
            ("fr", "protection sociale"),
            ("es", "protección social"),
        ):
            assert term not in definition[lang].lower(), lang
