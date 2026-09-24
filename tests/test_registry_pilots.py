"""Local registry identity, spatial and health/holding pilot checks."""
import copy
import json
from decimal import Decimal
from pathlib import Path

import jsonschema
import pytest
from pyshacl import validate
from rdflib import Namespace, URIRef
from rdflib.namespace import RDF

from tests.conftest import jsonld_graph, load_example

ROOT = Path(__file__).resolve().parents[1]
PS = Namespace('https://publicschema.org/')
AGRI = Namespace('https://publicschema.org/agri/')
HEALTH = Namespace('https://publicschema.org/health/')
LAND = Namespace('https://publicschema.org/land/')
profile = load_example('registry-pilots/profile.py')


@pytest.fixture(scope='module')
def exports(built_vocabulary, shacl_graph, schema_registry):
    records = json.loads((ROOT / 'examples/registry-pilots/records.json').read_text())
    return built_vocabulary, shacl_graph, records, schema_registry


def graph(records, context):
    return jsonld_graph(records, context)


def test_actual_pilot_exports_and_identity(exports):
    result, shapes, records, registry = exports
    for record in records:
        jsonschema.Draft202012Validator(result['concept_schemas'][record['@type']],registry=registry,format_checker=jsonschema.FormatChecker()).validate(record)
    data = graph(records,result['context'])
    ok, _, report = validate(data, shacl_graph=shapes, inference='rdfs')
    assert ok, report
    # Protects the registry-foundations decision: each role and tenure assertion is its own record, not a merged field.
    assert len(set(data.subjects(RDF.type, HEALTH.HealthFacility))) == 1
    assert len(set(data.subjects(RDF.type, PS.AssetPartyRole))) == 2
    assert len(list(data.subjects(AGRI.linked_parcel,Namespace('https://example.org/')['parcel/one']))) == 2
    assert len(set(data.subjects(RDF.type, LAND.LandTenureAssertion))) == 2
    building = Namespace('https://example.org/')['building/clinic']
    assert data.value(building, PS.spatial_geometry) == Namespace('https://example.org/')['geometry/clinic']
    assert all('register_owner' in r for r in records if r['@type'] == 'Register')
    for name in ('RegistryEntry','agri/Farm','agri/AgriculturalParcel','Registration'):
        jsonschema.Draft202012Validator(result['concept_schemas'][name],registry=registry).validate({})


def test_land_tenure_contract_and_shared_geometry(exports):
    import yaml
    result, shapes, records, registry = exports
    properties = result['properties']
    assert properties['tenure_object']['type'] == 'concept:land/LandAdministrativeUnit'
    assert properties['tenure_holder']['type'] == 'uri'
    assert properties['tenure_category']['vocabulary'] == 'land/tenure-category'
    assert {v['code'] for v in result['vocabularies']['land/tenure-category']['values']} == {'right', 'restriction', 'responsibility'}
    for name in ('tenure_holder', 'tenure_type', 'boundary_recognition', 'land_tenure'):
        assert properties[name]['sensitivity'] == 'sensitive', name
    # A share is a whole-number fraction, as in LADM, so a third is exact.
    assert 'tenure_share' not in properties
    slots = yaml.safe_load((ROOT / 'schema/land.yaml').read_text())['slots']
    assert (slots['tenure_share_numerator']['range'], slots['tenure_share_numerator']['minimum_value']) == ('integer', 0)
    assert (slots['tenure_share_denominator']['range'], slots['tenure_share_denominator']['minimum_value']) == ('integer', 1)
    tenure = jsonschema.Draft202012Validator(result['concept_schemas']['land/LandTenureAssertion'], registry=registry)
    tenure.validate({'tenure_share_numerator': 1, 'tenure_share_denominator': 3})
    for bad in ({'tenure_share_denominator': 0}, {'tenure_share_numerator': 0.5}, {'tenure_share_numerator': -1}):
        with pytest.raises(jsonschema.ValidationError):
            tenure.validate(bad)
    for kind in ('agri/AgriculturalParcel', 'land/LandSpatialUnit', 'land/LandBoundaryAssertion'):
        assert 'spatial_geometry' in result['concept_schemas'][kind]['properties'], kind
    for retired in ('parcel_geometry', 'land_geometry', 'boundary_geometry'):
        assert retired not in properties
    claims = [r for r in records if r['@type'] == 'land/LandTenureAssertion']
    units = {r['@id'] for r in records if r['@type'] == 'land/LandAdministrativeUnit'}
    assert claims and all(claim['tenure_object'] in units for claim in claims)
    validator = jsonschema.Draft202012Validator(result['concept_schemas']['land/LandTenureAssertion'], registry=registry)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({'tenure_category': 'ownership'})
    changed = copy.deepcopy(records)
    next(r for r in changed if r['@type'] == 'land/LandTenureAssertion')['tenure_object'] = 'https://example.org/parcel/one'
    assert not validate(graph(changed, result['context']), shacl_graph=shapes, inference='rdfs')[0]


