"""The offline metrics projection stays faithful to the authored catalog."""

import json
from pathlib import Path

import pytest
import yaml

from build.metrics_catalog import build_metrics_catalog, write_metrics_catalog


def test_catalog_projection_preserves_localization_calculation_and_scoped_ids(tmp_path):
    directory = tmp_path / "metric_catalog"
    directory.mkdir()
    calculation = {"scoring": "proportion", "populations": [{"criteria": "SELECT id\nFROM households", "population_type": "numerator"}]}
    entry = {
        "title": "Coverage", "description": "Covered households", "value_type": "proportion",
        "annotations": {"label_fr": "Couverture", "description_es": "Hogares cubiertos"},
        "calculation": calculation, "dimensions": ["publicschema:dim/ref_area"],
        "attributes": ["publicschema:attr/unit"], "aligns_with": ["https://example.org/indicator"],
        "core": True, "decimals": 0, "version": "1.2", "status": "bibo:draft",
    }
    for name in ("second", "first"):
        (directory / f"{name}.yaml").write_text(yaml.safe_dump({"id": name + "_seed", "metrics": {"coverage": entry}}))
    output = build_metrics_catalog(tmp_path, "https://example.org/")
    assert output["meta"] == {"schema_version": "0.1", "catalog_count": 2, "metric_count": 2}
    assert list(output["catalogs"]) == ["first", "second"]
    metric = output["metrics"]["first/coverage"]
    assert metric["uri"] == "https://example.org/metrics/first/coverage"
    assert metric["label"] == {"en": "Coverage", "fr": "Couverture"}
    assert metric["definition"] == {"en": "Covered households", "es": "Hogares cubiertos"}
    assert metric["calculation"] == calculation
    assert metric["decimals"] == 0
    assert metric["dimensions"] == entry["dimensions"]
    assert metric["attributes"] == entry["attributes"]
    assert metric["aligns_with"] == entry["aligns_with"]
    assert metric["unit"] is None


def test_projection_rebuild_reads_changes_and_is_byte_deterministic(tmp_path):
    directory = tmp_path / "schema" / "metric_catalog"
    directory.mkdir(parents=True)
    source = directory / "example.yaml"
    source.write_text("metrics:\n  coverage:\n    title: Original\n")
    output = tmp_path / "dist" / "metrics_catalog.json"
    write_metrics_catalog(directory.parent, output)
    before = output.read_bytes()
    write_metrics_catalog(directory.parent, output)
    assert output.read_bytes() == before
    source.write_text("metrics:\n  coverage:\n    title: Revised\n")
    write_metrics_catalog(directory.parent, output)
    metric = json.loads(output.read_text())["metrics"]["example/coverage"]
    assert metric["label"] == metric["definition"] == {"en": "Revised"}
    assert output.read_bytes() != before


def test_checked_in_catalogs_are_all_projected():
    schema_dir = Path(__file__).resolve().parents[1] / "schema"
    output = build_metrics_catalog(schema_dir)
    for source in (schema_dir / "metric_catalog").glob("*.yaml"):
        authored = yaml.safe_load(source.read_text())["metrics"]
        assert output["catalogs"][source.stem]["metric_count"] == len(authored)
        assert {key.split("/", 1)[1] for key in output["metrics"] if key.startswith(source.stem + "/")} == set(authored)


def test_historical_schema_without_catalog_projects_empty_data(tmp_path):
    assert build_metrics_catalog(tmp_path)["meta"]["metric_count"] == 0


@pytest.mark.parametrize("content, message", [
    ("- not a catalog", "catalog must be a mapping"),
    ("metrics: [wrong]", "metrics must be a mapping"),
    ("metrics: {coverage: null}", "metric 'coverage' must be a mapping"),
    ("metrics: {coverage: {annotations: wrong}}", "annotations must be a mapping"),
])
def test_malformed_catalog_names_source_and_problem(tmp_path, content, message):
    directory = tmp_path / "metric_catalog"
    directory.mkdir()
    source = directory / "broken.yaml"
    source.write_text(content)
    with pytest.raises(ValueError, match=message) as error:
        build_metrics_catalog(tmp_path)
    assert str(source) in str(error.value)
