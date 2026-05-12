#!/usr/bin/env python3
"""
Migrate PublicSchema bespoke YAML to LinkML. HISTORICAL/REFERENCE ONLY.

After the LinkML cutover this script is no longer invoked by the build
pipeline. It is preserved so that an old bespoke source tree can be
re-migrated if needed (e.g., during release archaeology). The current
source of truth is the LinkML composite under ``schema/`` directly.

When run, the script reads bespoke YAML from the directory passed as a
positional arg (default ``schema/``, which after cutover no longer
matches the expected shape) and writes to ``dist/linkml/`` (gitignored).
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "schema"
META_FILE = SOURCE_DIR / "_meta.yaml"
PROJECT_FILE = SOURCE_DIR / "project.yaml"
BASES_DIR = SOURCE_DIR / "bases"
PREFIXES_FILE = ROOT / "build" / "external_system_prefixes.yaml"
EXTENSIONS_FILE = ROOT / "build" / "linkml_extensions.yaml"
OUTPUT_DIR = ROOT / "dist" / "linkml"
EXTERNAL_DIR = OUTPUT_DIR / "external"


def load_base_uri() -> str:
    """Read the authoritative PublicSchema base URI from schema/_meta.yaml,
    cross-checking schema/project.yaml and (when present) schema/bases/active-base.yaml.

    Returns the trailing-slash-terminated URI (e.g. 'https://publicschema.org/').
    """
    with META_FILE.open() as f:
        meta = yaml.safe_load(f) or {}
    base = meta.get("base_uri")
    if not base:
        raise SystemExit(f"schema/_meta.yaml has no base_uri")
    if not base.endswith("/"):
        base = base + "/"
    # Cross-check project.yaml
    if PROJECT_FILE.exists():
        with PROJECT_FILE.open() as f:
            proj = yaml.safe_load(f) or {}
        proj_base = (proj.get("schema_project") or {}).get("base_uri")
        if proj_base and not proj_base.endswith("/"):
            proj_base = proj_base + "/"
        if proj_base and proj_base != base:
            print(f"warn: base_uri mismatch — _meta={base} vs project={proj_base}", file=sys.stderr)
    # Cross-check bases/active-base.yaml strategy
    active = BASES_DIR / "active-base.yaml"
    if active.exists():
        with active.open() as f:
            bdoc = yaml.safe_load(f) or {}
        strategy = bdoc.get("base_strategy")
        if strategy and strategy != "publicschema-native":
            print(
                f"warn: bases/active-base.yaml declares base_strategy={strategy!r}; "
                "migration assumes 'publicschema-native'",
                file=sys.stderr,
            )
    return base


PUBLICSCHEMA_BASE = load_base_uri()

STATUS_MAP = {
    "draft": "bibo:draft",
    "candidate": "bibo:status/forthcoming",
    "normative": "bibo:status/published",
}

# Domain assignment by concept name. Concepts not listed here go to "misc".
# Keyed by concept id (PascalCase, as it appears in schema/concepts/*.yaml).
CONCEPT_DOMAINS: dict[str, str] = {
    # core
    "Agent": "core", "Party": "core", "Thing": "core",
    # identity
    "Person": "identity", "Organization": "identity", "Household": "identity",
    "Family": "identity", "Group": "identity", "Address": "identity",
    "CrvsPerson": "identity",
    # civil_status (births, deaths, marriages, certificates)
    "Birth": "civil_status", "Death": "civil_status", "Marriage": "civil_status",
    "Divorce": "civil_status", "Adoption": "civil_status",
    "CivilStatusRecord": "civil_status", "CivilStatusAnnotation": "civil_status",
    "CivilStatusDocument": "civil_status", "FamilyRegister": "civil_status",
    "Event": "civil_status", "Certificate": "civil_status",
    # program (enrollment, entitlement)
    "Program": "program", "Enrollment": "program", "Entitlement": "program",
    "EligibilityDecision": "program", "BenefitSchedule": "program",
    # payment (deliveries)
    "Payment": "payment", "Delivery": "payment", "DeliveryItem": "payment",
    # assessment
    "Assessment": "assessment", "AssessmentBand": "assessment",
    "FunctioningProfile": "assessment", "FunctioningStatus": "assessment",
    "NutritionStatus": "assessment", "Profile": "assessment",
    # other
    "ConsentRecord": "consent",
    "BiometricSample": "biometric",
    "Document": "document",
    "IdentityDocument": "document",
}

# Special vocabularies that go to vocabularies.yaml regardless of usage.
DOMAIN_VOCABULARIES = "vocabularies"

# Source `domain:` values (PublicSchema-internal) -> LinkML domain name.
SOURCE_DOMAIN_MAP = {
    "crvs": "civil_status",
    "sp": "program",
    "core": "core",
    "identity": "identity",
    "payment": "payment",
    "assessment": "assessment",
}

# These source field names are recognised; anything else is reported.
KNOWN_CONCEPT_FIELDS = {
    "id", "label", "definition", "maturity", "featured", "abstract", "domain",
    "properties", "property_groups", "supertypes", "subtypes",
    "external_equivalents", "convergence",
    "see_also", "tags", "vc_guidance",
}
KNOWN_PROPERTY_FIELDS = {
    "id", "label", "definition", "maturity",
    "type", "cardinality", "vocabulary", "references", "category",
    "schema_org_equivalent", "external_equivalents", "system_mappings",
    "convergence", "tags", "domain_override", "sensitivity",
    "valid_instruments", "age_applicability", "immutable_after_status",
    "see_also", "vc_guidance",
}
KNOWN_VOCAB_FIELDS = {
    "id", "label", "definition", "maturity",
    "standard", "sync", "same_standard_systems", "external_values",
    "values", "external_equivalents", "system_mappings",
    "see_also", "tags", "domain", "references", "vc_guidance",
}

# Credentials are W3C VC descriptor metadata: each declares a subject_concept
# and an optional list of included_concepts.
KNOWN_CREDENTIAL_FIELDS = {
    "id", "label", "definition", "maturity",
    "subject_concept", "included_concepts",
    "see_also", "tags",
}

# Bibliography entries (citation records). One file per cited source.
# The `informs:` block reverses into per-target `bibliography_refs` annotations.
KNOWN_BIBLIOGRAPHY_FIELDS = {
    "id", "title", "short_title", "publisher", "year",
    "type", "domain", "uri", "access", "status",
    "informs", "label", "definition", "tags",
    "standard_number", "version", "authors", "note",
}

# Categories: UI taxonomy keys that property_groups[].category points at.
# The file has top-level entries (category_id -> {label: {en, fr, es}}); no `id` key.
KNOWN_CATEGORY_VALUE_FIELDS = {"label", "definition", "description"}

# Per-value fields inside `values:` of a vocabulary file. Anything not in this set
# is surfaced in the migration report as unmapped. Derived from an audit of all
# 115 vocabulary files (see build/AUDIT_NOTES.md for the inventory).
PER_VALUE_KNOWN_FIELDS = {
    "code", "label", "definition",
    "standard_code", "note", "notes",
    "parent_code", "level",
    "domain",
    "group_type_applicability",
    "unmapped_reason", "migration_note",
}

# Per-value fields inside system_mappings.<system>.values[]. Same audit basis.
SYSTEM_MAPPING_VALUE_KNOWN_FIELDS = {
    "code", "label", "maps_to",
    "note", "notes",
    "unmapped_reason", "migration_note",
}

# ============================================================================
# Data classes
# ============================================================================


@dataclasses.dataclass
class SourceFile:
    path: Path
    kind: str  # 'concept' | 'property' | 'vocabulary' | 'credential' | 'bibliography' | 'project' | 'meta' | 'categories' | 'other'
    id: str | None
    data: dict


@dataclasses.dataclass
class SystemRegistry:
    """Loaded from build/external_system_prefixes.yaml."""
    systems: dict[str, dict]  # system_id -> {prefix, uri, label, source, ...}
    vocab_prefixes: dict[str, dict]  # extra prefixes for external_equivalents


@dataclasses.dataclass
class MigrationContext:
    inv: dict[str, SourceFile]  # legacy single-key index (id -> SourceFile, last-write-wins; do not use for cross-kind lookups)
    concepts: dict[str, SourceFile]  # id -> concept SourceFile
    properties: dict[str, SourceFile]  # id -> property SourceFile
    vocabularies: dict[str, SourceFile]  # id -> vocabulary SourceFile
    by_kind: dict[str, list[SourceFile]]
    systems: SystemRegistry
    # SEMIC alignment architecture (P4 series on main):
    external_references: dict[str, dict] = dataclasses.field(default_factory=dict)  # id -> doc
    external_terms_by_source: dict[str, list[dict]] = dataclasses.field(default_factory=dict)  # source_id -> terms list
    alignments_by_subject: dict[tuple[str, str], list[dict]] = dataclasses.field(default_factory=lambda: collections.defaultdict(list))  # (kind, id) -> list[alignment record]
    bases: dict[str, dict] = dataclasses.field(default_factory=dict)  # id -> doc
    # Bibliography reverse index: (kind, id) -> list of bibliography ids that inform this element.
    # Built from schema/bibliography/*.yaml `informs: { concepts, vocabularies, properties }`.
    bibliography_refs: dict[tuple[str, str], list[str]] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(list)
    )
    # Categories taxonomy from schema/categories.yaml (flat key -> {label: {lang: text}}).
    categories: dict[str, dict] = dataclasses.field(default_factory=dict)
    # Per-system enum aggregation: system -> { enum_name -> { values -> {meaning_curie, title} } }
    external_enums: dict[str, dict[str, dict[str, dict]]] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(lambda: collections.defaultdict(dict))
    )
    # Domain assignments (filled by Phase 1).
    concept_domain: dict[str, str] = dataclasses.field(default_factory=dict)
    property_domain: dict[str, str] = dataclasses.field(default_factory=dict)
    vocab_domain: dict[str, str] = dataclasses.field(default_factory=dict)
    # Unmapped fields encountered (for migration report).
    unmapped: list[str] = dataclasses.field(default_factory=list)
    # Crosswalks emitted: (target_curie, source_class+value) for referential check.
    crosswalk_refs: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    # is_a / mixins choices for each concept (for report).
    inheritance_choices: dict[str, dict] = dataclasses.field(default_factory=dict)
    # Domain split rationale (for report).
    domain_rationale: dict[str, str] = dataclasses.field(default_factory=dict)


# ============================================================================
# Loading
# ============================================================================


def classify(path: Path) -> str:
    rel = path.relative_to(SOURCE_DIR).parts
    if path.name == "_meta.yaml":
        return "meta"
    if path.name == "project.yaml":
        return "project"
    if path.name == "categories.yaml":
        return "categories"
    top = rel[0]
    if top == "concepts":
        return "concept"
    if top == "properties":
        return "property"
    if top == "vocabularies":
        return "vocabulary"
    if top == "credentials":
        return "credential"
    if top == "bibliography":
        return "bibliography"
    if top == "external_references":
        return "external_reference"
    if top == "external_terms":
        return "external_terms"
    if top == "alignments":
        return "alignment"
    if top == "bases":
        return "base"
    return "other"


def load_systems() -> SystemRegistry:
    with PREFIXES_FILE.open() as f:
        data = yaml.safe_load(f)
    return SystemRegistry(
        systems=data.get("systems", {}),
        vocab_prefixes=data.get("external_vocabulary_prefixes", {}),
    )


def load_inventory(ctx_holder: dict | None = None) -> tuple[
    dict[str, SourceFile],
    dict[str, SourceFile],
    dict[str, SourceFile],
    dict[str, SourceFile],
    dict[str, list[SourceFile]],
]:
    """Return (combined_inv, concepts, properties, vocabularies, by_kind).

    Property and vocabulary IDs collide on 5 names (country, currency, literacy,
    occupation, sex) — they must be indexed separately.

    Also populates SEMIC alignment data (external_references, external_terms,
    alignments, bases) into ctx_holder if provided.
    """
    inv: dict[str, SourceFile] = {}
    concepts: dict[str, SourceFile] = {}
    properties: dict[str, SourceFile] = {}
    vocabularies: dict[str, SourceFile] = {}
    by_kind: dict[str, list[SourceFile]] = collections.defaultdict(list)
    external_references: dict[str, dict] = {}
    external_terms_by_source: dict[str, list[dict]] = {}
    alignments_by_subject: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    bases: dict[str, dict] = {}
    for p in sorted(SOURCE_DIR.rglob("*.yaml")):
        try:
            with p.open() as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"warn: skipping unparseable {p}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        kind = classify(p)
        sf = SourceFile(path=p, kind=kind, id=data.get("id"), data=data)
        by_kind[kind].append(sf)
        if not sf.id:
            continue
        if kind == "concept":
            concepts[sf.id] = sf
            inv.setdefault(sf.id, sf)
        elif kind == "property":
            properties[sf.id] = sf
            inv.setdefault(sf.id, sf)
        elif kind == "vocabulary":
            vocabularies[sf.id] = sf
            inv.setdefault(sf.id, sf)
        elif kind == "external_reference":
            external_references[sf.id] = data
        elif kind == "external_terms":
            src_id = data.get("source_id")
            if src_id and isinstance(data.get("terms"), list):
                external_terms_by_source[src_id] = data["terms"]
        elif kind == "alignment":
            for a in (data.get("alignments") or []):
                if not isinstance(a, dict):
                    continue
                subj = a.get("subject") or {}
                s_kind = subj.get("kind")
                s_id = subj.get("id")
                if s_kind and s_id:
                    alignments_by_subject[(s_kind, s_id)].append({
                        "alignment": a,
                        "set": data,
                    })
        elif kind == "base":
            bases[sf.id] = data

    # Bibliography reverse index: for each bibliography entry, fan out the
    # `informs:` lists into (kind, id) -> [biblio_id] entries.
    bibliography_refs: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for sf in by_kind.get("bibliography", []):
        biblio_id = sf.id
        if not biblio_id:
            continue
        informs = (sf.data.get("informs") or {})
        for target_kind, source_key in (
            ("concept", "concepts"),
            ("property", "properties"),
            ("vocabulary", "vocabularies"),
        ):
            for target_id in (informs.get(source_key) or []):
                if not isinstance(target_id, str):
                    continue
                # Bibliography may reference path-form ids (e.g. "crvs/Person").
                # Normalise to the bare id matching our index keys.
                bare = target_id.rsplit("/", 1)[-1]
                bibliography_refs[(target_kind, bare)].append(biblio_id)

    # Categories: a single top-level file mapping category_id -> {label: {...}}.
    # Stored as a flat dict; later emitted as an Enum.
    categories: dict[str, dict] = {}
    for sf in by_kind.get("categories", []):
        for k, v in (sf.data or {}).items():
            if isinstance(v, dict):
                categories[k] = v

    if ctx_holder is not None:
        ctx_holder["external_references"] = external_references
        ctx_holder["external_terms_by_source"] = external_terms_by_source
        ctx_holder["alignments_by_subject"] = alignments_by_subject
        ctx_holder["bases"] = bases
        ctx_holder["bibliography_refs"] = bibliography_refs
        ctx_holder["categories"] = categories
    return inv, concepts, properties, vocabularies, by_kind


# ============================================================================
# Naming helpers
# ============================================================================

_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")


def slugify(s: str) -> str:
    s = _NON_ALNUM.sub("_", str(s)).strip("_").lower()
    return s or "_"


def pascal_case(s: str) -> str:
    tokens = _NON_ALNUM.split(str(s))
    return "".join(t[:1].upper() + t[1:] for t in tokens if t)


# Reserved Python attribute names that conflict with jsonasobj2.ExtendedNamespace
# when used as permissible value keys (each PV's key becomes an attribute on a
# JsonObj built via ExtendedNamespace.__init__(self, **{key: value}); `self`
# collides with the positional `self` arg of __init__).
RESERVED_VALUE_KEYS = {"self"}


def value_key(maps_to: Any) -> str:
    """Stable permissible value key from a maps_to code.

    Numeric-looking codes (e.g. DHS '1'..'5', ISO 5218 '0'..'9') are kept
    verbatim; everything else is slugified. Keys that collide with Python
    reserved attribute names (e.g. 'self') are suffixed with an underscore.
    """
    s = str(maps_to)
    if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
        return s
    out = slugify(s)
    if out in RESERVED_VALUE_KEYS:
        out = f"{out}_"
    return out


def safe_curie_prefix(system_id: str) -> str:
    # CURIE prefix tokens (NCName) cannot contain hyphens at the start but can mid-token;
    # XML NCName disallows hyphens at start. Replace problematic chars.
    p = re.sub(r"[^A-Za-z0-9_-]", "_", system_id)
    # Replace underscores with hyphens (kebab) to match the convention used in our prefix file.
    return p.replace("_", "-")


# ============================================================================
# Conversion helpers
# ============================================================================


def get_multilingual(d: dict, key: str) -> tuple[str | None, dict[str, str]]:
    """For a field like label or definition, return (en, {lang: text for fr/es/...})."""
    v = d.get(key)
    if isinstance(v, str):
        return v, {}
    if isinstance(v, dict):
        en = v.get("en")
        other = {k: vv for k, vv in v.items() if k != "en" and isinstance(vv, str)}
        return en, other
    return None, {}


def i18n_annotations(label_other: dict[str, str], desc_other: dict[str, str]) -> dict:
    """Return compact-form scalar annotations for non-English label/definition."""
    out = {}
    for lang, text in sorted(label_other.items()):
        out[f"label_{lang}"] = text.strip()
    for lang, text in sorted(desc_other.items()):
        out[f"description_{lang}"] = text.strip()
    return out


def json_annotation(key: str, value: Any) -> tuple[str, str] | None:
    """Encode a structured (non-scalar) annotation value as a JSON-string annotation.

    Returns (key_with_json_suffix, json_string). JSON-string encoding survives
    LinkML annotation validation and produces clean RDF literals.
    """
    if value is None:
        return None
    return f"{key}_json", json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def map_external_equivalents(
    eqs: dict | None, ctx: MigrationContext
) -> tuple[list[str], list[str], list[dict]]:
    """Return (exact_mappings, close_mappings, alignments_records)."""
    exact: list[str] = []
    close: list[str] = []
    records: list[dict] = []
    if not isinstance(eqs, dict):
        return exact, close, records
    for vocab_id, entry in eqs.items():
        if not isinstance(entry, dict):
            continue
        uri = entry.get("uri")
        match = entry.get("match", "exact")
        # Convert uri to CURIE if possible, else leave as full URI.
        curie = uri_to_curie(uri, ctx) if isinstance(uri, str) else None
        target = curie or uri
        if target:
            if match == "exact":
                exact.append(target)
            elif match in ("close", "narrow", "broad", "related"):
                close.append(target)
        rec = {
            "vocabulary_id": vocab_id,
            "match": match,
        }
        for k in ("label", "uri", "vocabulary", "note"):
            if entry.get(k) is not None:
                rec[k] = entry[k]
        records.append(rec)
    return exact, close, records


# Source URIs sometimes use https:// where the canonical form is http:// (and
# vice versa). Normalise before matching against the declared prefix table.
URI_NORMALISATIONS = {
    "https://schema.org/": "http://schema.org/",
}


def normalise_uri(uri: str) -> str:
    for src_prefix, dst_prefix in URI_NORMALISATIONS.items():
        if uri.startswith(src_prefix):
            return dst_prefix + uri[len(src_prefix):]
    return uri


def uri_to_curie(uri: str, ctx: MigrationContext) -> str | None:
    uri = normalise_uri(uri)
    # Candidate (prefix_uri, curie_prefix) pairs from all three sources.
    candidates: list[tuple[str, str]] = []
    candidates.extend(
        (e["uri"], pid) for pid, e in ctx.systems.vocab_prefixes.items() if "uri" in e
    )
    candidates.extend(
        (e["uri"], e.get("prefix", sid)) for sid, e in ctx.systems.systems.items() if "uri" in e
    )
    # SEMIC external_references publish accurate upstream prefix tables.
    for ref_doc in ctx.external_references.values():
        for ref_prefix, ref_uri in (ref_doc.get("prefixes") or {}).items():
            if isinstance(ref_uri, str):
                candidates.append((ref_uri, ref_prefix))
    # Longest prefix URI wins; ties broken alphabetically by prefix.
    candidates.sort(key=lambda x: (-len(x[0]), x[1]))
    for prefix_uri, curie_prefix in candidates:
        if uri.startswith(prefix_uri):
            return f"{curie_prefix}:{uri[len(prefix_uri):]}"
    return None


# ============================================================================
# Conversion: vocabulary -> EnumDefinition
# ============================================================================


def convert_vocabulary(sf: SourceFile, ctx: MigrationContext) -> tuple[str, dict]:
    """Return (enum_name, EnumDefinition dict)."""
    src = sf.data
    enum_name = pascal_case(src.get("id") or sf.path.stem)
    en_label, label_other = get_multilingual(src, "label")
    en_def, def_other = get_multilingual(src, "definition")

    enum: dict[str, Any] = {
        "enum_uri": f"publicschema:{enum_name}",
    }
    if en_label:
        enum["title"] = en_label
    if en_def:
        enum["description"] = en_def

    # Status
    maturity = src.get("maturity")
    if maturity and maturity in STATUS_MAP:
        enum["status"] = STATUS_MAP[maturity]

    # Permissible values. Per the audit (build/AUDIT_NOTES.md), every recognised
    # per-value field is read explicitly; anything else lands in ctx.unmapped.
    pvs: dict[str, dict] = {}
    for v in src.get("values") or []:
        if not isinstance(v, dict):
            continue
        code = v.get("code")
        if code is None:
            continue
        key = value_key(code)
        pv: dict[str, Any] = {"meaning": f"publicschema:{enum_name}/{key}"}
        v_en_label, v_other_label = get_multilingual(v, "label")
        if v_en_label:
            pv["title"] = v_en_label
        # Per-value definition (LinkML PermissibleValue.description is a first-class slot)
        v_en_def, v_other_def = get_multilingual(v, "definition")
        if v_en_def:
            pv["description"] = v_en_def

        v_annotations: dict[str, Any] = {}
        # Multilingual labels and definitions for this value
        for lang, text in sorted(v_other_label.items()):
            v_annotations[f"label_{lang}"] = text.strip()
        for lang, text in sorted(v_other_def.items()):
            v_annotations[f"description_{lang}"] = text.strip()

        # standard_code: canonical code in the parent vocabulary's `standard:`
        # (e.g. ISO 3166 uppercase 'AF' for our 'af'). The audit found this in
        # 10 files / 9,476 values — largest silent-loss source.
        if v.get("standard_code") is not None:
            v_annotations["standard_code"] = str(v["standard_code"])

        # note / notes — value-level mapping or reference guidance.
        if v.get("note") is not None:
            v_annotations["note"] = str(v["note"]).strip()
        if v.get("notes") is not None:
            notes_val = v["notes"]
            if isinstance(notes_val, dict):
                # multilingual notes — keep English where available, else flatten
                en_notes = notes_val.get("en")
                if en_notes:
                    v_annotations.setdefault("note", str(en_notes).strip())
                for lang, text in notes_val.items():
                    if lang != "en":
                        v_annotations[f"note_{lang}"] = str(text).strip()
            else:
                v_annotations.setdefault("note", str(notes_val).strip())

        # parent_code / level — hierarchical vocabularies (occupation.yaml has 609/619).
        if v.get("parent_code") is not None:
            v_annotations["parent_code"] = str(v["parent_code"])
        if v.get("level") is not None:
            v_annotations["level"] = v["level"] if isinstance(v["level"], int) else str(v["level"])

        # domain on a value (rare; 3 occurrences across 2 files)
        if v.get("domain") is not None:
            v_annotations["source_domain"] = str(v["domain"])

        # group_type_applicability — list constraint (1 file / 13 values)
        if v.get("group_type_applicability") is not None:
            for jk, jv in [
                json_annotation("group_type_applicability", v["group_type_applicability"]),
            ]:
                v_annotations[jk] = jv

        # unmapped_reason / migration_note — value-level metadata
        if v.get("unmapped_reason") is not None:
            v_annotations["unmapped_reason"] = str(v["unmapped_reason"])
        if v.get("migration_note") is not None:
            v_annotations["migration_note"] = str(v["migration_note"]).strip()

        # Surface anything else as unmapped (per-value).
        for fname in v.keys():
            if fname not in PER_VALUE_KNOWN_FIELDS:
                ctx.unmapped.append(f"vocabulary:{sf.path.name}:values[].{fname}")

        if v_annotations:
            pv["annotations"] = v_annotations
        # Crosswalks via system_mappings (collected globally below; here we only
        # populate exact_mappings if a system_mappings entry maps to this value).
        # That happens in finalize step after the full enum is known.
        pvs[key] = pv

    if pvs:
        enum["permissible_values"] = pvs

    # External alignments at the enum level
    exact, close, alignments = map_external_equivalents(src.get("external_equivalents"), ctx)
    if exact:
        enum["exact_mappings"] = exact
    if close:
        enum["close_mappings"] = close

    # i18n + structured annotations
    annotations: dict[str, Any] = i18n_annotations(label_other, def_other)
    if src.get("domain"):
        annotations["source_domain"] = str(src["domain"])
    for jk, jv in filter(
        None,
        [
            json_annotation("external_alignments", alignments or None),
            json_annotation("standard", src.get("standard")),
            json_annotation("sync", src.get("sync")),
            json_annotation("same_standard_systems", src.get("same_standard_systems")),
            json_annotation("convergence", src.get("convergence")),
            json_annotation("vocab_references", src.get("references")),
            json_annotation("vc_guidance", src.get("vc_guidance")),
            json_annotation("see_also", src.get("see_also")),
            json_annotation("tags", src.get("tags")),
        ],
    ):
        annotations[jk] = jv
    if src.get("external_values") is not None:
        annotations["external_values"] = bool(src["external_values"])
    # Bibliography reverse-index: any biblio entry whose `informs:` lists this
    # vocabulary id contributes a per-element annotation.
    biblio_refs = ctx.bibliography_refs.get(("vocabulary", src.get("id") or sf.path.stem), [])
    if biblio_refs:
        annotations["bibliography_refs"] = json.dumps(
            sorted(set(biblio_refs)), sort_keys=True, ensure_ascii=False
        )

    if annotations:
        enum["annotations"] = annotations

    # System mappings -> exact_mappings on permissible values + populate external enums
    sm = src.get("system_mappings")
    if isinstance(sm, dict):
        process_enum_system_mappings(enum_name, pvs, sm, ctx)

    # Surface unmapped fields
    extras = set(src.keys()) - KNOWN_VOCAB_FIELDS
    for x in sorted(extras):
        ctx.unmapped.append(f"vocabulary:{sf.path.name}:{x}")

    return enum_name, enum


def process_enum_system_mappings(
    publicschema_enum_name: str,
    permissible_values: dict[str, dict],
    sm: dict,
    ctx: MigrationContext,
) -> None:
    """Populate exact_mappings on each permissible value pointing at external schema's meaning URIs.

    Also accumulates external enum definitions in ctx.external_enums for emission.
    """
    for system_id, entry in sm.items():
        if not isinstance(entry, dict):
            continue
        if system_id not in ctx.systems.systems:
            ctx.unmapped.append(f"system_mappings: unknown system '{system_id}'")
            continue
        sys_info = ctx.systems.systems[system_id]
        sys_prefix = sys_info["prefix"]
        # Derive external enum name
        vocab_name = entry.get("vocabulary_name") or publicschema_enum_name
        ext_enum = pascal_case(vocab_name) or publicschema_enum_name
        # Prefix with system to avoid cross-system collisions, except where the
        # vocab name already starts with the system token.
        if not ext_enum.lower().startswith(sys_prefix.replace("-", "").lower()):
            ext_enum = pascal_case(sys_prefix) + ext_enum
        # Track external values
        for vmap in entry.get("values") or []:
            if not isinstance(vmap, dict):
                continue
            src_code = vmap.get("code")
            tgt_code = vmap.get("maps_to")
            if src_code is None or tgt_code is None:
                continue
            src_key = value_key(src_code)
            tgt_key = value_key(tgt_code)
            ext_meaning_curie = f"{sys_prefix}:{ext_enum}/{tgt_key}"
            # Record in external_enums for emission
            if tgt_key not in ctx.external_enums[system_id][ext_enum]:
                ext_pv: dict[str, Any] = {
                    "meaning": ext_meaning_curie,
                }
                lbl = vmap.get("label")
                if isinstance(lbl, str):
                    ext_pv["title"] = lbl
                elif isinstance(lbl, dict) and lbl.get("en"):
                    ext_pv["title"] = lbl["en"]
                ctx.external_enums[system_id][ext_enum][tgt_key] = ext_pv
            # Add exact_mappings on the PublicSchema permissible value
            if src_key in permissible_values:
                pv = permissible_values[src_key]
                pv.setdefault("exact_mappings", []).append(ext_meaning_curie)
                ctx.crosswalk_refs.append(
                    (ext_meaning_curie, f"{publicschema_enum_name}/{src_key}")
                )
                # Crosswalk-level note / unmapped_reason / migration_note end up
                # as per-value annotations on the PublicSchema PV (keyed by system).
                pv_annotations = pv.setdefault("annotations", {})
                for fname in ("note", "unmapped_reason", "migration_note"):
                    fval = vmap.get(fname)
                    if fval is not None:
                        pv_annotations[f"{fname}__{system_id}"] = str(fval).strip()
            # Surface unknown system-mapping value fields
            for fname in vmap.keys():
                if fname not in SYSTEM_MAPPING_VALUE_KNOWN_FIELDS:
                    ctx.unmapped.append(
                        f"system_mappings.{system_id}.values[].{fname} (enum {publicschema_enum_name})"
                    )


# ============================================================================
# Conversion: property -> SlotDefinition
# ============================================================================


# PublicSchema 'type' -> LinkML 'range' (primitive).
PRIMITIVE_TYPE_MAP = {
    "string": "string",
    "text": "string",
    "boolean": "boolean",
    "integer": "integer",
    "number": "float",
    "float": "float",
    "decimal": "decimal",
    "date": "date",
    "datetime": "datetime",
    "uri": "uri",
    "object": "string",  # complex objects collapse to string here; deferred
    # PublicSchema's `geojson_geometry` is a structured GeoJSON Geometry object
    # (RFC 7946). LinkML has no native geo type, so it's represented as a
    # serialised string with an explicit format annotation on the slot.
    "geojson_geometry": "string",
}


def convert_property(sf: SourceFile, ctx: MigrationContext) -> tuple[str, dict]:
    src = sf.data
    slot_name = src.get("id") or sf.path.stem
    en_label, label_other = get_multilingual(src, "label")
    en_def, def_other = get_multilingual(src, "definition")

    slot: dict[str, Any] = {
        "slot_uri": f"publicschema:{slot_name}",
    }
    if en_label:
        slot["title"] = en_label
    if en_def:
        slot["description"] = en_def

    # Range
    ptype = src.get("type")
    refs = src.get("references")
    vocab = src.get("vocabulary")
    if isinstance(refs, str) and refs in ctx.concepts:
        slot["range"] = refs  # Class-valued
    elif isinstance(vocab, str) and vocab in ctx.vocabularies:
        slot["range"] = pascal_case(vocab)  # Enum-valued
    elif isinstance(ptype, str) and ptype.startswith("concept:"):
        # ptype like 'concept:Person' or 'concept:crvs/Person'
        # Extract the class name (last path segment).
        class_ref = ptype[len("concept:"):].rsplit("/", 1)[-1]
        slot["range"] = class_ref
    elif isinstance(ptype, str) and ptype in PRIMITIVE_TYPE_MAP:
        slot["range"] = PRIMITIVE_TYPE_MAP[ptype]
    elif isinstance(ptype, str):
        slot["range"] = "string"  # unknown primitive -> string
        ctx.unmapped.append(f"property:{slot_name}:type={ptype}")

    # Cardinality
    card = src.get("cardinality")
    if card == "multiple":
        slot["multivalued"] = True
    elif card == "single":
        slot["multivalued"] = False

    # Status
    maturity = src.get("maturity")
    if maturity and maturity in STATUS_MAP:
        slot["status"] = STATUS_MAP[maturity]

    # External equivalents + schema_org_equivalent + alignments
    exact, close, alignments = map_external_equivalents(src.get("external_equivalents"), ctx)
    soe = src.get("schema_org_equivalent")
    if isinstance(soe, str) and soe:
        exact.append(soe)
    for rec in get_alignments_for("property", slot_name, ctx):
        curie = uri_to_curie(rec["uri"], ctx) or rec["uri"]
        if rec.get("match") in ("close", "broad", "narrow", "related"):
            close.append(curie)
        else:
            exact.append(curie)
        alignments.append(rec)
    if exact:
        slot["exact_mappings"] = sorted(set(exact))
    if close:
        slot["close_mappings"] = sorted(set(close))

    # Annotations
    annotations: dict[str, Any] = i18n_annotations(label_other, def_other)
    for scalar_key in ("category", "sensitivity", "domain_override", "vc_guidance",
                       "immutable_after_status"):
        if src.get(scalar_key) is not None and isinstance(src.get(scalar_key), (str, int, bool, float)):
            annotations[scalar_key] = src[scalar_key]
    for jk, jv in filter(
        None,
        [
            json_annotation("external_alignments", alignments or None),
            json_annotation("convergence", src.get("convergence")),
            json_annotation("system_mappings", src.get("system_mappings")),
            json_annotation("valid_instruments", src.get("valid_instruments")),
            json_annotation("age_applicability", src.get("age_applicability")),
            json_annotation("see_also", src.get("see_also")),
            json_annotation("tags", src.get("tags")),
        ],
    ):
        annotations[jk] = jv

    # Bibliography reverse-index
    biblio_refs = ctx.bibliography_refs.get(("property", slot_name), [])
    if biblio_refs:
        annotations["bibliography_refs"] = json.dumps(
            sorted(set(biblio_refs)), sort_keys=True, ensure_ascii=False
        )

    if annotations:
        slot["annotations"] = annotations

    extras = set(src.keys()) - KNOWN_PROPERTY_FIELDS
    for x in sorted(extras):
        ctx.unmapped.append(f"property:{slot_name}:{x}")

    return slot_name, slot


# ============================================================================
# Conversion: concept -> ClassDefinition
# ============================================================================


def convert_concept(sf: SourceFile, ctx: MigrationContext) -> tuple[str, dict]:
    src = sf.data
    cls_name = src.get("id") or pascal_case(sf.path.stem)
    en_label, label_other = get_multilingual(src, "label")
    en_def, def_other = get_multilingual(src, "definition")

    cls: dict[str, Any] = {
        "class_uri": f"publicschema:{cls_name}",
    }
    if en_label:
        cls["title"] = en_label
    if en_def:
        cls["description"] = en_def

    # Supertypes -> is_a + mixins (strip any path/domain prefix like "crvs/VitalEvent").
    def _strip_path(name: str) -> str:
        return name.rsplit("/", 1)[-1] if isinstance(name, str) else name

    supers = src.get("supertypes") or []
    supers = [_strip_path(s) for s in supers if isinstance(s, str)]
    if supers:
        cls["is_a"] = supers[0]
        if len(supers) > 1:
            cls["mixins"] = list(supers[1:])
        ctx.inheritance_choices[cls_name] = {
            "is_a": supers[0],
            "mixins": list(supers[1:]),
            "rule": "first declared supertype = is_a; rest = mixins (path prefix stripped)",
        }

    # Slots (PublicSchema concept lists its properties by name)
    props = src.get("properties")
    if isinstance(props, list) and props:
        cls["slots"] = [p for p in props if isinstance(p, str)]

    # Status
    maturity = src.get("maturity")
    if maturity and maturity in STATUS_MAP:
        cls["status"] = STATUS_MAP[maturity]

    # External equivalents (from external_equivalents: on the source) + alignments
    # (from schema/alignments/<vocab>.yaml). The two sources are merged.
    exact, close, alignments = map_external_equivalents(src.get("external_equivalents"), ctx)
    for rec in get_alignments_for("concept", cls_name, ctx):
        curie = uri_to_curie(rec["uri"], ctx) or rec["uri"]
        if rec.get("match") in ("close", "broad", "narrow", "related"):
            close.append(curie)
        else:
            exact.append(curie)
        alignments.append(rec)
    if exact:
        cls["exact_mappings"] = sorted(set(exact))
    if close:
        cls["close_mappings"] = sorted(set(close))

    # Annotations
    annotations: dict[str, Any] = i18n_annotations(label_other, def_other)
    if src.get("featured"):
        annotations["featured"] = bool(src["featured"])
    if src.get("domain"):
        # Carry source-declared domain as an annotation for traceability.
        annotations["source_domain"] = str(src["domain"])
    for jk, jv in filter(
        None,
        [
            json_annotation("external_alignments", alignments or None),
            json_annotation("convergence", src.get("convergence")),
            json_annotation("property_groups", src.get("property_groups")),
            json_annotation("see_also", src.get("see_also")),
            json_annotation("tags", src.get("tags")),
            json_annotation("vc_guidance", src.get("vc_guidance")),
        ],
    ):
        annotations[jk] = jv

    # Bibliography reverse-index
    biblio_refs = ctx.bibliography_refs.get(("concept", cls_name), [])
    if biblio_refs:
        annotations["bibliography_refs"] = json.dumps(
            sorted(set(biblio_refs)), sort_keys=True, ensure_ascii=False
        )

    if annotations:
        cls["annotations"] = annotations

    # Abstract: prefer source `abstract:` field; fallback to known abstract supertypes.
    if src.get("abstract") is True or cls_name in {"Agent", "Party", "Thing"}:
        cls["abstract"] = True

    extras = set(src.keys()) - KNOWN_CONCEPT_FIELDS
    for x in sorted(extras):
        ctx.unmapped.append(f"concept:{cls_name}:{x}")

    return cls_name, cls


# ============================================================================
# Domain split (Phase 1)
# ============================================================================


def assign_concept_domain(name: str, sf: SourceFile, ctx: MigrationContext) -> str:
    # 1. Source-declared `domain:` is authoritative.
    src_domain = sf.data.get("domain")
    if isinstance(src_domain, str) and src_domain in SOURCE_DOMAIN_MAP:
        d = SOURCE_DOMAIN_MAP[src_domain]
        ctx.domain_rationale[f"concept:{name}"] = f"source `domain: {src_domain}` -> {d}"
        return d
    # 2. Hand-curated concept domain map.
    if name in CONCEPT_DOMAINS:
        ctx.domain_rationale[f"concept:{name}"] = f"explicit map -> {CONCEPT_DOMAINS[name]}"
        return CONCEPT_DOMAINS[name]
    # 3. Property_groups categories.
    cats = []
    pg = sf.data.get("property_groups")
    if isinstance(pg, list):
        cats = [g.get("category") for g in pg if isinstance(g, dict)]
    if "identity" in cats:
        ctx.domain_rationale[f"concept:{name}"] = "property_groups.identity -> identity"
        return "identity"
    if "demographics" in cats:
        ctx.domain_rationale[f"concept:{name}"] = "property_groups.demographics -> identity"
        return "identity"
    ctx.domain_rationale[f"concept:{name}"] = "fallback -> misc"
    return "misc"


def assign_property_domain(prop_name: str, ctx: MigrationContext) -> str:
    # Find which concepts list this property
    using = [c for c, sf in ctx.concepts.items()
             if prop_name in (sf.data.get("properties") or [])]
    if not using:
        ctx.domain_rationale[f"property:{prop_name}"] = "no concept uses it -> misc"
        return "misc"
    domains = collections.Counter(ctx.concept_domain.get(c, "misc") for c in using)
    if len(domains) == 1:
        d, _ = domains.most_common(1)[0]
        ctx.domain_rationale[f"property:{prop_name}"] = (
            f"single-domain use -> {d} (used by {len(using)} concepts)"
        )
        return d
    # Multi-domain property
    d, _ = domains.most_common(1)[0]
    if sum(domains.values()) - domains[d] >= 1 and d != "core":
        # Promote shared properties to a 'common' domain
        ctx.domain_rationale[f"property:{prop_name}"] = (
            f"used across domains {dict(domains)} -> common"
        )
        return "common"
    ctx.domain_rationale[f"property:{prop_name}"] = (
        f"multi-domain, majority -> {d} ({dict(domains)})"
    )
    return d


def assign_vocab_domain(vocab_name: str, ctx: MigrationContext) -> str:
    # Vocabularies referenced via a property's `vocabulary:` field
    refs = []
    for prop_id, sf in ctx.properties.items():
        if sf.data.get("vocabulary") == vocab_name or sf.data.get("vocabulary") == sf.path.stem:
            refs.append(prop_id)
    if not refs:
        ctx.domain_rationale[f"vocabulary:{vocab_name}"] = "unreferenced -> vocabularies"
        return DOMAIN_VOCABULARIES
    domains = collections.Counter(ctx.property_domain.get(p, "misc") for p in refs)
    if len(domains) == 1:
        d, _ = domains.most_common(1)[0]
        ctx.domain_rationale[f"vocabulary:{vocab_name}"] = f"single-domain use -> {d}"
        return d
    ctx.domain_rationale[f"vocabulary:{vocab_name}"] = (
        f"multi-domain ({dict(domains)}) -> vocabularies"
    )
    return DOMAIN_VOCABULARIES


def derive_domains(ctx: MigrationContext) -> None:
    for c, sf in ctx.concepts.items():
        ctx.concept_domain[c] = assign_concept_domain(c, sf, ctx)
    for p, sf in ctx.properties.items():
        ctx.property_domain[p] = assign_property_domain(p, ctx)
    for v, sf in ctx.vocabularies.items():
        ctx.vocab_domain[v] = assign_vocab_domain(v, ctx)


# ============================================================================
# Reporting
# ============================================================================


def write_inventory_report(ctx: MigrationContext) -> None:
    lines = ["# Inventory (Phase 0)", ""]
    kinds = (
        "concept", "property", "vocabulary", "credential", "bibliography",
        "categories", "external_reference", "external_terms", "alignment", "base",
        "project", "meta", "other",
    )
    for kind in kinds:
        files = ctx.by_kind.get(kind, [])
        lines.append(f"## {kind} ({len(files)})")
        lines.append("")
        for sf in sorted(files, key=lambda s: s.path):
            lines.append(f"- `{sf.path.relative_to(ROOT)}` (id: `{sf.id or '—'}`)")
        lines.append("")
    # SEMIC alignment summary
    if ctx.external_references or ctx.alignments_by_subject:
        lines.append("## SEMIC alignment architecture (P4 series on main)")
        lines.append("")
        lines.append(f"- {len(ctx.external_references)} external_reference vocabulary(ies).")
        n_alignments = sum(len(v) for v in ctx.alignments_by_subject.values())
        lines.append(f"- {n_alignments} alignment(s) authored against PublicSchema concepts/properties.")
        lines.append(f"- {len(ctx.external_terms_by_source)} external_terms file(s).")
        lines.append(f"- {len(ctx.bases)} base declaration(s).")
        lines.append("")
        lines.append("These flow into emitted dist/linkml/external/<sysid>.yaml files alongside")
        lines.append("the system_mappings-derived partial schemas; alignment records merge with")
        lines.append("external_equivalents on the corresponding concept/property.")
        lines.append("")
    (OUTPUT_DIR / "_inventory.md").write_text("\n".join(lines))


def write_domain_split_report(ctx: MigrationContext) -> None:
    lines = ["# Domain split (Phase 1)", "", "Auto-derived from property_groups and concept names."]
    lines.append("")
    for label, dmap in (
        ("Concepts", ctx.concept_domain),
        ("Properties", ctx.property_domain),
        ("Vocabularies", ctx.vocab_domain),
    ):
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| Name | Domain | Rationale |")
        lines.append("|---|---|---|")
        for name in sorted(dmap):
            kind_prefix = label.lower().rstrip("s")
            rk = f"{kind_prefix}:{name}"
            rat = ctx.domain_rationale.get(rk, "—")
            lines.append(f"| {name} | {dmap[name]} | {rat} |")
        lines.append("")
    (OUTPUT_DIR / "_domain_split.md").write_text("\n".join(lines))


def write_migration_report(
    ctx: MigrationContext, lint_failures: list[str], integrity_failures: list[str]
) -> None:
    lines = ["# Migration report (Phase 5)", ""]
    n_classes = len(ctx.concepts)
    n_slots = len(ctx.properties)
    n_enums = len(ctx.vocabularies)
    n_external_enums = sum(len(es) for es in ctx.external_enums.values())
    lines += [
        f"- PublicSchema: {n_classes} classes, {n_slots} slots, {n_enums} enums.",
        f"- External systems: {len(ctx.external_enums)} active, {n_external_enums} enums emitted.",
        f"- Crosswalk references: {len(ctx.crosswalk_refs)}.",
        f"- Unmapped source fields: {len(ctx.unmapped)}.",
        f"- linkml-lint failures: {len(lint_failures)}.",
        f"- Referential integrity failures: {len(integrity_failures)}.",
        "",
    ]
    if ctx.unmapped:
        lines.append("## Unmapped source fields")
        lines.append("")
        for u in sorted(set(ctx.unmapped)):
            lines.append(f"- `{u}`")
        lines.append("")
    if ctx.inheritance_choices:
        lines.append("## is_a / mixins choices")
        lines.append("")
        lines.append("| Concept | is_a | mixins | rule |")
        lines.append("|---|---|---|---|")
        for c, ch in sorted(ctx.inheritance_choices.items()):
            mix = ", ".join(ch.get("mixins") or []) or "—"
            lines.append(f"| {c} | {ch.get('is_a')} | {mix} | {ch.get('rule')} |")
        lines.append("")
    lines.append("## Prefixes")
    lines.append("")
    lines.append("| Prefix | URI | Source |")
    lines.append("|---|---|---|")
    for sid, info in sorted(ctx.systems.systems.items()):
        lines.append(f"| {info.get('prefix', sid)} | {info.get('uri', '')} | {info.get('source', '?')} |")
    for sid, info in sorted(ctx.systems.vocab_prefixes.items()):
        lines.append(f"| {sid} | {info.get('uri', '')} | {info.get('source', '?')} |")
    lines.append("")
    if lint_failures:
        lines.append("## linkml-lint failures")
        lines.append("")
        for f in lint_failures:
            lines.append(f"- {f}")
        lines.append("")
    if integrity_failures:
        lines.append("## Referential integrity failures")
        lines.append("")
        for f in integrity_failures:
            lines.append(f"- {f}")
        lines.append("")
    (OUTPUT_DIR / "_migration_report.md").write_text("\n".join(lines))


# ============================================================================
# Emission
# ============================================================================


def yaml_dump(d: Any) -> str:
    return yaml.safe_dump(
        d, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100
    )


PUBLICSCHEMA_PREFIXES = {
    "publicschema": PUBLICSCHEMA_BASE,
    "linkml": "https://w3id.org/linkml/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "bibo": "http://purl.org/ontology/bibo/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}


def build_prefixes(ctx: MigrationContext) -> dict[str, str]:
    """Build the prefixes dict, deduping by URI (LinkML / curies cannot handle multiple
    prefixes mapping to the same namespace URI).

    Sources, in priority order:
      1. Hard-coded PUBLICSCHEMA_PREFIXES (publicschema/linkml/xsd/bibo/skos)
      2. build/external_system_prefixes.yaml vocab_prefixes (schema/foaf/cpov/dpv/...)
      3. build/external_system_prefixes.yaml systems (dhs/dhis2/openspp/...)
      4. schema/external_references/<vocab>.yaml `prefixes:` (SEMIC P4 architecture
         — adms/cv/dct/foaf/locn/person/... from the actual upstream vocabularies)

    On URI collision, the earlier entry wins. SEMIC reference prefixes are
    additive (they introduce new prefix tokens like `person:` that weren't in
    our hand-curated table).
    """
    prefixes = dict(PUBLICSCHEMA_PREFIXES)
    seen_uris = {v: k for k, v in prefixes.items()}
    for sid, info in ctx.systems.vocab_prefixes.items():
        uri = info["uri"]
        if uri in seen_uris:
            continue
        prefixes[sid] = uri
        seen_uris[uri] = sid
    for sid, info in ctx.systems.systems.items():
        uri = info["uri"]
        prefix = info["prefix"]
        if uri in seen_uris:
            continue
        prefixes[prefix] = uri
        seen_uris[uri] = prefix
    # SEMIC external_references publish the actual upstream prefix tables.
    for ref_id, ref_doc in ctx.external_references.items():
        for ref_prefix, ref_uri in (ref_doc.get("prefixes") or {}).items():
            if not isinstance(ref_uri, str):
                continue
            if ref_uri in seen_uris:
                continue
            if ref_prefix in prefixes:
                continue
            prefixes[ref_prefix] = ref_uri
            seen_uris[ref_uri] = ref_prefix
    return prefixes


def alignment_to_record(alignment_entry: dict, ctx: MigrationContext) -> dict | None:
    """Convert one entry from schema/alignments/<vocab>.yaml.alignments[] into
    an ExternalAlignment-shaped record (matching the extension metamodel).
    Returns None if the entry doesn't have enough data to form a record."""
    a = alignment_entry["alignment"]
    aset = alignment_entry["set"]
    obj = a.get("object") or {}
    uri = obj.get("iri")
    if not uri:
        return None
    standard = aset.get("standard") or {}
    rec: dict[str, Any] = {
        "vocabulary": aset.get("label") or standard.get("source_id") or aset.get("id"),
        "uri": uri,
        "match": a.get("quality") or "exact",
    }
    term_id = obj.get("term_id")
    if term_id:
        rec["label"] = term_id.split(".", 1)[-1]  # last path segment
    rationale = a.get("rationale")
    if rationale:
        rec["note"] = rationale
    rec["source_id"] = aset.get("source_id")
    rec["source_version"] = aset.get("source_version")
    rec["predicate"] = a.get("predicate")
    rec["confidence"] = a.get("confidence")
    rec["review_status"] = a.get("review_status")
    return {k: v for k, v in rec.items() if v is not None}


