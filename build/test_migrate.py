"""End-to-end verification of build/migrate_to_linkml.py.

Runs the migration script once (session-scoped), then asserts:
  - exit code 0
  - dist/linkml/ has the expected structure
  - All four core LinkML generators (gen-owl, gen-shacl, gen-jsonld-context,
    gen-json-schema) succeed on the composite
  - Status fields use bibo: CURIEs
  - Person uses multi-inheritance (is_a + mixins)
  - DHS partial schema has explicit meaning: URIs
  - Referential integrity: every crosswalk CURIE in PublicSchema enums
    resolves to a meaning: URI in the corresponding external/<system>.yaml

Idempotency is verified separately by re-running the script and comparing
output trees with diff -r (see Makefile or run by hand).

Run with: uv run pytest build/test_migrate.py -v
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "build" / "migrate_to_linkml.py"
OUTPUT_DIR = ROOT / "dist" / "linkml"
EXTERNAL_DIR = OUTPUT_DIR / "external"


@pytest.fixture(scope="session")
def migration_run():
    """Run the migration once for the whole test session."""
    res = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"migration failed:\nstdout={res.stdout}\nstderr={res.stderr}"
    assert "linkml-lint failures: 0" in res.stdout
    assert "Referential integrity failures: 0" in res.stdout
    return res


def test_output_structure(migration_run):
    assert (OUTPUT_DIR / "publicschema.yaml").exists()
    assert (OUTPUT_DIR / "publicschema-extensions.yaml").exists()
    assert (OUTPUT_DIR / "_inventory.md").exists()
    assert (OUTPUT_DIR / "_domain_split.md").exists()
    assert (OUTPUT_DIR / "_migration_report.md").exists()
    assert EXTERNAL_DIR.is_dir()
    for f in OUTPUT_DIR.glob("*.yaml"):
        assert f.stat().st_size > 0, f"empty: {f}"
    assert any(EXTERNAL_DIR.glob("*.yaml"))


@pytest.mark.parametrize(
    "generator",
    ["gen-owl", "gen-shacl", "gen-jsonld-context", "gen-json-schema"],
)
def test_generator_succeeds_on_composite(migration_run, generator):
    tool = shutil.which(generator)
    assert tool is not None, f"{generator} not found on PATH"
    res = subprocess.run(
        [tool, str(OUTPUT_DIR / "publicschema.yaml")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"{generator} failed: {res.stderr[-500:]}"
    assert len(res.stdout) > 1000, f"{generator} produced suspiciously little output"


def test_referential_integrity(migration_run):
    """Every exact_mappings CURIE in PublicSchema enums points at a meaning: URI
    declared somewhere in dist/linkml/external/<system>.yaml."""
    declared_meanings: set[str] = set()
    for ext_file in EXTERNAL_DIR.glob("*.yaml"):
        with ext_file.open() as f:
            data = yaml.safe_load(f)
        for enum in (data.get("enums") or {}).values():
            for pv in (enum.get("permissible_values") or {}).values():
                if isinstance(pv, dict) and pv.get("meaning"):
                    declared_meanings.add(pv["meaning"])

    referenced: set[str] = set()
    for domain_file in OUTPUT_DIR.glob("*.yaml"):
        with domain_file.open() as f:
            data = yaml.safe_load(f)
        for enum in (data.get("enums") or {}).values():
            for pv in (enum.get("permissible_values") or {}).values():
                if isinstance(pv, dict):
                    for mapping in (pv.get("exact_mappings") or []):
                        if ":" in mapping and not mapping.startswith("publicschema:"):
                            referenced.add(mapping)

    dangling = referenced - declared_meanings
    assert not dangling, f"dangling crosswalk CURIEs: {sorted(dangling)[:10]}"


def test_status_uses_bibo_curies(migration_run):
    """The maturity -> bibo: status CURIE mapping reaches the emitted files."""
    found = {"draft": False, "forthcoming": False, "published": False}
    for f in OUTPUT_DIR.glob("*.yaml"):
        text = f.read_text()
        if "bibo:draft" in text:
            found["draft"] = True
        if "bibo:status/forthcoming" in text:
            found["forthcoming"] = True
        if "bibo:status/published" in text:
            found["published"] = True
    assert all(found.values()), f"missing bibo status values: {found}"


def test_person_multi_inheritance(migration_run):
    """Person must use is_a + mixins for its two supertypes (Party + Agent)."""
    with (OUTPUT_DIR / "identity.yaml").open() as f:
        data = yaml.safe_load(f)
    person = data["classes"]["Person"]
    assert person["is_a"] in ("Party", "Agent"), person.get("is_a")
    mixins = person.get("mixins") or []
    assert {person["is_a"]} | set(mixins) == {"Party", "Agent"}


def test_domain_scoped_person_is_not_collapsed(migration_run):
    """The CRVS Person snapshot and root Person must remain distinct terms."""
    with (OUTPUT_DIR / "identity.yaml").open() as f:
        identity = yaml.safe_load(f)
    with (OUTPUT_DIR / "civil_status.yaml").open() as f:
        civil_status = yaml.safe_load(f)

    assert "Person" in identity["classes"]
    assert "CrvsPerson" in civil_status["classes"]
    assert civil_status["classes"]["CrvsPerson"]["class_uri"] == "publicschema:crvs/Person"
    assert "person:Person" not in (civil_status["classes"]["CrvsPerson"].get("exact_mappings") or [])


def test_external_dhs_emits(migration_run):
    """DHS partial schema is emitted and contains at least one enum with explicit meaning: URIs."""
    f = EXTERNAL_DIR / "dhs.yaml"
    assert f.exists()
    with f.open() as fh:
        data = yaml.safe_load(fh)
    assert data.get("enums"), "dhs.yaml has no enums"
    for enum in data["enums"].values():
        for pv in (enum.get("permissible_values") or {}).values():
            if isinstance(pv, dict) and pv.get("meaning"):
                assert pv["meaning"].startswith("dhs:"), pv["meaning"]
                return
    raise AssertionError("no permissible value with dhs: meaning found")


def test_semic_alignment_integration(migration_run):
    """The SEMIC alignment architecture (P4 series on main) flows into the LinkML output:
    Person's exact_mappings includes person:Person (from alignments/semic-core-person.yaml),
    and external/semic-core-person.yaml declares the canonical person:Person class with
    provenance from external_references/.
    """
    # 1. PublicSchema Person has the SEMIC alignment in exact_mappings.
    with (OUTPUT_DIR / "identity.yaml").open() as f:
        identity = yaml.safe_load(f)
    person = identity["classes"]["Person"]
    assert "person:Person" in (person.get("exact_mappings") or []), \
        f"Person.exact_mappings missing person:Person: {person.get('exact_mappings')}"

    # 2. external/semic-core-person.yaml exists with prefix-qualified class name.
    sem = EXTERNAL_DIR / "semic-core-person.yaml"
    assert sem.exists()
    with sem.open() as f:
        sem_data = yaml.safe_load(f)
    assert any(
        cls.get("class_uri") == "person:Person"
        for cls in (sem_data.get("classes") or {}).values()
    ), "person:Person class_uri not found in external/semic-core-person.yaml"

    # 3. Provenance annotation preserved.
    prov = (sem_data.get("annotations") or {}).get("external_reference_provenance_json")
    assert prov and "sha256" in prov, "provenance annotation missing or incomplete"

    # 4. The cv: prefix from external_references is in the schema's prefixes block.
    assert sem_data.get("prefixes", {}).get("person") == "http://www.w3.org/ns/person#"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
