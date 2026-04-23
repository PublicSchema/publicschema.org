"""
DHIS2 to entities.json + enums.json converter.

Uses two sources:
1. Metadata API (tracked-entity-types.json, programs.json, option-sets.json):
   For domain-level entities like Person, where fields are runtime-configured
   TrackedEntityAttributes. Produces a Person entity with real domain fields
   (first name, gender, date of birth) instead of API envelope plumbing.
2. OpenAPI spec (openapi.json): For structural entities with fixed schemas
   (Program, ProgramStage, OrganisationUnit, etc.).

Run from the repo root:
    uv run python external/dhis2/convert.py               # convert only
    uv run python external/dhis2/convert.py --fetch       # fetch then convert
    uv run python external/dhis2/convert.py --fetch --version stable-2-42-4
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_DIR = Path(__file__).resolve().parent
_EXTRACTED = _DIR / "extracted"
_OPENAPI_PATH = _EXTRACTED / "openapi.json"
_TRACKED_ENTITY_TYPES_PATH = _EXTRACTED / "tracked-entity-types.json"
_PROGRAMS_PATH = _EXTRACTED / "programs.json"
_OPTION_SETS_PATH = _EXTRACTED / "option-sets.json"
_ENTITIES_OUT = _EXTRACTED / "entities.json"
_ENUMS_OUT = _EXTRACTED / "enums.json"

# ---------------------------------------------------------------------------
# Fetch configuration
# ---------------------------------------------------------------------------

_DEFAULT_VERSION = "stable-2-42-4"
_PLAY_HOST = "https://play.im.dhis2.org"
_DEMO_USER = "admin"
_DEMO_PASS = "district"

_METADATA_ENDPOINTS: dict[str, str] = {
    "tracked-entity-types.json": (
        "/api/trackedEntityTypes.json?fields="
        "id,name,trackedEntityTypeAttributes%5B"
        "trackedEntityAttribute%5Bid,name,shortName,valueType,unique,description,"
        "optionSet%5Bid,name%5D%5D%5D"
        "&paging=false"
    ),
    "programs.json": (
        "/api/programs.json?fields="
        "id,name,trackedEntityType%5Bid,name%5D,"
        "programTrackedEntityAttributes%5B"
        "trackedEntityAttribute%5Bid,name,shortName,valueType,unique,description,"
        "optionSet%5Bid,name%5D%5D%5D"
        "&paging=false"
    ),
    "option-sets.json": (
        "/api/optionSets.json?fields="
        "id,name,options%5Bid,code,name%5D"
        "&paging=false"
    ),
}

# ---------------------------------------------------------------------------
# OpenAPI schema extraction config
# ---------------------------------------------------------------------------

_ENTITY_ALLOWLIST: list[str] = [
    # Tracker data model (the operational/transactional layer)
    "TrackerEnrollment",
    "TrackerEvent",
    "TrackerRelationship",
    "TrackerRelationshipItem",
    "TrackerDataValue",
    "TrackerNote",
    "TrackerUser",
    "TrackerProgramOwner",
    # Metadata (configuration/definition layer)
    "Program",
    "ProgramStage",
    "TrackedEntityType",
    "TrackedEntityAttribute",
    "OrganisationUnit",
    "RelationshipType",
    "RelationshipConstraint",
    "DataElement",
]

_ENUM_ALLOWLIST: list[str] = [
    "EnrollmentStatus",
    "EventStatus",
    "ValueType",
    "FeatureType",
    "AccessLevel",
    "RelationshipEntity",
    "ProgramType",
]

_SKIP_PROPERTIES: set[str] = {
    # Audit/timestamps
    "created",
    "createdAt",
    "createdAtClient",
    "createdBy",
    "lastUpdated",
    "lastUpdatedBy",
    "updatedAt",
    "updatedAtClient",
    "updatedBy",
    # Display variants (derived from name/description)
    "displayName",
    "displayDescription",
    "displayFormName",
    "displayShortName",
    "displayFromToName",
    "displayToFromName",
    "displayDueDateLabel",
    "displayEventLabel",
    "displayExecutionDateLabel",
    "displayGenerateEventBox",
    "displayProgramStageLabel",
    # Access, sharing, i18n
    "access",
    "sharing",
    "translations",
    "attributeValues",
    # DHIS2 internals
    "href",
    "favorite",
    "favorites",
    "dimensionItem",
    "queryMods",
    "formName",
    # Soft-delete flag
    "deleted",
    # Audit user
    "storedBy",
}

_DESCRIPTIONS: dict[str, str] = {
    "TrackerEnrollment": (
        "The registration of a tracked entity into a specific program, "
        "with enrollment dates, status, and associated events."
    ),
    "TrackerEvent": (
        "A single data-collection occurrence within a program stage, "
        "carrying data values, dates, and assignment."
    ),
    "TrackerRelationship": (
        "A typed, optionally bidirectional link between two tracker items "
        "(tracked entities, enrollments, or events)."
    ),
    "TrackerRelationshipItem": (
        "One side of a tracker relationship, referencing either a "
        "tracked entity, enrollment, or event."
    ),
    "TrackerDataValue": (
        "A single data value recorded for a data element within an event."
    ),
    "TrackerNote": (
        "A timestamped text note attached to an enrollment or event."
    ),
    "TrackerUser": (
        "A lightweight user reference carrying UID, username, and display name."
    ),
    "TrackerProgramOwner": (
        "Links a tracked entity to the organisation unit that owns it "
        "within a given program."
    ),
    "Program": (
        "A program definition that configures how tracked entities are "
        "enrolled, what data is collected, and access rules."
    ),
    "ProgramStage": (
        "A stage within a program that defines a repeatable or one-time "
        "data collection step with its own data elements."
    ),
    "TrackedEntityType": (
        "A type definition for tracked entities (e.g. Person, Commodity), "
        "specifying which attributes apply and search rules."
    ),
    "TrackedEntityAttribute": (
        "A metadata definition for an attribute that can be attached to "
        "tracked entities, with value type, uniqueness, and display rules."
    ),
    "OrganisationUnit": (
        "A node in the organisational hierarchy (country, region, district, "
        "facility) that owns data and tracked entities."
    ),
    "RelationshipType": (
        "Defines a type of relationship between tracker items, with "
        "directional names and constraints on what can be linked."
    ),
    "RelationshipConstraint": (
        "Constrains one side of a relationship type to a specific entity "
        "type, program, or program stage."
    ),
    "DataElement": (
        "A metadata definition for a single data point (question/indicator) "
        "with value type, aggregation rules, and categorization."
    ),
}

# ---------------------------------------------------------------------------
# Metadata-based entity extraction configuration
# ---------------------------------------------------------------------------

# TrackedEntityTypes to extract as domain-level entities.
_METADATA_ENTITY_ALLOWLIST: set[str] = {"Person"}

# DHIS2 ValueType to standardized type mapping
_VALUETYPE_MAP: dict[str, str] = {
    "TEXT": "string",
    "LONG_TEXT": "string",
    "NUMBER": "number",
    "INTEGER": "integer",
    "INTEGER_POSITIVE": "integer",
    "INTEGER_NEGATIVE": "integer",
    "INTEGER_ZERO_OR_POSITIVE": "integer",
    "BOOLEAN": "boolean",
    "TRUE_ONLY": "boolean",
    "DATE": "date",
    "AGE": "date",
    "DATETIME": "dateTime",
    "PHONE_NUMBER": "string",
    "EMAIL": "string",
    "USERNAME": "string",
    "URL": "string",
    "COORDINATE": "string",
    "MULTI_TEXT": "string",
}

# Attributes to exclude even if they pass the frequency filter.
_ATTR_SKIP_LIST: set[str] = {
    "Username",
    "Weight in kg",
    "Height in cm",
}

# Attributes to include even if they appear in only one program.
_ATTR_INCLUDE_LIST: set[str] = {
    "Date of birth",
    "National identifier",
    "Mobile number",
    "Civil status",
}


def _resolve_valuetype(value_type: str) -> str:
    """Map a DHIS2 ValueType to a standardized type string."""
    return _VALUETYPE_MAP.get(value_type, "string")


def _collect_person_attributes(
    tracked_entity_type: dict,
    programs: list[dict],
) -> list[dict]:
    """
    Collect and filter attributes for a TrackedEntityType.

    Includes an attribute if it is defined on the type itself, appears
    in 2+ programs that use this type, or is on the manual include list.
    Deduplicates by attribute ID. Excludes attributes on the skip list.
    """
    type_id = tracked_entity_type["id"]

    # 1. Base attributes defined on the type itself (always included)
    base_attr_ids: set[str] = set()
    attrs_by_id: dict[str, dict] = {}
    for wrapper in tracked_entity_type.get("trackedEntityTypeAttributes", []):
        attr = wrapper["trackedEntityAttribute"]
        base_attr_ids.add(attr["id"])
        attrs_by_id[attr["id"]] = attr

    # 2. Count attribute appearances across programs using this type
    program_count: Counter = Counter()
    for program in programs:
        tet = program.get("trackedEntityType", {})
        if tet.get("id") != type_id:
            continue
        for wrapper in program.get("programTrackedEntityAttributes", []):
            attr = wrapper["trackedEntityAttribute"]
            program_count[attr["id"]] += 1
            # Keep the richest version of the attribute metadata
            if attr["id"] not in attrs_by_id:
                attrs_by_id[attr["id"]] = attr

    # 3. Filter: include if on the type itself, in 2+ programs, or on
    #    the manual include list (domain-relevant but only in 1 program)
    result: list[dict] = []
    seen: set[str] = set()
    for attr_id, attr in attrs_by_id.items():
        if attr_id in seen:
            continue
        if attr["name"] in _ATTR_SKIP_LIST:
            continue
        included = (
            attr_id in base_attr_ids
            or program_count[attr_id] >= 2
            or attr["name"] in _ATTR_INCLUDE_LIST
        )
        if included:
            result.append(attr)
            seen.add(attr_id)

    return result


def _build_option_set_enums(
    option_sets_data: dict,
    attrs_with_option_sets: list[dict],
) -> dict[str, dict]:
    """
    Build enum definitions from option sets referenced by the given attributes.

    Only includes option sets actually referenced by the filtered attributes,
    not all option sets in the system.
    """
    # Index option sets by ID
    os_by_id: dict[str, dict] = {}
    for os in option_sets_data.get("optionSets", []):
        os_by_id[os["id"]] = os

    # Collect referenced option set IDs
    referenced_ids: set[str] = set()
    for attr in attrs_with_option_sets:
        os_ref = attr.get("optionSet")
        if os_ref:
            referenced_ids.add(os_ref["id"])

    enums: dict[str, dict] = {}
    for os_id in referenced_ids:
        os_data = os_by_id.get(os_id)
        if os_data is None:
            continue
        name = os_data["name"]
        values = []
        for opt in os_data.get("options", []):
            values.append({
                "code": opt.get("code", opt.get("name", "")),
                "label": opt.get("name", opt.get("code", "")),
                "description": "",
            })
        enums[name] = {
            "description": f"Allowed values for {name} in DHIS2.",
            "values": values,
        }

    return enums


def _build_metadata_entity(
    type_name: str,
    attributes: list[dict],
    option_set_enums: dict[str, dict],
) -> dict:
    """
    Build a domain-level entity from collected TrackedEntityAttributes.

    Each attribute becomes a field with type derived from its ValueType
    (or enum name if it has an optionSet).
    """
    fields: list[dict] = []
    for attr in attributes:
        option_set = attr.get("optionSet")
        if option_set and option_set["name"] in option_set_enums:
            field_type = option_set["name"]
        else:
            field_type = _resolve_valuetype(attr.get("valueType", "TEXT"))

        field: dict = {
            "name": attr["name"],
            "type": field_type,
            "required": False,
            "cardinality": "0..1",
            "description": attr.get("description", ""),
        }
        if option_set and option_set["name"] in option_set_enums:
            field["enum"] = option_set["name"]

        fields.append(field)

    return {
        "id": type_name,
        "name": type_name,
        "description": (
            f"A person tracked across programs. In DHIS2, {type_name} is a "
            f"TrackedEntityType whose fields are configurable attributes. "
            f"The fields shown here are the defaults from the DHIS2 demo instance."
        ),
        "parent": None,
        "source_url": "https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-master/tracker.html",
        "fields": fields,
    }


# ---------------------------------------------------------------------------
# OpenAPI helpers
# ---------------------------------------------------------------------------


def _ref_name(ref: str) -> str:
    """Extract the schema name from a $ref string like '#/components/schemas/Foo'."""
    return ref.rsplit("/", 1)[-1]


def _resolve_type(prop_schema: dict) -> tuple[str, bool]:
    """
    Resolve an OpenAPI property schema to (type_name, is_array).

    Handles primitives, $ref, arrays, UID_* refs (shortened to "string (UID)"),
    and Instant (mapped to dateTime).
    """
    if "$ref" in prop_schema:
        name = _ref_name(prop_schema["$ref"])
        if name.startswith("UID_"):
            return ("string (UID)", False)
        if name == "Instant":
            return ("dateTime", False)
        return (name, False)

    prop_type = prop_schema.get("type", "unknown")

    if prop_type == "array":
        items = prop_schema.get("items", {})
        if "$ref" in items:
            item_name = _ref_name(items["$ref"])
            if item_name.startswith("UID_"):
                return ("string (UID)", True)
            if item_name == "Instant":
                return ("dateTime", True)
            return (item_name, True)
        return (items.get("type", "unknown"), True)

    if prop_type == "integer":
        return ("integer", False)
    if prop_type == "number":
        return ("number", False)

    return (prop_type, False)


def _is_inline_object(prop_schema: dict) -> bool:
    """Check if a property schema is an inline object (not a $ref)."""
    if prop_schema.get("type") == "object" and "properties" in prop_schema:
        return True
    if prop_schema.get("type") == "array":
        items = prop_schema.get("items", {})
        if items.get("type") == "object" and "properties" in items:
            return True
    return False


# ---------------------------------------------------------------------------
# Entity/enum extraction from OpenAPI
# ---------------------------------------------------------------------------


def extract_entity(name: str, schema: dict) -> dict:
    """Convert one OpenAPI schema object to the entity format."""
    required_set: set[str] = set(schema.get("required", []))
    properties: dict[str, dict] = schema.get("properties", {})

    fields: list[dict] = []
    for prop_name, prop_schema in sorted(properties.items()):
        if prop_name in _SKIP_PROPERTIES:
            continue

        # Inline objects on TrackerRelationshipItem are expansions of the
        # tracker entity types; reference them by name instead of inlining.
        if _is_inline_object(prop_schema):
            inline_type_map = {
                "trackedEntity": "TrackerTrackedEntity",
                "enrollment": "TrackerEnrollment",
                "event": "TrackerEvent",
            }
            ref_type = prop_name[0].upper() + prop_name[1:]
            resolved_type = inline_type_map.get(prop_name, ref_type)
            is_required = prop_name in required_set
            fields.append({
                "name": prop_name,
                "type": resolved_type,
                "required": is_required,
                "cardinality": "1..1" if is_required else "0..1",
                "description": prop_schema.get("description", ""),
            })
            continue

        field_type, is_array = _resolve_type(prop_schema)
        is_required = prop_name in required_set

        if is_array:
            cardinality = "1..*" if is_required else "0..*"
        else:
            cardinality = "1..1" if is_required else "0..1"

        fields.append({
            "name": prop_name,
            "type": field_type,
            "required": is_required,
            "cardinality": cardinality,
            "description": prop_schema.get("description", ""),
        })

    return {
        "id": name,
        "name": name,
        "description": _DESCRIPTIONS.get(name, ""),
        "parent": None,
        "source_url": "https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-master/tracker.html",
        "fields": fields,
    }


def extract_enum(name: str, schema: dict) -> tuple[str, dict]:
    """Convert an OpenAPI enum schema to the enum format."""
    values: list[dict] = []
    for code in schema.get("enum", []):
        label = code.replace("_", " ").title()
        values.append({
            "code": code,
            "label": label,
            "description": "",
        })

    return name, {
        "description": f"Allowed values for {name} in DHIS2.",
        "values": values,
    }


# ---------------------------------------------------------------------------
# Inline validation (minimal; replaces the v1 scripts.validate_entities dep)
# ---------------------------------------------------------------------------


def _validate_entities(entities: list[dict]) -> list[str]:
    """Check entity structural invariants. Return list of error strings."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, entity in enumerate(entities):
        prefix = f"entity[{i}]"
        for field in ("id", "name", "description"):
            value = entity.get(field)
            if not isinstance(value, str):
                errors.append(f"{prefix}: '{field}' must be a string")
            elif field in ("id", "name") and not value.strip():
                errors.append(f"{prefix}: '{field}' must be non-empty")

        if "parent" not in entity:
            errors.append(f"{prefix}: missing 'parent' (must be string or null)")

        fields = entity.get("fields")
        if not isinstance(fields, list):
            errors.append(f"{prefix}: 'fields' must be a list")

        entity_id = entity.get("id")
        if isinstance(entity_id, str) and entity_id.strip():
            if entity_id in seen_ids:
                errors.append(f"{prefix}: duplicate id '{entity_id}'")
            seen_ids.add(entity_id)

    return errors


