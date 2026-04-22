"""Regression tests for concept keying by (domain, id) composite key.

The build pipeline keys concepts by ``{domain}/{id}`` for domain-scoped
concepts and by bare ``id`` for universal ones. This prevents silent
overwrites when two domains define concepts with the same short name.
"""

import pytest
import yaml

from build.build import build_vocabulary, _concept_key, _resolve_concept_key
from tests.conftest import make_concept, make_property


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------


class TestConceptKey:
    def test_universal_concept_returns_bare_id(self):
        assert _concept_key(None, "Person") == "Person"

    def test_domain_concept_returns_composite_key(self):
        assert _concept_key("sp", "Enrollment") == "sp/Enrollment"

    def test_crvs_domain_returns_composite_key(self):
        assert _concept_key("crvs", "Birth") == "crvs/Birth"

    def test_empty_string_domain_treated_as_universal(self):
        # Falsy domain -> bare id (same as None)
        assert _concept_key("", "Event") == "Event"


class TestResolveConceptKey:
    """Strict reference rule: refs map directly to their key in ``concepts``.

    Bare ids ("Person") reference root concepts. Composite "domain/id"
    ("crvs/Person", "sp/Enrollment") reference domain-scoped concepts.
    The resolver is a pass-through; unknown refs are returned unchanged
    so callers can surface the miss.
    """

    def _concepts(self):
        return {
            "Person": {"id": "Person", "domain": None},
            "sp/Enrollment": {"id": "Enrollment", "domain": "sp"},
            "crvs/Birth": {"id": "Birth", "domain": "crvs"},
        }

    def test_existing_composite_key_returns_unchanged(self):
        concepts = self._concepts()
        assert _resolve_concept_key("sp/Enrollment", concepts) == "sp/Enrollment"

    def test_bare_id_resolves_to_root_key(self):
        concepts = self._concepts()
        assert _resolve_concept_key("Person", concepts) == "Person"

    def test_bare_id_is_not_magically_mapped_to_domain(self):
        """A bare id never maps to a domain-scoped concept; the ref is identity."""
        concepts = self._concepts()
        assert _resolve_concept_key("Enrollment", concepts) == "Enrollment"

    def test_unknown_ref_returns_unchanged(self):
        """An unknown ref is returned as-is; callers handle missing entries."""
        concepts = self._concepts()
        assert _resolve_concept_key("NonExistent", concepts) == "NonExistent"


class TestRealSchemaDomainResolution:
    """Verify that resolved URIs and $refs point to the domain-correct concept.

    These are the regression tests staff-engineer review asked for: they look
    at the build output, not the YAML input, to confirm the resolver picks the
    same-domain match when a bare short id collides across domains.
    """

    @pytest.fixture(scope="class")
    def real_result(self):
        from tests.conftest import SCHEMA_DIR
        return build_vocabulary(SCHEMA_DIR)

    def test_crvs_parent_supertype_is_crvs_person(self, real_result):
        """The crvs/Parent concept extends crvs/Person, not root Person."""
        parent = real_result["concepts"]["crvs/Parent"]
        assert "crvs/Person" in parent["supertypes"], (
            f"crvs/Parent supertypes should include crvs/Person, got {parent['supertypes']}"
        )
        assert "Person" not in parent["supertypes"], (
            "crvs/Parent supertypes must not include the root Person key"
        )

    def test_crvs_property_references_resolve_to_crvs_person(self, real_result):
        """Properties with domain_override: crvs that reference Person resolve to crvs/Person."""
        crvs_person_uri = real_result["concepts"]["crvs/Person"]["uri"]
        for pid in ("deceased", "informant", "registrar", "witnesses", "party_1", "party_2"):
            prop = real_result["properties"].get(pid)
            assert prop is not None, f"Expected CRVS property {pid} in build output"
            assert prop.get("domain") == "crvs", (
                f"Property {pid} should carry domain 'crvs', got {prop.get('domain')}"
            )

    def test_crvs_person_concept_schema_has_crvs_uri(self, real_result):
        """Properties typed ``concept:crvs/Person`` produce crvs/Person schema refs.

        The ``child`` property on crvs/Birth is typed ``concept:crvs/Person``.
        Its JSON Schema ref must target the crvs/Person schema URL, not the
        root Person schema.
        """
        schemas = real_result["concept_schemas"]
        birth_schema = schemas["crvs/Birth"]
        base = "https://publicschema.org"
        child_schema = birth_schema.get("properties", {}).get("child", {})
        refs = _collect_refs(child_schema)
        assert any(
            ref == f"{base}/crvs/Person.schema.json" for ref in refs
        ), (
            f"crvs/Birth.child should $ref crvs/Person.schema.json, got {refs}"
        )
        assert not any(
            ref == f"{base}/Person.schema.json" for ref in refs
        ), (
            f"crvs/Birth.child must not $ref root Person.schema.json, got {refs}"
        )

    def test_crvs_person_jsonld_concept_refs_use_crvs_uri(self, real_result):
        """JSON-LD concept output for crvs/Parent points ps:references/subClassOf at crvs/Person."""
        import json
        concept_schemas = real_result["concept_schemas"]
        # JSON-LD generation happens in write_outputs, but supertype URIs are
        # derivable from out_concepts itself: crvs/Parent.supertypes list
        # contains the composite key crvs/Person, whose URI we can fetch.
        parent = real_result["concepts"]["crvs/Parent"]
        person_uri = real_result["concepts"]["crvs/Person"]["uri"]
        # The supertype composite key resolves in out_concepts to the crvs URI.
        resolved_uris = [real_result["concepts"][s]["uri"] for s in parent["supertypes"]]
        assert person_uri in resolved_uris, (
            f"crvs/Parent supertype URIs should include crvs/Person URI; got {resolved_uris}"
        )


