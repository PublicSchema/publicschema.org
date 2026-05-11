"""LinkML-driven RDF export for site-facing artifacts.

Replaces ``build/rdf_export.py`` (now preserved as
``build/rdf_export_legacy.py``) for production builds. The three site
artifacts (Turtle OWL, SHACL shapes, full JSON-LD ``@graph``) are now
produced by LinkML's stock generators against the migrated composite at
``dist/linkml/publicschema.yaml`` (output of
``build/migrate_to_linkml.py``):

* ``write_turtle``      -> ``gen-owl``   -> ``dist/publicschema.ttl``
* ``write_shacl``       -> ``gen-shacl`` -> ``dist/publicschema.shacl.ttl``
* ``write_full_jsonld`` -> ``gen-owl`` + rdflib JSON-LD bridge ->
                           ``dist/publicschema.jsonld``

The JSON-LD bridge re-parses the gen-owl Turtle into rdflib and emits
JSON-LD, then rewrites the inline ``@context`` to a string reference to
the hosted draft context URL — matching the pre-LinkML behaviour so the
site can serve the document unchanged.

The semantic equivalence with the legacy pipeline (modulo four
documented enum-alignment losses for Country/Sex) is exercised by
``tests/test_linkml_roundtrip.py`` and is the basis for cutting over.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LINKML_COMPOSITE = ROOT / "dist" / "linkml" / "publicschema.yaml"
DEFAULT_CONTEXT_URL = "https://publicschema.org/ctx/draft.jsonld"


def _find_linkml_generator(name: str) -> str:
    """Locate a LinkML generator CLI (``gen-owl``, ``gen-shacl``, ...).

    Prefer the venv that runs the current Python interpreter, fall back
    to the repo-local ``.venv/bin``, and finally to ``$PATH``. Mirrors
    the resolution used by ``tests/test_linkml_roundtrip.py`` so the
    production build and the round-trip test always agree on which
    binary they invoke.
    """
    candidates: list[Path] = [
        Path(sys.executable).parent / name,
        ROOT / ".venv" / "bin" / name,
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(
        f"LinkML generator {name!r} not found. Install the linkml package "
        f"in the active venv (e.g. `.venv/bin/pip install linkml`)."
    )


def _require_composite(composite: Path = DEFAULT_LINKML_COMPOSITE) -> Path:
    """Ensure the LinkML composite schema exists before invoking a generator."""
    if not composite.exists():
        raise FileNotFoundError(
            f"LinkML composite not found at {composite}. Run "
            f"`build/migrate_to_linkml.py` first to produce it."
        )
    return composite


def _run_generator(
    generator: str,
    output_path: Path,
    extra_args: list[str] | None = None,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Invoke a LinkML generator CLI and write the stdout to ``output_path``.

    Generators write Turtle to stdout when no ``--output`` is given. We
    capture stdout and write it ourselves so the parent directory is
    created consistently with the rest of the build pipeline.
    """
    binary = _find_linkml_generator(generator)
    composite = _require_composite(composite)
    args = [binary, *(extra_args or []), str(composite)]
    proc = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(proc.stdout)
    return output_path


def write_turtle(
    output_path: Path,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate the full vocabulary as OWL Turtle via ``gen-owl``."""
    return _run_generator("gen-owl", output_path, composite=composite)


def write_shacl(
    output_path: Path,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate SHACL shapes via ``gen-shacl``.

    Uses LinkML's default closed-shapes profile (which matches the SHACL
    semantics consumers expect from a published shape file).
    """
    return _run_generator("gen-shacl", output_path, composite=composite)


def write_full_jsonld(
    output_path: Path,
    context_url: str = DEFAULT_CONTEXT_URL,
    composite: Path = DEFAULT_LINKML_COMPOSITE,
) -> Path:
    """Generate the full vocabulary JSON-LD ``@graph`` document.

    Strategy: run ``gen-owl`` to produce Turtle (the OWL projection
    is the single canonical RDF rendering of the schema), parse it
    with rdflib, re-serialise as JSON-LD, then rewrite the inline
    ``@context`` with a string reference to the hosted draft context.
    This matches the pre-LinkML behaviour where the published JSON-LD
    referenced a hosted context so the file stays compact.
    """
    # Lazy import: rdflib is only required when emitting JSON-LD.
    import rdflib  # noqa: WPS433 — local import is intentional.

    composite = _require_composite(composite)
    binary = _find_linkml_generator("gen-owl")
    proc = subprocess.run(
        [binary, str(composite)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    g = rdflib.Graph()
    g.parse(data=proc.stdout, format="turtle")

    # rdflib's JSON-LD serializer emits a {"@graph": [...], "@context": {...}}
    # document. We replace the inline @context with the hosted URL so the
    # served file is self-describing but compact.
    raw = g.serialize(format="json-ld", auto_compact=True)
    doc = json.loads(raw)
    if isinstance(doc, list):
        # rdflib occasionally returns a bare graph array. Wrap it.
        doc = {"@graph": doc}
    doc["@context"] = context_url

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    )
    return output_path


def ensure_linkml_composite(
    composite: Path = DEFAULT_LINKML_COMPOSITE,
    *,
    run_migration: bool = True,
) -> Path:
    """Make sure the LinkML composite schema exists.

    If ``run_migration`` is True and the composite is missing, invoke
    ``build/migrate_to_linkml.py`` to produce it. Otherwise just assert
    its presence. Returns the path of the composite.
    """
    if composite.exists():
        return composite
    if not run_migration:
        return _require_composite(composite)
    migrate_script = ROOT / "build" / "migrate_to_linkml.py"
    if not migrate_script.exists():
        raise FileNotFoundError(
            f"Cannot bootstrap LinkML composite: {migrate_script} is missing."
        )
    subprocess.run(
        [sys.executable, str(migrate_script)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        check=True,
    )
    return _require_composite(composite)
