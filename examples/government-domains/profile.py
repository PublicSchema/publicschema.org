"""Deliberately local example profile for the government domain records.

Run: uv run --locked python examples/government-domains/profile.py
This is not reference-vocabulary or runtime enforcement. Complete typed subjects
must be present; same-URI references do not mint new actors. Dates and ownership
percentage are application rules.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from profile_support import check_period, parse_day  # noqa: E402

ORGANIZATION_TYPES = {"Organization", "PublicOrganization", "edu/EducationProvider"}
ACTOR_TYPES = ORGANIZATION_TYPES | {"Person"}
# valid_to is the last valid day; end_date is the first inactive day.
PERIODS = (("valid_from", "valid_to", False), ("start_date", "end_date", True))


def period_errors(record):
    errors = []
    for begin, end, exclusive in PERIODS:
        bounds = []
        for field in (begin, end):
            try:
                bounds.append(parse_day(record[field], field) if field in record else None)
            except ValueError as error:
                errors.append(str(error))
                bounds.append(None)
        try:
            check_period(*bounds, exclusive=exclusive)
        except ValueError:
            errors.append("empty or reversed period")
    return errors


def profile_errors(records):
    """Return every profile error; an empty list means the records pass."""
    index = {}
    errors = []
    for record in records:
        if record["@id"] in index:
            errors.append(f"{record['@id']}: duplicate record identity")
        index[record["@id"]] = record
    for record in records:
        kind = record["@type"]
        errors.extend(period_errors(record))
        field = None
        allowed = set()
        if kind in {"ProfessionalLicense", "transport/DrivingEntitlement", "elections/VoterRegistration"}:
            field, allowed = "registered_subject", {"Person"}
        elif kind == "tax/TaxRegistration":
            field, allowed = "registered_subject", ACTOR_TYPES
        elif kind in {"OwnershipInterest", "InstitutionalRole"}:
            field = "interest_holder" if kind == "OwnershipInterest" else "role_actor"
            allowed = ACTOR_TYPES
        if kind == "AssetPartyRole":
            field, allowed = "asset_actor", ACTOR_TYPES
        if kind == "RepresentationRole":
            field, allowed = "representative", ACTOR_TYPES
            represented = index.get(record.get("represented"))
            if represented is None or represented["@type"] not in allowed:
                errors.append("invalid represented party")
        if field:
            target = index.get(record.get(field))
            if target is None:
                errors.append("missing actor")
            elif target["@type"] not in allowed:
                errors.append("wrong actor kind")
        if kind == "OwnershipInterest" and "interest_percentage" in record:
            percentage = record["interest_percentage"]
            if isinstance(percentage, bool) or not isinstance(percentage, (int, float)):
                errors.append("percentage must be a number")
            elif not 0 <= percentage <= 100:
                errors.append("percentage outside zero to one hundred")
    return errors


if __name__ == "__main__":
    errors = profile_errors(json.loads(Path(__file__).with_name("records.json").read_text()))
    if errors:
        sys.exit("Government domain example profile failed: " + "; ".join(errors))
    print("Government domain example profile: passed")