def get_alignments_for(kind: str, name: str, ctx: MigrationContext) -> list[dict]:
    """Look up alignments for a PublicSchema element. Subject keys in
    schema/alignments/*.yaml use kind=concept|property and id=PublicSchema id."""
    entries = ctx.alignments_by_subject.get((kind, name), [])
    records = []
    for entry in entries:
        rec = alignment_to_record(entry, ctx)
        if rec:
            records.append(rec)
    return records


def schema_header(domain: str, ctx: MigrationContext, *, extra_imports: list[str] | None = None) -> dict:
    imports = ["linkml:types", "publicschema-extensions"]
    if extra_imports:
        imports.extend(extra_imports)
    return {
        "id": f"{PUBLICSCHEMA_BASE}linkml/{domain}",
        "name": f"publicschema-{domain}",
        "title": f"PublicSchema {domain.replace('_', ' ')} domain",
        "license": "CC-BY-4.0",
        "default_prefix": "publicschema",
        "prefixes": build_prefixes(ctx),
        "imports": imports,
    }


def convert_credential(sf: SourceFile, ctx: MigrationContext) -> tuple[str, dict]:
    """A credential is a thin W3C VC descriptor: subject_concept + included_concepts
    plus the same multilingual label/definition + maturity that concepts have."""
    src = sf.data
    cls_name = src.get("id") or pascal_case(sf.path.stem)
    en_label, label_other = get_multilingual(src, "label")
    en_def, def_other = get_multilingual(src, "definition")

    cls: dict[str, Any] = {
        "class_uri": f"publicschema:{cls_name}",
        "is_a": "Credential",
    }
    if en_label:
        cls["title"] = en_label
    if en_def:
        cls["description"] = en_def

    maturity = src.get("maturity")
    if maturity and maturity in STATUS_MAP:
        cls["status"] = STATUS_MAP[maturity]

    annotations: dict[str, Any] = i18n_annotations(label_other, def_other)
    if src.get("subject_concept"):
        annotations["subject_concept"] = str(src["subject_concept"])
    inc = src.get("included_concepts")
    if isinstance(inc, list) and inc:
        ann = json_annotation("included_concepts", inc)
        if ann:
            annotations[ann[0]] = ann[1]
    for jk, jv in filter(
        None,
        [
            json_annotation("see_also", src.get("see_also")),
            json_annotation("tags", src.get("tags")),
        ],
    ):
        annotations[jk] = jv

    biblio_refs = ctx.bibliography_refs.get(("credential", cls_name), [])
    if biblio_refs:
        annotations["bibliography_refs"] = json.dumps(
            sorted(set(biblio_refs)), sort_keys=True, ensure_ascii=False
        )

    if annotations:
        cls["annotations"] = annotations

    extras = set(src.keys()) - KNOWN_CREDENTIAL_FIELDS
    for x in sorted(extras):
        ctx.unmapped.append(f"credential:{cls_name}:{x}")

    return cls_name, cls


