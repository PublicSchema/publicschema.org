# ADR-011: Humanitarian Profile subtypes live outside PublicSchema

**Status:** Accepted

## Context

ADR-006 introduced the Profile hierarchy with three concrete subtypes at the root namespace: SocioEconomicProfile, FunctioningProfile, and AnthropometricProfile. ADR-010 then added a fourth subtype, FoodSecurityProfile, together with new draft vocabularies (`food-consumption-group`, `hhs-category`, `muac-band`, `lcs-band`) and a set of score and band properties on those profiles.

After ADR-010 was written, the humanitarian Profile subtypes were extracted from this repo and now live in a sibling schema outside PublicSchema. The extraction moved AnthropometricProfile, FoodSecurityProfile, and a new DwellingDamageProfile, along with their instrument-specific properties, vocabularies, and bibliography. FunctioningProfile and SocioEconomicProfile stayed in PublicSchema because their instruments (Washington Group, SES/PMT questionnaires) are cross-sector and widely used outside humanitarian response.

No ADR recorded the extraction. ADR-006 decision 2 and ADR-010 still describe the extracted subtypes as concrete PublicSchema concepts, and several documentation files still list AnthropometricProfile, FoodSecurityProfile, and DwellingDamageProfile as PublicSchema subtypes.

The extraction was driven by scope: instruments like SMART anthropometry, FCS/rCSI/HDDS, MDD-W, HHS, FIES, LCS, and post-disaster dwelling damage assessments are humanitarian-sector specific. Their vocabularies, cutoff rules, and source bibliography come from WFP, FAO, UNHCR, WHO/UNICEF, IPC, and cluster-system guidance. Keeping them in PublicSchema mixed humanitarian-program concerns with the cross-sector registry.

## Decision

1. **Humanitarian Profile subtypes are not PublicSchema concepts.** AnthropometricProfile, FoodSecurityProfile, and DwellingDamageProfile are published in a sibling schema that consumes PublicSchema's abstract `Profile` as an external supertype. Their URIs are not `publicschema.org/*`.

2. **PublicSchema retains two concrete Profile subtypes:** SocioEconomicProfile and FunctioningProfile. Both serve cross-sector use cases (SES and disability measurement) and their instruments (DCI SEP questionnaires, Washington Group) are published by standards bodies rather than humanitarian agencies.

3. **Instrument-specific properties and vocabularies follow their concept.** Score, band, and measurement properties scoped to the humanitarian instruments (FCS, rCSI, HDDS, MDD-W, HHS, FIES, LCS, MUAC, WHZ, dwelling-damage) and their vocabularies (`food-consumption-group`, `hhs-category`, `muac-band`, `lcs-band`) are not part of PublicSchema. The `acute-malnutrition-severity` vocabulary stays in PublicSchema because it backs the `nutrition_status` summary flag on Person, which remains a PublicSchema property per ADR-006 decision 4.

4. **ScoringRule, ScoringEvent, Instrument, SoftwareAgent stay in PublicSchema.** These are cross-sector registry concepts used by humanitarian, health, education, and social-protection tools. The sibling schema references them; it does not duplicate them.

5. **ADR-006 decision 2 and ADR-010 are superseded as implemented.** Their text is not rewritten because it records the original reasoning and the subtypes it names are still concrete, just at a different URI. Readers should treat this ADR as the current list of PublicSchema Profile subtypes.

## Alternatives considered

- **Keep humanitarian subtypes in PublicSchema and namespace them under `/aid/` or `/humanitarian/`.** Rejected: the existing domain-code scheme from ADR-003 is for sectors that may adopt PublicSchema broadly (sp, crvs, edu, health). Humanitarian response tooling has its own governance cadence (cluster leads, OCHA, IASC) and its own standards body pipeline (Sphere, IPC, CHS); a sibling schema gives it its own change cadence without blocking PublicSchema's release cycle.
- **Keep everything in PublicSchema and flag humanitarian profiles as optional subtypes.** Rejected: the property set for humanitarian profiles (food-security scores, anthropometric bands, dwelling damage) pulls in a bibliography and vocabulary dependency that PublicSchema does not need for its social-protection and civil-registration scope. The drift between ADR-010 and the shipping schema was the direct consequence of that coupling.
- **Write one superseding ADR per moved subtype.** Rejected: the extraction is a single decision (where humanitarian profiles live), not three independent ones.

## Consequences

- PublicSchema's Profile subtype list is now: SocioEconomicProfile, FunctioningProfile. The concept YAML (`schema/concepts/profile.yaml`) already reflects this.
- Documentation referring to AnthropometricProfile, FoodSecurityProfile, or DwellingDamageProfile as PublicSchema subtypes must either remove the reference or note that those concepts live in a sibling schema and cite this ADR.
- `schema/vocabularies/acute-malnutrition-severity.yaml` stays in PublicSchema. It is consumed by `publicschema.org/Person.nutrition_status` as a summary flag, and by anthropometric-band properties in the sibling schema that consumes it. A summary flag and a detailed observation consume the same classification, which is the expected pattern.
- The sibling schema is responsible for versioning its own Profile subtypes, vocabularies, and properties. PublicSchema is responsible for the Profile abstract supertype and the scoring infrastructure that is reused across sectors.

## References

- [ADR-003: Domain-scoped URIs, not prefixed names](003-domain-namespacing.md)
- [ADR-006: Extract observation-shaped data into a Profile hierarchy](006-profile-hierarchy.md) (decision 2 superseded as implemented)
- [ADR-010: Canonical-rule derived outputs on Profile concepts](010-profile-derived-outputs.md) (superseded as implemented, the subtypes it names moved)
