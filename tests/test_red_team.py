"""Regression tests for issues found during red team review.

Each test documents a bug that was found and fixed, with severity
and a reference to the affected code.
"""

import json
from pathlib import Path

import jsonschema
import pytest
import rdflib
from pyld import jsonld
from rdflib.namespace import RDF, RDFS, XSD

from build.build import build_vocabulary
from build.rdf_export import SH, build_shacl
from tests.conftest import SCHEMA_DIR, make_concept, make_property, make_vocabulary


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_result():
    return build_vocabulary(SCHEMA_DIR)


# ---------------------------------------------------------------------------
# BUG 1 (Critical): SHACL sh:in uses untyped literals while
# sh:datatype xsd:string requires typed literals.
#
# File: build/rdf_export.py, build_shacl()
# Affects: all 23 vocabulary-backed properties
# ---------------------------------------------------------------------------

class TestShaclVocabTypedLiterals:
    """SHACL sh:in literals must be typed xsd:string to match sh:datatype."""

    def test_typed_string_passes_shacl_vocab_constraint(self, real_result):
        """A typed xsd:string value for a vocabulary property should conform.

        Currently fails: sh:in contains untyped literals ("male") while
        sh:datatype requires typed literals ("male"^^xsd:string). The two
        constraints are mutually exclusive, so no data can satisfy both.
        """
        from pyshacl import validate as shacl_validate

        shacl_ttl = build_shacl(real_result)

        data_ttl = """
        @prefix ps: <https://publicschema.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        _:p1 a ps:Person ;
            ps:given_name "Amina" ;
            ps:gender "male"^^xsd:string .
        """

        conforms, _, results_text = shacl_validate(
            data_graph=data_ttl,
            data_graph_format="turtle",
            shacl_graph=shacl_ttl,
            shacl_graph_format="turtle",
        )
        assert conforms, (
            f"Typed xsd:string 'male' should satisfy both sh:datatype and sh:in.\n"
            f"SHACL report:\n{results_text}"
        )

    def test_shacl_in_list_uses_typed_literals(
        self, tmp_schema, write_concept, write_property, write_vocabulary,
    ):
        """sh:in list entries should be typed xsd:string literals, not plain."""
        write_vocabulary("colors.yaml", make_vocabulary(
            id="colors",
            values=[
                {"code": "red", "label": {"en": "Red", "fr": "Rouge", "es": "Rojo"},
                 "definition": {"en": "Red.", "fr": "Rouge.", "es": "Rojo."}},
            ],
        ))
        write_concept("thing.yaml", make_concept(id="Thing", properties=["color"]))
        write_property("color.yaml", make_property(id="color", vocabulary="colors"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)
        g = rdflib.Graph()
        g.parse(data=shacl_ttl, format="turtle")

        # Find the sh:in list for the color property
        color_uri = rdflib.URIRef("https://test.example.org/color")
        prop_shapes = list(g.triples((None, SH.path, color_uri)))
        ps_node = prop_shapes[0][0]
        in_lists = list(g.triples((ps_node, SH["in"], None)))
        collection = rdflib.collection.Collection(g, in_lists[0][2])

        for item in collection:
            assert item.datatype == XSD.string, (
                f"sh:in entry {item!r} should have datatype xsd:string, "
                f"got {item.datatype!r}"
            )


# ---------------------------------------------------------------------------
# BUG 2 (Critical): context.jsonld missing @type:@id coercions for
# URI-valued predicates (rdfs:subClassOf, schema:domainIncludes, etc.)
#
# File: build/build.py, build_vocabulary() context_map construction
# Affects: all JSON-LD documents when consumed by external processors
# ---------------------------------------------------------------------------

class TestContextUriCoercions:
    """The published context must coerce URI-valued predicates to @id references."""

    def test_subclass_expands_as_id_not_value(self, real_result):
        """rdfs:subClassOf values should expand to @id, not @value.

        Currently fails: the generated context lacks @type:@id for
        rdfs:subClassOf, so pyld expands URI strings as plain literals.
        """
        # Find a concept doc that has supertypes (Household inherits Group)
        household_doc = None
        for path, doc in real_result["jsonld_docs"].items():
            if path.endswith("Household.jsonld"):
                household_doc = doc
                break
        assert household_doc is not None, "Household concept doc not found"

        # Replace the context URL with the inline context
        doc = dict(household_doc)
        if "@graph" in doc:
            # @graph structure: extract the concept node
            concept_node = doc["@graph"][0]
            doc_to_expand = dict(concept_node)
            doc_to_expand["@context"] = real_result["context"]["@context"]
        else:
            doc_to_expand = dict(doc)
            doc_to_expand["@context"] = real_result["context"]["@context"]

        expanded = jsonld.expand(doc_to_expand)
        assert len(expanded) > 0, "Expansion produced no results"

        subclass_key = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        assert subclass_key in expanded[0], (
            f"rdfs:subClassOf not found in expanded output. Keys: {list(expanded[0].keys())}"
        )

        subclass_values = expanded[0][subclass_key]
        for val in subclass_values:
            assert "@id" in val, (
                f"rdfs:subClassOf expanded to a literal (@value) instead of a URI (@id): {val}"
            )

    def test_domain_includes_expands_as_id(self, real_result):
        """schema:domainIncludes values should expand to @id, not @value.

        Currently fails: the context lacks @type:@id for schema:domainIncludes.
        """
        # Find a property doc that has domainIncludes
        prop_doc = None
        for path, doc in real_result["jsonld_docs"].items():
            if path.startswith("properties/") and path.endswith("given_name.jsonld"):
                prop_doc = doc
                break
        assert prop_doc is not None

        doc = dict(prop_doc)
        doc["@context"] = real_result["context"]["@context"]

        expanded = jsonld.expand(doc)
        domain_key = "https://schema.org/domainIncludes"
        assert domain_key in expanded[0], "domainIncludes not in expanded output"

        for val in expanded[0][domain_key]:
            assert "@id" in val, (
                f"domainIncludes expanded to literal instead of URI: {val}"
            )

    def test_range_includes_expands_as_id(self, real_result):
        """schema:rangeIncludes values should expand to @id, not @value.

        Currently fails for concept:X type properties where rangeIncludes
        is a full URI string that should expand to @id.
        """
        # Find a property with concept: type (rangeIncludes is a concept URI)
        prop_doc = None
        for path, doc in real_result["jsonld_docs"].items():
            if path.startswith("properties/") and path.endswith("beneficiary.jsonld"):
                prop_doc = doc
                break
        assert prop_doc is not None

        doc = dict(prop_doc)
        doc["@context"] = real_result["context"]["@context"]

        expanded = jsonld.expand(doc)
        range_key = "https://schema.org/rangeIncludes"
        assert range_key in expanded[0], "rangeIncludes not in expanded output"

        for val in expanded[0][range_key]:
            assert "@id" in val, (
                f"rangeIncludes expanded to literal instead of URI: {val}"
            )


# ---------------------------------------------------------------------------
# BUG 3 (Medium): JSON Schema for concepts does not include inherited
# properties from supertypes.
#
# File: build/build.py, concept_schemas construction (lines ~486-507)
# Affects: Household (missing Group properties), Family (same), Farm (same)
# ---------------------------------------------------------------------------

class TestJsonSchemaInheritance:
    """JSON Schema for subtypes should include inherited properties."""

    def test_household_schema_includes_group_properties(self, real_result):
        """Household JSON Schema should include Group's 'name' property.

        Currently fails: the schema builder only walks the concept's own
        properties list, not supertype properties.
        """
        household_schema = real_result["concept_schemas"]["Household"]
        props = household_schema["properties"]

        assert "name" in props, (
            f"Household schema should include 'name' (inherited from Group). "
            f"Got: {sorted(props.keys())}"
        )

    def test_household_schema_includes_group_type(self, real_result):
        """Household JSON Schema should include Group's 'group_type' property."""
        household_schema = real_result["concept_schemas"]["Household"]
        props = household_schema["properties"]

        assert "group_type" in props, (
            f"Household schema should include 'group_type' (inherited from Group). "
            f"Got: {sorted(props.keys())}"
        )

    def test_family_schema_includes_group_properties(self, real_result):
        """Family JSON Schema should include Group's properties."""
        family_schema = real_result["concept_schemas"]["Family"]
        props = family_schema["properties"]

        assert "name" in props, (
            f"Family schema should include 'name' (inherited from Group). "
            f"Got: {sorted(props.keys())}"
        )


# ---------------------------------------------------------------------------
# BUG 4 (Medium): SHACL shapes do not include inherited property
# constraints from supertypes.
#
# File: build/rdf_export.py, build_shacl()
# Affects: same subtypes as BUG 3
# ---------------------------------------------------------------------------

class TestShaclInheritance:
    """SHACL shapes for subtypes should constrain inherited properties."""

    def test_household_shape_constrains_name(self, real_result):
        """HouseholdShape should reject two 'name' values (maxCount 1, from Group).

        Currently fails: HouseholdShape only has constraints for Household's
        own properties, not inherited ones from Group.
        """
        from pyshacl import validate as shacl_validate

        shacl_ttl = build_shacl(real_result)

        data_ttl = """
        @prefix ps: <https://publicschema.org/> .

        _:hh a ps:Household ;
            ps:name "Alpha" ;
            ps:name "Beta" .
        """

        conforms, _, results_text = shacl_validate(
            data_graph=data_ttl,
            data_graph_format="turtle",
            shacl_graph=shacl_ttl,
            shacl_graph_format="turtle",
        )
        assert not conforms, (
            "Household with two 'name' values should fail maxCount 1 "
            "(inherited from Group)"
        )


# ---------------------------------------------------------------------------
# BUG 5 (Medium): SHACL sh:nodeKind BlankNodeOrIRI is incompatible
# with geojson_geometry's @type:@json (produces rdf:JSON literals).
#
# File: build/rdf_export.py, build_shacl() geojson_geometry handling
# Affects: geometry, geocodes properties
# ---------------------------------------------------------------------------

class TestShaclGeojsonGeometry:
    """SHACL shapes for geojson_geometry properties should accept JSON literals."""

    def test_geojson_literal_passes_validation(
        self, tmp_schema, write_concept, write_property,
    ):
        """A geojson_geometry value (rdf:JSON literal) should pass SHACL.

        Currently fails: the SHACL shape uses sh:nodeKind sh:BlankNodeOrIRI,
        but @type:@json produces an rdf:JSON typed literal, not a node.
        """
        from pyshacl import validate as shacl_validate

        write_concept("area.yaml", make_concept(id="Area", properties=["shape"]))
        write_property("shape.yaml", make_property(id="shape", type="geojson_geometry"))
        result = build_vocabulary(tmp_schema)

        shacl_ttl = build_shacl(result)

        # rdf:JSON literal is how @type:@json serializes in Turtle
        data_ttl = """
        @prefix test: <https://test.example.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

        _:a1 a test:Area ;
            test:shape "{\\\"type\\\":\\\"Point\\\",\\\"coordinates\\\":[0,0]}"^^rdf:JSON .
        """

        conforms, _, results_text = shacl_validate(
            data_graph=data_ttl,
            data_graph_format="turtle",
            shacl_graph=shacl_ttl,
            shacl_graph_format="turtle",
        )
        assert conforms, (
            f"rdf:JSON literal should pass SHACL for geojson_geometry.\n"
            f"Report:\n{results_text}"
        )


# ---------------------------------------------------------------------------
# BUG 6 (Medium): Credential schemas don't require 'VerifiableCredential'
# in the type array.
#
# File: build/build.py, credential schema construction (lines ~556-560)
# Affects: all credential schemas
# ---------------------------------------------------------------------------

class TestCredentialSchemaTypeArray:
    """Credential schemas must require VerifiableCredential in type array."""

    def test_missing_verifiable_credential_type_rejected(self, real_result):
        """A VC with type: ['IdentityCredential'] (no VerifiableCredential) should fail.

        Currently passes: the schema only checks for the specific credential
        type, not for the W3C-required 'VerifiableCredential' entry.
        """
        cred_schema = real_result["credential_schemas"]["IdentityCredential"]

        bad_vc = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://publicschema.org/ctx/draft.jsonld",
            ],
            "type": ["IdentityCredential"],  # missing VerifiableCredential
            "issuer": "did:web:example.org",
            "credentialSubject": {
                "given_name": "Test",
            },
        }

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(
                bad_vc, cred_schema,
                format_checker=jsonschema.FormatChecker(),
            )


# ---------------------------------------------------------------------------
# BUG 9 (Low): JSON Schema filename uses lower() but $id uses PascalCase.
#
# File: build/build.py, write_outputs() line 649
# Affects: all concept schemas (PaymentEvent -> paymentevent.schema.json
# but $id references PaymentEvent.schema.json)
# ---------------------------------------------------------------------------

class TestSchemaFilenameIdConsistency:
    """Schema filename should be consistent with the $id URI."""

    def test_schema_id_matches_filename(self, real_result):
        """The schema $id path should match the actual filename."""
        for concept_id, schema in real_result["concept_schemas"].items():
            schema_id = schema["$id"]
            # Extract the filename from $id
            id_filename = schema_id.rsplit("/", 1)[-1]
            # The actual filename written by write_outputs (PascalCase)
            actual_filename = f"{concept_id}.schema.json"

            assert id_filename == actual_filename, (
                f"Concept {concept_id}: $id references '{id_filename}' "
                f"but file is written as '{actual_filename}'"
            )
