"""Integration tests that load all generated JSON-LD into a single rdflib graph.

These tests check structural invariants that only the RDF graph can reveal.
They do not duplicate checks already done at the YAML level by validate.py.

The graph is built once per test session (module scope) because parsing ~50k
triples is expensive. Each test asserts a different structural property of the
combined graph.

Context note: each JSON-LD document references a hosted context URL that will
not resolve in tests. We replace it with the inline context dict produced by
build_vocabulary(), then add explicit @type:@id coercions for predicates that
carry URI values (schema:domainIncludes, schema:rangeIncludes, rdfs:subClassOf,
ps:subtypes, ps:references). Without these coercions rdflib would parse those
values as plain literals instead of URIRefs, which would break every invariant
that follows URI edges.
"""

import json

import pytest
import rdflib
from rdflib.namespace import RDF, RDFS, SKOS, XSD

from build.build import build_vocabulary
from tests.conftest import SCHEMA_DIR

SCHEMA = rdflib.Namespace("https://schema.org/")
PS = rdflib.Namespace("https://publicschema.org/meta/")
BASE_URI = "https://publicschema.org/"

# GeoJSON geometry URI used as a rangeIncludes target for geojson_geometry properties.
GEOJSON_GEOMETRY_URI = rdflib.URIRef("https://purl.org/geojson/vocab#Geometry")


def _build_context_with_coercions(ctx_inline: dict) -> dict:
    """Return the inline context with explicit @type:@id coercions added.

    The generated context maps concept and property names to URIs but does not
    declare how schema:domainIncludes, schema:rangeIncludes, rdfs:subClassOf,
    ps:subtypes, or ps:references values should be treated. Without coercions,
    rdflib parses string values for those predicates as plain literals. Adding
    @type:@id tells the JSON-LD processor to treat those strings as URIRefs.
    """
    ctx = dict(ctx_inline)
    ctx["schema:domainIncludes"] = {
        "@id": "https://schema.org/domainIncludes",
        "@type": "@id",
    }
    ctx["schema:rangeIncludes"] = {
        "@id": "https://schema.org/rangeIncludes",
        "@type": "@id",
    }
    ctx["rdfs:subClassOf"] = {
        "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "@type": "@id",
        "@container": "@set",
    }
    ctx["ps:subtypes"] = {
        "@id": "https://publicschema.org/meta/subtypes",
        "@type": "@id",
        "@container": "@set",
    }
    ctx["ps:references"] = {
        "@id": "https://publicschema.org/meta/references",
        "@type": "@id",
    }
    return ctx


@pytest.fixture(scope="module")
def graph():
    """Build the vocabulary and load all JSON-LD documents into a single rdflib graph.

    This fixture runs once per test module. It:
    1. Calls build_vocabulary() against the real schema directory.
    2. Replaces the hosted @context URL in each document with the inline context.
    3. Adds @type:@id coercions for URI-valued predicates.
    4. Parses every document into a single shared graph.

    Returns a tuple (graph, build_result) so individual tests can also inspect
    the raw build output if needed.
    """
    result = build_vocabulary(SCHEMA_DIR)
    ctx = _build_context_with_coercions(result["context"]["@context"])

    g = rdflib.Graph()
    for _path, doc in result["jsonld_docs"].items():
        copy = dict(doc)
        copy["@context"] = ctx
        g.parse(data=json.dumps(copy), format="json-ld")

    return g, result


