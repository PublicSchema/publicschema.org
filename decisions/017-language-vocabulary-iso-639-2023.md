# ADR-017: Language vocabulary cites ISO 639:2023 (Set 3), not the withdrawn ISO 639-3:2007

**Status:** Accepted

## Context

The `language` vocabulary is `normative` maturity. Breaking changes require an ADR (per ADR-002).

Until this ADR, `standard.name` was `ISO 639-3`. ISO 639-3:2007 was withdrawn and consolidated into ISO 639:2023 (published 2023, catalogue number 74575). ISO 639:2023 merged the six separate parts of ISO 639 (639-1 through 639-6) into a single multi-part standard whose "Set 3" corresponds to the former ISO 639-3 alpha-3 code set. SIL Global continues as the Language Coding Agency for Set 3.

The `standard.uri` at `https://www.iso.org/iso-639-language-code` is already canonical and forward-compatible: it resolves to the consolidated ISO 639:2023 landing page. The alpha-3 code points, the SIL-maintained download URL, and every value in the vocabulary are unchanged between ISO 639-3:2007 and ISO 639:2023 Set 3.

Citing a withdrawn standard from a normative vocabulary is misleading for adopters who follow the citation to verify that a vocabulary reference is current. The same reasoning that drove ADR-012 for `sex` applies here: revision year is material, code points are not.

## Decision

1. **Update `standard.name` to `ISO 639:2023 (Set 3)`.** The bare form `ISO 639-3` is retained in the definition field (adopters searching for "ISO 639-3" still find the vocabulary) and in narrative context, but the normative citation tracks the in-force standard.
2. **Add `standard.notes`** recording that the alpha-3 code set corresponds to Set 3 of ISO 639:2023, which superseded the withdrawn ISO 639-3:2007, and that SIL Global continues as the Language Coding Agency.
3. **Do not change `standard.uri`.** `https://www.iso.org/iso-639-language-code` already points at the consolidated standard.
4. **Do not change any code, label, definition, `standard_code`, sync source, or system mapping.** The 2023 consolidation preserved all Set 3 code points and semantics.
5. **Do not mint a new vocabulary URI.** Per ADR-002 and the ADR-012 precedent, swapping a citation name from a withdrawn revision to the current revision of the same standard, with no change to code points or semantics, is not a breaking change for adopters.
6. **No release-version bump is forced.** Citation correction, not a semantic change; rides the next scheduled release.

## Alternatives considered

- **Keep `ISO 639-3` as the standard name.** Rejected: it names a withdrawn standard. Adopters verifying citation currency against iso.org would find the 2007 revision withdrawn and the 2023 consolidation in force.
- **Use the bare name `ISO 639:2023`.** Rejected: loses the "Set 3" precision that distinguishes this vocabulary (alpha-3 comprehensive codes) from Set 1 (alpha-2) or Set 2 (bibliographic/terminologic alpha-3). `ISO 639:2023 (Set 3)` is how SIL refers to the authoritative scope in their post-2023 announcements.
- **Treat the name change as breaking and mint `language_v2`.** Rejected: the code points are identical. Forcing adopters to migrate vocabulary URIs for a citation-only change would penalise them for our citation mistake, exactly as argued in ADR-012.
- **Drop the ISO citation entirely.** Rejected: the alpha-3 code scheme derives authority from ISO 639. Removing the citation would disconnect this vocabulary from its peer systems (openSPP, FHIR R4, and every downstream that validates against ISO 639 Set 3).

## Consequences

- `schema/vocabularies/language.yaml` `standard.name` is updated to `ISO 639:2023 (Set 3)` and `standard.notes` is added.
- No change to any value, label, definition, `standard_code`, `sync.source_url`, or system mapping.
- No change to downstream JSON, RDF, or JSON-LD outputs besides the strings in `standard.name` and `standard.notes`.
- Future revisions of ISO 639 follow the same pattern: update citation in place, add an ADR, no vocabulary URI change unless Set 3 code points themselves change.

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- [ADR-012: Sex vocabulary cites ISO/IEC 5218:2022](012-sex-vocabulary-iso5218-2022.md): precedent for citation correction without minting a new URI
- ISO 639:2023, "Code for individual languages and language groups"
