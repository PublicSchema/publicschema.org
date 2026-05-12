"""Backwards-compatibility shim for the legacy RDF export module.

The legacy implementation lives at ``build/rdf_export_legacy.py``. The
production build now uses ``build/linkml_rdf_export.py`` (LinkML
generators plus an rdflib JSON-LD bridge). This shim re-exports the
legacy symbols so existing tests and call sites that import from
``build.rdf_export`` continue to work unchanged. New code should import
from ``build.linkml_rdf_export`` instead.

The three write_* functions below are production-replaced: ``build.build``
imports them from ``build.linkml_rdf_export``. Any test calling these
via this shim exercises the legacy code path, not the production one.
Legacy test files that still use this shim:
  - tests/test_rdf_export.py
  - tests/test_linkml_roundtrip.py
  - tests/test_red_team.py
"""

import warnings

from build.rdf_export_legacy import (  # noqa: F401
    PS,
    SCHEMA,
    SH,
    SHACL_DATATYPE_MAP,
    VOCAB_SIZE_THRESHOLD,
    XSD,
    _build_context_with_coercions,
    _resolve_all_properties,
    build_full_jsonld,
    build_shacl,
    build_turtle,
    load_graph,
)
from build.rdf_export_legacy import write_full_jsonld as _write_full_jsonld
from build.rdf_export_legacy import write_shacl as _write_shacl
from build.rdf_export_legacy import write_turtle as _write_turtle


def write_turtle(result: dict, dist_dir) -> object:
    """Write Turtle output via the legacy emitter.

    .. deprecated::
        Production uses ``build.linkml_rdf_export.write_turtle``. This
        shim calls the legacy implementation and is preserved for
        comparison tests only.
    """
    warnings.warn(
        "build.rdf_export.write_turtle is the legacy implementation. "
        "Use build.linkml_rdf_export.write_turtle for production output.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _write_turtle(result, dist_dir)


def write_shacl(result: dict, dist_dir) -> object:
    """Write SHACL output via the legacy emitter.

    .. deprecated::
        Production uses ``build.linkml_rdf_export.write_shacl``. This
        shim calls the legacy implementation and is preserved for
        comparison tests only.
    """
    warnings.warn(
        "build.rdf_export.write_shacl is the legacy implementation. "
        "Use build.linkml_rdf_export.write_shacl for production output.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _write_shacl(result, dist_dir)


def write_full_jsonld(result: dict, dist_dir) -> object:
    """Write full JSON-LD output via the legacy emitter.

    .. deprecated::
        Production uses ``build.linkml_rdf_export.write_full_jsonld``. This
        shim calls the legacy implementation and is preserved for
        comparison tests only.
    """
    warnings.warn(
        "build.rdf_export.write_full_jsonld is the legacy implementation. "
        "Use build.linkml_rdf_export.write_full_jsonld for production output.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _write_full_jsonld(result, dist_dir)
