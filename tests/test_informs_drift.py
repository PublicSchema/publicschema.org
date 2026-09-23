"""Drift check for bibliography `informs:` links.

Re-runs `build/propose_informs.py` in read-only mode. If a property, concept,
or vocabulary contains evidence of a link (external_equivalents, schema_org_equivalent,
or vocab standard.name) that is not reflected in the relevant bibliography
entry's `informs:` block, this test fails with a concrete pointer to the
source file and field.

This does NOT enforce the reverse direction: bibliography entries are allowed
to list informs that the extractor does not surface (curated editorial calls
go in that direction).

TODO: the reverse asymmetry means a contributor who removes evidence from a
source YAML (e.g., deletes an `external_equivalents.dci` block on a property)
will not be alerted that the bibliography still claims the link. If this
becomes an issue, add a reverse-drift test that walks bib_existing and fails
for non-surfaced entries that are not on an explicit editorial allow-list.
"""

from collections import defaultdict

from build import propose_informs


def _alignment(key: str, vocabulary: str) -> dict:
    return {
        "external_equivalents": {
            key: {"vocabulary": vocabulary, "match": "close", "uri": "https://example.org/x"}
        }
    }


def test_report_reads_the_linkml_schema():
    report = propose_informs.build_report()
    assert "fhir-r4" in report.bib_existing
    assert {p.kind for p in report.proposals} == {"concepts", "properties", "vocabularies"}


def test_fhir_r5_alignments_map_to_the_fhir_r5_entry():
    report = propose_informs.Report()
    propose_informs.process_external_equivalents(
        _alignment("fhir-r5", "FHIR R5"), "concept Example", "concepts", "Example", report
    )
    assert [(p.bib_id, p.target_id) for p in report.proposals] == [("fhir-r5", "Example")]


def test_alignment_ids_that_name_a_bibliography_entry_map_to_it():
    report = propose_informs.Report()
    report.bib_existing["eu-dir-2000-60"] = {"concepts": set(), "vocabularies": set(), "properties": set()}
    propose_informs.process_external_equivalents(
        _alignment("eu-dir-2000-60", "Directive 2000/60/EC"),
        "concept Example",
        "concepts",
        "Example",
        report,
    )
    assert [p.bib_id for p in report.proposals] == ["eu-dir-2000-60"]
    assert not report.flags


def test_no_informs_drift():
    report = propose_informs.build_report()
    missing: list[str] = []
    for prop in report.proposals:
        existing = report.bib_existing.get(prop.bib_id, {}).get(prop.kind, set())
        if prop.target_id not in existing:
            missing.append(
                f"- {prop.bib_id}.informs.{prop.kind} is missing {prop.target_id!r} "
                f"(evidence: {prop.source_path} {prop.field_path}: {prop.evidence})"
            )
    assert not missing, (
        "Bibliography informs drift detected. "
        "Either add the missing links by running `uv run python -m build.propose_informs --apply`, then update the matching term `bibliography_refs` annotations, "
        "or remove the evidence from the source YAMLs if the link is not intended.\n\n"
        + "\n".join(missing)
    )


def test_no_unmapped_flags():
    """Every external reference in the schema must resolve to a bibliography id.

    If this fails, the curated lookup tables in build/propose_informs.py
    need to be extended, or a new bibliography entry must be created.
    """
    report = propose_informs.build_report()
    grouped: dict[str, list[str]] = defaultdict(list)
    for flag in report.flags:
        grouped[flag.reason].append(
            f"  - {flag.source_path} {flag.field_path}: {flag.detail}"
        )
    if grouped:
        parts = []
        for reason, items in sorted(grouped.items()):
            parts.append(f"[{reason}]")
            parts.extend(items)
        raise AssertionError(
            "Unmapped references found. Extend EXTERNAL_EQUIV_LOOKUP / "
            "VOCAB_STANDARD_LOOKUP in build/propose_informs.py, or add a "
            "bibliography entry.\n\n" + "\n".join(parts)
        )
