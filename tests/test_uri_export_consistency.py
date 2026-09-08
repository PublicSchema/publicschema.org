"""Keep SHACL value kinds aligned with the public JSON-LD context."""

import json

import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SH, XSD

from build.build import build_vocabulary
from build.linkml_rdf_export import (
    DEFAULT_LINKML_COMPOSITE,
    write_full_jsonld,
    write_shacl,
    write_turtle,
)

PS = "https://publicschema.org/"


def _context_graph(document):
    """Expand an instance through the generated public context."""
    return Graph().parse(data=json.dumps(jsonld.expand(document)), format="json-ld")


def _property_shapes(shapes, field):
    return list(shapes.subjects(SH.path, URIRef(f"{PS}{field}")))


@pytest.fixture(scope="module")
def public_context_and_shapes(tmp_path_factory):
    context = build_vocabulary(DEFAULT_LINKML_COMPOSITE.parent)["context"]["@context"]
    export_dir = tmp_path_factory.mktemp("uri-export")
    shapes_path = export_dir / "shapes.ttl"
    shapes = Graph().parse(write_shacl(shapes_path), format="turtle")
    turtle = Graph().parse(write_turtle(export_dir / "vocabulary.ttl"), format="turtle")
    full_jsonld = json.loads(
        write_full_jsonld(export_dir / "vocabulary.jsonld").read_text(encoding="utf-8")
    )
    return context, shapes, turtle, full_jsonld


@pytest.mark.parametrize(
    ("class_name", "field"),
    [
        ("Registration", "registered_subject"),
        ("AgriculturalFacility", "facility_operator"),
    ],
)
def test_context_uri_values_expand_to_iris_and_conform(
    public_context_and_shapes, class_name, field,
):
    context, shapes, turtle, full_jsonld = public_context_and_shapes
    value = "https://example.org/subjects/amina"
    property_uri = URIRef(f"{PS}{field}")
    data = _context_graph({"@context": context, "@type": class_name, field: value})

    assert (None, property_uri, URIRef(value)) in data
    assert validate(data, shacl_graph=shapes)[0]
    for property_shape in _property_shapes(shapes, field):
        assert (property_shape, SH.nodeKind, SH.IRI) in shapes
        assert (property_shape, SH.datatype, XSD.anyURI) not in shapes
        assert (property_shape, SH.nodeKind, SH.Literal) not in shapes
    assert (property_uri, RDF.type, OWL.ObjectProperty) in turtle
    assert (property_uri, RDF.type, OWL.DatatypeProperty) not in turtle
    assert (property_uri, RDFS.range, XSD.anyURI) not in turtle
    restrictions = set(turtle.subjects(OWL.onProperty, property_uri))
    assert any((restriction, OWL.allValuesFrom, OWL.Thing) in turtle for restriction in restrictions)
    assert not any(
        (restriction, OWL.allValuesFrom, XSD.anyURI) in turtle for restriction in restrictions
    )
    property_node = next(
        node for node in full_jsonld["@graph"] if node["@id"] == str(property_uri)
    )
    assert str(OWL.ObjectProperty) in property_node["@type"]
    assert str(OWL.DatatypeProperty) not in property_node["@type"]


def test_uri_shape_rejects_an_explicit_jsonld_literal(public_context_and_shapes):
    context, shapes, _, _ = public_context_and_shapes
    value = "https://example.org/subjects/amina"
    data = _context_graph({
        "@context": context,
        "@type": "Registration",
        "registered_subject": {"@value": value},
    })

    assert (None, URIRef(f"{PS}registered_subject"), Literal(value)) in data
    conforms, report, _ = validate(data, shacl_graph=shapes)
    assert not conforms
    assert (None, SH.sourceConstraintComponent, SH.NodeKindConstraintComponent) in report


def test_uri_adjustment_preserves_date_string_and_enum_constraints(
    public_context_and_shapes,
):
    context, shapes, turtle, _ = public_context_and_shapes
    data = _context_graph({
        "@context": context,
        "@type": "Person",
        "name": "Amina",
        "date_of_birth": "1988-03-15",
        "sex": "female",
    })

    assert (None, URIRef(f"{PS}name"), Literal("Amina")) in data
    assert (None, URIRef(f"{PS}date_of_birth"), Literal("1988-03-15", datatype=XSD.date)) in data
    assert (None, URIRef(f"{PS}sex"), Literal("female")) in data
    assert validate(data, shacl_graph=shapes)[0]

    for property_shape in _property_shapes(shapes, "date_of_birth"):
        assert (property_shape, SH.nodeKind, SH.Literal) in shapes
        assert (property_shape, SH.datatype, XSD.date) in shapes
    for property_shape in _property_shapes(shapes, "name"):
        assert (property_shape, SH.nodeKind, SH.Literal) in shapes
        assert (property_shape, SH.datatype, XSD.string) in shapes
    enum_shapes = _property_shapes(shapes, "sex")
    assert enum_shapes
    enum_values = {
        value
        for property_shape in enum_shapes
        for value_list in shapes.objects(property_shape, SH["in"])
        for value in Collection(shapes, value_list)
    }
    assert Literal("female") in enum_values
    for field, datatype in (("date_of_birth", XSD.date), ("name", XSD.string)):
        property_uri = URIRef(f"{PS}{field}")
        assert (property_uri, RDF.type, OWL.DatatypeProperty) in turtle
        assert (property_uri, RDFS.range, datatype) in turtle
    sex = URIRef(f"{PS}sex")
    assert (sex, RDF.type, OWL.ObjectProperty) in turtle
    assert (sex, RDFS.range, URIRef(f"{PS}Sex")) in turtle
