"""Validate the bounded, locally resolved government relationship demonstration.

Run: uv run --locked python examples/government-relationships/validate_profile.py
These checks supplement the reference vocabulary. They do not verify source truth,
beneficial ownership, accreditation, legal authority or environmental compliance.
"""

import argparse
import copy
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from profile_support import absolute_uri, check_period, coded_value, parse_day  # noqa: E402

ORGANIZATIONS = {"Organization", "PublicOrganization", "edu/EducationProvider"}
INTEREST_ENTITIES = ORGANIZATIONS | {"LegalArrangement"}
INTEREST_HOLDERS = INTEREST_ENTITIES | {"Person"}
LOWER_BOUNDS = ("interest_minimum_percentage", "interest_exclusive_minimum_percentage")
UPPER_BOUNDS = ("interest_maximum_percentage", "interest_exclusive_maximum_percentage")
BOUNDS = LOWER_BOUNDS + UPPER_BOUNDS


def reference_uri(value):
    key = value.get("@id") if isinstance(value, dict) else value
    if not absolute_uri(key):
        raise ValueError("A reference must identify an absolute subject URI")
    return key


def qualification_definitions(record, index):
    values = record.get("qualification_awarded", [])
    if not isinstance(values, list):
        raise ValueError("Qualifications awarded must be a list of definition URIs")
    for value in values:
        if not absolute_uri(value):
            raise ValueError("A qualification awarded must be an absolute definition URI")
        if value in index:
            raise ValueError("This example uses an external qualification definition, not a local awarded qualification")


def index_records(records):
    if not isinstance(records, list):
        raise ValueError("The example exchange must be a list of records")
    index = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("@type"), str):
            raise ValueError("Each example record requires one explicit type")
        key = reference_uri(record)
        if key in index:
            raise ValueError("Duplicate subject URI in the example snapshot")
        index[key] = record
    return index


def resolve(value, index, accepted):
    key = reference_uri(value)
    if key not in index:
        raise ValueError("Unresolved local target")
    record = index[key]
    if record["@type"] not in accepted:
        raise ValueError("Wrong resolved target type")
    if isinstance(value, dict) and "@type" in value and value["@type"] != record["@type"]:
        raise ValueError("Reference type contradicts the resolved subject")
    return record


def period(record):
    start, end = (parse_day(record[key], key) if key in record else None
                  for key in ("start_date", "end_date"))
    # Whole-day convention: start is inclusive; end is the first inactive day.
    check_period(start, end, exclusive=True, message="The effective interval must contain at least one day")
    return start, end


