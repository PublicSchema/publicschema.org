#!/usr/bin/env python3
"""Seed the PublicSchema metric catalog from the DHS Program indicators API.

Fetches all indicator definitions from the DHS API, applies a relevance filter
(household characteristics and SP-adjacent categories), and writes
schema/metric_catalog/dhs_household.yaml with one Metric entry per indicator.

Caching: the indicator list is saved to build/cache/dhs/indicators.json and
reused if the cache file is newer than 30 days.
"""

import json
import re
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
CACHE_DIR = Path(__file__).parent / "cache" / "dhs"
OUT_FILE = REPO_ROOT / "schema" / "metric_catalog" / "dhs_household.yaml"
OUT_CONCEPT_FILE = REPO_ROOT / "schema" / "concept_schemes" / "dhs_household.yaml"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_CONCEPT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Concept URI minting
# Concepts are auto-derived from DHS Level2 bucket names via deterministic
# slugification. This is mechanical grouping at Level2 granularity, NOT a
# curated SKOS concept scheme. Some Level2 buckets (notably "Age of population"
# with 29 indicators) contain multiple underlying concepts and should be
# reviewed before treating these as authoritative. See
# docs/follow-ups/dhs-concept-scheme.md for grouping and stability limits.
# ---------------------------------------------------------------------------
CONCEPT_URI_PREFIX = "publicschema:concept/dhs/"
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify_level2(level2: str) -> str:
    """Deterministic slug for a DHS Level2 bucket label.

    Lowercase, replace non-alphanumeric runs with underscore, strip leading
    and trailing underscores. Stable across runs given the same Level2 string.
    """
    if not level2:
        raise ValueError("Cannot slugify empty Level2 value")
    slug = _NON_ALNUM.sub("_", level2.lower()).strip("_")
    if not slug:
        raise ValueError(f"Slugification produced empty string for Level2={level2!r}")
    return slug


def level2_to_concept_uri(level2: str) -> str:
    return CONCEPT_URI_PREFIX + slugify_level2(level2)

# ---------------------------------------------------------------------------
# DHS API
# ---------------------------------------------------------------------------
DHS_INDICATORS_URL = (
    "https://api.dhsprogram.com/rest/dhs/indicators"
    "?returnFields=IndicatorId,Label,Definition,Denominator,MeasurementType"
    ",Level1,Level2,Level3,IndicatorOrder&f=json&perPage=5000"
)
CACHE_FILE = CACHE_DIR / "indicators.json"
CACHE_MAX_AGE_DAYS = 30
USER_AGENT = "Mozilla/5.0 (PublicSchema metric seed; https://publicschema.org)"

# ---------------------------------------------------------------------------
# Relevance filter
# Each entry is (Level1, Level2_or_None).
# None for Level2 means "keep all Level2 sub-buckets under this Level1".
# ---------------------------------------------------------------------------
RELEVANCE_FILTER: list[tuple[str, str | None]] = [
    # Core target: all household characteristics sub-buckets
    ("Household Characteristics", None),
    # Background characteristics = dimension-equivalent breakdowns (residence, region, etc.)
    ("Survey Characteristics", "Background characteristics"),
    # Education attainment relates to PS Person.education_level
    ("Education", "Educational attainment of the household population"),
    # Asset ownership / intra-HH agency
    ("Women's Empowerment", "House ownership and documentation"),
    ("Women's Empowerment", "Participation in decision making: Major household purchases"),
    # HH-level dwelling sanitation characteristics
    ("Water and Sanitation", "Household sanitation facilities"),
    ("Water and Sanitation", "Management of household excreta"),
]

# ---------------------------------------------------------------------------
# MeasurementType → value_type mapping
# Derived directly from the DHS API field — no inference beyond this table.
# ---------------------------------------------------------------------------
MEASUREMENT_TYPE_MAP: dict[str, str] = {
    "Percent": "proportion",
    "Percentage": "proportion",  # in case the API ever uses the long form
    "Mean": "ratio",
    "Median": "ratio",
    "Number": "count",
    "Rate": "ratio",
    "Ratio": "ratio",
}

# Level3 values that indicate sex disaggregation in the data
SEX_LEVEL3_VALUES = {"Women", "Men", "Women and Men"}

# ---------------------------------------------------------------------------
# HTTP fetch with caching
# ---------------------------------------------------------------------------