def test_a_parcel_link_states_tenure_and_use_and_a_parcel_names_its_land_units(exports):
    result, shapes, records, _ = exports
    properties = result['properties']
    link = result['concept_schemas']['agri/HoldingParcelLink']['properties']
    assert {'parcel_tenure', 'parcel_land_use'} <= link.keys()
    # A farm can own one parcel and rent another, so the arrangement is stated per link.
    assert (properties['parcel_tenure']['vocabulary'], properties['parcel_tenure']['cardinality']) == ('agri/land-tenure', 'single')
    assert properties['parcel_tenure']['sensitivity'] == 'sensitive'
    assert (properties['parcel_land_use']['type'], properties['parcel_land_use']['cardinality']) == ('concept:CodedValue', 'single')
    assert 'one link per part' in properties['parcel_land_use']['definition']['en']
    assert 'land_spatial_units' in result['concept_schemas']['agri/AgriculturalParcel']['properties']
    assert properties['land_spatial_units']['type'] == 'concept:land/LandSpatialUnit'
    assert 'not make the agricultural parcel a title unit' in properties['land_spatial_units']['definition']['en']
    parcel = next(r for r in records if r['@id'] == 'https://example.org/parcel/one')
    assert parcel['land_spatial_units'] == ['https://example.org/land/unit']
    used = next(r for r in records if r['@id'] == 'https://example.org/holding-parcel/one')
    assert used['parcel_tenure'] == 'rented'
    changed = copy.deepcopy(records)
    next(r for r in changed if r['@id'] == 'https://example.org/parcel/one')['land_spatial_units'] = ['https://example.org/holding/one']
    assert not validate(graph(changed, result['context']), shacl_graph=shapes, inference='rdfs')[0]


def test_a_split_parcel_is_a_new_parcel_that_names_its_predecessor(exports):
    result, shapes, records, _ = exports
    properties = result['properties']
    assert 'predecessor_parcels' in result['concept_schemas']['agri/AgriculturalParcel']['properties']
    assert (properties['predecessor_parcels']['type'], properties['predecessor_parcels']['cardinality']) == ('concept:agri/AgriculturalParcel', 'multiple')
    rule = result['concepts']['agri/AgriculturalParcel']['definition']['en']
    assert 'split or merge creates a new parcel' in rule
    assert 'corrected measurement' in rule
    parcels = {r['@id']: r for r in records if r['@type'] == 'agri/AgriculturalParcel'}
    successor = parcels['https://example.org/parcel/two-north']
    assert successor['predecessor_parcels'] == ['https://example.org/parcel/two']
    # The predecessor keeps its identity and closes its validity before the successor starts.
    assert parcels['https://example.org/parcel/two']['valid_to'] < successor['valid_from']
    changed = copy.deepcopy(records)
    next(r for r in changed if r['@id'] == 'https://example.org/parcel/two-north')['predecessor_parcels'] = ['https://example.org/land/unit']
    assert not validate(graph(changed, result['context']), shacl_graph=shapes, inference='rdfs')[0]


def test_a_holding_uses_a_facility_through_a_dated_link(exports):
    result, shapes, records, _ = exports
    link = result['concept_schemas']['agri/HoldingFacilityLink']['properties']
    assert {'linked_holding', 'linked_facility', 'start_date', 'end_date', 'evidence_assertions'} <= link.keys()
    assert result['properties']['linked_facility']['type'] == 'concept:agri/AgriculturalFacility'
    definition = result['concepts']['agri/HoldingFacilityLink']['definition']['en']
    assert 'does not by itself assert ownership or operation' in definition
    used = next(r for r in records if r['@type'] == 'agri/HoldingFacilityLink')
    assert (used['linked_holding'], used['linked_facility']) == ('https://example.org/holding/one', 'https://example.org/facility/barn')
    changed = copy.deepcopy(records)
    next(r for r in changed if r['@type'] == 'agri/HoldingFacilityLink')['linked_facility'] = 'https://example.org/parcel/one'
    assert not validate(graph(changed, result['context']), shacl_graph=shapes, inference='rdfs')[0]


