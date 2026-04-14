"""Creates versioned release snapshots from build output.

Copies the contents of dist/ into releases/{version}/ and maintains
a releases/versions.json index. Refuses to overwrite an existing
version (safety check).
"""

import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml


def create_release(
    schema_dir: Path,
    dist_dir: Path,
    releases_dir: Path,
) -> Path:
    """Create a versioned release snapshot.

    Reads the version from schema_dir/_meta.yaml, copies dist_dir contents
    into releases_dir/{version}/, and updates releases_dir/versions.json.

    Returns the path to the created release directory.

    Raises ValueError if the version already exists in releases_dir.
    Raises FileNotFoundError if dist_dir does not exist or is empty.
    """
    meta_path = schema_dir / "_meta.yaml"
    meta = yaml.safe_load(meta_path.read_text())
    version = meta.get("version", "0.0.0")

    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        raise FileNotFoundError(
            f"dist directory {dist_dir} does not exist or is empty. Run the build first."
        )

    release_path = releases_dir / version
    if release_path.exists():
        raise ValueError(
            f"Release {version} already exists at {release_path}. "
            f"Bump the version in {meta_path} before creating a new release."
        )

    # Copy dist/ to releases/{version}/
    shutil.copytree(dist_dir, release_path)

    # Update versions.json
    versions_path = releases_dir / "versions.json"
    if versions_path.exists():
        versions = json.loads(versions_path.read_text())
    else:
        versions = {"releases": []}

    versions["releases"].append({
        "version": version,
        "date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "maturity": meta.get("maturity", "draft"),
    })

    releases_dir.mkdir(parents=True, exist_ok=True)
    versions_path.write_text(
        json.dumps(versions, indent=2, ensure_ascii=False) + "\n"
    )

    return release_path


def main():
    """CLI entry point for release creation."""
    schema_dir = Path("schema")
    dist_dir = Path("dist")
    releases_dir = Path("releases")

    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        dist_dir = Path(sys.argv[2])
    if len(sys.argv) > 3:
        releases_dir = Path(sys.argv[3])

    release_path = create_release(schema_dir, dist_dir, releases_dir)
    print(f"Release created at {release_path}")


if __name__ == "__main__":
    main()
