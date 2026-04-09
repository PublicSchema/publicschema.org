"""Integration tests that validate and build the real schema directory.

These tests catch issues in the actual YAML content files that unit tests
with synthetic data would miss.
"""

import json
from pathlib import Path

import jsonschema
import pytest
from pyld import jsonld

from tests.conftest import SCHEMA_DIR

from build.build import build_vocabulary
from build.validate import validate_schema_dir

V2_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = V2_ROOT / "examples"


def _classify_example(path: Path) -> str:
    """Return "sd-jwt" or "unknown" based on file content."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return "unknown"
    if "vct" in data and "iss" in data:
        return "sd-jwt"
    return "unknown"


def _all_example_paths() -> list[Path]:
    """Return all example JSON file paths, sorted for stable ordering."""
    return sorted(EXAMPLES_DIR.glob("*.json"))


def _example_params(paths: list[Path] | None = None):
    """Collect pytest.param entries for the given paths (defaults to all)."""
    if paths is None:
        paths = _all_example_paths()
    return [pytest.param(p, id=p.name) for p in paths]


class TestRealSchema:
    def test_real_schema_validates(self):
        """The real schema directory passes validation with zero errors."""
        issues = validate_schema_dir(SCHEMA_DIR)
        errors = [e for e in issues if e.severity == "error"]
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

    @pytest.mark.parametrize("example_path", _example_params(_all_example_paths()))
    def test_example_validates(self, example_path: Path):
        """Each SD-JWT VC example validates against its credential schema."""
        kind = _classify_example(example_path)
        example = json.loads(example_path.read_text())

        if kind == "sd-jwt":
            # Structural checks for SD-JWT VC
            assert "iss" in example, f"{example_path.name}: missing 'iss'"
            assert "vct" in example, f"{example_path.name}: missing 'vct'"
            assert "iat" in example, f"{example_path.name}: missing 'iat'"
            assert "@context" not in example, (
                f"{example_path.name}: SD-JWT VC must not have '@context'"
            )

            # Validate against generated schema
            result = build_vocabulary(SCHEMA_DIR)
            cred_schemas = result["credential_schemas"]

            # Extract credential type from vct URI
            vct = example["vct"]
            cred_type = vct.rsplit("/", 1)[-1] if "/" in vct else vct
            assert cred_type in cred_schemas, (
                f"{example_path.name}: no credential schema found for type '{cred_type}'"
            )
            jsonschema.validate(
                example,
                cred_schemas[cred_type],
                format_checker=jsonschema.FormatChecker(),
            )

        else:
            pytest.skip(f"{example_path.name}: unrecognized file type, skipping")

    def test_sd_jwt_examples_have_no_vc_fields(self):
        """SD-JWT VC examples must not contain W3C VCDM fields."""
        for path in _all_example_paths():
            example = json.loads(path.read_text())
            if _classify_example(path) != "sd-jwt":
                continue
            assert "@context" not in example, (
                f"{path.name}: SD-JWT VC must not have '@context'"
            )
            assert "type" not in example or isinstance(example.get("type"), str), (
                f"{path.name}: SD-JWT VC must not have W3C 'type' array"
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

        # given_name should expand to the PublicSchema bare URI
        assert "https://publicschema.org/given_name" in person
        assert person["https://publicschema.org/given_name"][0]["@value"] == "Amina"

        # date_of_birth should expand with xsd:date type
        dob = person["https://publicschema.org/date_of_birth"][0]
        assert dob["@value"] == "1988-03-15"
        assert dob["@type"] == "http://www.w3.org/2001/XMLSchema#date"

        # @type should expand to the Person bare URI
        assert person["@type"] == ["https://publicschema.org/Person"]

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
        # givenName alias should expand to the same PublicSchema bare URI as given_name
        assert "https://publicschema.org/given_name" in person
        assert person["https://publicschema.org/given_name"][0]["@value"] == "Amina"
