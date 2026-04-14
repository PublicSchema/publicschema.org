"""Shared YAML loading helpers for the build pipeline."""

from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    """Load a single YAML file, returning an empty dict for empty/missing content."""
    return yaml.safe_load(path.read_text()) or {}


def load_all_yaml(directory: Path) -> dict[str, dict]:
    """Load all YAML files from a directory, keyed by filename."""
    result = {}
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        result[p.name] = load_yaml(p)
    return result


def load_vocabularies_with_paths(directory: Path) -> list[tuple[Path, dict]]:
    """Load vocabulary YAMLs with their relative paths for domain validation."""
    result = []
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        rel = p.relative_to(directory)
        result.append((rel, load_yaml(p)))
    return result
