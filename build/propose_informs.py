"""Propose `informs` additions for bibliography entries by mechanically
extracting external alignments, schema.org mappings, and vocabulary
`standard_json` fields from the LinkML schema.

By default this writes a Markdown report to stdout (or --out file) and
modifies nothing. `--apply` adds the proposed links to the `informs_json`
annotations in schema/bibliography.yaml; term-level `bibliography_refs`
annotations must then be updated to match (see docs/authoring-linkml.md).

An alignment whose `vocabulary_id` is itself a bibliography id maps to that
entry. Other alignments go through the curated lookup tables, which are kept
small and explicit. Anything outside them is reported as "unmapped" so a
human can decide.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from build.linkml_reader import load_raw_from_linkml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "schema"
BIBLIOGRAPHY = SCHEMA / "bibliography.yaml"
INFORMS_KINDS = ("concepts", "properties", "vocabularies")

# (key, vocabulary) -> bibliography id; None means "do not auto-map; flag".
EXTERNAL_EQUIV_LOOKUP: dict[tuple[str, str | None], str | None] = {
    ("dci", "DCI Core"): "spdci-common-standards",
    ("dci", "DCI IBR"): "spdci-ibr",
    ("dci", "DCI Social Registry"): "spdci-social-registry",
    ("semic", "Core Person"): "semic-core-person",
    ("semic", "Core Location"): "semic-core-location",
    ("semic-adminunit", "Core Location"): "semic-core-location",
    ("semic", "CCCEV"): "semic-cccev",
    ("semic", "CPOV"): "semic-cpov",
    ("semic", "Core Vocabularies"): None,  # match=none in practice; flag if not
    ("semic", "ADMS"): "semic-adms",
    ("fhir", "FHIR R4"): "fhir-r4",
    ("fhir-r4", "FHIR R4"): "fhir-r4",
    ("fhir-r5", "FHIR R5"): "fhir-r5",
    ("icao", "ICAO Doc 9303"): "icao-doc-9303",
    ("prov", "PROV-O"): "w3c-prov-o",
    ("foaf", "FOAF"): "foaf",
    ("schema-org", "schema.org"): "schema-org",
    ("semic", "CPSV-AP 3.2.0"): "semic-cpsv-ap",
    ("elm", "European Learning Model 3"): "ebsi-europass-elm",
    ("geosparql", "GeoSPARQL 1.1"): "ogc-geosparql-11",
    # W3C DPV v2 and its GDPR legal extension are all tracked under a single
    # bibliography entry (w3c-dpv); the snapshots differ by module but the
    # informs relationship is to DPV as a whole.
    ("dpv", "W3C DPV v2"): "w3c-dpv",
    ("dpv", "DPV v2"): "w3c-dpv",
    ("dpv-gdpr", "DPV GDPR extension v2"): "w3c-dpv",
    ("dpv-consent-notice", "W3C DPV v2"): "w3c-dpv",
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
    "ISO 639:2023 (Set 3)": "iso-639-3",
    "UNSD Principles and Recommendations for Population and Housing Censuses, Rev.3": "un-census-rev3",
    "UN UNSD Population Census Framework": "un-census-rev3",
    "UN Principles and Recommendations for Population and Housing Censuses, Revision 3": "un-census-rev3",
    "ISCO-08": "isco-08",
    "UN M49": "un-m49",
    "ISO 15924": "iso-15924",
    "ISO/IEC 5218": "iso-5218",
    "ISO/IEC 5218:2022": "iso-5218",
    "ILO ICSE-18 (20th ICLS, 2018)": "ilo-20th-icls-2018",
    "WHO/UNICEF Joint Monitoring Programme (JMP)": "who-unicef-jmp",
    "WHO/UNICEF JMP Service Ladder (SDG 6.1.1)": "who-unicef-jmp",
    "WHO/UNICEF JMP Service Ladder (SDG 6.2.1)": "who-unicef-jmp",
    "DHS/MICS Harmonized Housing Codes": "dhs-recode7",
    "UN Principles and Recommendations for Population and Housing Censuses, Rev. 3": "un-census-rev3",
    "WHO Household Energy Database": "who-household-energy",
    "Washington Group Short Set on Functioning (WG-SS)": "washington-group-ss",
    "Washington Group Extended Set on Functioning (WG-ES)": "washington-group-es",
    "ITU Core ICT Indicators": "itu-core-ict",
    "FAO World Programme for the Census of Agriculture 2020": "fao-wca-2020-vol1",
    "FAO Voluntary Guidelines on the Responsible Governance of Tenure (VGGT)": "fao-vggt",
    "FAO Food Insecurity Experience Scale (FIES)": "fao-fies",
    "LOINC LL4129-4 Pregnancy Status": "loinc-pregnancy-status",
    "WHO Child Growth Standards (2006)": "who-child-growth-standards",
    "WHO/UNICEF/WFP/UNHCR Joint Statement on Community-based Management of Acute Malnutrition (2007)": "who-muac-cutoffs",
    "WHO/UNICEF Joint Statement: WHO child growth standards and the identification of severe acute malnutrition in infants and children (2009)": "who-muac-cutoffs",
    "UN Degree of Urbanisation (DEGURBA)": "un-degurba",
    "EGRISS International Recommendations on IDP Statistics (IRIS)": "egriss-iris",
    "WG/UNICEF Child Functioning Module (CFM)": "washington-group-cfm",
    "Washington Group Analytic Guidelines for the Creation of Disability Identifiers": "washington-group-ss",
    "WHO/UNICEF joint statement (2009) and Sphere Handbook (2018)": "who-muac-cutoffs",
    "WHO Child Growth Standards and Growth Reference": "who-child-growth-standards",
    "WHO Anthropometric Training Course (2008)": "who-child-growth-standards",
    "WFP VAM Food Consumption Analysis (2008)": "wfp-fcs",
    "The Coping Strategies Index (Maxwell and Caldwell, 2008)": "wfp-rcsi",
    "WFP CARI Guidelines (3rd edition, 2021)": "wfp-lcs",
    "FANTA Household Hunger Scale Indicator Guide (2011)": "fanta-hhs",
    "FAO Guidelines for Measuring Household and Individual Dietary Diversity (i1983e, 2011)": "fao-hdds",
    "FAO Minimum Dietary Diversity for Women (MDD-W) Guide, 2021": "fao-mdd-w",
    "IOM Displacement Tracking Matrix (DTM) Shelter Damage Assessment": "iom-dtm",
    "Sphere Handbook (2018) Shelter and Settlement chapter": "sphere-2018",
    "Global Shelter Cluster post-disaster shelter situation categories": "global-shelter-cluster",
    "ATC-20 Post-Earthquake Safety Evaluation of Buildings": "atc-20",
    "WFP VAM Food Consumption Score Technical Guidance Note (2015)": "wfp-fcs",
    "FANTA Household Hunger Scale: Indicator Definition and Measurement Guide (2010, revised 2017)": "fanta-hhs",
    "Washington Group Short Set on Functioning (WG-SS), 2006/2016": "washington-group-ss",
    "WHO/UNICEF/WFP/UNSCN Joint Statement on Community-based Management of Acute Malnutrition (2007/2009)": "who-muac-cutoffs",
    "WHO Service Availability and Readiness Assessment (SARA) Reference Manual v2.2": "who-sara",
    "WHO Health Systems Strengthening Glossary": "who-health-systems",
    "WHO Health Resources and Services Availability Monitoring System (HeRAMS)": "who-herams",
    "UNESCO International Standard Classification of Education (ISCED) 2011": "isced-2011",
    "UNESCO UIS ISCED 2011 \u2014 Operational Manual (Chapter 4, Management and Funding)": "isced-2011",
    "WHO/UNICEF JMP Core Questions on Drinking Water and Sanitation for Household Surveys": "who-unicef-jmp",
    "DHS-8 Woman's Questionnaire, Chapter 9 (m2, m3, rh_pnc_wm_pv series)": "dhs-woman-questionnaire",
    "Sphere Handbook 2018, Standard 6 Security of Tenure; UNHCR HLP guidance": "sphere-2018",
    "IOM Displacement Tracking Matrix (DTM) documentation indicator": "iom-dtm",
    "FAO World Programme for the Census of Agriculture 2030 (WCA 2030), Item 0204 Area of holding according to land tenure types": "fao-wca-2030",
    "FAO World Programme for the Census of Agriculture 2030 (WCA 2030), Annex 8 Classification of livestock": "fao-wca-2030",
    "ISO 19152-1:2024 Land Administration Domain Model (LADM)": "iso-19152-1-2024",
}

SKIPPED_KEYS = {"opencrvs", "dhis2"}


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


def collect_existing_informs(raw: dict, report: Report) -> None:
    for bid, entry in raw["bibliography"].items():
        informs = entry.get("informs") or {}
        report.bib_existing[bid] = {kind: set(informs.get(kind) or []) for kind in INFORMS_KINDS}


def resolve_alignment(key: str, vocab: str | None, report: Report) -> str | None:
    """Return the bibliography id for an alignment, None to flag, or "__MISSING__"."""
    if (key, vocab) in EXTERNAL_EQUIV_LOOKUP:
        return EXTERNAL_EQUIV_LOOKUP[(key, vocab)]
    if key in report.bib_existing:
        return key
    return "__MISSING__"


def process_external_equivalents(
    d: dict, source: str, kind: str, target_id: str, report: Report
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
            report.skipped.append(f"{source}: external_equivalents.{key} (system, not standard)")
            continue
        vocab = val.get("vocabulary")
        bib_id = resolve_alignment(key, vocab, report)
        if bib_id == "__MISSING__":
            report.flags.append(
                Flag(
                    source_path=source,
                    field_path=f"external_equivalents.{key}",
                    reason="unknown_key",
                    detail=f"no lookup entry for ({key!r}, {vocab!r}); add it or skip",
                )
            )
            continue
        if bib_id is None:
            report.flags.append(
                Flag(
                    source_path=source,
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
                source_path=source,
                field_path=f"external_equivalents.{key}",
                evidence=f"vocabulary={vocab!r}, match={match!r}, uri={val.get('uri')!r}",
            )
        )


def process_schema_org(d: dict, source: str, target_id: str, report: Report) -> None:
    s = d.get("schema_org_equivalent")
    if not s:
        return
    report.proposals.append(
        Proposal(
            bib_id="schema-org",
            kind="properties",
            target_id=target_id,
            source_path=source,
            field_path="schema_org_equivalent",
            evidence=str(s),
        )
    )


def process_vocab_standard(d: dict, source: str, vocab_id: str, report: Report) -> None:
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
                source_path=source,
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
            source_path=source,
            field_path="standard.name",
            evidence=f"name={name!r}, uri={std.get('uri')!r}",
        )
    )


def build_report(schema_dir: Path = SCHEMA) -> Report:
    """Collect proposals from the LinkML schema.

    Sources are labelled by term kind and catalog key (for example
    ``concept health/HealthFacility``), because the catalog keys are what
    `informs_json` lists.
    """
    raw = load_raw_from_linkml(schema_dir)
    report = Report()
    collect_existing_informs(raw, report)

    for cid, d in sorted(raw["concepts"].items()):
        process_external_equivalents(d, f"concept {cid}", "concepts", cid, report)

    for pid, d in sorted(raw["properties"].items()):
        process_external_equivalents(d, f"property {pid}", "properties", pid, report)
        process_schema_org(d, f"property {pid}", pid, report)

    for vid, d in sorted(raw["vocabularies"].items()):
        process_vocab_standard(d, f"vocabulary {vid}", vid, report)
        process_external_equivalents(d, f"vocabulary {vid}", "vocabularies", vid, report)

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

    out.append("\n## Summary\n")
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


def render_informs_json(informs: dict[str, set[str]]) -> str:
    """Render an `informs_json` annotation line in the bibliography.yaml style.

    Kinds appear in a fixed order, items are sorted, and empty kinds are omitted.
    """
    payload = {kind: sorted(informs[kind]) for kind in INFORMS_KINDS if informs.get(kind)}
    value = json.dumps(payload, ensure_ascii=False).replace("'", "''")
    return f"      informs_json: '{value}'"


def apply_proposals(report: Report, path: Path = BIBLIOGRAPHY) -> dict[str, dict[str, list[str]]]:
    """Add proposed links to the `informs_json` annotations in bibliography.yaml.

    Existing links are preserved; new links are added; nothing is removed.
    Returns a per-bibliography summary of what was added.
    """
    added: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for prop in report.proposals:
        existing = report.bib_existing.get(prop.bib_id)
        if existing is None:
            print(f"WARNING: bibliography {prop.bib_id!r} not found, skipping", file=sys.stderr)
            continue
        if prop.target_id not in existing[prop.kind]:
            added[prop.bib_id][prop.kind].add(prop.target_id)
    if not added:
        return {}

    citation_re = re.compile(r"^      citation_id: (\S+)$")
    pending = set(added)
    current: str | None = None
    out: list[str] = []
    lines = iter(path.read_text(encoding="utf-8").split("\n"))
    for line in lines:
        if line.startswith("  ") and not line.startswith("   "):
            current = None
        if m := citation_re.match(line):
            current = m.group(1)
        if current in pending and line.startswith("      informs_json: "):
            existing = report.bib_existing[current]
            out.append(
                render_informs_json({k: existing[k] | added[current][k] for k in INFORMS_KINDS})
            )
            pending.discard(current)
            # Drop continuation lines of a wrapped scalar.
            for line in lines:
                if not line.startswith("        "):
                    out.append(line)
                    break
            continue
        out.append(line)
    for bib_id in sorted(pending):
        print(f"WARNING: {bib_id!r} has no informs_json annotation, skipping", file=sys.stderr)
        del added[bib_id]
    path.write_text("\n".join(out), encoding="utf-8")
    return {bib_id: {k: sorted(v) for k, v in kinds.items() if v} for bib_id, kinds in added.items()}


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
        help="Add proposed links to informs_json in schema/bibliography.yaml. Only adds; never removes.",
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
