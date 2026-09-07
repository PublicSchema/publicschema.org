"""LinkML-driven RDF export for site-facing artifacts.

The three site artifacts (Turtle OWL, SHACL shapes, full JSON-LD
``@graph``) are produced by LinkML's generators against the
canonical composite at ``schema/publicschema.yaml``:

* ``write_turtle``      -> ``gen-owl``   -> ``dist/publicschema.ttl``
* ``write_shacl``       -> LinkML SHACL with public literal enum codes
                           -> ``dist/publicschema.shacl.ttl``
* ``write_full_jsonld`` -> ``gen-owl`` + rdflib JSON-LD bridge ->
                           ``dist/publicschema.jsonld``

The JSON-LD bridge re-parses the gen-owl Turtle into rdflib and emits
JSON-LD with expanded IRIs. This preserves the Turtle graph's meaning
when the document references the hosted public instance context.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LINKML_COMPOSITE = ROOT / "schema" / "publicschema.yaml"
DEFAULT_CONTEXT_URL = "https://publicschema.org/ctx/draft.jsonld"
# Publish authored class_uri/slot_uri identities, matching the public context
# and SHACL shapes, rather than LinkML's implementation names.
OWL_GENERATOR_ARGS = ["--no-use-native-uris"]


def _find_linkml_generator(name: str) -> str:
    """Locate a LinkML generator CLI (``gen-owl``, ``gen-shacl``, ...).

    Prefer the venv that runs the current Python interpreter, fall back
    to the repo-local ``.venv/bin``, and finally to ``$PATH``. Mirrors
    the resolution used by ``tests/test_linkml_roundtrip.py`` so the
    production build and the round-trip test always agree on which
    binary they invoke.
    """
    candidates: list[Path] = [
        Path(sys.executable).parent / name,
        ROOT / ".venv" / "bin" / name,
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(
        f"LinkML generator {name!r} not found. Install the linkml package "
        f"in the active venv (e.g. `.venv/bin/pip install linkml`)."
    )


def _require_composite(composite: Path = DEFAULT_LINKML_COMPOSITE) -> Path:
    """Ensure the LinkML composite schema exists before invoking a generator."""
    if not composite.exists():
        raise FileNotFoundError(
            f"LinkML composite not found at {composite}."
        )
    # Generator subprocesses run from ROOT, which can differ from the
    # caller's working directory when --linkml-dir is a relative path.
    return composite.resolve()


def _uri_slot_paths(composite: Path) -> set:
    """Return RDF paths for induced slots authored with LinkML's ``uri`` range."""
    from linkml_runtime.utils.schemaview import SchemaView
    from rdflib import URIRef

    schemaview = SchemaView(str(_require_composite(composite)))
    return {
        URIRef(schemaview.get_uri(slot, expand=True))
        for class_definition in schemaview.all_classes(imports=True).values()
        for slot in schemaview.class_induced_slots(class_definition.name)
        if slot.range == "uri"
    }


