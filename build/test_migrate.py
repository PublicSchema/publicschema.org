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

import json
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


def test_credentials_migrated(migration_run):
    """credentials.yaml has one ClassDefinition per VC descriptor, all subclassing
    a synthetic abstract Credential marker."""
    f = OUTPUT_DIR / "credentials.yaml"
    assert f.exists()
    with f.open() as fh:
        data = yaml.safe_load(fh)
    classes = data.get("classes") or {}
    assert "Credential" in classes
    assert classes["Credential"].get("abstract") is True
    # Each credential subclasses Credential and carries subject_concept annotation
    cred_subclasses = [
        n for n, c in classes.items()
        if c.get("is_a") == "Credential"
    ]
    assert len(cred_subclasses) >= 3, f"expected >=3 credentials, found {cred_subclasses}"
    for cname in cred_subclasses:
        ann = (classes[cname].get("annotations") or {})
        assert ann.get("subject_concept"), f"{cname} missing subject_concept annotation"


def test_bibliography_migrated(migration_run):
    """bibliography.yaml emits the Citation supertype plus one subclass per
    source file in schema/bibliography/. Every citation carries a citation_id
    annotation."""
    f = OUTPUT_DIR / "bibliography.yaml"
    assert f.exists()
    with f.open() as fh:
        data = yaml.safe_load(fh)
    classes = data.get("classes") or {}
    assert "Citation" in classes
    assert classes["Citation"].get("abstract") is True
    citations = [c for c in classes.values() if c.get("is_a") == "Citation"]
    assert len(citations) > 100, f"expected >100 citations, got {len(citations)}"
    # Every citation has a citation_id
    for c in citations:
        assert (c.get("annotations") or {}).get("citation_id"), c


def test_categories_migrated(migration_run):
    """categories.yaml emits a single PropertyCategory enum with one permissible
    value per category, including 'identity' (used by Person concept)."""
    f = OUTPUT_DIR / "categories.yaml"
    assert f.exists()
    with f.open() as fh:
        data = yaml.safe_load(fh)
    enums = data.get("enums") or {}
    assert "PropertyCategory" in enums
    pvs = enums["PropertyCategory"].get("permissible_values") or {}
    assert "identity" in pvs, f"identity category missing; keys={list(pvs)[:10]}"
    # Multilingual labels preserved as annotations
    identity = pvs["identity"]
    ann = identity.get("annotations") or {}
    assert ann.get("label_fr") or ann.get("label_es"), \
        f"identity missing multilingual label annotations: {identity}"


def test_bibliography_refs_back_on_concepts(migration_run):
    """A concept that's referenced in a bibliography entry's `informs:` list
    should carry a `bibliography_refs` annotation in its emitted form."""
    with (OUTPUT_DIR / "identity.yaml").open() as f:
        identity = yaml.safe_load(f)
    person = identity["classes"].get("Person", {})
    refs_json = (person.get("annotations") or {}).get("bibliography_refs")
    assert refs_json, "Person missing bibliography_refs annotation"
    refs = json.loads(refs_json)
    assert isinstance(refs, list) and len(refs) > 0, refs


def test_geojson_geometry_handled(migration_run):
    """The geometry property's geojson_geometry type must round-trip cleanly
    (no longer in the unmapped report)."""
    # Find the geometry slot in any domain file.
    found = False
    for f in OUTPUT_DIR.glob("*.yaml"):
        with f.open() as fh:
            d = yaml.safe_load(fh)
        slots = (d.get("slots") or {})
        if "geometry" in slots:
            assert slots["geometry"].get("range") == "string"
            found = True
            break
    assert found, "geometry slot not emitted in any domain file"


def test_zero_unmapped_fields(migration_run):
    """After all the migration work, the migration_report should report zero
    unmapped source fields. Regressions on this signal silent data loss."""
    report = (OUTPUT_DIR / "_migration_report.md").read_text()
    # The first occurrence of "Unmapped source fields:" gives the count.
    import re
    m = re.search(r"Unmapped source fields:\s*(\d+)", report)
    assert m, "migration report missing unmapped-fields count line"
    assert int(m.group(1)) == 0, f"unmapped fields: {m.group(1)} (was 0)"


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


def test_per_value_fields_preserved(migration_run):
    """Audit revealed standard_code, level, parent_code etc. were silently
    dropped from values[]. Verify they now ride as annotations on the
    permissible value."""
    with (OUTPUT_DIR / "vocabularies.yaml").open() as f:
        vocab = yaml.safe_load(f)

    # standard_code preserved (Country: af -> AF per ISO 3166).
    af = vocab["enums"]["Country"]["permissible_values"]["af"]
    assert (af.get("annotations") or {}).get("standard_code") == "AF", \
        f"Country.af missing standard_code annotation: {af}"

    # level + parent_code preserved (Occupation hierarchy). Domain assignment can
    # place this enum outside vocabularies.yaml, so find it across emitted domains.
    occ = {}
    for domain_file in OUTPUT_DIR.glob("*.yaml"):
        with domain_file.open() as f:
            domain_data = yaml.safe_load(f)
        occ = (domain_data.get("enums") or {}).get("Occupation", {}).get("permissible_values", {})
        if occ:
            break
    assert occ, "Occupation enum missing"
    sample_level = next(
        (pv for pv in occ.values() if isinstance(pv, dict)
         and (pv.get("annotations") or {}).get("level") is not None),
        None,
    )
    assert sample_level is not None, "no Occupation value carries a level annotation"


def test_base_uri_from_meta(migration_run):
    """The base URI in emitted schemas must match schema/_meta.yaml."""
    with (ROOT / "schema" / "_meta.yaml").open() as f:
        meta = yaml.safe_load(f)
    expected = meta["base_uri"]
    if not expected.endswith("/"):
        expected += "/"
    with (OUTPUT_DIR / "publicschema.yaml").open() as f:
        composite = yaml.safe_load(f)
    assert composite["prefixes"]["publicschema"] == expected, \
        f"composite.prefixes.publicschema={composite['prefixes']['publicschema']} != _meta.base_uri={expected}"


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
