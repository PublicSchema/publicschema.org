# DHS catalog grouping and limits

The checked-in `schema/concept_schemes/dhs_household.yaml` groups metrics from
`schema/metric_catalog/dhs_household.yaml` by DHS Level2 labels. The refresh script,
`build/seed_metrics_from_dhs_api.py`, derives each `publicschema:concept/dhs/{slug}`
by lowercasing that label and replacing non-alphanumeric runs with underscores.
Metrics in the same group share a `concept_uri`.

These groups preserve source organization. They are not a curated SKOS scheme or
proof that all metrics in a group measure one concept. The `likely_mixed` flags
identify groups that combine meanings, such as land and livestock ownership or
sanitation facility type and sharing status. The absence of a flag does not
establish conceptual equivalence. No cross-survey equivalence or SKOS hierarchy
is asserted by this mechanical grouping.

Ordinary builds read the checked-in YAML offline. Refreshing from the upstream API
is a separate authoring operation and requires review of changes to labels,
selection and group assignments. The local `build/cache/` responses are disposable
and are not source inputs for the site build.

Because the slug depends on the source label, an upstream rename can change the
URI produced by a refresh. Compare the refresh with the checked-in source and
preserve or explicitly migrate existing identities before adopting those changes.
See [Versioning and Maturity](../versioning-and-maturity.md) for URI guarantees.
