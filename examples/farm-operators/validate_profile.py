"""Validate the closed, local Farm holder demonstration exchange.

Run: uv run --locked python examples/farm-operators/validate_profile.py
This submission profile adds completeness and reference checks to the optional vocabulary.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from profile_support import absolute_uri, check_period, coded_value, parse_day  # noqa: E402

ROLE_ENDPOINTS = {
    "agri/PersonAgriculturalHolderRole": ("holder_person", {"Person"}),
    "agri/OrganizationAgriculturalHolderRole": ("holder_organization", {"Organization"}),
    "agri/GroupAgriculturalHolderRole": ("holder_group", {"Household", "Family", "InformalGroup"}),
}
ENDPOINTS = {pair[0] for pair in ROLE_ENDPOINTS.values()}
WORK_TYPES = {"WorkRelationship", "agri/HoldingWorkAssignment"}
ECONOMIC_UNIT_TYPES = {"Organization", "Household", "InformalGroup", "agri/Farm"}
WORK_CLASSIFICATIONS = {"work_status", "work_remuneration", "work_seasonality"}
# Fields that the vocabulary no longer defines on these types.
RETIRED_FIELDS = {
    "agri/Farm": {"holding_operator_roles", "primary_crop", "farm_area_hectares"},
    "WorkRelationship": {"work_functions"},
}



def validate_profile(records):
    """Raise ValueError on an incomplete or inconsistent locally resolved exchange.

    This deliberately supports the listed concrete subject types only. It never
    fetches remote references or infers beneficiary status. Unknown types require
    an explicit extension of this example profile.
    """
    index = {}
    objects = []

    def collect(value):
        if isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, dict):
            if "@type" in value:
                objects.append(value)
                if "@id" in value:
                    key = value["@id"]
                    # JSON-LD may embed a node where it is referenced as well as list it;
                    # only different content for one subject URI is a conflict.
                    if key in index and index[key] != value:
                        raise ValueError("Conflicting records for one subject URI")
                    index[key] = value
            for item in value.values():
                collect(item)

    collect(records)

    def resolve(value):
        if isinstance(value, dict) and "@type" in value:
            return value
        key = value.get("@id") if isinstance(value, dict) else value
        if not isinstance(key, str) or key not in index:
            raise ValueError("Unresolved local target")
        return index[key]

    def typed(value, accepted):
        target = resolve(value)
        if target.get("@type") not in accepted:
            raise ValueError("Wrong resolved target type")
        return target

    def same_subject(left, right):
        return left is right or bool(left.get("@id") and left["@id"] == right.get("@id"))

    def interval(record):
        start, end = (parse_day(record[field], field) if field in record else None
                      for field in ("start_date", "end_date"))
        # Whole-day example convention: start is inclusive; end is first inactive day.
        check_period(start, end, exclusive=True)
        return start, end

    def classification(value):
        coded_value(typed(value, {"CodedValue"}))

    for record in objects:
        if RETIRED_FIELDS.get(record["@type"], set()) & record.keys():
            raise ValueError("A retired field is present")
        if record["@type"] in WORK_TYPES:
            person = typed(record.get("work_person"), {"Person"})
            start, end = interval(record)
            for field in WORK_CLASSIFICATIONS:
                if field in record:
                    classification(record[field])
            if "work_functions" in record:
                if not isinstance(record["work_functions"], list):
                    raise ValueError("Work functions must be a list")
                for function in record["work_functions"]:
                    classification(function)
            if record["@type"] == "WorkRelationship":
                unit_uri = record.get("work_economic_unit")
                if not absolute_uri(unit_uri):
                    raise ValueError("The work economic unit requires a subject URI")
                typed(unit_uri, ECONOMIC_UNIT_TYPES)
            else:
                typed(record.get("assigned_holding"), {"agri/Farm"})
                if "assignment_work_relationship" in record:
                    relationship = typed(record["assignment_work_relationship"], {"WorkRelationship"})
                    related_person = typed(relationship.get("work_person"), {"Person"})
                    if not same_subject(person, related_person):
                        raise ValueError("Assignment and work relationship must identify the same person")
                    related_start, related_end = interval(relationship)
                    if (start and related_start and start < related_start
                            or end and related_end and end > related_end
                            or start and related_end and start >= related_end
                            or end and related_start and end <= related_start):
                        raise ValueError("Assignment lies outside the known work relationship interval")
        if record["@type"] == "GroupMembership":
            typed(record.get("person"), {"Person"})
            typed(record.get("group"), {"Household", "Family", "InformalGroup"})

    for record in objects:
        kind = record["@type"]
        if kind in {"AgriculturalHolderRole", "agri/AgriculturalHolderRole"}:
            raise ValueError("A concrete holder role type is required")
        if kind in ROLE_ENDPOINTS:
            endpoint, accepted = ROLE_ENDPOINTS[kind]
            if {key for key in ENDPOINTS if key in record} != {endpoint}:
                raise ValueError("Exactly the concrete type's holder endpoint is required")
            if resolve(record[endpoint]).get("@type") not in accepted:
                raise ValueError("Wrong holder target type")
            if resolve(record.get("holder_farm")).get("@type") != "agri/Farm":
                raise ValueError("The holder farm must resolve to a Farm")
            interval(record)


if __name__ == "__main__":
    for filename in ("records.json", "work-records.json"):
        validate_profile(json.loads(Path(__file__).with_name(filename).read_text()))
    print("Farm holder and work example profile: passed")
