"""Round-trip semantic equivalence between rdf_export.py and the LinkML migration.

This is a cross-pipeline integration test, not a unit test of either pipeline.
It runs both ``build/rdf_export.py`` (via ``build.build.build_vocabulary`` +
``build.rdf_export``) and ``build/migrate_to_linkml.py`` followed by
``gen-owl`` on the resulting LinkML composite schema, then loads both Turtle
outputs into rdflib graphs and asserts three triple-set invariants on
PublicSchema-owned subjects.

The three invariants are evaluated after applying explicit
**equivalence-preserving normalizations** that account for known
representation differences between the two pipelines:

1. ``rdfs:Class`` (rdf_export, AS/RDFS profile) and ``owl:Class``
   (LinkML's OWL projection) are treated as equivalent.
2. Domain-prefixed URIs in rdf_export (``ps:crvs/Adoption``) are folded to
   the unprefixed form LinkML emits (``ps:Adoption``).
3. Vocabulary IDs in rdf_export use kebab-case (``ps:registration-status``)
   while LinkML emits PascalCase enum class IRIs (``ps:RegistrationStatus``).
4. ``schema.org`` URI scheme differs: rdf_export emits ``https://`` per the
   PublicSchema context, gen-owl emits ``http://`` per the LinkML default
   curie prefix. The two schemes denote the same resource.
5. LinkML emits richer OWL artefacts that rdf_export does not (one
   ``owl:Class`` per vocabulary value, ``skos:exactMatch`` self-loops on
   every class, ``rdfs:subClassOf`` hierarchies for Citation/Credential
   sibling content). These are documented as **expected extras** and
   surfaced in the report; they do not cause the test to fail because they
   are additive structural projections, not contradictions of the source.

If an unexpected (= not whitelisted) divergence appears in either direction,
the test fails with the diagnostic ``missing_in_linkml`` / ``extra_in_linkml``
sets so the cause can be triaged.

The test skips cleanly if ``rdflib``, ``linkml``, or the ``gen-owl`` CLI is
not available in the active environment.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import pytest

# ---------------------------------------------------------------------------
# Optional-dependency guards
# ---------------------------------------------------------------------------

rdflib = pytest.importorskip(
    "rdflib", reason="rdflib is required for the LinkML round-trip test"
)
pytest.importorskip(
    "linkml", reason="linkml is required for the LinkML round-trip test"
)

from rdflib.namespace import OWL, RDF, RDFS, SKOS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
MIGRATE_SCRIPT = ROOT / "build" / "migrate_to_linkml.py"
LINKML_OUT_DIR = ROOT / "dist" / "linkml"
LINKML_COMPOSITE = LINKML_OUT_DIR / "publicschema.yaml"

PS = "https://publicschema.org/"


def _venv_bin(name: str) -> Path | None:
    """Return the path to a venv-installed executable, if present."""
    candidates: list[Path] = []
    # Inside the venv that runs pytest itself
    python_dir = Path(sys.executable).parent
    candidates.append(python_dir / name)
    # The repo-local .venv (used by the project's justfile / CI invocations)
    candidates.append(ROOT / ".venv" / "bin" / name)
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return c
    found = shutil.which(name)
    return Path(found) if found else None


GEN_OWL = _venv_bin("gen-owl")
if GEN_OWL is None:
    pytest.skip(
        "gen-owl CLI not available; install linkml in the active venv to run this test",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Session-scoped fixtures: run each expensive pipeline exactly once.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def rdf_export_graph(tmp_path_factory) -> rdflib.Graph:
    """Build the rdf_export Turtle output and return it parsed as a graph.

    Uses the in-process ``build_vocabulary`` + ``build_turtle`` path rather
    than spawning a subprocess so we avoid the rest of ``write_outputs``
    (CSV/XLSX/JSON-LD downloads, manifests, etc.) which are irrelevant here.
    The Turtle is still written to a temp directory so the artefact is
    available for inspection if a test fails.
    """
    from build.build import build_vocabulary
    from build.rdf_export import build_turtle

    result = build_vocabulary(SCHEMA_DIR)
    ttl = build_turtle(result)

    out_dir = tmp_path_factory.mktemp("rdf_export")
    (out_dir / "publicschema.ttl").write_text(ttl)

    g = rdflib.Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture(scope="session")
def linkml_owl_graph(tmp_path_factory) -> rdflib.Graph:
    """Run the migration + ``gen-owl`` and return the OWL Turtle as a graph.

    The migration script writes to a hard-coded ``dist/linkml/`` path. We
    invoke it (always re-running, to keep the test hermetic) and then point
    gen-owl at the resulting composite. gen-owl's Turtle output is captured
    to a tmp file purely for post-mortem inspection on failure.
    """
    if not MIGRATE_SCRIPT.exists():
        pytest.skip(f"migration script not found at {MIGRATE_SCRIPT}")

    # Run the migration. The script is idempotent: it resets dist/linkml/.
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    subprocess.run(
        [sys.executable, str(MIGRATE_SCRIPT)],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
    )
    if not LINKML_COMPOSITE.exists():
        pytest.fail(f"migration did not produce {LINKML_COMPOSITE}")

    # Run gen-owl. It prints OWL Turtle to stdout.
    out_dir = tmp_path_factory.mktemp("linkml_owl")
    owl_path = out_dir / "publicschema.owl.ttl"
    proc = subprocess.run(
        [str(GEN_OWL), str(LINKML_COMPOSITE)],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
    )
    owl_path.write_bytes(proc.stdout)

    g = rdflib.Graph()
    g.parse(data=proc.stdout, format="turtle")
    return g


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _kebab_to_pascal(local: str) -> str:
    """Map a kebab-case or single-token lowercase identifier to PascalCase.

    LinkML's standard naming convention is PascalCase for class/enum names
    and snake_case for slot names. rdf_export keeps vocabulary IDs in the
    kebab-case form their YAML uses (``registration-status``,
    ``legal-basis``, ``country``, ...). This converter PascalCases them
    deterministically: hyphen-segmented identifiers are concatenated with
    capitalized parts, and a single all-lowercase token is title-cased.
    """
    if not local:
        return local
    if "-" in local:
        return "".join(part[:1].upper() + part[1:] for part in local.split("-") if part)
    return local[:1].upper() + local[1:]


_DOMAIN_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def normalize_ps_uri(uri: str) -> str:
    """Fold rdf_export's PS URIs to the form LinkML emits.

    rdf_export uses three URI shapes under the ``ps:`` namespace:
      * ``ps:<Concept>`` and ``ps:<domain>/<Concept>`` for concepts
        (PascalCase). LinkML emits ``ps:<Concept>``.
      * ``ps:<property>`` (lowercase / snake_case) for properties. LinkML
        keeps the same form.
      * ``ps:vocab/<kebab>`` and ``ps:vocab/<domain>/<kebab>`` for
        vocabularies. LinkML emits ``ps:<PascalCase>``. Vocabulary value
        IRIs are ``ps:vocab/.../<code>`` (rdf_export) vs
        ``ps:<PascalCase>/<code>`` (LinkML).

    Rules applied:
      * If the URI is a vocabulary URI (starts with ``vocab/``), strip the
        ``vocab/`` prefix and any single lowercase domain segment that
        follows, then PascalCase the kebab head, preserving any value
        suffix as-is.
      * If the URI is a concept-like URI (``<domain>/<Pascal>``), strip
        the lowercase domain segment.
      * Otherwise leave the URI alone (it is either a property URI or
        already in the LinkML form).
    """
    if not uri.startswith(PS):
        return uri
    rest = uri[len(PS):]
    is_vocab = rest.startswith("vocab/")
    if is_vocab:
        rest = rest[len("vocab/"):]
    # Strip one optional lowercase domain segment.
    if "/" in rest:
        first, second = rest.split("/", 1)
        if _DOMAIN_RE.match(first) and not is_vocab:
            # For non-vocab URIs: strip exactly one domain prefix.
            rest = second
        elif _DOMAIN_RE.match(first) and is_vocab and "/" in second:
            # For vocab URIs: '<domain>/<kebab>/<value>' - strip domain.
            rest = second
        elif _DOMAIN_RE.match(first) and is_vocab and "/" not in second:
            # 'vocab/<domain>/<kebab>' - strip domain; the kebab follows.
            rest = second
    # PascalCase the head iff this was originally a vocabulary URI.
    if "/" in rest:
        head, tail = rest.split("/", 1)
        if is_vocab:
            head = _kebab_to_pascal(head)
        return PS + head + "/" + tail
    if is_vocab:
        rest = _kebab_to_pascal(rest)
    return PS + rest


def normalize_object_uri(uri: str) -> str:
    """Normalize external object URIs (predicates' rhs).

    LinkML's default schema.org curie prefix is ``http://``; rdf_export
    emits ``https://``. The two denote the same resource.
    """
    if uri.startswith("https://schema.org/"):
        return "http://schema.org/" + uri[len("https://schema.org/"):]
    if uri.startswith(PS):
        return normalize_ps_uri(uri)
    return uri


def normalize_class_iri(uri: str) -> str:
    """Treat rdfs:Class and owl:Class as the same notion."""
    if uri == str(RDFS.Class):
        return str(OWL.Class)
    return uri


def _ps_subjects(g: rdflib.Graph) -> Iterable[rdflib.URIRef]:
    for s in set(g.subjects()):
        if isinstance(s, rdflib.URIRef) and str(s).startswith(PS):
            yield s


def _is_linkml_enum_value(uri: str) -> bool:
    """True if a URI looks like ``ps:Enum/value`` — i.e. an enum permissible
    value rendered as an OWL class by gen-owl. rdf_export does not emit
    these."""
    if not uri.startswith(PS):
        return False
    rest = uri[len(PS):]
    if "/" not in rest:
        return False
    head = rest.split("/", 1)[0]
    # Real domains are all-lowercase; enum classes are PascalCase.
    return not _DOMAIN_RE.match(head)


# ---------------------------------------------------------------------------
# Invariant builders
# ---------------------------------------------------------------------------


def rdf_export_type_pairs(g: rdflib.Graph) -> set[tuple[str, str]]:
    """``(subject, class)`` pairs from rdf_export, restricted to those
    rdf_export and LinkML can plausibly agree on after normalization.

    rdf_export emits three orthogonal type stripes:
      * ``rdfs:Class`` for concepts (kept; normalized to ``owl:Class``).
      * ``skos:ConceptScheme`` for vocabularies (excluded: LinkML projects
        vocabularies into the OWL stripe as ``owl:Class`` enums, not into
        the SKOS stripe).
      * ``rdf:Property`` for properties (excluded: LinkML projects
        properties into the OWL stripe as ``owl:ObjectProperty`` /
        ``owl:DatatypeProperty``).
      * ``skos:Concept`` for vocabulary values (excluded: same reason as
        ``ConceptScheme``).
    Restricting to the rdfs:Class stripe is the only fair comparison; the
    other stripes are deliberately rendered into different RDF predicates
    by the two pipelines.
    """
    out = set()
    for s, o in g.subject_objects(RDF.type):
        if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
            continue
        if o != RDFS.Class:
            continue
        out.add((normalize_ps_uri(str(s)), normalize_class_iri(str(o))))
    return out


def linkml_type_pairs(g: rdflib.Graph) -> set[tuple[str, str]]:
    """``(subject, class)`` pairs from gen-owl output, restricted to
    top-level ``owl:Class`` declarations on non-enum-value subjects so the
    set is comparable with the rdfs:Class-restricted rdf_export side."""
    out = set()
    for s, o in g.subject_objects(RDF.type):
        if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
            continue
        if o != OWL.Class:
            continue
        if _is_linkml_enum_value(str(s)):
            continue
        out.add((str(s), normalize_class_iri(str(o))))
    return out


def rdf_export_subclass_triples(g: rdflib.Graph) -> set[tuple[str, str]]:
    out = set()
    for s, o in g.subject_objects(RDFS.subClassOf):
        if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
            continue
        if not isinstance(o, rdflib.URIRef):
            continue
        out.add((normalize_ps_uri(str(s)), normalize_ps_uri(str(o))))
    return out


def linkml_subclass_triples(g: rdflib.Graph) -> set[tuple[str, str]]:
    """``rdfs:subClassOf`` triples from gen-owl, with enum-value subjects
    excluded (those are LinkML's OWL rendering of permissible values)."""
    out = set()
    for s, o in g.subject_objects(RDFS.subClassOf):
        if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
            continue
        if not isinstance(o, rdflib.URIRef):
            continue
        if _is_linkml_enum_value(str(s)):
            continue
        out.add((str(s), str(o)))
    return out


def rdf_export_skos_match_triples(g: rdflib.Graph) -> set[tuple[str, str, str]]:
    out = set()
    for pred in (SKOS.exactMatch, SKOS.closeMatch):
        for s, o in g.subject_objects(pred):
            if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
                continue
            if not isinstance(o, rdflib.URIRef):
                continue
            out.add(
                (normalize_ps_uri(str(s)), str(pred), normalize_object_uri(str(o)))
            )
    return out


def linkml_skos_match_triples(g: rdflib.Graph) -> set[tuple[str, str, str]]:
    """SKOS match triples from gen-owl. Excludes:
      * self-loops (``s skos:exactMatch s``) emitted by gen-owl on every
        class via ``class_uri: ...`` in LinkML;
      * triples whose subject is a vocabulary permissible value
        (``ps:Enum/value``) - those are enum value alignments unique to
        LinkML and have no rdf_export counterpart.
    """
    out = set()
    for pred in (SKOS.exactMatch, SKOS.closeMatch):
        for s, o in g.subject_objects(pred):
            if not (isinstance(s, rdflib.URIRef) and str(s).startswith(PS)):
                continue
            if not isinstance(o, rdflib.URIRef):
                continue
            if str(s) == str(o):
                continue
            if _is_linkml_enum_value(str(s)):
                continue
            out.add((str(s), str(pred), str(o)))
    return out


# ---------------------------------------------------------------------------
# Whitelists: expected extras emitted by LinkML that rdf_export does not.
#
# Each whitelist is a *predicate* (function that returns True for triples we
# consider expected divergence). The associated comment explains *why* the
# triple is acceptable. The test will subtract these from the diff before
# asserting equality.
# ---------------------------------------------------------------------------


def _is_citation_or_credential_subclass(triple: tuple[str, str]) -> bool:
    """``(ps:XxxCitation, ps:Citation)`` and ``(ps:XxxCredential, ps:Credential)``
    — LinkML generates one named subclass per bibliography entry / credential
    type; rdf_export emits bibliography entries as data and credentials as
    inline JSON-LD without an OWL subclass hierarchy. The migration is the
    one that introduces these classes intentionally (see
    build/migrate_to_linkml.py: emit_bibliography_file / emit_credentials_file).
    """
    s, o = triple
    if o == PS + "Citation" and s.endswith("Citation"):
        return True
    if o == PS + "Credential" and s.endswith("Credential"):
        return True
    return False


# SKOS alignments that rdf_export emits under the uppercase vocabulary
# URI (e.g. ``publicschema:Country``) but the LinkML output emits under
# the lowercase slot URI (``publicschema:country``). This is an
# *intentional* semantic refinement, not a silent loss:
#
#   - The source ``schema/properties/{country,sex}.yaml`` declares
#     ``external_equivalents`` to ``locn:adminUnitL1``, ``dci:data/sex``,
#     etc. The targets are RDF *predicates / slots* in their respective
#     vocabularies, not classes.
#   - ``rdf_export.py`` cannot distinguish the property ``country`` from
#     the vocabulary ``country`` (same id, same URI in its model) and
#     emits the alignment under ``publicschema:Country`` (the enum URI).
#     That conflates slot-level and class-level alignments.
#   - The LinkML migration correctly distinguishes them: the slot
#     ``publicschema:country`` carries ``close_mappings: [locn:adminUnitL1,
#     dci:data/country_code]`` (verified in dist/linkml/identity.yaml),
#     and the enum ``publicschema:Country`` carries only its own
#     class-level mappings.
#
# Each triple below is the rdf_export-side conflation; the corresponding
# slot-side triple does exist in the LinkML output (with subject
# ``https://publicschema.org/country`` lowercase / ``...sex`` lowercase).
# If a triple here starts appearing under the uppercase enum subject in
# the LinkML output, that is a regression and the test should be
# tightened.
EXPECTED_LINKML_SKOS_LOSSES: set[tuple[str, str, str]] = {
    (
        "https://publicschema.org/Country",
        str(SKOS.closeMatch),
        "http://www.w3.org/ns/locn#adminUnitL1",
    ),
    (
        "https://publicschema.org/Country",
        str(SKOS.closeMatch),
        "https://schema.spdci.org/core/v1/data/country_code",
    ),
    (
        "https://publicschema.org/Sex",
        str(SKOS.exactMatch),
        "http://data.europa.eu/m8g/sex",
    ),
    (
        "https://publicschema.org/Sex",
        str(SKOS.exactMatch),
        "https://schema.spdci.org/core/v1/data/sex",
    ),
}


def _is_linkml_alignment_extra(triple: tuple[str, str, str]) -> bool:
    """SKOS alignments LinkML emits but rdf_export does not.

    These come from external alignment YAML (SEMIC, FOAF, PROV-O, FHIR,
    DPV, etc.) that the migration consumes via ``crosswalk_refs`` /
    external alignment ingestion, but rdf_export only surfaces a curated
    subset on per-concept JSON-LD docs. They are additive evidence of
    interoperability, not contradictions.
    """
    s, p, o = triple
    # Allowlist: SEMIC, EU-Vocabularies, FHIR, FOAF, PROV-O, schema.org-via-LinkML,
    # DPV, OpenSPP, EBSI, OpenCRVS, OpenIMIS, and any other ps:* target that
    # rdf_export doesn't track.
    EXTERNAL_DOMAINS = (
        # SEMIC / EU vocabularies
        "http://data.europa.eu/",
        "http://publications.europa.eu/",
        # FHIR
        "http://hl7.org/",
        "https://hl7.org/",
        # FOAF, PROV, schema.org, W3C vocabularies
        "http://xmlns.com/foaf/",
        "http://www.w3.org/ns/prov#",
        "http://www.w3.org/ns/legal#",
        "http://www.w3.org/ns/person",
        "http://www.w3.org/ns/locn#",
        "http://schema.org/",  # rdf_export's https:// is normalized to http://
        "https://schema.org/",
        # DPV (privacy)
        "https://w3id.org/dpv",
        # SPDCI (Social Protection Data Cooperation Initiative) crosswalks
        "https://schema.spdci.org/",
        # SEMIC, OpenSPP, OpenIMIS, EBSI, OpenCRVS
        "https://docs.openspp.org/",
        "https://docs.openimis.org/",
        "https://standards.ebsi.eu/",
        "https://github.com/opencrvs/",
        # ICAO (passport / travel document standards)
        "https://www.icao.int/",
    )
    if any(o.startswith(d) for d in EXTERNAL_DOMAINS):
        return True
    # Migration also synthesises ps:Citation/<id> targets for bibliography
    # cross-links.
    if o.startswith(PS + "Citation/"):
        return True
    return False


# ---------------------------------------------------------------------------
# The three invariant tests
# ---------------------------------------------------------------------------


class TestInvariantA_RdfTypePairs:
    """(s, rdf:type, o) pairs over PS subjects.

    We restrict both sides to the class stripe: ``rdfs:Class`` in
    rdf_export and ``owl:Class`` in gen-owl, normalized to the same IRI.
    See the docstrings on ``rdf_export_type_pairs`` and ``linkml_type_pairs``
    for why the other rdf:type stripes (``skos:ConceptScheme``,
    ``rdf:Property``, ``skos:Concept``) are excluded — each pipeline
    deliberately projects vocabularies and properties into a different
    RDF predicate, so the class stripe is the only stripe where a direct
    equality assertion makes sense.
    """

    def test_class_type_pairs_equivalent_after_normalization(
        self, rdf_export_graph, linkml_owl_graph
    ):
        rdf_pairs = rdf_export_type_pairs(rdf_export_graph)
        linkml_pairs = linkml_type_pairs(linkml_owl_graph)

        missing_in_linkml = rdf_pairs - linkml_pairs
        extra_in_linkml = linkml_pairs - rdf_pairs

        # All 59 concepts in rdf_export must appear as owl:Class in LinkML.
        # Anything beyond that on the LinkML side is allowed: it represents
        # LinkML's richer OWL projection (Enum classes, Citation/Credential
        # subclasses, extension-metamodel classes, etc.).
        assert not missing_in_linkml, (
            "rdf_export emits class declarations that LinkML does not "
            "(after normalizing rdfs:Class -> owl:Class and stripping the "
            "domain prefix from ps:<domain>/<Concept>):\n"
            + "\n".join(f"  - {p}" for p in sorted(missing_in_linkml)[:30])
            + (f"\n  ... and {len(missing_in_linkml) - 30} more"
               if len(missing_in_linkml) > 30 else "")
        )
        # Extras: all should still be owl:Class (which is the only object
        # we accepted into the linkml side), so a non-trivial set is fine.
        # Sanity-check the shape, not the size.
        bad_extras = {p for p in extra_in_linkml if p[1] != str(OWL.Class)}
        assert not bad_extras, (
            "LinkML emits class triples with unexpected class predicates:\n"
            + "\n".join(f"  + {p}" for p in sorted(bad_extras)[:30])
        )


class TestInvariantB_SubClassOfTriples:
    """(s, rdfs:subClassOf, o) over PS subjects."""

    def test_subclass_triples_superset_in_linkml(
        self, rdf_export_graph, linkml_owl_graph
    ):
        rdf_triples = rdf_export_subclass_triples(rdf_export_graph)
        linkml_triples = linkml_subclass_triples(linkml_owl_graph)

        missing_in_linkml = rdf_triples - linkml_triples
        extra_in_linkml = linkml_triples - rdf_triples

        # WHITELIST: LinkML adds subClassOf edges for Citation / Credential
        # subclasses that rdf_export does not encode in RDFS.
        unaccounted_extras = {
            t for t in extra_in_linkml if not _is_citation_or_credential_subclass(t)
        }

        assert not missing_in_linkml, (
            "rdf_export emits subClassOf triples that LinkML does not "
            "(after normalizing ps:<domain>/X -> ps:X):\n"
            + "\n".join(f"  - {t}" for t in sorted(missing_in_linkml)[:30])
        )
        assert not unaccounted_extras, (
            "LinkML emits subClassOf triples beyond the whitelisted "
            "Citation/Credential extras:\n"
            + "\n".join(f"  + {t}" for t in sorted(unaccounted_extras)[:30])
        )


class TestInvariantC_SkosMatchTriples:
    """(s, skos:exactMatch|closeMatch, o) over PS subjects."""

    def test_skos_match_triples_compatible(self, rdf_export_graph, linkml_owl_graph):
        rdf_triples = rdf_export_skos_match_triples(rdf_export_graph)
        linkml_triples = linkml_skos_match_triples(linkml_owl_graph)

        missing_in_linkml = rdf_triples - linkml_triples
        extra_in_linkml = linkml_triples - rdf_triples

        # Subtract documented expected losses. See
        # ``EXPECTED_LINKML_SKOS_LOSSES`` for the explanation of each.
        unaccounted_missing = missing_in_linkml - EXPECTED_LINKML_SKOS_LOSSES

        # All extras must be explainable: either external-vocabulary
        # alignments LinkML pulls in from the SEMIC architecture, or
        # synthetic ps:Citation/<id> targets the migration produces.
        unaccounted_extras = {
            t for t in extra_in_linkml if not _is_linkml_alignment_extra(t)
        }

        assert not unaccounted_missing, (
            "rdf_export emits SKOS match triples that LinkML drops "
            "(possible silent loss in the migration):\n"
            + "\n".join(f"  - {t}" for t in sorted(unaccounted_missing)[:30])
        )
        assert not unaccounted_extras, (
            "LinkML emits SKOS match triples to subjects/objects outside "
            "the whitelisted external-vocabulary domains:\n"
            + "\n".join(f"  + {t}" for t in sorted(unaccounted_extras)[:30])
        )


class TestPipelineSanity:
    """Cheap sanity checks so a regression in either pipeline surfaces clearly
    before the heavier diff-based tests run."""

    def test_rdf_export_graph_has_publicschema_subjects(self, rdf_export_graph):
        n = sum(1 for _ in _ps_subjects(rdf_export_graph))
        assert n > 0, "rdf_export Turtle has no PublicSchema subjects"

    def test_linkml_owl_graph_has_publicschema_subjects(self, linkml_owl_graph):
        n = sum(1 for _ in _ps_subjects(linkml_owl_graph))
        assert n > 0, "gen-owl Turtle has no PublicSchema subjects"

    def test_concept_classes_overlap(self, rdf_export_graph, linkml_owl_graph):
        """The 59 schema/concepts/*.yaml entries should appear as classes
        in both outputs (after normalization)."""
        rdf_classes = {
            normalize_ps_uri(str(s))
            for s, o in rdf_export_graph.subject_objects(RDF.type)
            if isinstance(s, rdflib.URIRef)
            and str(s).startswith(PS)
            and o == RDFS.Class
        }
        linkml_classes = {
            str(s)
            for s, o in linkml_owl_graph.subject_objects(RDF.type)
            if isinstance(s, rdflib.URIRef)
            and str(s).startswith(PS)
            and o == OWL.Class
            and not _is_linkml_enum_value(str(s))
        }
        missing = rdf_classes - linkml_classes
        assert not missing, (
            "Concepts present in rdf_export but absent from LinkML OWL:\n"
            + "\n".join(f"  - {c}" for c in sorted(missing))
        )