def _generate_owl_graph(composite: Path):
    """Generate OWL and align authored URI slots with the public IRI contract."""
    import rdflib  # noqa: WPS433 — local import is intentional.
    from rdflib.namespace import OWL, RDF, RDFS, XSD

    composite = _require_composite(composite)
    binary = _find_linkml_generator("gen-owl")
    proc = subprocess.run(
        [binary, *OWL_GENERATOR_ARGS, str(composite)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    graph = rdflib.Graph()
    graph.parse(data=proc.stdout, format="turtle")

    for property_uri in _uri_slot_paths(composite):
        graph.remove((property_uri, RDF.type, OWL.DatatypeProperty))
        graph.add((property_uri, RDF.type, OWL.ObjectProperty))
        graph.remove((property_uri, RDFS.range, XSD.anyURI))
        for restriction in graph.subjects(OWL.onProperty, property_uri):
            if (restriction, OWL.allValuesFrom, XSD.anyURI) in graph:
                graph.remove((restriction, OWL.allValuesFrom, XSD.anyURI))
                graph.add((restriction, OWL.allValuesFrom, OWL.Thing))
    return graph


def write_turtle(
    output_path: Path,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate the full vocabulary as OWL Turtle via ``gen-owl``."""
    graph = _generate_owl_graph(composite)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(graph.serialize(format="turtle"), encoding="utf-8")
    return output_path


def write_shacl(
    output_path: Path,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate LinkML SHACL shapes for the public JSON-LD representation.

    The public context and JSON schemas use literal vocabulary codes.
    LinkML's default enum projection uses ``meaning`` IRIs instead, so
    adapt only enum emission, including enums in ``any_of`` ranges.
    Source meanings remain intact for OWL and other LinkML consumers.
    """
    from dataclasses import asdict

    from linkml.generators.shaclgen import ShaclGenerator
    from rdflib import BNode, Literal, URIRef
    from rdflib.collection import Collection
    from rdflib.namespace import SH, XSD

    from build.linkml_reader import _convert_enum_to_vocabulary

    class PublicCodeShaclGenerator(ShaclGenerator):
        def as_graph(self):
            """Make authored ``uri`` slots match their JSON-LD IRI coercion.

            LinkML's generic SHACL generator renders its built-in ``uri`` type
            as an ``xsd:anyURI`` literal. PublicSchema's generated JSON-LD
            context deliberately expands the same fields as ``@id`` values, so
            their RDF representation is an IRI. Convert only those induced
            slots, leaving every other primitive and enum constraint untouched.
            """
            graph = super().as_graph()
            uri_slot_paths = {
                URIRef(self.schemaview.get_uri(slot, expand=True))
                for class_definition in self.schemaview.all_classes(
                    imports=not self.exclude_imports
                ).values()
                for slot in self.schemaview.class_induced_slots(class_definition.name)
                if slot.range == "uri"
            }
            for path in uri_slot_paths:
                for property_shape in graph.subjects(SH.path, path):
                    graph.remove((property_shape, SH.datatype, XSD.anyURI))
                    graph.remove((property_shape, SH.nodeKind, SH.Literal))
                    graph.add((property_shape, SH.nodeKind, SH.IRI))
            return graph

        def _add_enum(self, graph, emit, enum_name):
            enum = self.schemaview.get_enum(enum_name)
            # Reuse the reader's restoration of migrated codes, rather than
            # confusing external standard_code annotations with public codes.
            _, vocabulary = _convert_enum_to_vocabulary(enum_name, asdict(enum))
            # RDF 1.1 treats a plain string and explicit xsd:string as the
            # same value. RDFLib/pySHACL retain the distinction in sh:in, so
            # support both public JSON-LD strings and explicitly typed RDF.
            values = [
                literal
                for value in vocabulary["values"]
                for literal in (
                    Literal(str(value["code"])),
                    Literal(str(value["code"]), datatype=XSD.string),
                )
            ]
            node = BNode()
            Collection(graph, node, values)
            emit(SH.datatype, XSD.string)
            emit(SH["in"], node)

    generator = PublicCodeShaclGenerator(str(_require_composite(composite)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generator.serialize(), encoding="utf-8")
    return output_path


def write_full_jsonld(
    output_path: Path,
    context_url: str = DEFAULT_CONTEXT_URL,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate the full vocabulary JSON-LD ``@graph`` document.

    Strategy: run ``gen-owl`` to produce Turtle (the OWL projection
    is the single canonical RDF rendering of the schema), parse it
    with rdflib, re-serialise with expanded IRIs, then reference the hosted
    public context. Compacting with rdflib's generated prefixes and then
    discarding that context changes IRIs that the public context does not
    define, or defines differently.
    """
    g = _generate_owl_graph(composite)

    # The public context describes instance fields, not every namespace
    # in the OWL vocabulary. Expanded IRIs need no serializer-only context.
    raw = g.serialize(format="json-ld", auto_compact=False)
    doc = json.loads(raw)
    if isinstance(doc, list):
        # Expanded JSON-LD is a bare graph array. Keep the public envelope.
        doc = {"@graph": doc}
    doc["@context"] = context_url

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return output_path
