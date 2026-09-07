"""Local registry identity, spatial and health/holding pilot checks."""
import copy
import importlib.util
import json
from pathlib import Path
from decimal import Decimal

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from referencing import Registry, Resource
from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace('https://publicschema.org/')
spec = importlib.util.spec_from_file_location('pilot_profile', ROOT / 'examples/registry-pilots/profile.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


@pytest.fixture(scope='module')
def exports(tmp_path_factory):
    result = build_vocabulary(ROOT / 'schema')
    shapes = Graph().parse(write_shacl(tmp_path_factory.mktemp('registry') / 'shapes.ttl'), format='turtle')
    records = json.loads((ROOT / 'examples/registry-pilots/records.json').read_text())
    registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in result['concept_schemas'].values())
    return result, shapes, records, registry


def graph(records, context):
    # Use the standards conversion; RDFLib direct JSON-LD parsing can give
    # xsd:decimal a Python float/int and cause false pySHACL datatype errors.
    quads = jsonld.to_rdf({'@context':context['@context'],'@graph':records}, {'format':'application/n-quads'})
    return Graph().parse(data=quads,format='nquads')


def test_actual_pilot_exports_and_identity(exports):
    result, shapes, records, registry = exports
    for record in records:
        jsonschema.Draft202012Validator(result['concept_schemas'][record['@type']],registry=registry,format_checker=jsonschema.FormatChecker()).validate(record)
    data = graph(records,result['context'])
    ok, _, report = validate(data, shacl_graph=shapes, inference='rdfs')
    assert ok, report
    assert len(set(data.subjects(RDF.type,PS.HealthFacility))) == 1
    assert len(set(data.subjects(RDF.type,PS.FacilityManagementAssignment))) == 2
    assert len(list(data.subjects(PS.linked_parcel,Namespace('https://example.org/')['parcel/one']))) == 2
    assert len(set(data.subjects(RDF.type,PS.LandTenureAssertion))) == 2
    for name in ('RegistryEntry','Farm','AgriculturalParcel','Registration'):
        jsonschema.Draft202012Validator(result['concept_schemas'][name],registry=registry).validate({})


def test_wrong_facility_manager_type_fails_shacl(exports):
    result, shapes, records, _ = exports
    changed = copy.deepcopy(records)
    assignment = next(r for r in changed if r['@type']=='FacilityManagementAssignment')
    assignment['managing_organization'] = 'https://example.org/person/one'
    assert not validate(graph(changed,result['context']),shacl_graph=shapes,inference='rdfs')[0]


def test_qualified_reference_resolves_without_collapsing_local_ids():
    entries = {('https://example.org/register/a','001'):{'subject_uri':'https://example.org/one','subject_type':str(PS.Person)},('https://example.org/register/b','001'):{'subject_uri':'https://example.org/two','subject_type':str(PS.Organization)}}
    subjects = {'https://example.org/one':{'@type':str(PS.Person)},'https://example.org/two':{'@type':str(PS.Organization)}}
    a = {'register_uri':'https://example.org/register/a','record_id':'001','subject_type':str(PS.Person)}
    b = {'register_uri':'https://example.org/register/b','record_id':'001','subject_type':str(PS.Organization)}
    assert profile.resolve_reference(a,entries,subjects)['subject_uri'] != profile.resolve_reference(b,entries,subjects)['subject_uri']
    assert profile.resolve_reference({**a,'register_uri':'https://unavailable.example/register'},entries,subjects)['state']=='missing-record'
    assert profile.resolve_reference(a,entries,{})['state']=='missing-subject'
    for bad in ({**a,'subject_type':str(PS.Organization)},{**a,'subject_uri':'https://example.org/two'}):
        with pytest.raises(ValueError):profile.resolve_reference(bad,entries,subjects)
    with pytest.raises(ValueError):profile.resolve_reference(a,entries,{'https://example.org/one':{'@type':str(PS.Organization)}})


def test_submission_requiredness_and_late_recording():
    entry = {'register_uri':'https://example.org/r','record_id':'001','subject_uri':'https://example.org/s','subject_type':str(PS.Farm),'recorded_at':'2026-09-07T00:00:00Z','valid_from':'2026-01-01','valid_to':'2026-12-31'}
    profile.validate_entry(entry)
    with pytest.raises(KeyError):profile.validate_entry({})
    with pytest.raises(ValueError):profile.validate_period({'valid_from':'2026-03-01','valid_to':'2026-02-01'})
    profile.validate_period({'valid_from':'2026-03-01'})
    with pytest.raises(ValueError):profile.validate_entry({**entry,'recorded_at':'2026-09-07T00:00:00'})


