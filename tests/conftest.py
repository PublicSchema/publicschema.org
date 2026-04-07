"""Shared test fixtures for PublicSchema build pipeline tests."""

import json
from pathlib import Path

import pytest
import yaml


FIXTURES_DIR = Path(__file__).parent / "fixtures"
V2_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = V2_ROOT / "schema"
BUILD_SCHEMAS_DIR = V2_ROOT / "build" / "schemas"


@pytest.fixture
def tmp_schema(tmp_path):
    """Create a minimal valid schema directory for testing."""
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()
    (schema_dir / "concepts").mkdir()
    (schema_dir / "properties").mkdir()
    (schema_dir / "vocabularies").mkdir()

    meta = {
        "name": "TestSchema",
        "base_uri": "https://test.example.org/",
        "version": "0.1.0",
        "maturity": "draft",
        "languages": ["en", "fr", "es"],
        "license": "CC-BY-4.0",
    }
    (schema_dir / "_meta.yaml").write_text(yaml.dump(meta, allow_unicode=True))

    return schema_dir


@pytest.fixture
def write_concept(tmp_schema):
    """Helper to write a concept YAML file into the tmp schema."""
    def _write(filename, data):
        path = tmp_schema / "concepts" / filename
        path.write_text(yaml.dump(data, allow_unicode=True))
        return path
    return _write


@pytest.fixture
def write_property(tmp_schema):
    """Helper to write a property YAML file into the tmp schema."""
    def _write(filename, data):
        path = tmp_schema / "properties" / filename
        path.write_text(yaml.dump(data, allow_unicode=True))
        return path
    return _write


@pytest.fixture
def write_credential(tmp_schema):
    """Helper to write a credential YAML file into the tmp schema."""
    def _write(filename, data):
        creds_dir = tmp_schema / "credentials"
        creds_dir.mkdir(exist_ok=True)
        path = creds_dir / filename
        path.write_text(yaml.dump(data, allow_unicode=True))
        return path
    return _write


@pytest.fixture
def write_vocabulary(tmp_schema):
    """Helper to write a vocabulary YAML file into the tmp schema."""
    def _write(filename, data):
        path = tmp_schema / "vocabularies" / filename
        path.write_text(yaml.dump(data, allow_unicode=True))
        return path
    return _write


def make_concept(id="Person", **overrides):
    """Create a minimal valid concept dict."""
    data = {
        "id": id,
        "maturity": "draft",
        "definition": {
            "en": f"A test {id}.",
            "fr": f"Un test {id}.",
            "es": f"Un test {id}.",
        },
        "properties": [],
    }
    data.update(overrides)
    return data


def make_property(id="test_field", type="string", **overrides):
    """Create a minimal valid property dict."""
    data = {
        "id": id,
        "maturity": "draft",
        "definition": {
            "en": f"A test property {id}.",
            "fr": f"Un test {id}.",
            "es": f"Un test {id}.",
        },
        "type": type,
        "cardinality": "single",
    }
    data.update(overrides)
    return data


def make_credential(id="TestCredential", **overrides):
    """Create a minimal valid credential type dict."""
    data = {
        "id": id,
        "maturity": "draft",
        "definition": {
            "en": f"A test credential {id}.",
            "fr": f"Un test {id}.",
            "es": f"Un test {id}.",
        },
        "subject_concept": "Person",
        "included_concepts": [],
    }
    data.update(overrides)
    return data


def make_vocabulary(id="test-vocab", **overrides):
    """Create a minimal valid vocabulary dict."""
    data = {
        "id": id,
        "maturity": "draft",
        "definition": {
            "en": "A test vocabulary.",
            "fr": "Un vocabulaire test.",
            "es": "Un vocabulario test.",
        },
        "values": [
            {
                "code": "value_a",
                "label": {"en": "Value A", "fr": "Valeur A", "es": "Valor A"},
                "definition": {"en": "First value.", "fr": "Premiere valeur.", "es": "Primer valor."},
            }
        ],
    }
    data.update(overrides)
    return data
