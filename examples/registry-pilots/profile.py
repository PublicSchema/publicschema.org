"""Local illustrative submission rules, not a PublicSchema runtime or compiler.

This example never fetches a record or context. The caller supplies a reviewed
local record index and decides whether an unresolved reference is acceptable.
"""
import json
from datetime import date, datetime
from decimal import Decimal, localcontext
from urllib.parse import urlparse

UCUM = 'http://unitsofmeasure.org'
CRS84 = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'


def absolute_uri(value):
    if not isinstance(value, str) or not urlparse(value).scheme:
        raise ValueError('expected an absolute URI')
    return value


def subject_index(records, type_uris):
    """Normalize compact native types using the caller's built local catalog.

    The pilot uses one concrete type per subject. No remote context is loaded.
    """
    index = {}
    for record in records:
        subject = absolute_uri(record["@id"])
        if subject in index:
            raise ValueError("duplicate subject identity")
        type_name = record["@type"]
        type_uri = type_uris.get(type_name, type_name)
        absolute_uri(type_uri)
        index[subject] = {**record, "@type": type_uri}
    return index


def resolve_reference(reference, records, subjects):
    """Return resolved/missing-record/missing-subject without network access.

    Type mismatches and conflicting explicit subject identities are errors.
    Keys are tuples, never concatenated strings or unqualified local IDs.
    """
    key = (absolute_uri(reference['register_uri']), reference['record_id'])
    if not isinstance(key[1], str) or not key[1]:
        raise ValueError('record_id must be a nonempty string')
    if key not in records:
        return {'state': 'missing-record', 'reference': dict(reference)}
    record = records[key]
    subject = absolute_uri(record['subject_uri'])
    if reference.get('subject_uri', subject) != subject:
        raise ValueError('record and reference disagree on subject identity')
    expected = reference.get('subject_type')
    if expected and record.get('subject_type') != expected:
        raise ValueError('record and reference disagree on subject type')
    if subject not in subjects:
        return {'state': 'missing-subject', 'reference': dict(reference), 'subject_uri': subject}
    actual = subjects[subject]['@type']
    declared = record.get('subject_type')
    if declared and declared != actual:
        raise ValueError('resolved subject has wrong type')
    return {'state': 'resolved', 'subject_uri': subject, 'subject': subjects[subject]}


def validate_entry(entry):
    for key in ('register_uri', 'subject_uri', 'subject_type'):
        absolute_uri(entry[key])
    if not isinstance(entry['record_id'], str) or not entry['record_id']:
        raise ValueError('record_id must be a nonempty string')
    timestamp = datetime.fromisoformat(entry['recorded_at'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        raise ValueError('recorded_at requires a timezone')
    validate_period(entry)


def validate_period(record):
    start = date.fromisoformat(record['valid_from']) if 'valid_from' in record else None
    end = date.fromisoformat(record['valid_to']) if 'valid_to' in record else None
    if start is not None and end is not None and start > end:
        raise ValueError('valid_from must not follow valid_to')


def validate_asset_party_role(record, subjects):
    """Apply this pilot's concrete actor-kind rule to an asset role assertion.

    The shared vocabulary deliberately accepts URI references. This profile
    resolves local identities and permits only a Person or Organization actor.
    """
    actor = absolute_uri(record['asset_actor'])
    if actor not in subjects:
        raise ValueError('unresolved asset actor')
    if subjects[actor]['@type'] not in {
        'https://publicschema.org/Person', 'https://publicschema.org/Organization',
    }:
        raise ValueError('wrong asset actor kind')


def area_hectares(quantity):
    """Exact decimal conversion for this example's two supported UCUM units."""
    if quantity.get('unit_scheme') != UCUM:
        raise ValueError('unsupported unit scheme')
    factors = {'har': Decimal(1), 'm2': Decimal('0.0001')}
    if quantity.get('unit_code') not in factors:
        raise ValueError('expected supported area unit har or m2')
    number = Decimal(str(quantity['quantity_value']))
    if not number.is_finite() or number < 0:
        raise ValueError('area must be finite and nonnegative')
    with localcontext() as context:
        context.prec = max(28, len(number.as_tuple().digits) + 4)
        return number * factors[quantity['unit_code']]


def validate_geometry(value):
    """This pilot supports 2D RFC 7946 Point/Polygon, not topology validation."""
    if value.get('geometry_encoding') != 'application/geo+json' or value.get('coordinate_reference_system') != CRS84:
        raise ValueError('expected GeoJSON in longitude/latitude CRS84')
    geometry = json.loads(value['geometry_literal'])
    if set(geometry) != {'type', 'coordinates'}:
        raise ValueError('pilot geometry accepts only type and coordinates')
    def position(point):
        if not isinstance(point, list) or len(point) != 2 or any(type(x) not in (int, float) for x in point):
            raise ValueError('expected two numerical coordinates')
        if not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
            raise ValueError('coordinate outside longitude/latitude bounds')
    if geometry['type'] == 'Point':
        position(geometry['coordinates'])
    elif geometry['type'] == 'Polygon':
        rings = geometry['coordinates']
        if not isinstance(rings, list) or not rings:
            raise ValueError('polygon requires rings')
        for ring in rings:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError('polygon rings must close and contain at least four positions')
            for point in ring:
                position(point)
    else:
        raise ValueError('unsupported pilot geometry type')
    return geometry
