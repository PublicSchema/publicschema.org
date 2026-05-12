"""Focused regression tests for build.linkml_reader fixes that recovered
data the LinkML cutover (commit d594bf7) silently dropped.

These exercise three narrow converter paths directly:

1. ``class_uri: publicschema:<domain>/<BareId>`` parsing — the LinkML
   class name (e.g. ``CrvsPerson``) fuses domain + bare id; the bespoke
   catalog stores it as bare ``Person`` under domain ``crvs``.

2. ``bespoke_type:`` annotation override on a slot — required for cases
   where the LinkML range can't express the bespoke type directly,
   e.g. ``geojson_geometry`` on a ``range: string`` slot.

3. ``domain_override: "null"`` string sentinel — distinguishes "no
   override" (key absent) from "explicit universal" (key present with
   value ``None``). LinkML annotations can't carry a real ``None``, so
   the literal string ``"null"`` decodes to Python ``None``.

The full end-to-end behavior is already covered by
``tests/test_crvs_domain.py`` and ``tests/test_domain_keying.py`` against
the real schema; these tests pin the converter contracts so a future
refactor can't regress them without a clear unit-level failure.
"""

from __future__ import annotations

from build.linkml_reader import (
    _bespoke_id_and_domain_from_class,
    _convert_class_to_concept,
    _convert_slot_to_property,
)


# ---------------------------------------------------------------------------
# 1. class_uri: publicschema:<domain>/<BareId> parsing
# ---------------------------------------------------------------------------


class TestClassUriDomainQualification:
    def test_domain_qualified_class_uri_yields_bare_id_and_domain(self):
        bare, domain = _bespoke_id_and_domain_from_class(
            "CrvsPerson", "publicschema:crvs/Person", annotation_domain=None,
        )
        assert bare == "Person"
        assert domain == "crvs"

    def test_unqualified_class_uri_falls_back_to_linkml_name(self):
        bare, domain = _bespoke_id_and_domain_from_class(
            "Person", "publicschema:Person", annotation_domain=None,
        )
        assert bare == "Person"
        assert domain is None

    def test_unqualified_uri_uses_source_domain_annotation(self):
        bare, domain = _bespoke_id_and_domain_from_class(
            "Program", "publicschema:Program", annotation_domain="sp",
        )
        assert bare == "Program"
        assert domain == "sp"

    def test_uri_domain_overrides_source_domain_annotation(self):
        # If both are present, the URI wins (it's the canonical source).
        bare, domain = _bespoke_id_and_domain_from_class(
            "CrvsPerson", "publicschema:crvs/Person",
            annotation_domain="civil_status",
        )
        assert bare == "Person"
        assert domain == "crvs"

    def test_convert_class_to_concept_uses_uri_domain(self):
        cls_def = {
            "class_uri": "publicschema:crvs/Person",
            "title": "Person",
            "description": "A person registered in CRVS.",
            "annotations": {"source_domain": "crvs"},
        }
        result = _convert_class_to_concept("CrvsPerson", cls_def)
        assert result is not None
        composite_key, concept = result
        assert composite_key == "crvs/Person"
        assert concept["id"] == "Person"
        assert concept["domain"] == "crvs"


# ---------------------------------------------------------------------------
# 2. bespoke_type annotation override on slots
# ---------------------------------------------------------------------------


class TestBespokeTypeOverride:
    def test_bespoke_type_overrides_inferred_range_type(self):
        slot_def = {
            "range": "string",
            "annotations": {"bespoke_type": "geojson_geometry"},
        }
        _, prop = _convert_slot_to_property(
            "geometry", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        assert prop["type"] == "geojson_geometry"

    def test_bespoke_type_overrides_class_range_but_preserves_references(self):
        # When a slot's ``range`` is a class but a ``bespoke_type``
        # annotation overrides to a scalar (e.g. ``uri``), the
        # ``references`` link to the class is still recorded so the site
        # can still render the cross-link.
        slot_def = {
            "range": "Program",
            "annotations": {"bespoke_type": "uri"},
        }
        _, prop = _convert_slot_to_property(
            "program_ref", slot_def,
            enum_to_vocab_key={}, class_names={"Program"},
        )
        assert prop["type"] == "uri"
        assert prop["references"] == "Program"

    def test_full_linkml_annotation_form_unwraps_bespoke_type(self):
        # LinkML annotations can appear in either compact form (key: value)
        # or full form ({tag, value}). Both must decode the same.
        slot_def = {
            "range": "string",
            "annotations": {
                "bespoke_type": {"tag": "bespoke_type", "value": "geojson_geometry"},
            },
        }
        _, prop = _convert_slot_to_property(
            "geometry", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        assert prop["type"] == "geojson_geometry"

    def test_no_bespoke_type_leaves_inferred_type_intact(self):
        slot_def = {"range": "integer"}
        _, prop = _convert_slot_to_property(
            "count", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        # LINKML_RANGE_TO_BESPOKE_TYPE maps integer -> integer.
        assert prop["type"] == "integer"


# ---------------------------------------------------------------------------
# 3. domain_override: "null" string sentinel decoding
# ---------------------------------------------------------------------------


class TestDomainOverrideSentinel:
    def test_string_null_sentinel_decodes_to_python_none(self):
        slot_def = {
            "range": "string",
            "annotations": {"domain_override": "null"},
        }
        _, prop = _convert_slot_to_property(
            "applicant", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        # The key must be present (signals "explicit universal") with value None.
        assert "domain_override" in prop
        assert prop["domain_override"] is None

    def test_yaml_null_value_omits_domain_override(self):
        # YAML null on the annotation key means "no override at all": the
        # bespoke shape distinguishes this from the "null" sentinel by
        # omitting the key entirely.
        slot_def = {
            "range": "string",
            "annotations": {"domain_override": None},
        }
        _, prop = _convert_slot_to_property(
            "applicant", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        assert "domain_override" not in prop

    def test_non_null_string_passes_through(self):
        slot_def = {
            "range": "string",
            "annotations": {"domain_override": "sp"},
        }
        _, prop = _convert_slot_to_property(
            "applicant", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        assert prop["domain_override"] == "sp"

    def test_string_null_sentinel_in_full_annotation_form(self):
        slot_def = {
            "range": "string",
            "annotations": {
                "domain_override": {"tag": "domain_override", "value": "null"},
            },
        }
        _, prop = _convert_slot_to_property(
            "applicant", slot_def,
            enum_to_vocab_key={}, class_names=set(),
        )
        assert "domain_override" in prop
        assert prop["domain_override"] is None