def emit_credentials_file(ctx: MigrationContext) -> set[str]:
    """Emit dist/linkml/credentials.yaml with one class per credential file plus
    a synthetic abstract Credential marker. Returns the set of cross-domain
    concept ids referenced (for the composite imports)."""
    credential_files = ctx.by_kind.get("credential", [])
    if not credential_files:
        return set()

    classes: dict[str, dict] = {
        "Credential": {
            "class_uri": "publicschema:Credential",
            "title": "Credential",
            "description": (
                "Abstract supertype for PublicSchema verifiable credential "
                "descriptors. Each subclass declares a subject_concept and an "
                "optional list of included_concepts via annotations."
            ),
            "abstract": True,
            "status": "bibo:draft",
        }
    }
    referenced_concepts: set[str] = set()
    for sf in credential_files:
        name, cls = convert_credential(sf, ctx)
        classes[name] = cls
        subj = sf.data.get("subject_concept")
        if isinstance(subj, str):
            referenced_concepts.add(subj)
        for c in sf.data.get("included_concepts") or []:
            if isinstance(c, str):
                referenced_concepts.add(c)

    cross_domain_imports = {
        ctx.concept_domain[c] for c in referenced_concepts if c in ctx.concept_domain
    }
    header = schema_header("credentials", ctx, extra_imports=sorted(cross_domain_imports))
    out = dict(header)
    out["classes"] = classes
    (OUTPUT_DIR / "credentials.yaml").write_text(yaml_dump(out))
    return referenced_concepts


