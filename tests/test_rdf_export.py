"""Tests for RDF export generation (Turtle, SHACL).

Unit tests use synthetic schemas; integration tests run against the real schema.
"""

import json
from pathlib import Path

import pytest
import rdflib
from rdflib.namespace import RDF, RDFS, SKOS

from build.build import build_vocabulary
from build.rdf_export import build_turtle, load_graph, write_turtle
from tests.conftest import SCHEMA_DIR, make_concept, make_property, make_vocabulary


SCHEMA = rdflib.Namespace("https://schema.org/")


# ---------------------------------------------------------------------------
# Unit tests (synthetic schema)
# ---------------------------------------------------------------------------

class TestBuildTurtle:
    """Turtle serialization from synthetic schema data."""

    def test_turtle_is_valid_rdf(
        self, tmp_schema, write_concept, write_property,
    ):
        """Generated Turtle parses back into rdflib without errors."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        ttl = build_turtle(result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")
        assert len(g) > 0

    def test_turtle_contains_class_triple(
        self, tmp_schema, write_concept, write_property,
    ):
        """Turtle output contains rdfs:Class triples for concepts."""
        write_concept("widget.yaml", make_concept(id="Widget", properties=["size"]))
        write_property("size.yaml", make_property(id="size", type="integer"))
        result = build_vocabulary(tmp_schema)

        ttl = build_turtle(result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")

        widget_uri = rdflib.URIRef("https://test.example.org/Widget")
        assert (widget_uri, RDF.type, RDFS.Class) in g

    def test_turtle_contains_property_triple(
        self, tmp_schema, write_concept, write_property,
    ):
        """Turtle output contains rdf:Property triples for properties."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["color"]))
        write_property("color.yaml", make_property(id="color"))
        result = build_vocabulary(tmp_schema)

        ttl = build_turtle(result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")

        color_uri = rdflib.URIRef("https://test.example.org/color")
        assert (color_uri, RDF.type, RDF.Property) in g

    def test_turtle_contains_vocabulary(
        self, tmp_schema, write_concept, write_property, write_vocabulary,
    ):
        """Turtle output contains skos:ConceptScheme for vocabularies."""
        write_vocabulary("colors.yaml", make_vocabulary(id="colors"))
        write_concept("thing.yaml", make_concept(id="Thing", properties=["color"]))
        write_property("color.yaml", make_property(id="color", vocabulary="colors"))
        result = build_vocabulary(tmp_schema)

        ttl = build_turtle(result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")

        vocab_uri = rdflib.URIRef("https://test.example.org/vocab/colors")
        assert (vocab_uri, RDF.type, SKOS.ConceptScheme) in g


class TestWriteTurtle:
    """File writing for Turtle output."""

    def test_writes_file(
        self, tmp_schema, tmp_path, write_concept, write_property,
    ):
        """write_turtle creates publicschema.ttl in the dist directory."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        out_path = write_turtle(result, dist_dir)

        assert out_path.exists()
        assert out_path.name == "publicschema.ttl"
        assert out_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Integration test (real schema)
# ---------------------------------------------------------------------------

class TestTurtleIntegration:
    """Turtle export against the real schema directory."""

    @pytest.fixture(scope="class")
    def real_result(self):
        return build_vocabulary(SCHEMA_DIR)

    def test_real_schema_turtle_parses(self, real_result):
        """Turtle from the real schema parses without errors."""
        ttl = build_turtle(real_result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")
        assert len(g) > 0

    def test_real_schema_turtle_has_expected_counts(self, real_result):
        """Turtle contains at least the expected number of classes and properties."""
        ttl = build_turtle(real_result)
        g = rdflib.Graph()
        g.parse(data=ttl, format="turtle")

        classes = list(g.triples((None, RDF.type, RDFS.Class)))
        properties = list(g.triples((None, RDF.type, RDF.Property)))
        schemes = list(g.triples((None, RDF.type, SKOS.ConceptScheme)))

        assert len(classes) >= 19, f"Expected >= 19 classes, got {len(classes)}"
        assert len(properties) >= 91, f"Expected >= 91 properties, got {len(properties)}"
        assert len(schemes) >= 10, f"Expected >= 10 concept schemes, got {len(schemes)}"

    def test_real_schema_turtle_roundtrips(self, real_result):
        """Turtle serialization roundtrips: serialize then parse produces same triple count."""
        ttl = build_turtle(real_result)
        g1 = rdflib.Graph()
        g1.parse(data=ttl, format="turtle")

        ttl2 = g1.serialize(format="turtle")
        g2 = rdflib.Graph()
        g2.parse(data=ttl2, format="turtle")

        assert len(g1) == len(g2)
