"""Tests for the validation pipeline.

TDD: these tests define expected behavior before implementation.
"""

import pytest

from build.validate import validate_schema_dir, ValidationError
from tests.conftest import make_concept, make_property, make_vocabulary


# ---------------------------------------------------------------------------
# Happy path: valid schemas pass validation
# ---------------------------------------------------------------------------

class TestValidSchemas:
    def test_empty_schema_passes(self, tmp_schema):
        """A schema dir with no concepts/properties/vocabularies is valid."""
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_concept_with_properties_passes(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("given_name.yaml", make_property(id="given_name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["given_name"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_concept_with_domain_passes(
        self, tmp_schema, write_concept
    ):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_concept_with_null_domain_passes(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(
            id="Person", domain=None,
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_property_with_vocabulary_passes(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="gender-type",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_property_referencing_concept_passes(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("beneficiary.yaml", make_property(
            id="beneficiary", type="concept:Person", references="Person",
        ))
        write_concept("person.yaml", make_concept(id="Person"))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", properties=["beneficiary"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []


# ---------------------------------------------------------------------------
# YAML schema validation errors
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    def test_concept_missing_definition(self, tmp_schema, write_concept):
        data = make_concept()
        del data["definition"]
        write_concept("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("definition" in str(e) for e in errors)

    def test_concept_bad_id_format(self, tmp_schema, write_concept):
        write_concept("bad.yaml", make_concept(id="not_pascal"))
        errors = validate_schema_dir(tmp_schema)
        assert any("id" in str(e) for e in errors)

    def test_property_missing_type(self, tmp_schema, write_property, write_concept):
        data = make_property()
        del data["type"]
        write_property("bad.yaml", data)
        write_concept("person.yaml", make_concept(
            id="Person", properties=["test_field"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("type" in str(e) for e in errors)

    def test_property_bad_id_format(self, tmp_schema, write_property):
        write_property("bad.yaml", make_property(id="BadCase"))
        errors = validate_schema_dir(tmp_schema)
        assert any("id" in str(e) for e in errors)

    def test_vocabulary_missing_values(self, tmp_schema, write_vocabulary):
        data = make_vocabulary()
        del data["values"]
        write_vocabulary("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("values" in str(e) for e in errors)

    def test_vocabulary_with_sync_block_passes(self, tmp_schema, write_vocabulary):
        data = make_vocabulary()
        data["sync"] = {
            "source_url": "https://hl7.org/fhir/R4/codesystem-administrative-gender.json",
            "format": "fhir-codesystem",
            "last_synced": "2026-04-07",
        }
        write_vocabulary("synced.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_vocabulary_sync_block_requires_source_url(self, tmp_schema, write_vocabulary):
        data = make_vocabulary()
        data["sync"] = {"format": "fhir-codesystem"}
        write_vocabulary("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("source_url" in str(e) for e in errors)

    def test_property_bad_type_rejected(self, tmp_schema, write_property):
        write_property("bad.yaml", make_property(id="test_field", type="strng"))
        errors = validate_schema_dir(tmp_schema)
        assert any("type" in str(e) for e in errors)

    def test_vocabulary_duplicate_value_codes(self, tmp_schema, write_vocabulary):
        data = make_vocabulary()
        data["values"].append(data["values"][0].copy())  # duplicate first value
        write_vocabulary("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("Duplicate" in str(e) or "duplicate" in str(e) for e in errors)


# ---------------------------------------------------------------------------
# Referential integrity
# ---------------------------------------------------------------------------

class TestReferentialIntegrity:
    def test_concept_references_missing_property(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(
            id="Person", properties=["nonexistent_prop"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("nonexistent_prop" in str(e) for e in errors)

    def test_property_references_missing_vocabulary(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="nonexistent-vocab",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("nonexistent-vocab" in str(e) for e in errors)

    def test_property_references_missing_concept(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("beneficiary.yaml", make_property(
            id="beneficiary", references="NonexistentConcept",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", properties=["beneficiary"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("NonexistentConcept" in str(e) for e in errors)

    def test_orphaned_property_reported(self, tmp_schema, write_property):
        write_property("orphan.yaml", make_property(id="orphan"))
        errors = validate_schema_dir(tmp_schema)
        assert any("orphan" in str(e) for e in errors)


# ---------------------------------------------------------------------------
# Supertype / subtype relationships
# ---------------------------------------------------------------------------

class TestSupertypeSubtype:
    def test_concept_with_valid_supertypes_passes(
        self, tmp_schema, write_concept
    ):
        write_concept("group.yaml", make_concept(
            id="Group", subtypes=["Household"],
        ))
        write_concept("household.yaml", make_concept(
            id="Household", supertypes=["Group"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_concept_references_missing_supertype(
        self, tmp_schema, write_concept
    ):
        write_concept("household.yaml", make_concept(
            id="Household", supertypes=["Nonexistent"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("Nonexistent" in str(e) for e in errors)

    def test_concept_references_missing_subtype(
        self, tmp_schema, write_concept
    ):
        write_concept("group.yaml", make_concept(
            id="Group", subtypes=["Nonexistent"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("Nonexistent" in str(e) for e in errors)

    def test_supertype_subtype_symmetry_required(
        self, tmp_schema, write_concept
    ):
        """If A lists B as supertype, B must list A as subtype."""
        write_concept("group.yaml", make_concept(
            id="Group", subtypes=[],
        ))
        write_concept("household.yaml", make_concept(
            id="Household", supertypes=["Group"],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert any("symmetry" in str(e).lower() or "does not list" in str(e) for e in errors)


# ---------------------------------------------------------------------------
# Multilingual completeness
# ---------------------------------------------------------------------------

class TestMultilingualCompleteness:
    def test_concept_missing_french_definition(self, tmp_schema, write_concept):
        data = make_concept()
        del data["definition"]["fr"]
        write_concept("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("fr" in str(e) for e in errors)

    def test_vocabulary_value_missing_translation_is_ok(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values only require English (synced sources lack translations)."""
        data = make_vocabulary()
        del data["values"][0]["label"]["es"]
        del data["values"][0]["label"]["fr"]
        write_vocabulary("ok.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_vocabulary_value_missing_english_label_fails(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values must have at least an English label."""
        data = make_vocabulary()
        del data["values"][0]["label"]["en"]
        write_vocabulary("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("en" in str(e) for e in errors)

    def test_vocabulary_definition_still_requires_all_languages(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary-level definitions still require all configured languages."""
        data = make_vocabulary()
        del data["definition"]["fr"]
        write_vocabulary("bad.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert any("fr" in str(e) for e in errors)
