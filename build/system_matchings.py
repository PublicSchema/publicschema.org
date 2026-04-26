"""Projects external/<system>/matching.yaml files into a slim site bundle.

The build pipeline emits ``dist/system_matchings.json`` from this projection
so the site can render concept matches and documented gaps on each system
detail page without re-parsing YAML at request time.

The MVP surface is intentionally narrow: only the top-level metadata,
``concept_matches``, and ``no_match`` are projected. ``matches`` (per-property
mappings) and ``external_excess`` (PublicSchema's coverage backlog) are
deliberately excluded; both will get their own treatment later.
"""

from pathlib import Path

import yaml

META_FIELDS = (
    "system",
    "system_version",
    "source_repository",
    "source_branch",
    "fhir_repository",
    "fhir_branch",
    "country_config_reference",
    "last_reviewed",
)


def build_system_matchings(external_dir: Path) -> dict[str, dict]:
    """Return ``{system_id: projected_entry}`` for every matching.yaml.

    Empty dict if ``external_dir`` is missing or contains no matching files.
    Entries are keyed by the YAML ``system`` field (snake_case identifier
    matching the site's systemRegistry), not by directory name.
    """
    if not external_dir.exists():
        return {}

    out: dict[str, dict] = {}
    for path in sorted(external_dir.glob("*/matching.yaml")):
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            continue
        system_id = data.get("system")
        if not system_id:
            continue
        entry: dict = {}
        for field in META_FIELDS:
            if field in data and data[field] is not None:
                entry[field] = data[field]
        entry["concept_matches"] = list(data.get("concept_matches") or [])
        entry["no_match"] = list(data.get("no_match") or [])
        out[system_id] = entry

    return out
