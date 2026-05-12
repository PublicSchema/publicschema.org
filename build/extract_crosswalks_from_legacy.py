"""One-shot extractor: pre-cutover system_mappings -> value_crosswalk YAMLs.

Reads each pre-LinkML-cutover schema/vocabularies/**/*.yaml and
schema/properties/**/*.yaml at git rev d594bf7~1 (the commit *before*
the bespoke schema was deleted), walks its ``system_mappings:`` block,
and emits one YAML per (source, target_system) pair under
``schema/value_crosswalks/`` conforming to ``build/schemas/value_crosswalk.schema.json``.

The schema is byte-identical to publicschema-build's copy; the format is
also what publicschema.com/apps/core validates. Authoring crosswalks as
first-class value_crosswalk documents lets us drop the lossy
``system_mappings`` decomposition path from migrate_to_linkml.py without
losing ``vocabulary_name``, ``unmapped_canonical``, per-pair notes, or
per-pair migration_notes.

This script is intended to run once. After the emitted YAMLs are
committed, the build pipeline reads them directly and we can delete or
archive this script.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

LEGACY_REV = "d594bf7~1"
TODO = "TODO"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def crosswalk_id(source_kind: str, source_id: str, target_system_id: str) -> str:
    """Stable id for a (source, target_system) crosswalk.

    The id doubles as the filename stem. Domain-scoped vocab keys like
    ``crvs/registration-status`` collapse to ``crvs-registration-status``
    (filesystem-safe). Property names with underscores collapse to
    hyphens for consistency with the kebab-case vocab ids.
    """
    if source_kind not in {"vocabulary", "property"}:
        raise ValueError(f"unknown source_kind: {source_kind!r}")
    slug = source_id.replace("/", "-").replace("_", "-")
    return f"{slug}--{target_system_id}"


def crosswalk_filename(crosswalk_id_value: str) -> str:
    return f"{crosswalk_id_value}.yaml"


def extract_crosswalk(
    *,
    source_kind: str,
    source_id: str,
    target_system_id: str,
    entry: dict[str, Any],
    system_registry: dict[str, dict[str, Any]],
    external_references: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Convert one pre-cutover ``system_mappings.<sys>`` entry to a
    value_crosswalk dict.

    Raises ``KeyError`` if ``target_system_id`` is not in
    ``system_registry`` (so the caller can't silently emit a crosswalk
    pointing at an unknown system).
    """
    if target_system_id not in system_registry:
        raise KeyError(
            f"target_system_id {target_system_id!r} not in build/external_system_prefixes.yaml"
        )

    target_system = system_registry[target_system_id]
    target_set_id = entry.get("vocabulary_name") or target_system_id

    out: dict[str, Any] = {
        "id": crosswalk_id(source_kind, source_id, target_system_id),
        "source_value_set": {
            "id": source_id,
            "kind": source_kind,
            "source_id": "publicschema",
        },
        "target_value_set": {
            "id": target_set_id,
            "source_id": target_system_id,
        },
        "pairs": _build_pairs(entry),
        "standard": _build_standard(target_system_id, target_system, external_references),
    }
    top_note = entry.get("note")
    if isinstance(top_note, str) and top_note.strip():
        out["notes"] = top_note.strip()
    return out


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _build_pairs(entry: dict[str, Any]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for v in entry.get("values") or []:
        if not isinstance(v, dict):
            continue
        ext_code = v.get("code")
        ext_label = v.get("label")
        maps_to = v.get("maps_to")
        if maps_to is None:
            pair: dict[str, Any] = {
                "source_value": None,
                "target_value": ext_code,
                "quality": "unmapped",
            }
        else:
            pair = {
                "source_value": maps_to,
                "target_value": ext_code,
                "quality": "exact",
            }
        if isinstance(ext_label, str) and ext_label != "":
            pair["target_label"] = ext_label
        for fname in ("note", "unmapped_reason", "migration_note"):
            fval = v.get(fname)
            if isinstance(fval, str) and fval.strip():
                pair[fname] = fval.strip()
        pairs.append(pair)

    for canon in entry.get("unmapped_canonical") or []:
        if not isinstance(canon, str):
            continue
        pairs.append({
            "source_value": canon,
            "target_value": None,
            "quality": "unmapped",
        })

    return pairs


def _build_standard(
    target_system_id: str,
    target_system: dict[str, Any],
    external_references: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Source the ``standard:`` block from ``external_references[sysid]``
    when present; otherwise fall back to the TODO placeholder for fields
    that aren't safely derivable from the bare system registry.

    Option (a) per Jeremi: ``TODO`` is a literal marker the build refuses
    to ship. The lint step in build/value_crosswalks.py rejects any
    crosswalk where any standard field equals ``TODO``.
    """
    uri = target_system.get("uri") or TODO
    ext = external_references.get(target_system_id) or {}
    license_doc = ext.get("license") or {}
    artifacts = ext.get("artifacts") or []
    first_artifact = artifacts[0] if isinstance(artifacts, list) and artifacts else {}

    return {
        "source_id": target_system_id,
        "uri": uri,
        "custodian": ext.get("custodian") or TODO,
        "license": license_doc.get("id") or TODO,
        "license_uri": license_doc.get("uri") or TODO,
        "version": ext.get("version") or TODO,
        "attribution_text": license_doc.get("attribution_text") or TODO,
        "redistribution": license_doc.get("redistribution") or TODO,
        "retrieved_at": first_artifact.get("retrieved_at") or TODO,
        "source_sha256": first_artifact.get("sha256") or TODO,
    }


# ---------------------------------------------------------------------------
# Git-history scan & file emission (CLI)
# ---------------------------------------------------------------------------


def _git_show(rev_path: str, repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "show", rev_path],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git show {rev_path} failed: {result.stderr.strip()}")
    return result.stdout


def _git_ls_tree(rev: str, path: str, repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", rev, "--", path],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-tree {rev} {path} failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def _load_yaml_str(text: str) -> dict[str, Any] | None:
    doc = yaml.safe_load(text)
    return doc if isinstance(doc, dict) else None


def _load_legacy_resources(
    repo_root: Path, rev: str
) -> tuple[list[tuple[str, str, dict]], list[tuple[str, str, dict]]]:
    """Return ((source_kind, source_id, doc)) tuples for every legacy
    vocab and property that has a system_mappings: block."""
    vocab_paths = _git_ls_tree(rev, "schema/vocabularies/", repo_root)
    prop_paths = _git_ls_tree(rev, "schema/properties/", repo_root)

    vocabs: list[tuple[str, str, dict]] = []
    for path in vocab_paths:
        if not path.endswith(".yaml"):
            continue
        doc = _load_yaml_str(_git_show(f"{rev}:{path}", repo_root))
        if not isinstance(doc, dict) or not isinstance(doc.get("system_mappings"), dict):
            continue
        # Derive composite id: <domain>/<id> if path is schema/vocabularies/<domain>/<id>.yaml,
        # else bare <id>. The bespoke id field is authoritative.
        rel = path[len("schema/vocabularies/"):]
        if "/" in rel:
            domain = rel.split("/", 1)[0]
            bespoke_id = doc.get("id") or Path(rel).stem
            composite = f"{domain}/{bespoke_id}"
        else:
            composite = doc.get("id") or Path(rel).stem
        vocabs.append(("vocabulary", composite, doc))

    props: list[tuple[str, str, dict]] = []
    for path in prop_paths:
        if not path.endswith(".yaml"):
            continue
        doc = _load_yaml_str(_git_show(f"{rev}:{path}", repo_root))
        if not isinstance(doc, dict) or not isinstance(doc.get("system_mappings"), dict):
            continue
        prop_id = doc.get("id") or Path(path).stem
        props.append(("property", prop_id, doc))

    return vocabs, props


def _load_system_registry(repo_root: Path) -> dict[str, dict[str, Any]]:
    text = (repo_root / "build" / "external_system_prefixes.yaml").read_text(encoding="utf-8")
    doc = yaml.safe_load(text) or {}
    systems = doc.get("systems") or {}
    if not isinstance(systems, dict):
        raise RuntimeError("build/external_system_prefixes.yaml: 'systems' is not a mapping")
    return systems


def _load_external_references(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Read every schema/external_references/<sys>.yaml. Keyed by the
    ``id:`` field declared in the document (which matches the system id
    used in system_mappings: blocks)."""
    ext_dir = repo_root / "schema" / "external_references"
    out: dict[str, dict[str, Any]] = {}
    if not ext_dir.is_dir():
        return out
    for path in sorted(ext_dir.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(doc, dict) and isinstance(doc.get("id"), str):
            out[doc["id"]] = doc
    return out


def _yaml_dump(doc: dict[str, Any]) -> str:
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=1000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rev",
        default=LEGACY_REV,
        help=f"git revision to read pre-cutover schema from (default: {LEGACY_REV})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("schema/value_crosswalks"),
        help="output directory (default: schema/value_crosswalks)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = (repo_root / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    system_registry = _load_system_registry(repo_root)
    external_references = _load_external_references(repo_root)
    vocabs, props = _load_legacy_resources(repo_root, args.rev)

    written = 0
    todo_systems: set[str] = set()
    for source_kind, source_id, doc in (*vocabs, *props):
        sm = doc.get("system_mappings") or {}
        for target_system_id, entry in sm.items():
            if not isinstance(entry, dict):
                continue
            cw = extract_crosswalk(
                source_kind=source_kind,
                source_id=source_id,
                target_system_id=target_system_id,
                entry=entry,
                system_registry=system_registry,
                external_references=external_references,
            )
            path = out_dir / crosswalk_filename(cw["id"])
            path.write_text(_yaml_dump(cw), encoding="utf-8")
            written += 1
            if any(v == TODO for v in cw["standard"].values()):
                todo_systems.add(target_system_id)

    print(f"Wrote {written} value_crosswalk YAMLs to {out_dir}", file=sys.stderr)
    if todo_systems:
        print(
            "TODO standard metadata for these systems (option (a) fails the "
            "build until populated): " + ", ".join(sorted(todo_systems)),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