def emit_bibliography_file(ctx: MigrationContext) -> None:
    """Emit dist/linkml/bibliography.yaml: one Citation instance class plus one
    permissible-value-style record per source. Each citation is a class
    instance, not a permissible value (rich structure), so we emit one
    Citation subclass per source for typed access."""
    biblio_files = ctx.by_kind.get("bibliography", [])
    if not biblio_files:
        return

    # The Citation class — abstract marker only. We previously declared typed
    # `attributes:` here but that broke gen-shacl's slot-uri lookup for slots
    # inherited by every citation subclass. All citation data lives as
    # annotations on each subclass instead, which round-trips cleanly through
    # all four stock LinkML generators.
    citation_cls = {
        "class_uri": "publicschema:Citation",
        "title": "Citation",
        "description": (
            "Abstract supertype for bibliographic references cited by "
            "PublicSchema. Each subclass carries the citation record fields "
            "(title, publisher, year, uri, access, status, ...) as annotations "
            "for downstream JSON-loadable consumption."
        ),
        "abstract": True,
    }

    citations_classes: dict[str, dict] = {"Citation": citation_cls}
    for sf in sorted(biblio_files, key=lambda s: s.path):
        biblio_id = sf.id
        if not biblio_id:
            continue
        src = sf.data
        # Use the file id as the class name (PascalCased + Citation suffix).
        local = pascal_case(biblio_id) + "Citation"
        cls: dict[str, Any] = {
            "class_uri": f"publicschema:Citation/{biblio_id}",
            "is_a": "Citation",
            "title": src.get("title") or biblio_id,
        }
        annotations: dict[str, Any] = {"citation_id": biblio_id}
        for fname in (
            "title", "short_title", "publisher", "year",
            "type", "domain", "uri", "access", "status",
            "standard_number", "version", "note",
        ):
            if src.get(fname) is not None:
                annotations[fname] = src[fname] if isinstance(src[fname], (int, str)) else str(src[fname])
        if src.get("authors") is not None:
            ann = json_annotation("authors", src["authors"])
            if ann:
                annotations[ann[0]] = ann[1]
        # The informs block is reversed elsewhere; preserve here as JSON for traceability.
        if src.get("informs"):
            ann = json_annotation("informs", src["informs"])
            if ann:
                annotations[ann[0]] = ann[1]
        for fname in src.keys():
            if fname not in KNOWN_BIBLIOGRAPHY_FIELDS:
                ctx.unmapped.append(f"bibliography:{biblio_id}:{fname}")
        cls["annotations"] = annotations
        citations_classes[local] = cls

    header = schema_header("bibliography", ctx)
    out = dict(header)
    out["classes"] = citations_classes
    (OUTPUT_DIR / "bibliography.yaml").write_text(yaml_dump(out))