def test_area_conversion_preserves_precision_and_rejects_wrong_dimension():
    quantity={'quantity_value':Decimal('12500.25'),'unit_code':'m2','unit_scheme':profile.UCUM}
    assert profile.area_hectares(quantity)==Decimal('1.250025')
    assert profile.area_hectares({**quantity,'quantity_value':Decimal('1.250025'),'unit_code':'har'})==Decimal('1.250025')
    for change in ({'unit_code':'kg'},{'quantity_value':-1},{'quantity_value':'NaN'},{'unit_scheme':'https://example.org/local'}):
        with pytest.raises(ValueError):profile.area_hectares({**quantity,**change})


def test_geometry_encoding_crs_and_coordinate_order():
    value={'geometry_encoding':'application/geo+json','coordinate_reference_system':profile.CRS84,'geometry_literal':'{"type":"Point","coordinates":[100,13]}'}
    assert profile.validate_geometry(value)['coordinates']==[100,13]
    for literal in ('{"type":"Point","coordinates":[13,100]}','{"type":"LineString","coordinates":[[100,13],[101,14]]}','{"type":"Polygon","coordinates":[[[100,13],[101,13],[101,14]]]}'):
        with pytest.raises(ValueError):profile.validate_geometry({**value,'geometry_literal':literal})
    with pytest.raises(ValueError):profile.validate_geometry({**value,'coordinate_reference_system':'http://www.opengis.net/def/crs/EPSG/0/4326'})
    with pytest.raises(ValueError):profile.validate_geometry({**value,'geometry_encoding':'WKT'})
    profile.validate_geometry({**value,'geometry_literal':'{"type":"Polygon","coordinates":[[[100,13],[101,13],[101,14],[100,13]]]}'} )


def test_unmapped_code_is_preserved(exports):
    result, _, _, registry=exports
    schema=result['concept_schemas']['CodedValue']
    for code in ('known','local-only','unknown','retired'):
        payload={'code_scheme':'https://example.org/v1/codes','code_value':code}
        jsonschema.Draft202012Validator(schema,registry=registry).validate(payload)
        assert payload['code_value']==code and 'code_meaning' not in payload


def test_reference_resolution_of_the_actual_pilot_records(exports):
    result, _, records, _ = exports
    types = {k: v['uri'] for k, v in result['concepts'].items()}
    subjects = profile.subject_index(records, types)
    entry = next(r for r in records if r['@type'] == 'RegistryEntry')
    profile.validate_entry(entry)
    reference = {k: entry[k] for k in ('register_uri', 'record_id', 'subject_uri', 'subject_type')}
    resolved = profile.resolve_reference(reference, {(entry['register_uri'], entry['record_id']): entry}, subjects)
    assert resolved['state'] == 'resolved'
    assert resolved['subject']['@type'] == str(PS.HealthFacility)
    assert resolved['subject_uri'] != entry['@id']


def test_area_conversion_does_not_round_long_decimal_coefficients():
    value = Decimal('12345678901234567890123456789.123456789')
    assert profile.area_hectares({'quantity_value': value, 'unit_code': 'har', 'unit_scheme':profile.UCUM}) == value
    expected = Decimal('1234567890123456789012345.6789123456789')
    assert profile.area_hectares({'quantity_value': value, 'unit_code': 'm2', 'unit_scheme':profile.UCUM}) == expected


def test_every_authored_shared_class_and_field_survives_exports(exports):
    import yaml
    from rdflib.namespace import SH
    result, shapes, _, _ = exports
    for module in ('registry', 'agriculture', 'health_services', 'farm_operators', 'agriculture_biology'):
        authored = yaml.safe_load((ROOT / f'schema/{module}.yaml').read_text())
        for name, definition in authored.get('classes', {}).items():
            assert name in result['concepts']
            assert result['concepts'][name]['maturity'] == 'draft'
            assert result['concepts'][name]['bibliography_refs'], name
            assert set(definition.get('slots', [])) <= result['concept_schemas'][name]['properties'].keys()
        for name in authored.get('slots', {}):
            assert name in result['properties']
            assert list(shapes.subjects(SH.path, PS[name])), name
