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

# VC context URL used in the examples
_VC_CONTEXT_URL = "https://www.w3.org/ns/credentials/v2"

# Minimal W3C VC Data Model 2.0 context stub -- enough for the terms used in
# our examples. This avoids network calls during testing.
_VC_CONTEXT_STUB = {
    "@context": {
        "@version": 1.1,
        "@protected": True,
        "id": "@id",
        "type": "@type",
        "VerifiableCredential": {
            "@id": "https://www.w3.org/2018/credentials#VerifiableCredential",
        },
        "credentialSubject": {
            "@id": "https://www.w3.org/2018/credentials#credentialSubject",
            "@type": "@id",
        },
        "issuer": {
            "@id": "https://www.w3.org/2018/credentials#issuer",
            "@type": "@id",
        },
        "validFrom": {
            "@id": "https://www.w3.org/2018/credentials#validFrom",
            "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        },
        "validUntil": {
            "@id": "https://www.w3.org/2018/credentials#validUntil",
            "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        },
        "credentialSchema": {
            "@id": "https://www.w3.org/2018/credentials#credentialSchema",
            "@type": "@id",
        },
        "credentialStatus": {
            "@id": "https://www.w3.org/2018/credentials#credentialStatus",
            "@type": "@id",
        },
    }
}


def _make_document_loader():
    """Return a pyld document loader that stubs the W3C VC context URL."""
    from pyld import jsonld as _jsonld

    def loader(url, options):
        if url == _VC_CONTEXT_URL:
            return {
                "document": _VC_CONTEXT_STUB,
                "documentUrl": url,
                "contextUrl": None,
                "contentType": "application/ld+json",
            }
        raise _jsonld.JsonLdError(
            f"No document loader for URL: {url}",
            "jsonld.LoadDocumentError",
            {"url": url},
            code="loading remote context failed",
        )

    return loader


def _classify_example(path: Path) -> str:
    """Return "vc", "sd-jwt", or "unknown" based on file content and name."""
    if "-sd" in path.name:
        return "sd-jwt"
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return "unknown"
    if "@context" in data and "credentialSubject" in data:
        return "vc"
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
        """Each example file validates against its credential schema (VC) or
        has the correct SD-JWT structure."""
        kind = _classify_example(example_path)
        example = json.loads(example_path.read_text())

        if kind == "vc":
            result = build_vocabulary(SCHEMA_DIR)
            cred_schemas = result["credential_schemas"]

            # Find the credential type: the entry in "type" that is not "VerifiableCredential"
            type_list = example.get("type", [])
            cred_type = next(
                (t for t in type_list if t != "VerifiableCredential"),
                None,
            )
            assert cred_type is not None, (
                f"{example_path.name}: could not determine credential type from {type_list}"
            )
            assert cred_type in cred_schemas, (
                f"{example_path.name}: no credential schema found for type '{cred_type}'"
            )
            jsonschema.validate(
                example,
                cred_schemas[cred_type],
                format_checker=jsonschema.FormatChecker(),
            )

        elif kind == "sd-jwt":
            assert "iss" in example, f"{example_path.name}: missing 'iss'"
            assert "vct" in example, f"{example_path.name}: missing 'vct'"
            assert "_sd_alg" in example, f"{example_path.name}: missing '_sd_alg'"
            assert "sub" in example, f"{example_path.name}: missing 'sub'"
            assert "cnf" in example, f"{example_path.name}: missing 'cnf'"
            assert "@context" not in example, (
                f"{example_path.name}: SD-JWT must not have '@context'"
            )
            assert "type" not in example, (
                f"{example_path.name}: SD-JWT must not have 'type'"
            )

        else:
            pytest.skip(f"{example_path.name}: unrecognized file type, skipping")

    @pytest.mark.parametrize(
        "example_path",
        _example_params([p for p in _all_example_paths() if _classify_example(p) == "vc"]),
    )
    def test_vc_examples_expand_with_jsonld(self, example_path: Path):
        """VC examples expand correctly using the generated JSON-LD context."""
        result = build_vocabulary(SCHEMA_DIR)
        ps_context = result["context"]["@context"]

        example = json.loads(example_path.read_text())

        # Replace every non-VC context entry with the inline PS context dict so
        # expansion works without any HTTP fetches. The VC context URL is kept
        # so the stub document loader can serve it.
        original_ctx = example.get("@context", [])
        inline_ctx = [
            _VC_CONTEXT_URL if entry == _VC_CONTEXT_URL else ps_context
            for entry in original_ctx
        ]
        example["@context"] = inline_ctx

        expanded = jsonld.expand(example, {"documentLoader": _make_document_loader()})
        assert len(expanded) >= 1, (
            f"{example_path.name}: JSON-LD expansion produced no results"
        )

        credential = expanded[0]

        # credentialSubject properties should resolve to full URIs, not compact keys
        cs_key = "https://www.w3.org/2018/credentials#credentialSubject"
        assert cs_key in credential, (
            f"{example_path.name}: credentialSubject did not expand to a full URI"
        )
        subject = credential[cs_key][0]
        # Every key in the expanded subject should be a full URI (no bare property names)
        for key in subject:
            if key == "@type" or key == "@id":
                continue
            assert key.startswith("http"), (
                f"{example_path.name}: property '{key}' did not expand to a full URI"
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
