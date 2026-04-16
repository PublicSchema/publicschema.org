"""Invariants for the Document and Specification abstract supertypes (ADR-011).

These tests guard the decisions in ADR-011:
- Document is an abstract supertype for Certificate, CivilStatusRecord,
  FamilyRegister, IdentityDocument, Voucher.
- Specification is an abstract supertype for BenefitSchedule, Instrument,
  ScoringRule.
- document_number (string), identifiers, issuer, issue_date are hoisted
  onto Document. expiry_date is NOT on Document: it lives on the subtypes
  where it applies (Certificate, IdentityDocument, Voucher) because civil
  status actes and family registers are permanent.
- name, version, publisher, publication_url are hoisted onto Specification.
- issuer is Agent-ranged, mirroring the actor-typing pattern from ADR-008.
- The three legacy per-subtype identifier properties (certificate_number,
  register_number, serial_number) are retired in favor of document_number.
- creation_date is retained on FamilyRegister (not retired), since register
  creation (the family-life event trigger) and register issuance are
  semantically distinct.
- Document and Specification subtypes appear as rdfs:subClassOf in the
  built RDF graph.
"""

from __future__ import annotations

import json

import rdflib
import yaml
from rdflib.namespace import RDFS

from tests.conftest import SCHEMA_DIR


CONCEPTS = SCHEMA_DIR / "concepts"
PROPERTIES = SCHEMA_DIR / "properties"

DOCUMENT_SUBTYPES = {
    "certificate.yaml": "Certificate",
    "civil-status-record.yaml": "CivilStatusRecord",
    "family-register.yaml": "FamilyRegister",
    "identity-document.yaml": "IdentityDocument",
    "voucher.yaml": "Voucher",
}

SPECIFICATION_SUBTYPES = {
    "benefit-schedule.yaml": "BenefitSchedule",
    "instrument.yaml": "Instrument",
    "scoring-rule.yaml": "ScoringRule",
}

RETIRED_PROPERTIES = ["certificate_number", "register_number", "serial_number"]


def load(path):
    with path.open() as f:
        return yaml.safe_load(f)


