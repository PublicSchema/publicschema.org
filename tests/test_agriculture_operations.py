"""Check agriculture operations against the production export writers."""
import json
from pathlib import Path

import jsonschema
import pytest
from referencing import Registry, Resource
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, OWL, RDFS

from build.build import build_vocabulary
from build.linkml_rdf_export import DEFAULT_LINKML_COMPOSITE, write_shacl, write_turtle

PS = Namespace('https://publicschema.org/')
EXAMPLES = Path(__file__).resolve().parents[1] / 'examples/agriculture-operations'


@pytest.fixture(scope='module')
def exports(tmp_path_factory):
    result = build_vocabulary(DEFAULT_LINKML_COMPOSITE.parent)
    out = tmp_path_factory.mktemp('agriculture-operations')
    shapes = Graph().parse(write_shacl(out / 'shapes.ttl'), format='turtle')
    ontology = Graph().parse(write_turtle(out / 'ontology.ttl'), format='turtle')
    return result, shapes, ontology


def validate_json(record, result):
    registry = Registry().with_resources(
        (schema['$id'], Resource.from_contents(schema))
        for schema in result['concept_schemas'].values()
    )
    schema = result['concept_schemas'][record['@type']]
    jsonschema.Draft202012Validator(schema, registry=registry).validate(record)


def data_graph(record, result):
    document = {'@context': result['context']['@context'], **record}
    # PyLD performs the JSON-LD to RDF conversion. RDFLib's direct JSON-LD
    # parser retains Python int for xsd:decimal and misleads pySHACL.
    quads = jsonld.to_rdf(document, {'format': 'application/n-quads'})
    return Graph().parse(data=quads, format='nquads')


@pytest.mark.parametrize('path', sorted(EXAMPLES.glob('*.json')), ids=lambda p: p.stem)
def test_examples_across_actual_exports(exports, path):
    result, shapes, ontology = exports
    record = json.loads(path.read_text())
    validate_json(record, result)
    graph = data_graph(record, result)
    conforms, _, report = validate(graph, shacl_graph=shapes)
    assert conforms, report
    assert (PS[record['@type']], RDF.type, OWL.Class) in ontology


def test_authorization_quantity_is_not_an_array(exports):
    result, shapes, _ = exports
    record = json.loads((EXAMPLES / 'water.json').read_text())
    record['authorized_water_quantity'] = [record['authorized_water_quantity']] * 2
    with pytest.raises(jsonschema.ValidationError):
        validate_json(record, result)
    conforms, _, _ = validate(data_graph(record, result), shacl_graph=shapes)
    assert not conforms


def test_composition_quantity_must_be_numeric(exports):
    result, shapes, _ = exports
    record = json.loads((EXAMPLES / 'feed.json').read_text())
    # Resolve generated references locally, without requesting published schemas.
    quantity = {'@type': 'QuantityValue', 'quantity_value': 'eighteen', 'unit_code': 'percent'}
    with pytest.raises(jsonschema.ValidationError):
        validate_json(quantity, result)
    record['product_component'][0]['component_amount'] = quantity
    conforms, _, _ = validate(data_graph(record, result), shacl_graph=shapes)
    assert not conforms


def test_asset_roles_and_permissions_do_not_collapse(exports):
    _, _, ontology = exports
    assert (PS.WaterUseAuthorization, RDFS.subClassOf, PS.Authorization) in ontology
    assert (PS.VeterinaryMedicinalProduct, RDFS.subClassOf, PS.MedicinalProduct) in ontology
    assert (PS.ProducerOrganization, RDFS.subClassOf, PS.Organization) in ontology
    for name in ('AgriculturalFacility', 'FishingVessel', 'AgriculturalCertification', 'AgriculturalServiceRole'):
        assert (PS[name], RDFS.subClassOf, PS.Registration) not in ontology
    assert (PS.AgriculturalFacility, RDFS.subClassOf, PS.Organization) not in ontology


def test_certification_scope_survives_jsonld(exports):
    result, _, _ = exports
    record = json.loads((EXAMPLES / 'certification.json').read_text())
    graph = data_graph(record, result)
    assert (None, PS.certification_scope, Literal('soil pH testing')) in graph
    assert not list(graph.triples((None, PS.authorized_activity, None)))


def test_every_operations_class_has_a_direct_example():
    import yaml

    authored = yaml.safe_load((EXAMPLES.parents[1] / 'schema/agriculture_operations.yaml').read_text())
    represented = {json.loads(path.read_text())['@type'] for path in EXAMPLES.glob('*.json')}
    assert set(authored['classes']) <= represented


def test_membership_preserves_actor_identity_and_interval(exports):
    result, shapes, ontology = exports
    for filename in ('membership-person.json', 'membership-organization.json'):
        record = json.loads((EXAMPLES / filename).read_text())
        validate_json(record, result)
        graph = data_graph(record, result)
        conforms, _, report = validate(graph, shacl_graph=shapes)
        assert conforms, report
        assert list(graph.objects(predicate=PS.producer_member))
        assert not list(graph.objects(predicate=PS.service_provider))
    assert (PS.ProducerMembership, RDFS.subClassOf, PS.GroupMembership) not in ontology