def test_asset_actor_kind_is_a_local_profile_rule(exports):
    result, shapes, records, _ = exports
    changed = copy.deepcopy(records)
    assignment = next(r for r in changed if r['@type']=='AssetPartyRole')
    changed.append({'@id': 'https://example.org/group/one', '@type': 'InformalGroup'})
    assignment['asset_actor'] = 'https://example.org/group/one'
    # Shared SHACL permits URI-shaped actors; the locally resolved profile owns
    # this pilot's narrower Person/Organization rule.
    assert validate(graph(changed,result['context']),shacl_graph=shapes,inference='rdfs')[0]
    types = {name: concept['uri'] for name, concept in result['concepts'].items()}
    subjects = profile.subject_index(changed, types)
    with pytest.raises(ValueError, match='wrong asset actor kind'):
        profile.validate_asset_party_role(assignment, subjects)


def test_qualified_reference_resolves_without_collapsing_local_ids():
    entries = {('https://example.org/register/a','001'):{'subject_uri':'https://example.org/one','subject_type':str(PS.Person)},('https://example.org/register/b','001'):{'subject_uri':'https://example.org/two','subject_type':str(PS.Organization)}}
    subjects = {'https://example.org/one':{'@type':str(PS.Person)},'https://example.org/two':{'@type':str(PS.Organization)}}
    a = {'register_uri':'https://example.org/register/a','record_id':'001','subject_type':str(PS.Person)}
    b = {'register_uri':'https://example.org/register/b','record_id':'001','subject_type':str(PS.Organization)}
    assert profile.resolve_reference(a,entries,subjects)['subject_uri'] != profile.resolve_reference(b,entries,subjects)['subject_uri']
    assert profile.resolve_reference({**a,'register_uri':'https://unavailable.example/register'},entries,subjects)['state']=='missing-record'
    assert profile.resolve_reference(a,entries,{})['state']=='missing-subject'
    for bad in ({**a,'subject_type':str(PS.Organization)},{**a,'subject_uri':'https://example.org/two'}):
        with pytest.raises(ValueError):
            profile.resolve_reference(bad,entries,subjects)
    with pytest.raises(ValueError):
        profile.resolve_reference(a,entries,{'https://example.org/one':{'@type':str(PS.Organization)}})


def test_submission_requiredness_and_late_recording():
    entry = {'register_uri':'https://example.org/r','record_id':'001','subject_uri':'https://example.org/s','subject_type':str(AGRI.Farm),'recorded_at':'2026-09-07T00:00:00Z','valid_from':'2026-01-01','valid_to':'2026-12-31'}
    profile.validate_entry(entry)
    with pytest.raises(KeyError):
        profile.validate_entry({})
    with pytest.raises(ValueError):
        profile.validate_period({'valid_from':'2026-03-01','valid_to':'2026-02-01'})
    profile.validate_period({'valid_from':'2026-03-01'})
    with pytest.raises(ValueError):
        profile.validate_entry({**entry,'recorded_at':'2026-09-07T00:00:00'})


def test_validity_is_inclusive_and_uses_exact_calendar_days():
    # valid_to is the last valid day, so a one-day validity is allowed.
    profile.validate_period({'valid_from': '2026-03-01', 'valid_to': '2026-03-01'})
    for value in ('20260301', 20260301, '2026-02-30'):
        with pytest.raises(ValueError, match='valid_from'):
            profile.validate_period({'valid_from': value})


def test_area_conversion_preserves_precision_and_rejects_wrong_dimension():
    quantity={'quantity_value':Decimal('12500.25'),'unit_code':'m2','unit_scheme':profile.UCUM}
    assert profile.area_hectares(quantity)==Decimal('1.250025')
    assert profile.area_hectares({**quantity,'quantity_value':Decimal('1.250025'),'unit_code':'har'})==Decimal('1.250025')
    for change in ({'unit_code':'kg'},{'quantity_value':-1},{'quantity_value':'NaN'},{'unit_scheme':'https://example.org/local'},{'unit_scheme':'http://unitsofmeasure.org'}):
        with pytest.raises(ValueError):
            profile.area_hectares({**quantity,**change})


