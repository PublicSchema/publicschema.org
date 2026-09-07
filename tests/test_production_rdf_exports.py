"""Exercise the RDF writers used by the production build and public context."""

import json
from collections import Counter
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF, SH

from build.build import build_vocabulary
from build.linkml_rdf_export import (
    DEFAULT_CONTEXT_URL,
    DEFAULT_LINKML_COMPOSITE,
    write_full_jsonld,
    write_shacl,
    write_turtle,
)

PS = Namespace("https://publicschema.org/")
EX = Namespace("https://example.org/custom/")


def _jsonld_graph(document, context, context_url=DEFAULT_CONTEXT_URL):
    """Resolve the published context from this build, without network access."""
    def load_context(url, options=None):
        assert url == context_url, f"Unexpected remote document: {url}"
        return {"contextUrl": None, "documentUrl": url, "document": context}

    expanded = jsonld.expand(document, options={"documentLoader": load_context})
    return Graph().parse(data=json.dumps(expanded), format="json-ld")


def _write_exports(directory, composite, context_url=DEFAULT_CONTEXT_URL):
    turtle = write_turtle(directory / "publicschema.ttl", composite=composite)
    shapes = write_shacl(directory / "publicschema.shacl.ttl", composite=composite)
    full_jsonld = write_full_jsonld(
        directory / "publicschema.jsonld", context_url=context_url, composite=composite,
    )
    return (
        Graph().parse(turtle, format="turtle"),
        Graph().parse(shapes, format="turtle"),
        json.loads(full_jsonld.read_text()),
    )


@pytest.fixture(scope="module")
def production_exports(tmp_path_factory):
    result = build_vocabulary(DEFAULT_LINKML_COMPOSITE.parent)
    exports = _write_exports(
        tmp_path_factory.mktemp("production-rdf"), DEFAULT_LINKML_COMPOSITE,
    )
    return result, *exports


def test_production_jsonld_preserves_turtle_graph(production_exports):
    result, turtle, _, document = production_exports
    assert document["@context"] == DEFAULT_CONTEXT_URL
    linked = _jsonld_graph(document, result["context"])
    assert (PS.Person, RDF.type, OWL.Class) in linked
    for public_name, native_name in (
        ("metrics/Metric", "Metric"),
        ("metrics/MetricObservation", "MetricObservation"),
        ("crvs/Person", "CrvsPerson"),
    ):
        public_uri = PS[public_name]
        assert result["concepts"][public_name]["uri"] == str(public_uri)
        for graph in (turtle, linked):
            assert (public_uri, RDF.type, OWL.Class) in graph
            assert (PS[native_name], RDF.type, OWL.Class) not in graph
    for graph in (turtle, linked):
        assert (PS["metrics/metric_value"], RDF.type, OWL.DatatypeProperty) in graph
        assert (PS.metric_value, RDF.type, OWL.DatatypeProperty) not in graph
    # Whole-graph canonicalization of the catalog's thousands of enum list
    # nodes is prohibitively slow. Compare every named triple and structural
    # counts, then check representative anonymous restrictions and lists with
    # RDFLib's concise bounded descriptions. The small custom composite below
    # additionally exercises full-graph isomorphism through the same writers.
    def ground_triples(graph):
        return {triple for triple in graph if not any(isinstance(n, BNode) for n in triple)}

    assert ground_triples(turtle) == ground_triples(linked)
    assert len(turtle) == len(linked)
    assert Counter(turtle.predicates()) == Counter(linked.predicates())
    assert Counter(turtle.objects(predicate=RDF.type)) == Counter(linked.objects(predicate=RDF.type))
    for subject in (PS.Person, PS.Sex, PS.Country):
        assert isomorphic(turtle.cbd(subject), linked.cbd(subject)), subject


