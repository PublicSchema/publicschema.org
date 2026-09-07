"""Whole-day date conversion preserves meaning and refuses ambiguous source facts."""
import copy
import importlib.util
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld
from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import write_shacl

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/relationship-date-migration"
_spec = importlib.util.spec_from_file_location("date_migration", EXAMPLES / "migrate.py")
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)
BOUNDARY = migration.SOURCE_BOUNDARY


@pytest.fixture(scope="module")
def legacy():
    return json.loads((EXAMPLES / "legacy-records.json").read_text())


def convert(document, source_boundary=BOUNDARY):
    return migration.migrate_relationship_dates(document, source_boundary=source_boundary)


def schema_for(result, type_name):
    uri = result["context"]["@context"][type_name]
    return next(schema for schema in result["concept_schemas"].values() if schema["$id"] == uri + ".schema.json")


def test_fixture_conversion_is_reviewable_idempotent_and_does_not_mutate(legacy):
    original = copy.deepcopy(legacy)
    migrated = convert(legacy)
    assert migrated == json.loads((EXAMPLES / "records.json").read_text())
    assert legacy == original
    assert migrated is not legacy
    assert migration.migrate_relationship_dates(migrated) == migrated
    assert {record["@type"] for record in legacy} >= migration.RELATIONSHIPS
    for before, after in zip(legacy, migrated, strict=True):
        assert before["@id"] == after["@id"] and before["@type"] == after["@type"]
        if before["@type"] in migration.RELATIONSHIPS:
            assert {key: value for key, value in before.items() if key not in migration.OLD_DATES} == {
                key: value for key, value in after.items() if key not in migration.CURRENT_DATES
            }
            assert ("valid_from" in before) == ("start_date" in after)
            assert ("valid_to" in before) == ("end_date" in after)
        else:
            assert after == before


@pytest.mark.parametrize("start,end,expected_end", [
    ("2024-02-28", "2024-02-29", "2024-03-01"),
    ("2023-02-28", "2023-02-28", "2023-03-01"),
    ("2026-04-01", "2026-04-30", "2026-05-01"),
    ("2026-12-31", "2026-12-31", "2027-01-01"),
])
@pytest.mark.parametrize("kind", ["AnimalResponsibility", "PesticideApplicatorRole", "SeedOperatorRole"])
def test_inclusive_membership_of_every_day_is_preserved(kind, start, end, expected_end):
    before = {"@type": kind, "valid_from": start, "valid_to": end}
    after = convert(before)
    assert after["start_date"] == start and after["end_date"] == expected_end
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    for offset in range(-1, (last - first).days + 3):
        day = first + timedelta(days=offset)
        old_effective = first <= day <= last
        new_effective = date.fromisoformat(after["start_date"]) <= day < date.fromisoformat(after["end_date"])
        assert old_effective == new_effective


@pytest.mark.parametrize("patch,code,path", [
    ({"valid_from": "2026-07-02", "valid_to": "2026-07-01"}, "invalid-period", "/0"),
    ({"valid_to": "9999-12-31"}, "unrepresentable-end-date", "/0/valid_to"),
    ({"valid_to": "2026-02-30"}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": "2026-06"}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": "20260630"}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": "2026-06-30T23:59:59Z"}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": None}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": 20260630}, "invalid-calendar-date", "/0/valid_to"),
    ({"valid_to": "2026-06-30", "end_date": "2026-07-01"}, "mixed-date-pairs", "/0"),
    ({"start_date": "2026-07-01", "end_date": "2026-07-01"}, "invalid-period", "/0"),
])
def test_impossible_or_ambiguous_dates_fail_with_stable_field_diagnostics(patch, code, path):
    source = [{"@type": "AnimalResponsibility", **patch}]
    original = copy.deepcopy(source)
    with pytest.raises(migration.MigrationError) as first:
        convert(source)
    with pytest.raises(migration.MigrationError) as second:
        convert(source)
    assert source == original
    assert first.value.diagnostics == second.value.diagnostics
    assert first.value.diagnostics[0]["code"] == code
    assert first.value.diagnostics[0]["path"] == path


