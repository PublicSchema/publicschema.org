"""Validate the bounded, locally resolved facility estate example exchange.

This is an example submission profile; the vocabulary itself accepts any URI.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from profile_support import absolute_uri, check_period, parse_day  # noqa: E402

ROLE_SCHEME = "https://publicschema.org/vocab/asset-role-type"
ROLE_TYPES = {"owner", "operator", "upkeep"}
ADDRESS_PURPOSE_SCHEME = "https://publicschema.org/vocab/address-purpose"
ADDRESS_PURPOSES = {"physical", "postal"}
AGRICULTURAL_FACILITIES = {"AgriculturalFacility", "AgriculturalLaboratory"}
FACILITY_TYPES = {"School", "HealthFacility"} | AGRICULTURAL_FACILITIES
ACTOR_TYPES = {
    "Person", "Organization", "PublicOrganization",
    "EducationProvider", "ProducerOrganization",
}
GROUP_TYPES = {"InformalGroup", "Household", "Family"}


def period(record):
    """Return known bounds; end_date is the first inactive calendar day here."""
    if "valid_from" in record or "valid_to" in record:
        raise ValueError("period: use start_date/end_date; legacy validity cannot be renamed without review")
    start, end = (parse_day(record[field], field) if field in record else None
                  for field in ("start_date", "end_date"))
    check_period(start, end, exclusive=True,
                 message="end_date: an assignment must contain at least one effective calendar day")
    return start, end


def effective_on(record, day):
    """Return True, False or None (unknown), without turning missing dates into infinity."""
    if type(day) is not date:
        raise ValueError("day: expected a calendar date")
    start, end = period(record)
    if start and day < start or end and day >= end:
        return False
    if start is None or end is None:
        return None
    return True


def validate_profile(records):
    """Check explicit roles and locally resolved actor/facility kinds.

    Only the listed concrete types are accepted. The profile does not fetch URIs,
    infer an actor's other roles or prohibit simultaneous responsibilities.
    """
    if not isinstance(records, list):
        raise ValueError("records: expected a list of identified records")
    index = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("record: expected an object")
        identifier = record.get("@id")
        if not absolute_uri(identifier):
            raise ValueError("@id: expected an absolute subject URI")
        if identifier in index:
            raise ValueError("@id: duplicate subject URI; reconcile the records before validation")
        index[identifier] = record

    def typed_uri(record, field, accepted):
        value = record.get(field)
        if not absolute_uri(value):
            raise ValueError(f"{field}: expected an absolute subject URI")
        if value not in index:
            raise ValueError(f"{field}: unresolved local subject URI")
        if index[value].get("@type") not in accepted:
            raise ValueError(f"{field}: unsupported resolved subject type")
        return index[value]

    for record in records:
        kind = record.get("@type")
        if kind == "AssetAddressAssignment":
            typed_uri(record, "subject_uri", FACILITY_TYPES)
            typed_uri(record, "assigned_address", {"Address"})
            purpose = record.get("address_purpose")
            if not isinstance(purpose, dict) or purpose.get("@type") != "CodedValue":
                raise ValueError("address_purpose: expected a CodedValue")
            if purpose.get("code_scheme") != ADDRESS_PURPOSE_SCHEME:
                raise ValueError("address_purpose.code_scheme: expected the example's declared address purpose scheme")
            if purpose.get("code_value") not in ADDRESS_PURPOSES:
                raise ValueError("address_purpose.code_value: expected physical or postal")
            period(record)
        if kind != "AssetPartyRole":
            continue
        typed_uri(record, "subject_uri", FACILITY_TYPES)
        typed_uri(record, "asset_actor", ACTOR_TYPES | GROUP_TYPES)
        role = record.get("asset_role_type")
        if not isinstance(role, dict) or role.get("@type") != "CodedValue":
            raise ValueError("asset_role_type: expected a CodedValue")
        if role.get("code_scheme") != ROLE_SCHEME:
            raise ValueError("asset_role_type.code_scheme: expected the example's declared role scheme")
        if role.get("code_value") not in ROLE_TYPES:
            raise ValueError("asset_role_type.code_value: expected owner, operator or upkeep")
        period(record)


if __name__ == "__main__":
    validate_profile(json.loads(Path(__file__).with_name("records.json").read_text()))
    print("Facility estate example profile: passed")
