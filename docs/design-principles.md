# Design Principles

## 1. Semantic, not structural

Concepts carry meaning. A Person is not a bag of fields; it is a named entity with a definition written for domain practitioners. The interoperability problem is vocabulary divergence: systems use different names for the same real-world entities, and when those names encode different semantic choices, mappings between them lose information. PublicSchema provides shared definitions that make equivalences explicit and preserve meaning across systems.

## 2. Descriptive, not prescriptive

Nothing is mandatory. Systems adopt the concepts, properties, and vocabularies that apply to them. PublicSchema describes what delivery data looks like across systems; it does not mandate what any system must collect.

## 3. Evidence-based and incremental

Convergence data drives priorities. A property present in 6 out of 6 systems is worth standardizing before one present in 2 out of 6. Start with what is confirmed, extend when adoption surfaces genuine need.

Standards-body convergence supplements mapped-system convergence at the abstract-supertype level. Abstract concepts such as Agent, Event, and Instrument report `system_count: 0/6` against the v1 mapped-system corpus because no mapped system exposes an explicit supertype by that name, yet the abstractions are aligned with widely-deployed standards (PROV-O for Agent and Event, FOAF/schema.org for Agent and Organization, FHIR for Instrument). Convergence across those standards is acceptable evidence for introducing an abstract supertype, provided subtypes still carry mapped-system evidence of their own. See [ADR-008](../decisions/008-agent-organization.md) for this pattern applied to Agent and Organization.

## 4. Plain language for practitioners

Definitions are written for policy officers and program managers, not developers. "The lifecycle states of an enrollment in a program" is preferable to "an enumeration of status codes applicable to the beneficiary registration entity."

## 5. Abstract supertypes

Some concepts exist only as shared foundations for more specific subtypes. Agent, Event, Party, and Profile are the four **core abstract supertypes**. They carry `abstract: true`, define common properties, and are never instantiated directly. Subtypes (e.g., FunctioningProfile, ScoringEvent, Organization) inherit those properties and add their own. Agent is the actor-side supertype (Person, Organization, SoftwareAgent); Party is the beneficiary-side supertype (Person, Group). Person belongs to both. See [ADR-006](../decisions/006-profile-hierarchy.md) and [ADR-008](../decisions/008-agent-organization.md).

A small number of **intermediate abstract categorisers** also carry `abstract: true` without being core supertypes. Group intermediates between Party and its concrete subtypes (Household, Family, Farm). VitalEvent intermediates between Event and the concrete vital events (Birth, Death, Marriage, etc.). MarriageTermination intermediates between VitalEvent and the concrete termination subtypes (Divorce, Annulment). Each intermediate groups siblings that share common structure but have no direct use of their own. They are abstract for the same reason as the core supertypes (never instantiated, always realised through a subtype) but they are not intended as cross-domain foundations.

## 6. Observation and scoring separation

Data collection and data scoring are distinct steps with different actors, timestamps, and audit trails. Profile subtypes record the structured responses from a single instrument administration and may also carry outputs derived by applying the instrument's canonical scoring rule (for example, the WG-SS disability identifier on FunctioningProfile, or a PMT score on SocioEconomicProfile). ScoringEvent records the act of applying a non-default rule, an alternate threshold, or recomputing a score after a rule revision. This separation lets systems recompute scores without re-collecting data while keeping canonical outputs close to the observations that produced them. Domain-specific profile subtypes published in sibling schemas follow the same pattern. See [ADR-006](../decisions/006-profile-hierarchy.md), [ADR-010](../decisions/010-profile-derived-outputs.md), and [ADR-011](../decisions/011-humanitarian-profile-extraction.md).

## 7. Property categories

Properties are grouped by topical category (e.g., functioning, nutrition, housing) rather than listed flat. Categories are defined in `schema/categories.yaml` and rendered as visual groupings on concept detail pages. This helps practitioners locate relevant properties on concepts that carry many of them.

## 8. Instrument metadata

Properties that record data-collection context (administration mode, respondent, respondent relationship, age applicability) travel with the observation data, not in a separate metadata sidecar. This ensures that a Profile record is self-describing: a consumer can determine how the data was collected without consulting an external registry. See [schema-design.md section 7](schema-design.md#7-age-applicability) for age applicability details.

## 9. Core and extended property tiers

Properties may carry an optional `core: true` flag, marking them as part of the must-ask subset of their owning profile. The flag enables a single profile definition to support both rapid and comprehensive assessments without duplicating the schema. Form compilers can filter to core-only properties to produce a rapid-assessment variant of any form (for example, a short WG-SS subset derived from the full FunctioningProfile).

When omitted, `core` defaults to `false` (extended). The flag is independent of `valid_instruments`: a property may be both `core: true` and tied to a specific instrument. Programs that need a different rapid subset can override the filter at the form layer.

## See also

- [Schema Design](../schema-design/) -- naming, scoping, and modeling
- [Vocabulary Design](../vocabulary-design/) -- controlled value sets and system mappings
- [Versioning and Maturity](../versioning-and-maturity/) -- stability guarantees and evolution rules
- [Selective Disclosure](../selective-disclosure/) -- credential privacy design