def _validate_enums(enums: dict) -> list[str]:
    """Check enum structural invariants. Return list of error strings."""
    errors: list[str] = []
    for name, definition in enums.items():
        prefix = f"enum['{name}']"
        if not isinstance(definition, dict):
            errors.append(f"{prefix}: definition must be an object")
            continue
        values = definition.get("values")
        if not isinstance(values, list) or not values:
            errors.append(f"{prefix}: 'values' must be a non-empty list")
            continue
        seen: set[str] = set()
        for k, v in enumerate(values):
            if not isinstance(v, dict):
                errors.append(f"{prefix}.values[{k}]: must be an object")
                continue
            code = v.get("code")
            if not isinstance(code, str) or not code.strip():
                errors.append(f"{prefix}.values[{k}]: 'code' must be non-empty string")
                continue
            if code in seen:
                errors.append(f"{prefix}.values[{k}]: duplicate code '{code}'")
            seen.add(code)

    return errors


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def _auth_header() -> str:
    credentials = base64.b64encode(
        f"{_DEMO_USER}:{_DEMO_PASS}".encode("ascii")
    ).decode("ascii")
    return f"Basic {credentials}"


def _download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url)
    request.add_header("Authorization", _auth_header())
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=60) as response:
        dest.write_bytes(response.read())


