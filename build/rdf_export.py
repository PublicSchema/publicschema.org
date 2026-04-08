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


def build_full_jsonld(result: dict) -> str:
    """Build a single JSON-LD document containing the full vocabulary.

    Loads all per-entity JSON-LD documents into a graph, then serializes
    as a compact JSON-LD @graph array. This is the JSON-LD equivalent of
    publicschema.ttl.
    """
    g = load_graph(result)
    meta = result["meta"]
    base_uri = meta["base_uri"]
    version = meta["version"]
    maturity = meta.get("maturity", "draft")
    version_label = "draft" if maturity == "draft" else ".".join(version.split(".")[:2])
    context_url = f"{base_uri}ctx/{version_label}.jsonld"
    # Pass the inline context so rdflib compacts URIs into short terms
    ctx = result["context"]["@context"]
    raw = g.serialize(format="json-ld", context=ctx)
    doc = json.loads(raw)
    # Replace the inline context with the hosted URL for the published file
    doc["@context"] = context_url
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def write_full_jsonld(result: dict, dist_dir: Path) -> Path:
    """Write the full vocabulary JSON-LD to dist/publicschema.jsonld. Returns the output path."""
    content = build_full_jsonld(result)
    out_path = dist_dir / "publicschema.jsonld"
    out_path.write_text(content)
    return out_path


# ---------------------------------------------------------------------------
# SHACL shapes
# ---------------------------------------------------------------------------

SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

# Map YAML property types to XSD datatypes for sh:datatype.
SHACL_DATATYPE_MAP = {
    "string": XSD.string,
    "date": XSD.date,
    "datetime": XSD.dateTime,
    "integer": XSD.integer,
    "decimal": XSD.decimal,
    "boolean": XSD.boolean,
    "uri": XSD.anyURI,
}

# Vocabulary value count threshold: vocabularies with more values than this
# are excluded from sh:in constraints to keep SHACL files readable.
VOCAB_SIZE_THRESHOLD = 50


def _resolve_all_properties(concept_id: str, concepts: dict) -> list:
    """Collect property entries from a concept and all its supertypes."""
    visited = set()
    all_props = []
    seen_ids = set()

    def walk(cid):
        if cid in visited or cid not in concepts:
            return
        visited.add(cid)
        for st in concepts[cid].get("supertypes", []):
            walk(st)
        for entry in concepts[cid].get("properties", []):
            pid = entry["id"]
            if pid not in seen_ids:
                seen_ids.add(pid)
                all_props.append(entry)

    walk(concept_id)
    return all_props


def build_shacl(result: dict) -> str:
    """Build SHACL shapes from the build result.

    Generates one sh:NodeShape per concept, with sh:property entries for
    each of the concept's properties. Constraints are derived from the
    property type, cardinality, and vocabulary.

    Phase 5a: sh:datatype, sh:maxCount, sh:class for concept references,
              sh:nodeKind for geojson_geometry and URI types.
    Phase 5b: sh:in for vocabulary-backed properties (small vocabularies only).
    """
    g = rdflib.Graph()
    g.bind("sh", SH)
    g.bind("xsd", XSD)
    g.bind("ps", rdflib.Namespace("https://publicschema.org/"))

    concepts = result["concepts"]
    properties = result["properties"]
    vocabularies = result["vocabularies"]

    for concept_id, concept in concepts.items():
        concept_uri = rdflib.URIRef(concept["uri"])
        shape_uri = rdflib.URIRef(concept["uri"] + "Shape")

        g.add((shape_uri, RDF.type, SH.NodeShape))
        g.add((shape_uri, SH.targetClass, concept_uri))
        g.add((shape_uri, RDFS.label, rdflib.Literal(f"{concept_id} shape")))

        for prop_entry in _resolve_all_properties(concept_id, concepts):
            prop_id = prop_entry["id"]
            if prop_id not in properties:
                continue
            prop = properties[prop_id]
            prop_uri = rdflib.URIRef(prop["uri"])

            # Create a blank node for the sh:property entry
            prop_shape = rdflib.BNode()
            g.add((shape_uri, SH.property, prop_shape))
            g.add((prop_shape, SH.path, prop_uri))
            g.add((prop_shape, SH.name, rdflib.Literal(prop_id)))

            prop_type = prop.get("type", "string")
            cardinality = prop.get("cardinality", "single")

            # Cardinality: single -> maxCount 1 (everything is optional, no minCount)
            if cardinality == "single":
                g.add((prop_shape, SH.maxCount, rdflib.Literal(1)))

            # Type constraints
            if prop_type.startswith("concept:"):
                ref_id = prop_type.split(":", 1)[1]
                if ref_id in concepts:
                    g.add((prop_shape, SH["class"], rdflib.URIRef(concepts[ref_id]["uri"])))
                g.add((prop_shape, SH.nodeKind, SH.BlankNodeOrIRI))
            elif prop_type == "geojson_geometry":
                g.add((prop_shape, SH.datatype, RDF.JSON))
            elif prop_type == "uri":
                g.add((prop_shape, SH.nodeKind, SH.IRI))
            elif prop_type in SHACL_DATATYPE_MAP:
                g.add((prop_shape, SH.datatype, SHACL_DATATYPE_MAP[prop_type]))

            # Vocabulary constraints (Phase 5b): sh:in for small vocabularies
            vocab_id = prop.get("vocabulary")
            if vocab_id and vocab_id in vocabularies:
                vocab = vocabularies[vocab_id]
                values = vocab.get("values", [])
                if 0 < len(values) <= VOCAB_SIZE_THRESHOLD:
                    collection = rdflib.BNode()
                    items = [rdflib.Literal(v["code"], datatype=XSD.string) for v in values]
                    rdflib.collection.Collection(g, collection, items)
                    g.add((prop_shape, SH["in"], collection))

    return g.serialize(format="turtle")


def write_shacl(result: dict, dist_dir: Path) -> Path:
    """Write the SHACL shapes file to dist/publicschema.shacl.ttl. Returns the output path."""
    shacl_ttl = build_shacl(result)
    out_path = dist_dir / "publicschema.shacl.ttl"
    out_path.write_text(shacl_ttl)
    return out_path
