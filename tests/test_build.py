"""Tests for the build pipeline.

TDD: these tests define expected behavior before implementation.
"""

import json
import re

import jsonschema
import pytest

from build.build import build_vocabulary, _to_snake_case
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
        assert result["concepts"]["Enrollment"]["uri"] == "https://test.example.org/sp/Enrollment"

    def test_domain_concept_path(self, tmp_schema, write_concept):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Enrollment"]["path"] == "/sp/Enrollment"

    def test_universal_concept_path(self, tmp_schema, write_concept):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Person"]["path"] == "/Person"

    def test_concept_domain_field_preserved(self, tmp_schema, write_concept):
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert result["concepts"]["Enrollment"]["domain"] == "sp"

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

    def test_vocabulary_flat_values_omit_hierarchy_fields(
        self, tmp_schema, write_vocabulary
    ):
        """Flat vocabulary values (no level/parent_code) omit those fields."""
        write_vocabulary("gender-type.yaml", make_vocabulary(id="gender-type"))
        result = build_vocabulary(tmp_schema)
        value = result["vocabularies"]["gender-type"]["values"][0]
        assert "level" not in value
        assert "parent_code" not in value

    def test_vocabulary_uri_domain_specific(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Vocabulary referenced only by domain-specific properties gets a domain URI."""
        write_vocabulary("estatus.yaml", make_vocabulary(id="estatus"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["estatus"]
        assert vocab["uri"] == "https://test.example.org/sp/vocab/estatus"
        assert vocab["domain"] == "sp"

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
        """Domain-specific vocabulary gets a domain path."""
        write_vocabulary("estatus.yaml", make_vocabulary(id="estatus"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        vocab = result["vocabularies"]["estatus"]
        assert vocab["path"] == "/sp/vocab/estatus"


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

    def test_credential_schema_wraps_concept_in_vc_envelope(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """Credential schema has VC envelope with required fields and concept properties."""
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

        # Required fields
        assert "required" in schema
        assert "@context" in schema["required"]
        assert "issuer" in schema["required"]

        # VC envelope structure
        props = schema["properties"]
        assert "type" in props
        assert "issuer" in props
        assert "credentialSubject" in props

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
            included_concepts=["Enrollment"],
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

    def test_credential_schema_validates_example(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """A valid example VC validates against the generated credential schema."""
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
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://test.example.org/ctx/v0.1.jsonld",
            ],
            "type": ["VerifiableCredential", "IdentityCredential"],
            "issuer": "did:web:example.gov",
            "credentialSubject": {
                "type": "Person",
                "name": "Amina Diallo",
            },
        }
        jsonschema.validate(example, schema)

    def test_credential_schema_rejects_missing_required_fields(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """A document without @context or issuer fails validation."""
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        write_credential("identity.yaml", make_credential(
            id="IdentityCredential", subject_concept="Person",
        ))
        result = build_vocabulary(tmp_schema)
        schema = result["credential_schemas"]["IdentityCredential"]

        # Missing @context and issuer
        bad_example = {
            "type": ["VerifiableCredential", "IdentityCredential"],
            "credentialSubject": {"name": "Test"},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad_example, schema)

    def test_credential_schema_rejects_empty_context_array(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """An empty @context array fails validation (minItems)."""
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
            "@context": [],
            "type": ["VerifiableCredential", "IdentityCredential"],
            "issuer": "did:web:example.gov",
            "credentialSubject": {"name": "Test"},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad_example, schema)

    def test_credential_schema_rejects_wrong_context_first_element(
        self, tmp_schema, write_concept, write_property, write_credential
    ):
        """@context with wrong first element fails validation."""
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
            "@context": ["https://wrong.example.com"],
            "type": ["VerifiableCredential", "IdentityCredential"],
            "issuer": "did:web:example.gov",
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


# ---------------------------------------------------------------------------
# JSON-LD document generation
# ---------------------------------------------------------------------------

class TestJsonLdDocuments:
    def test_concept_jsonld_has_bare_uri(
        self, tmp_schema, write_concept
    ):
        """Concept JSON-LD @id is the bare URI (no .jsonld suffix)."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        docs = result["jsonld_docs"]
        doc = docs["Person.jsonld"]
        assert doc["@id"] == "https://test.example.org/Person"
        assert not doc["@id"].endswith(".jsonld")

    def test_concept_jsonld_type_is_rdfs_class(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["Person.jsonld"]
        assert doc["@type"] == "rdfs:Class"

    def test_concept_jsonld_has_context_url(
        self, tmp_schema, write_concept
    ):
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["Person.jsonld"]
        assert doc["@context"] == "https://test.example.org/ctx/v0.1.jsonld"

    def test_concept_jsonld_language_tagged_comments(
        self, tmp_schema, write_concept
    ):
        """rdfs:comment uses language-tagged values, not invented rdfs:comment_fr."""
        write_concept("person.yaml", make_concept(
            id="Person",
            definition={"en": "A person.", "fr": "Une personne.", "es": "Una persona."},
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["Person.jsonld"]
        comments = doc["rdfs:comment"]
        assert isinstance(comments, list)
        langs = {c["@language"]: c["@value"] for c in comments}
        assert langs["en"] == "A person."
        assert langs["fr"] == "Une personne."
        assert langs["es"] == "Una persona."
        # No invented properties
        assert "rdfs:comment_fr" not in doc
        assert "rdfs:comment_es" not in doc

    def test_concept_jsonld_domain_path(
        self, tmp_schema, write_concept
    ):
        """Domain-specific concept uses domain path in output key."""
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp",
        ))
        result = build_vocabulary(tmp_schema)
        assert "sp/Enrollment.jsonld" in result["jsonld_docs"]
        doc = result["jsonld_docs"]["sp/Enrollment.jsonld"]
        assert doc["@id"] == "https://test.example.org/sp/Enrollment"

    def test_concept_jsonld_supertypes(
        self, tmp_schema, write_concept
    ):
        write_concept("group.yaml", make_concept(id="Group"))
        write_concept("household.yaml", make_concept(
            id="Household", supertypes=["Group"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["Household.jsonld"]
        # Supertypes use bare URIs
        assert doc["rdfs:subClassOf"] == ["https://test.example.org/Group"]

    def test_concept_jsonld_embedded_properties(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["Person.jsonld"]
        props = doc["ps:properties"]
        assert len(props) == 1
        assert props[0]["@type"] == "rdf:Property"
        assert not props[0]["@id"].endswith(".jsonld")

    def test_property_jsonld_has_bare_uri(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["name.jsonld"]
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
        doc = result["jsonld_docs"]["dob.jsonld"]
        assert doc["schema:rangeIncludes"] == "xsd:date"

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
        doc = result["jsonld_docs"]["beneficiary.jsonld"]
        assert doc["schema:rangeIncludes"] == "https://test.example.org/Person"

    def test_property_jsonld_domain_includes(
        self, tmp_schema, write_concept, write_property
    ):
        write_property("name.yaml", make_property(id="name"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        doc = result["jsonld_docs"]["name.jsonld"]
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
        doc = result["jsonld_docs"]["name.jsonld"]
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
        labels = {l["@language"]: l["@value"] for l in v["skos:prefLabel"]}
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
        write_outputs(result, dist)
        jsonld_path = dist / "jsonld" / "Person.jsonld"
        assert jsonld_path.exists()
        doc = json.loads(jsonld_path.read_text())
        assert doc["@id"] == "https://test.example.org/Person"

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
        write_outputs(result, dist)
        assert (dist / "jsonld" / "sp" / "Enrollment.jsonld").exists()

    def test_vocabulary_jsonld_domain_specific_uses_flat_path(
        self, tmp_schema, write_concept, write_property, write_vocabulary
    ):
        """Domain-specific vocabulary JSON-LD is keyed under vocab/ (no domain segment)."""
        write_vocabulary("estatus.yaml", make_vocabulary(id="estatus"))
        write_property("enrollment_status.yaml", make_property(
            id="enrollment_status", vocabulary="estatus",
        ))
        write_concept("enrollment.yaml", make_concept(
            id="Enrollment", domain="sp", properties=["enrollment_status"],
        ))
        result = build_vocabulary(tmp_schema)
        # Key should be flat vocab/ path so Astro endpoint can find it
        assert "vocab/estatus.jsonld" in result["jsonld_docs"]
        # The @id still contains the domain
        doc = result["jsonld_docs"]["vocab/estatus.jsonld"]
        assert "/sp/vocab/estatus" in doc["@id"]


# ---------------------------------------------------------------------------
# Helper: _to_snake_case
# ---------------------------------------------------------------------------

class TestToSnakeCase:
    def test_pascal_to_snake(self):
        assert _to_snake_case("PaymentEvent") == "payment_event"

    def test_single_word(self):
        assert _to_snake_case("Enrollment") == "enrollment"

    def test_already_lower(self):
        assert _to_snake_case("person") == "person"

    def test_multi_caps(self):
        assert _to_snake_case("AssessmentEvent") == "assessment_event"
