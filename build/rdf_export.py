"""Backwards-compatibility shim for the legacy RDF export module.

The legacy implementation lives at ``build/rdf_export_legacy.py``. The
production build now uses ``build/linkml_rdf_export.py`` (LinkML
generators plus an rdflib JSON-LD bridge). This shim re-exports the
legacy symbols so existing tests and call sites that import from
``build.rdf_export`` continue to work unchanged. New code should import
from ``build.linkml_rdf_export`` instead.
"""

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
    write_full_jsonld,
    write_shacl,
    write_turtle,
)
