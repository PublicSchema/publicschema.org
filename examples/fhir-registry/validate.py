"""Offline reference integration, not a general FHIR conformance validator.

Use the byte-pinned official R5 JSON Schema for structural checks and published
StructureDefinition targetProfile constraints for this example's local links.
The separate HL7 Java validator command in the guide checks FHIR invariants.
Neither this adapter nor the JSON Schema validates terminology or custom profiles.
"""

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft6Validator, ValidationError
from referencing import Registry
from referencing.exceptions import NoSuchResource

HERE = Path(__file__).resolve().parent
FHIR_RELEASE = "5.0.0"
PROFILE_BASE = "http://hl7.org/fhir/StructureDefinition/"
LOCATION_FORM_SYSTEM = "http://terminology.hl7.org/CodeSystem/location-physical-type"
NATIVE_SUBJECTS = {
    "Organization": ("Organization", "https://publicschema.org/Organization"),
    "SubstanceDefinition": ("Substance", "https://publicschema.org/Substance"),
    "Location": ("health/HealthFacility", "https://publicschema.org/health/HealthFacility"),
}


class ContractError(ValueError):
    """A supplied resource or registry link violates this example's contract."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def absolute_uri(value):
    require(isinstance(value, str) and bool(urlsplit(value).scheme), "expected absolute URI")
    require(not any(c.isspace() for c in value), "URI contains whitespace")
    return value


def record_key(value):
    register = absolute_uri(value["register_uri"])
    identifier = value["record_id"]
    require(isinstance(identifier, str) and bool(identifier), "record_id must be a nonempty string")
    return register, identifier


def _no_remote_schema(uri):
    raise NoSuchResource(ref=uri)


@lru_cache(maxsize=1)
def artifacts():
    """Read exact upstream bytes; no schema, profile, or context fetch is possible."""
    directory = HERE / "artifacts"
    manifest = json.loads((directory / "manifest.json").read_text())
    require(manifest["fhir_release"] == FHIR_RELEASE, "artifact release mismatch")
    for archive in (manifest["json_schema"], manifest["profile_archive"]):
        content = (directory / archive["file"]).read_bytes()
        require(hashlib.sha256(content).hexdigest() == archive["sha256"], "artifact checksum mismatch")
    with zipfile.ZipFile(directory / manifest["json_schema"]["file"]) as archive:
        schema = json.loads(archive.read(manifest["json_schema"]["member"]))
    profiles = {}
    with zipfile.ZipFile(directory / manifest["profile_archive"]["file"]) as archive:
        for item in manifest["profiles"]:
            content = archive.read(item["member"])
            require(hashlib.sha256(content).hexdigest() == item["sha256"], "profile checksum mismatch")
            profile = json.loads(content)
            require(profile["version"] == FHIR_RELEASE, "profile release mismatch")
            require(profile["url"] + "|" + FHIR_RELEASE == item["canonical"], "profile canonical mismatch")
            profiles[item["resource_type"]] = profile
    return schema, profiles


@lru_cache(maxsize=None)
def structural_validator(kind):
    schema, profiles = artifacts()
    require(kind in profiles, "resource type outside the example contract")
    # Select the published resource definition without changing its properties.
    selected = {
        "$schema": schema["$schema"],
        "$ref": "#/definitions/" + kind,
        "definitions": schema["definitions"],
    }
    return Draft6Validator(selected, registry=Registry(retrieve=_no_remote_schema))


def validate_structure(resource):
    kind = resource.get("resourceType")
    try:
        structural_validator(kind).validate(resource)
    except ValidationError as error:
        path = ".".join(str(part) for part in error.path) or "(resource)"
        raise ContractError(f"{kind}.{path}: {error.message}") from error


def validate_supported_content(value):
    """Fail explicitly on FHIR features this small integration cannot interpret."""
    if isinstance(value, dict):
        for key, child in value.items():
            require(key not in {"@context", "@type", "@id"}, "native FHIR JSON must not contain JSON-LD fields")
            require(key not in {"extension", "modifierExtension", "contained", "implicitRules"},
                    f"{key} requires an explicit extension of this example contract")
            validate_supported_content(child)
    elif isinstance(value, list):
        for child in value:
            validate_supported_content(child)


def _profile(kind):
    return PROFILE_BASE + kind + "|" + FHIR_RELEASE


def resource_index(bundle):
    require(bundle.get("resourceType") == "Bundle" and bundle.get("type") == "collection",
            "expected a native FHIR collection Bundle")
    validate_supported_content(bundle)
    require(bundle.get("meta", {}).get("profile") == [_profile("Bundle")], "Bundle profile must be pinned")
    result = {}
    for entry in bundle.get("entry", []):
        resource = entry["resource"]
        validate_structure(resource)
        kind = resource["resourceType"]
        require(kind != "Bundle", "nested Bundles are outside the example contract")
        require(resource.get("meta", {}).get("profile") == [_profile(kind)], "resource profile must be pinned")
        full_url = absolute_uri(entry["fullUrl"])
        parsed = urlsplit(full_url)
        require(parsed.scheme in {"https", "http"} and parsed.netloc and not parsed.query
                and not parsed.fragment and not parsed.username, "fullUrl must be an absolute HTTP(S) resource URL")
        require(full_url.endswith("/" + kind + "/" + resource.get("id", ""))
                and resource.get("id"), "fullUrl must correspond to resourceType/id")
        require(full_url not in result, "duplicate FHIR fullUrl")
        result[full_url] = resource
    require(bool(result), "collection Bundle requires local resources")
    validate_structure(bundle)
    return result


@lru_cache(maxsize=None)
def reference_targets(kind):
    """Use official R5 targetProfile values, including CodeableReference choices."""
    _, profiles = artifacts()
    result = {}
    for element in profiles[kind]["snapshot"]["element"]:
        for datatype in element.get("type", []):
            code = datatype["code"]
            if code not in {"Reference", "CodeableReference"}:
                continue
            path = element["path"].replace("[x]", code)
            if code == "CodeableReference":
                path += ".reference"
            result[path] = {uri.removeprefix(PROFILE_BASE) for uri in datatype["targetProfile"]}
    return result


def _references(value, definition, path):
    """Walk JSON Schema types so identifier-only Reference objects are also seen."""
    definitions = artifacts()[0]["definitions"]
    if "$ref" in definition:
        name = definition["$ref"].removeprefix("#/definitions/")
        if name == "Reference":
            yield path, value
            return
        definition = definitions[name]
    if isinstance(value, list):
        for index, child in enumerate(value):
            yield from _references(child, definition["items"], (*path, index))
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _references(child, definition["properties"][key], (*path, key))


def _identifiers(resource):
    values = resource.get("identifier", [])
    return [values] if isinstance(values, dict) else values


def _identifier_matches(identifier, resource):
    require(isinstance(identifier.get("value"), str) and identifier["value"], "business identifier requires a value")
    absolute_uri(identifier["system"])
    return any(item.get("system") == identifier["system"] and item.get("value") == identifier["value"]
               for item in _identifiers(resource))


def validate_fhir_references(resources):
    count = 0
    for full_url, resource in resources.items():
        kind = resource["resourceType"]
        definition = artifacts()[0]["definitions"][kind]
        rules = reference_targets(kind)
        for path, reference in _references(resource, definition, (kind,)):
            semantic_path = ".".join(part for part in path if isinstance(part, str))
            allowed = rules.get(semantic_path)
            require(allowed is not None, f"{semantic_path}: reference path requires a reviewed contract addition")
            literal = reference.get("reference")
            require(isinstance(literal, str) and literal, f"{semantic_path}: literal reference required")
            if urlsplit(literal).scheme:
                target_url = literal
            else:
                require(re.fullmatch(r"[A-Z][A-Za-z]+/[A-Za-z0-9\-.]{1,64}", literal),
                        f"{semantic_path}: expected ResourceType/id or exact absolute fullUrl")
                target_url = full_url.rsplit("/", 2)[0] + "/" + literal
            target = resources.get(target_url)
            require(target is not None, f"{semantic_path}: missing local FHIR target (no remote resolution)")
            target_kind = target["resourceType"]
            require(target_kind in allowed or "Resource" in allowed,
                    f"{semantic_path}: wrong FHIR target type {target_kind}")
            if "type" in reference:
                require(reference["type"] in {target_kind, PROFILE_BASE + target_kind},
                        f"{semantic_path}: Reference.type disagrees with target")
            if "identifier" in reference:
                require(_identifier_matches(reference["identifier"], target),
                        f"{semantic_path}: Reference.identifier disagrees with target")
            count += 1
    return count


def registry_index(envelope):
    result = {}
    for binding in envelope["records"]:
        entry = binding["entry"]
        require(entry.get("@type") == "RegistryEntry", "expected PublicSchema RegistryEntry")
        key = record_key(entry)
        require(key not in result, "duplicate qualified registry record key")
        absolute_uri(entry["subject_uri"])
        timestamp = datetime.fromisoformat(entry["recorded_at"].replace("Z", "+00:00"))
        require(timestamp.tzinfo is not None, "recorded_at requires a timezone")
        result[key] = binding
    return result


def resolve_record(reference, expected_resource_type, records, resources):
    """Resolve only supplied qualified records; preserve the native FHIR resource.

    Missing entries are explicit outcomes, while identity/type disagreement is an
    error. The caller decides whether a missing source is acceptable for its use.
    """
    require(reference.get("@type") == "RecordReference", "expected PublicSchema RecordReference")
    binding = records.get(record_key(reference))
    if binding is None:
        return {"state": "missing-record"}
    entry = binding["entry"]
    for field in ("subject_uri", "subject_type"):
        if field in reference:
            require(reference[field] == entry.get(field), f"record and reference disagree on {field}")
    require(binding["resource_type"] == expected_resource_type, "wrong expected FHIR resource type")
    resource = resources.get(binding["fhir_full_url"])
    if resource is None:
        return {"state": "missing-resource", "subject_uri": entry["subject_uri"]}
    require(resource["resourceType"] == expected_resource_type, "binding has wrong FHIR resource type")
    require(binding["profile"] == _profile(expected_resource_type)
            and resource.get("meta", {}).get("profile") == [binding["profile"]], "binding profile mismatch")
    require(_identifier_matches(binding["business_identifier"], resource), "binding business identifier mismatch")
    require(entry["subject_uri"] != binding["fhir_full_url"], "subject URI must be distinct from the FHIR record URL")
    return {"state": "resolved", "subject_uri": entry["subject_uri"], "resource": resource}


def validate_integration(bundle, envelope):
    require(envelope.get("contract") == "publicschema-fhir-r5-local-v1", "unknown integration contract")
    require(envelope.get("fhir_release") == FHIR_RELEASE, "FHIR release mismatch")
    require(envelope.get("fhir_media_type") == "application/fhir+json", "native FHIR media type required")
    resources = resource_index(bundle)
    reference_count = validate_fhir_references(resources)
    records = registry_index(envelope)
    subjects = {}
    for subject in envelope["subjects"]:
        uri = absolute_uri(subject["@id"])
        require(uri not in subjects, "duplicate native subject identity")
        subjects[uri] = subject
    bound_urls = set()
    used_subjects = set()
    for binding in records.values():
        entry = binding["entry"]
        reference = {"@type": "RecordReference", "register_uri": entry["register_uri"], "record_id": entry["record_id"]}
        resolved = resolve_record(reference, binding["resource_type"], records, resources)
        require(resolved["state"] == "resolved", "registry binding has a missing local FHIR resource")
        require(binding["fhir_full_url"] not in bound_urls, "duplicate FHIR record binding")
        bound_urls.add(binding["fhir_full_url"])
        native = NATIVE_SUBJECTS.get(binding["resource_type"])
        if native:
            if binding["resource_type"] == "Location":
                location = resolved["resource"]
                forms = {coding.get("code") for coding in location.get("form", {}).get("coding", [])
                         if coding.get("system") == LOCATION_FORM_SYSTEM}
                require(location.get("mode") == "instance" and forms and forms <= {"si", "bu"},
                        "HealthFacility binding requires an instance Location classified as a physical site or building")
            require(entry.get("subject_type") == native[1], "wrong native subject type for FHIR binding")
            subject = subjects.get(entry["subject_uri"])
            require(subject is not None, "missing native subject")
            require(subject.get("@type") == native[0], "resolved native subject has wrong type")
            used_subjects.add(entry["subject_uri"])
        else:
            require("subject_type" not in entry, "this contract does not mint a native medical subject type")
    require(bound_urls == resources.keys(), "every supplied FHIR resource needs an explicit registry binding")
    require(used_subjects == subjects.keys(), "native subject lacks a reviewed FHIR binding")
    for link in envelope["links"]:
        resolved = resolve_record(link["record"], link["expected_resource_type"], records, resources)
        require(resolved["state"] == "resolved", "required consumer link is " + resolved["state"])
    for outcome in envelope.get("migration_outcomes", []):
        record_key(outcome["source_record"])
        require(outcome.get("state") == "unmapped" and outcome.get("source_path")
                and "source_value" in outcome and outcome.get("reason"), "unmapped outcome must retain source, value, and reason")
    return {"fhir_resources": len(resources), "registry_entries": len(records),
            "local_fhir_references": reference_count, "consumer_links": len(envelope["links"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=HERE / "bundle.fhir.json")
    parser.add_argument("--links", type=Path, default=HERE / "registry-links.json")
    args = parser.parse_args()
    try:
        result = validate_integration(json.loads(args.bundle.read_text()), json.loads(args.links.read_text()))
    except (ContractError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Reference integration failed: {error}\n")
    print(json.dumps(result, indent=2))
    print("PASS: official R5 JSON Schema and local reference contract; not full FHIR conformance.")


if __name__ == "__main__":
    main()
