"""Validate the closed, local Farm operator demonstration exchange.

Run: .venv/bin/python examples/farm-operators/validate_profile.py
This submission profile adds completeness and reference checks to the optional vocabulary.
"""
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROLE_ENDPOINTS = {
    "PersonHoldingOperatorRole": ("holding_operator_person", {"Person"}),
    "OrganizationHoldingOperatorRole": ("holding_operator_organization", {"Organization"}),
    "GroupHoldingOperatorRole": ("holding_operator_group", {"Household", "Family", "InformalGroup"}),
}
ENDPOINTS = {pair[0] for pair in ROLE_ENDPOINTS.values()}
WORK_TYPES = {"WorkRelationship", "HoldingWorkAssignment"}
ECONOMIC_UNIT_TYPES = {"Organization", "Household", "InformalGroup", "Farm"}
WORK_CLASSIFICATIONS = {"work_form", "work_status", "work_remuneration", "work_seasonality"}



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
        result = []
        for field in ("start_date", "end_date"):
            value = record.get(field)
            if field in record and not isinstance(value, str):
                raise ValueError("An effective date must be an ISO date string")
            result.append(date.fromisoformat(value) if value is not None else None)
        start, end = result
        # Whole-day example convention: start is inclusive; end is first inactive day.
        if start and end and end <= start:
            raise ValueError("Work interval must contain at least one effective day")
        return start, end

    def classification(value):
        code = typed(value, {"CodedValue"})
        scheme, text = code.get("code_scheme"), code.get("code_value")
        if not isinstance(scheme, str) or not urlsplit(scheme).scheme:
            raise ValueError("A supplied work classification requires an absolute scheme URI")
        if not isinstance(text, str) or not text:
            raise ValueError("A supplied work classification requires its original code")

    for record in objects:
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
                if not isinstance(unit_uri, str) or not urlsplit(unit_uri).scheme:
                    raise ValueError("The work economic unit requires a subject URI")
                typed(unit_uri, ECONOMIC_UNIT_TYPES)
            else:
                typed(record.get("assigned_holding"), {"Farm"})
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
        if kind == "HoldingOperatorRole":
            raise ValueError("A concrete holder responsibility type is required")
        if kind in ROLE_ENDPOINTS:
            endpoint, accepted = ROLE_ENDPOINTS[kind]
            if {key for key in ENDPOINTS if key in record} != {endpoint}:
                raise ValueError("Exactly the concrete type's operator endpoint is required")
            if resolve(record[endpoint]).get("@type") not in accepted:
                raise ValueError("Wrong operator target type")
            if resolve(record.get("operated_holding")).get("@type") != "Farm":
                raise ValueError("The operated holding must resolve to a Farm")
            start = date.fromisoformat(record["start_date"]) if "start_date" in record else None
            end = date.fromisoformat(record["end_date"]) if "end_date" in record else None
            if start and end and end < start:
                raise ValueError("Responsibility ends before it starts")
        if kind == "Farm":
            for value in record.get("holding_operator_roles", []):
                role = resolve(value)
                if role.get("@type") not in ROLE_ENDPOINTS:
                    raise ValueError("Listed role must use a supported concrete type")
                holding = resolve(role.get("operated_holding"))
                if holding is not record and (
                    not record.get("@id") or holding.get("@id") != record["@id"]
                ):
                    raise ValueError("Listed responsibility identifies a different Farm")


if __name__ == "__main__":
    for filename in ("records.json", "work-records.json"):
        validate_profile(json.loads(Path(__file__).with_name(filename).read_text()))
    print("Farm holder and work example profile: passed")
