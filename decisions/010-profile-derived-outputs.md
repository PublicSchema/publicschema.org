# ADR-010: Canonical-rule derived outputs on Profile concepts

**Status:** Accepted

## Context

External feedback from a form-authoring team (aubex-tools) highlighted an inconsistency in how Profile subtypes handle derived outputs. AnthropometricProfile already carries z-scores, status bands, and a cutoff rule alongside raw measurements, consistent with ADR-006's explicit decision to keep derived fields. However, FoodSecurityProfile and FunctioningProfile definitions stated that scoring is recorded separately via ScoringEvent, and `design-principles.md` section 6 generalized this into "Profile subtypes capture raw observation data; ScoringEvent records the act of applying a rule to that data."

This created a contradiction: ADR-006 kept derived fields on AnthropometricProfile and explicitly rejected the alternative of removing them ("Delete derived anthropometric status fields and compute on read. Rejected: many programs inherit a band without the raw z-score and need to store it."), while the downstream documentation and two concept definitions oversimplified that decision into a blanket "Profiles hold raw data only" rule.

The same operational argument that justified keeping anthropometric bands applies to other instrument families. Food consumption scores (FCS, rCSI, HDDS, MDD-W, HHS, FIES), the WG-SS recommended disability identifier, and MUAC screening bands are all canonical outputs of a single scoring rule applied at collection time. Programs routinely inherit these outputs from partner data, census, or DHS without item-level responses. Requiring a separate ScoringEvent for the default-rule score is disproportionate overhead that does not match how field collection software works.

| Concept | Raw items | Default-rule derivatives | Statement before this ADR |
|---|---|---|---|
| AnthropometricProfile | yes | **yes** (z-scores, status bands, `cutoff_rule`) | Definition describes derived bands as part of the concept |
| FoodSecurityProfile | yes | **no** | "scoring is recorded separately as a ScoringEvent" |
| FunctioningProfile | yes | **no** | "not a disability classification ... raw evidence from which disability identifiers can be constructed" |

## Decision

1. **Canonical-rule derived outputs live on the Profile.** When an instrument has a single canonical scoring function (WFP standard FCS thresholds, WG-SS recommended cutoff, WHO/UNICEF MUAC bands), the derived score or classification is a property of the Profile. This aligns all Profile subtypes with the pattern AnthropometricProfile already follows and corrects the downstream docs that oversimplified ADR-006.

2. **Non-canonical scoring goes to ScoringEvent.** Alternate thresholds (e.g., FCS 28/42 for high-sugar/high-oil contexts), a different rule version, recomputation after a rule revision, or composite indices that consume other scores (e.g., CARI) are recorded as a ScoringEvent that references its ScoringRule and the input Profile(s).

3. **No general `scoring_rule_applied` property on Profile.** The existing `cutoff_rule` (renamed to `muac_cutoff_rule` in this ADR's implementation) is specific to MUAC: it records which population-dependent cutoff rule was applied, because the cutoff depends on subject attributes observable only at measurement time (age, pregnancy status). For instruments with one canonical scoring function (FCS standard 21/35, WG-SS recommended cutoff, HDDS simple count), the rule is implicit in the derived property's definition; no record-level field is needed. A single `scoring_rule_applied` on FoodSecurityProfile would be ambiguous (FSP multiplexes FCS, rCSI, HDDS, HHS, FIES, and MDD-W); a multi-valued version would lose the link between rule and output.

4. **ScoringEvent references Profile, not the reverse.** ScoringEvent.inputs points to the Profile(s) it consumed. Profile does not carry a back-pointer to ScoringEvent. Systems that need the reverse traversal index on `inputs`.

## Alternatives considered

- **Move all derived fields to ScoringEvent (Option B).** Rejected: forces every operational system to emit a ScoringEvent for the canonical instrument score at collection time, which is disproportionate overhead. ADR-006 itself rejected this for anthropometric data. Programs routinely receive canonical scores without raw items (e.g., FCS consumption group from a partner dataset); requiring a ScoringEvent for each one adds structural complexity without semantic benefit.

- **Add `scoring_rule_applied` as a general-purpose slot on all Profile subtypes.** Rejected: the need for an explicit rule reference is specific to MUAC, where the cutoff depends on subject attributes. Other canonical scores are defined by a single rule with no subject-dependent parameters.

## Consequences

- Three concept definitions are updated: `profile.yaml`, `food-security-profile.yaml`, `functioning-profile.yaml`. Their definitions now state that the profile carries canonical-rule derived outputs.
- `design-principles.md` section 6 is corrected to match ADR-006's actual decision: Profiles record structured responses and may carry canonical-rule derived outputs; ScoringEvent records the act of applying a non-default rule, an alternate threshold, or recomputing a score.
- New properties are added at `draft` maturity: nine score/classification properties on FoodSecurityProfile (FCS score, FCS consumption group, rCSI score, HDDS score, MDD-W score, MDD-W achieved, HHS score, HHS category, FIES raw score), two disability identifier properties on FunctioningProfile, one MUAC band property on AnthropometricProfile, and two JMP input properties on SocioEconomicProfile.
- Five new vocabularies are added at `draft` maturity: `food-consumption-group`, `hhs-category`, `wg-ss-domain`, `muac-band`, `lcs-band`.
- `cutoff_rule` is renamed to `muac_cutoff_rule` to make its scope explicit.

## Follow-on work

- **LCS band:** added. `lcs_band` property on FoodSecurityProfile with `lcs-band` vocabulary (none/stress/crisis/emergency).
- **CARI:** a second-order composite of FCS, HHS, and LCS. Because it consumes scores from other instruments rather than raw items, it belongs on ScoringEvent, not on FoodSecurityProfile. No additional schema work needed; the existing ScoringEvent properties (`raw_score`, `assessment_band`, `inputs`, `rule_applied`) handle it.
- **CFM / WG-ES disability identifiers:** different response scales and domain groupings from WG-SS. Deferred to a separate plan. FunctioningProfile's definition notes that no equivalent derived identifier is yet defined for CFM or WG-ES.
- **`wdds_*` prefix cleanup:** the 10 existing `wdds_*_consumed` properties on FoodSecurityProfile encode MDD-W food groups but use the WDDS prefix. Renaming to `mdd_w_*` is a breaking change for adopters and should be handled separately.

## References

- [ADR-006: Extract observation-shaped data into a Profile hierarchy](006-profile-hierarchy.md)
- WFP VAM, Food Consumption Score Guidance Note (2015)
- Washington Group, Analytic Guidelines for the Creation of Disability Identifiers (2020)
- FANTA, Household Hunger Scale: Indicator Definition and Measurement Guide (2010, revised 2017)
- FAO, Minimum Dietary Diversity for Women (MDD-W) Guidelines (2016)
- WHO/UNICEF/WFP/UNSCN, Community-based management of acute malnutrition joint statement (2007/2009)
