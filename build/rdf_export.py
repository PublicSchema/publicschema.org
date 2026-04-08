"""Generates RDF serialization outputs (Turtle, SHACL) from build results.

Separate from export.py, which handles tabular formats (CSV, XLSX).
This module handles linked data serializations that consumers can load
into RDF toolchains (Protege, SPARQL endpoints, pySHACL, etc.).
"""

import json
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS, SKOS, XSD


SCHEMA = rdflib.Namespace("https://schema.org/")
PS = rdflib.Namespace("https://publicschema.org/meta/")


def _build_context_with_coercions(ctx_inline: dict) -> dict:
    """Return the inline context with @type:@id coercions for URI-valued predicates.

    Without these coercions, rdflib's JSON-LD parser treats URI strings in
    predicates like schema:domainIncludes and rdfs:subClassOf as plain
    literals instead of URIRefs.
    """
    ctx = dict(ctx_inline)
    ctx["schema:domainIncludes"] = {
        "@id": "https://schema.org/domainIncludes",
        "@type": "@id",
    }
    ctx["schema:rangeIncludes"] = {
        "@id": "https://schema.org/rangeIncludes",
        "@type": "@id",
    }
    ctx["rdfs:subClassOf"] = {
        "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "@type": "@id",
        "@container": "@set",
    }
    ctx["ps:subtypes"] = {
        "@id": "https://publicschema.org/meta/subtypes",
        "@type": "@id",
        "@container": "@set",
    }
    ctx["ps:references"] = {
        "@id": "https://publicschema.org/meta/references",
        "@type": "@id",
    }
    ctx["ps:vocabulary"] = {
        "@id": "https://publicschema.org/meta/vocabulary",
        "@type": "@id",
    }
    return ctx


def load_graph(result: dict) -> rdflib.Graph:
    """Load all JSON-LD documents from a build result into a single rdflib graph.

    Replaces the hosted @context URL in each document with the inline
    context (plus URI coercions) so parsing works without network access.
    """
    ctx = _build_context_with_coercions(result["context"]["@context"])

    g = rdflib.Graph()
    g.bind("ps", PS)
    g.bind("schema", SCHEMA)
    g.bind("skos", SKOS)
    g.bind("xsd", XSD)

    for _path, doc in result["jsonld_docs"].items():
        copy = dict(doc)
        copy["@context"] = ctx
        g.parse(data=json.dumps(copy), format="json-ld")

    return g


def build_turtle(result: dict) -> str:
    """Build a Turtle serialization of the full vocabulary.

    Loads all per-entity JSON-LD documents into a graph, then serializes
    as Turtle with readable namespace prefixes.
    """
    g = load_graph(result)
    return g.serialize(format="turtle")


def write_turtle(result: dict, dist_dir: Path) -> Path:
    """Write the Turtle file to dist/publicschema.ttl. Returns the output path."""
    ttl = build_turtle(result)
    out_path = dist_dir / "publicschema.ttl"
    out_path.write_text(ttl)
    return out_path
