"""Invariants for the Agent/Party split introduced by ADR-008.

These tests guard the decisions in ADR-008:
- Agent is an abstract supertype for Person, Organization, SoftwareAgent.
- Party is the beneficiary-side abstract supertype for Person and Group.
- Person belongs to both hierarchies.
- Organization is an Agent, not a Party.
- Actor-side properties (performed_by, evaluator, publisher) reference Agent.
- Profile carries software_used, inherited by all Profile subtypes.
- Party and Agent must NOT carry an owl:disjointWith axiom between them.
"""

from __future__ import annotations

import json

import rdflib
from rdflib.namespace import OWL, RDFS

from tests.conftest import SCHEMA_DIR
from tests.schema_reader import bibliography, concept, property_, subtypes_of

PROFILE_SUBTYPES = [
    "FunctioningProfile",
    "SocioEconomicProfile",
]

ACTOR_PROPERTIES = ["performed_by", "evaluator", "publisher"]


class TestAgentConcept:
    def test_agent_is_abstract(self):
        agent = concept("Agent")
        assert agent["id"] == "Agent"
        assert agent.get("abstract") is True

    def test_agent_subtypes(self):
        assert subtypes_of("Agent") == {"Person", "Organization", "SoftwareAgent"}

    def test_agent_has_no_supertype(self):
        agent = concept("Agent")
        assert agent["supertypes"] == []

    def test_agent_has_multilingual_definition(self):
        agent = concept("Agent")
        for lang in ("en", "fr", "es"):
            assert lang in agent["definition"], f"Missing {lang} definition on Agent"
            assert agent["definition"][lang].strip()


class TestOrganizationConcept:
    def test_organization_is_concrete(self):
        org = concept("Organization")
        assert org["id"] == "Organization"
        assert org.get("abstract") is not True

    def test_organization_supertype_is_agent(self):
        org = concept("Organization")
        assert org["supertypes"] == ["Agent"]

    def test_organization_min_properties(self):
        org = concept("Organization")
        assert set(org["properties"]) == {"name", "identifiers", "location"}

    def test_organization_has_multilingual_definition(self):
        org = concept("Organization")
        for lang in ("en", "fr", "es"):
            assert lang in org["definition"], f"Missing {lang} definition on Organization"
            assert org["definition"][lang].strip()


class TestPersonDualSupertype:
    def test_person_supertypes_include_party_and_agent(self):
        person = concept("Person")
        assert set(person["supertypes"]) == {"Party", "Agent"}


class TestSoftwareAgentIsAgent:
    def test_software_agent_supertype_is_agent(self):
        sw = concept("SoftwareAgent")
        assert sw["supertypes"] == ["Agent"]


class TestPartyScopeUnchanged:
    """Party stays beneficiary-side. Organization is NOT a Party."""

    def test_party_subtypes_are_person_and_group(self):
        assert subtypes_of("Party") == {"Person", "Group"}

    def test_organization_is_not_a_party_subtype(self):
        assert "Organization" not in subtypes_of("Party")


class TestActorPropertyRanges:
    """performed_by, evaluator, and publisher must reference Agent, not Party."""

    def test_performed_by_references_agent(self):
        prop = property_("performed_by")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"

    def test_evaluator_references_agent(self):
        prop = property_("evaluator")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"

    def test_publisher_references_agent(self):
        prop = property_("publisher")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"


class TestProfileSoftwareUsed:
    """Profile gains software_used; each subtype surfaces it in property_groups."""

    def test_profile_lists_software_used(self):
        profile = concept("Profile")
        assert "software_used" in profile["properties"]

    def test_all_profile_subtypes_include_software_used_in_admin_group(self):
        for concept_id in PROFILE_SUBTYPES:
            data = concept(concept_id)
            admin_group = next(
                (g for g in data.get("property_groups", []) if g.get("category") == "administrative"),
                None,
            )
            assert admin_group is not None, f"{concept_id} has no administrative group"
            assert "software_used" in admin_group["properties"], (
                f"{concept_id} administrative group is missing software_used"
            )


class TestLocationConceptAgnostic:
    """location's definition no longer mentions household."""

    def test_location_definition_is_not_household_specific(self):
        loc = property_("location")
        for lang in ("en", "fr", "es"):
            defn = loc["definition"][lang].lower()
            for household_word in ("household", "ménage", "hogar"):
                assert household_word not in defn, (
                    f"location {lang} definition still mentions {household_word!r}"
                )


class TestBibliographyInforms:
    def test_prov_informs_includes_agent_and_organization(self):
        bib = bibliography("w3c-prov-o")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "SoftwareAgent"} <= concepts

    def test_foaf_informs_includes_agent_and_organization(self):
        bib = bibliography("foaf")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "SoftwareAgent"} <= concepts

    def test_schema_org_informs_includes_agent_and_organization(self):
        bib = bibliography("schema-org")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "Person"} <= concepts

    def test_fhir_informs_includes_agent_and_organization(self):
        bib = bibliography("fhir-r4")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization"} <= concepts


class TestPartyAgentNotDisjointInGraph:
    """Party and Agent share Person as a subtype, so they must not be OWL-disjoint.

    A disjointness axiom would make the graph inconsistent under an OWL reasoner:
    Person would be declared a subclass of two disjoint classes. This test scans
    the built JSON-LD documents for any owl:disjointWith axiom between Party and
    Agent in either direction.
    """

    def test_no_owl_disjointness_between_party_and_agent(self):
        from build.build import build_vocabulary

        result = build_vocabulary(SCHEMA_DIR)
        ctx = dict(result["context"]["@context"])
        ctx["rdfs:subClassOf"] = {
            "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            "@type": "@id",
            "@container": "@set",
        }
        ctx["owl:disjointWith"] = {
            "@id": "http://www.w3.org/2002/07/owl#disjointWith",
            "@type": "@id",
        }

        g = rdflib.Graph()
        for _path, doc in result["jsonld_docs"].items():
            copy = dict(doc)
            copy["@context"] = ctx
            g.parse(data=json.dumps(copy), format="json-ld")

        party_uri = rdflib.URIRef("https://publicschema.org/Party")
        agent_uri = rdflib.URIRef("https://publicschema.org/Agent")

        assert (party_uri, OWL.disjointWith, agent_uri) not in g
        assert (agent_uri, OWL.disjointWith, party_uri) not in g

    def test_person_is_subclass_of_both_party_and_agent(self):
        from build.build import build_vocabulary

        result = build_vocabulary(SCHEMA_DIR)
        ctx = dict(result["context"]["@context"])
        ctx["rdfs:subClassOf"] = {
            "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            "@type": "@id",
            "@container": "@set",
        }

        g = rdflib.Graph()
        for _path, doc in result["jsonld_docs"].items():
            copy = dict(doc)
            copy["@context"] = ctx
            g.parse(data=json.dumps(copy), format="json-ld")

        person_uri = rdflib.URIRef("https://publicschema.org/Person")
        party_uri = rdflib.URIRef("https://publicschema.org/Party")
        agent_uri = rdflib.URIRef("https://publicschema.org/Agent")

        assert (person_uri, RDFS.subClassOf, party_uri) in g, (
            "Person is not a subclass of Party in the built graph"
        )
        assert (person_uri, RDFS.subClassOf, agent_uri) in g, (
            "Person is not a subclass of Agent in the built graph"
        )
