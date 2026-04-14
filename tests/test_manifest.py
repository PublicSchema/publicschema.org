"""Tests for manifest.json generation.

The manifest is a machine-readable index of all published artifacts
and their URLs. It is generated in write_outputs() after all other
artifacts are written.
"""

import json

import pytest

from build.build import build_vocabulary, write_outputs
from tests.conftest import SCHEMA_DIR


@pytest.fixture(scope="module")
def build_result():
    return build_vocabulary(SCHEMA_DIR)


@pytest.fixture(scope="module")
def manifest(build_result, tmp_path_factory):
    """Build outputs and return the parsed manifest.json."""
    dist_dir = tmp_path_factory.mktemp("dist")
    write_outputs(build_result, dist_dir)
    manifest_path = dist_dir / "manifest.json"
    assert manifest_path.exists(), "manifest.json was not generated"
    return json.loads(manifest_path.read_text())


class TestManifestStructure:
    def test_top_level_keys(self, manifest):
        """Manifest has required top-level keys."""
        expected = {"name", "version", "maturity", "base_uri", "artifacts", "concepts", "vocabularies", "credentials"}
        assert expected == set(manifest.keys())

    def test_meta_fields(self, manifest):
        """Manifest meta fields match _meta.yaml values."""
        assert manifest["name"] == "PublicSchema"
        assert manifest["version"] == "0.2.0"
        assert manifest["maturity"] == "draft"
        assert manifest["base_uri"] == "https://publicschema.org/"

    def test_artifacts_keys(self, manifest):
        """Artifacts section lists the global artifact URLs."""
        artifacts = manifest["artifacts"]
        expected = {"context", "vocabulary", "turtle", "jsonld", "shacl"}
        assert expected == set(artifacts.keys())

    def test_artifacts_are_paths(self, manifest):
        """Each artifact value is a URL path starting with /."""
        for key, path in manifest["artifacts"].items():
            assert path.startswith("/"), f"Artifact {key} path should start with /: {path}"


class TestManifestCounts:
    def test_concept_count_matches(self, manifest, build_result):
        """Number of concepts in manifest matches build result."""
        assert len(manifest["concepts"]) == len(build_result["concepts"])

    def test_vocabulary_count_matches(self, manifest, build_result):
        """Number of vocabularies in manifest matches build result."""
        assert len(manifest["vocabularies"]) == len(build_result["vocabularies"])

    def test_credential_count_matches(self, manifest, build_result):
        """Number of credentials in manifest matches build result."""
        assert len(manifest["credentials"]) == len(build_result.get("credential_schemas", {}))


class TestManifestConceptEntries:
    def test_concept_has_expected_keys(self, manifest):
        """Each concept entry has schema, jsonld, csv, xlsx_definition, xlsx_template."""
        for concept_id, entry in manifest["concepts"].items():
            expected = {"schema", "jsonld", "csv", "xlsx_definition", "xlsx_template"}
            assert expected == set(entry.keys()), f"Concept {concept_id} has wrong keys: {entry.keys()}"

    def test_concept_paths_start_with_slash(self, manifest):
        """All concept artifact paths start with /."""
        for concept_id, entry in manifest["concepts"].items():
            for key, path in entry.items():
                assert path.startswith("/"), (
                    f"Concept {concept_id} {key} should start with /: {path}"
                )


class TestManifestVocabularyEntries:
    def test_vocabulary_has_jsonld(self, manifest):
        """Each vocabulary entry has a jsonld key."""
        for vocab_id, entry in manifest["vocabularies"].items():
            assert "jsonld" in entry, f"Vocabulary {vocab_id} missing jsonld key"

    def test_vocabulary_paths_start_with_slash(self, manifest):
        """All vocabulary artifact paths start with /."""
        for vocab_id, entry in manifest["vocabularies"].items():
            for key, path in entry.items():
                assert path.startswith("/"), (
                    f"Vocabulary {vocab_id} {key} should start with /: {path}"
                )


class TestManifestCredentialEntries:
    def test_credential_has_schema(self, manifest, build_result):
        """Each credential entry has a schema key (if credentials exist)."""
        if not build_result.get("credential_schemas"):
            pytest.skip("No credentials in build result")
        for cred_id, entry in manifest["credentials"].items():
            assert "schema" in entry, f"Credential {cred_id} missing schema key"