class TestDomainIncludesTargetsExist:
    """Every schema:domainIncludes object must be a known rdfs:Class.

    If a property claims to belong to a concept but that concept was never
    emitted as an rdfs:Class node, the graph is internally inconsistent. This
    catches transformation bugs such as a missing concept document or a typo
    in a used_by list.
    """

    def test_domain_includes_targets_exist(self, graph):
        g, _result = graph

        classes = frozenset(
            s for s, p, o in g.triples((None, RDF.type, RDFS.Class))
        )

        violations = []
        for subj, _pred, obj in g.triples((None, SCHEMA.domainIncludes, None)):
            if not isinstance(obj, rdflib.URIRef):
                continue
            if obj not in classes:
                violations.append(
                    f"Property <{subj}> has domainIncludes <{obj}> "
                    f"but that URI is not typed as rdfs:Class in the graph."
                )

        assert violations == [], (
            f"Found {len(violations)} domainIncludes target(s) with no corresponding rdfs:Class:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestRangeIncludesTargetsAreValid:
    """Every schema:rangeIncludes object must be a recognized type reference.

    Valid targets are:
    - XSD datatype URIs (http://www.w3.org/2001/XMLSchema#...)
    - Known concept URIs (subject of rdf:type rdfs:Class)
    - The GeoJSON geometry URI (https://purl.org/geojson/vocab#Geometry)

    Anything else is a broken type reference, most likely caused by a typo
    in a property YAML type field or a missing range-to-URI mapping in the
    build pipeline.
    """

    def test_range_includes_targets_are_valid(self, graph):
        g, _result = graph

        classes = frozenset(
            s for s, p, o in g.triples((None, RDF.type, RDFS.Class))
        )
        xsd_prefix = str(XSD)

        violations = []
        for subj, _pred, obj in g.triples((None, SCHEMA.rangeIncludes, None)):
            if not isinstance(obj, rdflib.URIRef):
                continue
            obj_str = str(obj)
            if obj_str.startswith(xsd_prefix):
                continue
            if obj in classes:
                continue
            if obj == GEOJSON_GEOMETRY_URI:
                continue
            violations.append(
                f"Property <{subj}> has rangeIncludes <{obj}> "
                f"which is not an XSD type, a known concept, or the GeoJSON geometry URI."
            )

        assert violations == [], (
            f"Found {len(violations)} invalid rangeIncludes target(s):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestSubclassChainsAreAcyclic:
    """No class should be a subclass of itself, directly or transitively.

    A cycle in the rdfs:subClassOf graph would make subclass reasoning
    undefined and break any tooling that follows subclass chains. This test
    detects cycles by doing a depth-first traversal of the full transitive
    closure.
    """

    def test_subclass_chains_are_acyclic(self, graph):
        g, _result = graph

        # Build adjacency list: class -> set of direct superclasses
        superclasses: dict[rdflib.URIRef, set[rdflib.URIRef]] = {}
        for subj, _pred, obj in g.triples((None, RDFS.subClassOf, None)):
            if isinstance(subj, rdflib.URIRef) and isinstance(obj, rdflib.URIRef):
                superclasses.setdefault(subj, set()).add(obj)

        def has_cycle(start: rdflib.URIRef) -> bool:
            """Return True if start can reach itself via rdfs:subClassOf."""
            visited: set[rdflib.URIRef] = set()
            stack = list(superclasses.get(start, set()))
            while stack:
                node = stack.pop()
                if node == start:
                    return True
                if node in visited:
                    continue
                visited.add(node)
                stack.extend(superclasses.get(node, set()))
            return False

        violations = [
            str(cls)
            for cls in superclasses
            if has_cycle(cls)
        ]

        assert violations == [], (
            f"Found {len(violations)} class(es) involved in rdfs:subClassOf cycle(s):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestNoDanglingConceptReferences:
    """URI objects of rdfs:subClassOf, ps:subtypes, and ps:references must exist as subjects.

    A dangling reference means the build emitted a link to a concept URI that
    was never itself emitted as a document. This is a sign of a broken
    cross-reference in the YAML (e.g., a supertype or reference that points to
    a concept that was renamed or deleted).

    Only publicschema.org URIs are checked; external URIs (XSD, GeoJSON, etc.)
    are allowed to have no in-graph subject.
    """

    def test_no_dangling_concept_references(self, graph):
        g, _result = graph

        all_subjects = frozenset(s for s, _p, _o in g)

        subtypes_pred = rdflib.URIRef("https://publicschema.org/meta/subtypes")
        references_pred = rdflib.URIRef("https://publicschema.org/meta/references")

        candidate_predicates = [RDFS.subClassOf, subtypes_pred, references_pred]

        violations = []
        for pred in candidate_predicates:
            for _subj, _p, obj in g.triples((None, pred, None)):
                if not isinstance(obj, rdflib.URIRef):
                    continue
                if not str(obj).startswith(BASE_URI):
                    continue
                if obj not in all_subjects:
                    violations.append(
                        f"URI <{obj}> appears as object of <{pred}> "
                        f"but is never a subject in the graph (dangling reference)."
                    )

        assert violations == [], (
            f"Found {len(violations)} dangling concept reference(s):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestDPVNamespacePinning:
    """Every DPV URI cited in external_equivalents must resolve in the pinned snapshot.

    ADR-009 decision 20: we reference DPV URIs (dpv:, dpv-gdpr:) as external
    equivalents on concepts, properties, and vocabularies. Those URIs must exist
    as classes or properties in the pinned Turtle snapshot under external/dpv/.
    This test parses the snapshots with rdflib and checks each cited URI
    resolves to rdfs:Class / rdf:Property / owl:Class / owl:ObjectProperty /
    owl:DatatypeProperty. Prevents silent drift when DPV releases URI changes.
    """

    DPV_PREFIXES = ("dpv:", "dpv-gdpr:")
    DPV_SNAPSHOTS = (
        ("external/dpv/dpv-v2.ttl", "https://w3id.org/dpv#", "dpv:"),
        (
            "external/dpv/dpv-gdpr-v2.ttl",
            "https://w3id.org/dpv/legal/eu/gdpr#",
            "dpv-gdpr:",
        ),
    )

    @pytest.fixture(scope="class")
    def dpv_graph(self):
        """Parse all pinned DPV snapshots into a single rdflib graph."""
        from pathlib import Path

        root = Path(__file__).parent.parent
        g = rdflib.Graph()
        for rel_path, _ns, _prefix in self.DPV_SNAPSHOTS:
            path = root / rel_path
            assert path.is_file(), (
                f"Pinned DPV snapshot missing: {path}. Refresh per external/dpv/manifest.yaml."
            )
            g.parse(path, format="turtle")
        return g

    @pytest.fixture(scope="class")
    def dpv_term_uris(self, dpv_graph):
        """Collect every URI that is typed as a class or property in the snapshots."""
        OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
        type_targets = (
            RDFS.Class,
            RDF.Property,
            OWL.Class,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
        )
        uris = set()
        for target in type_targets:
            for s, _p, _o in dpv_graph.triples((None, RDF.type, target)):
                if isinstance(s, rdflib.URIRef):
                    uris.add(str(s))
        return uris

    def test_cited_dpv_uris_resolve(self, dpv_graph, dpv_term_uris):
        from pathlib import Path

        import yaml

        root = Path(__file__).parent.parent
        cited = set()
        schema_dir = root / "schema"
        for sub in ("concepts", "properties", "vocabularies"):
            for yaml_path in (schema_dir / sub).rglob("*.yaml"):
                with yaml_path.open() as f:
                    data = yaml.safe_load(f) or {}
                eq = data.get("external_equivalents") or {}
                for key, entry in eq.items():
                    if not key.startswith(self.DPV_PREFIXES):
                        continue
                    uri = (entry or {}).get("uri")
                    if uri:
                        cited.add(uri)
                values = data.get("values") or []
                for v in values:
                    v_eq = (v or {}).get("external_equivalents") or {}
                    for key, entry in v_eq.items():
                        if not key.startswith(self.DPV_PREFIXES):
                            continue
                        uri = (entry or {}).get("uri")
                        if uri:
                            cited.add(uri)

        # Every cited DPV URI must exist as a class or property in the snapshots.
        missing = sorted(uri for uri in cited if uri not in dpv_term_uris)
        assert missing == [], (
            f"Cited DPV URIs not present as class/property in pinned snapshots:\n"
            + "\n".join(f"  - {u}" for u in missing)
            + "\nRefresh snapshot per external/dpv/manifest.yaml or fix the YAML."
        )


class TestVocabularyValuesHaveNotation:
    """Every skos:Concept must have a skos:notation triple.

    skos:notation carries the machine-readable value code (e.g., 'male',
    'active'). If it is missing for any value, that value's code was dropped
    during the transformation from YAML to JSON-LD, which would break any
    system that reads codes from the RDF graph.
    """

    def test_vocabulary_values_have_notation(self, graph):
        g, _result = graph

        skos_concepts = frozenset(
            s for s, p, o in g.triples((None, RDF.type, SKOS.Concept))
        )
        with_notation = frozenset(
            s for s, p, o in g.triples((None, SKOS.notation, None))
        )

        missing = skos_concepts - with_notation

        assert missing == set(), (
            f"Found {len(missing)} skos:Concept(s) without a skos:notation triple:\n"
            + "\n".join(f"  - {uri}" for uri in sorted(str(u) for u in missing))
        )
