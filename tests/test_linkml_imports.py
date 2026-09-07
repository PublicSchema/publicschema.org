"""The renderer follows the selected composite, including its namespace."""

import pytest
import yaml

from build.build import build_vocabulary
from build.linkml_reader import load_raw_from_linkml


@pytest.fixture
def write_schema(tmp_path):
    def write(name, **fields):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = {
            "id": f"https://publicschema.org/linkml/{path.stem}",
            "name": path.stem,
            "default_prefix": "publicschema",
            "prefixes": {
                "publicschema": "https://publicschema.org/",
                "linkml": "https://w3id.org/linkml/",
            },
            **fields,
        }
        path.write_text(yaml.safe_dump(doc))
        return path
    return write


def test_inline_composite_definitions_build_without_ambient_siblings(tmp_path, write_schema):
    write_schema(
        "publicschema.yaml", imports=["linkml:types"],
        classes={"InlineRecord": {"slots": ["display_name", "status"]}},
        slots={"display_name": {"range": "string"}, "status": {"range": "Status"}},
        enums={"Status": {"permissible_values": {"active": {"title": "Active"}}}},
    )
    write_schema("unimported.yaml", classes={"Unimported": {}}, slots={"unused": {}})

    result = build_vocabulary(tmp_path)

    assert set(result["concepts"]) == {"InlineRecord"}
    assert set(result["properties"]) == {"display_name", "status"}
    assert set(result["vocabularies"]) == {"status"}
    assert result["concept_schemas"]["InlineRecord"]["properties"]["status"]["enum"] == ["active"]


def test_empty_composite_does_not_import_undeclared_siblings(tmp_path, write_schema):
    write_schema("publicschema.yaml")
    write_schema("domain.yaml", classes={"Unimported": {}})
    assert load_raw_from_linkml(tmp_path)["concepts"] == {}


def test_nested_imports_resolve_from_their_module_and_cycles_terminate(tmp_path, write_schema):
    write_schema("publicschema.yaml", imports=["nested/domain", "external/upstream", "publicschema-extensions"])
    write_schema("nested/domain.yaml", imports=["types", "../publicschema"], classes={"Record": {"slots": ["code"]}})
    write_schema("nested/types.yaml", slots={"code": {"range": "Code"}}, enums={"Code": {"permissible_values": {"one": {}}}})
    write_schema("types.yaml", slots={"ambient_code": {}})
    write_schema("external/upstream.yaml", classes={"UpstreamClass": {}}, enums={"UpstreamEnum": {}})
    write_schema("publicschema-extensions.yaml", classes={"ExternalAlignment": {}}, enums={"MatchStrength": {}})

    result = load_raw_from_linkml(tmp_path)

    assert set(result["concepts"]) == {"Record"}
    assert set(result["properties"]) == {"code"}
    assert set(result["vocabularies"]) == {"code"}
    assert result["properties"]["code"]["vocabulary"] == "code"


def test_import_order_and_inline_overrides_match_linkml(tmp_path, write_schema):
    write_schema("publicschema.yaml", imports=["first", "second"], classes={"Record": {"title": "Inline"}})
    write_schema("first.yaml", classes={"Record": {"title": "First"}}, slots={"code": {"range": "string"}})
    write_schema("second.yaml", classes={"Record": {"title": "Second"}}, slots={"code": {"range": "integer"}})

    result = load_raw_from_linkml(tmp_path)

    assert result["concepts"]["Record"]["label"]["en"] == "Inline"
    assert result["properties"]["code"]["type"] == "integer"


def test_imported_sibling_catalogs_are_preserved(tmp_path, write_schema):
    write_schema("publicschema.yaml", imports=["catalog/bibliography", "catalog/credentials", "catalog/categories"])
    write_schema("catalog/bibliography.yaml", classes={"SourceCitation": {"annotations": {"citation_id": "source", "title": "Source"}}})
    write_schema("catalog/credentials.yaml", classes={"Credential": {"abstract": True}, "RecordCredential": {"is_a": "Credential", "annotations": {"subject_concept": "Record"}}})
    write_schema("catalog/categories.yaml", enums={"PropertyCategory": {"permissible_values": {"identity": {"title": "Identity"}}}})

    result = load_raw_from_linkml(tmp_path)

    assert set(result["bibliography"]) == {"source"}
    assert set(result["credentials"]) == {"RecordCredential"}
    assert set(result["categories"]) == {"identity"}
    assert result["concepts"] == {}
    assert result["vocabularies"] == {}


