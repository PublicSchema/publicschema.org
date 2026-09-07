"""Project the checked-in metric catalogs into the site's JSON data contract.

This build step is offline: upstream catalog refreshes are separate authoring
operations, and ordinary builds use only ``schema/metric_catalog/*.yaml``.
"""

import argparse
import json
from pathlib import Path

from build.loader import load_yaml


def build_metrics_catalog(schema_dir: Path, base_uri: str = "https://publicschema.org/") -> dict:
    catalogs = {}
    metrics = {}
    for source in sorted((schema_dir / "metric_catalog").glob("*.yaml")):
        raw = load_yaml(source)
        if not isinstance(raw, dict):
            raise ValueError(f"{source}: catalog must be a mapping")
        key = source.stem
        entries = raw.get("metrics", {})
        if not isinstance(entries, dict):
            raise ValueError(f"{source}: metrics must be a mapping keyed by metric ID")
        catalogs[key] = {
            "key": key,
            "id": raw.get("id", key),
            "title": raw.get("title", key),
            "description": raw.get("description", "").strip(),
            "source": raw.get("source", ""),
            "license": raw.get("license", ""),
            "path": f"/metrics/{key}",
            "metric_count": len(entries),
        }
        for metric_id, entry in sorted(entries.items()):
            if not isinstance(entry, dict):
                raise ValueError(f"{source}: metric {metric_id!r} must be a mapping")
            path = f"/metrics/{key}/{metric_id}"
            annotations = entry.get("annotations", {})
            if not isinstance(annotations, dict):
                raise ValueError(f"{source}: metric {metric_id!r} annotations must be a mapping")
            label = {"en": entry.get("title", metric_id)}
            definition = {"en": entry.get("description", label["en"]).strip()}
            for locale in ("fr", "es"):
                if annotations.get(f"label_{locale}"):
                    label[locale] = annotations[f"label_{locale}"]
                if annotations.get(f"description_{locale}"):
                    definition[locale] = annotations[f"description_{locale}"]
            metrics[f"{key}/{metric_id}"] = {
                "id": metric_id,
                "catalog_key": key,
                "path": path,
                "uri": base_uri.rstrip("/") + path,
                "label": label,
                "definition": definition,
                "value_type": entry.get("value_type", "number"),
                "unit": entry.get("unit"),
                "decimals": entry.get("decimals"),
                "dimensions": entry.get("dimensions", []),
                "attributes": entry.get("attributes", []),
                "aligns_with": entry.get("aligns_with", []),
                "concept_uri": entry.get("concept_uri"),
                "calculation": entry.get("calculation"),
                "core": entry.get("core", False),
                "version": entry.get("version", ""),
                "status": entry.get("status", "bibo:draft"),
            }
    return {
        "meta": {"schema_version": "0.1", "catalog_count": len(catalogs), "metric_count": len(metrics)},
        "catalogs": catalogs,
        "metrics": metrics,
    }


def write_metrics_catalog(schema_dir: Path, output: Path, base_uri: str = "https://publicschema.org/"):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_metrics_catalog(schema_dir, base_uri), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-dir", type=Path, default=Path("schema"))
    parser.add_argument("--out", type=Path, default=Path("dist/metrics_catalog.json"))
    args = parser.parse_args()
    write_metrics_catalog(args.schema_dir, args.out)


if __name__ == "__main__":
    main()
