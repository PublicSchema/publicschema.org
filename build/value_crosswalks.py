"""Load authored ``schema/value_crosswalks/*.yaml`` and synthesize them
back into the pre-cutover ``system_mappings`` shape that vocabulary.json
and the site renderer consume.

The value_crosswalk format is the SSSOM-flavoured org-internal format
used across publicschema-build and publicschema.com/apps/core. It is
the *source of truth* post-cutover for per-(source, system) crosswalks
that the bespoke pre-cutover schema previously expressed as inline
``system_mappings:`` blocks (and which migrate_to_linkml.py decomposed
lossily into per-PV annotations).

Synthesis is the inverse of extract_crosswalks_from_legacy.

Strict TODO policy: the build refuses to ship a crosswalk whose
``standard:`` block contains any literal ``"TODO"`` marker. Call
``load_crosswalks(..., strict=True)`` to enforce; the default
non-strict mode is for tests and one-off introspection.

Documented "no canonical artifact" exception: some upstream standards
(multi-repo assemblies, multi-country surveys, GitBook/wiki specs,
country-configured enums) have no single fetchable artifact a SHA-256
can represent. For those, the crosswalk file sets ``artifact_kind:
none`` and provides a non-empty ``artifact_notes:`` explaining why.
The JSON schema (``build/schemas/value_crosswalk.schema.json``) waives
the ``source_sha256`` requirement in that case; the strict TODO gate
still applies to every other field.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

import yaml

TODO = "TODO"


class SourceKey(NamedTuple):
    """(source_kind, source_id) — the index key for crosswalks.

    ``source_kind`` is ``"vocabulary"`` or ``"property"``; ``source_id``
    is the bespoke composite id (e.g. ``"sex"`` or
    ``"crvs/registration-status"`` for vocabs, bare property name for
    properties).
    """

    kind: str
    id: str


class StandardTodoError(RuntimeError):
    """Raised when a crosswalk's ``standard:`` block still contains
    literal ``"TODO"`` placeholders and the loader is in strict mode."""


CrosswalkIndex = dict[SourceKey, dict[str, dict[str, Any]]]


def load_crosswalks(
    crosswalks_dir: Path,
    *,
    strict: bool = False,
) -> CrosswalkIndex:
    """Load every ``*.yaml`` in ``crosswalks_dir`` and key by source.

    Returns ``{SourceKey(kind, id): {target_system_id: crosswalk_doc}}``.

    With ``strict=True``, raises ``StandardTodoError`` on the first
    crosswalk whose ``standard:`` block contains a literal ``"TODO"``
    placeholder. This is the build-time gate that enforces option (a)
    from the design discussion: the build refuses to ship until every
    standard's metadata is populated.
    """
    index: CrosswalkIndex = {}
    if not crosswalks_dir.is_dir():
        return index

    for path in sorted(crosswalks_dir.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            continue
        if strict:
            _check_no_todo(doc, path.name)

        src = doc.get("source_value_set") or {}
        tgt = doc.get("target_value_set") or {}
        kind = src.get("kind")
        sid = src.get("id")
        tsid = tgt.get("source_id")
        if not isinstance(kind, str) or not isinstance(sid, str) or not isinstance(tsid, str):
            continue
        key = SourceKey(kind, sid)
        index.setdefault(key, {})[tsid] = doc
    return index


def _check_no_todo(doc: dict[str, Any], filename: str) -> None:
    std = doc.get("standard") or {}
    if not isinstance(std, dict):
        return
    bad = [k for k, v in std.items() if v == TODO]
    if bad:
        raise StandardTodoError(
            f"{filename}: standard metadata still has TODO placeholders "
            f"for {', '.join(sorted(bad))}. Populate "
            "schema/external_references/<system>.yaml or fill these fields "
            "directly before shipping."
        )


def synthesize_system_mappings(
    index: CrosswalkIndex,
    source_kind: str,
    source_id: str,
) -> dict[str, dict[str, Any]] | None:
    """Build the pre-cutover ``system_mappings`` dict for one source.

    Returns ``{target_system_id: {vocabulary_name, values,
    unmapped_canonical?}}`` matching the shape the site's
    ``Record<string, SystemMapping>`` TS interface expects. Returns
    ``None`` if no crosswalks are authored for the given source (so the
    caller can distinguish "no authored crosswalks" from "authored but
    empty").
    """
    bucket = index.get(SourceKey(source_kind, source_id))
    if not bucket:
        return None

    out: dict[str, dict[str, Any]] = {}
    for tsid, doc in bucket.items():
        out[tsid] = _doc_to_system_mapping(doc)
    return out


def _doc_to_system_mapping(doc: dict[str, Any]) -> dict[str, Any]:
    target_set = doc.get("target_value_set") or {}
    pairs = doc.get("pairs") or []

    values: list[dict[str, Any]] = []
    unmapped_canonical: list[str] = []

    for pair in pairs:
        if not isinstance(pair, dict):
            continue
        target_value = pair.get("target_value")
        source_value = pair.get("source_value")

        if target_value is None:
            if isinstance(source_value, str):
                unmapped_canonical.append(source_value)
            continue

        label = pair.get("target_label")
        if not isinstance(label, str) or not label:
            label = str(target_value)
        v: dict[str, Any] = {
            "code": target_value,
            "label": label,
            "maps_to": source_value,
        }
        if isinstance(pair.get("unmapped_reason"), str):
            v["unmapped_reason"] = pair["unmapped_reason"]
        values.append(v)

    sm: dict[str, Any] = {"values": values}
    vocab_name = target_set.get("id")
    target_sys = target_set.get("source_id")
    # The crosswalk schema requires target_value_set.id to be non-empty,
    # so the extractor falls back to the target system id when the
    # legacy authoring had no vocabulary_name. Treat that fallback as
    # "no name given" rather than synthesizing a redundant
    # "System vocabulary: <system_id>" line on the site.
    if isinstance(vocab_name, str) and vocab_name != target_sys:
        sm["vocabulary_name"] = vocab_name
    if unmapped_canonical:
        sm["unmapped_canonical"] = unmapped_canonical

    # Re-order so vocabulary_name surfaces first when present (cosmetic;
    # matches the pre-cutover authoring order so diffs against legacy
    # output stay readable).
    if "vocabulary_name" in sm:
        sm = {
            "vocabulary_name": sm["vocabulary_name"],
            "values": sm["values"],
            **({"unmapped_canonical": unmapped_canonical} if unmapped_canonical else {}),
        }
    return sm