def test_missing_import_is_reported_instead_of_an_incomplete_catalog(tmp_path, write_schema):
    write_schema("publicschema.yaml", imports=["missing"])
    with pytest.raises(FileNotFoundError, match="missing.yaml"):
        load_raw_from_linkml(tmp_path)


def test_nonlocal_product_import_reports_renderer_limit(tmp_path, write_schema):
    write_schema("publicschema.yaml", imports=["https://example.org/schema"])
    with pytest.raises(ValueError, match="Unsupported non-local LinkML import"):
        load_raw_from_linkml(tmp_path)


@pytest.mark.parametrize("expanded_prefix", [False, True])
def test_custom_namespace_preserves_class_uris_and_context(tmp_path, write_schema, expanded_prefix):
    import rdflib
    from rdflib.namespace import OWL, RDF

    from build.linkml_rdf_export import write_turtle

    base = "https://example.org/custom/"
    prefix = {"prefix_reference": base} if expanded_prefix else base
    composite = write_schema("publicschema.yaml", default_prefix="custom", prefixes={"custom": prefix, "linkml": "https://w3id.org/linkml/"}, imports=["linkml:types", "domain"])
    write_schema(
        "domain.yaml", default_prefix="custom", prefixes={"custom": prefix},
        classes={
            "Record": {"class_uri": "custom:Record", "slots": ["display_name"]},
            "DomainRecord": {"class_uri": "custom:domain/Record", "is_a": "Record"},
        },
        slots={"display_name": {"slot_uri": "custom:display_name", "range": "string"}},
    )

    result = build_vocabulary(tmp_path)

    assert result["meta"]["base_uri"] == base
    assert result["concepts"]["Record"]["uri"] == base + "Record"
    assert result["concepts"]["domain/Record"]["uri"] == base + "domain/Record"
    assert result["concepts"]["domain/Record"]["supertypes"] == ["Record"]
    assert result["properties"]["display_name"]["uri"] == base + "display_name"
    assert result["context"]["@context"]["@vocab"] == base
    assert result["context"]["@context"]["display_name"] == base + "display_name"

    turtle = write_turtle(tmp_path / "output.ttl", composite=composite)
    graph = rdflib.Graph().parse(turtle)
    for concept in result["concepts"].values():
        assert (rdflib.URIRef(concept["uri"]), RDF.type, OWL.Class) in graph


def test_authored_slot_alias_validates_with_public_context_and_shacl(tmp_path, write_schema):
    import json

    import jsonschema
    import rdflib
    from pyshacl import validate

    from build.linkml_rdf_export import write_shacl

    base = "https://example.org/custom/"
    composite = write_schema(
        "publicschema.yaml", default_prefix="custom",
        prefixes={"custom": base, "linkml": "https://w3id.org/linkml/"},
        imports=["linkml:types", "nested/domain"],
    )
    write_schema(
        "nested/domain.yaml", default_prefix="custom", prefixes={"custom": base},
        classes={"Record": {"class_uri": "custom:Record", "slots": ["display_name"]}},
        slots={"display_name": {"slot_uri": "custom:label", "range": "string"}},
    )

    assert load_raw_from_linkml(tmp_path)["properties"]["display_name"]["uri"] == base + "label"
    result = build_vocabulary(tmp_path)
    instance = {"display_name": "Example"}
    jsonschema.validate(instance, result["concept_schemas"]["Record"])
    graph = rdflib.Graph().parse(data=json.dumps({
        "@context": result["context"]["@context"],
        "@id": "urn:test:record", "@type": "Record", **instance,
    }), format="json-ld")
    assert (rdflib.URIRef("urn:test:record"), rdflib.URIRef(base + "label"), rdflib.Literal("Example")) in graph
    shapes = write_shacl(tmp_path / "shapes.ttl", composite=composite)
    conforms, _, report = validate(graph, shacl_graph=str(shapes))
    assert conforms, report


@pytest.mark.parametrize("root_first", [False, True])
def test_short_id_fixture_prefers_root_regardless_of_import_order(root_first):
    from tests.conftest import _key_by_short_id

    root = {"id": "Person"}
    snapshot = {"id": "Person", "domain": "crvs"}
    entries = [("Person", root), ("crvs/Person", snapshot)]
    if not root_first:
        entries.reverse()
    assert _key_by_short_id(dict(entries))["Person"] is root
