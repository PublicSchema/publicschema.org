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
    def _concepts(self):
        return {
            "Person": {"id": "Person", "domain": None},
            "sp/Enrollment": {"id": "Enrollment", "domain": "sp"},
            "crvs/Birth": {"id": "Birth", "domain": "crvs"},
        }

    def test_existing_composite_key_returns_unchanged(self):
        concepts = self._concepts()
        assert _resolve_concept_key("sp/Enrollment", concepts) == "sp/Enrollment"

    def test_bare_id_resolves_to_universal_key(self):
        concepts = self._concepts()
        assert _resolve_concept_key("Person", concepts) == "Person"

    def test_bare_id_resolves_to_unique_domain_concept(self):
        """A bare id that matches exactly one domain concept resolves to that key."""
        concepts = self._concepts()
        assert _resolve_concept_key("Enrollment", concepts) == "sp/Enrollment"

    def test_ambiguous_bare_id_raises(self):
        """A bare id matching multiple domains raises ValueError."""
        concepts = {
            "sp/Enrollment": {"id": "Enrollment", "domain": "sp"},
            "edu/Enrollment": {"id": "Enrollment", "domain": "edu"},
        }
        with pytest.raises(ValueError, match="Ambiguous concept reference"):
            _resolve_concept_key("Enrollment", concepts)

    def test_unknown_ref_returns_unchanged(self):
        """An unknown ref is returned as-is; callers handle missing entries."""
        concepts = self._concepts()
        assert _resolve_concept_key("NonExistent", concepts) == "NonExistent"


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

    def test_supertype_resolved_to_composite_key(self, tmp_schema, write_concept):
        """Subtypes reference supertypes by bare id in YAML; resolved to composite key in build."""
        write_concept("Event.yaml", make_concept(id="Event", domain=None, abstract=True))
        write_concept(
            "Enrollment.yaml",
            make_concept(id="Enrollment", domain="sp", supertypes=["Event"]),
        )
        result = build_vocabulary(tmp_schema)
        enrollment = result["concepts"]["sp/Enrollment"]
        # Supertype should be resolved to the universal key "Event"
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
        for name in ("Birth", "Death", "Marriage", "CRVSPerson"):
            key = f"crvs/{name}"
            assert key in real_result["concepts"], (
                f"Expected composite key '{key}' in concepts"
            )

    def test_universal_concepts_keyed_by_bare_id(self, real_result):
        """Known universal concepts appear under bare id keys (no slash prefix)."""
        for name in ("Person", "Event", "Organization", "Household", "Location"):
            assert name in real_result["concepts"], (
                f"Expected bare key '{name}' in concepts"
            )
            assert f"sp/{name}" not in real_result["concepts"]
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