def percentage(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("An ownership percentage must be a number")
    # str() of an int, float or Decimal is always a valid Decimal literal, including nan and inf.
    number = Decimal(str(value))
    if not number.is_finite() or not 0 <= number <= 100:
        raise ValueError("An ownership percentage must be between zero and one hundred")
    return number


def validate_share(record):
    present = {key for key in BOUNDS if key in record}
    if "interest_percentage" in record:
        percentage(record["interest_percentage"])
        if present:
            raise ValueError("An exact ownership percentage cannot also be an interval")
    if all(key in present for key in LOWER_BOUNDS) or all(key in present for key in UPPER_BOUNDS):
        raise ValueError("Inclusive and exclusive bounds cannot describe the same side")
    for key in present:
        percentage(record[key])
    # Mathematical limits of a percentage do not become asserted missing bounds.
    lower_key = next((key for key in LOWER_BOUNDS if key in present), None)
    upper_key = next((key for key in UPPER_BOUNDS if key in present), None)
    lower = percentage(record[lower_key]) if lower_key else Decimal(0)
    upper = percentage(record[upper_key]) if upper_key else Decimal(100)
    exclusive = lower_key == LOWER_BOUNDS[1] or upper_key == UPPER_BOUNDS[1]
    if lower > upper or (lower == upper and exclusive):
        raise ValueError("Ownership bounds describe an empty interval")


def ownership_route(primary, index):
    """Return explicit component IDs in endpoint order, without computing an interest."""
    if primary.get("interest_directness") != "indirect":
        raise ValueError("Component interests require an explicitly indirect interest")
    components = primary.get("component_interests")
    if not isinstance(components, list) or len(components) < 2:
        raise ValueError("The example indirect route requires at least two components")
    remaining = {}
    for value in components:
        component = resolve(value, index, {"OwnershipInterest"})
        if component["@id"] == primary["@id"] or component["@id"] in remaining:
            raise ValueError("A route cannot contain its primary interest or duplicate components")
        if component.get("interest_directness") != "direct":
            raise ValueError("This example route requires explicitly direct components")
        remaining[component["@id"]] = component

    current = reference_uri(primary.get("interest_holder"))
    destination = reference_uri(primary.get("interest_entity"))
    visited = {current}
    ordered = []
    primary_start, primary_end = period(primary)
    known_starts = [primary_start] if primary_start else []
    known_ends = [primary_end] if primary_end else []
    while current != destination:
        following = [record for record in remaining.values()
                     if reference_uri(record.get("interest_holder")) == current]
        if len(following) != 1:
            raise ValueError("The asserted route must be connected and must not branch")
        component = following[0]
        start, end = period(component)
        if start:
            known_starts.append(start)
        if end:
            known_ends.append(end)
        if (primary_start and start and primary_start < start
                or primary_end and end and primary_end > end
                or primary_start and end and primary_start >= end
                or primary_end and start and primary_end <= start):
            raise ValueError("A component period contradicts the asserted indirect period")
        current = reference_uri(component.get("interest_entity"))
        if current in visited:
            raise ValueError("The example ownership route must not contain a cycle")
        visited.add(current)
        ordered.append(component["@id"])
        del remaining[component["@id"]]
    if remaining:
        raise ValueError("The asserted route contains disconnected or unused components")
    if known_starts and known_ends and max(known_starts) >= min(known_ends):
        raise ValueError("The known component periods have no common effective day")
    return ordered


def validate_profile(records):
    """Check the selected exchange's complete references and local consistency rules."""
    index = index_records(records)
    for record in records:
        kind = record["@type"]
        if kind in {"OwnershipInterest", "edu/EducationOffering"}:
            period(record)
        if kind == "LegalArrangement":
            coded_value(record.get("arrangement_type"))
        if kind == "OwnershipInterest":
            resolve(record.get("interest_holder"), index, INTEREST_HOLDERS)
            resolve(record.get("interest_entity"), index, INTEREST_ENTITIES)
            coded_value(record.get("interest_type"))
            if record.get("interest_directness") not in {"direct", "indirect", "unknown"}:
                raise ValueError("An interest requires its asserted directness")
            validate_share(record)
        if kind == "edu/EducationOffering":
            provider = resolve(record.get("offering_provider"), index, {"edu/EducationProvider"})
            program = resolve(record.get("offering_program"), index, {"edu/EducationProgram"})
            sites = record.get("offering_sites")
            if not isinstance(sites, list) or not sites:
                raise ValueError("The example offering requires at least one delivery site")
            for value in sites:
                site = resolve(value, index, {"edu/ProviderSite"})
                site_provider = resolve(site.get("education_provider"), index, {"edu/EducationProvider"})
                if site_provider["@id"] != provider["@id"]:
                    raise ValueError("The offering and delivery site identify different providers")
                if "physical_service_point" in site:
                    resolve(site["physical_service_point"], index, {"ServicePoint", "edu/School"})
                if "virtual_site_url" in site and not absolute_uri(site["virtual_site_url"]):
                    raise ValueError("A virtual delivery site requires an absolute URL")
                if not {"physical_service_point", "virtual_site_url"} & site.keys():
                    raise ValueError("The example site requires a physical or virtual delivery point")
            for mode in record.get("offering_mode", []):
                coded_value(mode)
            qualification_definitions(record, index)
            qualification_definitions(program, index)
    for record in records:
        if record["@type"] == "OwnershipInterest" and "component_interests" in record:
            ownership_route(record, index)


def apply_case(records, case):
    """Apply a documented negative example to an independent copy of the fixture."""
    changed = copy.deepcopy(records)
    target = next((record for record in changed if record["@id"] == case["target"]), None)
    if target is None:
        raise ValueError(f"{case['name']}: no record {case['target']} to change")
    target.update(case.get("set", {}))
    for key in case.get("remove", []):
        target.pop(key, None)
    changed.extend(case.get("append", []))
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative", action="store_true", help="also verify documented counterexamples")
    arguments = parser.parse_args()
    records = json.loads(Path(__file__).with_name("records.json").read_text())
    validate_profile(records)
    print("Government qualified relationships example profile: passed")
    if arguments.negative:
        cases = json.loads(Path(__file__).with_name("negative-cases.json").read_text())
        for case in cases:
            changed = apply_case(records, case)
            try:
                validate_profile(changed)
            except ValueError as error:
                if case["expected"] not in str(error):
                    raise AssertionError(f"{case['name']}: unexpected rejection: {error}") from error
            else:
                raise AssertionError(f"{case['name']}: invalid example was accepted")
        print("Documented government relationship counterexamples: rejected as expected")
