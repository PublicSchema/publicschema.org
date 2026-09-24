"""SyntheticPermitJourneyProfileV1: local fixture checks, not a legal decision engine.

Run structural JSON Schema/SHACL checks through tests/test_public_services.py.
The sidecar grants are trusted synthetic profile configuration, never caller claims.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from profile_support import check_period, parse_day  # noqa: E402

ORGANIZATIONS = {"Organization", "PublicOrganization"}
APPLICANTS = ORGANIZATIONS | {"Person"}
REQUIRED = {
    "PublicService": ("name", "service_competent_authorities", "legal_resources"),
    "ServiceApplication": (
        "public_service", "service_applicant", "subject_uri", "submitted_by",
        "authority", "request_submission_date", "recorded_at",
    ),
    "AdministrativeDecision": (
        "subject_uri", "authority", "decision_outcome", "decision_date",
        "effective_at", "recorded_at", "legal_resources",
    ),
    "AdministrativeAppeal": (
        "challenged_decision", "appellant", "submitted_by", "authority",
        "request_submission_date", "recorded_at",
    ),
    "OrganizationalChangeEvent": (
        "original_organizations", "resulting_organizations", "lifecycle_kind", "effective_at",
        "recorded_at", "authority", "legal_resources",
    ),
    "Authorization": ("registered_subject", "registration_authority", "authorized_activity"),
    "RegulatoryAction": ("subject_uri", "authority", "action_type", "action_date"),
    "RecordLifecycleEvent": ("affected_record",),
    "RepresentationRole": ("representative", "represented", "start_date"),
}


class ProfileError(ValueError):
    """An addressable failure in the named synthetic profile."""


def validate_journey(records, config):
    """Validate complete local references and this synthetic permit journey's rules.

    This function reads no remote records and changes no input. It neither accepts
    arbitrary jurisdictions nor computes the current legal status of a permission.
    """
    index = {}
    for record in records:
        key = record.get("@id")
        if not key or key in index:
            raise ProfileError(f"{key}: missing or duplicate record identity")
        index[key] = record
        for field in REQUIRED.get(record.get("@type"), ()):
            if record.get(field) in (None, "", []):
                raise ProfileError(f"{key}.{field}: required by SyntheticPermitJourneyProfileV1")

    def reference(value, allowed, path):
        key = value.get("@id") if isinstance(value, dict) else value
        if not isinstance(key, str) or not key:
            raise ProfileError(f"{path}: URI string or @id reference required")
        target = index.get(key)
        if target is None:
            raise ProfileError(f"{path}: missing referenced record {key}")
        if isinstance(value, dict) and value.get("@type") not in (None, target["@type"]):
            raise ProfileError(f"{path}: declared type disagrees with referenced record")
        if allowed is not None and target["@type"] not in allowed:
            raise ProfileError(f"{path}: wrong referenced type {target['@type']}")
        return target

    def timestamp(record, field):
        if field not in record:
            raise ProfileError(f"{record['@id']}.{field}: required to check this record's dates")
        value = record[field]
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.utcoffset() is None:
                raise ValueError("missing timezone")
        except (AttributeError, TypeError, ValueError) as exc:
            raise ProfileError(f"{record['@id']}.{field}: timezone-qualified timestamp required") from exc
        return parsed

    def calendar_date(record, field):
        try:
            return parse_day(record.get(field), field)
        except ValueError as exc:
            raise ProfileError(f"{record['@id']}.{field}: calendar date required") from exc

    def period(record, start, end, *, exclusive, label):
        try:
            check_period(calendar_date(record, start), calendar_date(record, end), exclusive=exclusive)
        except ProfileError:
            raise
        except ValueError as exc:
            raise ProfileError(f"{record['@id']}.{end}: empty or reversed {label}") from exc

    def utc_day(record, field):
        # This synthetic profile compares calendar dates with the UTC day of a timestamp.
        return timestamp(record, field).astimezone(UTC).date()

    def linked(record, field, allowed):
        return reference(record[field], allowed, f"{record['@id']}.{field}")

    def structured_value(value, kind, path):
        if isinstance(value, dict) and "@id" not in value:
            if value.get("@type") not in (None, kind):
                raise ProfileError(f"{path}: wrong inline value type {value['@type']}")
            return value
        return reference(value, {kind}, path)

    def local_code(record, field):
        value = structured_value(record[field], "CodedValue", f"{record['@id']}.{field}")
        if not all(
            isinstance(value.get(part), str) and value[part] for part in ("code_value", "code_scheme")
        ):
            raise ProfileError(f"{record['@id']}.{field}: code and scheme required by synthetic profile")
        return value

    def service_for_application(application):
        return linked(application, "public_service", {"PublicService"})["@id"]

    def service_for_appeal(appeal):
        # This fixture appeals a suspension of an issued permit. Other appeal
        # patterns need their own profile; no generic legal procedure is inferred.
        challenged = linked(appeal, "challenged_decision", {"AdministrativeDecision"})
        permit = linked(challenged, "subject_uri", {"Authorization"})
        grants = [
            decision for decision in records
            if decision["@type"] == "AdministrativeDecision"
            and any(reference(value, {"Authorization"}, f"{decision['@id']}.decision_authorizations")["@id"] == permit["@id"]
                    for value in decision.get("decision_authorizations", []))
        ]
        if len(grants) != 1 or "decides_application" not in grants[0]:
            raise ProfileError(f"{appeal['@id']}: expected one original application grant for permit")
        application = linked(grants[0], "decides_application", {"ServiceApplication"})
        return service_for_application(application)

    created_at = {}
    for record in records:
        if record["@type"] != "OrganizationalChangeEvent":
            continue
        original = {reference(value, ORGANIZATIONS, record["@id"])["@id"]
                    for value in record["original_organizations"]}
        resulting = {reference(value, ORGANIZATIONS, record["@id"])["@id"]
                     for value in record["resulting_organizations"]}
        if not resulting - original:
            raise ProfileError(f"{record['@id']}: material change requires a distinct resulting identity")
        effective = utc_day(record, "effective_at")
        for key in resulting - original:
            created_at[key] = min(effective, created_at.get(key, effective))
        linked(record, "authority", ORGANIZATIONS)

    for record in records:
        key, kind = record["@id"], record["@type"]
        label = "representation period" if kind == "RepresentationRole" else "period"
        # end_date is the first inactive day; valid_to is the last valid day.
        for start, end, exclusive in (("start_date", "end_date", True), ("valid_from", "valid_to", False)):
            if start in record and end in record:
                period(record, start, end, exclusive=exclusive, label=label)
        for field in ("effective_at", "recorded_at"):
            if field in record:
                timestamp(record, field)
        for field in ("request_submission_date", "decision_date"):
            if field in record and calendar_date(record, field) > utc_day(record, "recorded_at"):
                raise ProfileError(f"{key}.recorded_at: precedes {field}")
        for value in record.get("evidence_assertions", []):
            evidence = structured_value(value, "EvidenceAssertion", f"{key}.evidence_assertions")
            if evidence.get("assertion_uri") != key:
                raise ProfileError(f"{key}.evidence_assertions: evidence is about a different assertion")
            reference(evidence.get("assertion_authority"), ORGANIZATIONS, f"{key}.assertion_authority")
        if kind == "PublicService":
            for value in record["service_competent_authorities"]:
                reference(value, {"PublicOrganization"}, f"{key}.service_competent_authorities")
        if kind == "RecordLifecycleEvent":
            affected = structured_value(record["affected_record"], "RecordReference", f"{key}.affected_record")
            reference(affected.get("subject_uri"), None, f"{key}.affected_record.subject_uri")
        if kind in {"ServiceApplication", "AdministrativeAppeal"}:
            actor_field = "service_applicant" if kind == "ServiceApplication" else "appellant"
            actor = linked(record, actor_field, APPLICANTS)
            submitter = linked(record, "submitted_by", APPLICANTS)
            service = service_for_application(record) if kind == "ServiceApplication" else service_for_appeal(record)
            authority = linked(record, "authority", {"PublicOrganization"})
            when = calendar_date(record, "request_submission_date")
            if authority["@id"] in created_at and when < created_at[authority["@id"]]:
                raise ProfileError(f"{key}.authority: authority predates its creation")
            if kind == "ServiceApplication":
                linked(record, "subject_uri", None)
            else:
                challenged = linked(record, "challenged_decision", {"AdministrativeDecision"})
                if when < calendar_date(challenged, "decision_date"):
                    raise ProfileError(f"{key}.request_submission_date: appeal precedes challenged decision")
            if actor["@id"] != submitter["@id"] or "submission_representation" in record:
                if "submission_representation" not in record:
                    raise ProfileError(f"{key}.submission_representation: representative requires a cited role")
                role = linked(record, "submission_representation", {"RepresentationRole"})
                representative = linked(role, "representative", APPLICANTS)["@id"]
                represented = linked(role, "represented", APPLICANTS)["@id"]
                if (representative, represented) != (submitter["@id"], actor["@id"]):
                    raise ProfileError(f"{key}.submission_representation: representative or represented party mismatch")
                # The start day is included and the end day is the first inactive day.
                # Permission validity is separate.
                starts = calendar_date(role, "start_date")
                ends = calendar_date(role, "end_date") if "end_date" in role else None
                if when < starts or (ends is not None and when >= ends):
                    raise ProfileError(f"{key}.submission_representation: outside representation period")
                if not any(
                    grant["representation_uri"] == role["@id"]
                    and grant["service_uri"] == service
                    and kind in grant["allowed_submission_types"]
                    for grant in config["representation_grants"]
                ):
                    raise ProfileError(f"{key}.submission_representation: no bound grant for submission kind and service")
        if kind != "AdministrativeDecision":
            continue
        subject = linked(record, "subject_uri", None)
        authority = linked(record, "authority", {"PublicOrganization"})
        made_on = calendar_date(record, "decision_date")
        if authority["@id"] in created_at and made_on < created_at[authority["@id"]]:
            raise ProfileError(f"{key}.authority: authority predates its creation")
        if "decides_application" in record:
            application = linked(record, "decides_application", {"ServiceApplication"})
            if subject["@id"] != linked(application, "subject_uri", None)["@id"]:
                raise ProfileError(f"{key}.subject_uri: differs from application subject")
            if made_on < calendar_date(application, "request_submission_date"):
                raise ProfileError(f"{key}.decision_date: precedes application")
        for value in record.get("decision_authorizations", []):
            permit = reference(value, {"Authorization"}, f"{key}.decision_authorizations")
            if linked(permit, "registered_subject", None)["@id"] != subject["@id"]:
                raise ProfileError(f"{key}.decision_authorizations: permit subject differs from decision subject")
            issuer = linked(permit, "registration_authority", {"PublicOrganization"})
            if issuer["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.decision_authorizations: permit issuer differs from deciding authority")
        for value in record.get("decision_regulatory_actions", []):
            action = reference(value, {"RegulatoryAction"}, f"{key}.decision_regulatory_actions")
            if linked(action, "subject_uri", None)["@id"] != subject["@id"]:
                raise ProfileError(f"{key}.decision_regulatory_actions: action subject differs from decision subject")
            if linked(action, "authority", {"PublicOrganization"})["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.decision_regulatory_actions: action authority differs from deciding authority")
        outcome = local_code(record, "decision_outcome")
        if outcome["code_scheme"] != config["decision_outcome_scheme"]:
            raise ProfileError(f"{key}.decision_outcome: unsupported local outcome scheme")
        if outcome["code_value"] == "granted":
            if not record.get("decision_authorizations"):
                raise ProfileError(f"{key}.decision_authorizations: synthetic grant requires a permission")
        elif outcome["code_value"] == "suspended":
            if subject["@type"] != "Authorization":
                raise ProfileError(f"{key}.subject_uri: suspension must target a permission")
            actions = record.get("decision_regulatory_actions", [])
            if not actions:
                raise ProfileError(f"{key}.decision_regulatory_actions: synthetic suspension requires an action")
            for value in actions:
                action = reference(value, {"RegulatoryAction"}, key)
                action_type = local_code(action, "action_type")
                if action_type["code_scheme"] != config["regulatory_action_scheme"] or action_type["code_value"] != "suspension":
                    raise ProfileError(f"{key}.decision_regulatory_actions: requires local suspension code and scheme")
        elif outcome["code_value"] == "upheld":
            if "resolves_appeal" not in record:
                raise ProfileError(f"{key}.resolves_appeal: synthetic review requires an appeal")
        else:
            raise ProfileError(f"{key}.decision_outcome: unsupported local outcome code")
        if "resolves_appeal" in record:
            appeal = linked(record, "resolves_appeal", {"AdministrativeAppeal"})
            challenged = linked(appeal, "challenged_decision", {"AdministrativeDecision"})
            if challenged["@id"] == key:
                raise ProfileError(f"{key}.resolves_appeal: cannot resolve an appeal against itself")
            if linked(challenged, "subject_uri", None)["@id"] != subject["@id"]:
                raise ProfileError(f"{key}.subject_uri: differs from challenged decision subject")
            if made_on < calendar_date(appeal, "request_submission_date"):
                raise ProfileError(f"{key}.decision_date: precedes appeal")
            if linked(appeal, "authority", {"PublicOrganization"})["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.authority: differs from reviewing authority")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path, nargs="?", default=directory / "records.json")
    parser.add_argument("--profile", type=Path, default=directory / "profile.json")
    args = parser.parse_args()
    records = json.loads(args.records.read_text())
    validate_journey(records, json.loads(args.profile.read_text()))
    print(f"Validated {len(records)} synthetic public service records.")