@pytest.mark.parametrize("boundary", [None, "unknown", "end-is-exclusive"])
def test_source_boundary_is_required_evidence(boundary):
    with pytest.raises(migration.MigrationError) as error:
        convert({"@type": "ProducerMembership", "valid_to": "2026-06-30"}, boundary)
    assert error.value.diagnostics[0]["code"] == "unknown-source-boundary"


def test_nested_exchange_is_all_or_nothing_and_missing_dates_are_not_invented():
    source = {"@graph": [
        {"@type": "AnimalResponsibility", "valid_from": "2026-01-01"},
        {"a/b~c": {"@type": "NameUsage", "valid_to": "2026"}},
    ]}
    original = copy.deepcopy(source)
    with pytest.raises(migration.MigrationError) as error:
        convert(source)
    assert source == original
    assert error.value.diagnostics[0]["path"] == "/@graph/1/a~1b~0c/valid_to"
    assert convert(source["@graph"][0]) == {"@type": "AnimalResponsibility", "start_date": "2026-01-01"}
    assert convert({"@type": "AnimalResponsibility"}) == {"@type": "AnimalResponsibility"}


@pytest.mark.parametrize("type_id", [
    "AnimalResidence", "publicschema:AnimalResidence", "https://publicschema.org/AnimalResidence",
    "agri/AnimalResidence", "publicschema:agri/AnimalResidence", "https://publicschema.org/agri/AnimalResidence",
    "agri/AgriculturalServiceRole", "agri/InputSupplierRole",
    "https://publicschema.org/agri/AgriculturalServiceRole", "https://publicschema.org/agri/InputSupplierRole",
    "AnimalResponsibility", "https://publicschema.org/AnimalResponsibility",
])
def test_exact_type_identifiers_are_preserved(type_id):
    assert convert({"@type": type_id, "valid_to": "2026-06-30"}) == {
        "@type": type_id, "end_date": "2026-07-01",
    }


@pytest.mark.parametrize("kind", ["PesticideApplicatorRole", "SeedOperatorRole"])
@pytest.mark.parametrize("prefix", [
    "", "publicschema:", "https://publicschema.org/", "agri/",
    "publicschema:agri/", "https://publicschema.org/agri/",
])
def test_inherited_roles_accept_exact_historical_and_current_type_identifiers(kind, prefix):
    type_id = prefix + kind
    assert convert({"@type": type_id, "valid_from": "2026-12-31", "valid_to": "2026-12-31"}) == {
        "@type": type_id, "start_date": "2026-12-31", "end_date": "2027-01-01",
    }


@pytest.mark.parametrize("type_id", [
    "https://unrelated.example/AnimalResidence", "alien:AnimalResidence",
    "https://publicschema.org/agri/AnimalResponsibility", "health/AnimalResidence",
    ["AnimalResidence", "AnimalResponsibility"],
])
def test_a_matching_local_name_does_not_establish_class_identity(type_id):
    with pytest.raises(migration.MigrationError) as error:
        convert({"@type": type_id, "valid_to": "2026-06-30"})
    assert error.value.diagnostics[0]["code"] == "unsupported-type-identifier"


@pytest.mark.parametrize("kind", ["PesticideApplicatorRole", "SeedOperatorRole"])
@pytest.mark.parametrize("prefix", ["https://unrelated.example/", "alien:", "health/"])
def test_inherited_roles_reject_foreign_namespaces(kind, prefix):
    with pytest.raises(migration.MigrationError) as error:
        convert({"@type": prefix + kind, "valid_to": "2026-06-30"})
    assert error.value.diagnostics[0]["code"] == "unsupported-type-identifier"


@pytest.mark.parametrize("kind", ["PesticideApplicatorRole", "SeedOperatorRole"])
def test_inherited_roles_require_source_boundary_and_reject_unrepresentable_end(kind):
    source = {"@type": kind, "valid_to": "9999-12-31"}
    with pytest.raises(migration.MigrationError) as error:
        convert(source, None)
    assert error.value.diagnostics[0]["code"] == "unknown-source-boundary"
    with pytest.raises(migration.MigrationError) as error:
        convert(source)
    assert error.value.diagnostics[0]["code"] == "unrepresentable-end-date"


