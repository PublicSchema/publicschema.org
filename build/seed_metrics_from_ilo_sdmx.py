#!/usr/bin/env python3
"""Seed the PublicSchema metric catalog from the ILO SDMX 2.1 dataflow registry.

Fetches an allowlist of SDG dataflows that are relevant to social protection
delivery (excludes macro and country-level-qualitative indicators), parses each
DSD for dimensions and attributes, and writes schema/metric_catalog/ilo_sdg.yaml.

Caching: responses are saved to build/cache/ilo_sdmx/<dataflow_id>.xml and
reused if the cache file is newer than 30 days.
"""

import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
CACHE_DIR = Path(__file__).parent / "cache" / "ilo_sdmx"
OUT_FILE = REPO_ROOT / "schema" / "metric_catalog" / "ilo_sdg.yaml"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# SDMX API
# ---------------------------------------------------------------------------
SDMX_BASE = "https://sdmx.ilo.org/rest"
DATAFLOW_LIST_URL = f"{SDMX_BASE}/dataflow/ILO?detail=allstubs"
DATAFLOW_DETAIL_URL = f"{SDMX_BASE}/dataflow/ILO/{{id}}?references=descendants"

ACCEPT_HEADER = "application/vnd.sdmx.structure+xml;version=2.1"
USER_AGENT = "Mozilla/5.0"
CACHE_MAX_AGE_DAYS = 30

# Allowlist of ILO SDG dataflows kept in the PublicSchema seed.
# Selection rule: indicator must be derivable (now or with a small slot addition)
# from PublicSchema record-level data — i.e. Person.employment_status,
# Person.occupation, Person.industry, Enrollment in Program, etc.
# Excluded: macro indicators (8.2.1 GDP/worker, 8.5.1 wages, 10.4.1 income share),
# country-level qualitative ratings (8.8.2, 8.b.1), and injury registry (8.8.1)
# which is outside SP delivery scope.
RELEVANT_SDG_DATAFLOWS = frozenset({
    "DF_SDG_0111_SEX_AGE_RT",  # 1.1.1 working poverty rate by sex/age
    "DF_SDG_0131_SEX_SOC_RT",  # 1.3.1 SP coverage by sex and SP function
    "DF_SDG_0552_NOC_RT",      # 5.5.2 women in senior/middle mgmt (18th ICLS)
    "DF_SDG_B552_NOC_RT",      # 5.5.2 women in senior/middle mgmt (19th ICLS)
    "DF_SDG_T552_NOC_RT",      # 5.5.2 women in managerial positions (18th ICLS)
    "DF_SDG_U552_NOC_RT",      # 5.5.2 women in managerial positions (19th ICLS)
    "DF_SDG_0831_SEX_ECO_RT",  # 8.3.1 informal employment (18th ICLS)
    "DF_SDG_B831_SEX_ECO_RT",  # 8.3.1 informal employment (19th ICLS)
    "DF_SDG_0852_SEX_AGE_RT",  # 8.5.2 unemployment rate by sex/age (18th ICLS)
    "DF_SDG_B852_SEX_AGE_RT",  # 8.5.2 unemployment rate by sex/age (19th ICLS)
    "DF_SDG_0852_SEX_DSB_RT",  # 8.5.2 unemployment rate by sex/disability (18th ICLS)
    "DF_SDG_B852_SEX_DSB_RT",  # 8.5.2 unemployment rate by sex/disability (19th ICLS)
    "DF_SDG_0861_SEX_RT",      # 8.6.1 NEET by sex
    "DF_SDG_A871_SEX_AGE_RT",  # 8.7.1 child labour - economic activity
    "DF_SDG_B871_SEX_AGE_RT",  # 8.7.1 child labour - economic activity + chores
    "DF_SDG_0922_NOC_RT",      # 9.2.2 manufacturing employment share (18th ICLS)
    "DF_SDG_B922_NOC_RT",      # 9.2.2 manufacturing employment share (19th ICLS)
})

# ---------------------------------------------------------------------------
# XML namespaces
# ---------------------------------------------------------------------------
NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

# ---------------------------------------------------------------------------
# HTTP fetch with caching
# ---------------------------------------------------------------------------

