"""Public vocabulary codes survive LinkML naming and export."""

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from build.build import build_vocabulary
from build.linkml_reader import _convert_enum_to_vocabulary
from build.migrate_to_linkml import (
    MigrationContext,
    SourceFile,
    SystemRegistry,
    convert_vocabulary,
)


@pytest.mark.parametrize("code", ["self", "self_"])
def test_migration_preserves_escaped_and_literal_self_codes(code):
    source = SourceFile(
        path=Path("schema/vocabularies/delegation-type.yaml"),
        kind="vocabulary", id="delegation-type", key="delegation-type",
        data={"id": "delegation-type", "values": [{"code": code}]},
    )
    context = MigrationContext(
        inv={}, concepts={}, properties={}, vocabularies={source.key: source},
        by_kind={}, systems=SystemRegistry(systems={}, vocab_prefixes={}),
    )
    name, enum = convert_vocabulary(source, context)
    _, vocabulary = _convert_enum_to_vocabulary(name, enum)
    assert vocabulary["values"][0]["code"] == code


@pytest.mark.parametrize("property_id", ["delegation_type", "administration_mode"])
def test_real_instance_schemas_accept_original_self_code(real_schema, property_id):
    result = build_vocabulary(raws=real_schema)
    schemas = [schema for schema in result["concept_schemas"].values()
               if property_id in schema["properties"]]
    assert schemas, f"No instance schema uses {property_id}"
    for schema in schemas:
        validator = Draft202012Validator(schema)
        assert not list(validator.iter_errors({property_id: "self"}))
        assert list(validator.iter_errors({property_id: "self_"}))