def emit_categories_file(ctx: MigrationContext) -> None:
    """Emit dist/linkml/categories.yaml as a flat Enum (PropertyCategory) whose
    permissible values mirror schema/categories.yaml. Multilingual labels are
    preserved as per-value annotations (label_<lang>)."""
    if not ctx.categories:
        return
    permissible_values: dict[str, dict] = {}
    for cat_key in sorted(ctx.categories):
        meta = ctx.categories[cat_key]
        if not isinstance(meta, dict):
            continue
        label = meta.get("label") or {}
        en = label.get("en") if isinstance(label, dict) else None
        pv: dict[str, Any] = {"meaning": f"publicschema:Category/{cat_key}"}
        if en:
            pv["title"] = en
        v_annotations: dict[str, Any] = {}
        if isinstance(label, dict):
            for lang, text in sorted(label.items()):
                if lang != "en" and isinstance(text, str):
                    v_annotations[f"label_{lang}"] = text
        # Per-value definition if present.
        defn = meta.get("definition") or meta.get("description")
        if isinstance(defn, dict):
            d_en = defn.get("en")
            if d_en:
                pv["description"] = d_en
            for lang, text in sorted(defn.items()):
                if lang != "en" and isinstance(text, str):
                    v_annotations[f"description_{lang}"] = text
        elif isinstance(defn, str):
            pv["description"] = defn
        for fname in meta.keys():
            if fname not in KNOWN_CATEGORY_VALUE_FIELDS:
                ctx.unmapped.append(f"categories:{cat_key}:{fname}")
        if v_annotations:
            pv["annotations"] = v_annotations
        permissible_values[cat_key] = pv

    enum: dict[str, Any] = {
        "enum_uri": "publicschema:PropertyCategory",
        "title": "Property category",
        "description": (
            "UI taxonomy referenced by property_groups[].category on concept "
            "files. Sourced from schema/categories.yaml."
        ),
        "permissible_values": permissible_values,
    }
    header = schema_header("categories", ctx)
    out = dict(header)
    out["enums"] = {"PropertyCategory": enum}
    (OUTPUT_DIR / "categories.yaml").write_text(yaml_dump(out))


