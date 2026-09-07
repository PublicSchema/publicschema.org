"""Test-only semantic reader for the authored LinkML source.

These helpers keep tests focused on PublicSchema terms and mappings instead
of the historical ``schema/concepts`` / ``schema/properties`` file layout.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from build.linkml_reader import load_raw_from_linkml
from tests.conftest import SCHEMA_DIR


@lru_cache
def raw_schema(schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    return load_raw_from_linkml(schema_dir)


def concept(key: str) -> dict[str, Any]:
    return raw_schema()["concepts"][key]


def property_(key: str) -> dict[str, Any]:
    return raw_schema()["properties"][key]


def vocabulary(key: str) -> dict[str, Any]:
    return raw_schema()["vocabularies"][key]


def bibliography(key: str) -> dict[str, Any]:
    return raw_schema()["bibliography"][key]


def subtypes_of(parent: str) -> set[str]:
    return {
        key
        for key, item in raw_schema()["concepts"].items()
        if parent in item.get("supertypes", [])
    }
