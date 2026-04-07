"""Integration tests that validate and build the real schema directory.

These tests catch issues in the actual YAML content files that unit tests
with synthetic data would miss.
"""

import json
from pathlib import Path

import jsonschema
from pyld import jsonld

from tests.conftest import SCHEMA_DIR

from build.build import build_vocabulary
from build.validate import validate_schema_dir

V2_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = V2_ROOT / "examples"


class TestRealSchema:
    def test_real_schema_validates(self):
        """The real schema directory passes validation with zero errors."""
        errors = validate_schema_dir(SCHEMA_DIR)
        assert errors == [], (
            f"Validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def test_real_schema_builds(self):
        """The real schema builds successfully with expected structure."""
        result = build_vocabulary(SCHEMA_DIR)

        # Check top-level keys exist
        assert "meta" in result
        assert "concepts" in result
        assert "properties" in result
        assert "vocabularies" in result
        assert "context" in result
        assert "concept_schemas" in result

        # Verify counts match what we expect (19 concepts, 91+ properties, 11 vocabularies)
        assert len(result["concepts"]) >= 19, (
            f"Expected at least 19 concepts, got {len(result['concepts'])}"
        )
        assert len(result["properties"]) >= 91, (
            f"Expected at least 91 properties, got {len(result['properties'])}"
        )
        assert len(result["vocabularies"]) >= 10, (
            f"Expected at least 10 vocabularies, got {len(result['vocabularies'])}"
        )

        # Every concept should have a JSON Schema generated
        for concept_id in result["concepts"]:
            assert concept_id in result["concept_schemas"], (
                f"Missing JSON Schema for concept {concept_id}"
            )

        # JSON-LD context should have entries for all concepts and properties
        ctx = result["context"]["@context"]
        for concept_id in result["concepts"]:
            assert concept_id in ctx, f"Missing context entry for concept {concept_id}"
        for prop_id in result["properties"]:
            assert prop_id in ctx, f"Missing context entry for property {prop_id}"

    def test_domain_concepts_have_domain_uris(self):
        """Domain-specific concepts should have domain segments in their URIs."""
        result = build_vocabulary(SCHEMA_DIR)

        # Enrollment is domain: sp
        enrollment = result["concepts"].get("Enrollment")
        assert enrollment is not None, "Enrollment concept not found"
        assert enrollment["domain"] == "sp"
        assert "/sp/Enrollment" in enrollment["uri"]
        assert enrollment["path"] == "/sp/Enrollment"

        # Person is universal (domain: null)
        person = result["concepts"].get("Person")
        assert person is not None, "Person concept not found"
        assert person["domain"] is None
        assert "/sp/" not in person["uri"]
        assert person["path"] == "/Person"

    def test_credential_schemas_generated(self):
        """Credential schemas are generated for all credential YAML files."""
        result = build_vocabulary(SCHEMA_DIR)
        cred_schemas = result.get("credential_schemas", {})
        assert "IdentityCredential" in cred_schemas
        assert "EnrollmentCredential" in cred_schemas
        assert "PaymentCredential" in cred_schemas

    def test_example_vcs_validate_against_schemas(self):
        """All example VC JSON files validate against their credential schemas."""
        result = build_vocabulary(SCHEMA_DIR)
        cred_schemas = result["credential_schemas"]

        examples = {
            "identity-credential.json": "IdentityCredential",
            "enrollment-credential.json": "EnrollmentCredential",
            "payment-credential.json": "PaymentCredential",
        }
        for filename, cred_type in examples.items():
            example_path = EXAMPLES_DIR / filename
            assert example_path.exists(), f"Example file not found: {filename}"
            example = json.loads(example_path.read_text())
            schema = cred_schemas[cred_type]
            jsonschema.validate(
                example, schema,
                format_checker=jsonschema.FormatChecker(),
            )

    def test_jsonld_expansion_resolves_properties(self):
        """JSON-LD expansion using the generated context resolves property URIs."""
        result = build_vocabulary(SCHEMA_DIR)
        ps_context = result["context"]["@context"]

        doc = {
            "@context": ps_context,
            "@type": "Person",
            "given_name": "Amina",
            "date_of_birth": "1988-03-15",
        }
        expanded = jsonld.expand(doc)
        assert len(expanded) == 1
        person = expanded[0]

        # given_name should expand to the PublicSchema URI
        assert "https://publicschema.org/given_name" in person
        assert person["https://publicschema.org/given_name"][0]["@value"] == "Amina"

        # date_of_birth should expand with xsd:date type
        dob = person["https://publicschema.org/date_of_birth"][0]
        assert dob["@value"] == "1988-03-15"
        assert dob["@type"] == "http://www.w3.org/2001/XMLSchema#date"

        # @type should expand to the Person URI
        assert person["@type"] == ["https://publicschema.org/Person"]

    def test_data_classification_annotations_present(self):
        """All properties in the real schema have data_classification annotations."""
        result = build_vocabulary(SCHEMA_DIR)
        missing = []
        for prop_id, prop_data in result["properties"].items():
            if prop_data.get("data_classification") is None:
                missing.append(prop_id)
        assert missing == [], (
            f"{len(missing)} properties missing data_classification: {missing}"
        )

    def test_data_classification_levels_are_valid(self):
        """All data_classification values are one of non_personal, personal, special_category."""
        result = build_vocabulary(SCHEMA_DIR)
        valid = {"non_personal", "personal", "special_category"}
        invalid = []
        for prop_id, prop_data in result["properties"].items():
            s = prop_data.get("data_classification")
            if s not in valid:
                invalid.append((prop_id, s))
        assert invalid == [], f"Invalid data_classification levels: {invalid}"

    def test_jsonld_expansion_schema_org_alias(self):
        """camelCase schema.org aliases expand to the same URIs."""
        result = build_vocabulary(SCHEMA_DIR)
        ps_context = result["context"]["@context"]

        doc = {
            "@context": ps_context,
            "@type": "Person",
            "givenName": "Amina",
        }
        expanded = jsonld.expand(doc)
        person = expanded[0]
        # givenName alias should expand to the same PublicSchema URI as given_name
        assert "https://publicschema.org/given_name" in person
        assert person["https://publicschema.org/given_name"][0]["@value"] == "Amina"