def emit_domain_file(domain: str, ctx: MigrationContext) -> None:
    classes: dict[str, dict] = {}
    slots: dict[str, dict] = {}
    enums: dict[str, dict] = {}
    used_external_systems: set[str] = set()
    cross_domain_imports: set[str] = set()

    referenced_slots: set[str] = set()
    referenced_classes: set[str] = set()
    referenced_enums: set[str] = set()

    for cid, ddom in ctx.concept_domain.items():
        if ddom != domain:
            continue
        sf = ctx.concepts[cid]
        name, cls = convert_concept(sf, ctx)
        classes[name] = cls
        for s in cls.get("slots", []) or []:
            referenced_slots.add(s)
        for sup in [cls.get("is_a")] + (cls.get("mixins") or []):
            if sup:
                referenced_classes.add(sup)

    for pid, ddom in ctx.property_domain.items():
        if ddom != domain:
            continue
        sf = ctx.properties[pid]
        name, slot = convert_property(sf, ctx)
        slots[name] = slot
        # Track class/enum range references for cross-domain imports
        rng = slot.get("range")
        if isinstance(rng, str):
            if rng in ctx.concept_domain:
                referenced_classes.add(rng)
            # Enum names are PascalCase from vocab ids
            elif rng[0].isupper() and rng not in PRIMITIVE_TYPE_MAP.values():
                referenced_enums.add(rng)
        # Track external systems and populate ctx.external_enums so external
        # schema files are emitted (even when the property has no PublicSchema enum).
        sm = sf.data.get("system_mappings")
        if isinstance(sm, dict):
            for sysid, entry in sm.items():
                if sysid not in ctx.systems.systems:
                    continue
                used_external_systems.add(sysid)
                if not isinstance(entry, dict):
                    continue
                sys_prefix = ctx.systems.systems[sysid]["prefix"]
                vocab_name = entry.get("vocabulary_name") or name
                ext_enum = pascal_case(vocab_name) or pascal_case(name)
                if not ext_enum.lower().startswith(sys_prefix.replace("-", "").lower()):
                    ext_enum = pascal_case(sys_prefix) + ext_enum
                for vmap in entry.get("values") or []:
                    if not isinstance(vmap, dict):
                        continue
                    tgt_code = vmap.get("maps_to")
                    if tgt_code is None:
                        continue
                    tgt_key = value_key(tgt_code)
                    if tgt_key in ctx.external_enums[sysid][ext_enum]:
                        continue
                    ext_pv: dict[str, Any] = {
                        "meaning": f"{sys_prefix}:{ext_enum}/{tgt_key}",
                    }
                    lbl = vmap.get("label")
                    if isinstance(lbl, str):
                        ext_pv["title"] = lbl
                    elif isinstance(lbl, dict) and lbl.get("en"):
                        ext_pv["title"] = lbl["en"]
                    ctx.external_enums[sysid][ext_enum][tgt_key] = ext_pv
                    # Surface unknown system-mapping value fields
                    for fname in vmap.keys():
                        if fname not in SYSTEM_MAPPING_VALUE_KNOWN_FIELDS:
                            ctx.unmapped.append(
                                f"property:{pid}:system_mappings.{sysid}.values[].{fname}"
                            )

    for vid, ddom in ctx.vocab_domain.items():
        if ddom != domain:
            continue
        sf = ctx.vocabularies[vid]
        name, enum = convert_vocabulary(sf, ctx)
        enums[name] = enum
        sm = sf.data.get("system_mappings")
        if isinstance(sm, dict):
            for sysid in sm:
                if sysid in ctx.systems.systems:
                    used_external_systems.add(sysid)

    if not (classes or slots or enums):
        return

    # Resolve cross-domain imports: slot used here but defined in another domain.
    for s in referenced_slots:
        d = ctx.property_domain.get(s)
        if d and d != domain:
            cross_domain_imports.add(d)
    for c in referenced_classes:
        d = ctx.concept_domain.get(c)
        if d and d != domain:
            cross_domain_imports.add(d)
    # Enums: vocab_domain is keyed by source id (e.g. "country"), not PascalCase. Reverse-lookup.
    enum_to_domain: dict[str, str] = {}
    for vid in ctx.vocabularies:
        enum_to_domain[pascal_case(vid)] = ctx.vocab_domain.get(vid, DOMAIN_VOCABULARIES)
    for e in referenced_enums:
        d = enum_to_domain.get(e)
        if d and d != domain:
            cross_domain_imports.add(d)

    # Only import an external/<sid> if that file will actually be emitted
    # (i.e. ctx.external_enums[sid] has content).
    emittable_externals = [
        sid for sid in sorted(used_external_systems) if ctx.external_enums.get(sid)
    ]
    extra_imports = sorted(cross_domain_imports) + [
        f"external/{sid}" for sid in emittable_externals
    ]
    header = schema_header(domain, ctx, extra_imports=extra_imports)
    out = dict(header)
    if classes:
        out["classes"] = classes
    if slots:
        out["slots"] = slots
    if enums:
        out["enums"] = enums

    (OUTPUT_DIR / f"{domain}.yaml").write_text(yaml_dump(out))


