"""Integration tests: parse every generated JSON-LD document as RDF using rdflib.

These tests complement the pyld-based tests in test_integration.py. They focus
on triple-level assertions: verifying that the correct RDF types, labels, and
domain links are present after parsing each document through rdflib.

The JSON-LD documents reference a context URL that does not resolve at test
time. Each document's @context is replaced inline with the actual context dict
from the build result before parsing.
"""

import json

import pytest
import rdflib
from rdflib.namespace import RDF, RDFS, SKOS

from tests.conftest import SCHEMA_DIR
from build.build import build_vocabulary


SCHEMA = rdflib.Namespace("https://schema.org/")


@pytest.fixture(scope="module")
def build_result():
    """Build the real schema once for all tests in this module."""
    return build_vocabulary(SCHEMA_DIR)


def _parse_doc(doc: dict, inline_context: dict) -> rdflib.Graph:
    """Parse a JSON-LD document dict using rdflib.

    Replaces the @context value (typically a URL) with the actual inline
    context dict so rdflib can resolve all terms without network access.
    """
    patched = dict(doc)
    patched["@context"] = inline_context
    g = rdflib.Graph()
    g.parse(data=json.dumps(patched), format="json-ld")
    return g


class TestContextParsesAsJsonld:
    def test_context_parses_as_jsonld(self, build_result):
        """The generated JSON-LD context document parses without errors.

        A bare context document contains no triples, so the graph will be
        empty. The assertion is that no exception is raised.
        """
        context_doc = build_result["context"]
        g = rdflib.Graph()
        g.parse(data=json.dumps(context_doc), format="json-ld")
        # No assertion on graph size: a context-only document produces no triples.


class TestConceptJsonld:
    def test_all_concept_jsonld_parse(self, build_result):
        """Every concept JSON-LD document parses without errors and is non-empty."""
        inline_ctx = build_result["context"]["@context"]
        concept_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("concepts/")
        }
        assert concept_docs, "No concept JSON-LD documents found in build result"
        for path, doc in concept_docs.items():
            g = _parse_doc(doc, inline_ctx)
            assert len(g) > 0, f"Graph is empty for concept doc: {path}"

    def test_all_concept_jsonld_has_rdf_class_type(self, build_result):
        """Every concept URI appears as subject of an rdf:type rdfs:Class triple."""
        inline_ctx = build_result["context"]["@context"]
        concept_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("concepts/")
        }
        for path, doc in concept_docs.items():
            g = _parse_doc(doc, inline_ctx)
            concept_uri = rdflib.URIRef(doc["@id"])
            assert (concept_uri, RDF.type, RDFS.Class) in g, (
                f"Missing rdf:type rdfs:Class for concept at {path} "
                f"(URI: {doc['@id']})"
            )

    def test_concept_jsonld_has_label_and_comment(self, build_result):
        """Every concept doc has rdfs:label and at least one rdfs:comment triple."""
        inline_ctx = build_result["context"]["@context"]
        concept_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("concepts/")
        }
        for path, doc in concept_docs.items():
            g = _parse_doc(doc, inline_ctx)
            concept_uri = rdflib.URIRef(doc["@id"])
            labels = list(g.objects(concept_uri, RDFS.label))
            comments = list(g.objects(concept_uri, RDFS.comment))
            assert labels, f"No rdfs:label found for concept at {path}"
            assert comments, f"No rdfs:comment found for concept at {path}"


class TestPropertyJsonld:
    def test_all_property_jsonld_parse(self, build_result):
        """Every property JSON-LD document parses without errors and is non-empty."""
        inline_ctx = build_result["context"]["@context"]
        property_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("properties/")
        }
        assert property_docs, "No property JSON-LD documents found in build result"
        for path, doc in property_docs.items():
            g = _parse_doc(doc, inline_ctx)
            assert len(g) > 0, f"Graph is empty for property doc: {path}"

    def test_all_property_jsonld_has_rdf_property_type(self, build_result):
        """Every property URI appears as subject of an rdf:type rdf:Property triple."""
        inline_ctx = build_result["context"]["@context"]
        property_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("properties/")
        }
        for path, doc in property_docs.items():
            g = _parse_doc(doc, inline_ctx)
            prop_uri = rdflib.URIRef(doc["@id"])
            assert (prop_uri, RDF.type, RDF.Property) in g, (
                f"Missing rdf:type rdf:Property for property at {path} "
                f"(URI: {doc['@id']})"
            )

    def test_property_jsonld_has_domain(self, build_result):
        """Properties with used_by concepts have schema:domainIncludes triples."""
        inline_ctx = build_result["context"]["@context"]
        property_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("properties/")
        }
        for path, doc in property_docs.items():
            # Only test properties that declare domainIncludes in the source doc
            if "schema:domainIncludes" not in doc:
                continue
            g = _parse_doc(doc, inline_ctx)
            prop_uri = rdflib.URIRef(doc["@id"])
            domain_triples = list(g.objects(prop_uri, SCHEMA.domainIncludes))
            assert domain_triples, (
                f"Property at {path} declares schema:domainIncludes in source "
                f"but no domainIncludes triples found after parsing"
            )


class TestVocabularyJsonld:
    def test_all_vocabulary_jsonld_parse(self, build_result):
        """Every vocabulary JSON-LD document parses without errors and is non-empty."""
        inline_ctx = build_result["context"]["@context"]
        vocab_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("vocab/")
        }
        assert vocab_docs, "No vocabulary JSON-LD documents found in build result"
        for path, doc in vocab_docs.items():
            g = _parse_doc(doc, inline_ctx)
            assert len(g) > 0, f"Graph is empty for vocabulary doc: {path}"

    def test_all_vocabulary_jsonld_has_concept_scheme_type(self, build_result):
        """Every vocabulary URI appears as subject of an rdf:type skos:ConceptScheme triple."""
        inline_ctx = build_result["context"]["@context"]
        vocab_docs = {
            k: v for k, v in build_result["jsonld_docs"].items()
            if k.startswith("vocab/")
        }
        for path, doc in vocab_docs.items():
            g = _parse_doc(doc, inline_ctx)
            vocab_uri = rdflib.URIRef(doc["@id"])
            assert (vocab_uri, RDF.type, SKOS.ConceptScheme) in g, (
                f"Missing rdf:type skos:ConceptScheme for vocabulary at {path} "
                f"(URI: {doc['@id']})"
            )


class TestUriMatchesBaseUri:
    def test_concept_uris_match_base_uri(self, build_result):
        """All concept URIs start with the base_uri from meta."""
        base_uri = build_result["meta"]["base_uri"]
        for concept_id, concept in build_result["concepts"].items():
            assert concept["uri"].startswith(base_uri), (
                f"Concept {concept_id} URI {concept['uri']!r} does not start "
                f"with base_uri {base_uri!r}"
            )

    def test_property_uris_match_base_uri(self, build_result):
        """All property URIs start with the base_uri from meta."""
        base_uri = build_result["meta"]["base_uri"]
        for prop_id, prop in build_result["properties"].items():
            assert prop["uri"].startswith(base_uri), (
                f"Property {prop_id} URI {prop['uri']!r} does not start "
                f"with base_uri {base_uri!r}"
            )

    def test_vocabulary_uris_match_base_uri(self, build_result):
        """All vocabulary URIs start with the base_uri from meta."""
        base_uri = build_result["meta"]["base_uri"]
        for vocab_id, vocab in build_result["vocabularies"].items():
            assert vocab["uri"].startswith(base_uri), (
                f"Vocabulary {vocab_id} URI {vocab['uri']!r} does not start "
                f"with base_uri {base_uri!r}"
            )