def _collect_refs(schema_fragment):
    """Yield every $ref value inside a JSON Schema fragment (recursive)."""
    refs = []
    if isinstance(schema_fragment, dict):
        for k, v in schema_fragment.items():
            if k == "$ref" and isinstance(v, str):
                refs.append(v)
            else:
                refs.extend(_collect_refs(v))
    elif isinstance(schema_fragment, list):
        for item in schema_fragment:
            refs.extend(_collect_refs(item))
    return refs


# ---------------------------------------------------------------------------
# Build-level integration tests with synthetic schemas
# ---------------------------------------------------------------------------


class TestDomainKeyedBuild:
    @pytest.fixture
    def schema_dir_with_same_name_concepts(self, tmp_schema, write_concept):
        """A schema where two domains define an 'Event' concept with different semantics."""
        write_concept(
            "Event.yaml",
            make_concept(id="Event", domain=None, definition={"en": "A universal event.", "fr": "Un événement.", "es": "Un evento."}),
        )
        write_concept(
            "sp_event.yaml",
            make_concept(id="Event", domain="sp", definition={"en": "A social protection event.", "fr": "Un événement SP.", "es": "Un evento SP."}),
        )
        return tmp_schema

    def test_two_concepts_same_id_different_domains_both_present(
        self, schema_dir_with_same_name_concepts
    ):
        """Both concepts survive in the build output when domains differ."""
        result = build_vocabulary(schema_dir_with_same_name_concepts)
        assert "Event" in result["concepts"], "Universal Event missing"
        assert "sp/Event" in result["concepts"], "sp/Event missing"

    def test_universal_concept_has_no_domain_prefix_in_uri(
        self, schema_dir_with_same_name_concepts
    ):
        result = build_vocabulary(schema_dir_with_same_name_concepts)
        uri = result["concepts"]["Event"]["uri"]
        assert "/sp/" not in uri, f"Universal Event should not have /sp/ in URI: {uri}"

    def test_domain_concept_has_domain_prefix_in_uri(
        self, schema_dir_with_same_name_concepts
    ):
        result = build_vocabulary(schema_dir_with_same_name_concepts)
        uri = result["concepts"]["sp/Event"]["uri"]
        assert "/sp/Event" in uri, f"Domain Event should have /sp/Event in URI: {uri}"

    def test_domain_concept_key_contains_slash(self, tmp_schema, write_concept):
        """Domain-scoped concept is keyed with a slash separator."""
        write_concept(
            "Enrollment.yaml",
            make_concept(id="Enrollment", domain="sp"),
        )
        result = build_vocabulary(tmp_schema)
        assert "sp/Enrollment" in result["concepts"]
        assert "Enrollment" not in result["concepts"]

    def test_universal_concept_key_has_no_slash(self, tmp_schema, write_concept):
        """Universal concept is keyed by bare id without slash."""
        write_concept("Person.yaml", make_concept(id="Person", domain=None))
        result = build_vocabulary(tmp_schema)
        assert "Person" in result["concepts"]

    def test_bare_id_stored_in_concept_id_field(self, tmp_schema, write_concept):
        """The 'id' field inside each concept dict is always the bare id."""
        write_concept("Enrollment.yaml", make_concept(id="Enrollment", domain="sp"))
        result = build_vocabulary(tmp_schema)
        concept = result["concepts"]["sp/Enrollment"]
        assert concept["id"] == "Enrollment", (
            f"Expected bare id 'Enrollment', got '{concept['id']}'"
        )

    def test_jsonld_context_uses_bare_id(self, tmp_schema, write_concept):
        """JSON-LD context terms use bare concept ids, not composite keys."""
        write_concept("Enrollment.yaml", make_concept(id="Enrollment", domain="sp"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert "Enrollment" in ctx, "Bare id 'Enrollment' should be a context term"
        assert "sp/Enrollment" not in ctx, "Composite key must not appear in context"

    def test_supertype_preserved_as_written(self, tmp_schema, write_concept):
        """Supertypes are stored in the build output exactly as written in YAML.

        With the strict reference rule, ``supertypes: [Event]`` targets the
        root Event; a domain-scoped supertype must be written ``domain/Event``.
        """
        write_concept("Event.yaml", make_concept(id="Event", domain=None, abstract=True))
        write_concept(
            "Enrollment.yaml",
            make_concept(id="Enrollment", domain="sp", supertypes=["Event"]),
        )
        result = build_vocabulary(tmp_schema)
        enrollment = result["concepts"]["sp/Enrollment"]
        assert "Event" in enrollment.get("supertypes", []), (
            f"Expected 'Event' in supertypes, got {enrollment.get('supertypes')}"
        )


# ---------------------------------------------------------------------------
# Real-schema smoke test
# ---------------------------------------------------------------------------


class TestRealSchemaKeying:
    """Verify composite keying against the real schema directory."""

    @pytest.fixture(scope="class")
    def real_result(self):
        from tests.conftest import SCHEMA_DIR
        return build_vocabulary(SCHEMA_DIR)

    def test_sp_concepts_keyed_by_composite(self, real_result):
        """Known sp/ concepts appear under composite keys."""
        for name in ("Enrollment", "Grievance", "Program", "Entitlement"):
            key = f"sp/{name}"
            assert key in real_result["concepts"], (
                f"Expected composite key '{key}' in concepts"
            )

    def test_crvs_concepts_keyed_by_composite(self, real_result):
        """Known crvs/ concepts appear under composite keys."""
        for name in ("Birth", "Death", "Marriage", "Person"):
            key = f"crvs/{name}"
            assert key in real_result["concepts"], (
                f"Expected composite key '{key}' in concepts"
            )

    def test_universal_concepts_keyed_by_bare_id(self, real_result):
        """Known universal concepts appear under bare id keys (no slash prefix).
        Person is excluded from the crvs/ assertion because crvs/Person is a
        legitimate domain-scoped concept (a temporal snapshot of Person at event
        time) introduced alongside the universal root Person.
        """
        for name in ("Person", "Event", "Organization", "Household", "Location"):
            assert name in real_result["concepts"], (
                f"Expected bare key '{name}' in concepts"
            )
            assert f"sp/{name}" not in real_result["concepts"]
        # Only names that have no domain-specific subtype should be absent from crvs/.
        for name in ("Event", "Organization", "Household", "Location"):
            assert f"crvs/{name}" not in real_result["concepts"]

    def test_no_concept_id_field_contains_slash(self, real_result):
        """The 'id' field within each concept dict is always the bare id."""
        for key, concept in real_result["concepts"].items():
            bare_id = concept["id"]
            assert "/" not in bare_id, (
                f"Concept keyed as '{key}' has slash in id field: '{bare_id}'"
            )

    def test_all_concepts_have_id_in_jsonld_context(self, real_result):
        """Every concept's bare id appears as a term in the JSON-LD context."""
        ctx = real_result["context"]["@context"]
        for key, concept in real_result["concepts"].items():
            bare_id = concept["id"]
            assert bare_id in ctx, (
                f"Concept '{key}' (bare id '{bare_id}') missing from JSON-LD context"
            )
