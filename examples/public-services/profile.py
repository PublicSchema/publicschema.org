"""SyntheticPermitJourneyProfileV1: local fixture checks, not a legal decision engine.

Run structural JSON Schema/SHACL checks through tests/test_public_services.py.
The sidecar grants are trusted synthetic profile configuration, never caller claims.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ORGANIZATIONS = {"Organization", "PublicOrganization", "LegalEntity"}
APPLICANTS = ORGANIZATIONS | {"Person"}
REQUIRED = {
    "PublicService": ("name", "service_competent_authorities", "legal_resources"),
    "ServiceApplication": (
        "public_service", "service_applicant", "application_subject", "submitted_by",
        "receiving_authority", "submitted_at", "recorded_at",
    ),
    "AdministrativeDecision": (
        "decision_subject", "decision_authority", "decision_outcome", "decision_made_at",
        "effective_at", "recorded_at", "legal_resources",
    ),
    "AdministrativeAppeal": (
        "challenged_decision", "appellant", "submitted_by", "reviewing_authority",
        "submitted_at", "recorded_at",
    ),
    "OrganizationalChangeEvent": (
        "original_organizations", "resulting_organizations", "lifecycle_kind", "effective_at",
        "recorded_at", "event_authority", "legal_resources",
    ),
    "Authorization": ("registered_subject", "registration_authority", "authorized_activity"),
    "RegulatoryAction": ("action_subject", "action_authority", "action_type", "action_date"),
    "RepresentationRole": ("representative_actor", "represented_subject", "start_date"),
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
        value = record[field]
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.utcoffset() is None:
                raise ValueError("missing timezone")
        except (AttributeError, TypeError, ValueError) as exc:
            raise ProfileError(f"{record['@id']}.{field}: timezone-qualified timestamp required") from exc
        return parsed

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
        permit = linked(challenged, "decision_subject", {"Authorization"})
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
        effective = timestamp(record, "effective_at")
        for key in resulting - original:
            created_at[key] = min(effective, created_at.get(key, effective))
        linked(record, "event_authority", ORGANIZATIONS)

    for record in records:
        key, kind = record["@id"], record["@type"]
        for start, end in (("start_date", "end_date"), ("valid_from", "valid_to")):
            if start in record and end in record and record[start] > record[end]:
                raise ProfileError(f"{key}.{end}: reversed period")
        if kind == "RepresentationRole" and record.get("end_date") == record["start_date"]:
            raise ProfileError(f"{key}.end_date: empty or reversed representation period")
        for field in ("submitted_at", "decision_made_at", "effective_at", "recorded_at"):
            if field in record:
                timestamp(record, field)
        for field in ("submitted_at", "decision_made_at"):
            if field in record and timestamp(record, field) > timestamp(record, "recorded_at"):
                raise ProfileError(f"{key}.recorded_at: precedes {field}")
        for value in record.get("evidence_assertions", []):
            evidence = structured_value(value, "EvidenceAssertion", f"{key}.evidence_assertions")
            if evidence.get("assertion_uri") != key:
                raise ProfileError(f"{key}.evidence_assertions: evidence is about a different assertion")
            reference(evidence.get("evidence_authority"), ORGANIZATIONS, f"{key}.evidence_authority")
        if kind == "PublicService":
            for value in record["service_competent_authorities"]:
                reference(value, {"PublicOrganization"}, f"{key}.service_competent_authorities")
        if kind == "RecordLifecycleEvent":
            linked(record, "subject_uri", None)
        if kind in {"ServiceApplication", "AdministrativeAppeal"}:
            actor_field = "service_applicant" if kind == "ServiceApplication" else "appellant"
            actor = linked(record, actor_field, APPLICANTS)
            submitter = linked(record, "submitted_by", APPLICANTS)
            service = service_for_application(record) if kind == "ServiceApplication" else service_for_appeal(record)
            authority_field = "receiving_authority" if kind == "ServiceApplication" else "reviewing_authority"
            authority = linked(record, authority_field, {"PublicOrganization"})
            when = timestamp(record, "submitted_at")
            if authority["@id"] in created_at and when < created_at[authority["@id"]]:
                raise ProfileError(f"{key}.{authority_field}: authority predates its creation")
            if kind == "ServiceApplication":
                linked(record, "application_subject", None)
            else:
                challenged = linked(record, "challenged_decision", {"AdministrativeDecision"})
                if when < timestamp(challenged, "decision_made_at"):
                    raise ProfileError(f"{key}.submitted_at: appeal precedes challenged decision")
            if actor["@id"] != submitter["@id"] or "submission_representation" in record:
                if "submission_representation" not in record:
                    raise ProfileError(f"{key}.submission_representation: representative requires a cited role")
                role = linked(record, "submission_representation", {"RepresentationRole"})
                if (role["representative_actor"], role["represented_subject"]) != (submitter["@id"], actor["@id"]):
                    raise ProfileError(f"{key}.submission_representation: actor or represented subject mismatch")
                # This synthetic profile uses UTC calendar days: start included,
                # end is the first inactive day. Permission validity is separate.
                day = when.astimezone(timezone.utc).date().isoformat()
                if day < role["start_date"] or (role.get("end_date") and day >= role["end_date"]):
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
        subject = linked(record, "decision_subject", None)
        authority = linked(record, "decision_authority", {"PublicOrganization"})
        made_at = timestamp(record, "decision_made_at")
        if authority["@id"] in created_at and made_at < created_at[authority["@id"]]:
            raise ProfileError(f"{key}.decision_authority: authority predates its creation")
        if "decides_application" in record:
            application = linked(record, "decides_application", {"ServiceApplication"})
            if subject["@id"] != application["application_subject"]:
                raise ProfileError(f"{key}.decision_subject: differs from application subject")
            if made_at < timestamp(application, "submitted_at"):
                raise ProfileError(f"{key}.decision_made_at: precedes application")
        for value in record.get("decision_authorizations", []):
            permit = reference(value, {"Authorization"}, f"{key}.decision_authorizations")
            if permit["registered_subject"] != subject["@id"]:
                raise ProfileError(f"{key}.decision_authorizations: permit subject differs from decision subject")
            issuer = linked(permit, "registration_authority", {"PublicOrganization"})
            if issuer["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.decision_authorizations: permit issuer differs from deciding authority")
        for value in record.get("decision_regulatory_actions", []):
            action = reference(value, {"RegulatoryAction"}, f"{key}.decision_regulatory_actions")
            if action["action_subject"] != subject["@id"]:
                raise ProfileError(f"{key}.decision_regulatory_actions: action subject differs from decision subject")
            if linked(action, "action_authority", {"PublicOrganization"})["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.decision_regulatory_actions: action authority differs from deciding authority")
        outcome = local_code(record, "decision_outcome")
        if outcome["code_scheme"] != config["decision_outcome_scheme"]:
            raise ProfileError(f"{key}.decision_outcome: unsupported local outcome scheme")
        if outcome["code_value"] == "granted":
            if not record.get("decision_authorizations"):
                raise ProfileError(f"{key}.decision_authorizations: synthetic grant requires a permission")
        elif outcome["code_value"] == "suspended":
            if subject["@type"] != "Authorization":
                raise ProfileError(f"{key}.decision_subject: suspension must target a permission")
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
            if challenged["decision_subject"] != subject["@id"]:
                raise ProfileError(f"{key}.decision_subject: differs from challenged decision subject")
            if made_at < timestamp(appeal, "submitted_at"):
                raise ProfileError(f"{key}.decision_made_at: precedes appeal")
            if linked(appeal, "reviewing_authority", {"PublicOrganization"})["@id"] != authority["@id"]:
                raise ProfileError(f"{key}.decision_authority: differs from reviewing authority")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path, nargs="?", default=directory / "records.json")
    parser.add_argument("--profile", type=Path, default=directory / "profile.json")
    args = parser.parse_args()
    records = json.loads(args.records.read_text())
    validate_journey(records, json.loads(args.profile.read_text()))
    print(f"Validated {len(records)} synthetic public service records.")
