"""Tests for the build pipeline.

TDD: these tests define expected behavior before implementation.
"""

import json
from pathlib import Path

import jsonschema
import pytest

from build.build import _external_equivalents_triples, _to_snake_case, build_vocabulary
from tests.conftest import make_concept, make_credential, make_property, make_vocabulary

# ---------------------------------------------------------------------------
# Round-trip: YAML in -> JSON out -> parse back -> assert structure
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_vocabulary_json_structure(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="gender-type",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))

        result = build_vocabulary(tmp_schema)

        assert "meta" in result
        assert "concepts" in result
        assert "properties" in result
        assert "vocabularies" in result

        # Concepts are keyed by ID
        assert "Person" in result["concepts"]
        person = result["concepts"]["Person"]
        assert person["id"] == "Person"
        assert "definition" in person
        assert "properties" in person

        # Properties include computed used_by list
        assert "gender" in result["properties"]
        gender = result["properties"]["gender"]
        assert "Person" in gender["used_by"]

        # Vocabularies include values
        assert "gender-type" in result["vocabularies"]
        vocab = result["vocabularies"]["gender-type"]
        assert len(vocab["values"]) == 1

    def test_concept_property_normalized_to_id(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob"],
        ))

        result = build_vocabulary(tmp_schema)
        props = result["concepts"]["Person"]["properties"]
        dob_prop = next(p for p in props if p["id"] == "dob")
        assert "required" not in dob_prop

    def test_bibliography_ids_preserve_source_id(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Bibliography ids stay bare while informed resources keep namespaces."""
        (tmp_schema / "bibliography").mkdir()
        (tmp_schema / "bibliography" / "sourcebook.yaml").write_text(
            """
id: sourcebook
title: Test Sourcebook
publisher: Test Publisher
year: 2026
type: guidance_publication
domain: social_protection
uri: https://example.org/sourcebook
access: open
status: active
informs:
  concepts:
    - sp/Enrollment
  vocabularies:
    - sp/enrollment-status
  properties:
    - enrollment_status
""".lstrip()
        )
        write_vocabulary(
            "sp/enrollment-status.yaml",
            make_vocabulary(id="enrollment-status", domain="sp"),
        )
        write_property(
            "enrollment_status.yaml",
            make_property(id="enrollment_status", vocabulary="sp/enrollment-status"),
        )
        write_concept(
            "enrollment.yaml",
            make_concept(id="Enrollment", domain="sp", properties=["enrollment_status"]),
        )

        result = build_vocabulary(tmp_schema)

        assert "sourcebook" in result["bibliography"]
        assert "social_protection/sourcebook" not in result["bibliography"]
        assert result["bibliography"]["sourcebook"]["id"] == "sourcebook"
        assert result["concepts"]["sp/Enrollment"]["bibliography_refs"] == ["sourcebook"]
        assert result["vocabularies"]["sp/enrollment-status"]["bibliography_refs"] == [
            "sourcebook"
        ]
        assert result["properties"]["enrollment_status"]["bibliography_refs"] == [
            "sourcebook"
        ]


# ---------------------------------------------------------------------------
# URI generation
# ---------------------------------------------------------------------------

class TestURIGeneration:
    def test_universal_concept_uri(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["uri"] == "https://test.example.org/Person"

    def test_domain_concept_uri(self, tmp_schema, write_concept):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["sp/Enrollment"]["uri"] == "https://test.example.org/sp/Enrollment"

    def test_domain_concept_path(self, tmp_schema, write_concept):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["sp/Enrollment"]["path"] == "/sp/Enrollment"

    def test_universal_concept_path(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["path"] == "/Person"

    def test_concept_domain_field_preserved(self, tmp_schema, write_concept):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["sp/Enrollment"]["domain"] == "sp"

    def test_universal_concept_domain_is_null(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["domain"] is None

    def test_property_uri_universal(self, tmp_schema, write_concept, write_property):
        """Property used by a universal concept gets a universal URI."""
        write_property("dob.yaml", make_property(id="dob"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["dob"]["uri"] == "https://test.example.org/dob"
        assert result["properties"]["dob"]["path"] == "/dob"

    def test_property_uri_domain_specific(
        self, tmp_schema, write_concept, write_property
    ):
        """Property used only by domain-specific concepts gets a domain URI."""
        write_property("enrollment_status.yaml", make_property(id="enrollment_status"))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["enrollment_status"]["uri"] == "https://test.example.org/sp/enrollment_status"
        assert result["properties"]["enrollment_status"]["path"] == "/sp/enrollment_status"

    def test_property_domain_override_forces_universal(
        self, tmp_schema, write_concept, write_property
    ):
        """Property with domain_override: null stays universal even if only used by SP concepts."""
        write_property("amount.yaml", make_property(
            id="amount", type="decimal", domain_override=None,
        ))
        write_concept("entitlement.yaml", make_concept(
            id="Entitlement", domain="sp", properties=["amount"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["amount"]["uri"] == "https://test.example.org/amount"
        assert result["properties"]["amount"]["path"] == "/amount"

    def test_property_domain_override_sp_forces_domain(
        self, tmp_schema, write_concept, write_property
    ):
        """Property with domain_override: sp gets SP URI even if used by universal concepts."""
        write_property("targeting.yaml", make_property(
            id="targeting", domain_override="sp",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["targeting"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["targeting"]["uri"] == "https://test.example.org/sp/targeting"

    def test_property_without_domain_override_uses_derived(
        self, tmp_schema, write_concept, write_property
    ):
        """Property without domain_override uses the derived domain (existing behavior)."""
        write_property("enrollment_status.yaml", make_property(id="enrollment_status"))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["enrollment_status"]["uri"] == "https://test.example.org/sp/enrollment_status"

    def test_property_uri_mixed_domains_stays_universal(
        self, tmp_schema, write_concept, write_property
    ):
        """Property used by both universal and domain concepts stays universal."""
        write_property("start_date.yaml", make_property(id="start_date", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["start_date"],
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["start_date"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["start_date"]["uri"] == "https://test.example.org/start_date"

    def test_vocabulary_uri(self, tmp_schema, write_vocabulary):
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["gender-type"]
        assert vocab["uri"] == "https://test.example.org/vocab/gender-type"

    def test_vocabulary_value_uri(self, tmp_schema, write_vocabulary):
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        value = result["vocabularies"]["gender-type"]["values"][0]
        assert value["uri"] == "https://test.example.org/vocab/gender-type/value_a"

    def test_vocabulary_hierarchy_fields_passed_through(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values with level and parent_code appear in build output."""
        data = make_vocabulary(id="occupation")
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
        write_vocabulary("occupation.yaml", data)
        result = build_vocabulary(tmp_schema)
        values = result["vocabularies"]["occupation"]["values"]
        assert values[0]["level"] == 1
        assert "parent_code" not in values[0]
        assert values[1]["level"] == 2
        assert values[1]["parent_code"] == "1"

    def test_vocabulary_value_group_type_applicability_passed_through(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary values pass through advisory group-type applicability metadata."""
        data = make_vocabulary(id="group-role")
        data["values"] = [
            {
                "code": "head",
                "label": {"en": "Head"},
                "group_type_applicability": ["household", "family"],
            }
        ]
        write_vocabulary("group-role.yaml", data)
        result = build_vocabulary(tmp_schema)
        value = result["vocabularies"]["group-role"]["values"][0]
        assert value["group_type_applicability"] == ["household", "family"]

    def test_vocabulary_flat_values_omit_hierarchy_fields(
        self, tmp_schema, write_vocabulary
    ):
        """Flat vocabulary values (no level/parent_code) omit those fields."""
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        value = result["vocabularies"]["gender-type"]["values"][0]
        assert "level" not in value
        assert "parent_code" not in value

    def test_vocabulary_external_values_true(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary with external_values: true passes the flag through."""
        write_vocabulary("country.yaml", make_vocabulary(
            id="country", external_values=True,
        ))
        result = build_vocabulary(tmp_schema)
        assert result["vocabularies"]["country"]["external_values"] is True

    def test_vocabulary_external_values_defaults_false(
        self, tmp_schema, write_vocabulary
    ):
        """Vocabulary without external_values defaults to False."""
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        assert result["vocabularies"]["gender-type"]["external_values"] is False

    def test_vocabulary_uri_domain_specific(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Domain-scoped vocabulary (declared via domain + subdir) gets a domain URI."""
        write_vocabulary("sp/estatus.yaml", make_vocabulary(id="estatus", domain="sp"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="sp/estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["sp/estatus"]
        assert vocab["uri"] == "https://test.example.org/vocab/sp/estatus"
        assert vocab["domain"] == "sp"
        assert vocab["id"] == "estatus"

    def test_vocabulary_uri_universal(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Vocabulary referenced by universal properties stays universal."""
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="gender-type",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["gender-type"]
        assert vocab["uri"] == "https://test.example.org/vocab/gender-type"
        assert vocab["domain"] is None

    def test_vocabulary_path_domain_specific(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Domain-scoped vocabulary gets a /vocab/<domain>/<id> path."""
        write_vocabulary("sp/estatus.yaml", make_vocabulary(id="estatus", domain="sp"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="sp/estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["sp/estatus"]
        assert vocab["path"] == "/vocab/sp/estatus"


# ---------------------------------------------------------------------------
# JSON-LD context generation
# ---------------------------------------------------------------------------

class TestJsonLdContext:
    def test_context_has_vocab_and_prefixes(
        self, tmp_schema, write_concept
    ):
        """Context includes @vocab, xsd, schema, ps, rdfs, rdf, skos prefixes."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["@vocab"] == "https://test.example.org/"
        assert ctx["xsd"] == "http://www.w3.org/2001/XMLSchema#"
        assert ctx["schema"] == "https://schema.org/"
        assert ctx["ps"] == "https://publicschema.org/meta/"
        assert ctx["rdfs"] == "http://www.w3.org/2000/01/rdf-schema#"
        assert ctx["rdf"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        assert ctx["skos"] == "http://www.w3.org/2004/02/skos/core#"

    def test_context_skos_match_predicates_have_id_coercion(
        self, tmp_schema, write_concept
    ):
        """SKOS match predicates in context have full @id IRI and @type: @id.

        Without the explicit @id, JSON-LD processors cannot resolve CURIE keys
        like 'skos:exactMatch' as valid context terms.
        """
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        skos_base = "http://www.w3.org/2004/02/skos/core#"
        for pred_name in ["exactMatch", "closeMatch", "broadMatch", "narrowMatch", "relatedMatch"]:
            key = f"skos:{pred_name}"
            assert key in ctx, f"Missing context entry for {key}"
            entry = ctx[key]
            assert isinstance(entry, dict), f"{key} should be a dict, got {type(entry)}"
            assert entry["@id"] == f"{skos_base}{pred_name}", (
                f"{key} @id should be full IRI, got {entry.get('@id')}"
            )
            assert entry["@type"] == "@id", (
                f"{key} should have @type: @id for URI coercion"
            )

    def test_context_rdfs_see_also_has_id_coercion(
        self, tmp_schema, write_concept
    ):
        """rdfs:seeAlso in context has full @id IRI and @type: @id."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        entry = ctx["rdfs:seeAlso"]
        assert isinstance(entry, dict)
        assert entry["@id"] == "http://www.w3.org/2000/01/rdf-schema#seeAlso"
        assert entry["@type"] == "@id"

    def test_context_has_no_id(
        self, tmp_schema, write_concept
    ):
        """Context document has no @id (it describes the context, not itself)."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        context = result["context"]
        assert "@id" not in context

    def test_context_has_type_alias(
        self, tmp_schema, write_concept
    ):
        """Context maps 'type' to '@type' for standalone use without VC context."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["type"] == "@type"

    def test_context_concept_has_bare_uri(
        self, tmp_schema, write_concept
    ):
        """Concepts in context use bare URIs (HTML page IS the concept URI)."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["Person"] == "https://test.example.org/Person"

    def test_context_string_property_has_bare_uri(
        self, tmp_schema, write_concept, write_property
    ):
        """String properties use bare URIs in the context."""
        write_property("name.yaml", make_property(id="name", type="string"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["name"] == "https://test.example.org/name"

    def test_context_date_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        """Date properties get @type: xsd:date coercion with bare URI."""
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["dob"] == {
            "@id": "https://test.example.org/dob",
            "@type": "xsd:date",
        }

    def test_context_datetime_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("created.yaml", make_property(id="created", type="datetime"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["created"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["created"] == {
            "@id": "https://test.example.org/created",
            "@type": "xsd:dateTime",
        }

    def test_context_decimal_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("amount.yaml", make_property(id="amount", type="decimal"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["amount"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["amount"] == {
            "@id": "https://test.example.org/amount",
            "@type": "xsd:decimal",
        }

    def test_context_integer_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("count.yaml", make_property(id="count", type="integer"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["count"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["count"] == {
            "@id": "https://test.example.org/count",
            "@type": "xsd:integer",
        }

    def test_context_boolean_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("active.yaml", make_property(id="active", type="boolean"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["active"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["active"] == {
            "@id": "https://test.example.org/active",
            "@type": "xsd:boolean",
        }

    def test_context_concept_ref_property_has_id_type(
        self, tmp_schema, write_concept, write_property
    ):
        """Properties referencing a concept get @type: @id with bare URI."""
        write_property("beneficiary.yaml", make_property(
            id="beneficiary", type="concept:Person",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["beneficiary"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["beneficiary"] == {
            "@id": "https://test.example.org/beneficiary",
            "@type": "@id",
        }

    def test_context_uri_property_has_id_type(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("link.yaml", make_property(id="link", type="uri"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["link"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["link"] == {
            "@id": "https://test.example.org/link",
            "@type": "@id",
        }

    def test_context_uses_domain_uris(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("enrollment_status.yaml", make_property(id="enrollment_status"))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))

        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["Enrollment"] == "https://test.example.org/sp/Enrollment"
        assert ctx["enrollment_status"] == "https://test.example.org/sp/enrollment_status"

    def test_context_schema_org_alias_for_string_property(
        self, tmp_schema, write_concept, write_property
    ):
        """Property with schema_org_equivalent gets a camelCase alias in context."""
        write_property("given_name.yaml", make_property(
            id="given_name", schema_org_equivalent="schema:givenName",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["given_name"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        # Original entry still present
        assert ctx["given_name"] == "https://test.example.org/given_name"
        # schema.org alias resolves to the same PublicSchema URI
        assert ctx["givenName"] == "https://test.example.org/given_name"

    def test_context_schema_org_alias_for_typed_property(
        self, tmp_schema, write_concept, write_property
    ):
        """Typed property with schema_org_equivalent gets alias with same type coercion."""
        write_property("dob.yaml", make_property(
            id="dob", type="date",
            schema_org_equivalent="schema:birthDate",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["dob"] == {
            "@id": "https://test.example.org/dob",
            "@type": "xsd:date",
        }
        assert ctx["birthDate"] == {
            "@id": "https://test.example.org/dob",
            "@type": "xsd:date",
        }

    def test_context_geojson_geometry_property_has_json_type(
        self, tmp_schema, write_concept, write_property
    ):
        """geojson_geometry properties get @type: @json in the JSON-LD context."""
        write_property("geom.yaml", make_property(id="geom", type="geojson_geometry"))
        write_concept("area.yaml", make_concept(
            id="Area", properties=["geom"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["geom"] == {
            "@id": "https://test.example.org/geom",
            "@type": "@json",
        }

    def test_context_multivalued_property_has_container_set(
        self, tmp_schema, write_concept, write_property
    ):
        """Multi-valued properties get @container: @set in context."""
        write_property("ids.yaml", make_property(
            id="ids", type="string", cardinality="multiple",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["ids"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["ids"] == {
            "@id": "https://test.example.org/ids",
            "@container": "@set",
        }

    def test_context_multivalued_typed_property_has_container_set(
        self, tmp_schema, write_concept, write_property
    ):
        """Multi-valued typed properties get both @type and @container."""
        write_property("dates.yaml", make_property(
            id="dates", type="date", cardinality="multiple",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dates"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["dates"] == {
            "@id": "https://test.example.org/dates",
            "@type": "xsd:date",
            "@container": "@set",
        }

    def test_context_has_credential_types(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Credential types appear in context with explicit URIs."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["IdentityCredential"] == "https://test.example.org/credentials/IdentityCredential"

    def test_vocabulary_json_has_schema_org_equivalent(
        self, tmp_schema, write_concept, write_property
    ):
        """Properties with schema_org_equivalent include it in vocabulary.json output."""
        write_property("given_name.yaml", make_property(
            id="given_name", schema_org_equivalent="schema:givenName",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["given_name"],
        ))
        result = build_vocabulary(tmp_schema)
        prop = result["properties"]["given_name"]
        assert prop["schema_org_equivalent"] == "schema:givenName"

    def test_property_without_schema_org_equivalent_is_null(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        prop = result["properties"]["name"]
        assert prop["schema_org_equivalent"] is None


# ---------------------------------------------------------------------------
# JSON Schema per concept generation
# ---------------------------------------------------------------------------

class TestJsonSchemaGeneration:
    def test_concept_schema_is_valid_json_schema(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob", "name"],
        ))

        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Person"]

        # It should be a valid JSON Schema (meta-validate)
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_concept_schema_has_no_required_array(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["dob", "name"],
        ))

        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Person"]

        assert "required" not in schema

    def test_concept_schema_type_mappings(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_property("count.yaml", make_property(id="count", type="integer"))
        write_property("active.yaml", make_property(id="active", type="boolean"))
        write_property("amount.yaml", make_property(id="amount", type="decimal"))
        write_concept("test.yaml", make_concept(
            id="Test",
            properties=["dob", "count", "active", "amount"],
        ))

        result = build_vocabulary(tmp_schema)
        props = result["concept_schemas"]["Test"]["properties"]

        assert props["dob"]["type"] == "string"
        assert props["dob"]["format"] == "date"
        assert props["count"]["type"] == "integer"
        assert props["active"]["type"] == "boolean"
        assert props["amount"]["type"] == "number"

    def test_concept_schema_vocabulary_enum(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(
            id="gender-type",
            values=[
                {"code": "male", "label": {"en": "Male", "fr": "M", "es": "M"},
                 "definition": {"en": "Male.", "fr": "M.", "es": "M."}},
                {"code": "female", "label": {"en": "Female", "fr": "F", "es": "F"},
                 "definition": {"en": "Female.", "fr": "F.", "es": "F."}},
            ],
        ))
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="gender-type",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))

        result = build_vocabulary(tmp_schema)
        gender_schema = result["concept_schemas"]["Person"]["properties"]["gender"]
        assert set(gender_schema["enum"]) == {"male", "female"}

    def test_concept_schema_vocabulary_enum_has_comment_uri(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Vocabulary enum schema includes $comment with the vocabulary URI."""
        write_vocabulary("gender-type.yaml", make_vocabulary(
            id="gender-type",
            values=[
                {"code": "male", "label": {"en": "Male", "fr": "M", "es": "M"},
                 "definition": {"en": "Male.", "fr": "M.", "es": "M."}},
            ],
        ))
        write_property("gender.yaml", make_property(
            id="gender", vocabulary="gender-type",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["gender"],
        ))
        result = build_vocabulary(tmp_schema)
        gender_schema = result["concept_schemas"]["Person"]["properties"]["gender"]
        assert "$comment" in gender_schema
        assert gender_schema["$comment"] == "https://test.example.org/vocab/gender-type"

    def test_concept_schema_multivalued_property(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("ids.yaml", make_property(
            id="ids", type="string", cardinality="multiple",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["ids"],
        ))

        result = build_vocabulary(tmp_schema)
        ids_schema = result["concept_schemas"]["Person"]["properties"]["ids"]
        assert ids_schema["type"] == "array"
        assert ids_schema["items"]["type"] == "string"

    def test_concept_schema_geojson_geometry_has_ref(
        self, tmp_schema, write_concept, write_property
    ):
        """geojson_geometry type produces a $ref to GeoJSON Geometry schema."""
        write_property("geom.yaml", make_property(id="geom", type="geojson_geometry"))
        write_concept("area.yaml", make_concept(
            id="Area", properties=["geom"],
        ))
        result = build_vocabulary(tmp_schema)
        geom_schema = result["concept_schemas"]["Area"]["properties"]["geom"]
        assert geom_schema["$ref"] == "https://geojson.org/schema/Geometry.json"

    def test_concept_schema_geojson_geometry_multivalued(
        self, tmp_schema, write_concept, write_property
    ):
        """Multi-valued geojson_geometry wraps the $ref in an array."""
        write_property("geoms.yaml", make_property(
            id="geoms", type="geojson_geometry", cardinality="multiple",
        ))
        write_concept("area.yaml", make_concept(
            id="Area", properties=["geoms"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Area"]["properties"]["geoms"]
        assert schema["type"] == "array"
        assert schema["items"]["$ref"] == "https://geojson.org/schema/Geometry.json"

    # --- Phase 1: Descriptions ---

    def test_concept_schema_has_description(
        self, tmp_schema, write_concept, write_property
    ):
        """Concept schema includes English definition as description."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person",
            properties=["name"],
            definition={"en": "An individual human being.", "fr": "Un.", "es": "Un."},
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Person"]
        assert schema["description"] == "An individual human being."

    def test_property_schema_has_description(
        self, tmp_schema, write_concept, write_property
    ):
        """Property schema includes English definition as description."""
        write_property("name.yaml", make_property(
            id="name",
            definition={"en": "Full legal name.", "fr": "Nom.", "es": "Nombre."},
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        name_schema = result["concept_schemas"]["Person"]["properties"]["name"]
        assert name_schema["description"] == "Full legal name."

    def test_property_schema_no_description_when_missing(
        self, tmp_schema, write_concept, write_property
    ):
        """Property without definition.en should not have a description key."""
        write_property("code.yaml", make_property(
            id="code", definition={"en": "", "fr": "", "es": ""},
        ))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["code"],
        ))
        result = build_vocabulary(tmp_schema)
        code_schema = result["concept_schemas"]["Test"]["properties"]["code"]
        assert "description" not in code_schema

    # --- Phase 2: Vocab size threshold ---

    def test_concept_schema_large_vocab_omits_enum(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Vocab with >50 values should not inline enum, but should have $comment."""
        values = [
            {"code": f"v{i}", "label": {"en": f"V{i}", "fr": f"V{i}", "es": f"V{i}"},
             "definition": {"en": f"Value {i}.", "fr": f"V {i}.", "es": f"V {i}."}}
            for i in range(51)
        ]
        write_vocabulary("big-vocab.yaml", make_vocabulary(
            id="big-vocab", values=values,
        ))
        write_property("field.yaml", make_property(
            id="field", vocabulary="big-vocab",
        ))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["field"],
        ))
        result = build_vocabulary(tmp_schema)
        field_schema = result["concept_schemas"]["Test"]["properties"]["field"]
        assert "enum" not in field_schema
        assert field_schema["type"] == "string"
        assert "$comment" in field_schema

    def test_concept_schema_small_vocab_still_has_enum(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Vocab with <=50 values should still inline enum."""
        write_vocabulary("small-vocab.yaml", make_vocabulary(
            id="small-vocab",
            values=[
                {"code": "a", "label": {"en": "A", "fr": "A", "es": "A"},
                 "definition": {"en": "A.", "fr": "A.", "es": "A."}},
                {"code": "b", "label": {"en": "B", "fr": "B", "es": "B"},
                 "definition": {"en": "B.", "fr": "B.", "es": "B."}},
            ],
        ))
        write_property("field.yaml", make_property(
            id="field", vocabulary="small-vocab",
        ))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["field"],
        ))
        result = build_vocabulary(tmp_schema)
        field_schema = result["concept_schemas"]["Test"]["properties"]["field"]
        assert "enum" in field_schema
        assert set(field_schema["enum"]) == {"a", "b"}

    def test_concept_schema_vocab_threshold_boundary(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Exactly 50 values should inline; 51 should skip."""
        values_50 = [
            {"code": f"v{i}", "label": {"en": f"V{i}", "fr": f"V{i}", "es": f"V{i}"},
             "definition": {"en": f"V{i}.", "fr": f"V{i}.", "es": f"V{i}."}}
            for i in range(50)
        ]
        values_51 = values_50 + [
            {"code": "v50", "label": {"en": "V50", "fr": "V50", "es": "V50"},
             "definition": {"en": "V50.", "fr": "V50.", "es": "V50."}}
        ]
        write_vocabulary("exact50.yaml", make_vocabulary(id="exact50", values=values_50))
        write_vocabulary("exact51.yaml", make_vocabulary(id="exact51", values=values_51))
        write_property("f50.yaml", make_property(id="f50", vocabulary="exact50"))
        write_property("f51.yaml", make_property(id="f51", vocabulary="exact51"))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["f50", "f51"],
        ))
        result = build_vocabulary(tmp_schema)
        props = result["concept_schemas"]["Test"]["properties"]
        assert "enum" in props["f50"]
        assert "enum" not in props["f51"]

    # --- Phase 3: $defs for repeated vocab enums ---

    def test_concept_schema_repeated_vocab_uses_defs(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Two properties sharing a vocab should produce $defs with $ref on both."""
        write_vocabulary("status.yaml", make_vocabulary(
            id="status",
            values=[
                {"code": "active", "label": {"en": "Active", "fr": "A", "es": "A"},
                 "definition": {"en": "Active.", "fr": "A.", "es": "A."}},
                {"code": "inactive", "label": {"en": "Inactive", "fr": "I", "es": "I"},
                 "definition": {"en": "Inactive.", "fr": "I.", "es": "I."}},
            ],
        ))
        write_property("status_a.yaml", make_property(id="status_a", vocabulary="status"))
        write_property("status_b.yaml", make_property(id="status_b", vocabulary="status"))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["status_a", "status_b"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Test"]
        assert "$defs" in schema
        assert "status" in schema["$defs"]
        assert schema["$defs"]["status"]["enum"] == ["active", "inactive"]
        # Both properties should use $ref
        assert schema["properties"]["status_a"] == {"$ref": "#/$defs/status"}
        assert schema["properties"]["status_b"] == {"$ref": "#/$defs/status"}

    def test_concept_schema_single_use_vocab_stays_inline(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """A vocab used by only one property should remain inline, no $defs."""
        write_vocabulary("color.yaml", make_vocabulary(
            id="color",
            values=[
                {"code": "red", "label": {"en": "Red", "fr": "R", "es": "R"},
                 "definition": {"en": "Red.", "fr": "R.", "es": "R."}},
            ],
        ))
        write_property("color.yaml", make_property(id="color", vocabulary="color"))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["color"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Test"]
        assert "$defs" not in schema
        assert "enum" in schema["properties"]["color"]

    def test_concept_schema_multivalued_with_defs(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Multi-valued property using a deduped vocab wraps $ref in array."""
        write_vocabulary("tag.yaml", make_vocabulary(
            id="tag",
            values=[
                {"code": "a", "label": {"en": "A", "fr": "A", "es": "A"},
                 "definition": {"en": "A.", "fr": "A.", "es": "A."}},
            ],
        ))
        write_property("tags.yaml", make_property(
            id="tags", vocabulary="tag", cardinality="multiple",
        ))
        write_property("more_tags.yaml", make_property(
            id="more_tags", vocabulary="tag", cardinality="multiple",
        ))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["tags", "more_tags"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Test"]
        assert "$defs" in schema
        assert "tag" in schema["$defs"]
        assert schema["properties"]["tags"] == {
            "type": "array", "items": {"$ref": "#/$defs/tag"},
        }
        assert schema["properties"]["more_tags"] == {
            "type": "array", "items": {"$ref": "#/$defs/tag"},
        }

    def test_concept_schema_with_defs_is_valid_json_schema(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Schema with $defs should still pass JSON Schema meta-validation."""
        write_vocabulary("status.yaml", make_vocabulary(
            id="status",
            values=[
                {"code": "active", "label": {"en": "Active", "fr": "A", "es": "A"},
                 "definition": {"en": "Active.", "fr": "A.", "es": "A."}},
                {"code": "inactive", "label": {"en": "Inactive", "fr": "I", "es": "I"},
                 "definition": {"en": "Inactive.", "fr": "I.", "es": "I."}},
            ],
        ))
        write_property("status_a.yaml", make_property(id="status_a", vocabulary="status"))
        write_property("status_b.yaml", make_property(id="status_b", vocabulary="status"))
        write_concept("test.yaml", make_concept(
            id="Test", properties=["status_a", "status_b"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["concept_schemas"]["Test"]
        jsonschema.Draft202012Validator.check_schema(schema)

    # --- Phase 4: $ref for concept references ---

    def test_concept_schema_concept_ref_uses_oneOf(
        self, tmp_schema, write_concept, write_property
    ):
        """concept:X property produces oneOf with $ref and string."""
        write_property("addr.yaml", make_property(id="addr", type="concept:Address"))
        write_concept("address.yaml", make_concept(id="Address", properties=[]))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["addr"],
        ))
        result = build_vocabulary(tmp_schema)
        addr_schema = result["concept_schemas"]["Person"]["properties"]["addr"]
        assert "oneOf" in addr_schema
        assert len(addr_schema["oneOf"]) == 2
        ref_option = addr_schema["oneOf"][0]
        assert ref_option["$ref"] == "https://test.example.org/Address.schema.json"
        str_option = addr_schema["oneOf"][1]
        assert str_option["type"] == "string"

    def test_concept_schema_concept_ref_domain_scoped(
        self, tmp_schema, write_concept, write_property
    ):
        """concept:sp/Enrollment produces the domain-scoped $ref URI."""
        write_property("enrollment_ref.yaml", make_property(
            id="enrollment_ref", type="concept:sp/Enrollment",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=[],
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["enrollment_ref"],
        ))
        result = build_vocabulary(tmp_schema)
        ref_schema = result["concept_schemas"]["Person"]["properties"]["enrollment_ref"]
        assert "oneOf" in ref_schema
        assert ref_schema["oneOf"][0]["$ref"] == "https://test.example.org/sp/Enrollment.schema.json"


# ---------------------------------------------------------------------------
# Credential schema generation
# ---------------------------------------------------------------------------

class TestCredentialSchemas:
    def test_credential_schemas_in_build_output(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Build output includes credential_schemas when credentials/ dir exists."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        assert "credential_schemas" in result
        assert "IdentityCredential" in result["credential_schemas"]

    def test_credential_schema_uses_sd_jwt_vc_envelope(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Credential schema has SD-JWT VC envelope with required fields and concept properties."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["IdentityCredential"]

        # Valid JSON Schema
        jsonschema.Draft202012Validator.check_schema(schema)

        # Has $id and $schema
        assert "$id" in schema
        assert "$schema" in schema
        assert schema["title"] == "IdentityCredential"

        # Required fields for SD-JWT VC
        assert "required" in schema
        assert "vct" in schema["required"]
        assert "iss" in schema["required"]
        assert "iat" in schema["required"]

        # No W3C VCDM fields
        assert "@context" not in schema["required"]

        # SD-JWT VC envelope structure
        props = schema["properties"]
        assert "vct" in props
        assert "iss" in props
        assert "iat" in props
        assert "cnf" in props
        assert "credentialSubject" in props

        # vct has the correct const value
        assert props["vct"]["const"] == "https://test.example.org/schemas/credentials/IdentityCredential"

        # credentialSubject has the concept's properties
        subject = props["credentialSubject"]
        assert "name" in subject["properties"]

    def test_credential_schema_includes_nested_concepts(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Credential with included_concepts nests those concept schemas in credentialSubject."""
        write_property("name.yaml", make_property(id="name"))
        write_property("enrollment_status.yaml", make_property(id="enrollment_status"))
        write_property("program_ref.yaml", make_property(id="program_ref"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
            properties=["enrollment_status", "program_ref"],
        ))
        write_credential("enrollment_cred.yaml", make_credential(
            id="EnrollmentCredential",
            subject_concept="Person",
            included_concepts=["sp/Enrollment"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["EnrollmentCredential"]
        subject_props = schema["properties"]["credentialSubject"]["properties"]

        # Person properties at top level of credentialSubject
        assert "name" in subject_props
        # Enrollment nested as an object
        assert "enrollment" in subject_props
        enrollment = subject_props["enrollment"]
        assert "enrollment_status" in enrollment["properties"]

    def test_credential_schema_validates_sd_jwt_example(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """A valid SD-JWT VC payload validates against the generated credential schema."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["IdentityCredential"]

        example = {
            "vct": "https://test.example.org/schemas/credentials/IdentityCredential",
            "iss": "did:web:example.gov",
            "iat": 1736899200,
            "credentialSubject": {
                "type": "Person",
                "name": "Amina Diallo",
            },
        }
        jsonschema.validate(example, schema)

    def test_credential_schema_rejects_missing_required_fields(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """A document without vct, iss, or iat fails validation."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["IdentityCredential"]

        # Missing vct and iss
        bad_example = {
            "iat": 1736899200,
            "credentialSubject": {"name": "Test"},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad_example, schema)

    def test_credential_schema_rejects_wrong_vct(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """A payload with incorrect vct value fails validation."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["IdentityCredential"]

        bad_example = {
            "vct": "https://wrong.example.com/WrongType",
            "iss": "did:web:example.gov",
            "iat": 1736899200,
            "credentialSubject": {"name": "Test"},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad_example, schema)

    def test_credential_schema_snake_case_nested_key(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Multi-word included concept uses snake_case key (PaymentEvent -> payment_event)."""
        write_property("name.yaml", make_property(id="name"))
        write_property("amount.yaml", make_property(id="amount", type="decimal"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_concept("payment_event.yaml", make_concept(
            id="PaymentEvent", properties=["amount"],
        ))
        write_credential("payment.yaml", make_credential(
            id="PaymentCredential",
            subject_concept="Person",
            included_concepts=["PaymentEvent"],
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["PaymentCredential"]
        subject_props = schema["properties"]["credentialSubject"]["properties"]
        assert "payment_event" in subject_props
        assert "paymentEvent" not in subject_props

    def test_credential_schema_propagates_defs_from_concept(
        self, tmp_schema, write_concept, write_property, write_vocabulary,
        write_credential
    ):
        """Credential schema should include $defs from its subject concept."""
        write_vocabulary("status.yaml", make_vocabulary(
            id="status",
            values=[
                {"code": "active", "label": {"en": "Active", "fr": "A", "es": "A"},
                 "definition": {"en": "Active.", "fr": "A.", "es": "A."}},
                {"code": "inactive", "label": {"en": "Inactive", "fr": "I", "es": "I"},
                 "definition": {"en": "Inactive.", "fr": "I.", "es": "I."}},
            ],
        ))
        write_property("status_a.yaml", make_property(id="status_a", vocabulary="status"))
        write_property("status_b.yaml", make_property(id="status_b", vocabulary="status"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["status_a", "status_b"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        cred_schema = result["credential_schemas"]["IdentityCredential"]
        # $defs from Person should be propagated
        assert "$defs" in cred_schema
        assert "status" in cred_schema["$defs"]
        # credentialSubject properties should use $ref
        subject_props = cred_schema["properties"]["credentialSubject"]["properties"]
        assert subject_props["status_a"] == {"$ref": "#/$defs/status"}

    def test_credential_schema_merges_defs_from_included_concepts(
        self, tmp_schema, write_concept, write_property, write_vocabulary,
        write_credential
    ):
        """Credential schema should merge $defs from both subject and included concepts."""
        write_vocabulary("status.yaml", make_vocabulary(
            id="status",
            values=[
                {"code": "active", "label": {"en": "Active", "fr": "A", "es": "A"},
                 "definition": {"en": "Active.", "fr": "A.", "es": "A."}},
                {"code": "inactive", "label": {"en": "Inactive", "fr": "I", "es": "I"},
                 "definition": {"en": "Inactive.", "fr": "I.", "es": "I."}},
            ],
        ))
        write_vocabulary("priority.yaml", make_vocabulary(
            id="priority",
            values=[
                {"code": "high", "label": {"en": "High", "fr": "H", "es": "H"},
                 "definition": {"en": "High.", "fr": "H.", "es": "H."}},
                {"code": "low", "label": {"en": "Low", "fr": "L", "es": "L"},
                 "definition": {"en": "Low.", "fr": "L.", "es": "L."}},
            ],
        ))
        write_property("status_a.yaml", make_property(id="status_a", vocabulary="status"))
        write_property("status_b.yaml", make_property(id="status_b", vocabulary="status"))
        write_property("prio_a.yaml", make_property(id="prio_a", vocabulary="priority"))
        write_property("prio_b.yaml", make_property(id="prio_b", vocabulary="priority"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["status_a", "status_b"],
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
            properties=["prio_a", "prio_b"],
        ))
        write_credential("enrollment_cred.yaml", make_credential(
            id="EnrollmentCredential",
            subject_concept="Person",
            included_concepts=["sp/Enrollment"],
        ))
        result = build_vocabulary(tmp_schema)
        cred_schema = result["credential_schemas"]["EnrollmentCredential"]
        # Should have $defs from both Person (status) and Enrollment (priority)
        assert "$defs" in cred_schema
        assert "status" in cred_schema["$defs"]
        assert "priority" in cred_schema["$defs"]


# ---------------------------------------------------------------------------
# JSON-LD document generation
# ---------------------------------------------------------------------------

class TestJsonLdDocuments:
    def _concept_node(self, doc: dict) -> dict:
        """Extract the concept (rdfs:Class) node from a @graph-based doc."""
        return doc["@graph"][0]

    def test_concept_jsonld_has_bare_uri(
        self, tmp_schema, write_concept
    ):
        """Concept JSON-LD @id is the bare URI (no .jsonld suffix)."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        docs = result["jsonld_docs"]
        doc = docs["concepts/Person.jsonld"]
        concept = self._concept_node(doc)
        assert concept["@id"] == "https://test.example.org/Person"
        assert not concept["@id"].endswith(".jsonld")

    def test_concept_jsonld_type_is_rdfs_class(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        assert self._concept_node(doc)["@type"] == "rdfs:Class"

    def test_concept_jsonld_has_context_url(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        assert doc["@context"] == "https://test.example.org/ctx/draft.jsonld"

    def test_concept_jsonld_uses_graph_array(
        self, tmp_schema, write_concept
    ):
        """Concept JSON-LD uses @graph array, not a single top-level node."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        assert "@graph" in doc
        assert isinstance(doc["@graph"], list)
        assert len(doc["@graph"]) >= 1
        # Top-level should only have @context and @graph
        assert "@id" not in doc
        assert "@type" not in doc

    def test_concept_jsonld_language_tagged_comments(
        self, tmp_schema, write_concept
    ):
        """rdfs:comment uses language-tagged values, not invented rdfs:comment_fr."""
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={"en": "A person.", "fr": "Une personne.", "es": "Una persona."},
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        concept = self._concept_node(doc)
        comments = concept["rdfs:comment"]
        assert isinstance(comments, list)
        langs = {c["@language"]: c["@value"] for c in comments}
        assert langs["en"] == "A person."
        assert langs["fr"] == "Une personne."
        assert langs["es"] == "Una persona."
        # No invented properties
        assert "rdfs:comment_fr" not in concept
        assert "rdfs:comment_es" not in concept

    def test_concept_jsonld_domain_path(
        self, tmp_schema, write_concept
    ):
        """Domain-specific concept uses domain path in output key."""
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert "concepts/sp/Enrollment.jsonld" in result["jsonld_docs"]
        doc = result["jsonld_docs"]["concepts/sp/Enrollment.jsonld"]
        assert self._concept_node(doc)["@id"] == "https://test.example.org/sp/Enrollment"

    def test_concept_jsonld_supertypes(
        self, tmp_schema, write_concept
    ):
        write_concept("group.yaml", make_concept(id="Group"))
        write_concept("household.yaml", make_concept(
            id="Household", supertypes=["Group"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Household.jsonld"]
        concept = self._concept_node(doc)
        # Supertypes use bare URIs
        assert concept["rdfs:subClassOf"] == ["https://test.example.org/Group"]

    def test_concept_jsonld_properties_in_graph(
        self, tmp_schema, write_concept, write_property
    ):
        """Properties appear as peer nodes in @graph with schema:domainIncludes."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        graph = doc["@graph"]
        # First node is the concept, rest are properties
        assert len(graph) == 2
        prop_node = graph[1]
        assert prop_node["@type"] == "rdf:Property"
        assert not prop_node["@id"].endswith(".jsonld")
        assert prop_node["schema:domainIncludes"] == {"@id": "https://test.example.org/Person"}
        # No ps:properties on the concept node
        assert "ps:properties" not in graph[0]

    def test_property_jsonld_has_bare_uri(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/name.jsonld"]
        assert doc["@id"] == "https://test.example.org/name"
        assert doc["@type"] == "rdf:Property"

    def test_property_jsonld_range_includes_xsd(
        self, tmp_schema, write_concept, write_property
    ):
        """rangeIncludes maps to proper XSD URIs, not raw type strings."""
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/dob.jsonld"]
        assert doc["schema:rangeIncludes"] == "xsd:date"

    def test_property_jsonld_range_includes_geojson_geometry(
        self, tmp_schema, write_concept, write_property
    ):
        """geojson_geometry type maps to GeoJSON-LD Geometry URI for rangeIncludes."""
        write_property("geom.yaml", make_property(id="geom", type="geojson_geometry"))
        write_concept("area.yaml", make_concept(
            id="Area", properties=["geom"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/geom.jsonld"]
        assert doc["schema:rangeIncludes"] == "https://purl.org/geojson/vocab#Geometry"

    def test_property_jsonld_range_includes_concept_uri(
        self, tmp_schema, write_concept, write_property
    ):
        """concept:X references get the concept's bare URI for rangeIncludes."""
        write_property("beneficiary.yaml", make_property(
            id="beneficiary", type="concept:Person",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["beneficiary"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/beneficiary.jsonld"]
        assert doc["schema:rangeIncludes"] == "https://test.example.org/Person"

    def test_property_jsonld_domain_includes(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/name.jsonld"]
        assert "https://test.example.org/Person" in doc["schema:domainIncludes"]

    def test_property_jsonld_language_tagged_comments(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(
            id="name",
            definition={"en": "Name.", "fr": "Nom.", "es": "Nombre."},
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/name.jsonld"]
        comments = doc["rdfs:comment"]
        langs = {c["@language"]: c["@value"] for c in comments}
        assert langs["en"] == "Name."
        assert langs["fr"] == "Nom."
        assert "rdfs:comment_fr" not in doc

    def test_vocabulary_jsonld_skos_scheme(
        self, tmp_schema, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["vocab/gender-type.jsonld"]
        assert doc["@type"] == "skos:ConceptScheme"
        assert not doc["@id"].endswith(".jsonld")

    def test_vocabulary_jsonld_values_are_skos_concepts(
        self, tmp_schema, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(
            id="gender-type",
            values=[
                {"code": "male", "label": {"en": "Male", "fr": "Masculin", "es": "Masculino"},
                 "definition": {"en": "Male.", "fr": "Masculin.", "es": "Masculino."}},
            ],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["vocab/gender-type.jsonld"]
        values = doc["skos:hasTopConcept"]
        assert len(values) == 1
        v = values[0]
        assert v["@type"] == "skos:Concept"
        assert v["skos:notation"] == "male"
        # Language-tagged labels
        labels = {tag["@language"]: tag["@value"] for tag in v["skos:prefLabel"]}
        assert labels["en"] == "Male"
        assert labels["fr"] == "Masculin"
        # No invented properties
        assert "skos:prefLabel_fr" not in v

    def test_vocabulary_jsonld_language_tagged_definition(
        self, tmp_schema, write_vocabulary
    ):
        write_vocabulary("gender-type.yaml", make_vocabulary(
            id="gender-type",
            values=[
                {"code": "male", "label": {"en": "Male", "fr": "M", "es": "M"},
                 "definition": {"en": "Male.", "fr": "Masculin.", "es": "Masculino."}},
            ],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["vocab/gender-type.jsonld"]
        v = doc["skos:hasTopConcept"][0]
        defns = {d["@language"]: d["@value"] for d in v["skos:definition"]}
        assert defns["en"] == "Male."
        assert defns["fr"] == "Masculin."

    def test_jsonld_docs_written_to_dist(
        self, tmp_schema, write_concept, tmp_path
    ):
        """write_outputs() creates dist/jsonld/ with correct files."""
        from build.build import write_outputs
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        dist = tmp_path / "dist"
        write_outputs(result, dist, schema_dir=tmp_schema, source="bespoke")
        jsonld_path = dist / "jsonld" / "concepts" / "Person.jsonld"
        assert jsonld_path.exists()
        doc = json.loads(jsonld_path.read_text())
        assert doc["@graph"][0]["@id"] == "https://test.example.org/Person"

    def test_jsonld_docs_domain_subdir(
        self, tmp_schema, write_concept, tmp_path
    ):
        """Domain-specific concepts write to domain subdirectory."""
        from build.build import write_outputs
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        dist = tmp_path / "dist"
        write_outputs(result, dist, schema_dir=tmp_schema, source="bespoke")
        assert (dist / "jsonld" / "concepts" / "sp" / "Enrollment.jsonld").exists()

    def test_vocabulary_jsonld_domain_specific_uses_prefixed_path(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Domain-scoped vocabulary JSON-LD is keyed under vocab/<domain>/<id>."""
        write_vocabulary("sp/estatus.yaml", make_vocabulary(id="estatus", domain="sp"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="sp/estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        # Key reflects the domain subdirectory so Astro catch-all can serve it
        assert "vocab/sp/estatus.jsonld" in result["jsonld_docs"]
        doc = result["jsonld_docs"]["vocab/sp/estatus.jsonld"]
        assert doc["@id"] == "https://test.example.org/vocab/sp/estatus"


# ---------------------------------------------------------------------------
# Helper: _to_snake_case
# ---------------------------------------------------------------------------

class TestExternalEquivalentsTriples:
    def test_exact_match_emits_skos_exact(self):
        raw = {"id": "X", "external_equivalents": {
            "sys": {"uri": "http://ex/a", "match": "exact"},
        }}
        assert _external_equivalents_triples(raw) == {"skos:exactMatch": ["http://ex/a"]}

    def test_match_none_without_uri_is_silent(self, capsys):
        """match: none declares 'no equivalent'; the missing URI is intentional."""
        raw = {"id": "X", "external_equivalents": {
            "sys": {"match": "none", "label": "N/A"},
        }}
        assert _external_equivalents_triples(raw) == {}
        assert "missing 'uri'" not in capsys.readouterr().err

    def test_missing_uri_without_match_none_warns(self, capsys):
        raw = {"id": "X", "external_equivalents": {
            "sys": {"match": "close", "label": "something"},
        }}
        assert _external_equivalents_triples(raw) == {}
        assert "missing 'uri'" in capsys.readouterr().err


class TestToSnakeCase:
    def test_pascal_to_snake(self):
        assert _to_snake_case("PaymentEvent") == "payment_event"

    def test_single_word(self):
        assert _to_snake_case("Enrollment") == "enrollment"

    def test_already_lower(self):
        assert _to_snake_case("person") == "person"

    def test_multi_caps(self):
        assert _to_snake_case("ScoringEvent") == "scoring_event"


# ---------------------------------------------------------------------------
# Property categories and concept property_groups
# ---------------------------------------------------------------------------

class TestPropertyCategories:
    def test_property_category_passes_through(
        self, tmp_schema, write_concept, write_property
    ):
        """Property category field appears in build output."""
        write_property("dob.yaml", make_property(
            id="dob", type="date", category="demographics",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["dob"]["category"] == "demographics"

    def test_property_without_category_is_null(
        self, tmp_schema, write_concept, write_property
    ):
        """Properties without category have null in output."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["name"]["category"] is None

    def test_concept_property_groups_passes_through(
        self, tmp_schema, write_concept, write_property
    ):
        """Concept property_groups field appears in build output."""
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
        result = build_vocabulary(tmp_schema)
        groups = result["concepts"]["Person"]["property_groups"]
        assert groups is not None
        assert len(groups) == 2
        assert groups[0]["category"] == "demographics"
        assert groups[0]["properties"] == ["dob"]

    def test_concept_without_property_groups_is_null(
        self, tmp_schema, write_concept, write_property
    ):
        """Concepts without property_groups have null/None in output."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["property_groups"] is None

    def test_categories_yaml_loaded(self, tmp_schema, write_concept):
        """categories.yaml is loaded and included in build output."""
        import yaml
        categories = {
            "demographics": {"label": {"en": "Demographics", "fr": "Démographie", "es": "Demografía"}},
            "identity": {"label": {"en": "Identity"}},
        }
        (tmp_schema / "categories.yaml").write_text(yaml.dump(categories, allow_unicode=True))
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert "categories" in result
        assert "demographics" in result["categories"]
        assert result["categories"]["demographics"]["label"]["en"] == "Demographics"

    def test_categories_empty_when_no_file(self, tmp_schema, write_concept):
        """Build succeeds with empty categories when no categories.yaml exists."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["categories"] == {}


# ---------------------------------------------------------------------------
# Featured concepts
# ---------------------------------------------------------------------------

class TestFeaturedConcepts:
    """The featured flag passes through the build pipeline."""

    def test_featured_true_passes_through(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person", featured=True))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["featured"] is True

    def test_featured_defaults_to_false(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["featured"] is False


# ---------------------------------------------------------------------------
# Schema / build output drift detection
# ---------------------------------------------------------------------------

class TestImmutableAfterStatusAnnotation:
    """The immutable_after_status annotation must flow through to RDF output.

    ADR-009 decision 14 resolves this explicitly: emit ps:immutableAfterStatus
    in the JSON-LD (and therefore Turtle), and do NOT emit a sh:PropertyShape
    with a comment-only constraint. SHACL cannot enforce cross-version
    immutability with its standard validators; pretending otherwise would
    mislead adopters about enforcement.
    """

    def test_annotation_emitted_on_concept_property_node(
        self, tmp_schema, write_concept, write_property,
    ):
        write_property("probe.yaml", make_property(
            id="probe", immutable_after_status="given",
        ))
        write_concept("person.yaml", make_concept(id="Person", properties=["probe"]))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        prop_node = next(n for n in doc["@graph"] if n.get("@id", "").endswith("/probe"))
        assert prop_node.get("ps:immutableAfterStatus") == "given"

    def test_annotation_emitted_on_standalone_property_doc(
        self, tmp_schema, write_concept, write_property,
    ):
        write_property("probe.yaml", make_property(
            id="probe", immutable_after_status="given",
        ))
        write_concept("person.yaml", make_concept(id="Person", properties=["probe"]))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/probe.jsonld"]
        assert doc.get("ps:immutableAfterStatus") == "given"

    def test_no_annotation_when_unset(
        self, tmp_schema, write_concept, write_property,
    ):
        write_property("probe.yaml", make_property(id="probe"))
        write_concept("person.yaml", make_concept(id="Person", properties=["probe"]))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/probe.jsonld"]
        assert "ps:immutableAfterStatus" not in doc


class TestPropertyLabel:
    """Property label field passes through the build pipeline."""

    def test_property_label_passes_through(
        self, tmp_schema, write_concept, write_property,
    ):
        """label dict from YAML appears in build output."""
        write_property("dob.yaml", make_property(
            id="dob", type="date",
            label={"en": "Date of birth", "fr": "Date de naissance", "es": "Fecha de nacimiento"},
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        prop = result["properties"]["dob"]
        assert prop["label"] == {
            "en": "Date of birth",
            "fr": "Date de naissance",
            "es": "Fecha de nacimiento",
        }

    def test_property_label_empty_when_absent(
        self, tmp_schema, write_concept, write_property,
    ):
        """Properties without a label field produce an empty dict in output."""
        data = make_property(id="dob", type="date")
        del data["label"]
        write_property("dob.yaml", data)
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        assert result["properties"]["dob"]["label"] == {}

    def test_property_jsonld_rdfs_label_language_tagged(
        self, tmp_schema, write_concept, write_property,
    ):
        """JSON-LD rdfs:label is a list of language-tagged dicts when label exists."""
        write_property("dob.yaml", make_property(
            id="dob", type="date",
            label={"en": "Date of birth", "fr": "Date de naissance"},
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/dob.jsonld"]
        labels = doc["rdfs:label"]
        assert isinstance(labels, list)
        langs = {item["@language"]: item["@value"] for item in labels}
        assert langs["en"] == "Date of birth"
        assert langs["fr"] == "Date de naissance"

    def test_property_jsonld_rdfs_label_fallback_also_tagged(
        self, tmp_schema, write_concept, write_property,
    ):
        """JSON-LD rdfs:label falls back to language-tagged id (not a plain string)."""
        data = make_property(id="dob", type="date")
        del data["label"]
        write_property("dob.yaml", data)
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["properties/dob.jsonld"]
        labels = doc["rdfs:label"]
        assert isinstance(labels, list)
        assert {"@value": "dob", "@language": "en"} in labels

    def test_concept_property_jsonld_rdfs_label_language_tagged(
        self, tmp_schema, write_concept, write_property,
    ):
        """Property nodes in concept @graph also use language-tagged rdfs:label."""
        write_property("dob.yaml", make_property(
            id="dob", type="date",
            label={"en": "Date of birth", "fr": "Date de naissance"},
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["concepts/Person.jsonld"]
        prop_node = doc["@graph"][1]
        labels = prop_node["rdfs:label"]
        assert isinstance(labels, list)
        langs = {item["@language"]: item["@value"] for item in labels}
        assert langs["en"] == "Date of birth"


class TestPropertySchemaDrift:
    """Catch fields defined in property.schema.json but missing from build output."""

    # Fields consumed at build time but intentionally excluded from output.
    BUILD_ONLY_FIELDS = {"domain_override"}

    def test_build_output_covers_all_schema_fields(
        self, tmp_schema, write_concept, write_property,
    ):
        """Every field in property.schema.json appears in build output.

        If this test fails, a field was added to the JSON schema but not
        passed through in build_vocabulary's property output dict.
        Update build.py to include the missing field, or add it to
        BUILD_ONLY_FIELDS if it is intentionally excluded.
        """
        schema_path = self.tmp_schema = (
            Path(__file__).parent.parent / "build" / "schemas" / "property.schema.json"
        )
        with schema_path.open() as f:
            schema_fields = set(json.load(f)["properties"].keys())

        # Build a property that carries every optional field so we can
        # inspect which keys build_vocabulary passes through.
        write_property("probe.yaml", make_property(id="probe"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["probe"],
        ))
        result = build_vocabulary(tmp_schema)
        output_keys = set(result["properties"]["probe"].keys())

        expected = schema_fields - self.BUILD_ONLY_FIELDS
        missing = expected - output_keys
        assert not missing, (
            f"property.schema.json fields not in build output: {sorted(missing)}. "
            f"Add them to build_vocabulary in build.py, or to BUILD_ONLY_FIELDS if intentional."
        )


# ---------------------------------------------------------------------------
# Fix #10: crosswalks_dir kwarg — explicit path overrides schema_dir default
# ---------------------------------------------------------------------------

class TestCrosswalksDir:
    """build_vocabulary(crosswalks_dir=...) loads crosswalks from the given path.

    Regression guard: when --linkml-dir overrides schema_dir in main(),
    crosswalks must still be read from the canonical schema_dir's
    value_crosswalks/, not from the override directory.
    """

    def _make_crosswalk(self, crosswalks_dir: Path, vocab_id: str, sysid: str) -> None:
        """Write a minimal valid crosswalk YAML into crosswalks_dir."""
        import yaml
        doc = {
            "id": f"{vocab_id}--{sysid}",
            "source_value_set": {
                "id": vocab_id, "kind": "vocabulary", "source_id": "publicschema",
            },
            "target_value_set": {"id": "TargetVocab", "source_id": sysid},
            "pairs": [
                {"source_value": "val_a", "target_value": "T1",
                 "quality": "exact", "target_label": "Target One"},
            ],
            "standard": {
                "source_id": sysid, "uri": "https://example.org/",
                "custodian": "X", "license": "X",
                "license_uri": "https://example.org/license",
                "version": "1", "attribution_text": "x",
                "redistribution": "embed-with-attribution",
                "retrieved_at": "2026-01-01",
                "source_sha256": "a" * 64,
            },
        }
        (crosswalks_dir / f"{vocab_id}--{sysid}.yaml").write_text(
            yaml.safe_dump(doc, sort_keys=False), encoding="utf-8"
        )

    def test_crosswalks_loaded_from_explicit_dir(self, tmp_path):
        """Crosswalks in crosswalks_dir are applied even when schema_dir has none.

        The schema lives at tmp_path/schema (no value_crosswalks/ subdir).
        Crosswalks live at tmp_path/cw/. Passing crosswalks_dir=cw must cause
        the crosswalk to be applied; not passing it would silently skip them.
        """
        import yaml

        schema_dir = tmp_path / "schema"
        schema_dir.mkdir()
        (schema_dir / "concepts").mkdir()
        (schema_dir / "properties").mkdir()
        (schema_dir / "vocabularies").mkdir()
        meta = {
            "name": "TestSchema",
            "base_uri": "https://test.example.org/",
            "version": "0.1.0",
            "maturity": "draft",
            "languages": ["en"],
            "license": "CC-BY-4.0",
        }
        (schema_dir / "_meta.yaml").write_text(yaml.dump(meta))

        vocab_id = "test-vocab"
        vocab_data = {
            "id": vocab_id,
            "values": [{"code": "val_a", "label": {"en": "Value A"},
                        "definition": {"en": "First value"}}],
        }
        (schema_dir / "vocabularies" / f"{vocab_id}.yaml").write_text(
            yaml.dump(vocab_data)
        )

        # Crosswalks live in a separate directory (simulating --linkml-dir pointing elsewhere).
        custom_cw = tmp_path / "cw"
        custom_cw.mkdir()
        self._make_crosswalk(custom_cw, vocab_id, "testsys")

        # With explicit crosswalks_dir: crosswalk is applied.
        result_with = build_vocabulary(schema_dir, crosswalks_dir=custom_cw)
        sm_with = result_with["vocabularies"][vocab_id].get("system_mappings", {})
        assert "testsys" in sm_with, (
            f"Crosswalk from custom_cw not applied; system_mappings keys: {list(sm_with)}"
        )

        # Without crosswalks_dir (default): schema_dir has no value_crosswalks/, so none applied.
        result_without = build_vocabulary(schema_dir)
        sm_without = result_without["vocabularies"][vocab_id].get("system_mappings") or {}
        assert "testsys" not in sm_without, (
            "Crosswalk should not be applied when crosswalks_dir is not passed "
            "and schema_dir has no value_crosswalks/ subdir"
        )


@pytest.mark.parametrize("override", [False, True])
def test_cli_forwards_selected_linkml_composite(tmp_path, monkeypatch, override):
    from build import build

    schema = tmp_path / "schema"
    selected = tmp_path / "selected" if override else schema
    calls = {}
    result = {"concepts": {}, "properties": {}, "vocabularies": {}}

    def capture_vocabulary(directory, **kwargs):
        calls["directory"] = directory
        calls["crosswalks"] = kwargs["crosswalks_dir"]
        return result

    def capture_outputs(value, directory, **kwargs):
        calls["outputs"] = kwargs

    monkeypatch.setattr(build, "build_vocabulary", capture_vocabulary)
    monkeypatch.setattr(build, "write_outputs", capture_outputs)
    argv = ["build", str(schema), str(tmp_path / "dist")]
    if override:
        argv.extend(["--linkml-dir", str(selected)])
    monkeypatch.setattr("sys.argv", argv)
    build.main()
    assert calls["directory"] == selected
    assert calls["crosswalks"] == schema / "value_crosswalks"
    assert calls["outputs"]["rdf_composite"] == selected / "publicschema.yaml"
    assert calls["outputs"]["schema_dir"] == schema
    assert calls["outputs"]["source"] == "linkml"


def test_bespoke_build_emits_its_own_rdf_and_static_downloads(
    tmp_schema, write_concept, write_property, tmp_path, monkeypatch,
):
    from build import build, linkml_rdf_export

    def unexpected_linkml(*args, **kwargs):
        pytest.fail("Bespoke output must not load the current LinkML composite")

    for name in ("write_turtle", "write_full_jsonld", "write_shacl"):
        monkeypatch.setattr(linkml_rdf_export, name, unexpected_linkml)
    write_property("amount.yaml", make_property(id="amount", type="decimal"))
    write_concept("sample.yaml", make_concept(id="Sample", properties=["amount"]))
    dist = tmp_path / "output"
    public = tmp_path / "public"
    public.mkdir()
    (public / "Sample.schema.json").write_text('{"stale": true}')
    monkeypatch.setattr("sys.argv", [
        "build", str(tmp_schema), str(dist), "--source", "bespoke",
        "--site-public-dir", str(public),
    ])
    build.main()
    import rdflib

    graph = rdflib.Graph().parse(dist / "publicschema.ttl")
    assert any(graph.triples((rdflib.URIRef("https://test.example.org/Sample"), None, None)))
    schema = json.loads((public / "Sample.schema.json").read_text())
    assert schema["properties"]["amount"]["type"] == "number"
    for suffix in (".csv", "-definition.xlsx", "-template.xlsx"):
        assert (public / f"Sample{suffix}").read_bytes() == (dist / "downloads" / f"Sample{suffix}").read_bytes()
        assert (public / "downloads" / f"Sample{suffix}").read_bytes() == (public / f"Sample{suffix}").read_bytes()
    assert (public / "vocabulary.json").read_bytes() == (dist / "vocabulary.json").read_bytes()
    assert (public / "preview" / "en.json").exists()
    assert json.loads((dist / "metrics_catalog.json").read_text())["meta"]["metric_count"] == 0


def test_rebuild_prunes_renamed_and_retired_generated_artifacts(
    tmp_schema, write_concept, write_property, tmp_path,
):
    """A second build removes only artifacts owned by the earlier build."""
    from build import build

    write_property("farm_name.yaml", make_property(id="farm_name"))
    farm = write_concept("farm.yaml", make_concept(
        id="Farm", properties=["farm_name"],
    ))
    medicinal_product = write_concept("medicinal-product.yaml", make_concept(
        id="MedicinalProduct",
    ))
    dist = tmp_path / "dist"
    public = tmp_path / "public"
    public.mkdir()
    static_asset = public / "robots.txt"
    static_asset.write_text("User-agent: *\n")

    build.write_outputs(
        build.build_vocabulary(tmp_schema), dist, schema_dir=tmp_schema,
        source="bespoke",
    )
    build.prepare_site_artifacts(dist, public)
    assert (public / "Farm.schema.json").exists()
    assert (public / "MedicinalProduct.schema.json").exists()

    write_concept("farm.yaml", make_concept(
        id="Farm", domain="agri", properties=["farm_name"],
    ))
    medicinal_product.unlink()
    build.write_outputs(
        build.build_vocabulary(tmp_schema), dist, schema_dir=tmp_schema,
        source="bespoke",
    )
    # A build-only invocation replaces dist without touching site/public. A
    # later normal build must still recover the last copied public ownership.
    build.write_outputs(
        build.build_vocabulary(tmp_schema), dist, schema_dir=tmp_schema,
        source="bespoke",
    )
    build.prepare_site_artifacts(dist, public)

    assert (dist / "schemas" / "agri" / "Farm.schema.json").exists()
    assert not (dist / "schemas" / "Farm.schema.json").exists()
    assert not (dist / "schemas" / "MedicinalProduct.schema.json").exists()
    assert (dist / "jsonld" / "concepts" / "agri" / "Farm.jsonld").exists()
    assert not (dist / "jsonld" / "concepts" / "Farm.jsonld").exists()
    assert not (dist / "jsonld" / "concepts" / "MedicinalProduct.jsonld").exists()
    assert (dist / "jsonld" / "properties" / "agri" / "farm_name.jsonld").exists()
    assert not (dist / "jsonld" / "properties" / "farm_name.jsonld").exists()
    assert (dist / "downloads" / "agri" / "Farm.csv").exists()
    assert not (dist / "downloads" / "Farm.csv").exists()
    assert not (dist / "downloads" / "MedicinalProduct.csv").exists()
    assert (public / "agri" / "Farm.schema.json").exists()
    assert not (public / "Farm.schema.json").exists()
    assert not (public / "MedicinalProduct.schema.json").exists()
    assert (public / "agri" / "Farm.csv").exists()
    assert (public / "downloads" / "agri" / "Farm.csv").exists()
    assert not (public / "Farm.csv").exists()
    assert not (public / "downloads" / "MedicinalProduct.csv").exists()
    assert static_asset.read_text() == "User-agent: *\n"


def test_write_outputs_passes_explicit_composite_to_all_rdf_generators(
    tmp_schema, write_concept, tmp_path, monkeypatch,
):
    from build import build, linkml_rdf_export

    write_concept("sample.yaml", make_concept(id="Sample"))
    calls = []

    def capture(path, **kwargs):
        calls.append((path.name, kwargs))

    for name in ("write_turtle", "write_full_jsonld", "write_shacl"):
        monkeypatch.setattr(linkml_rdf_export, name, capture)
    composite = tmp_path / "custom" / "publicschema.yaml"
    build.write_outputs(
        build.build_vocabulary(tmp_schema), tmp_path / "output",
        schema_dir=tmp_schema, rdf_composite=composite,
    )
    assert {name for name, _ in calls} == {"publicschema.ttl", "publicschema.jsonld", "publicschema.shacl.ttl"}
    assert all(kwargs["composite"] == composite for _, kwargs in calls)
    assert next(kwargs for name, kwargs in calls if name.endswith(".jsonld"))["context_url"] == "https://test.example.org/ctx/draft.jsonld"


def test_published_metric_observation_preserves_linkml_numeric_value(tmp_path, monkeypatch):
    """The downloaded schema and context preserve the source float contract."""
    from build import build, linkml_rdf_export
    from tests.conftest import SCHEMA_DIR
    import rdflib

    # RDF generators have their own production integration tests. This test
    # follows the public JSON Schema and context through the actual publisher.
    for name in ("write_turtle", "write_full_jsonld", "write_shacl"):
        monkeypatch.setattr(linkml_rdf_export, name, lambda *args, **kwargs: None)
    result = build.build_vocabulary(SCHEMA_DIR)
    dist = tmp_path / "dist"
    public = tmp_path / "public"
    build.write_outputs(result, dist, schema_dir=SCHEMA_DIR)
    build.prepare_site_artifacts(dist, public)

    schema = json.loads((public / "metrics" / "MetricObservation.schema.json").read_text())
    jsonschema.validate({"metric_value": 42.5}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"metric_value": "not a number"}, schema)
    context = json.loads((dist / "context.jsonld").read_text())
    assert context["@context"]["metric_value"]["@type"] == "xsd:float"
    graph = rdflib.Graph().parse(data=json.dumps({
        "@context": context["@context"], "@id": "urn:test:observation", "metric_value": 42.5,
    }), format="json-ld")
    value = graph.value(rdflib.URIRef("urn:test:observation"), rdflib.URIRef("https://publicschema.org/metrics/metric_value"))
    assert value.datatype == rdflib.XSD.float
    assert float(value) == 42.5
    prop = json.loads((dist / "jsonld" / "properties" / "metrics" / "metric_value.jsonld").read_text())
    assert prop["schema:rangeIncludes"] == "xsd:float"


def test_metrics_authored_uris_match_public_context_and_downloads():
    """LinkML RDF identities and the site's domain paths describe the same terms."""
    from build.loader import load_yaml
    from tests.conftest import SCHEMA_DIR

    authored = load_yaml(SCHEMA_DIR / "metrics.yaml")
    result = build_vocabulary(SCHEMA_DIR)
    context = result["context"]["@context"]
    base = authored["prefixes"]["publicschema"]
    for name, definition in authored["classes"].items():
        uri = definition["class_uri"].replace("publicschema:", base, 1)
        concept = result["concepts"][f"metrics/{name}"]
        assert uri == concept["uri"] == context[name]
        assert result["concept_schemas"][f"metrics/{name}"]["$id"] == uri + ".schema.json"
    for name, definition in authored["slots"].items():
        uri = definition["slot_uri"].replace("publicschema:", base, 1)
        term = context[name]
        assert uri == result["properties"][name]["uri"]
        assert uri == (term["@id"] if isinstance(term, dict) else term)


@pytest.mark.parametrize("reverse", [False, True])
def test_context_root_name_precedes_domain_collision_regardless_of_order(reverse):
    from pyld import jsonld

    concepts = {
        "Person": make_concept(id="Person"),
        "crvs/Person": make_concept(id="Person", domain="crvs"),
        "sp/Enrollment": make_concept(id="Enrollment", domain="sp"),
    }
    if reverse:
        concepts = dict(reversed(concepts.items()))
    result = build_vocabulary(raws={"concepts": concepts})
    context = result["context"]["@context"]
    assert context["Person"] == "https://publicschema.org/Person"
    assert context["crvs/Person"] == "https://publicschema.org/crvs/Person"
    assert context["Enrollment"] == context["sp/Enrollment"] == "https://publicschema.org/sp/Enrollment"
    for name, expected in (("Person", "Person"), ("crvs/Person", "crvs/Person")):
        expanded = jsonld.expand({"@context": context, "@id": "urn:test:person", "@type": name})
        assert expanded[0]["@type"] == ["https://publicschema.org/" + expected]


@pytest.mark.parametrize("reverse", [False, True])
def test_context_ambiguous_domain_names_require_qualified_alias(reverse):
    from pyld import jsonld

    concepts = {
        "first/Record": make_concept(id="Record", domain="first"),
        "second/Record": make_concept(id="Record", domain="second"),
    }
    if reverse:
        concepts = dict(reversed(concepts.items()))
    context = build_vocabulary(raws={"concepts": concepts})["context"]["@context"]
    assert "Record" not in context
    for domain in ("first", "second"):
        expected = f"https://publicschema.org/{domain}/Record"
        assert context[f"{domain}/Record"] == expected
        expanded = jsonld.expand({"@context": context, "@id": "urn:test:record", "@type": f"{domain}/Record"})
        assert expanded[0]["@type"] == [expected]


def test_authored_property_uri_preserves_json_field_and_site_path():
    from pyld import jsonld

    result = build_vocabulary(raws={
        "meta": {"base_uri": "https://example.org/"},
        "concepts": {"Record": make_concept(id="Record", properties=["display_name"])},
        "properties": {"display_name": make_property(
            id="display_name", uri="https://example.org/label", type="string",
        )},
    })
    prop = result["properties"]["display_name"]
    assert prop["id"] == "display_name"
    assert prop["path"] == "/display_name"
    assert prop["uri"] == "https://example.org/label"
    assert "display_name" in result["concept_schemas"]["Record"]["properties"]
    context = result["context"]["@context"]
    assert context["display_name"] == "https://example.org/label"
    expanded = jsonld.expand({
        "@context": context, "@id": "urn:test:record", "@type": "Record", "display_name": "Ada",
    })
    assert expanded[0]["https://example.org/label"] == [{"@value": "Ada"}]
    assert result["jsonld_docs"]["properties/display_name.jsonld"]["@id"] == prop["uri"]