def emit_external_schemas(ctx: MigrationContext) -> None:
    """Emit dist/linkml/external/<sysid>.yaml partial schemas.

    Two sources, merged on the same output file:
      (a) ctx.external_enums (collected from schema/**/system_mappings:)
          produces enum permissible values with explicit meaning: URIs.
      (b) ctx.external_terms_by_source (from schema/external_terms/*.yaml)
          produces classes and slots for the canonical terms in the upstream
          vocabulary, with provenance and license metadata from
          schema/external_references/*.yaml.
    """
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    all_sysids = set(ctx.external_enums.keys()) | set(ctx.external_terms_by_source.keys())
    for sysid in sorted(all_sysids):
        enums = ctx.external_enums.get(sysid, {})
        terms = ctx.external_terms_by_source.get(sysid, [])
        # Find the canonical prefix + URI for this sysid:
        # 1. external_references[sysid] is the new authoritative source (per P4 commits).
        # 2. ctx.systems.systems[sysid] is our hand-curated table.
        ref_doc = ctx.external_references.get(sysid)
        if ref_doc:
            # SEMIC-style external_reference. Use its declared prefixes.
            ref_prefixes = ref_doc.get("prefixes") or {}
            # Choose the prefix whose URI is the most-specific (longest) match
            # for the source_url's namespace; default to the first listed.
            default_prefix = next(iter(ref_prefixes), sysid)
            schema_uri = ref_doc.get("homepage") or f"{PUBLICSCHEMA_BASE}linkml/external/{sysid}"
            schema_prefixes = dict(ref_prefixes)
            schema_prefixes.setdefault("linkml", "https://w3id.org/linkml/")
            schema_prefixes.setdefault("xsd", "http://www.w3.org/2001/XMLSchema#")
            title = ref_doc.get("name") or sysid
            license_id = (ref_doc.get("license") or {}).get("id", "CC-BY-4.0")
            description_extra = (
                f"Generated from schema/external_terms/{sysid}.yaml (source_version: "
                f"{ref_doc.get('version', '?')}). Provenance and license attribution "
                f"are preserved from schema/external_references/{sysid}.yaml."
            )
            # Provenance annotation
            provenance_ann = {
                "version": ref_doc.get("version"),
                "custodian": ref_doc.get("custodian"),
                "kind": ref_doc.get("kind"),
                "license": ref_doc.get("license"),
                "homepage": ref_doc.get("homepage"),
                "reference_url": ref_doc.get("reference_url"),
                "artifacts": ref_doc.get("artifacts"),
            }
        elif sysid in ctx.systems.systems:
            info = ctx.systems.systems[sysid]
            default_prefix = info["prefix"]
            schema_uri = info.get("homepage") or f"{PUBLICSCHEMA_BASE}linkml/external/{sysid}"
            schema_prefixes = {
                info["prefix"]: info["uri"],
                "linkml": "https://w3id.org/linkml/",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            }
            title = info.get("label", sysid)
            license_id = "CC-BY-4.0"
            description_extra = (
                f"Minimal LinkML rendering of {info.get('label', sysid)} enumerations "
                f"referenced by PublicSchema crosswalks. Not authoritative. See "
                f"{info.get('homepage', '')} for the full specification."
            )
            provenance_ann = None
        else:
            # Unknown system. Skip.
            continue

        # Emit enums collected from system_mappings.
        emitted_enums: dict[str, dict] = {}
        for enum_name in sorted(enums):
            pvs_in: dict[str, dict] = enums[enum_name]
            pvs_out: dict[str, dict] = {}
            for vkey in sorted(pvs_in):
                pvs_out[vkey] = pvs_in[vkey]
            emitted_enums[enum_name] = {
                "enum_uri": f"{default_prefix}:{enum_name}" if default_prefix else enum_name,
                "title": enum_name,
                "permissible_values": pvs_out,
            }

        # Emit classes/slots from external_terms.
        # IMPORTANT: name them with the CURIE prefix included to avoid collisions
        # with PublicSchema's own classes (e.g. locn:Address vs publicschema:Address).
        # The class_uri / slot_uri uses the canonical CURIE; the LinkML local name
        # is prefix-qualified.
        emitted_classes: dict[str, dict] = {}
        emitted_slots: dict[str, dict] = {}
        for term in terms:
            if not isinstance(term, dict):
                continue
            curie = term.get("curie") or term.get("id")
            iri = term.get("iri")
            term_type = term.get("term_type")
            if not (curie and iri and term_type):
                continue
            term_prefix = term.get("prefix") or (curie.split(":", 1)[0] if ":" in curie else "")
            local = curie.split(":", 1)[-1] if ":" in curie else curie
            if term_type == "class":
                qualified = pascal_case(term_prefix) + pascal_case(local) if term_prefix else pascal_case(local)
                emitted_classes[qualified] = {
                    "class_uri": curie,
                    "title": local,
                    "description": (
                        f"External class {curie} ({iri}). Sourced from "
                        f"schema/external_terms/{sysid}.yaml (term_id: {term.get('id')})."
                    ),
                }
            elif term_type == "property":
                qualified = f"{slugify(term_prefix)}_{slugify(local)}" if term_prefix else slugify(local)
                emitted_slots[qualified] = {
                    "slot_uri": curie,
                    "title": local,
                    "description": (
                        f"External property {curie} ({iri}). Sourced from "
                        f"schema/external_terms/{sysid}.yaml (term_id: {term.get('id')})."
                    ),
                }

        if not (emitted_enums or emitted_classes or emitted_slots):
            continue

        out: dict[str, Any] = {
            "id": f"{PUBLICSCHEMA_BASE}linkml/external/{sysid}",
            "name": f"publicschema-external-{default_prefix}",
            "title": f"{title} (PublicSchema partial view)",
            "description": description_extra,
            "license": license_id,
            "default_prefix": default_prefix,
            "prefixes": schema_prefixes,
            "imports": ["linkml:types"],
        }
        if emitted_classes:
            out["classes"] = emitted_classes
        if emitted_slots:
            out["slots"] = emitted_slots
        if emitted_enums:
            out["enums"] = emitted_enums
        if provenance_ann:
            out["annotations"] = {
                "external_reference_provenance_json": json.dumps(
                    provenance_ann, sort_keys=True, ensure_ascii=False, default=str
                ),
            }
        (EXTERNAL_DIR / f"{sysid}.yaml").write_text(yaml_dump(out))


