"""Check agriculture operations against the production export writers."""
import json
from pathlib import Path

import jsonschema
import pytest
from pyshacl import validate
from rdflib import Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS

from tests.conftest import jsonld_graph

PS = Namespace('https://publicschema.org/')
AGRI = Namespace('https://publicschema.org/agri/')
ENVIRONMENT = Namespace('https://publicschema.org/environment/')
TRANSPORT = Namespace('https://publicschema.org/transport/')
UCUM = 'ucum'
EXAMPLES = Path(__file__).resolve().parents[1] / 'examples/agriculture-operations'


@pytest.fixture(scope='module')
def exports(built_vocabulary, shacl_graph, owl_graph):
    return built_vocabulary, shacl_graph, owl_graph


def validate_json(record, result, registry):
    schema = result['concept_schemas'][record['@type']]
    jsonschema.Draft202012Validator(schema, registry=registry).validate(record)


def data_graph(record, result, hierarchy=None):
    return jsonld_graph(record, result['context'], hierarchy)


@pytest.mark.parametrize('path', sorted(EXAMPLES.glob('*.json')), ids=lambda p: p.stem)
def test_examples_across_actual_exports(exports, schema_registry, subclass_hierarchy, path):
    result, shapes, ontology = exports
    record = json.loads(path.read_text())
    validate_json(record, result, schema_registry)
    # sh:class follows rdfs:subClassOf in the data graph, so a nested
    # ProducerOrganization satisfies an Organization-typed slot.
    graph = data_graph(record, result, subclass_hierarchy)
    conforms, _, report = validate(graph, shacl_graph=shapes)
    assert conforms, report
    assert (PS[record['@type']], RDF.type, OWL.Class) in ontology


def test_authorization_quantities_are_rate_limits(exports, schema_registry):
    result, shapes, _ = exports
    record = json.loads((EXAMPLES / 'water.json').read_text())
    limits = record['authorized_water_quantity']
    # Several limits apply together; each states its period in a UCUM rate unit.
    assert len(limits) > 1
    assert all('/' in limit['unit_code'] for limit in limits)
    assert len({limit['unit_code'] for limit in limits}) == len(limits)
    assert 'water_quantity_period' not in result['properties']
    assert 'water_quantity_period' not in result['concept_schemas'][record['@type']]['properties']
    scalar = dict(record, authorized_water_quantity=limits[0])
    with pytest.raises(jsonschema.ValidationError):
        validate_json(scalar, result, schema_registry)
    non_numeric = dict(record, authorized_water_quantity=[dict(limits[0], quantity_value='many')])
    with pytest.raises(jsonschema.ValidationError):
        validate_json(non_numeric, result, schema_registry)
    conforms, _, _ = validate(data_graph(non_numeric, result), shacl_graph=shapes)
    assert not conforms


def test_composition_quantity_must_be_numeric(exports, schema_registry):
    result, shapes, _ = exports
    record = json.loads((EXAMPLES / 'feed.json').read_text())
    # Resolve generated references locally, without requesting published schemas.
    quantity = {'@type': 'QuantityValue', 'quantity_value': 'eighteen', 'unit_code': '%', 'unit_scheme': UCUM}
    with pytest.raises(jsonschema.ValidationError):
        validate_json(quantity, result, schema_registry)
    record['product_component'][0]['component_amount'] = quantity
    conforms, _, _ = validate(data_graph(record, result), shacl_graph=shapes)
    assert not conforms


def test_asset_roles_and_permissions_do_not_collapse(exports):
    _, _, ontology = exports
    assert (ENVIRONMENT.WaterUseAuthorization, RDFS.subClassOf, PS.Authorization) in ontology
    assert (AGRI.ProducerOrganization, RDFS.subClassOf, PS.Organization) in ontology
    for name in ('AgriculturalFacility', 'FishingVessel', 'AgriculturalServiceRole'):
        assert (AGRI[name], RDFS.subClassOf, PS.Registration) not in ontology
    assert (PS.Certification, RDFS.subClassOf, PS.Registration) not in ontology
    assert (AGRI.AgriculturalFacility, RDFS.subClassOf, PS.Organization) not in ontology


def test_certification_scope_survives_jsonld(exports):
    result, _, _ = exports
    record = json.loads((EXAMPLES / 'certification.json').read_text())
    graph = data_graph(record, result)
    scopes = list(graph.objects(None, PS.certification_scope))
    assert [graph.value(scope, PS.code_value) for scope in scopes] == [Literal('soil-ph-testing')]
    assert graph.value(scopes[0], PS.code_scheme) is not None
    assert not list(graph.triples((None, PS.authorized_activity, None)))


def test_every_operations_class_has_a_direct_example(exports):
    import yaml

    authored = yaml.safe_load((EXAMPLES.parents[1] / 'schema/agriculture_operations.yaml').read_text())
    environment = yaml.safe_load((EXAMPLES.parents[1] / 'schema/environment.yaml').read_text())
    authored['classes']['WaterUseAuthorization'] = environment['classes']['WaterUseAuthorization']
    represented = {json.loads(path.read_text())['@type'] for path in EXAMPLES.glob('*.json')}
    result, _, _ = exports
    expected = {
        result['context']['@context'][name].removeprefix('https://publicschema.org/')
        for name in authored['classes']
    }
    assert expected <= represented


def test_membership_is_an_institutional_role(exports):
    result, shapes, ontology = exports
    for filename in ('membership-person.json', 'membership-organization.json'):
        record = json.loads((EXAMPLES / filename).read_text())
        assert record['@type'] == 'InstitutionalRole'
        assert record['start_date']
        graph = data_graph(record, result)
        assert list(graph.objects(predicate=PS.role_actor))
        organizations = list(graph.objects(predicate=PS.role_organization))
        assert organizations
        assert all((org, RDF.type, AGRI.ProducerOrganization) in graph for org in organizations)
        assert not list(graph.objects(predicate=PS.service_provider))
    assert (AGRI.ProducerMembership, RDF.type, OWL.Class) not in ontology