def fetch(version: str) -> None:
    """Download openapi.json and the metadata JSONs from the DHIS2 demo server."""
    _EXTRACTED.mkdir(parents=True, exist_ok=True)
    base = f"{_PLAY_HOST}/{version}"

    print(f"Fetching DHIS2 data from {base} (user={_DEMO_USER})")

    # OpenAPI spec
    openapi_url = f"{base}/api/openapi.json"
    print(f"  {openapi_url}")
    _download(openapi_url, _OPENAPI_PATH)
    print(f"  -> {_OPENAPI_PATH.name} ({_OPENAPI_PATH.stat().st_size:,} bytes)")

    # Metadata endpoints
    for filename, endpoint in _METADATA_ENDPOINTS.items():
        url = base + endpoint
        dest = _EXTRACTED / filename
        print(f"  {url}")
        _download(url, dest)
        print(f"  -> {filename} ({dest.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# Conversion pipeline
# ---------------------------------------------------------------------------


def _extract_metadata_entities() -> tuple[list[dict], dict[str, dict]]:
    """Extract domain-level entities from DHIS2 metadata API responses."""
    if not (
        _TRACKED_ENTITY_TYPES_PATH.exists()
        and _PROGRAMS_PATH.exists()
        and _OPTION_SETS_PATH.exists()
    ):
        print(
            "WARNING: metadata files missing; skipping metadata-derived entities. "
            "Run with --fetch to download them.",
            file=sys.stderr,
        )
        return [], {}

    types_data = json.loads(_TRACKED_ENTITY_TYPES_PATH.read_text(encoding="utf-8"))
    programs_data = json.loads(_PROGRAMS_PATH.read_text(encoding="utf-8"))
    option_sets_data = json.loads(_OPTION_SETS_PATH.read_text(encoding="utf-8"))

    programs = programs_data.get("programs", [])

    entities: list[dict] = []
    all_enums: dict[str, dict] = {}

    for tet in types_data.get("trackedEntityTypes", []):
        if tet["name"] not in _METADATA_ENTITY_ALLOWLIST:
            continue

        attrs = _collect_person_attributes(tet, programs)
        attrs_with_os = [a for a in attrs if a.get("optionSet")]
        option_set_enums = _build_option_set_enums(option_sets_data, attrs_with_os)
        all_enums.update(option_set_enums)

        entity = _build_metadata_entity(tet["name"], attrs, option_set_enums)
        entities.append(entity)

    return entities, all_enums


def _extract_openapi_entities() -> tuple[list[dict], dict[str, dict]]:
    """Extract structural entities and enums from the OpenAPI spec."""
    raw = json.loads(_OPENAPI_PATH.read_text(encoding="utf-8"))
    all_schemas: dict[str, dict] = raw.get("components", {}).get("schemas", {})

    entities: list[dict] = []
    for name in _ENTITY_ALLOWLIST:
        schema = all_schemas.get(name)
        if schema is None:
            print(f"WARNING: schema '{name}' not found in OpenAPI spec", file=sys.stderr)
            continue
        entity = extract_entity(name, schema)
        if not entity["fields"]:
            print(f"WARNING: entity '{name}' has zero fields", file=sys.stderr)
        if not entity["description"]:
            print(f"WARNING: entity '{name}' has no description", file=sys.stderr)
        entities.append(entity)

    enums: dict[str, dict] = {}
    for name in _ENUM_ALLOWLIST:
        schema = all_schemas.get(name)
        if schema is None:
            print(f"WARNING: enum schema '{name}' not found", file=sys.stderr)
            continue
        if "enum" not in schema:
            print(f"WARNING: schema '{name}' has no enum values", file=sys.stderr)
            continue
        enum_name, enum_def = extract_enum(name, schema)
        enums[enum_name] = enum_def

    return entities, enums


def convert() -> tuple[list[dict], dict[str, dict]]:
    """Run the full conversion. Returns (entities, enums)."""
    meta_entities, meta_enums = _extract_metadata_entities()
    openapi_entities, openapi_enums = _extract_openapi_entities()

    entities = meta_entities + openapi_entities
    enums = {**openapi_enums, **meta_enums}

    total_fields = sum(len(e["fields"]) for e in entities)
    print(
        f"Converted {len(entities)} entities "
        f"({len(meta_entities)} from metadata, {len(openapi_entities)} from OpenAPI), "
        f"{total_fields} fields, "
        f"{len(enums)} enums"
    )

    return entities, enums


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Download openapi.json and metadata JSONs from the DHIS2 demo before converting.",
    )
    parser.add_argument(
        "--version",
        default=_DEFAULT_VERSION,
        help=f"DHIS2 demo version path segment (default: {_DEFAULT_VERSION})",
    )
    args = parser.parse_args()

    if args.fetch:
        fetch(args.version)

    entities, enums = convert()

    entity_errors = _validate_entities(entities)
    enum_errors = _validate_enums(enums)

    if entity_errors or enum_errors:
        for err in entity_errors:
            print(f"  ERROR (entities): {err}", file=sys.stderr)
        for err in enum_errors:
            print(f"  ERROR (enums): {err}", file=sys.stderr)
        sys.exit(1)

    _ENTITIES_OUT.write_text(
        json.dumps(entities, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _ENUMS_OUT.write_text(
        json.dumps(enums, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {_ENTITIES_OUT}")
    print(f"Wrote {_ENUMS_OUT}")


if __name__ == "__main__":
    main()
