"""Tests for the build pipeline.

TDD: these tests define expected behavior before implementation.
"""

import json

import jsonschema
import pytest

from build.build import build_vocabulary
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
        """Context includes @vocab, xsd, and schema prefixes."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["@vocab"] == "https://test.example.org/"
        assert ctx["xsd"] == "http://www.w3.org/2001/XMLSchema#"
        assert ctx["schema"] == "https://schema.org/"

    def test_context_has_versioned_id(
        self, tmp_schema, write_concept
    ):
        """Context document has a versioned @id from _meta.yaml version."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        context = result["context"]
        assert context["@id"] == "https://test.example.org/ctx/v0.1"

    def test_context_concept_has_jsonld_uri(
        self, tmp_schema, write_concept
    ):
        """Concepts in context use .jsonld URIs for static-host dereferencing."""
        write_concept("person.yaml", make_concept(id="Person"))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["Person"] == "https://test.example.org/Person.jsonld"

    def test_context_string_property_has_jsonld_uri(
        self, tmp_schema, write_concept, write_property
    ):
        """String properties use .jsonld URIs in the context."""
        write_property("name.yaml", make_property(id="name", type="string"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["name"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["name"] == "https://test.example.org/name.jsonld"

    def test_context_date_property_has_xsd_type(
        self, tmp_schema, write_concept, write_property
    ):
        """Date properties get @type: xsd:date coercion with .jsonld URI."""
        write_property("dob.yaml", make_property(id="dob", type="date"))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["dob"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["dob"] == {
            "@id": "https://test.example.org/dob.jsonld",
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
            "@id": "https://test.example.org/created.jsonld",
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
            "@id": "https://test.example.org/amount.jsonld",
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
            "@id": "https://test.example.org/count.jsonld",
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
            "@id": "https://test.example.org/active.jsonld",
            "@type": "xsd:boolean",
        }

    def test_context_concept_ref_property_has_id_type(
        self, tmp_schema, write_concept, write_property
    ):
        """Properties referencing a concept get @type: @id with .jsonld URI."""
        write_property("beneficiary.yaml", make_property(
            id="beneficiary", type="concept:Person",
        ))
        write_concept("person.yaml", make_concept(
            id="Person", properties=["beneficiary"],
        ))
        result = build_vocabulary(tmp_schema)
        ctx = result["context"]["@context"]
        assert ctx["beneficiary"] == {
            "@id": "https://test.example.org/beneficiary.jsonld",
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
            "@id": "https://test.example.org/link.jsonld",
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
        assert ctx["Enrollment"] == "https://test.example.org/sp/Enrollment.jsonld"
        assert ctx["enrollment_status"] == "https://test.example.org/sp/enrollment_status.jsonld"

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
        assert ctx["given_name"] == "https://test.example.org/given_name.jsonld"
        # schema.org alias resolves to the same PublicSchema URI
        assert ctx["givenName"] == "https://test.example.org/given_name.jsonld"

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
            "@id": "https://test.example.org/dob.jsonld",
            "@type": "xsd:date",
        }
        assert ctx["birthDate"] == {
            "@id": "https://test.example.org/dob.jsonld",
            "@type": "xsd:date",
        }

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
        """Credential schema has VC envelope: type array, credentialSubject with concept properties."""
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

        # VC envelope structure
        props = schema["properties"]
        assert "type" in props
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
                "https://test.example.org/ctx/v0.1",
            ],
            "type": ["VerifiableCredential", "IdentityCredential"],
            "credentialSubject": {
                "type": "Person",
                "name": "Amina Diallo",
            },
        }
        jsonschema.validate(example, schema)
