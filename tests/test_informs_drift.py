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
        "Either add the missing links by running `uv run python build/propose_informs.py --apply`, "
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
