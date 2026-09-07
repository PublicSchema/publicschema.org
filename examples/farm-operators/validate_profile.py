"""Validate the closed, local Farm operator demonstration exchange.

Run: .venv/bin/python examples/farm-operators/validate_profile.py
This submission profile adds completeness and reference checks to the optional vocabulary.
"""
import json
from datetime import date
from pathlib import Path

ROLE_ENDPOINTS = {
    "PersonHoldingOperatorRole": ("holding_operator_person", {"Person"}),
    "OrganizationHoldingOperatorRole": ("holding_operator_organization", {"Organization"}),
    "GroupHoldingOperatorRole": ("holding_operator_group", {"Household", "Family", "InformalGroup"}),
}
ENDPOINTS = {pair[0] for pair in ROLE_ENDPOINTS.values()}


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
    validate_profile(json.loads(Path(__file__).with_name("records.json").read_text()))
    print("Farm operator example profile: passed")