REMOVED_CLASSES = (
    'Apiary', 'AquacultureEstablishment', 'LivestockEstablishment', 'PlantNursery',
    'InputSupplierRole', 'PesticideApplicatorRole', 'SeedOperatorRole',
    'FeedProduct', 'FertilizerProduct', 'PesticideProduct',
    'AgriculturalProduct', 'AgriculturalMachinery', 'ProducerMembership',
)


def test_collapsed_and_renamed_classes_stay_removed(exports):
    result, _, ontology = exports
    for name in REMOVED_CLASSES:
        assert f'agri/{name}' not in result['concept_schemas']
        assert (AGRI[name], RDF.type, OWL.Class) not in ontology
    for name in ('AgriculturalInputProduct', 'AgriculturalMachine', 'AgriculturalLaboratory'):
        assert (AGRI[name], RDF.type, OWL.Class) in ontology


REMOVED_SLOTS = (
    (PS, 'facility_location'), (PS, 'facility_operator'), (PS, 'machine_serial_number'),
    (AGRI, 'scheme_operator'), (AGRI, 'producer_member'), (AGRI, 'producer_organization'),
    (AGRI, 'producer_membership_role'), (TRANSPORT, 'vessel_length'),
)


def test_replaced_slots_stay_removed(exports):
    result, _, ontology = exports
    context = result['context']['@context']
    for namespace, name in REMOVED_SLOTS:
        assert name not in context
        assert not list(ontology.triples((namespace[name], None, None)))


@pytest.mark.parametrize('filename, field, codes', [
    ('apiary.json', 'facility_function',
     {'apiary', 'aquaculture_establishment', 'livestock_establishment', 'plant_nursery'}),
    ('supplier.json', 'agricultural_service',
     {'input_supply', 'pesticide_application', 'seed_processing', 'seed_packing', 'seed_marketing'}),
    ('feed.json', 'input_product_category', {'feed', 'fertilising_product', 'pesticide'}),
])
def test_collapsed_subtypes_are_closed_codes(exports, schema_registry, filename, field, codes):
    result, shapes, _ = exports
    record = json.loads((EXAMPLES / filename).read_text())
    kind = record['@type']
    published = set(result['concept_schemas'][kind]['properties'][field]['items']['enum'])
    assert codes <= published
    assert set(record[field]) <= published
    record[field] = ['unlisted_code']
    with pytest.raises(jsonschema.ValidationError):
        validate_json(record, result, schema_registry)
    conforms, _, _ = validate(data_graph(record, result), shacl_graph=shapes)
    assert not conforms


@pytest.mark.parametrize('vocabulary', [
    'agricultural-facility-function', 'agricultural-service-type', 'agricultural-input-category',
])
def test_code_vocabularies_are_published_in_the_agri_domain(exports, vocabulary):
    result, _, _ = exports
    assert vocabulary not in result['vocabularies']
    published = result['vocabularies']['agri/' + vocabulary]
    assert published['uri'] == f'https://publicschema.org/vocab/agri/{vocabulary}'
    assert all(value['uri'].startswith(published['uri'] + '/') for value in published['values'])


def test_component_basis_and_role_are_coded(exports):
    result, _, ontology = exports
    properties = result['concept_schemas']['ProductComponent']['properties']
    for name in ('component_basis', 'component_role'):
        assert 'CodedValue.schema.json' in json.dumps(properties[name])
        assert (PS[name], RDFS.range, PS.CodedValue) in ontology
    record = json.loads((EXAMPLES / 'component.json').read_text())
    assert record['component_basis']['@type'] == 'CodedValue'
    assert record['component_role']['@type'] == 'CodedValue'


def test_vessel_length_overall_keeps_the_transport_domain(exports):
    result, _, _ = exports
    term = result['context']['@context']['vessel_length_overall']
    assert term['@id'] == str(TRANSPORT.vessel_length_overall)
    graph = data_graph(json.loads((EXAMPLES / 'vessel.json').read_text()), result)
    assert list(graph.objects(predicate=TRANSPORT.vessel_length_overall))


@pytest.mark.parametrize('role_file, subject_file', [
    ('facility-operator.json', 'facility.json'),
    ('irrigation-operator.json', 'irrigation.json'),
])
def test_operation_is_a_dated_asset_party_role(role_file, subject_file):
    role = json.loads((EXAMPLES / role_file).read_text())
    subject = json.loads((EXAMPLES / subject_file).read_text())
    assert role['@type'] == 'AssetPartyRole'
    assert role['subject_uri'] == subject['@id']
    assert role['asset_role_type']['code_value'] == 'operator'
    assert role['start_date']


def _quantities(value):
    if isinstance(value, dict):
        if value.get('@type') == 'QuantityValue':
            yield value
        for item in value.values():
            yield from _quantities(item)
    elif isinstance(value, list):
        for item in value:
            yield from _quantities(item)


# water.json is owned by the environment module and checked by its own tests.
OWN_EXAMPLES = sorted(path for path in EXAMPLES.glob('*.json') if path.name != 'water.json')


@pytest.mark.parametrize('path', OWN_EXAMPLES, ids=lambda p: p.stem)
def test_example_quantities_use_ucum(path):
    for quantity in _quantities(json.loads(path.read_text())):
        assert quantity['unit_scheme'] == UCUM
        assert quantity['unit_code'] not in {'percent', 'ha'}