def test_all_production_term_uris_match_public_paths_and_rdf_shapes(production_exports):
    result, turtle, shapes, _ = production_exports
    base_uri = result["meta"]["base_uri"].rstrip("/")
    classes = set(turtle.subjects(RDF.type, OWL.Class))
    properties = (
        set(turtle.subjects(RDF.type, OWL.ObjectProperty))
        | set(turtle.subjects(RDF.type, OWL.DatatypeProperty))
    )
    # This is the current public catalog's path contract. Custom composites
    # may deliberately map JSON field names to different RDF URI suffixes.
    for group in ("concepts", "properties"):
        for term in result[group].values():
            assert term["uri"] == base_uri + term["path"], term["id"]
    assert not {URIRef(term["uri"]) for term in result["concepts"].values()} - classes
    assert not {URIRef(term["uri"]) for term in result["properties"].values()} - properties

    for concept in result["concepts"].values():
        uri = URIRef(concept["uri"])
        targets = set(shapes.subjects(SH.targetClass, uri))
        assert targets, uri
        paths = {
            path
            for target in targets
            for property_shape in shapes.objects(target, SH.property)
            for path in shapes.objects(property_shape, SH.path)
        }
        expected_paths = {
            URIRef(result["properties"][entry["id"]]["uri"])
            for entry in concept["properties"]
        }
        assert expected_paths <= paths, (uri, expected_paths - paths)


def test_public_person_codes_validate_in_json_schema_and_shacl(production_exports):
    result, _, shapes, _ = production_exports
    person = {
        "@context": DEFAULT_CONTEXT_URL,
        "@type": "Person",
        "name": "Amina Diallo",  # inherited from Party
        "given_name": "Amina",
        "date_of_birth": "1988-03-15",
        "sex": "male",
        "country_of_birth": "af",  # standard_code is AF, public code is af
    }
    jsonschema.validate(person, result["concept_schemas"]["Person"])
    data = _jsonld_graph(person, result["context"])
    assert (None, PS.sex, Literal("male")) in data
    conforms, _, report = validate(data, shacl_graph=shapes)
    assert conforms, report


@pytest.mark.parametrize(
    ("changes", "constraint"),
    [
        ({"sex": "not-a-sex-code"}, SH.InConstraintComponent),
        ({"country_of_birth": "AF"}, SH.InConstraintComponent),
        ({"name": ["Amina", "Diallo"]}, SH.MaxCountConstraintComponent),
    ],
)
def test_production_shapes_reject_invalid_codes_and_inherited_cardinality(
    production_exports, changes, constraint,
):
    result, _, shapes, _ = production_exports
    person = {"@context": DEFAULT_CONTEXT_URL, "@type": "Person", **changes}
    conforms, report, _ = validate(
        _jsonld_graph(person, result["context"]), shacl_graph=shapes,
    )
    assert not conforms
    assert (None, SH.sourceConstraintComponent, constraint) in report


@pytest.mark.parametrize(("value", "expected"), [(42.5, True), ("not-a-number", False)])
def test_public_numeric_metric_observation_targets_production_shape(
    production_exports, value, expected,
):
    result, _, shapes, _ = production_exports
    document = {
        "@context": DEFAULT_CONTEXT_URL,
        "@type": "MetricObservation",
        "metric_value": value,
    }
    schema = result["concept_schemas"]["metrics/MetricObservation"]
    if expected:
        jsonschema.validate(document, schema)
    else:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(document, schema)

    data = _jsonld_graph(document, result["context"])
    target = PS["metrics/MetricObservation"]
    path = PS["metrics/metric_value"]
    assert (None, RDF.type, target) in data
    assert (None, SH.targetClass, target) in shapes
    assert (None, path, None) in data
    conforms, report, text = validate(data, shacl_graph=shapes)
    assert conforms == expected, text
    if not expected:
        assert (None, SH.sourceConstraintComponent, SH.DatatypeConstraintComponent) in report


@pytest.fixture(scope="module")
def custom_exports(tmp_path_factory):
    directory = tmp_path_factory.mktemp("custom-rdf")
    # A local import proves that the supplied composite, its imports and
    # prefixes drive all writers instead of the repository default schema.
    (directory / "codes.yaml").write_text("""\
id: https://example.org/custom/codes
name: codes
prefixes:
  outside: https://example.net/codes/
enums:
  Mode:
    permissible_values:
      af:
        meaning: outside:Afghanistan
        annotations:
          standard_code: AF
      self_:
        meaning: outside:Self
        annotations:
          standard_code: self
      raw:
        description: A code without a meaning IRI.
""", encoding="utf-8")
    composite = directory / "publicschema.yaml"
    composite.write_text("""\
id: https://example.org/custom/schema
name: custom
default_prefix: custom
default_range: string
prefixes:
  custom: https://example.org/custom/
  linkml: https://w3id.org/linkml/
  schema: http://schema.org/
imports:
  - linkml:types
  - codes
classes:
  Base:
    abstract: true
    slots: [label]
  Record:
    is_a: Base
    exact_mappings: [schema:Thing]
    slots: [state, selection]
  DomainRecord:
    class_uri: custom:domain/Record
    is_a: Record
    slots: [native_value]
slots:
  label:
    required: true
  state:
    range: Mode
    required: true
  selection:
    any_of:
      - range: Mode
      - range: integer
  native_value:
    slot_uri: custom:domain/value
    range: integer
""", encoding="utf-8")
    before = composite.read_bytes(), (directory / "codes.yaml").read_bytes()
    exports = _write_exports(directory / "out", composite)
    assert before == (composite.read_bytes(), (directory / "codes.yaml").read_bytes())
    # Exercise the reader-to-public-context bridge as well as the generators.
    # The public schema: prefix deliberately uses https, while OWL uses http.
    context = build_vocabulary(directory)["context"]
    return context, *exports


