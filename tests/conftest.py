"""Shared test fixtures for PublicSchema build pipeline tests."""

from pathlib import Path

import pytest
import yaml

from build.linkml_reader import load_raw_from_linkml

FIXTURES_DIR = Path(__file__).parent / "fixtures"
V2_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = V2_ROOT / "schema"
BUILD_SCHEMAS_DIR = V2_ROOT / "build" / "schemas"


def _load_real_schema() -> dict:
    """Load the canonical LinkML schema once per session.

    Post-cutover, the real schema/ holds LinkML files. Most legacy tests
    were authored against the bespoke per-element YAML shape. This loader
    re-projects the LinkML composite back to that shape via
    ``build.linkml_reader.load_raw_from_linkml`` so the tests can read
    ``concept["external_equivalents"]`` etc. unchanged.
    """
    return load_raw_from_linkml(SCHEMA_DIR)


@pytest.fixture(scope="session")
def real_schema():
    """Full re-projected raws dict from the canonical schema/."""
    return _load_real_schema()


def _key_by_short_id(elements: dict) -> dict:
    """Re-key a ``<domain>/<id>`` dict by bare ``<id>``.

    The bespoke-format tests look up entries by their declared ``id``
    (e.g. ``"PaternityRecognition"``); the build pipeline keys them as
    ``"crvs/PaternityRecognition"`` to disambiguate cross-domain collisions.
    Across the current schema there are no short-id collisions, so the
    re-keying is loss-free.
    """
    out: dict = {}
    for k, v in elements.items():
        short = k.split("/")[-1]
        out[short] = v
    return out


@pytest.fixture(scope="session")
def all_concepts(real_schema):
    """Map of concept id -> bespoke-shaped concept dict."""
    return _key_by_short_id(real_schema["concepts"])


@pytest.fixture(scope="session")
def all_concepts_keyed(real_schema):
    """Map of ``<domain>/<id>`` -> bespoke-shaped concept dict (build-style)."""
    return real_schema["concepts"]


@pytest.fixture(scope="session")
def all_properties(real_schema):
    """Map of property id -> bespoke-shaped property dict."""
    return _key_by_short_id(real_schema["properties"])


@pytest.fixture(scope="session")
def all_vocabularies(real_schema):
    """Map of vocabulary id -> bespoke-shaped vocabulary dict.

    Universal vocabularies are keyed by bare ``<id>``; domain-scoped ones
    keep the ``<domain>/<id>`` form because cross-domain consumers
    (``test_opencrvs_mapping``) reference them by that compound key.
    """
    out: dict = {}
    for k, v in real_schema["vocabularies"].items():
        out[k] = v
    return out


@pytest.fixture(scope="session")
def all_vocabularies_short(real_schema):
    """Vocabularies keyed by bare ``<id>``."""
    return _key_by_short_id(real_schema["vocabularies"])


@pytest.fixture(scope="session")
def all_bibliography(real_schema):
    """Map of bibliography id -> bespoke-shaped citation dict."""
    return real_schema.get("bibliography", {})


@pytest.fixture(scope="session")
def all_credentials(real_schema):
    """Map of credential id -> bespoke-shaped credential dict."""
    return real_schema.get("credentials", {})


@pytest.fixture(scope="session")
def all_categories(real_schema):
    """Map of category id -> bespoke-shaped category dict."""
    return real_schema.get("categories", {})


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
    """Helper to write a vocabulary YAML file into the tmp schema.

    Filenames may include subdirectory segments (e.g. ``'sp/estatus.yaml'``)
    which are interpreted as domain subdirectories under ``vocabularies/``.
    """
    def _write(filename, data):
        path = tmp_schema / "vocabularies" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
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
        "label": {
            "en": id.replace("_", " ").capitalize(),
            "fr": f"Libellé {id}",
            "es": f"Etiqueta {id}",
        },
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
