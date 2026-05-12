"""Adapter: read ``schema/*.yaml`` (LinkML) and re-project to the renderer shape.

The website renderer (``build/build.py``) ultimately consumes
``dist/vocabulary.json`` plus ``dist/preview/*.json`` and
``dist/system_matchings.json``. Its internal model is per-element raw dicts
(``concepts_raw``, ``properties_raw``, ``vocabularies_raw``,
``bibliography_raw``, ``categories_raw``, ``credentials_raw``).

The canonical source-of-truth at ``schema/`` is a LinkML composite where each
domain file contains many classes/slots/enums. This module bridges the gap:
it reads those domain files and re-projects them into per-element dicts.

Field-by-field mapping follows ``docs/migration-cheatsheet.md``. Where
structured data lives under ``annotations.<name>_json`` the adapter parses
the JSON back into the original shape; lossy areas (e.g. domain-prefixed
``vocabulary:`` references that don't round-trip through LinkML's ``range``
slot) get best-effort fallbacks that keep the public site shape stable.

The adapter is read-only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

# Reverse of STATUS_MAP from build/migrate_to_linkml.py.
STATUS_REVERSE_MAP = {
    "bibo:draft": "draft",
    "bibo:status/forthcoming": "candidate",
    "bibo:status/published": "normative",
}

# Reverse of SOURCE_DOMAIN_MAP from build/migrate_to_linkml.py. The bespoke
# YAML's ``domain:`` field uses short codes (crvs, sp, …); ``source_domain``
# annotations on LinkML elements preserve those codes verbatim, so we read
# them as-is and only fall back to LinkML's split-domain (civil_status, …)
# when the annotation is absent.
LINKML_DOMAIN_TO_BESPOKE = {
    "civil_status": "crvs",
    "program": "sp",
    # core / identity / payment / assessment share the same code on both sides
}

# Reverse of PRIMITIVE_TYPE_MAP. Most LinkML ranges map back 1:1; "float"
# came from PublicSchema's "number" / "float" (ambiguous), so we prefer
# "number" since it's the more common original. The lossy direction here
# is acceptable: build.py treats both interchangeably for JSON Schema
# emission.
LINKML_RANGE_TO_BESPOKE_TYPE = {
    "string": "string",
    "boolean": "boolean",
    "integer": "integer",
    "float": "number",
    "decimal": "decimal",
    "date": "date",
    "datetime": "datetime",
    "uri": "uri",
}


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        data = yaml.safe_load(f)
    return data or {}


def _parse_json_annotation(value: Any) -> Any:
    """Annotations are stored as compact LinkML annotation values.

    LinkML lets a scalar annotation be either a plain string (when authored
    via the compact form ``key: value``) or a dict with ``tag``/``value``
    (full form). Both shapes appear in the migrated output. Structured
    payloads are always JSON-stringified.
    """
    if isinstance(value, dict):
        # Full LinkML annotation form: {tag: <name>, value: <payload>}
        value = value.get("value", value.get("@value"))
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value
    return value


def _scalar_annotation(value: Any) -> Any:
    """Unwrap the full LinkML annotation form to its scalar payload."""
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def _split_multilingual(
    en_text: str | None,
    annotations: dict,
    prefix: str,
) -> dict[str, str]:
    """Reconstruct a ``{en, fr, es, ...}`` dict from title/description and
    ``label_<lang>`` / ``description_<lang>`` annotations.
    """
    out: dict[str, str] = {}
    if en_text:
        out["en"] = en_text
    for key, val in (annotations or {}).items():
        if not isinstance(key, str) or not key.startswith(prefix):
            continue
        lang = key[len(prefix):]
        if not lang:
            continue
        text = _scalar_annotation(val)
        if isinstance(text, str):
            out[lang] = text
    return out


def _maturity_from_status(status: str | None) -> str:
    if not status:
        return "draft"
    return STATUS_REVERSE_MAP.get(status, "draft")


def _normalise_annotations(annotations: dict | None) -> dict:
    """Flatten LinkML annotations into a name->scalar/parsed dict.

    LinkML compact form: ``annotations: {key: value}``. Full form:
    ``annotations: {key: {tag: key, value: <payload>}}``. We coalesce both.
    JSON-stringified annotations remain as raw strings here; callers parse
    them via ``_parse_json_annotation`` when needed.
    """
    out: dict[str, Any] = {}
    for key, val in (annotations or {}).items():
        if isinstance(val, dict) and "value" in val:
            out[key] = val["value"]
        else:
            out[key] = val
    return out


def _split_external_alignments(
    alignments_json: Any,
) -> dict[str, dict]:
    """Reconstruct bespoke ``external_equivalents`` from
    ``external_alignments_json``.

    The annotation payload is a list of records keyed by ``vocabulary_id``
    in the original schema (one record per external vocabulary); the
    bespoke shape is a dict ``{vocab_id: {label, uri, match, vocabulary, note}}``.
    """
    parsed = _parse_json_annotation(alignments_json)
    if not isinstance(parsed, list):
        return {}
    out: dict[str, dict] = {}
    for record in parsed:
        if not isinstance(record, dict):
            continue
        vid = record.get("vocabulary_id")
        if not vid:
            continue
        entry: dict[str, Any] = {}
        for k in ("label", "uri", "match", "vocabulary", "note"):
            if k in record:
                entry[k] = record[k]
        out[vid] = entry
    return out


def _domain_from_source(source_domain: Any) -> str | None:
    if not isinstance(source_domain, str) or not source_domain:
        return None
    # The annotation stores the bespoke short code verbatim ("crvs", "sp",
    # "core", "identity", …). Leave it as-is.
    return source_domain


def _is_external_domain_file(path: Path) -> bool:
    """External partial schemas live under ``schema/external/`` and do
    not contribute to PublicSchema's own catalog of concepts/slots/enums.
    They're separate inputs (mapping targets), so the adapter skips them.
    """
    return path.parent.name == "external"


# ---------------------------------------------------------------------------
# Enum reverse mapping (PascalCase enum name -> kebab-case vocab id)
# ---------------------------------------------------------------------------

_PASCAL_RE = re.compile(r"(?<=[a-z0-9])([A-Z])")


def _pascal_to_kebab(name: str) -> str:
    """Reverse of ``pascal_case`` for typical PublicSchema enum names.

    Not all PascalCase round-trips cleanly back to the original (e.g.
    ``DhsAgrep`` would lose the original ``-``/``_`` distinction). For the
    115 vocabularies in the catalogue this heuristic works because vocab
    ids are kebab-case ASCII words.
    """
    s = _PASCAL_RE.sub(r"-\1", name).lower()
    return s


def _vocab_key_from_range(
    range_value: str,
    enum_to_vocab_key: dict[str, str],
) -> str | None:
    """Resolve a property's LinkML ``range`` to a bespoke vocabulary key.

    ``range`` is the PascalCase enum name. We look it up in the index of
    enums actually defined in the LinkML schema. Returns the composite
    vocabulary key (``<domain>/<id>`` or bare ``<id>``) or ``None`` if the
    range isn't an enum.
    """
    return enum_to_vocab_key.get(range_value)


# ---------------------------------------------------------------------------
# Conversion: LinkML enum -> bespoke vocabulary
# ---------------------------------------------------------------------------


def _convert_enum_to_vocabulary(
    enum_name: str, enum_def: dict,
) -> tuple[str, dict] | None:
    """Return ``(composite_key, vocab_dict)`` in the bespoke shape.

    ``composite_key`` is ``<domain>/<id>`` for domain-scoped vocabularies
    (those whose source had a ``domain:`` field), bare ``<id>`` otherwise.
    The bespoke ``id`` value is the original kebab-case vocabulary id —
    derived heuristically from the PascalCase enum name and rendered as
    the local filename stem in the LinkML schema.
    """
    if not isinstance(enum_def, dict):
        return None
    annotations = _normalise_annotations(enum_def.get("annotations"))
    domain = _domain_from_source(annotations.get("source_domain"))
    kebab_id = _pascal_to_kebab(enum_name)
    composite_key = f"{domain}/{kebab_id}" if domain else kebab_id

    title = enum_def.get("title")
    description = enum_def.get("description")
    label = _split_multilingual(title, annotations, "label_")
    definition = _split_multilingual(description, annotations, "description_")

    values: list[dict] = []
    for code, pv in (enum_def.get("permissible_values") or {}).items():
        if not isinstance(pv, dict):
            continue
        pv_ann = _normalise_annotations(pv.get("annotations"))
        v_title = pv.get("title")
        v_desc = pv.get("description")
        original_code = pv_ann.get("standard_code")
        # The PV key is the canonical bespoke ``code``. When the migration
        # had to slugify a non-identifier source (e.g. ``"M-1"`` -> ``m_1``
        # or ``"self"`` -> ``self_``), the original verbatim form is in
        # ``standard_code``; reveal that as the canonical only when the
        # PV key was a slug-mangle of the original.
        sc_str = str(original_code) if original_code is not None else None
        is_mangled = (
            sc_str is not None and sc_str.strip() and sc_str != code
            and (
                code == "self_"
                or (not sc_str.replace("_", "").replace("-", "").isalnum())
                or sc_str.startswith(("-", "+"))
            )
        )
        if is_mangled:
            display_code: Any = sc_str
        else:
            display_code = code[:-1] if code == "self_" else code

        v_entry: dict[str, Any] = {
            "code": display_code,
            "label": _split_multilingual(v_title, pv_ann, "label_"),
            "definition": _split_multilingual(v_desc, pv_ann, "description_"),
        }
        if original_code is not None:
            v_entry["standard_code"] = sc_str
        for opt_key in ("parent_code", "level", "unmapped_reason",
                        "migration_note", "note"):
            if opt_key in pv_ann and pv_ann[opt_key] is not None:
                v_entry[opt_key] = pv_ann[opt_key]
        gta = _parse_json_annotation(pv_ann.get("group_type_applicability_json"))
        if isinstance(gta, list):
            v_entry["group_type_applicability"] = gta
        domain_on_value = _domain_from_source(pv_ann.get("source_domain"))
        if domain_on_value:
            v_entry["domain"] = domain_on_value
        values.append(v_entry)

    vocab: dict[str, Any] = {
        "id": kebab_id,
        "maturity": _maturity_from_status(enum_def.get("status")),
        "label": label,
        "definition": definition,
        "values": values,
    }
    if domain:
        vocab["domain"] = domain

    # Reconstruct system_mappings from per-PV exact_mappings/close_mappings.
    # The migration script lifts bespoke system_mappings.<system>.values into
    # per-PV ``exact_mappings`` (CURIEs like ``openspp:gender_type/m``); this
    # is the inverse for legacy consumers that still expect the nested dict.
    sm_reconstructed: dict[str, dict[str, Any]] = {}
    for code, pv in (enum_def.get("permissible_values") or {}).items():
        if not isinstance(pv, dict):
            continue
        display_code = code[:-1] if code == "self_" else code
        for mapping_key, match_strength in (
            ("exact_mappings", "exact"),
            ("close_mappings", "close"),
            ("broad_mappings", "broad"),
            ("narrow_mappings", "narrow"),
            ("related_mappings", "related"),
        ):
            for curie in pv.get(mapping_key, []) or []:
                if not isinstance(curie, str) or ":" not in curie:
                    continue
                system, target = curie.split(":", 1)
                if system in {"publicschema", "skos", "schema", "rdf", "rdfs", "owl"}:
                    continue
                bucket = sm_reconstructed.setdefault(system, {"values": []})
                bucket["values"].append({
                    "publicschema_code": display_code,
                    "maps_to": target,
                    "match": match_strength,
                })
    if sm_reconstructed:
        vocab["system_mappings"] = sm_reconstructed

    # Restore JSON-stringified structured fields.
    for src_key, dest_key in (
        ("standard_json", "standard"),
        ("sync_json", "sync"),
        ("same_standard_systems_json", "same_standard_systems"),
        ("convergence_json", "convergence"),
        ("vocab_references_json", "references"),
        ("vc_guidance_json", "vc_guidance"),
        ("see_also_json", "see_also"),
        ("tags_json", "tags"),
        ("system_mappings_json", "system_mappings"),
    ):
        parsed = _parse_json_annotation(annotations.get(src_key))
        if parsed is not None:
            vocab[dest_key] = parsed

    if "external_values" in annotations:
        ev = annotations.get("external_values")
        ev_val = _scalar_annotation(ev)
        if isinstance(ev_val, str):
            vocab["external_values"] = ev_val.lower() == "true"
        else:
            vocab["external_values"] = bool(ev_val)

    # external_equivalents reconstituted from the alignments record.
    eqs = _split_external_alignments(annotations.get("external_alignments_json"))
    if eqs:
        vocab["external_equivalents"] = eqs

    return composite_key, vocab


# ---------------------------------------------------------------------------
# Conversion: LinkML slot -> bespoke property
# ---------------------------------------------------------------------------


def _resolve_class_ref(
    bare_name: str,
    class_name_to_composite: dict[str, list[str]],
) -> str:
    """Pick the best composite key for a bare class reference.

    Bespoke ``concept:<X>`` references and ``references: <X>`` fields can
    point at either a root concept (bare key) or a domain-scoped concept
    (composite key). The migration script strips domain prefixes from
    ``range:`` values, so the reverse pass has to re-attach them when
    only one domain-scoped class with that name exists. When both a
    universal and a domain-scoped class share the name we prefer the
    universal — that matches the original schema's most common case.
    """
    candidates = class_name_to_composite.get(bare_name, [])
    if not candidates:
        return bare_name
    if bare_name in candidates:
        return bare_name
    # Only domain-scoped candidates: pick the lexicographically first
    # for deterministic output. There is currently no concept where two
    # domain-scoped classes share a name, so this branch typically yields
    # a single candidate.
    return sorted(candidates)[0]


def _convert_slot_to_property(
    slot_name: str,
    slot_def: dict,
    enum_to_vocab_key: dict[str, str],
    class_names: set[str],
    class_name_to_composite: dict[str, list[str]] | None = None,
) -> tuple[str, dict]:
    annotations = _normalise_annotations(slot_def.get("annotations"))
    title = slot_def.get("title")
    description = slot_def.get("description")
    label = _split_multilingual(title, annotations, "label_")
    definition = _split_multilingual(description, annotations, "description_")

    range_val = slot_def.get("range")
    vocabulary: str | None = None
    references: str | None = None
    bespoke_type: str = "string"

    if isinstance(range_val, str):
        if range_val in enum_to_vocab_key:
            vocabulary = enum_to_vocab_key[range_val]
            bespoke_type = "string"
        elif range_val in class_names:
            # Re-attach a domain prefix if the bare class name resolves
            # uniquely to a domain-scoped composite key. Without this, the
            # JSON-LD ``schema:rangeIncludes`` and JSON Schema $ref
            # generation would dangle off the bare URI instead of the
            # ``/sp/Program``-style URI the site expects.
            resolved = (
                _resolve_class_ref(range_val, class_name_to_composite)
                if class_name_to_composite is not None else range_val
            )
            bespoke_type = f"concept:{resolved}"
            references = resolved
        elif range_val in LINKML_RANGE_TO_BESPOKE_TYPE:
            bespoke_type = LINKML_RANGE_TO_BESPOKE_TYPE[range_val]
        else:
            bespoke_type = "string"

    cardinality = "multiple" if slot_def.get("multivalued") else "single"

    prop: dict[str, Any] = {
        "id": slot_name,
        "maturity": _maturity_from_status(slot_def.get("status")),
        "label": label,
        "definition": definition,
        "type": bespoke_type,
        "cardinality": cardinality,
    }
    if vocabulary is not None:
        prop["vocabulary"] = vocabulary
    if references is not None:
        prop["references"] = references

    # Scalar annotations restored verbatim.
    for scalar_key in (
        "category", "sensitivity", "domain_override", "vc_guidance",
        "immutable_after_status",
    ):
        if scalar_key in annotations and annotations[scalar_key] is not None:
            val = _scalar_annotation(annotations[scalar_key])
            prop[scalar_key] = val

    # JSON-stringified structured annotations.
    for src_key, dest_key in (
        ("convergence_json", "convergence"),
        ("system_mappings_json", "system_mappings"),
        ("valid_instruments_json", "valid_instruments"),
        ("age_applicability_json", "age_applicability"),
        ("see_also_json", "see_also"),
        ("tags_json", "tags"),
    ):
        parsed = _parse_json_annotation(annotations.get(src_key))
        if parsed is not None:
            prop[dest_key] = parsed

    eqs = _split_external_alignments(annotations.get("external_alignments_json"))
    if eqs:
        prop["external_equivalents"] = eqs

    # schema_org_equivalent is folded into exact_mappings; not strictly
    # recoverable but the legacy field is non-essential for rendering.

    return slot_name, prop


# ---------------------------------------------------------------------------
# Conversion: LinkML class -> bespoke concept
# ---------------------------------------------------------------------------


def _convert_class_to_concept(
    cls_name: str, cls_def: dict,
    class_name_to_composite: dict[str, list[str]] | None = None,
) -> tuple[str, dict] | None:
    """Return ``(composite_key, concept_dict)`` for a class.

    Skips abstract supertypes that never appeared in the bespoke catalog
    (``Citation``, ``Credential``). Concrete classes — including ``Agent``,
    ``Party``, ``Thing`` — pass through.
    """
    if not isinstance(cls_def, dict):
        return None
    class_uri = cls_def.get("class_uri", "")
    # Bibliography Citation subclasses are detected by class_uri pattern
    # ("publicschema:Citation/<biblio-id>") rather than name. Skip them
    # here; bibliography is loaded separately.
    if class_uri.startswith("publicschema:Citation/"):
        return None
    # Abstract umbrella classes that only exist in the LinkML view.
    if cls_name in {"Citation", "Credential"}:
        return None

    annotations = _normalise_annotations(cls_def.get("annotations"))
    title = cls_def.get("title")
    description = cls_def.get("description")
    label = _split_multilingual(title, annotations, "label_")
    definition = _split_multilingual(description, annotations, "description_")
    domain = _domain_from_source(annotations.get("source_domain"))
    composite_key = f"{domain}/{cls_name}" if domain else cls_name

    # Supertypes: is_a + mixins; both are bare class names in LinkML. The
    # bespoke ``supertypes:`` field stores composite keys for domain-scoped
    # supertypes (e.g. ``crvs/VitalEvent``); we re-attach the prefix when
    # the bare name resolves unambiguously.
    def _resolve_super(name: str) -> str:
        if class_name_to_composite is None:
            return name
        candidates = class_name_to_composite.get(name, [])
        if not candidates or name in candidates:
            return name
        return sorted(candidates)[0]

    supertypes: list[str] = []
    is_a = cls_def.get("is_a")
    if isinstance(is_a, str) and is_a:
        supertypes.append(_resolve_super(is_a))
    for m in cls_def.get("mixins") or []:
        if isinstance(m, str) and m:
            supertypes.append(_resolve_super(m))

    slots = [s for s in (cls_def.get("slots") or []) if isinstance(s, str)]

    concept: dict[str, Any] = {
        "id": cls_name,
        "maturity": _maturity_from_status(cls_def.get("status")),
        "label": label,
        "definition": definition,
        "properties": slots,
        "supertypes": supertypes,
        "subtypes": [],  # build.py reads subtypes from out_concepts only
    }
    if domain:
        concept["domain"] = domain
    if cls_def.get("abstract"):
        concept["abstract"] = True
    if _scalar_annotation(annotations.get("featured")):
        featured_val = _scalar_annotation(annotations.get("featured"))
        if isinstance(featured_val, str):
            concept["featured"] = featured_val.lower() == "true"
        else:
            concept["featured"] = bool(featured_val)

    # JSON-stringified structured annotations.
    for src_key, dest_key in (
        ("convergence_json", "convergence"),
        ("property_groups_json", "property_groups"),
        ("see_also_json", "see_also"),
        ("tags_json", "tags"),
        ("vc_guidance_json", "vc_guidance"),
    ):
        parsed = _parse_json_annotation(annotations.get(src_key))
        if parsed is not None:
            concept[dest_key] = parsed

    eqs = _split_external_alignments(annotations.get("external_alignments_json"))
    if eqs:
        concept["external_equivalents"] = eqs

    return composite_key, concept


# ---------------------------------------------------------------------------
# Bibliography / credentials / categories
# ---------------------------------------------------------------------------


def _convert_citation_to_bibliography(
    cls_name: str, cls_def: dict,
) -> tuple[str, dict] | None:
    annotations = _normalise_annotations(cls_def.get("annotations"))
    biblio_id = _scalar_annotation(annotations.get("citation_id"))
    if not isinstance(biblio_id, str) or not biblio_id:
        return None
    entry: dict[str, Any] = {"id": biblio_id}
    for key in (
        "title", "short_title", "standard_number", "publisher",
        "year", "version", "type", "domain", "uri", "access", "status",
    ):
        val = _scalar_annotation(annotations.get(key))
        if val is not None:
            entry[key] = val
    authors = _parse_json_annotation(annotations.get("authors_json"))
    if isinstance(authors, list):
        entry["authors"] = authors
    informs = _parse_json_annotation(annotations.get("informs_json"))
    if isinstance(informs, dict):
        entry["informs"] = {
            "concepts": list(informs.get("concepts") or []),
            "vocabularies": list(informs.get("vocabularies") or []),
            "properties": list(informs.get("properties") or []),
        }
    return biblio_id, entry


def _convert_credential_class(
    cls_name: str, cls_def: dict,
) -> tuple[str, dict] | None:
    if cls_name == "Credential" or cls_def.get("abstract"):
        return None
    annotations = _normalise_annotations(cls_def.get("annotations"))
    title = cls_def.get("title")
    description = cls_def.get("description")
    label = _split_multilingual(title, annotations, "label_")
    definition = _split_multilingual(description, annotations, "description_")
    subject_concept = _scalar_annotation(annotations.get("subject_concept"))
    included = _parse_json_annotation(annotations.get("included_concepts_json"))
    if not isinstance(included, list):
        included = []
    entry: dict[str, Any] = {
        "id": cls_name,
        "maturity": _maturity_from_status(cls_def.get("status")),
        "label": label,
        "definition": definition,
        "subject_concept": subject_concept,
        "included_concepts": included,
    }
    return cls_name, entry


def _convert_categories_enum(enum_def: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for code, pv in (enum_def.get("permissible_values") or {}).items():
        if not isinstance(pv, dict):
            continue
        pv_ann = _normalise_annotations(pv.get("annotations"))
        title = pv.get("title")
        label = _split_multilingual(title, pv_ann, "label_")
        out[code] = {"label": label}
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _bibliography_refs_from_annotations(
    annotations: dict | None,
) -> list[str]:
    if not annotations:
        return []
    refs = _parse_json_annotation(annotations.get("bibliography_refs"))
    if isinstance(refs, list):
        return [r for r in refs if isinstance(r, str)]
    return []


def load_raw_from_linkml(linkml_dir: Path) -> dict[str, Any]:
    """Load and re-project all LinkML domain files under ``linkml_dir``.

    Returns a dict with the keys:
    ``meta``, ``concepts``, ``properties``, ``vocabularies``, ``bibliography``,
    ``credentials``, ``categories``. Each entry is shaped to match the
    bespoke loader output (see ``build/build.py``'s ``build_vocabulary``).
    """
    composite = _load_yaml(linkml_dir / "publicschema.yaml")
    # Meta is reconstructed from the composite header. The bespoke
    # ``schema/_meta.yaml`` carries name/base_uri/version/maturity/languages/license;
    # only base_uri/version/name/license/maturity survive the migration.
    meta = {
        "name": composite.get("name") or "PublicSchema",
        "base_uri": "https://publicschema.org/",
        "version": str(composite.get("version") or "0.1.0"),
        "maturity": "draft",
        "languages": ["en", "fr", "es"],
        "license": composite.get("license") or "CC-BY-4.0",
    }
    # Recover the user-facing display name from ``title`` if the
    # short ``name:`` is the lowercased package id.
    title = composite.get("title")
    if isinstance(title, str) and title:
        meta["name"] = title

    # Walk every domain file (skip external partials).
    domain_files: list[Path] = []
    if linkml_dir.exists():
        for p in sorted(linkml_dir.glob("*.yaml")):
            if p.name in {"publicschema.yaml", "publicschema-extensions.yaml"}:
                continue
            if p.stem.startswith("_"):
                continue
            domain_files.append(p)

    # First pass: index every class/enum/slot so cross-refs resolve. This
    # is necessary because slots reference enums (vocabulary look-ups) and
    # classes (concept references) across domain files.
    all_classes: dict[str, dict] = {}
    all_slots: dict[str, dict] = {}
    all_enums: dict[str, dict] = {}
    citation_classes: dict[str, dict] = {}
    credential_classes: dict[str, dict] = {}
    categories_enum: dict | None = None

    for path in domain_files:
        doc = _load_yaml(path)
        for k, v in (doc.get("classes") or {}).items():
            if not isinstance(v, dict):
                continue
            class_uri = v.get("class_uri", "")
            if path.name == "bibliography.yaml" or class_uri.startswith(
                "publicschema:Citation"
            ):
                citation_classes[k] = v
            elif path.name == "credentials.yaml":
                credential_classes[k] = v
            else:
                all_classes[k] = v
        for k, v in (doc.get("slots") or {}).items():
            if isinstance(v, dict):
                all_slots[k] = v
        for k, v in (doc.get("enums") or {}).items():
            if not isinstance(v, dict):
                continue
            if path.name == "categories.yaml" and k == "PropertyCategory":
                categories_enum = v
            else:
                all_enums[k] = v

    # Build vocabulary index first so slot conversion can resolve ranges.
    vocabularies_raw: dict[str, dict] = {}
    enum_to_vocab_key: dict[str, str] = {}
    for enum_name, enum_def in all_enums.items():
        converted = _convert_enum_to_vocabulary(enum_name, enum_def)
        if not converted:
            continue
        composite_key, vocab_dict = converted
        vocabularies_raw[composite_key] = vocab_dict
        enum_to_vocab_key[enum_name] = composite_key

    # Concepts. We do a first pass without composite resolution to learn
    # which bare class names correspond to which composite keys, then a
    # second pass to re-attach domain prefixes on supertype references.
    class_names = set(all_classes.keys())
    composite_index_first_pass: dict[str, list[str]] = {}
    for cls_name, cls_def in all_classes.items():
        converted = _convert_class_to_concept(cls_name, cls_def)
        if not converted:
            continue
        composite_key, _ = converted
        bare = composite_key.split("/", 1)[-1] if "/" in composite_key else composite_key
        composite_index_first_pass.setdefault(bare, []).append(composite_key)

    concepts_raw: dict[str, dict] = {}
    for cls_name, cls_def in all_classes.items():
        converted = _convert_class_to_concept(
            cls_name, cls_def,
            class_name_to_composite=composite_index_first_pass,
        )
        if not converted:
            continue
        composite_key, concept_dict = converted
        concepts_raw[composite_key] = concept_dict

    class_name_to_composite = composite_index_first_pass

    # Properties.
    properties_raw: dict[str, dict] = {}
    for slot_name, slot_def in all_slots.items():
        slot_id, prop_dict = _convert_slot_to_property(
            slot_name, slot_def, enum_to_vocab_key, class_names,
            class_name_to_composite=class_name_to_composite,
        )
        properties_raw[slot_id] = prop_dict

    # Bibliography (one Citation subclass per entry).
    bibliography_raw: dict[str, dict] = {}
    for cls_name, cls_def in citation_classes.items():
        converted = _convert_citation_to_bibliography(cls_name, cls_def)
        if not converted:
            continue
        biblio_id, entry = converted
        bibliography_raw[biblio_id] = entry

    # Credentials (one class per descriptor).
    credentials_raw: dict[str, dict] = {}
    for cls_name, cls_def in credential_classes.items():
        converted = _convert_credential_class(cls_name, cls_def)
        if not converted:
            continue
        cred_id, entry = converted
        credentials_raw[cred_id] = entry

    # Categories.
    categories_raw: dict[str, dict] = {}
    if categories_enum is not None:
        categories_raw = _convert_categories_enum(categories_enum)

    # Reconstruct ``subtypes`` (the inverse of ``supertypes``). The migration
    # records the directed edge once on the child via is_a/mixins; consumers
    # that expect the bespoke shape (test_agent_hierarchy.py etc.) want the
    # reverse edge populated as well. Subtype entries use composite keys
    # (``<domain>/<id>``) so cross-domain hierarchies don't collapse.
    short_name = {k: k.split("/")[-1] for k in concepts_raw}
    for child_key, child in concepts_raw.items():
        for parent in child.get("supertypes", []) or []:
            parent_short = parent.split("/")[-1]
            for cand_key, cand in concepts_raw.items():
                if cand_key == parent or short_name[cand_key] == parent_short:
                    cand.setdefault("subtypes", []).append(child_key)
                    break

    return {
        "meta": meta,
        "concepts": concepts_raw,
        "properties": properties_raw,
        "vocabularies": vocabularies_raw,
        "bibliography": bibliography_raw,
        "credentials": credentials_raw,
        "categories": categories_raw,
    }