def test_custom_composite_jsonld_preserves_imports_and_namespace_meanings(custom_exports):
    context, turtle, shapes, document = custom_exports
    linked = _jsonld_graph(document, context)
    assert (EX.Record, RDF.type, OWL.Class) in linked
    assert (PS.Person, RDF.type, OWL.Class) not in linked
    assert URIRef("https://example.net/codes/Afghanistan") in set(turtle.all_nodes())
    for graph in (turtle, linked):
        assert (EX["domain/Record"], RDF.type, OWL.Class) in graph
        assert (EX.DomainRecord, RDF.type, OWL.Class) not in graph
        assert (EX["domain/value"], RDF.type, OWL.DatatypeProperty) in graph
        assert (EX.native_value, RDF.type, OWL.DatatypeProperty) not in graph
    assert (None, SH.targetClass, EX["domain/Record"]) in shapes
    assert (None, SH.path, EX["domain/value"]) in shapes
    assert isomorphic(turtle, linked)


@pytest.mark.parametrize("code", ["af", "self", "raw"])
def test_custom_enum_codes_and_any_of_use_public_literals(custom_exports, code):
    context, _, shapes, _ = custom_exports
    document = {
        "@context": DEFAULT_CONTEXT_URL,
        "@type": "Record",
        "label": "Example",
        "state": code,
        "selection": {"@value": code, "@type": "xsd:string"},
    }
    conforms, _, report = validate(_jsonld_graph(document, context), shacl_graph=shapes)
    assert conforms, report


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"state": "AF"}, False),
        ({"state": "self_"}, False),
        ({"state": {"@id": "https://example.net/codes/Afghanistan"}}, False),
        ({"label": ["One", "Two"]}, False),
        ({"selection": {"@value": "unknown", "@type": "xsd:string"}}, False),
        ({"selection": 7}, True),
    ],
)
def test_custom_shapes_preserve_other_constraints(custom_exports, changes, expected):
    context, _, shapes, _ = custom_exports
    document = {
        "@context": DEFAULT_CONTEXT_URL, "@type": "Record",
        "label": "Example", "state": "af", **changes,
    }
    conforms, _, report = validate(_jsonld_graph(document, context), shacl_graph=shapes)
    assert conforms == expected, report


def test_custom_context_and_shapes_share_authored_slot_uri(custom_exports):
    context, _, shapes, _ = custom_exports
    document = {
        "@context": DEFAULT_CONTEXT_URL,
        "@type": "domain/Record",
        "label": "Example",
        "state": "af",
        "native_value": 3,
    }
    data = _jsonld_graph(document, context)
    assert (None, RDF.type, EX["domain/Record"]) in data
    assert (None, EX["domain/value"], Literal(3)) in data
    conforms, _, report = validate(data, shacl_graph=shapes)
    assert conforms, report


def test_relative_composite_uses_callers_working_directory(tmp_path, monkeypatch):
    composite = tmp_path / "custom.yaml"
    composite.write_text("""\
id: https://example.org/custom/schema
name: custom
default_prefix: custom
prefixes:
  custom: https://example.org/custom/
classes:
  RelativeRecord: {}
""", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    context_url = "https://example.org/custom/context.jsonld"
    turtle, shapes, document = _write_exports(
        tmp_path / "out", Path("custom.yaml"), context_url=context_url,
    )
    assert (EX.RelativeRecord, RDF.type, OWL.Class) in turtle
    assert (None, SH.targetClass, EX.RelativeRecord) in shapes
    assert document["@context"] == context_url
    linked = _jsonld_graph(document, {"@context": {}}, context_url=context_url)
    assert isomorphic(turtle, linked)
