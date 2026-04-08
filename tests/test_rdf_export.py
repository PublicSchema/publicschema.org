"""Tests for RDF export generation (Turtle, SHACL).

Unit tests use synthetic schemas; integration tests run against the real schema.
"""

import json
from pathlib import Path

import pytest
import rdflib
from rdflib.namespace import RDF, RDFS, SKOS

from build.build import build_vocabulary
from build.rdf_export import (
    SH, build_full_jsonld, build_shacl, build_turtle, load_graph,
    write_full_jsonld, write_shacl, write_turtle,
)
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


# ===========================================================================
# Full vocabulary JSON-LD
# ===========================================================================

class TestBuildFullJsonld:
    """Full vocabulary JSON-LD serialization from synthetic schema data."""

    def test_full_jsonld_is_valid(
        self, tmp_schema, write_concept, write_property,
    ):
        """Generated JSON-LD parses back into rdflib without errors."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        content = build_full_jsonld(result)
        doc = json.loads(content)
        assert "@context" in doc
        assert "@graph" in doc
        assert isinstance(doc["@graph"], list)
        assert len(doc["@graph"]) > 0

    def test_full_jsonld_contains_class_and_property(
        self, tmp_schema, write_concept, write_property,
    ):
        """Full JSON-LD graph contains both concepts and properties."""
        write_concept("widget.yaml", make_concept(id="Widget", properties=["size"]))
        write_property("size.yaml", make_property(id="size", type="integer"))
        result = build_vocabulary(tmp_schema)

        content = build_full_jsonld(result)
        doc = json.loads(content)
        ids = {node.get("@id") for node in doc["@graph"]}
        # rdflib expands CURIEs to full URIs
        assert any("Widget" in str(i) for i in ids if i)
        assert any("size" in str(i) for i in ids if i)


class TestWriteFullJsonld:
    """File writing for full vocabulary JSON-LD."""

    def test_writes_file(
        self, tmp_schema, tmp_path, write_concept, write_property,
    ):
        """write_full_jsonld creates publicschema.jsonld in the dist directory."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        out_path = write_full_jsonld(result, dist_dir)

        assert out_path.exists()
        assert out_path.name == "publicschema.jsonld"
        assert out_path.stat().st_size > 0


class TestFullJsonldIntegration:
    """Full JSON-LD export against the real schema directory."""

    @pytest.fixture(scope="class")
    def real_result(self):
        return build_vocabulary(SCHEMA_DIR)

    def test_real_schema_full_jsonld_parses(self, real_result):
        """Full JSON-LD from the real schema parses without errors."""
        content = build_full_jsonld(real_result)
        doc = json.loads(content)
        assert "@context" in doc
        assert len(doc["@graph"]) > 0

    def _parse_full_jsonld(self, real_result):
        """Parse the full JSON-LD with the inline context (avoids network fetch)."""
        content = build_full_jsonld(real_result)
        doc = json.loads(content)
        doc["@context"] = real_result["context"]["@context"]
        g = rdflib.Graph()
        g.parse(data=json.dumps(doc), format="json-ld")
        return g

    def test_real_schema_full_jsonld_has_expected_counts(self, real_result):
        """Full JSON-LD contains at least the expected number of classes and properties."""
        g = self._parse_full_jsonld(real_result)
        classes = list(g.triples((None, RDF.type, RDFS.Class)))
        properties = list(g.triples((None, RDF.type, RDF.Property)))
        schemes = list(g.triples((None, RDF.type, SKOS.ConceptScheme)))
        assert len(classes) >= 19, f"Expected >= 19 classes, got {len(classes)}"
        assert len(properties) >= 91, f"Expected >= 91 properties, got {len(properties)}"
        assert len(schemes) >= 10, f"Expected >= 10 concept schemes, got {len(schemes)}"

    def test_real_schema_full_jsonld_roundtrips_via_turtle(self, real_result):
        """Full JSON-LD and Turtle produce the same number of triples."""
        ttl = build_turtle(real_result)
        g_ttl = rdflib.Graph()
        g_ttl.parse(data=ttl, format="turtle")

        g_jsonld = self._parse_full_jsonld(real_result)

        assert len(g_jsonld) == len(g_ttl), (
            f"JSON-LD graph has {len(g_jsonld)} triples, "
            f"Turtle has {len(g_ttl)}"
        )