def _fetch_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_cached_indicators() -> list[dict]:
    """Return indicators from disk cache or fetch from DHS API."""
    if CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_MAX_AGE_DAYS * 86400:
            print(f"  cache hit: indicators.json (age {age/3600:.1f}h)")
            raw = CACHE_FILE.read_bytes()
        else:
            print(f"  refetch (stale cache, age {age/86400:.0f}d): indicators.json")
            raw = _fetch_url(DHS_INDICATORS_URL)
            CACHE_FILE.write_bytes(raw)
    else:
        print("  refetch (no cache): indicators.json")
        raw = _fetch_url(DHS_INDICATORS_URL)
        CACHE_FILE.write_bytes(raw)

    payload = json.loads(raw)
    if "Data" not in payload:
        raise ValueError(f"Unexpected DHS API response shape — missing 'Data' key. Keys: {list(payload.keys())}")
    records = payload["Data"]
    if not isinstance(records, list):
        raise TypeError(f"DHS API 'Data' is not a list — got {type(records).__name__}")
    return records


# ---------------------------------------------------------------------------
# Relevance filter
# ---------------------------------------------------------------------------


def is_relevant(record: dict) -> bool:
    """Return True if the record falls under a kept Level1/Level2 bucket."""
    l1 = record.get("Level1", "")
    l2 = record.get("Level2", "")
    for fl1, fl2 in RELEVANCE_FILTER:
        if fl1 == l1:
            if fl2 is None or fl2 == l2:
                return True
    return False


# ---------------------------------------------------------------------------
# Field derivation
# ---------------------------------------------------------------------------


def derive_value_type(record: dict) -> tuple[str | None, str | None]:
    """Return (value_type, todo_comment). Exactly one will be non-None."""
    mt = record.get("MeasurementType", "")
    vt = MEASUREMENT_TYPE_MAP.get(mt)
    if vt is not None:
        return vt, None
    indicator_id = record.get("IndicatorId", "?")
    return None, f"# TODO: unmapped MeasurementType \"{mt}\" for {indicator_id}"


def has_sex_dimension(record: dict) -> bool:
    """Return True if Level3 exactly names a sex-disaggregated population."""
    l3 = record.get("Level3", "")
    if l3 in SEX_LEVEL3_VALUES:
        return True
    if "by sex" in l3.lower():
        return True
    return False


# ---------------------------------------------------------------------------
# YAML serialisation helpers (no ruamel dependency — manual emit like ILO converter)
# ---------------------------------------------------------------------------


def _yaml_str(s: str) -> str:
    """Return a safely quoted YAML string value."""
    if any(c in s for c in (":", "#", "\n", '"', "'")):
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return f'"{s}"'


# ---------------------------------------------------------------------------
# Hand-authored MetricCalculation blocks.
#
# Keyed by DHS IndicatorId. The value is the raw YAML body for the
# `calculation:` slot, with NO leading indentation on the first line — the
# converter prefixes every line with the 4-space indent required to live under
# a metric entry.
#
# Convention (first calculation blocks authored against PublicSchema, so a
# convention is being set here — revisit when more accrue):
#   - Expression language: application/sql. The SQL targets a PublicSchema-
#     shaped relational model where class names are tables and slot names are
#     columns. Joins traverse declared inverse/back-pointer slots.
#   - PS class references use the spec-defined ${ps.<Class>} placeholder
#     (metrics-spec.md, "Criteria language"). The executor resolves each
#     placeholder against its warehouse schema, so bare table names that
#     happen to collide with PS class names are avoided.
#   - `scoring: proportion` requires populations [initial-population,
#     denominator, numerator]; `scoring: continuous-variable` requires
#     [initial-population, measure-population, measure-observation]. For
#     these DHS metrics the initial-population is the universe of households
#     and matches the denominator (proportion) or measure-population
#     (continuous-variable).
#   - measure-observation in continuous-variable scoring takes `:subject_id`,
#     a bind variable resolved by the engine to the current measure-population
#     row. This avoids the FHIR Measure ambiguity around per-subject evaluation
#     semantics; the engine is expected to evaluate the SELECT once per subject
#     with `:subject_id` bound.
#   - Household members are reached via GroupMembership (Household has no
#     `members` slot; `head_of_household` is encoded as a GroupMembership with
#     role = 'head'). Joins filter on `gm.is_active = true` so historical
#     memberships do not pollute current headship. SELECT DISTINCT on the
#     numerator guards against multi-active-head data quality issues.
# ---------------------------------------------------------------------------
HAND_AUTHORED_CALCULATIONS: dict[str, str] = {
    "HC_MEMB_H_MNM": """\
calculation:
  scoring: continuous-variable
  subject_class: publicschema:Household
  populations:
    - population_type: initial-population
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: measure-population
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: measure-observation
      language: application/sql
      criteria: "SELECT member_count FROM ${ps.Household} WHERE id = :subject_id"
  rate_aggregation: average""",

    "HC_HHHD_H_FEM": """\
calculation:
  scoring: proportion
  subject_class: publicschema:Household
  populations:
    - population_type: initial-population
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: denominator
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: numerator
      language: application/sql
      criteria: |
        SELECT DISTINCT h.id
        FROM ${ps.Household} h
        JOIN ${ps.GroupMembership} gm ON gm.group = h.id
        JOIN ${ps.Person} p ON p.id = gm.person
        WHERE gm.role = 'head'
          AND gm.is_active = true
          AND p.sex = 'female'""",

    "HC_HHHD_H_MAL": """\
calculation:
  scoring: proportion
  subject_class: publicschema:Household
  populations:
    - population_type: initial-population
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: denominator
      language: application/sql
      criteria: "SELECT id FROM ${ps.Household}"
    - population_type: numerator
      language: application/sql
      criteria: |
        SELECT DISTINCT h.id
        FROM ${ps.Household} h
        JOIN ${ps.GroupMembership} gm ON gm.group = h.id
        JOIN ${ps.Person} p ON p.id = gm.person
        WHERE gm.role = 'head'
          AND gm.is_active = true
          AND p.sex = 'male'""",
}


