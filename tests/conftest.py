"""Shared test fixtures for PublicSchema build pipeline tests."""

import copy
import importlib.util
from pathlib import Path

import pytest
import yaml
from pyld import jsonld
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS
from referencing import Registry, Resource

from build.build import build_vocabulary
from build.linkml_rdf_export import DEFAULT_CONTEXT_URL, write_shacl, write_turtle
from build.linkml_reader import load_raw_from_linkml

FIXTURES_DIR = Path(__file__).parent / "fixtures"
V2_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = V2_ROOT / "schema"
BUILD_SCHEMAS_DIR = V2_ROOT / "build" / "schemas"
EXAMPLES_DIR = V2_ROOT / "examples"


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


@pytest.fixture(scope="session")
def built_vocabulary():
    """The real vocabulary build, run once per session.

    Shared by many modules: treat it as read-only and deep-copy anything a
    test changes. Teardown fails if a test mutated it, because later tests
    would otherwise see order-dependent data.
    """
    built = build_vocabulary(SCHEMA_DIR)
    snapshot = copy.deepcopy(built)
    yield built
    assert built == snapshot, "a test mutated the shared built_vocabulary; deep-copy it before changing it"


@pytest.fixture(scope="session")
def schema_registry(built_vocabulary):
    """Offline ``referencing`` registry of the generated concept schemas."""
    return schema_registry_for(built_vocabulary)


@pytest.fixture(scope="session")
def shacl_graph(tmp_path_factory):
    """The production SHACL export of the real schema, generated once."""
    path = tmp_path_factory.mktemp("shacl") / "publicschema.shacl.ttl"
    return Graph().parse(write_shacl(path), format="turtle")


@pytest.fixture(scope="session")
def owl_graph(tmp_path_factory):
    """The production OWL Turtle export of the real schema, generated once."""
    path = tmp_path_factory.mktemp("owl") / "publicschema.ttl"
    return Graph().parse(write_turtle(path), format="turtle")


@pytest.fixture(scope="session")
def subclass_hierarchy(owl_graph):
    """Named-class ``rdfs:subClassOf`` triples from the OWL export.

    ``sh:class`` follows ``rdfs:subClassOf*`` in the data graph, so SHACL
    checks of references to abstract ranges need this hierarchy, either as
    pySHACL's ``ont_graph`` or merged into the data graph.
    """
    hierarchy = Graph()
    for child, parent in owl_graph.subject_objects(RDFS.subClassOf):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            hierarchy.add((child, RDFS.subClassOf, parent))
    return hierarchy


def schema_registry_for(built: dict) -> Registry:
    """Resolve generated concept schema references without network access."""
    return Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema))
        for schema in built["concept_schemas"].values()
    )


def load_example(relative_path: str):
    """Import an example script (``examples/<dir>/<file>.py``) as a module.

    Example directories contain hyphens, so they are loaded by path rather
    than imported as packages, the same way the scripts run from the CLI.
    """
    path = EXAMPLES_DIR / relative_path
    name = "example_" + "_".join(path.with_suffix("").relative_to(EXAMPLES_DIR).parts).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jsonld_graph(
    document, context: dict, hierarchy: Graph | None = None, *, context_url: str = DEFAULT_CONTEXT_URL,
) -> Graph:
    """Convert JSON-LD data to RDF through PyLD n-quads.

    ``document`` is a list of records, a record, or a full document whose
    ``@context`` may name ``context_url``; that URL resolves to ``context``
    (the generated ``{"@context": ...}`` document) offline, and any other
    remote document fails the test.
    PyLD is the standards conversion: RDFLib's direct JSON-LD parser keeps
    Python numbers for ``xsd:decimal`` and causes false pySHACL datatype
    errors. ``hierarchy`` triples are merged into the returned graph.
    """
    if isinstance(document, list):
        document = {"@context": context["@context"], "@graph": document}
    elif "@context" not in document:
        document = {"@context": context["@context"], **document}

    def loader(url, options=None):
        assert url == context_url, f"Unexpected remote document: {url}"
        return {"contextUrl": None, "documentUrl": url, "document": context}

    quads = jsonld.to_rdf(document, {"format": "application/n-quads", "documentLoader": loader})
    graph = Graph().parse(data=quads, format="nquads")
    if hierarchy is not None:
        graph += hierarchy
    return graph


def _key_by_short_id(elements: dict) -> dict:
    """Re-key a ``<domain>/<id>`` dict by bare ``<id>``.

    The bespoke-format tests look up entries by their declared ``id``
    (e.g. ``"PaternityRecognition"``); the build pipeline keys them as
    ``"crvs/PaternityRecognition"`` to disambiguate cross-domain collisions.
    Prefer the root concept when it shares a name with a domain snapshot.
    Tests that need both entries use the composite-keyed fixture instead.
    """
    out: dict = {}
    for k, v in elements.items():
        short = k.split("/")[-1]
        if short not in out or k == short:
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