class TestDocumentConcept:
    def test_document_is_abstract(self):
        doc = load(CONCEPTS / "document.yaml")
        assert doc["id"] == "Document"
        assert doc.get("abstract") is True

    def test_document_has_no_supertype(self):
        doc = load(CONCEPTS / "document.yaml")
        assert doc["supertypes"] == []

    def test_document_subtypes(self):
        doc = load(CONCEPTS / "document.yaml")
        assert set(doc["subtypes"]) == set(DOCUMENT_SUBTYPES.values())

    def test_document_hoisted_properties(self):
        doc = load(CONCEPTS / "document.yaml")
        expected = {"document_number", "identifiers", "issuer", "issue_date"}
        assert expected <= set(doc["properties"])

    def test_document_does_not_hoist_expiry_date(self):
        doc = load(CONCEPTS / "document.yaml")
        assert "expiry_date" not in doc["properties"], (
            "expiry_date must not live on Document: civil status actes and "
            "family registers do not expire. See ADR-011."
        )

    def test_expiry_date_on_expiring_subtypes_only(self):
        expiring = {"certificate.yaml", "identity-document.yaml", "voucher.yaml"}
        non_expiring = {"civil-status-record.yaml", "family-register.yaml"}
        for filename in expiring:
            c = load(CONCEPTS / filename)
            assert "expiry_date" in c["properties"], (
                f"{filename} is an expiring Document subtype and must list expiry_date"
            )
        for filename in non_expiring:
            c = load(CONCEPTS / filename)
            assert "expiry_date" not in c["properties"], (
                f"{filename} is a permanent Document subtype and must not list expiry_date"
            )

    def test_document_has_multilingual_definition(self):
        doc = load(CONCEPTS / "document.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in doc["definition"], f"Missing {lang} definition on Document"
            assert doc["definition"][lang].strip()


class TestSpecificationConcept:
    def test_specification_is_abstract(self):
        spec = load(CONCEPTS / "specification.yaml")
        assert spec["id"] == "Specification"
        assert spec.get("abstract") is True

    def test_specification_has_no_supertype(self):
        spec = load(CONCEPTS / "specification.yaml")
        assert spec["supertypes"] == []

    def test_specification_subtypes(self):
        spec = load(CONCEPTS / "specification.yaml")
        assert set(spec["subtypes"]) == set(SPECIFICATION_SUBTYPES.values())

    def test_specification_hoisted_properties(self):
        spec = load(CONCEPTS / "specification.yaml")
        expected = {"name", "version", "publisher", "publication_url"}
        assert expected <= set(spec["properties"])

    def test_specification_has_multilingual_definition(self):
        spec = load(CONCEPTS / "specification.yaml")
        for lang in ("en", "fr", "es"):
            assert lang in spec["definition"], f"Missing {lang} definition on Specification"
            assert spec["definition"][lang].strip()


class TestDocumentSubtypes:
    """Each Document subtype must declare Document as a supertype."""

    def test_certificate_supertype_includes_document(self):
        data = load(CONCEPTS / "certificate.yaml")
        assert "Document" in data["supertypes"]

    def test_civil_status_record_supertype_includes_document(self):
        data = load(CONCEPTS / "civil-status-record.yaml")
        assert "Document" in data["supertypes"]

    def test_family_register_supertype_includes_document(self):
        data = load(CONCEPTS / "family-register.yaml")
        assert "Document" in data["supertypes"]

    def test_identity_document_supertype_includes_document(self):
        data = load(CONCEPTS / "identity-document.yaml")
        assert "Document" in data["supertypes"]

    def test_voucher_supertype_includes_document(self):
        data = load(CONCEPTS / "voucher.yaml")
        assert "Document" in data["supertypes"]


class TestSpecificationSubtypes:
    """Each Specification subtype must declare Specification as its supertype."""

    def test_benefit_schedule_supertype_is_specification(self):
        data = load(CONCEPTS / "benefit-schedule.yaml")
        assert data["supertypes"] == ["Specification"]

    def test_instrument_supertype_is_specification(self):
        data = load(CONCEPTS / "instrument.yaml")
        assert data["supertypes"] == ["Specification"]

    def test_scoring_rule_supertype_is_specification(self):
        data = load(CONCEPTS / "scoring-rule.yaml")
        assert data["supertypes"] == ["Specification"]


class TestRetiredProperties:
    """certificate_number, register_number, serial_number must not exist."""

    def test_certificate_number_yaml_absent(self):
        assert not (PROPERTIES / "certificate_number.yaml").exists()

    def test_register_number_yaml_absent(self):
        assert not (PROPERTIES / "register_number.yaml").exists()

    def test_serial_number_yaml_absent(self):
        assert not (PROPERTIES / "serial_number.yaml").exists()

    def test_no_subtype_references_retired_properties(self):
        for fname in DOCUMENT_SUBTYPES:
            data = load(CONCEPTS / fname)
            props = set(data.get("properties", []))
            for retired in RETIRED_PROPERTIES:
                assert retired not in props, (
                    f"{fname} still lists retired property {retired!r}"
                )


class TestCreationDateRetained:
    """creation_date must NOT be retired; it stays on FamilyRegister.

    Rationale: in livret de famille, koseki, and hukou systems, register
    creation (family-life event trigger) and register issuance are
    semantically distinct. Retiring creation_date to issue_date would
    collapse a meaningful distinction.
    """

    def test_creation_date_yaml_exists(self):
        assert (PROPERTIES / "creation_date.yaml").exists()

    def test_family_register_lists_creation_date(self):
        data = load(CONCEPTS / "family-register.yaml")
        assert "creation_date" in data["properties"]


class TestDocumentNumberProperty:
    """document_number is a single string, not Agent-ranged or vocabulary-bound."""

    def test_document_number_yaml_exists(self):
        assert (PROPERTIES / "document_number.yaml").exists()

    def test_document_number_is_string_single(self):
        prop = load(PROPERTIES / "document_number.yaml")
        assert prop["type"] == "string"
        assert prop["cardinality"] == "single"


class TestIssuerProperty:
    """issuer is Agent-ranged, mirroring ADR-008's actor-typing pattern."""

    def test_issuer_yaml_exists(self):
        assert (PROPERTIES / "issuer.yaml").exists()

    def test_issuer_references_agent(self):
        prop = load(PROPERTIES / "issuer.yaml")
        assert prop["type"] == "concept:Agent"
        assert prop["references"] == "Agent"
        assert prop["cardinality"] == "single"


class TestBuiltGraphSubClassEdges:
    """Document and Specification subtypes must appear as rdfs:subClassOf in the built RDF graph."""

    def _graph(self):
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
        return g

    def test_certificate_is_subclass_of_document(self):
        g = self._graph()
        cert = rdflib.URIRef("https://publicschema.org/crvs/Certificate")
        doc = rdflib.URIRef("https://publicschema.org/Document")
        assert (cert, RDFS.subClassOf, doc) in g, (
            "Certificate is not rdfs:subClassOf Document in the built graph"
        )

    def test_civil_status_record_is_subclass_of_document(self):
        g = self._graph()
        csr = rdflib.URIRef("https://publicschema.org/crvs/CivilStatusRecord")
        doc = rdflib.URIRef("https://publicschema.org/Document")
        assert (csr, RDFS.subClassOf, doc) in g, (
            "CivilStatusRecord is not rdfs:subClassOf Document in the built graph"
        )

    def test_family_register_is_subclass_of_document(self):
        g = self._graph()
        fr = rdflib.URIRef("https://publicschema.org/crvs/FamilyRegister")
        doc = rdflib.URIRef("https://publicschema.org/Document")
        assert (fr, RDFS.subClassOf, doc) in g, (
            "FamilyRegister is not rdfs:subClassOf Document in the built graph"
        )

    def test_identity_document_is_subclass_of_document(self):
        g = self._graph()
        ident = rdflib.URIRef("https://publicschema.org/IdentityDocument")
        doc = rdflib.URIRef("https://publicschema.org/Document")
        assert (ident, RDFS.subClassOf, doc) in g, (
            "IdentityDocument is not rdfs:subClassOf Document in the built graph"
        )

    def test_voucher_is_subclass_of_document(self):
        g = self._graph()
        voucher = rdflib.URIRef("https://publicschema.org/Voucher")
        doc = rdflib.URIRef("https://publicschema.org/Document")
        assert (voucher, RDFS.subClassOf, doc) in g, (
            "Voucher is not rdfs:subClassOf Document in the built graph"
        )

    def test_instrument_is_subclass_of_specification(self):
        g = self._graph()
        instrument = rdflib.URIRef("https://publicschema.org/Instrument")
        spec = rdflib.URIRef("https://publicschema.org/Specification")
        assert (instrument, RDFS.subClassOf, spec) in g, (
            "Instrument is not rdfs:subClassOf Specification in the built graph"
        )

    def test_scoring_rule_is_subclass_of_specification(self):
        g = self._graph()
        sr = rdflib.URIRef("https://publicschema.org/ScoringRule")
        spec = rdflib.URIRef("https://publicschema.org/Specification")
        assert (sr, RDFS.subClassOf, spec) in g, (
            "ScoringRule is not rdfs:subClassOf Specification in the built graph"
        )

    def test_benefit_schedule_is_subclass_of_specification(self):
        g = self._graph()
        bs = rdflib.URIRef("https://publicschema.org/sp/BenefitSchedule")
        spec = rdflib.URIRef("https://publicschema.org/Specification")
        assert (bs, RDFS.subClassOf, spec) in g, (
            "BenefitSchedule is not rdfs:subClassOf Specification in the built graph"
        )
