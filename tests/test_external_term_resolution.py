"""OAK-based external-term resolution.

For each external ontology with a pinned local Turtle snapshot under
``external/<id>/manifest.yaml``, this test:

  1. Loads the snapshot via OAK's ``SparqlImplementation`` (local TTL adapter,
     no network).
  2. Walks the LinkML composite at ``schema/publicschema.yaml`` and collects
     every CURIE referenced via ``exact_mappings``, ``close_mappings``,
     ``broad_mappings``, ``narrow_mappings`` or ``related_mappings`` at the
     class, slot, enum and permissible-value levels.
  3. Expands each CURIE using the LinkML schema's prefix map.
  4. Asserts every cited URI that falls inside the snapshot's namespace is a
     known entity in the loaded ontology.

This is the post-cutover replacement for
``tests/test_graph_invariants.py::TestDPVNamespacePinning``, which walked the
bespoke ``schema/concepts/``, ``schema/properties/`` and
``schema/vocabularies/`` directories. Those directories no longer exist after
the LinkML migration, so the legacy test silently iterates an empty set; this
file restores the invariant against the canonical LinkML source.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from linkml_runtime.utils.schemaview import SchemaView
from oaklib.implementations.sparql.sparql_implementation import SparqlImplementation
from oaklib.resource import OntologyResource

V2_ROOT = Path(__file__).parent.parent
COMPOSITE = V2_ROOT / "schema" / "publicschema.yaml"
EXTERNAL_DIR = V2_ROOT / "external"

MAPPING_ATTRS = (
    "exact_mappings",
    "close_mappings",
    "broad_mappings",
    "narrow_mappings",
    "related_mappings",
)


@dataclass(frozen=True)
class Snapshot:
    external_id: str
    file: Path
    namespace: str

    @property
    def label(self) -> str:
        return f"{self.external_id}:{self.file.name}"


def _discover_snapshots() -> list[Snapshot]:
    """Return every Turtle snapshot declared in any ``external/*/manifest.yaml``.

    Only TTL snapshots are returned — JSON-LD or other formats would need a
    different OAK adapter. Snapshots whose file is missing on disk are
    deliberately included so the test fails loudly (the manifest is the
    source of truth for what should be pinned).
    """
    out: list[Snapshot] = []
    for manifest in sorted(EXTERNAL_DIR.glob("*/manifest.yaml")):
        data = yaml.safe_load(manifest.read_text()) or {}
        ext_id = data.get("id") or manifest.parent.name
        for snap in data.get("snapshots") or []:
            content_type = snap.get("content_type", "")
            if "turtle" not in content_type and not snap["file"].endswith(".ttl"):
                continue
            out.append(
                Snapshot(
                    external_id=ext_id,
                    file=manifest.parent / snap["file"],
                    namespace=snap["namespace"],
                )
            )
    return out


SNAPSHOTS = _discover_snapshots()


@pytest.fixture(scope="module")
def schemaview() -> SchemaView:
    return SchemaView(str(COMPOSITE))


@pytest.fixture(scope="module")
def cited_uris(schemaview: SchemaView) -> set[str]:
    """All non-ontology-identifier URIs cited via *_mappings in the composite.

    A CURIE that expands to exactly the namespace IRI (e.g.
    ``https://w3id.org/dpv#``) is the ontology identifier, not a term, so it
    is filtered out. Term checks should only assert membership of real
    subjects in the loaded graph.
    """
    sv = schemaview
    uris: set[str] = set()

    def collect(obj) -> None:
        for attr in MAPPING_ATTRS:
            for curie in getattr(obj, attr, None) or []:
                expanded = sv.expand_curie(curie)
                if not expanded.endswith(("#", "/")):
                    uris.add(expanded)

    for cname in sv.all_classes():
        collect(sv.get_class(cname))
    for sname in sv.all_slots():
        collect(sv.get_slot(sname))
    for ename in sv.all_enums():
        enum = sv.get_enum(ename)
        collect(enum)
        for pv in (enum.permissible_values or {}).values():
            collect(pv)
    return uris


def _load_ontology(snapshot: Snapshot) -> SparqlImplementation:
    res = OntologyResource(
        slug=snapshot.file.name,
        directory=str(snapshot.file.parent),
        local=True,
        format="ttl",
    )
    return SparqlImplementation(resource=res)


def test_snapshots_were_discovered() -> None:
    """At least one external snapshot must be pinned; an empty list would
    silently turn the parameterised test below into a no-op."""
    assert SNAPSHOTS, (
        "No external Turtle snapshots discovered under external/*/manifest.yaml. "
        "If snapshots were intentionally removed, also delete this test; "
        "otherwise restore the manifest entry."
    )


@pytest.mark.parametrize(
    "snapshot", SNAPSHOTS, ids=[s.label for s in SNAPSHOTS]
)
def test_pinned_snapshot_resolves_cited_terms(
    snapshot: Snapshot, cited_uris: set[str]
) -> None:
    """Every CURIE we cite that falls inside this snapshot's namespace must
    resolve to a real entity in the pinned graph."""
    assert snapshot.file.is_file(), (
        f"Pinned snapshot missing on disk: {snapshot.file}. "
        f"Refresh per {snapshot.file.parent / 'manifest.yaml'}."
    )

    impl = _load_ontology(snapshot)
    known = set(impl.entities(filter_obsoletes=False))

    in_scope = {u for u in cited_uris if u.startswith(snapshot.namespace)}
    missing = sorted(in_scope - known)

    assert not missing, (
        f"URIs cited in schema/publicschema.yaml mappings that are NOT "
        f"present as entities in pinned snapshot {snapshot.label}:\n"
        + "\n".join(f"  - {u}" for u in missing)
        + f"\nRefresh the snapshot per external/{snapshot.external_id}/manifest.yaml "
        "or fix the cited CURIE in the LinkML schema."
    )


def test_at_least_one_cited_term_per_snapshot(cited_uris: set[str]) -> None:
    """Sanity check: each pinned namespace should have at least one citation
    somewhere in the schema. A pinned snapshot with zero citations is dead
    weight — drop the snapshot or add a real mapping."""
    orphans: list[str] = []
    for snap in SNAPSHOTS:
        if not any(u.startswith(snap.namespace) for u in cited_uris):
            orphans.append(snap.label)
    if orphans:
        pytest.skip(
            "Pinned snapshots with no cited terms (acceptable while a "
            f"vocabulary is being prepared for citation): {orphans}"
        )
