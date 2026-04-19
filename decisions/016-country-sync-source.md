# ADR-016: Retain the lukes ISO-3166 GitHub mirror as the country-vocabulary sync source

**Status:** Accepted

## Context

The `country` vocabulary is `normative` maturity. Breaking changes require an ADR (per ADR-002).

The vocabulary's `sync.source_url` points to [`lukes/ISO-3166-Countries-with-Regional-Codes`](https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json), a GitHub mirror of ISO 3166-1 alpha-2 data. The mirror's own README states that its data is "the result of merging data from two sources, the Wikipedia ISO 3166-1 article for alpha and numeric country codes, and the UN M49 Standard country or area codes for statistical use data." It cautions that "the data is not authoritative."

This was flagged as a provenance concern: an authoritative normative vocabulary should not depend on a Wikipedia-derived feed. The concern proposed switching to a more authoritative UNSD-direct source.

## Options investigated

Three alternatives were evaluated.

### Option 1: `datasets/country-codes` on GitHub

The [`datasets/country-codes`](https://raw.githubusercontent.com/datasets/country-codes/main/data/country-codes.csv) CSV consolidates UNSD-published M49 data with ISO 3166-1 alpha-2 codes. Its README names UNSD and the UN Protocol and Liaison Service as upstream sources. The `region` vocabulary already uses this feed.

Empirical comparison against the current `lukes` feed:

- **Code set**: 249 alpha-2 codes, identical to lukes (zero symmetric difference).
- **English display labels**: 42 of 249 differ. Many differences are "(the)" suffixes authentic to UNSD usage (e.g., "Bahamas (the)", "Gambia (the)") which degrade readability without gaining authority. Several are substantive regressions: CI would be labelled "Ivory Coast" instead of "Côte d'Ivoire", and HK would be labelled "China, Hong Kong Special Administrative Region" instead of "Hong Kong". These follow from the CSV's `UNTERM English Short` column being empty for those entries, forcing fallback to less idiomatic columns.

### Option 2: ISO OBP (Online Browsing Platform)

ISO publishes the official ISO 3166-1 list at `https://www.iso.org/obp/ui/#iso:pub:PUB500001:en`. The landing page returns HTTP 403 to programmatic clients (bot-blocking), and the complete dataset is sold as a subscription product, not a free machine-readable download. Not usable as a sync source.

### Option 3: UNSD direct download

`https://unstats.un.org/unsd/methodology/m49/overview/` serves the M49 classification but does not expose a stable machine-readable download URL. The page is HTML-and-JavaScript-rendered; probes for `Comprehensive.xlsx` and `Comprehensive.csv` return 404. Not usable as a sync source.

## Decision

1. **Retain `lukes/ISO-3166-Countries-with-Regional-Codes` as the sync source for `country.yaml`.** The code set has been empirically verified identical to UNSD-sourced data, and the mirror's English labels match ISO 3166-1 English Short Name conventions more consistently than the candidate alternatives.
2. **Strengthen the `sync.note` field** to be transparent about the mirror's self-description ("not authoritative"), record the empirical verification done in this ADR, and direct readers to `standard.uri` as the canonical citation.
3. **Do not mint a new vocabulary URI.** The code points, labels, definitions, and canonical citation are unchanged. This is a documentation update, not a breaking change per the ADR-012 precedent.
4. **Re-verify on each sync run.** Going forward, `build/sync_standards.py`'s drift report (`added`, `removed`, `updated` code lists) is the mechanism that catches divergence between the mirror and authoritative sources. If the mirror's code set ever drifts from UNSD-published M49, the divergence will surface in the sync report and trigger a new decision.

## Alternatives considered

- **Switch to `datasets/country-codes`.** Rejected: the label quality regresses on 42 entries including substantive cases (CI, HK) where the CSV's English label fields are empty or non-preferred, forcing fallback to less idiomatic forms. The code set gain is zero; the label loss is real.
- **Switch to ISO OBP.** Rejected: paywalled, bot-blocked, and not machine-accessible. Cannot drive a sync pipeline.
- **Hand-curate the vocabulary, drop the sync entirely.** Rejected: ISO 3166-1 is stable but not static, and hand-curation would drift silently. The sync report is a detection mechanism we want to keep.
- **Dual-source (fetch both, fail if they disagree).** Rejected: the payoff over a single-source sync is small given the codes currently agree. Adds complexity for a low-probability failure mode.

## Consequences

- `schema/vocabularies/country.yaml` `sync.source_url` is unchanged.
- `sync.note` is rewritten to document the provenance posture, the empirical verification, and the drift-detection mechanism.
- No change to any code, label, definition, `standard_code`, `standard.uri`, `system_mappings`, or `external_equivalents`.
- Future re-verification should compare the sync source's code set to `datasets/country-codes` (UNSD-derived) as a convergence check. If the two sources ever diverge on code points, the divergence triggers a follow-up ADR.

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- [ADR-012: Sex vocabulary cites ISO/IEC 5218:2022](012-sex-vocabulary-iso5218-2022.md): precedent for citation correction on a normative vocabulary without minting a new URI
- ISO 3166-1, "Codes for the representation of names of countries and their subdivisions"
