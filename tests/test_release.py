"""Tests for the release snapshot mechanism."""

import json
from pathlib import Path

import pytest
import yaml

from build.release import create_release


@pytest.fixture
def release_env(tmp_path):
    """Set up a minimal schema dir and a populated dist dir for release testing."""
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()
    meta = {
        "name": "TestSchema",
        "base_uri": "https://test.example.org/",
        "version": "0.2.0",
        "maturity": "trial-use",
        "languages": ["en", "fr", "es"],
        "license": "CC-BY-4.0",
    }
    (schema_dir / "_meta.yaml").write_text(yaml.dump(meta, allow_unicode=True))

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "vocabulary.json").write_text('{"meta": {}}')
    (dist_dir / "context.jsonld").write_text('{"@context": {}}')
    schemas_dir = dist_dir / "schemas"
    schemas_dir.mkdir()
    (schemas_dir / "person.schema.json").write_text('{}')

    releases_dir = tmp_path / "releases"

    return schema_dir, dist_dir, releases_dir


class TestCreateRelease:
    """Release snapshot creation."""

    def test_creates_versioned_directory(self, release_env):
        """Release creates releases/{version}/ with the dist contents."""
        schema_dir, dist_dir, releases_dir = release_env
        release_path = create_release(schema_dir, dist_dir, releases_dir)

        assert release_path.exists()
        assert release_path.name == "0.2.0"
        assert (release_path / "vocabulary.json").exists()
        assert (release_path / "context.jsonld").exists()
        assert (release_path / "schemas" / "person.schema.json").exists()

    def test_creates_versions_json(self, release_env):
        """Release creates/updates versions.json with the release entry."""
        schema_dir, dist_dir, releases_dir = release_env
        create_release(schema_dir, dist_dir, releases_dir)

        versions_path = releases_dir / "versions.json"
        assert versions_path.exists()

        versions = json.loads(versions_path.read_text())
        assert len(versions["releases"]) == 1
        entry = versions["releases"][0]
        assert entry["version"] == "0.2.0"
        assert entry["maturity"] == "trial-use"
        assert "date" in entry

    def test_appends_to_existing_versions_json(self, release_env):
        """A second release appends to the existing versions.json."""
        schema_dir, dist_dir, releases_dir = release_env

        # First release
        create_release(schema_dir, dist_dir, releases_dir)

        # Bump version for second release
        meta_path = schema_dir / "_meta.yaml"
        meta = yaml.safe_load(meta_path.read_text())
        meta["version"] = "0.3.0"
        meta_path.write_text(yaml.dump(meta, allow_unicode=True))

        create_release(schema_dir, dist_dir, releases_dir)

        versions = json.loads((releases_dir / "versions.json").read_text())
        assert len(versions["releases"]) == 2
        assert versions["releases"][0]["version"] == "0.2.0"
        assert versions["releases"][1]["version"] == "0.3.0"

    def test_rejects_duplicate_version(self, release_env):
        """Creating a release for an existing version raises ValueError."""
        schema_dir, dist_dir, releases_dir = release_env
        create_release(schema_dir, dist_dir, releases_dir)

        with pytest.raises(ValueError, match="already exists"):
            create_release(schema_dir, dist_dir, releases_dir)

    def test_rejects_empty_dist(self, release_env):
        """Creating a release with no dist output raises FileNotFoundError."""
        schema_dir, dist_dir, releases_dir = release_env

        empty_dist = dist_dir.parent / "empty_dist"
        empty_dist.mkdir()

        with pytest.raises(FileNotFoundError, match="does not exist or is empty"):
            create_release(schema_dir, empty_dist, releases_dir)

    def test_rejects_missing_dist(self, release_env):
        """Creating a release when dist/ doesn't exist raises FileNotFoundError."""
        schema_dir, dist_dir, releases_dir = release_env

        missing_dist = dist_dir.parent / "no_such_dir"

        with pytest.raises(FileNotFoundError, match="does not exist or is empty"):
            create_release(schema_dir, missing_dist, releases_dir)
