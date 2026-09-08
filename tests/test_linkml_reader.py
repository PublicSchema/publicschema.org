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

import json

import pytest
import yaml

from build.build import build_vocabulary
from build.linkml_reader import (
    _bespoke_id_and_domain_from_class,
    _convert_class_to_concept,
    _convert_enum_to_vocabulary,
    _convert_slot_to_property,
    _parse_json_annotation,
    load_raw_from_linkml,
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


@pytest.mark.parametrize("base_uri", ["https://publicschema.org/", "https://registry.example/schema/"])
def test_authored_property_namespace_survives_a_consumer_domain_change(tmp_path, base_uri):
    """A root date stays root and a sector fact stays scoped when consumers move."""
    definition = {
        "id": base_uri + "linkml/test", "name": "test", "default_prefix": "product",
        "prefixes": {"product": base_uri},
        "classes": {
            "Premises": {
                "class_uri": "product:Premises", "title": "Premises",
                "slots": ["observed_on", "cultivation_kind"],
            },
        },
        "slots": {
            "observed_on": {
                "slot_uri": "product:observed_on", "range": "date",
                "annotations": {"domain_override": "health"},
            },
            "cultivation_kind": {
                "slot_uri": "product:agri/cultivation_kind", "range": "string",
                "annotations": {"domain_override": "null"},
            },
        },
        "annotations": {"domains_json": json.dumps({
            "agri": {"label": {"en": "Agriculture", "fr": "Agriculture"}},
            "health": {"label": {"en": "Health"}},
        })},
    }
    source = tmp_path / "publicschema.yaml"
    for consumer_uri in ("product:Premises", "product:health/Premises"):
        definition["classes"]["Premises"]["class_uri"] = consumer_uri
        source.write_text(yaml.safe_dump(definition))
        built = build_vocabulary(tmp_path)
        shared = built["properties"]["observed_on"]
        scoped = built["properties"]["cultivation_kind"]
        assert (shared["uri"], shared["path"], shared["domain"]) == (
            base_uri + "observed_on", "/observed_on", None,
        )
        assert (scoped["uri"], scoped["path"], scoped["domain"]) == (
            base_uri + "agri/cultivation_kind", "/agri/cultivation_kind", "agri",
        )
        assert built["context"]["@context"]["observed_on"]["@id"] == shared["uri"]
        assert built["context"]["@context"]["cultivation_kind"] == scoped["uri"]
        assert list(built["meta"]["domains"]) == ["agri", "health"]
        assert built["meta"]["domains"]["agri"]["label"]["fr"] == "Agriculture"


# ---------------------------------------------------------------------------
# Fix 1: subtypes reconstruction must not use fuzzy short-name fallback
# ---------------------------------------------------------------------------


class TestSubtypesFuzzyMatchRemoved:
    """The subtypes reconstruction loop must match parent references only by
    exact composite key. The short-name fallback (``short_name[cand_key] ==
    parent_short``) can attach a child to the wrong parent when two concepts
    share a bare name across domains (e.g. ``crvs/Person`` and a bare
    ``Person``).

    This test drives ``load_raw_from_linkml`` against a minimal in-memory
    fixture (written to a temp directory) that has exactly this collision,
    then asserts ``crvs/Person`` does NOT gain a subtype that references
    only the bare name.
    """

    def test_domain_scoped_parent_not_matched_by_bare_name(self, tmp_path):
        # The subtypes reconstruction loop must use exact composite-key
        # matching only. The scenario here has:
        # - ``CrvsPerson`` (composite key ``crvs/Person``)
        # - ``Person``     (composite key ``Person``, a distinct root concept)
        # - ``Child``      (composite key ``Child``) whose is_a is bare ``Person``
        #
        # The two-pass resolution rewrites Child's supertypes to ``["Person"]``
        # (bare, because bare ``Person`` exists as a direct composite key).
        # The subtypes loop must then add ``Child`` to bare ``Person``'s
        # subtypes — NOT to ``crvs/Person``'s subtypes. Before the fix the
        # fuzzy fallback would also add Child to ``crvs/Person`` because both
        # share the bare name ``Person``.
        domain_yaml = """
id: https://publicschema.org/schema
name: publicschema
prefixes:
  publicschema: https://publicschema.org/
classes:
  CrvsPerson:
    class_uri: publicschema:crvs/Person
    title: Person (CRVS)
    description: A person in CRVS.
  Person:
    class_uri: publicschema:Person
    title: Person
    description: A generic person.
  Child:
    class_uri: publicschema:Child
    title: Child
    description: A child entity.
    is_a: Person
"""
        schema_dir = tmp_path / "schema"
        schema_dir.mkdir()
        (schema_dir / "publicschema.yaml").write_text(
            "id: test\nname: test\nimports: [domain]\n"
        )
        (schema_dir / "domain.yaml").write_text(domain_yaml)

        result = load_raw_from_linkml(schema_dir)
        concepts = result["concepts"]

        assert "crvs/Person" in concepts
        assert "Person" in concepts
        assert "Child" in concepts

        # Child's is_a resolves to bare ``Person`` (direct composite-key hit
        # takes priority over domain-scoped candidate in _resolve_super).
        # Therefore Child must appear in bare Person's subtypes ...
        assert "Child" in concepts["Person"].get("subtypes", [])
        # ... and must NOT appear in crvs/Person's subtypes (the fuzzy
        # short-name fallback was the only path that caused this).
        crvs_person_subtypes = concepts["crvs/Person"].get("subtypes", [])
        assert "Child" not in crvs_person_subtypes, (
            "Fuzzy short-name fallback incorrectly attached Child to crvs/Person"
        )


# ---------------------------------------------------------------------------
# Fix 2: self_ PV key with no standard_code must not strip the trailing _
# ---------------------------------------------------------------------------


class TestSelfUnderscoreRoundtrip:
    """A PermissibleValue keyed ``self_`` with no ``standard_code`` annotation
    should round-trip as ``display_code == "self_"``.

    Before the fix the else branch always ran ``code[:-1] if code == "self_"``
    so a missing ``standard_code`` would produce ``"self"`` instead of ``"self_"``.
    """

    def test_self_underscore_no_standard_code_roundtrips(self):
        enum_def = {
            "permissible_values": {
                "self_": {
                    "title": "Self",
                    # No standard_code annotation: the PV key is canonical.
                },
            },
        }
        result = _convert_enum_to_vocabulary("MaritalStatus", enum_def)
        assert result is not None
        _, vocab = result
        values = vocab["values"]
        assert len(values) == 1
        assert values[0]["code"] == "self_", (
            f"Expected 'self_' but got {values[0]['code']!r}"
        )

    def test_self_underscore_with_standard_code_self_strips(self):
        # When standard_code is ``self`` (the Python keyword) and the PV
        # key is ``self_`` (the slug), the mangling logic should fire and
        # set display_code to ``"self"`` (the original).
        enum_def = {
            "permissible_values": {
                "self_": {
                    "title": "Self",
                    "annotations": {"standard_code": "self"},
                },
            },
        }
        result = _convert_enum_to_vocabulary("MaritalStatus", enum_def)
        assert result is not None
        _, vocab = result
        values = vocab["values"]
        assert len(values) == 1
        assert values[0]["code"] == "self", (
            f"Expected 'self' but got {values[0]['code']!r}"
        )


# ---------------------------------------------------------------------------
# Fix 3: _parse_json_annotation must warn and return None on parse failure
# ---------------------------------------------------------------------------


class TestParseJsonAnnotationWarnsOnBadJson:
    """When _parse_json_annotation receives a string that is not valid JSON,
    it must emit a warning to stderr and return ``None`` instead of the raw
    string. Callers guard with ``if parsed is not None`` so returning the raw
    string would silently corrupt structured fields.
    """

    def test_invalid_json_returns_none(self):
        result = _parse_json_annotation("{not valid json")
        assert result is None

    def test_invalid_json_emits_stderr_warning(self, capsys):
        _parse_json_annotation("{not valid json")
        captured = capsys.readouterr()
        assert captured.err, "Expected a warning on stderr for bad JSON"

    def test_valid_json_returns_parsed(self):
        result = _parse_json_annotation('{"key": "value"}')
        assert result == {"key": "value"}

    def test_none_input_returns_none(self):
        result = _parse_json_annotation(None)
        assert result is None

    def test_non_string_non_dict_passes_through(self):
        # Integers and booleans are valid annotation scalars; pass through.
        assert _parse_json_annotation(42) == 42
        assert _parse_json_annotation(True) is True

    def test_plain_scalar_string_returns_none_with_warning(self, capsys):
        # A plain non-JSON word (e.g. a bare string that should have been
        # JSON-encoded) must also warn and return None so callers don't
        # accidentally use it as a structured value.
        _parse_json_annotation("not-json-at-all")
        captured = capsys.readouterr()
        assert captured.err