def render_metric_entry(record: dict) -> list[str]:
    """Return lines for one metric YAML entry."""
    indicator_id = record.get("IndicatorId")
    if not indicator_id:
        raise ValueError(f"Record missing IndicatorId: {record!r}")
    label = record.get("Label")
    if label is None:
        raise ValueError(f"Record {indicator_id} missing Label")

    definition = record.get("Definition") or ""
    level2 = record.get("Level2") or ""

    metric_id = indicator_id.lower()

    lines: list[str] = []

    # Leading provenance comment
    lines.append(f"  # DHS indicator: {indicator_id}")
    lines.append(f"  # Level1: {record.get('Level1', '')} / Level2: {level2}")
    lines.append(f"  {metric_id}:")

    # title
    lines.append(f"    title: {_yaml_str(label)}")

    # Translations intentionally omitted — DHS source is English-only
    lines.append("    # TODO: DHS source is English-only; translations require separate authority")

    # description
    if definition.strip():
        lines.append(f"    description: {_yaml_str(definition.strip())}")
    else:
        lines.append(f"    # TODO: Definition missing in DHS API for {indicator_id}")

    # value_type
    vt, vt_todo = derive_value_type(record)
    if vt is not None:
        lines.append(f"    value_type: {vt}")
    else:
        lines.append(f"    {vt_todo}")

    # decimals (DHS standard reporting precision)
    lines.append("    decimals: 1")

    # topic — only assignable if Level2 contains "coverage" (rare in DHS)
    if "coverage" in level2.lower():
        lines.append("    topic: coverage")
    else:
        lines.append(f"    # TODO: map Level2 '{level2}' to MetricTopic")

    # concept_uri — auto-minted from DHS Level2 bucket (see concept scheme file)
    if level2:
        lines.append(f"    concept_uri: {level2_to_concept_uri(level2)}")
    else:
        lines.append(f"    # TODO: missing Level2 for {indicator_id}; cannot mint concept_uri")

    # dimensions
    lines.append("    dimensions:")
    lines.append("      - publicschema:dim/ref_area")
    lines.append("      - publicschema:dim/time_period")
    if has_sex_dimension(record):
        lines.append("      - publicschema:dim/sex")

    # calculation (only for hand-authored indicators)
    if indicator_id in HAND_AUTHORED_CALCULATIONS:
        for ln in HAND_AUTHORED_CALCULATIONS[indicator_id].splitlines():
            lines.append(f"    {ln}" if ln else "")

    # aligns_with
    lines.append("    aligns_with:")
    lines.append(f'      - "https://api.dhsprogram.com/rest/dhs/indicators/{indicator_id}"')
    lines.append("      # TODO: DHS technical doc PDF")

    lines.append("    core: true")
    lines.append('    version: "1.0.0"')
    lines.append("    status: bibo:draft")

    return lines


# ---------------------------------------------------------------------------
# dimensions_referenced and attributes_referenced builders
# ---------------------------------------------------------------------------


