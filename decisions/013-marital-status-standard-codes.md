# ADR-013: Marital-status vocabulary reattributes single-letter codes to implementation peers

**Status:** Accepted

## Context

The `marital-status` vocabulary is `normative` maturity. Breaking changes require an ADR (per ADR-002). Two substantive errors were identified against the cited source.

The vocabulary cites the UN Principles and Recommendations for Population and Housing Censuses, Revision 3 (ST/ESA/STAT/SER.M/67/Rev.3, UN 2017). Verbatim extraction from paragraphs 4.164-4.171 of that document establishes:

1. **UN P&R prescribes five minimum categories, not six.** The minimum list is: Single (never married), Married, Married but separated, Widowed and not remarried, Divorced and not remarried. Paragraph 4.171 explicitly distinguishes consensual union from marital status and treats it as a separate union-characteristic variable, not a marital-status value.
2. **The single-letter codes S, M, W, D, L, C do not appear in UN P&R at all.** They come from FHIR R4's Marital Status Code System (v3-MaritalStatus) and from OpenSPP's MaritalStatus enumeration, which both follow an HL7 v3 lineage. Our vocabulary had imported them as `standard_code` values on each entry, implicitly attributing them to UN P&R.

The practical effect is misleading citations on every `standard_code`. A reviewer or adopter who follows the citation path expects to find `S` / `M` / `W` / `D` / `L` / `C` in UN P&R; they will not. The code points themselves are fine; the attribution is wrong.

## Decision

1. **Remove `standard_code` from every marital-status value.** `standard_code` is reserved for codes that appear in the cited primary standard (as it does for ISO 5218 on the `sex` vocabulary, where `0`/`1`/`2`/`9` are the standard's own codes). UN P&R does not define letter codes for the minimum categories, so none of our values carry one.
2. **Keep the six values: `never_married`, `married`, `widowed`, `divorced`, `legally_separated`, `consensual_union`.** The first five correspond to the UN P&R minimum categories (`legally_separated` maps to UN P&R's "Married, but separated"). `consensual_union` is retained as a PublicSchema extension beyond the UN P&R minimum, because most adopter systems (openSPP, DCI-reachable national registries) and peer standards (FHIR R4's MaritalStatus code system, when extended) represent consensual unions as a distinct category alongside married. The extension is noted in the vocabulary's standard citation.
3. **Keep the UN P&R Rev.3 citation as the `standard.uri`.** UN P&R is the authoritative source for the category set that this vocabulary aligns with. The citation URL is unchanged.
4. **Keep the single-letter codes in `system_mappings` for `openspp` and `fhir_r4`.** That is where they correctly belong: as external-system values that map to the canonical codes. They continue to appear as `code` entries within those mappings, with their natural provenance (OpenSPP / FHIR R4).
5. **No new vocabulary URI is minted.** The change is a citation correction: no canonical code changes, no value is renamed, no external mapping is removed. Adopters pinned to the vocabulary see the same six codes and the same six definitions.
6. **No release-version bump is forced by this change alone.** It will ride in the next scheduled release.

## Alternatives considered

- **Remove `consensual_union` to match UN P&R exactly.** Rejected: consensual union is one of the most common national-registry categories outside the UN P&R minimum, and removing it would force every adopter who tracks it to extend the vocabulary locally. UN P&R itself acknowledges consensual union as a widespread variable and handles it separately rather than forbidding it.
- **Reattribute the letter codes to UN P&R by arguing they are "common implementation practice".** Rejected: `standard_code` is a primary-source field. Implementation conventions are the business of `system_mappings`.
- **Replace the UN P&R citation with FHIR R4 / HL7 v3.** Rejected: the category set (never-married / married / widowed / divorced / legally-separated) is UN P&R's minimum list. Citing the implementation standard would understate the category set's primary source.
- **Migrate the vocabulary to `candidate` because of the attribution error.** Rejected: the category set and the external mappings are stable and widely adopted. The fix is a citation correction, not a semantic change.

## Consequences

- `schema/vocabularies/marital-status.yaml` loses six `standard_code: S|M|W|D|L|C` lines, one per value. No label, code, or definition changes.
- The `standard.notes` field gains a one-line clarification that UN P&R does not define letter codes for these categories; the letter codes that appear in `system_mappings` are provenance of FHIR R4 and OpenSPP.
- No downstream system-mapping value changes. FHIR R4's `S`/`M`/`W`/`D`/`L` codes still map to the canonical codes they mapped to before.
- The content change rests on the verbatim quote from UN P&R Rev.3 paragraphs 4.164-4.165; readers can independently verify against the cited document.

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- United Nations Department of Economic and Social Affairs, Statistics Division, "Principles and Recommendations for Population and Housing Censuses, Revision 3" (ST/ESA/STAT/SER.M/67/Rev.3), 2017, paragraphs 4.164-4.171
- HL7 v3 MaritalStatus code system, inherited by FHIR R4
- OpenSPP MaritalStatus enumeration
