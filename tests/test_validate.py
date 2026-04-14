"""Tests for the validation pipeline.

TDD: these tests define expected behavior before implementation.
"""

import yaml

from build.validate import validate_schema_dir
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

    def test_property_geojson_geometry_type_passes(
        self, tmp_schema, write_property, write_concept
    ):
        """geojson_geometry is a valid property type."""
        write_property("geom.yaml", make_property(id="geom", type="geojson_geometry"))
        write_concept("area.yaml", make_concept(id="Area", properties=["geom"]))
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

    def test_vocabulary_with_hierarchical_values_passes(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values with level and parent_code pass validation."""
        data = make_vocabulary()
        data["values"] = [
            {
                "code": "managers",
                "label": {"en": "Managers"},
                "standard_code": "1",
                "level": 1,
            },
            {
                "code": "chief_executives",
                "label": {"en": "Chief executives"},
                "standard_code": "11",
                "level": 2,
                "parent_code": "1",
            },
        ]
        write_vocabulary("hierarchical.yaml", data)
        errors = validate_schema_dir(tmp_schema)
        assert errors == []

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
    def test_draft_concept_missing_french_is_warning(self, tmp_schema, write_concept):
        """Draft concepts produce warnings (not errors) for missing non-English translations."""
        data = make_concept(maturity="draft")
        del data["definition"]["fr"]
        write_concept("warn.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        fr_issues = [e for e in issues if "fr" in str(e)]
        assert len(fr_issues) == 1
        assert fr_issues[0].severity == "warning"

    def test_candidate_concept_missing_french_is_error(self, tmp_schema, write_concept):
        """Candidate concepts produce errors for missing translations."""
        data = make_concept(maturity="candidate")
        del data["definition"]["fr"]
        write_concept("bad.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        fr_issues = [e for e in issues if "fr" in str(e) and e.severity == "error"]
        assert len(fr_issues) == 1

    def test_normative_concept_missing_french_is_error(self, tmp_schema, write_concept):
        """Normative concepts produce errors for missing translations."""
        data = make_concept(maturity="normative")
        del data["definition"]["fr"]
        write_concept("bad.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        fr_issues = [e for e in issues if "fr" in str(e) and e.severity == "error"]
        assert len(fr_issues) == 1

    def test_draft_concept_missing_english_is_error(self, tmp_schema, write_concept):
        """Even draft concepts require English."""
        data = make_concept(maturity="draft")
        del data["definition"]["en"]
        write_concept("bad.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        en_errors = [e for e in issues if "en" in str(e) and e.severity == "error"]
        assert len(en_errors) >= 1

    def test_draft_property_missing_spanish_is_warning(
        self, tmp_schema, write_property, write_concept
    ):
        """Draft properties produce warnings for missing non-English translations."""
        data = make_property(maturity="draft")
        del data["definition"]["es"]
        write_property("warn.yaml", data)
        write_concept("person.yaml", make_concept(
            id="Person", properties=["test_field"],
        ))
        issues = validate_schema_dir(tmp_schema)
        es_issues = [e for e in issues if "es" in str(e)]
        assert len(es_issues) == 1
        assert es_issues[0].severity == "warning"

    def test_vocabulary_value_missing_translation_is_ok(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values only require English (synced sources lack translations)."""
        data = make_vocabulary()
        del data["values"][0]["label"]["es"]
        del data["values"][0]["label"]["fr"]
        write_vocabulary("ok.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        errors = [e for e in issues if e.severity == "error"]
        assert errors == []

    def test_vocabulary_value_missing_english_label_fails(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values must have at least an English label."""
        data = make_vocabulary()
        del data["values"][0]["label"]["en"]
        write_vocabulary("bad.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        assert any("en" in str(e) and e.severity == "error" for e in issues)

    def test_draft_vocabulary_definition_missing_french_is_warning(
        self, tmp_schema, write_vocabulary
    ):
        """Draft vocabulary definitions produce warnings for missing non-English translations."""
        data = make_vocabulary(maturity="draft")
        del data["definition"]["fr"]
        write_vocabulary("warn.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        fr_issues = [e for e in issues if "fr" in str(e)]
        assert len(fr_issues) == 1
        assert fr_issues[0].severity == "warning"

    def test_candidate_vocabulary_definition_missing_french_is_error(
        self, tmp_schema, write_vocabulary
    ):
        """Candidate vocabulary definitions require all configured languages."""
        data = make_vocabulary(maturity="candidate")
        del data["definition"]["fr"]
        write_vocabulary("bad.yaml", data)
        issues = validate_schema_dir(tmp_schema)
        fr_errors = [e for e in issues if "fr" in str(e) and e.severity == "error"]
        assert len(fr_errors) == 1


# ---------------------------------------------------------------------------
# Property groups validation
# ---------------------------------------------------------------------------

class TestPropertyGroups:
    def _write_categories(self, tmp_schema, categories=None):
        """Write categories.yaml to tmp schema."""
        import yaml
        if categories is None:
            categories = {
                "demographics": {"label": {"en": "Demographics"}},
                "identity": {"label": {"en": "Identity"}},
                "other": {"label": {"en": "Other"}},
            }
        (tmp_schema / "categories.yaml").write_text(
            yaml.dump(categories, allow_unicode=True)
        )

    def test_valid_property_groups_pass(
        self, tmp_schema, write_concept, write_property
    ):
        """Concept with valid property_groups passes validation."""
        self._write_categories(tmp_schema)
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob", "name"],
            property_groups=[
                {"category": "demographics", "properties": ["dob"]},
                {"category": "identity", "properties": ["name"]},
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        assert not any("property_groups" in str(e) for e in errors)

    def test_property_groups_with_inherited_pass(
        self, tmp_schema, write_concept, write_property
    ):
        """property_groups that include inherited properties pass."""
        self._write_categories(tmp_schema)
        write_property("name.yaml", make_property(id="name"))
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("party.yaml", make_concept(
            id="Party", properties=["name"], subtypes=["Person"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob"],
            supertypes=["Party"],
            property_groups=[
                {"category": "identity", "properties": ["name"]},
                {"category": "demographics", "properties": ["dob"]},
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        prop_group_errors = [e for e in errors if "property_groups" in str(e)]
        assert prop_group_errors == []

    def test_missing_own_property_in_groups_is_error(
        self, tmp_schema, write_concept, write_property
    ):
        """Own property not in any group is an error."""
        self._write_categories(tmp_schema)
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob", "name"],
            property_groups=[
                {"category": "demographics", "properties": ["dob"]},
                # name is missing from groups
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        missing_errors = [e for e in errors if "missing properties" in str(e)]
        assert len(missing_errors) == 1
        assert "name" in str(missing_errors[0])

    def test_missing_inherited_property_in_groups_is_error(
        self, tmp_schema, write_concept, write_property
    ):
        """Inherited property not in any group is an error."""
        self._write_categories(tmp_schema)
        write_property("name.yaml", make_property(id="name"))
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("party.yaml", make_concept(
            id="Party", properties=["name"], subtypes=["Person"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob"],
            supertypes=["Party"],
            property_groups=[
                {"category": "demographics", "properties": ["dob"]},
                # name (inherited from Party) is missing
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        missing_errors = [e for e in errors if "missing properties" in str(e)]
        assert len(missing_errors) == 1
        assert "name" in str(missing_errors[0])

    def test_invalid_category_reference_is_error(
        self, tmp_schema, write_concept, write_property
    ):
        """Category ID not in categories.yaml is an error."""
        self._write_categories(tmp_schema)
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob"],
            property_groups=[
                {"category": "nonexistent_cat", "properties": ["dob"]},
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        cat_errors = [e for e in errors if "nonexistent_cat" in str(e)]
        assert len(cat_errors) == 1

    def test_undefined_property_in_groups_is_error(
        self, tmp_schema, write_concept, write_property
    ):
        """Property in groups that doesn't exist in properties/ is an error."""
        self._write_categories(tmp_schema)
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob"],
            property_groups=[
                {"category": "demographics", "properties": ["dob", "nonexistent"]},
            ],
        ))
        errors = validate_schema_dir(tmp_schema)
        ref_errors = [e for e in errors if "nonexistent" in str(e) and "property_groups" in str(e)]
        assert len(ref_errors) == 1


# ---------------------------------------------------------------------------
# age_applicability bibliography cross-check
# ---------------------------------------------------------------------------

class TestAgeApplicability:
    """age_applicability must cover the bands implied by WG/CFM citations."""

    def _write_bibliography(self, tmp_schema, filename, data):
        path = tmp_schema / "bibliography"
        path.mkdir(exist_ok=True)
        (path / filename).write_text(yaml.dump(data, allow_unicode=True))

    def test_wg_ss_citation_without_adult_band_fails(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("difficulty_seeing.yaml", make_property(
            id="difficulty_seeing", age_applicability=["child_5_17"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["difficulty_seeing"],
        ))
        self._write_bibliography(tmp_schema, "wg-ss.yaml", {
            "id": "washington-group-ss",
            "title": "WG-SS",
            "publisher": "WG",
            "type": "international_standard",
            "domain": "general",
            "status": "active",
            "informs": {"properties": ["difficulty_seeing"]},
        })
        errors = validate_schema_dir(tmp_schema)
        band_errors = [
            e for e in errors
            if "age_applicability" in str(e) and "adult" in str(e)
        ]
        assert len(band_errors) == 1

    def test_wg_es_citation_with_adult_band_passes(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("fatigue_frequency.yaml", make_property(
            id="fatigue_frequency", age_applicability=["adult"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["fatigue_frequency"],
        ))
        self._write_bibliography(tmp_schema, "wg-es.yaml", {
            "id": "washington-group-es",
            "title": "WG-ES",
            "publisher": "WG",
            "type": "international_standard",
            "domain": "general",
            "status": "active",
            "informs": {"properties": ["fatigue_frequency"]},
        })
        errors = validate_schema_dir(tmp_schema)
        band_errors = [e for e in errors if "age_applicability" in str(e)]
        assert band_errors == []

    def test_cfm_citation_without_child_band_fails(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("difficulty_playing.yaml", make_property(
            id="difficulty_playing", age_applicability=["adult"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["difficulty_playing"],
        ))
        self._write_bibliography(tmp_schema, "cfm.yaml", {
            "id": "washington-group-cfm",
            "title": "CFM",
            "publisher": "WG/UNICEF",
            "type": "international_standard",
            "domain": "general",
            "status": "active",
            "informs": {"properties": ["difficulty_playing"]},
        })
        errors = validate_schema_dir(tmp_schema)
        band_errors = [
            e for e in errors
            if "age_applicability" in str(e) and "child band" in str(e)
        ]
        assert len(band_errors) == 1

    def test_cfm_citation_narrowed_to_single_child_band_passes(
        self, tmp_schema, write_concept, write_property
    ):
        """CFM items may apply to only one child variant (e.g. difficulty_playing is 2-4 only)."""
        write_property("difficulty_playing.yaml", make_property(
            id="difficulty_playing", age_applicability=["child_2_4"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["difficulty_playing"],
        ))
        self._write_bibliography(tmp_schema, "cfm.yaml", {
            "id": "washington-group-cfm",
            "title": "CFM",
            "publisher": "WG/UNICEF",
            "type": "international_standard",
            "domain": "general",
            "status": "active",
            "informs": {"properties": ["difficulty_playing"]},
        })
        errors = validate_schema_dir(tmp_schema)
        band_errors = [e for e in errors if "age_applicability" in str(e)]
        assert band_errors == []

    def test_invalid_age_band_value_fails_schema(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("prop.yaml", make_property(
            id="prop", age_applicability=["toddler"],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["prop"],
        ))
        errors = validate_schema_dir(tmp_schema)
        enum_errors = [e for e in errors if "toddler" in str(e)]
        assert len(enum_errors) == 1
