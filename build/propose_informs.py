"""Propose `informs:` additions for bibliography entries by mechanically
extracting external_equivalents, schema_org_equivalent, and vocab `standard:`
fields from the schema.

Read-only: writes a Markdown report to stdout (or --out file). Does not modify
any YAML.

Curated lookup tables are kept small and explicit. Anything outside the table
is reported as "unmapped" so a human can decide.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Matches the start of the `informs:` block at column 0. Anchoring to line
# start avoids false matches on inline comments or string values containing
# the substring "informs:".
INFORMS_HEADER_RE = re.compile(r"^informs:", re.MULTILINE)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "schema"

# (key, vocabulary) -> bibliography id; None means "do not auto-map; flag".
EXTERNAL_EQUIV_LOOKUP: dict[tuple[str, str | None], str | None] = {
    ("dci", "DCI Core"): "spdci-common-standards",
    ("dci", "DCI IBR"): "spdci-ibr",
    ("semic", "Core Person"): "semic-core-person",
    ("semic", "Core Location"): "semic-core-location",
    ("semic", "CCCEV"): "semic-cccev",
    ("semic", "Core Vocabularies"): None,  # match=none in practice; flag if not
    ("semic", "ADMS"): "semic-adms",
    ("fhir", "FHIR R4"): "fhir-r4",
    ("icao", "ICAO Doc 9303"): "icao-doc-9303",
    # opencrvs is a system, not a standard; intentionally excluded.
}

# Vocab standard.name -> bibliography id (exact string match).
VOCAB_STANDARD_LOOKUP: dict[str, str] = {
    "ISO 3166-1": "iso-3166-1",
    "WHO/ICD Manner of Death classification": "who-icd-manner-of-death",
    "ISO 4217": "iso-4217",
    "ISCED 2011": "isced-2011",
    "ILO 19th ICLS Resolution concerning statistics of work, employment, and labour underutilization": "ilo-19th-icls-2013",
    "OASIS CAP v1.2": "oasis-cap-v1-2",
    "ISO 639-3": "iso-639-3",
    "UNSD Principles and Recommendations for Population and Housing Censuses, Rev.3": "un-census-rev3",
    "UN UNSD Population Census Framework": "un-census-rev3",
    "ISCO-08": "isco-08",
    "UN M49": "un-m49",
    "ISO 15924": "iso-15924",
    "ISO/IEC 5218": "iso-5218",
    "ILO ICSE-18 (20th ICLS, 2018)": "ilo-20th-icls-2018",
    "WHO/UNICEF Joint Monitoring Programme (JMP)": "who-unicef-jmp",
    "WHO/UNICEF JMP Service Ladder (SDG 6.1.1)": "who-unicef-jmp",
    "WHO/UNICEF JMP Service Ladder (SDG 6.2.1)": "who-unicef-jmp",
    "DHS/MICS Harmonized Housing Codes": "dhs-recode7",
    "UN Principles and Recommendations for Population and Housing Censuses, Rev. 3": "un-census-rev3",
    "WHO Household Energy Database": "who-household-energy",
    "Washington Group Short Set on Functioning (WG-SS)": "washington-group-ss",
    "ITU Core ICT Indicators": "itu-core-ict",
    "FAO World Programme for the Census of Agriculture 2020": "fao-wca-2020-vol1",
    "FAO Voluntary Guidelines on the Responsible Governance of Tenure (VGGT)": "fao-vggt",
    "FAO Food Insecurity Experience Scale (FIES)": "fao-fies",
}

SKIPPED_KEYS = {"opencrvs"}


@dataclass
class Proposal:
    bib_id: str
    kind: str  # 'concepts' | 'properties' | 'vocabularies'
    target_id: str
    source_path: str
    field_path: str  # e.g. "external_equivalents.dci"
    evidence: str  # short excerpt for the human reviewer


@dataclass
class Flag:
    source_path: str
    field_path: str
    reason: str
    detail: str


@dataclass
class Report:
    proposals: list[Proposal] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    bib_existing: dict[str, dict[str, set[str]]] = field(default_factory=dict)


def load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text()) or {}


def vocab_canonical_id(p: Path) -> str:
    """Return canonical vocab id: '<domain>/<id>' if nested, else '<id>'."""
    rel = p.relative_to(SCHEMA / "vocabularies")
    parts = rel.with_suffix("").parts
    return "/".join(parts) if len(parts) > 1 else parts[0]


def collect_existing_informs(report: Report) -> None:
    for p in sorted((SCHEMA / "bibliography").glob("*.yaml")):
        d = load_yaml(p)
        bid = d.get("id") or p.stem
        informs = d.get("informs") or {}
        report.bib_existing[bid] = {
            "concepts": set(informs.get("concepts") or []),
            "vocabularies": set(informs.get("vocabularies") or []),
            "properties": set(informs.get("properties") or []),
        }


def process_external_equivalents(
    d: dict, p: Path, kind: str, target_id: str, report: Report
) -> None:
    ee = d.get("external_equivalents") or {}
    if not isinstance(ee, dict):
        return
    for key, val in ee.items():
        if not isinstance(val, dict):
            continue
        match = val.get("match")
        if match == "none":
            continue
        if key in SKIPPED_KEYS:
            report.skipped.append(
                f"{p.relative_to(REPO_ROOT)}: external_equivalents.{key} (system, not standard)"
            )
            continue
        vocab = val.get("vocabulary")
        bib_id = EXTERNAL_EQUIV_LOOKUP.get((key, vocab), "__MISSING__")
        if bib_id == "__MISSING__":
            report.flags.append(
                Flag(
                    source_path=str(p.relative_to(REPO_ROOT)),
                    field_path=f"external_equivalents.{key}",
                    reason="unknown_key",
                    detail=f"no lookup entry for ({key!r}, {vocab!r}); add it or skip",
                )
            )
            continue
        if bib_id is None:
            report.flags.append(
                Flag(
                    source_path=str(p.relative_to(REPO_ROOT)),
                    field_path=f"external_equivalents.{key}",
                    reason="needs_decision",
                    detail=f"({key!r}, {vocab!r}) has no dedicated bibliography entry yet",
                )
            )
            continue
        report.proposals.append(
            Proposal(
                bib_id=bib_id,
                kind=kind,
                target_id=target_id,
                source_path=str(p.relative_to(REPO_ROOT)),
                field_path=f"external_equivalents.{key}",
                evidence=f"vocabulary={vocab!r}, match={match!r}, uri={val.get('uri')!r}",
            )
        )


def process_schema_org(d: dict, p: Path, target_id: str, report: Report) -> None:
    s = d.get("schema_org_equivalent")
    if not s:
        return
    report.proposals.append(
        Proposal(
            bib_id="schema-org",
            kind="properties",
            target_id=target_id,
            source_path=str(p.relative_to(REPO_ROOT)),
            field_path="schema_org_equivalent",
            evidence=str(s),
        )
    )


def process_vocab_standard(d: dict, p: Path, vocab_id: str, report: Report) -> None:
    std = d.get("standard")
    if not isinstance(std, dict):
        return
    name = (std.get("name") or "").strip()
    if not name:
        return
    bib_id = VOCAB_STANDARD_LOOKUP.get(name)
    if bib_id is None:
        report.flags.append(
            Flag(
                source_path=str(p.relative_to(REPO_ROOT)),
                field_path="standard.name",
                reason="unknown_standard_name",
                detail=f"no lookup entry for {name!r}; add it or skip",
            )
        )
        return
    report.proposals.append(
        Proposal(
            bib_id=bib_id,
            kind="vocabularies",
            target_id=vocab_id,
            source_path=str(p.relative_to(REPO_ROOT)),
            field_path="standard.name",
            evidence=f"name={name!r}, uri={std.get('uri')!r}",
        )
    )


def build_report() -> Report:
    report = Report()
    collect_existing_informs(report)

    for p in sorted((SCHEMA / "concepts").glob("*.yaml")):
        d = load_yaml(p)
        cid = d.get("id") or p.stem
        process_external_equivalents(d, p, "concepts", cid, report)

    for p in sorted((SCHEMA / "properties").glob("*.yaml")):
        d = load_yaml(p)
        pid = d.get("id") or p.stem
        process_external_equivalents(d, p, "properties", pid, report)
        process_schema_org(d, p, pid, report)

    for p in sorted((SCHEMA / "vocabularies").glob("**/*.yaml")):
        d = load_yaml(p)
        vid = vocab_canonical_id(p)
        process_vocab_standard(d, p, vid, report)
        process_external_equivalents(d, p, "vocabularies", vid, report)

    return report


def render_markdown(report: Report) -> str:
    out: list[str] = []
    out.append("# Proposed `informs:` additions (mechanical Phase 1)\n")
    out.append(
        "Generated by `build/propose_informs.py`. Read-only report; no files modified.\n"
    )
    out.append(
        "Each proposal lists the source file and field that triggered it so you can verify before applying.\n"
    )

    by_bib: dict[str, list[Proposal]] = defaultdict(list)
    for prop in report.proposals:
        by_bib[prop.bib_id].append(prop)

    out.append(f"\n## Summary\n")
    out.append(f"- Bibliography entries touched: **{len(by_bib)}**")
    out.append(f"- Total proposed links: **{len(report.proposals)}**")
    new_links = sum(
        1
        for prop in report.proposals
        if prop.target_id not in report.bib_existing.get(prop.bib_id, {}).get(prop.kind, set())
    )
    out.append(f"- Net-new links (not already in informs): **{new_links}**")
    out.append(f"- Flags needing human decision: **{len(report.flags)}**")
    out.append(f"- Skipped (opencrvs etc.): **{len(report.skipped)}**\n")

    out.append("\n## Per-bibliography proposals\n")
    for bib_id in sorted(by_bib):
        existing = report.bib_existing.get(bib_id, {"concepts": set(), "vocabularies": set(), "properties": set()})
        props = by_bib[bib_id]
        by_kind: dict[str, list[Proposal]] = defaultdict(list)
        for prop in props:
            by_kind[prop.kind].append(prop)

        out.append(f"\n### `{bib_id}`")
        for kind in ("concepts", "vocabularies", "properties"):
            items = by_kind.get(kind, [])
            if not items:
                continue
            out.append(f"\n**{kind}**\n")
            out.append("| target | status | source | evidence |")
            out.append("|---|---|---|---|")
            seen: set[str] = set()
            for prop in sorted(items, key=lambda x: x.target_id):
                if prop.target_id in seen:
                    continue
                seen.add(prop.target_id)
                already = prop.target_id in existing.get(kind, set())
                status = "already present" if already else "**ADD**"
                out.append(
                    f"| `{prop.target_id}` | {status} | `{prop.source_path}` | {prop.evidence} |"
                )
            already_set = existing.get(kind, set())
            missing_from_proposal = sorted(already_set - seen)
            if missing_from_proposal:
                out.append("")
                out.append(
                    f"_Currently in `informs.{kind}` but not surfaced by extractor (review): "
                    + ", ".join(f"`{x}`" for x in missing_from_proposal)
                    + "_"
                )

    if report.flags:
        out.append("\n## Flags (need human decision)\n")
        out.append("| source | field | reason | detail |")
        out.append("|---|---|---|---|")
        for f in report.flags:
            out.append(
                f"| `{f.source_path}` | `{f.field_path}` | {f.reason} | {f.detail} |"
            )

    if report.skipped:
        out.append("\n## Skipped\n")
        for s in report.skipped:
            out.append(f"- {s}")

    out.append("")
    return "\n".join(out)


def render_informs_block(informs: dict[str, list[str]]) -> str:
    """Render an `informs:` block matching the existing bibliography YAML style.

    2-space indent, `[]` for empty arrays, sorted item order within each list.
    Note: existing custom ordering in a bibliography YAML is not preserved;
    the first `--apply` run that touches a file re-sorts its informs lists
    alphabetically.
    """
    lines = ["informs:"]
    for kind in ("concepts", "vocabularies", "properties"):
        items = sorted(set(informs.get(kind) or []))
        if not items:
            lines.append(f"  {kind}: []")
        else:
            lines.append(f"  {kind}:")
            for item in items:
                lines.append(f"    - {item}")
    return "\n".join(lines) + "\n"


def apply_proposals(report: Report) -> dict[str, dict[str, list[str]]]:
    """Apply proposals by rewriting the `informs:` block of each touched bib YAML.

    Existing entries are preserved; new entries are added; nothing is removed.
    Returns a per-bib summary of what was added.
    """
    by_bib: dict[str, list[Proposal]] = defaultdict(list)
    for prop in report.proposals:
        by_bib[prop.bib_id].append(prop)

    summary: dict[str, dict[str, list[str]]] = {}
    for bib_id, props in by_bib.items():
        bib_path = SCHEMA / "bibliography" / f"{bib_id}.yaml"
        if not bib_path.exists():
            print(f"WARNING: {bib_path} not found, skipping", file=sys.stderr)
            continue
        text = bib_path.read_text()
        parts = INFORMS_HEADER_RE.split(text, maxsplit=1)
        if len(parts) != 2:
            print(f"WARNING: {bib_path} has no informs: block, skipping", file=sys.stderr)
            continue

        existing = report.bib_existing.get(bib_id, {"concepts": set(), "vocabularies": set(), "properties": set()})
        merged = {kind: set(existing.get(kind, set())) for kind in ("concepts", "vocabularies", "properties")}
        added = {"concepts": [], "vocabularies": [], "properties": []}
        for prop in props:
            if prop.target_id not in merged[prop.kind]:
                merged[prop.kind].add(prop.target_id)
                added[prop.kind].append(prop.target_id)

        if not any(added.values()):
            continue

        before = parts[0].rstrip() + "\n\n"
        new_block = render_informs_block({k: sorted(v) for k, v in merged.items()})
        bib_path.write_text(before + new_block)
        summary[bib_id] = {k: sorted(set(v)) for k, v in added.items() if v}

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        help="Write report to this file. If omitted, writes to stdout.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write proposed informs additions back into bibliography YAMLs. Only adds; never removes.",
    )
    args = parser.parse_args()

    report = build_report()
    md = render_markdown(report)
    if args.out:
        args.out.write_text(md)
        print(f"Wrote {args.out} ({len(md):,} bytes)", file=sys.stderr)
    elif not args.apply:
        sys.stdout.write(md)

    if args.apply:
        summary = apply_proposals(report)
        if not summary:
            print("No additions to apply.", file=sys.stderr)
        else:
            print(f"Applied additions to {len(summary)} bibliography entries:", file=sys.stderr)
            for bib_id, added in sorted(summary.items()):
                total = sum(len(v) for v in added.values())
                parts = ", ".join(f"{k}+{len(v)}" for k, v in added.items() if v)
                print(f"  {bib_id}: {total} new ({parts})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