# ===========================================================================
# SHACL shapes
# ===========================================================================

class TestBuildShacl:
    """SHACL shape generation from synthetic schema data."""

    def test_shacl_is_valid_rdf(
        self, tmp_schema, write_concept, write_property,
    ):
        """Generated SHACL parses as valid Turtle."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")
        assert len(g) > 0

    def test_shacl_has_node_shape_per_concept(
        self, tmp_schema, write_concept, write_property,
    ):
        """Each concept gets one sh:NodeShape targeting its class URI."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_concept("widget.yaml", make_concept(id="Widget", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        shapes = list(g.triples((None, RDF.type, SH.NodeShape)))
        assert len(shapes) == 2

        thing_shape = rdflib.URIRef("https://test.example.org/ThingShape")
        widget_shape = rdflib.URIRef("https://test.example.org/WidgetShape")
        assert (thing_shape, SH.targetClass, rdflib.URIRef("https://test.example.org/Thing")) in g
        assert (widget_shape, SH.targetClass, rdflib.URIRef("https://test.example.org/Widget")) in g

    def test_shacl_string_property_has_datatype(
        self, tmp_schema, write_concept, write_property,
    ):
        """String properties get sh:datatype xsd:string."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name", type="string"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        # Find the property shape for "name"
        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/name"))))
        assert len(prop_shapes) == 1
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH.datatype, rdflib.XSD.string) in g

    def test_shacl_date_property_has_datatype(
        self, tmp_schema, write_concept, write_property,
    ):
        """Date properties get sh:datatype xsd:date."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["created"]))
        write_property("created.yaml", make_property(id="created", type="date"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/created"))))
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH.datatype, rdflib.XSD.date) in g

    def test_shacl_single_cardinality_has_max_count(
        self, tmp_schema, write_concept, write_property,
    ):
        """Single-cardinality properties get sh:maxCount 1."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name", cardinality="single"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/name"))))
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH.maxCount, rdflib.Literal(1)) in g

    def test_shacl_multiple_cardinality_no_max_count(
        self, tmp_schema, write_concept, write_property,
    ):
        """Multiple-cardinality properties do not get sh:maxCount."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["tags"]))
        write_property("tags.yaml", make_property(id="tags", cardinality="multiple"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/tags"))))
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH.maxCount, None) not in g

    def test_shacl_concept_ref_has_class_constraint(
        self, tmp_schema, write_concept, write_property,
    ):
        """concept:X type properties get sh:class pointing to the referenced concept."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["owner"]))
        write_concept("person.yaml", make_concept(id="Person"))
        write_property("owner.yaml", make_property(id="owner", type="concept:Person"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/owner"))))
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH["class"], rdflib.URIRef("https://test.example.org/Person")) in g
        assert (ps_node, SH.nodeKind, SH.BlankNodeOrIRI) in g

    def test_shacl_uri_property_has_iri_node_kind(
        self, tmp_schema, write_concept, write_property,
    ):
        """URI-typed properties get sh:nodeKind sh:IRI."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["homepage"]))
        write_property("homepage.yaml", make_property(id="homepage", type="uri"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/homepage"))))
        ps_node = prop_shapes[0][0]
        assert (ps_node, SH.nodeKind, SH.IRI) in g

    def test_shacl_vocabulary_generates_in_constraint(
        self, tmp_schema, write_concept, write_property, write_vocabulary,
    ):
        """Vocabulary-backed properties get sh:in with the value codes."""
        write_vocabulary("colors.yaml", make_vocabulary(
            id="colors",
            values=[
                {"code": "red", "label": {"en": "Red", "fr": "Rouge", "es": "Rojo"},
                 "definition": {"en": "Red.", "fr": "Rouge.", "es": "Rojo."}},
                {"code": "blue", "label": {"en": "Blue", "fr": "Bleu", "es": "Azul"},
                 "definition": {"en": "Blue.", "fr": "Bleu.", "es": "Azul."}},
            ],
        ))
        write_concept("thing.yaml", make_concept(id="Thing", properties=["color"]))
        write_property("color.yaml", make_property(id="color", vocabulary="colors"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        prop_shapes = list(g.triples((None, SH.path, rdflib.URIRef("https://test.example.org/color"))))
        ps_node = prop_shapes[0][0]
        # sh:in should exist
        in_lists = list(g.triples((ps_node, SH["in"], None)))
        assert len(in_lists) == 1
        # Extract values from the RDF list
        collection = rdflib.collection.Collection(g, in_lists[0][2])
        codes = [str(item) for item in collection]
        assert "red" in codes
        assert "blue" in codes


class TestWriteShacl:
    """File writing for SHACL output."""

    def test_writes_file(
        self, tmp_schema, tmp_path, write_concept, write_property,
    ):
        """write_shacl creates publicschema.shacl.ttl in the dist directory."""
        write_concept("thing.yaml", make_concept(id="Thing", properties=["name"]))
        write_property("name.yaml", make_property(id="name"))
        result = build_vocabulary(tmp_schema)

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        out_path = write_shacl(result, dist_dir)

        assert out_path.exists()
        assert out_path.name == "publicschema.shacl.ttl"
        assert out_path.stat().st_size > 0


class TestShaclIntegration:
    """SHACL shapes against the real schema directory."""

    @pytest.fixture(scope="class")
    def real_result(self):
        return build_vocabulary(SCHEMA_DIR)

    def test_real_schema_shacl_parses(self, real_result):
        """SHACL from the real schema parses without errors."""
        shacl_ttl = build_shacl(real_result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")
        assert len(g) > 0

    def test_real_schema_shacl_has_shapes_for_all_concepts(self, real_result):
        """Every concept has a corresponding NodeShape."""
        shacl_ttl = build_shacl(real_result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        shapes = set(s for s, p, o in g.triples((None, RDF.type, SH.NodeShape)))
        assert len(shapes) >= 19, f"Expected >= 19 shapes, got {len(shapes)}"

    def test_real_schema_shacl_property_constraints(self, real_result):
        """Spot-check: Person shape has a date_of_birth property with xsd:date datatype."""
        shacl_ttl = build_shacl(real_result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        person_shape = rdflib.URIRef("https://publicschema.org/PersonShape")
        dob_uri = rdflib.URIRef("https://publicschema.org/date_of_birth")

        # Find the property shape for date_of_birth on Person
        found = False
        for _, _, prop_node in g.triples((person_shape, SH.property, None)):
            if (prop_node, SH.path, dob_uri) in g:
                found = True
                assert (prop_node, SH.datatype, rdflib.XSD.date) in g
                assert (prop_node, SH.maxCount, rdflib.Literal(1)) in g
                break
        assert found, "PersonShape should have a property constraint for date_of_birth"

    def test_real_schema_shacl_validates_sample_data(self, real_result):
        """A valid Person document passes SHACL validation against the generated shapes."""
        from pyshacl import validate as shacl_validate

        shacl_ttl = build_shacl(real_result)

        # Build a minimal valid data graph
        data_ttl = """
        @prefix ps: <https://publicschema.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        _:person1 a ps:Person ;
            ps:given_name "Amina" ;
            ps:family_name "Diallo" ;
            ps:date_of_birth "1988-03-15"^^xsd:date .
        """

        conforms, results_graph, results_text = shacl_validate(
            data_graph=data_ttl,
            data_graph_format="turtle",
            shacl_graph=shacl_ttl,
            shacl_graph_format="turtle",
        )
        assert conforms, f"SHACL validation failed:\n{results_text}"

    def test_real_schema_shacl_rejects_invalid_cardinality(self, real_result):
        """A Person with two date_of_birth values fails SHACL validation (maxCount 1)."""
        from pyshacl import validate as shacl_validate

        shacl_ttl = build_shacl(real_result)

        data_ttl = """
        @prefix ps: <https://publicschema.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        _:person1 a ps:Person ;
            ps:given_name "Amina" ;
            ps:date_of_birth "1988-03-15"^^xsd:date ;
            ps:date_of_birth "1990-01-01"^^xsd:date .
        """

        conforms, results_graph, results_text = shacl_validate(
            data_graph=data_ttl,
            data_graph_format="turtle",
            shacl_graph=shacl_ttl,
            shacl_graph_format="turtle",
        )
        assert not conforms, "Two date_of_birth values should violate maxCount 1"