def test_geometry_encoding_crs_and_coordinate_order():
    value={'geometry_encoding':'geojson','coordinate_reference_system':profile.CRS84,'geometry_literal':'{"type":"Point","coordinates":[100,13]}'}
    assert profile.validate_geometry(value)['coordinates']==[100,13]
    for literal in ('{"type":"Point","coordinates":[13,100]}','{"type":"LineString","coordinates":[[100,13],[101,14]]}','{"type":"Polygon","coordinates":[[[100,13],[101,13],[101,14]]]}'):
        with pytest.raises(ValueError):
            profile.validate_geometry({**value,'geometry_literal':literal})
    with pytest.raises(ValueError):
        profile.validate_geometry({**value,'coordinate_reference_system':'http://www.opengis.net/def/crs/EPSG/0/4326'})
    with pytest.raises(ValueError):
        profile.validate_geometry({**value,'geometry_encoding':'wkt'})
    profile.validate_geometry({**value,'geometry_literal':'{"type":"Polygon","coordinates":[[[100,13],[101,13],[101,14],[100,13]]]}'} )


def test_a_scheme_and_code_without_a_mapped_meaning_is_a_valid_coded_value(exports):
    result, _, _, registry=exports
    schema=result['concept_schemas']['CodedValue']
    for code in ('known','local-only','unknown','retired'):
        payload={'code_scheme':'https://example.org/v1/codes','code_value':code}
        jsonschema.Draft202012Validator(schema,registry=registry).validate(payload)


def test_reference_resolution_of_the_actual_pilot_records(exports):
    result, _, records, _ = exports
    types = {k: v['uri'] for k, v in result['concepts'].items()}
    subjects = profile.subject_index(records, types)
    entry = next(r for r in records if r['@type'] == 'RegistryEntry')
    profile.validate_entry(entry)
    reference = {k: entry[k] for k in ('register_uri', 'record_id', 'subject_uri', 'subject_type')}
    resolved = profile.resolve_reference(reference, {(entry['register_uri'], entry['record_id']): entry}, subjects)
    assert resolved['state'] == 'resolved'
    assert resolved['subject']['@type'] == str(HEALTH.HealthFacility)
    assert resolved['subject_uri'] != entry['@id']


def test_licence_number_and_record_key_preserve_separate_identities(exports):
    result, _, records, _ = exports
    types = {name: concept['uri'] for name, concept in result['concepts'].items()}
    subjects = profile.subject_index(records, types)
    assignment = next(record for record in records if record['@type'] == 'IdentifierAssignment')
    entry = next(record for record in records if record.get('subject_type') == str(PS.Authorization))
    reference = {
        key: entry[key]
        for key in ('register_uri', 'record_id', 'subject_uri', 'subject_type')
    }
    entries = {(entry['register_uri'], entry['record_id']): entry}
    resolved = profile.resolve_reference(reference, entries, subjects)
    assert resolved['state'] == 'resolved'
    assert resolved['subject_uri'] == assignment['subject_uri']
    assert assignment['assigned_identifier']['identifier_value'] != entry['record_id']
    assert len({entry['@id'], resolved['subject_uri'], resolved['subject']['registered_subject']}) == 3
    wrong_key = {**reference, 'record_id': assignment['assigned_identifier']['identifier_value']}
    assert profile.resolve_reference(wrong_key, entries, subjects)['state'] == 'missing-record'


def test_area_conversion_does_not_round_long_decimal_coefficients():
    value = Decimal('12345678901234567890123456789.123456789')
    assert profile.area_hectares({'quantity_value': value, 'unit_code': 'har', 'unit_scheme':profile.UCUM}) == value
    expected = Decimal('1234567890123456789012345.6789123456789')
    assert profile.area_hectares({'quantity_value': value, 'unit_code': 'm2', 'unit_scheme':profile.UCUM}) == expected


def test_every_authored_shared_class_and_field_survives_exports(exports):
    import yaml
    from rdflib.namespace import SH
    result, shapes, _, _ = exports
    context = result['context']['@context']
    for module in ('value_types', 'registry', 'work', 'land', 'agriculture_holdings', 'animals', 'plants'):
        authored = yaml.safe_load((ROOT / f'schema/{module}.yaml').read_text())
        for name, definition in authored.get('classes', {}).items():
            value = context[name]
            class_uri = value['@id'] if isinstance(value, dict) else value
            class_key = class_uri.removeprefix(str(PS))
            assert class_key in result['concepts']
            assert result['concepts'][class_key]['maturity'] == 'draft'
            assert result['concepts'][class_key]['bibliography_refs'], name
            assert set(definition.get('slots', [])) <= result['concept_schemas'][class_key]['properties'].keys()
        for name in authored.get('slots', {}):
            assert name in result['properties']
            value = context[name]
            property_uri = value['@id'] if isinstance(value, dict) else value
            assert list(shapes.subjects(SH.path, URIRef(property_uri))), name
