# ADR-012: Sex vocabulary cites ISO/IEC 5218:2022, not the withdrawn 2004 revision

**Status:** Accepted

## Context

The `sex` vocabulary is `normative` maturity. Breaking changes require an ADR (per ADR-002).

Until this ADR, the vocabulary's `standard.uri` pointed to `https://www.iso.org/standard/36266.html`, which is ISO/IEC 5218:2004. The round-1 adversarial review (finding T03) confirmed that ISO/IEC 5218:2004 is officially withdrawn and has been superseded by ISO/IEC 5218:2022, published under catalogue number 81682 (`https://www.iso.org/standard/81682.html`). The 2022 revision retains the same four code points (0, 1, 2, 9) with the same semantics; nothing about the value set, the codes, or the definitions changes.

Citing a withdrawn standard from a normative vocabulary is misleading on its own, and it is specifically a problem for adopters building VC-ready credential schemas who follow the URI to verify that a vocabulary reference is current. The standard is still referenced by the same name (ISO/IEC 5218) and the same code points; only the canonical URL and the revision year change.

## Decision

1. **Update `standard.uri` to `https://www.iso.org/standard/81682.html`** (ISO/IEC 5218:2022).
2. **Do not change any code, label, definition, or `standard_code` value.** The 2022 revision preserves the 2004 code points and semantics.
3. **Update `standard.notes` to say "ISO/IEC 5218:2022".** Keep the note about EBSI PID extension codes (3/4/5/6); it is independent of the revision year.
4. **Do not mint a new vocabulary URI.** Per ADR-002, breaking changes to a normative entity require a new URI. Swapping a citation URL from a withdrawn revision to the current revision of the same standard, with no change to the code points or semantics, is not a breaking change for adopters of the vocabulary. Adopters who pinned to the vocabulary get the same codes and the same definitions; they just now cite the correct, in-force standard.
5. **No release-version bump is forced by this change.** It is a citation correction, not a semantic change. It will ride in the next scheduled release.

## Alternatives considered

- **Treat the URI change as breaking and mint `sex_v2`.** Rejected: the value set is identical. Forcing adopters to migrate to a new vocabulary URI for an identical set of codes penalises them for our citation mistake.
- **Leave the 2004 URI in place as the "date of adoption" and add a second field for the current revision.** Rejected: the `standard.uri` slot is the citation URL; it should point to the current, in-force standard. Historical revision tracking is not part of the schema's job.
- **Drop the ISO citation entirely and treat the 4-code vocabulary as a local one.** Rejected: the codes come from ISO/IEC 5218 and interoperate with FHIR's AdministrativeGender, DCI SexCategoryEnum, OpenSPP Iso5218GenderCodes, and the SEMIC EU Human Sex NAL precisely because they track the ISO standard. Removing the citation would disconnect this vocabulary from its peer systems.

## Consequences

- `schema/vocabularies/sex.yaml` `standard.uri` is updated to `https://www.iso.org/standard/81682.html` and `standard.notes` now says "ISO/IEC 5218:2022" rather than leaving the revision year implicit.
- No change to any value, label, definition, standard_code, system_mapping, or external_equivalent.
- No change to downstream JSON, RDF, or JSON-LD outputs besides the URL string in the `standard.uri` field.
- Future withdrawal of ISO/IEC 5218:2022 by a later revision follows the same pattern: update the URI in place, add an ADR, no vocabulary URI change unless the code points themselves change.

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- Round-1 adversarial review finding T03: `.work/reviews/adversarial/round-1/standards-findings.md`
- ISO/IEC 5218:2022, "Information technology — Codes for the representation of human sexes"