def build_references_section(kept: list[dict]) -> tuple[dict, dict]:
    """Collect all referenced dimension URIs with origin notes."""
    dim_refs: dict[str, str] = {
        "publicschema:dim/ref_area": "DHS: country/region of data collection",
        "publicschema:dim/time_period": "DHS: survey reference period",
    }
    # Add sex dimension if any metric uses it
    if any(has_sex_dimension(r) for r in kept):
        dim_refs["publicschema:dim/sex"] = "DHS Level3 sex disaggregation (Women / Men / Women and Men)"

    attr_refs: dict[str, str] = {}

    return dict(sorted(dim_refs.items())), dict(sorted(attr_refs.items()))


# ---------------------------------------------------------------------------
# Concept scheme builder
# ---------------------------------------------------------------------------


# Level2 buckets known to contain multiple underlying concepts. Flagged in the
# concept scheme file so a curation pass can split them later.
LIKELY_MIXED_LEVEL2 = {
    "Age of population",  # spans many age bands, treated as one bucket
    "Educational attainment of the household population",  # attainment levels + by-sex
    "Background characteristics",  # residence + region + age + wealth
    "Household sanitation facilities",  # facility type + sharing + improved-status
    "Children's living arrangements and orphanhood",
    "Children 10-14 living arrangements and orphanhood",
    "Agricultural ownership",  # land vs farm animals are distinct concepts
    "Clean fuels and technologies",  # clean-fuel use for cooking, heating, lighting bundled
    "Household effects",  # asset-index components (radio, TV, phone, fridge, ...) under one label
    "House ownership and documentation",  # ownership status and title-deed status are independent
    "Lighting fuel or technology",  # Level2 name itself bundles fuel and technology
    "Older age persons",  # HH composition wrt elders, non-nuclear families, and de jure 65+ pop
}


def build_concept_scheme(kept: list[dict]) -> list[dict]:
    """One entry per distinct (Level1, Level2) bucket present in kept records."""
    by_slug: dict[str, dict] = {}
    for r in kept:
        level2 = r.get("Level2") or ""
        if not level2:
            continue
        slug = slugify_level2(level2)
        entry = by_slug.setdefault(
            slug,
            {
                "slug": slug,
                "uri": CONCEPT_URI_PREFIX + slug,
                "label": level2,
                "source_level1": r.get("Level1") or "",
                "source_level2": level2,
                "metric_count": 0,
                "likely_mixed": level2 in LIKELY_MIXED_LEVEL2,
            },
        )
        entry["metric_count"] += 1
    return sorted(by_slug.values(), key=lambda x: x["slug"])