def _fetch_url(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"Accept": ACCEPT_HEADER, "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_cached(dataflow_id: str, url: str) -> bytes:
    """Return cached bytes or fetch from URL, caching the result."""
    cache_file = CACHE_DIR / f"{dataflow_id}.xml"
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_MAX_AGE_DAYS * 86400:
            print(f"  cache hit: {dataflow_id}")
            return cache_file.read_bytes()
        print(f"  refetch (stale cache): {dataflow_id}")
    else:
        print(f"  refetch (no cache): {dataflow_id}")
    data = _fetch_url(url)
    cache_file.write_bytes(data)
    return data


# ---------------------------------------------------------------------------
# SDMX XML parsers
# ---------------------------------------------------------------------------

def _text(elem, path: str, lang: str) -> str | None:
    """Find a common:Name or common:Description with the given xml:lang."""
    for node in elem.findall(path, NS):
        if node.get("{http://www.w3.org/XML/1998/namespace}lang") == lang:
            return node.text
    return None


def parse_dataflow_stubs(xml_bytes: bytes) -> list[dict]:
    """Parse the dataflow stubs response; return list of dataflow dicts."""
    root = ET.fromstring(xml_bytes)
    structs = root.find("message:Structures", NS)
    if structs is None:
        raise ValueError("SDMX response missing <message:Structures>")
    dfs_el = structs.find("structure:Dataflows", NS)
    if dfs_el is None:
        raise ValueError("SDMX response missing <structure:Dataflows>")
    results = []
    for df in dfs_el.findall("structure:Dataflow", NS):
        df_id = df.get("id")
        version = df.get("version", "1.0")
        name_en = _text(df, "common:Name", "en") or ""
        name_es = _text(df, "common:Name", "es") or ""
        name_fr = _text(df, "common:Name", "fr") or ""
        # DSD reference
        struct_el = df.find("structure:Structure", NS)
        ref = struct_el.find("Ref") if struct_el is not None else None
        dsd_id = ref.get("id") if ref is not None else None
        dsd_version = ref.get("version", "1.0") if ref is not None else "1.0"
        results.append({
            "id": df_id,
            "version": version,
            "name_en": name_en,
            "name_es": name_es,
            "name_fr": name_fr,
            "dsd_id": dsd_id,
            "dsd_version": dsd_version,
        })
    return results


def parse_full_dataflow(xml_bytes: bytes, dataflow_id: str) -> dict:
    """Parse the full dataflow+descendants response; return DSD info."""
    root = ET.fromstring(xml_bytes)
    structs = root.find("message:Structures", NS)
    if structs is None:
        raise ValueError(f"SDMX response for {dataflow_id} missing <message:Structures>")

    # Re-read dataflow names from the full response (canonical)
    dfs_el = structs.find("structure:Dataflows", NS)
    if dfs_el is None:
        raise ValueError(f"SDMX response for {dataflow_id} missing <structure:Dataflows>")
    df_el = None
    df_version = "1.0"
    name_en = name_es = name_fr = ""
    for df in dfs_el.findall("structure:Dataflow", NS):
        if df.get("id") == dataflow_id:
            df_el = df
            df_version = df.get("version", "1.0")
            name_en = _text(df, "common:Name", "en") or ""
            name_es = _text(df, "common:Name", "es") or ""
            name_fr = _text(df, "common:Name", "fr") or ""
            break

    # DSD reference
    dsd_id = dsd_version = None
    if df_el is not None:
        struct_el = df_el.find("structure:Structure", NS)
        ref = struct_el.find("Ref") if struct_el is not None else None
        if ref is not None:
            dsd_id = ref.get("id")
            dsd_version = ref.get("version", "1.0")

    # Parse DSD
    dsd_list_el = structs.find("structure:DataStructures", NS)
    dimensions = []   # list of {id, position, concept_id, codelist_id}
    time_dimension = None
    attributes = []
    primary_measure = None

    if dsd_list_el is not None:
        for dsd_el in dsd_list_el.findall("structure:DataStructure", NS):
            if dsd_el.get("id") != dsd_id:
                continue
            comps = dsd_el.find("structure:DataStructureComponents", NS)
            if comps is None:
                break

            dim_list_el = comps.find("structure:DimensionList", NS)
            if dim_list_el is not None:
                for dim_el in dim_list_el.findall("structure:Dimension", NS):
                    pos = int(dim_el.get("position", 0))
                    did = dim_el.get("id")
                    ci = dim_el.find("structure:ConceptIdentity", NS)
                    concept_ref = ci.find("Ref") if ci is not None else None
                    lr = dim_el.find("structure:LocalRepresentation", NS)
                    enum_el = lr.find("structure:Enumeration", NS) if lr is not None else None
                    cl_ref = enum_el.find("Ref") if enum_el is not None else None
                    dimensions.append({
                        "id": did,
                        "position": pos,
                        "concept_id": concept_ref.get("id") if concept_ref is not None else None,
                        "concept_scheme": concept_ref.get("maintainableParentID") if concept_ref is not None else None,
                        "codelist_id": cl_ref.get("id") if cl_ref is not None else None,
                    })
                td_el = dim_list_el.find("structure:TimeDimension", NS)
                if td_el is not None:
                    td_pos = int(td_el.get("position", 9999))
                    time_dimension = {"id": td_el.get("id"), "position": td_pos}

            attr_list_el = comps.find("structure:AttributeList", NS)
            if attr_list_el is not None:
                for attr_el in attr_list_el.findall("structure:Attribute", NS):
                    attributes.append(attr_el.get("id"))

            meas_list_el = comps.find("structure:MeasureList", NS)
            if meas_list_el is not None:
                pm_el = meas_list_el.find("structure:PrimaryMeasure", NS)
                if pm_el is not None:
                    primary_measure = pm_el.get("id")
            break

    # Sort dimensions by position
    dimensions.sort(key=lambda d: d["position"])

    return {
        "df_id": dataflow_id,
        "df_version": df_version,
        "name_en": name_en,
        "name_es": name_es,
        "name_fr": name_fr,
        "dsd_id": dsd_id,
        "dsd_version": dsd_version,
        "dimensions": dimensions,
        "time_dimension": time_dimension,
        "attributes": attributes,
        "primary_measure": primary_measure,
    }


# ---------------------------------------------------------------------------
# Field derivation helpers
# ---------------------------------------------------------------------------

# Allowed attribute ids (emit others with TODO comment)
ALLOWED_ATTRS = {"OBS_STATUS", "UNIT_MEASURE", "UNIT_MULT", "UNIT_MEASURE_TYPE", "CONF_STATUS"}

# Suffix → value_type mapping
SUFFIX_VALUE_TYPE = {
    "_RT": "proportion",
    "_NB": "count",
    "_NO": "count",
    "_PR": "proportion",
}

# SDG indicator prefix → topic mapping
# Strip "DF_" then check prefix (e.g. "SDG_013")
PREFIX_TOPIC = {
    "SDG_013": "coverage",
    "SDG_038": "coverage",
}


def derive_value_type(df_id: str) -> tuple[str | None, str | None]:
    """Return (value_type, todo_comment). One of them will be None."""
    bare = df_id[3:] if df_id.startswith("DF_") else df_id  # strip DF_
    for suffix, vt in SUFFIX_VALUE_TYPE.items():
        if bare.endswith(suffix):
            return vt, None
    # Find the actual suffix (last segment after final _)
    parts = bare.rsplit("_", 1)
    actual_suffix = f"_{parts[-1]}" if len(parts) == 2 else bare
    return None, f"# TODO: derive value_type for suffix {actual_suffix}"


def derive_topic(df_id: str) -> tuple[str | None, str | None]:
    """Return (topic, todo_comment). One of them will be None."""
    bare = df_id[3:] if df_id.startswith("DF_") else df_id
    for prefix, topic in PREFIX_TOPIC.items():
        if bare.startswith(prefix):
            return topic, None
    # Extract prefix up to 3rd segment: SDG_NNN
    parts = bare.split("_")
    if len(parts) >= 2:
        prefix = "_".join(parts[:2])
    else:
        prefix = bare
    return None, f"# TODO: map SDG indicator prefix {prefix} to MetricTopic"


def has_percent_in_title(name_en: str) -> bool:
    return "(%)" in name_en or "(per cent)" in name_en.lower()


# ---------------------------------------------------------------------------
# YAML serialisation helpers (no ruamel dependency — use stdlib + manual)
# ---------------------------------------------------------------------------

def _yaml_str(s: str) -> str:
    """Quote a string for YAML if it contains special chars."""
    # If it contains : # or starts with special chars, wrap in double quotes
    if any(c in s for c in (':', '#', '\n', '"', "'")):
        escaped = s.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return f'"{s}"'


def render_metric_entry(info: dict) -> list[str]:
    """Return lines for one metric YAML entry (no trailing newline)."""
    df_id = info["df_id"]
    df_version = info["df_version"]
    dsd_id = info["dsd_id"] or "UNKNOWN"
    dsd_version = info["dsd_version"] or "1.0"
    name_en = info["name_en"]
    name_es = info["name_es"]
    name_fr = info["name_fr"]
    dims = info["dimensions"]
    td = info["time_dimension"]
    attrs = info["attributes"]

    # Metric id: strip DF_ prefix, lowercase
    metric_id = df_id[3:].lower() if df_id.startswith("DF_") else df_id.lower()

    # Ordered dim ids for comment (DSD order)
    all_dim_ids = [d["id"] for d in dims]
    if td:
        all_dim_ids.append(td["id"])

    lines = []
    # Leading comments
    lines.append(f"  # ILO dataflow: {df_id} (v{df_version})")
    lines.append(f"  # DSD: {dsd_id} (v{dsd_version})")
    lines.append(f"  # Dimensions (DSD order): {', '.join(all_dim_ids)}")
    lines.append(f"  {metric_id}:")

    # title
    lines.append(f"    title: {_yaml_str(name_en)}")

    # annotations
    lines.append("    annotations:")
    lines.append(f"      label_es: {_yaml_str(name_es)}")
    lines.append(f"      label_fr: {_yaml_str(name_fr)}")
    lines.append(f"      description_es: {_yaml_str(name_es)}")
    lines.append(f"      description_fr: {_yaml_str(name_fr)}")

    # value_type
    vt, vt_todo = derive_value_type(df_id)
    if vt:
        lines.append(f"    value_type: {vt}")
    else:
        lines.append(f"    {vt_todo}")

    # unit
    if vt == "proportion":
        if has_percent_in_title(name_en):
            lines.append('    unit: "PT"')
        else:
            lines.append('    # TODO: derive unit — title does not contain (%); confirm UNIT_MEASURE from ILOSTAT')
    elif vt == "count":
        lines.append('    # TODO: derive unit from UNIT_MEASURE codelist')
    # else vt is None — already have a TODO above for value_type; skip unit

    # decimals
    if vt == "proportion":
        lines.append("    decimals: 1")

    # topic
    topic, topic_todo = derive_topic(df_id)
    if topic:
        lines.append(f"    topic: {topic}")
    else:
        lines.append(f"    {topic_todo}")

    # dimensions — skip MEASURE
    ps_dims = []
    for d in dims:
        if d["id"] == "MEASURE":
            continue
        ps_dims.append(f"publicschema:dim/{d['id'].lower()}")
    if td:
        ps_dims.append(f"publicschema:dim/{td['id'].lower()}")

    lines.append("    dimensions:")
    for d in ps_dims:
        lines.append(f"      - {d}")

    # attributes
    allowed_attrs_found = []
    extra_attrs = []
    for a in attrs:
        if a in ALLOWED_ATTRS:
            allowed_attrs_found.append(a)
        else:
            extra_attrs.append(a)

    lines.append("    attributes:")
    for a in allowed_attrs_found:
        lines.append(f"      - publicschema:attr/{a.lower()}")
    for a in extra_attrs:
        lines.append(f"      # TODO: non-standard attribute {a} — confirm whether to include")
        lines.append(f"      - publicschema:attr/{a.lower()}")

    # aligns_with
    lines.append("    aligns_with:")
    lines.append(f'      - "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=ILO:{df_id}({df_version})"')
    lines.append("      # TODO: UN SDG series URI")

    lines.append("    core: true")
    lines.append('    version: "1.0.0"')
    lines.append("    status: bibo:draft")

    return lines


# ---------------------------------------------------------------------------
# dimensions_referenced and attributes_referenced builders
# ---------------------------------------------------------------------------

def build_references_section(all_infos: list[dict]) -> tuple[dict, dict]:
    """Collect all dimension and attribute URIs with one-line origins."""
    dim_refs: dict[str, str] = {}
    attr_refs: dict[str, str] = {}

    for info in all_infos:
        for d in info["dimensions"]:
            if d["id"] == "MEASURE":
                continue
            uri = f"publicschema:dim/{d['id'].lower()}"
            if uri not in dim_refs:
                cl = d["codelist_id"] or "?"
                cs = d["concept_scheme"] or "?"
                dim_refs[uri] = f"ILO concept {d['id']} (ConceptScheme {cs}, Codelist {cl})"
        td = info["time_dimension"]
        if td:
            uri = f"publicschema:dim/{td['id'].lower()}"
            if uri not in dim_refs:
                dim_refs[uri] = "SDMX TimeDimension TIME_PERIOD"

        for a in info["attributes"]:
            uri = f"publicschema:attr/{a.lower()}"
            if uri not in attr_refs:
                attr_refs[uri] = f"ILO concept {a}"

    # Sort
    dim_refs = dict(sorted(dim_refs.items()))
    attr_refs = dict(sorted(attr_refs.items()))
    return dim_refs, attr_refs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Fetch dataflow stubs
    print("Fetching dataflow stubs list …")
    stubs_bytes = _fetch_url(DATAFLOW_LIST_URL)
    stubs = parse_dataflow_stubs(stubs_bytes)
    sdg_stubs = [s for s in stubs if s["id"] in RELEVANT_SDG_DATAFLOWS]

    found_ids = {s["id"] for s in sdg_stubs}
    missing = RELEVANT_SDG_DATAFLOWS - found_ids
    if missing:
        raise RuntimeError(
            f"Allowlisted dataflows not found in ILO registry: {sorted(missing)}"
        )
    count = len(sdg_stubs)
    expected = len(RELEVANT_SDG_DATAFLOWS)
    print(f"Found {count} of {expected} allowlisted SDG dataflows.")

    # 2. Fetch full detail per SDG dataflow (cached)
    all_infos = []
    for stub in sdg_stubs:
        df_id = stub["id"]
        url = DATAFLOW_DETAIL_URL.format(id=df_id)
        xml_bytes = fetch_cached(df_id, url)
        info = parse_full_dataflow(xml_bytes, df_id)
        all_infos.append(info)

    # Sort by metric id (strips DF_ prefix, lowercased)
    all_infos.sort(key=lambda x: x["df_id"][3:].lower() if x["df_id"].startswith("DF_") else x["df_id"].lower())

    # 3. Build references sections
    dim_refs, attr_refs = build_references_section(all_infos)

    # 4. Render YAML
    out_lines = []

    # File header
    out_lines.append("# ILO SDMX SDG metric catalog seed.")
    out_lines.append("#")
    out_lines.append("# Generated by build/seed_metrics_from_ilo_sdmx.py.")
    out_lines.append("# Source: ILO SDMX 2.1 registry (https://sdmx.ilo.org/rest/)")
    out_lines.append("# Filter: allowlist of SDG dataflows derivable (now or with a small")
    out_lines.append("# PublicSchema slot addition) from record-level PS data.")
    out_lines.append("# Excludes macro indicators (8.2.1 GDP/worker, 8.5.1 wages, 10.4.1 income share),")
    out_lines.append("# country-level qualitative (8.8.2, 8.b.1), and injury registry (8.8.1).")
    out_lines.append(f"# Retrieved at: {timestamp}")
    out_lines.append(f"# Indicator count: {count}")
    out_lines.append("# License: Reproduction of ILO material is permitted for non-commercial purposes per https://www.ilo.org/rights-and-permissions")
    out_lines.append("#")
    out_lines.append("# Calculation blocks are out of scope for this converter;")
    out_lines.append("# docs/metrics-spec.md line 310 prescribes hand-authoring for the derivable subset.")
    out_lines.append("")
    out_lines.append("id: ilo_sdg_seed")
    out_lines.append("title: ILO SDMX SDG indicators relevant to social protection — seed metric catalog")
    out_lines.append("description: |")
    out_lines.append("  Auto-generated seed from ILO's SDMX 2.1 dataflow registry, filtered to SDG")
    out_lines.append("  indicators relevant to social protection delivery. The selection rule is")
    out_lines.append("  derivability from PublicSchema record-level data: each kept indicator can be")
    out_lines.append("  computed (now or with a small slot addition) from Person.employment_status,")
    out_lines.append("  Person.occupation, Person.industry, Person.status_in_employment,")
    out_lines.append("  Enrollment in Program, etc. Macro indicators and country-level qualitative")
    out_lines.append("  ratings are excluded. Trilingual labels (en/es/fr) come from the SDMX")
    out_lines.append("  <common:Name> elements; dimensions and attributes are derived from each")
    out_lines.append("  DSD's authoritative DimensionList and AttributeList. Calculations, concept")
    out_lines.append("  URIs, and dimension/attribute catalogue definitions are out of scope for")
    out_lines.append("  this seed and tracked as TODOs.")
    out_lines.append("source: ILO SDMX (https://sdmx.ilo.org/rest/)")
    out_lines.append('license: "Reproduction of ILO material is permitted for non-commercial purposes per https://www.ilo.org/rights-and-permissions"')
    out_lines.append("")
    out_lines.append("metrics:")

    for info in all_infos:
        out_lines.append("")
        out_lines.extend(render_metric_entry(info))

    # dimensions_referenced section
    out_lines.append("")
    out_lines.append("dimensions_referenced:")
    for uri, desc in dim_refs.items():
        safe_desc = desc.replace('"', '\\"')
        out_lines.append(f'  {uri}: "{safe_desc}"')

    # attributes_referenced section
    out_lines.append("")
    out_lines.append("attributes_referenced:")
    for uri, desc in attr_refs.items():
        safe_desc = desc.replace('"', '\\"')
        out_lines.append(f'  {uri}: "{safe_desc}"')

    out_lines.append("")

    # 5. Write output
    OUT_FILE.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\nWrote {count} metric entries to {OUT_FILE}")

    # Stats summary
    vt_assigned = sum(1 for i in all_infos if derive_value_type(i["df_id"])[0] is not None)
    topic_assigned = sum(1 for i in all_infos if derive_topic(i["df_id"])[0] is not None)
    print(f"value_type assigned: {vt_assigned}/{count}")
    print(f"topic assigned: {topic_assigned}/{count}")

    # Distinct suffixes
    suffixes = set()
    for i in all_infos:
        bare = i["df_id"][3:] if i["df_id"].startswith("DF_") else i["df_id"]
        parts = bare.rsplit("_", 1)
        if len(parts) == 2:
            suffixes.add(f"_{parts[-1]}")
    print(f"Distinct dataflow id suffixes: {sorted(suffixes)}")

    # Distinct SDG prefixes (first two _-segments after DF_)
    prefixes = set()
    for i in all_infos:
        bare = i["df_id"][3:] if i["df_id"].startswith("DF_") else i["df_id"]
        parts = bare.split("_")
        if len(parts) >= 2:
            prefixes.add("_".join(parts[:2]))
    print(f"Distinct SDG prefixes: {sorted(prefixes)}")

    # Distinct dim ids across all DSDs
    all_dim_ids = set()
    for i in all_infos:
        for d in i["dimensions"]:
            all_dim_ids.add(d["id"])
        if i["time_dimension"]:
            all_dim_ids.add(i["time_dimension"]["id"])
    print(f"Distinct dimension ids: {sorted(all_dim_ids)}")

    # Distinct attr ids
    all_attr_ids = set()
    for i in all_infos:
        for a in i["attributes"]:
            all_attr_ids.add(a)
    print(f"Distinct attribute ids: {sorted(all_attr_ids)}")


if __name__ == "__main__":
    main()