@pytest.mark.parametrize("kind,code", [
    ("FacilityManagementAssignment", "ambiguous-facility-management"),
    ("FacilityAddressAssignment", "address-purpose-review-required"),
])
def test_retired_facility_assertions_need_source_meaning_review(kind, code):
    with pytest.raises(migration.MigrationError) as error:
        convert({"@type": kind, "valid_to": "2026-06-30"})
    assert error.value.diagnostics[0]["code"] == code


@pytest.mark.parametrize("kind,endpoint,meaning_field,code", [
    ("AssetPartyRole", "asset_actor", "asset_role_type", "upkeep"),
    ("AssetAddressAssignment", "assigned_address", "address_purpose", "postal"),
])
def test_only_explicitly_transformed_facility_facts_can_have_dates_converted(kind, endpoint, meaning_field, code):
    source = {"@type": kind, "asset_subject": "https://example.org/facility",
              endpoint: "https://example.org/endpoint", "valid_to": "2026-06-30"}
    with pytest.raises(migration.MigrationError) as error:
        convert(source)
    assert error.value.diagnostics[0]["code"] == "assignment-meaning-required"
    source[meaning_field] = {"@type": "CodedValue", "code_scheme": "https://example.org/reviewed-scheme", "code_value": code}
    converted = convert(source)
    assert converted["end_date"] == "2026-07-01" and converted[meaning_field] == source[meaning_field]
    source["addressed_facility"] = "https://example.org/facility"
    with pytest.raises(migration.MigrationError) as error:
        convert(source)
    assert error.value.diagnostics[0]["code"] == "incomplete-assignment-transformation"


def test_cli_never_rewrites_input_or_emits_a_partial_result(tmp_path, legacy):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(legacy))
    original = source.read_bytes()
    command = [sys.executable, str(EXAMPLES / "migrate.py"), str(source)]
    rejected = subprocess.run(command, text=True, capture_output=True, check=False)
    assert rejected.returncode == 2 and not rejected.stdout
    assert json.loads(rejected.stderr)["errors"][0]["code"] == "unknown-source-boundary"
    accepted = subprocess.run(command + ["--source-boundary", BOUNDARY], text=True, capture_output=True, check=False)
    assert accepted.returncode == 0 and not accepted.stderr
    assert json.loads(accepted.stdout) == convert(legacy)
    assert source.read_bytes() == original


def test_migrated_examples_validate_against_real_exports(tmp_path, legacy):
    result = build_vocabulary(ROOT / "schema")
    migrated = convert(legacy)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in result["concept_schemas"].values()
    )
    for record in migrated:
        jsonschema.Draft202012Validator(
            schema_for(result, record["@type"]), registry=registry,
            format_checker=jsonschema.FormatChecker(),
        ).validate(record)
    for kind in migration.RELATIONSHIPS:
        properties = schema_for(result, kind)["properties"]
        assert {"start_date", "end_date"} <= properties.keys()
        assert not {"valid_from", "valid_to"} & properties.keys()
    for kind in ("RegistryEntry", "Registration", "LandTenureAssertion", "RoadRestriction", "AgriculturalCertification"):
        properties = schema_for(result, kind)["properties"]
        assert {"valid_from", "valid_to"} <= properties.keys()
    graph = Graph().parse(data=json.dumps(jsonld.expand({
        "@context": result["context"]["@context"], "@graph": migrated,
    })), format="json-ld")
    for concept in result["concepts"].values():
        for parent in concept.get("supertypes", []):
            graph.add((URIRef(concept["uri"]), RDFS.subClassOf, URIRef(result["concepts"][parent]["uri"])))
    migrated_roots = {URIRef(result["context"]["@context"][kind]) for kind in (
        "HoldingParcelLink", "AnimalResidence", "AnimalResponsibility", "ProducerMembership",
        "AgriculturalServiceRole", "IdentifierAssignment", "NameUsage", "ContactPoint",
    )}
    for concept in result["concepts"].values():
        ancestors = set(graph.transitive_objects(URIRef(concept["uri"]), RDFS.subClassOf))
        if ancestors & migrated_roots:
            assert migration.TYPE_ALIASES.get(concept["uri"]) in migration.RELATIONSHIPS, concept["uri"]
    shapes = Graph().parse(write_shacl(tmp_path / "shapes.ttl"), format="turtle")
    conforms, _, report = validate(graph, shacl_graph=shapes, inference="rdfs")
    assert conforms, report