def emit_extension_metamodel() -> None:
    shutil.copy(EXTENSIONS_FILE, OUTPUT_DIR / "publicschema-extensions.yaml")


def emit_composite(ctx: MigrationContext, domains: list[str]) -> None:
    prefixes = build_prefixes(ctx)
    # Import every external/<sysid>.yaml that was actually emitted.
    emitted_external_sysids = sorted(
        p.stem for p in EXTERNAL_DIR.glob("*.yaml")
    )
    out = {
        "id": f"{PUBLICSCHEMA_BASE}linkml/publicschema",
        "name": "publicschema",
        "title": "PublicSchema",
        "description": (
            "Top-level composite LinkML schema for PublicSchema. Auto-generated "
            "from schema/**/*.yaml by build/migrate_to_linkml.py. Do not edit by hand."
        ),
        "license": "CC-BY-4.0",
        "version": "0.3.0",
        "default_prefix": "publicschema",
        "default_range": "string",
        "prefixes": prefixes,
        "imports": (
            ["linkml:types", "publicschema-extensions"]
            + sorted(domains)
            + [f"external/{sid}" for sid in emitted_external_sysids]
        ),
    }
    (OUTPUT_DIR / "publicschema.yaml").write_text(yaml_dump(out))


# ============================================================================
# Validation (Phase 5)
# ============================================================================


def run_lint(file: Path) -> tuple[bool, str]:
    cmd = [str(ROOT / ".venv" / "bin" / "linkml-lint"), "--validate", str(file)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # lint exits 1 if there are *any* problems (incl. warnings). Check stderr/stdout for 'error'.
    has_error = "error" in (res.stdout + res.stderr).lower() and "[Errno" not in res.stderr
    if has_error:
        return False, res.stdout + "\n" + res.stderr
    return True, res.stdout


def validate_outputs(ctx: MigrationContext) -> list[str]:
    failures = []
    files = (
        [OUTPUT_DIR / "publicschema-extensions.yaml"]
        + sorted(OUTPUT_DIR.glob("*.yaml"))
        + sorted(EXTERNAL_DIR.glob("*.yaml"))
    )
    seen = set()
    for f in files:
        if f in seen or not f.exists():
            continue
        seen.add(f)
        ok, msg = run_lint(f)
        if not ok:
            failures.append(f"{f.relative_to(ROOT)}: {msg.strip()[:500]}")
    return failures


def check_referential_integrity(ctx: MigrationContext) -> list[str]:
    """Every crosswalk CURIE points at a declared external enum meaning URI."""
    failures = []
    declared = set()
    for sysid, enums in ctx.external_enums.items():
        prefix = ctx.systems.systems[sysid]["prefix"]
        for enum_name, pvs in enums.items():
            for vkey, pv in pvs.items():
                declared.add(pv["meaning"])
    for target, source in ctx.crosswalk_refs:
        if target not in declared:
            failures.append(f"crosswalk {source} -> {target} is dangling")
    return failures


# ============================================================================
# Main
# ============================================================================


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true",
                    help="fail on lint warnings as well as errors")
    args = ap.parse_args()

    # Reset output dir
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    EXTERNAL_DIR.mkdir(parents=True)

    # Phase 0: inventory (including SEMIC alignment architecture from P4 commits on main).
    semic_data: dict = {}
    inv, concepts, properties, vocabularies, by_kind = load_inventory(semic_data)
    systems = load_systems()
    ctx = MigrationContext(
        inv=inv,
        concepts=concepts,
        properties=properties,
        vocabularies=vocabularies,
        by_kind=by_kind,
        systems=systems,
        external_references=semic_data.get("external_references", {}),
        external_terms_by_source=semic_data.get("external_terms_by_source", {}),
        alignments_by_subject=semic_data.get("alignments_by_subject", collections.defaultdict(list)),
        bases=semic_data.get("bases", {}),
        bibliography_refs=semic_data.get("bibliography_refs", collections.defaultdict(list)),
        categories=semic_data.get("categories", {}),
    )
    write_inventory_report(ctx)

    # Phase 1: domain split
    derive_domains(ctx)
    write_domain_split_report(ctx)

    # Phase 2: extension metamodel
    emit_extension_metamodel()

    # Phase 3 + 4: emit per-domain LinkML
    domains_present: set[str] = set()
    for v in ctx.concept_domain.values():
        domains_present.add(v)
    for v in ctx.property_domain.values():
        domains_present.add(v)
    for v in ctx.vocab_domain.values():
        domains_present.add(v)

    for domain in sorted(domains_present):
        emit_domain_file(domain, ctx)

    # Sibling content: credentials, bibliography, categories.
    emit_credentials_file(ctx)
    emit_bibliography_file(ctx)
    emit_categories_file(ctx)
    for d in ("credentials", "bibliography", "categories"):
        if (OUTPUT_DIR / f"{d}.yaml").exists():
            domains_present.add(d)

    # Phase 2b: external schemas (depends on Phase 3 having walked all vocabs/properties)
    emit_external_schemas(ctx)

    # Composite (must reference whichever domains and external schemas were actually emitted)
    emitted_domains = [d for d in sorted(domains_present) if (OUTPUT_DIR / f"{d}.yaml").exists()]
    emit_composite(ctx, emitted_domains)

    # Phase 5: validate
    integrity_failures = check_referential_integrity(ctx)
    lint_failures = validate_outputs(ctx)
    write_migration_report(ctx, lint_failures, integrity_failures)

    # Exit code
    print(f"Inventory: {sum(len(v) for v in by_kind.values())} source files")
    print(f"  Concepts: {len(by_kind.get('concept', []))}")
    print(f"  Properties: {len(by_kind.get('property', []))}")
    print(f"  Vocabularies: {len(by_kind.get('vocabulary', []))}")
    print(f"Domain split: {len(domains_present)} domains")
    print(f"External systems active: {sum(1 for es in ctx.external_enums.values() if es)}")
    print(f"Crosswalk references: {len(ctx.crosswalk_refs)}")
    print(f"Unmapped source fields: {len(set(ctx.unmapped))}")
    print(f"Referential integrity failures: {len(integrity_failures)}")
    print(f"linkml-lint failures: {len(lint_failures)}")
    print(f"Outputs written to: {OUTPUT_DIR}")

    if integrity_failures or lint_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