def write_concept_scheme(concepts: list[dict], timestamp: str, total_indicators: int) -> None:
    """Emit schema/concept_schemes/dhs_household.yaml."""
    lines: list[str] = []
    lines.append("# DHS Program — concept scheme for the household indicator metric catalog.")
    lines.append("#")
    lines.append("# Generated by build/seed_metrics_from_dhs_api.py.")
    lines.append("# Concepts are auto-minted from DHS Level2 buckets by deterministic")
    lines.append("# slugification. This is MECHANICAL GROUPING, not a curated SKOS scheme.")
    lines.append("# Each concept_uri groups all metrics in the same DHS Level2 bucket.")
    lines.append("#")
    lines.append("# Entries with `likely_mixed: true` are buckets known to contain multiple")
    lines.append("# underlying concepts and need a curation pass before being treated as")
    lines.append("# authoritative. See docs/follow-ups/dhs-concept-scheme.md.")
    lines.append("#")
    lines.append(f"# Retrieved at: {timestamp}")
    lines.append(f"# Concept count: {len(concepts)} (one per distinct Level2 bucket)")
    lines.append(f"# Spans {total_indicators} kept DHS indicators")
    lines.append("")
    lines.append("id: dhs_household_concepts")
    lines.append('title: DHS Program — Household concept scheme (auto-minted from Level2 buckets)')
    lines.append("description: |")
    lines.append("  Concept URIs auto-minted from DHS Level2 bucket names. Each concept groups")
    lines.append("  every Metric in the corresponding bucket; concept_uri values on Metric")
    lines.append("  entries in schema/metric_catalog/dhs_household.yaml reference these URIs.")
    lines.append("  This is mechanical Level2-granularity grouping, not a curated SKOS scheme.")
    lines.append('source: "ICF, The DHS Program — DHS API Level2 buckets"')
    lines.append('license: "CC-BY-4.0 (PublicSchema-minted URIs; underlying Level2 labels from DHS)"')
    lines.append("")
    lines.append("concepts:")
    for c in concepts:
        lines.append("")
        lines.append(f"  {c['slug']}:")
        lines.append(f"    uri: {c['uri']}")
        safe_label = c["label"].replace('"', '\\"')
        lines.append(f'    label: "{safe_label}"')
        safe_l1 = c["source_level1"].replace('"', '\\"')
        lines.append(f'    source_level1: "{safe_l1}"')
        safe_l2 = c["source_level2"].replace('"', '\\"')
        lines.append(f'    source_level2: "{safe_l2}"')
        lines.append(f"    metric_count: {c['metric_count']}")
        lines.append('    mint_method: "Level2 slugification"')
        if c["likely_mixed"]:
            lines.append("    likely_mixed: true  # contains multiple underlying concepts; needs curation")
    lines.append("")
    OUT_CONCEPT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(concepts)} concept entries to {OUT_CONCEPT_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Fetch indicators
    print("Fetching DHS indicator definitions …")
    all_records = fetch_cached_indicators()
    print(f"  Total indicators in DHS API: {len(all_records)}")

    # Validate required keys on every record
    required_keys = {"IndicatorId", "Label", "MeasurementType", "Level1", "Level2"}
    for rec in all_records:
        missing = required_keys - rec.keys()
        if missing:
            raise ValueError(
                f"DHS API record missing required keys {missing}: {rec!r}"
            )

    # 2. Apply relevance filter
    kept = [r for r in all_records if is_relevant(r)]
    dropped_count = len(all_records) - len(kept)
    print(f"  Kept: {len(kept)}, Dropped: {dropped_count}")

    # 3. Sort by IndicatorOrder (DHS canonical), fall back to IndicatorId
    kept.sort(key=lambda r: (r.get("IndicatorOrder") or 0, r.get("IndicatorId") or ""))

    # 4. Print breakdown stats
    bucket_counts: Counter = Counter(
        (r.get("Level1", ""), r.get("Level2", "")) for r in kept
    )
    print("\nIndicators kept by (Level1, Level2):")
    for (l1, l2), cnt in sorted(bucket_counts.items()):
        print(f"  {l1} / {l2}: {cnt}")

    mt_counts: Counter = Counter(r.get("MeasurementType", "") for r in kept)
    vt_dist: Counter = Counter()
    todo_mt: set = set()
    for r in kept:
        vt, _ = derive_value_type(r)
        if vt is not None:
            vt_dist[vt] += 1
        else:
            vt_dist["TODO"] += 1
            todo_mt.add(r.get("MeasurementType", ""))

    print("\nMeasurementType distribution (kept):")
    for k, v in sorted(mt_counts.items()):
        print(f"  {k}: {v}")
    print("\nvalue_type distribution:")
    for k, v in sorted(vt_dist.items()):
        print(f"  {k}: {v}")
    if todo_mt:
        print(f"  Unmapped MeasurementType values: {sorted(todo_mt)}")

    # 5. Build reference sections
    dim_refs, _ = build_references_section(kept)

    # 6. Build filter rules as a readable string for the file header
    filter_rules_lines = [
        "# Relevance filter rules (encoded in RELEVANCE_FILTER list in the script):",
        "#   Level1 = 'Household Characteristics' — all Level2 sub-buckets",
        "#   Level1 = 'Survey Characteristics', Level2 = 'Background characteristics'",
        "#   Level1 = 'Education', Level2 = 'Educational attainment of the household population'",
        "#   Level1 = 'Women's Empowerment', Level2 = 'House ownership and documentation'",
        "#   Level1 = 'Women's Empowerment', Level2 = 'Participation in decision making: Major household purchases'",
        "#   Level1 = 'Water and Sanitation', Level2 = 'Household sanitation facilities'",
        "#   Level1 = 'Water and Sanitation', Level2 = 'Management of household excreta'",
        "# DROP: all other Level1/Level2 buckets (HIV, malaria, fertility, anthropometry, etc.)",
    ]

    # 7. Render YAML
    out_lines: list[str] = []

    # File header
    out_lines.append("# DHS Program household indicator metric catalog seed.")
    out_lines.append("#")
    out_lines.append("# Generated by build/seed_metrics_from_dhs_api.py.")
    out_lines.append(f"# Source: ICF, The DHS Program — DHS API ({DHS_INDICATORS_URL[:80]}...)")
    out_lines.append(f"# Retrieved at: {timestamp}")
    out_lines.append(f"# Indicators kept: {len(kept)} of {len(all_records)} total")
    out_lines.append("# License: DHS indicator definitions are publicly available;")
    out_lines.append("#   data downloads require DHS Program registration (https://dhsprogram.com)")
    out_lines.append("# Attribution: ICF, The DHS Program. DHS Indicators.")
    out_lines.append("#   https://api.dhsprogram.com/rest/dhs/indicators")
    out_lines.append("#")
    out_lines.extend(filter_rules_lines)
    out_lines.append("#")
    out_lines.append("# MeasurementType → value_type mapping (from MEASUREMENT_TYPE_MAP in script):")
    out_lines.append("#   Percent / Percentage → proportion")
    out_lines.append("#   Mean, Median, Rate, Ratio → ratio")
    out_lines.append("#   Number → count")
    out_lines.append("#")
    out_lines.append("# sex dimension added only when Level3 is exactly:")
    out_lines.append('#   "Women", "Men", "Women and Men", or contains "by sex".')
    out_lines.append("")
    out_lines.append("id: dhs_household_seed")
    out_lines.append("title: DHS Program — Household and SP-adjacent indicator seed metric catalog")
    out_lines.append("description: |")
    out_lines.append("  Auto-generated seed from the ICF DHS Program indicators API, filtered to")
    out_lines.append("  household characteristics and social-protection-adjacent categories.")
    out_lines.append("  Selection rule: indicators must be derivable from PublicSchema household-level")
    out_lines.append("  record data — Household.dwelling_type, Household.cooking_fuel,")
    out_lines.append("  Household.electricity_access, Household.floor_material,")
    out_lines.append("  Person.education_level, and asset/empowerment slots. Clinical indicators")
    out_lines.append("  (HIV, malaria, fertility, anthropometry, immunisation) are excluded.")
    out_lines.append("  Labels and definitions are English-only as provided by the DHS API.")
    out_lines.append("  concept_uri values are auto-minted per DHS Level2 bucket (see")
    out_lines.append("  schema/concept_schemes/dhs_household.yaml); this is mechanical grouping,")
    out_lines.append("  not a curated SKOS scheme — see docs/follow-ups/dhs-concept-scheme.md.")
    out_lines.append("  Topic mappings and translations are out of scope for this seed and tracked")
    out_lines.append("  as TODOs. Calculation blocks are hand-authored for a small number of")
    out_lines.append("  indicators (see HAND_AUTHORED_CALCULATIONS in the converter); the rest carry")
    out_lines.append("  no calculation block.")
    out_lines.append('source: "ICF, The DHS Program — DHS API"')
    out_lines.append('license: "DHS indicator definitions are publicly available; data downloads require DHS Program registration"')
    out_lines.append("")
    out_lines.append("metrics:")

    # Metric entries
    for record in kept:
        out_lines.append("")
        out_lines.extend(render_metric_entry(record))

    # dimensions_referenced section
    out_lines.append("")
    out_lines.append("dimensions_referenced:")
    for uri, desc in dim_refs.items():
        safe_desc = desc.replace('"', '\\"')
        out_lines.append(f'  {uri}: "{safe_desc}"')

    # attributes_referenced section (empty for DHS — no structured attribute list)
    out_lines.append("")
    out_lines.append("attributes_referenced: {}")
    out_lines.append("")

    # 8. Write metric catalog
    OUT_FILE.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\nWrote {len(kept)} metric entries to {OUT_FILE}")

    # 9. Write sibling concept scheme
    concepts = build_concept_scheme(kept)
    write_concept_scheme(concepts, timestamp, len(kept))
    mixed_count = sum(1 for c in concepts if c["likely_mixed"])

    # TODO summary
    todo_translations = len(kept)  # every metric has a translations TODO
    todo_topic = sum(
        1 for r in kept if "coverage" not in (r.get("Level2") or "").lower()
    )
    todo_definition = sum(
        1 for r in kept if not (r.get("Definition") or "").strip()
    )
    todo_vt = vt_dist.get("TODO", 0)

    print("\nTODO summary:")
    print(f"  translations (all metrics, English-only source): {todo_translations}")
    print(f"  topic mappings needed: {todo_topic}")
    print(f"  concept curation: {len(concepts)} concepts minted, {mixed_count} flagged as likely_mixed")
    if todo_definition:
        print(f"  missing Definition in DHS API: {todo_definition}")
    if todo_vt:
        print(f"  unmapped MeasurementType (value_type TODO): {todo_vt}")


if __name__ == "__main__":
    main()
