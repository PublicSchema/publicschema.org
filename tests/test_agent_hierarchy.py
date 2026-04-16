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
import yaml
from rdflib.namespace import OWL, RDFS

from tests.conftest import SCHEMA_DIR


CONCEPTS = SCHEMA_DIR / "concepts"
PROPERTIES = SCHEMA_DIR / "properties"
BIBLIOGRAPHY = SCHEMA_DIR / "bibliography"

PROFILE_SUBTYPES = [
    "functioning-profile.yaml",
    "socio-economic-profile.yaml",
]

ACTOR_PROPERTIES = ["performed_by", "evaluator", "publisher"]


def load(path):
    with path.open() as f:
        return yaml.safe_load(f)


class TestAgentConcept:
    def test_agent_is_abstract(self):
        agent = load(CONCEPTS / "agent.yaml")
        assert agent["id"] == "Agent"
        assert agent.get("abstract") is True

    def test_agent_subtypes(self):
        agent = load(CONCEPTS / "agent.yaml")
        assert set(agent["subtypes"]) == {"Person", "Organization", "SoftwareAgent"}

    def test_agent_has_no_supertype(self):
        agent = load(CONCEPTS / "agent.yaml")
        assert agent["supertypes"] == []

    def test_agent_has_multilingual_definition(self):
        agent = load(CONCEPTS / "agent.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in agent["definition"], f"Missing {lang} definition on Agent"
            assert agent["definition"][lang].strip()


class TestOrganizationConcept:
    def test_organization_is_concrete(self):
        org = load(CONCEPTS / "organization.yaml")
        assert org["id"] == "Organization"
        assert org.get("abstract") is not True

    def test_organization_supertype_is_agent(self):
        org = load(CONCEPTS / "organization.yaml")
        assert org["supertypes"] == ["Agent"]

    def test_organization_min_properties(self):
        org = load(CONCEPTS / "organization.yaml")
        assert set(org["properties"]) == {"name", "identifiers", "location"}

    def test_organization_has_multilingual_definition(self):
        org = load(CONCEPTS / "organization.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in org["definition"], f"Missing {lang} definition on Organization"
            assert org["definition"][lang].strip()


class TestPersonDualSupertype:
    def test_person_supertypes_include_party_and_agent(self):
        person = load(CONCEPTS / "person.yaml")
        assert set(person["supertypes"]) == {"Party", "Agent"}


class TestSoftwareAgentIsAgent:
    def test_software_agent_supertype_is_agent(self):
        sw = load(CONCEPTS / "software-agent.yaml")
        assert sw["supertypes"] == ["Agent"]


class TestPartyScopeUnchanged:
    """Party stays beneficiary-side. Organization is NOT a Party."""

    def test_party_subtypes_are_person_and_group(self):
        party = load(CONCEPTS / "party.yaml")
        assert set(party["subtypes"]) == {"Person", "Group"}

    def test_organization_is_not_a_party_subtype(self):
        party = load(CONCEPTS / "party.yaml")
        assert "Organization" not in party["subtypes"]


class TestActorPropertyRanges:
    """performed_by, evaluator, and publisher must reference Agent, not Party."""

    def test_performed_by_references_agent(self):
        prop = load(PROPERTIES / "performed_by.yaml")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"

    def test_evaluator_references_agent(self):
        prop = load(PROPERTIES / "evaluator.yaml")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"

    def test_publisher_references_agent(self):
        prop = load(PROPERTIES / "publisher.yaml")
        assert prop["references"] == "Agent"
        assert prop["type"] == "concept:Agent"


class TestProfileSoftwareUsed:
    """Profile gains software_used; each subtype surfaces it in property_groups."""

    def test_profile_lists_software_used(self):
        profile = load(CONCEPTS / "profile.yaml")
        assert "software_used" in profile["properties"]

    def test_all_profile_subtypes_include_software_used_in_admin_group(self):
        for fname in PROFILE_SUBTYPES:
            data = load(CONCEPTS / fname)
            admin_group = next(
                (g for g in data.get("property_groups", []) if g.get("category") == "administrative"),
                None,
            )
            assert admin_group is not None, f"{fname} has no administrative group"
            assert "software_used" in admin_group["properties"], (
                f"{fname} administrative group is missing software_used"
            )


class TestLocationConceptAgnostic:
    """location's definition no longer mentions household."""

    def test_location_definition_is_not_household_specific(self):
        loc = load(PROPERTIES / "location.yaml")
        for lang in ("en", "fr", "es"):
            defn = loc["definition"][lang].lower()
            for household_word in ("household", "ménage", "hogar"):
                assert household_word not in defn, (
                    f"location {lang} definition still mentions {household_word!r}"
                )


class TestBibliographyInforms:
    def test_prov_informs_includes_agent_and_organization(self):
        bib = load(BIBLIOGRAPHY / "w3c-prov-o.yaml")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "SoftwareAgent"} <= concepts

    def test_foaf_informs_includes_agent_and_organization(self):
        bib = load(BIBLIOGRAPHY / "foaf.yaml")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "SoftwareAgent"} <= concepts

    def test_schema_org_informs_includes_agent_and_organization(self):
        bib = load(BIBLIOGRAPHY / "schema-org.yaml")
        concepts = set(bib["informs"]["concepts"])
        assert {"Agent", "Organization", "Person"} <= concepts

    def test_fhir_informs_includes_agent_and_organization(self):
        bib = load(BIBLIOGRAPHY / "fhir-r4.yaml")
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
