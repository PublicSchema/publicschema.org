"""Illustrative movement-submission rules beyond the optional reference vocabulary.

Run: uv run --locked python examples/agriculture-biology/validate_movement_profile.py
This small example accepts flat local records, compact concrete types and URI
references. It does not fetch records, validate a complete traceability programme,
calculate inventories or derive residence and responsibility changes.
"""
import json
from pathlib import Path

import jsonschema

MOVEMENT_PROFILE = {
    "type": "object",
    "required": [
        "@id", "@type", "animal_movement_date", "moved_animal_count",
        "movement_origin_site", "movement_destination_site",
    ],
    "properties": {
        "@id": {"type": "string", "format": "uri"},
        "@type": {"const": "AnimalMovement"},
        "animal_movement_date": {"type": "string", "format": "date"},
        "recorded_at": {"type": "string", "format": "date-time"},
        "moved_animal_count": {"type": "integer", "minimum": 1},
        "moved_animals": {
            "type": "array", "uniqueItems": True,
            "items": {"type": "string", "format": "uri"},
        },
        "movement_source_group": {"type": "string", "format": "uri"},
        "movement_origin_site": {"type": "string", "format": "uri"},
        "movement_destination_site": {"type": "string", "format": "uri"},
        "movement_transit_sites": {
            "type": "array", "items": {"type": "string", "format": "uri"},
        },
    },
    "anyOf": [
        {"required": ["movement_source_group"]},
        {"required": ["moved_animals"], "properties": {"moved_animals": {"minItems": 1}}},
    ],
}


def validate_profile(records):
    """Validate movement submissions and resolve their references locally.

    JSON Schema exports should validate native record structure separately.
    This example requires AgriculturalFacility sites; other physical site types
    need an explicit profile extension. Dates have calendar precision only, so
    no timezone or chronology is inferred from their relation to recorded_at.
    """
    index = {}
    for record in records:
        if "@id" in record:
            if record["@id"] in index:
                raise ValueError("Duplicate local subject URI")
            index[record["@id"]] = record

    def typed_target(uri, accepted, field):
        if uri not in index:
            raise ValueError(f"{field}: unresolved local target")
        if index[uri].get("@type") not in accepted:
            raise ValueError(f"{field}: wrong resolved target type")

    validator = jsonschema.Draft202012Validator(
        MOVEMENT_PROFILE, format_checker=jsonschema.FormatChecker(),
    )
    for record in records:
        if record.get("@type") != "AnimalMovement":
            continue
        validator.validate(record)
        moved = record.get("moved_animals", [])
        if record["moved_animal_count"] < len(moved):
            raise ValueError("moved_animal_count: fewer animals than identified participants")
        for animal in moved:
            typed_target(animal, {"IndividualAnimal"}, "moved_animals")
        if "movement_source_group" in record:
            typed_target(record["movement_source_group"], {"AnimalGroup"}, "movement_source_group")
        for field in ("movement_origin_site", "movement_destination_site"):
            typed_target(record[field], {"agri/AgriculturalFacility"}, field)
        for site in record.get("movement_transit_sites", []):
            typed_target(site, {"agri/AgriculturalFacility"}, "movement_transit_sites")


if __name__ == "__main__":
    validate_profile(json.loads(Path(__file__).with_name("movement-records.json").read_text()))
    print("Animal movement example profile: passed")