class TestManifestPathCorrectness:
    """Verify that manifest paths correspond to real files and follow naming rules."""

    @pytest.fixture(scope="class")
    def dist_with_manifest(self, tmp_path_factory):
        """Build outputs and return (dist_dir, manifest)."""
        result = build_vocabulary(SCHEMA_DIR)
        dist_dir = tmp_path_factory.mktemp("dist_paths")
        write_outputs(result, dist_dir)
        manifest = json.loads((dist_dir / "manifest.json").read_text())
        return dist_dir, manifest, result

    def test_concept_schema_files_exist(self, dist_with_manifest):
        """Every concept schema path in the manifest corresponds to a real file."""
        dist_dir, manifest, _ = dist_with_manifest
        for concept_id, entry in manifest["concepts"].items():
            # Schema path is /schemas/Concept.schema.json -> dist/schemas/Concept.schema.json
            schema_rel = entry["schema"].lstrip("/")
            assert (dist_dir / schema_rel).exists(), (
                f"Concept {concept_id} schema file missing: {schema_rel}"
            )

    def test_concept_jsonld_files_exist(self, dist_with_manifest):
        """Every concept jsonld path in the manifest corresponds to a real file."""
        dist_dir, manifest, _ = dist_with_manifest
        for concept_id, entry in manifest["concepts"].items():
            # jsonld path like /Person.jsonld or /sp/Enrollment.jsonld
            # maps to dist/jsonld/concepts/Person.jsonld or dist/jsonld/concepts/sp/Enrollment.jsonld
            jsonld_path = entry["jsonld"]  # e.g. "/sp/Enrollment.jsonld"
            jsonld_rel = "jsonld/concepts" + jsonld_path
            assert (dist_dir / jsonld_rel).exists(), (
                f"Concept {concept_id} jsonld file missing: {jsonld_rel}"
            )

    def test_vocabulary_jsonld_files_exist(self, dist_with_manifest):
        """Every vocabulary jsonld path in the manifest corresponds to a real file."""
        dist_dir, manifest, _ = dist_with_manifest
        for vocab_id, entry in manifest["vocabularies"].items():
            jsonld_rel = "jsonld/" + entry["jsonld"].lstrip("/")
            assert (dist_dir / jsonld_rel).exists(), (
                f"Vocabulary {vocab_id} jsonld file missing: {jsonld_rel}"
            )

    def test_credential_schema_files_exist(self, dist_with_manifest):
        """Every credential schema path in the manifest corresponds to a real file."""
        dist_dir, manifest, result = dist_with_manifest
        if not result.get("credential_schemas"):
            pytest.skip("No credentials in build result")
        for cred_id, entry in manifest["credentials"].items():
            schema_rel = entry["schema"].lstrip("/")
            assert (dist_dir / schema_rel).exists(), (
                f"Credential {cred_id} schema file missing: {schema_rel}"
            )

    def test_domain_concept_has_domain_jsonld_path(self, dist_with_manifest):
        """Domain-specific concepts have domain segment in their jsonld path."""
        _, manifest, result = dist_with_manifest
        for concept_id, concept in result["concepts"].items():
            if concept.get("domain"):
                entry = manifest["concepts"][concept_id]
                assert entry["jsonld"].startswith(f"/{concept['domain']}/"), (
                    f"Domain concept {concept_id} should have /{concept['domain']}/ "
                    f"prefix in jsonld path, got {entry['jsonld']}"
                )

    def test_domain_concept_has_flat_schema_path(self, dist_with_manifest):
        """Domain-specific concepts still use flat /schemas/ path (no domain prefix)."""
        _, manifest, result = dist_with_manifest
        for concept_id, concept in result["concepts"].items():
            if concept.get("domain"):
                entry = manifest["concepts"][concept_id]
                assert entry["schema"] == f"/schemas/{concept_id}.schema.json", (
                    f"Domain concept {concept_id} schema should be flat, "
                    f"got {entry['schema']}"
                )

    def test_download_files_exist(self, dist_with_manifest):
        """Every download path (CSV, XLSX) in the manifest corresponds to a real file."""
        dist_dir, manifest, _ = dist_with_manifest
        for concept_id, entry in manifest["concepts"].items():
            for key in ["csv", "xlsx_definition", "xlsx_template"]:
                rel = entry[key].lstrip("/")
                assert (dist_dir / rel).exists(), (
                    f"Concept {concept_id} {key} file missing: {rel}"
                )

    def test_domain_concept_download_paths_include_domain(self, dist_with_manifest):
        """Domain-specific concepts have domain prefix in download paths."""
        _, manifest, result = dist_with_manifest
        for concept_id, concept in result["concepts"].items():
            if concept.get("domain"):
                domain = concept["domain"]
                entry = manifest["concepts"][concept_id]
                assert entry["csv"] == f"/downloads/{domain}/{concept_id}.csv", (
                    f"Domain concept {concept_id} csv should include /{domain}/, "
                    f"got {entry['csv']}"
                )
