# Design Principles

## 1. Semantic, not structural

Concepts carry meaning. A Person is not a bag of fields; it is a named entity with a definition written for domain practitioners. The interoperability problem is vocabulary divergence: systems use different names for the same real-world entities, and when those names encode different semantic choices, mappings between them lose information. PublicSchema provides shared definitions that make equivalences explicit and preserve meaning across systems.

## 2. Descriptive, not prescriptive

Nothing is mandatory. Systems adopt the concepts, properties, and vocabularies that apply to them. PublicSchema describes what delivery data looks like across systems; it does not mandate what any system must collect.

## 3. Evidence-based and incremental

Convergence data drives priorities. A property present in 6 out of 6 systems is worth standardizing before one present in 2 out of 6. Start with what is confirmed, extend when adoption surfaces genuine need.

## 4. Plain language for practitioners

Definitions are written for policy officers and program managers, not developers. "The lifecycle states of an enrollment in a program" is preferable to "an enumeration of status codes applicable to the beneficiary registration entity."

## 5. Abstract supertypes

Some concepts exist only as shared foundations for more specific subtypes. Agent, Event, Party, and Profile carry `abstract: true`, meaning they define common properties but are never instantiated directly. Subtypes (e.g., FunctioningProfile, ScoringEvent, Organization) inherit those properties and add their own. Agent is the actor-side supertype (Person, Organization, SoftwareAgent); Party is the beneficiary-side supertype (Person, Group). Person belongs to both. See [ADR-006](../decisions/006-profile-hierarchy.md) and [ADR-008](../decisions/008-agent-organization.md).

## 6. Observation and scoring separation

Data collection and data scoring are distinct steps with different actors, timestamps, and audit trails. Profile subtypes capture raw observation data (questionnaire responses, measurements); ScoringEvent records the act of applying a rule to that data. This separation lets systems recompute scores without re-collecting data. See [ADR-006](../decisions/006-profile-hierarchy.md).

## 7. Property categories

Properties are grouped by topical category (e.g., functioning, nutrition, housing) rather than listed flat. Categories are defined in `schema/categories.yaml` and rendered as visual groupings on concept detail pages. This helps practitioners locate relevant properties on concepts that carry many of them.

## 8. Instrument metadata

Properties that record data-collection context (administration mode, respondent, respondent relationship, age applicability) travel with the observation data, not in a separate metadata sidecar. This ensures that a Profile record is self-describing: a consumer can determine how the data was collected without consulting an external registry. See [schema-design.md section 7](schema-design.md#7-age-applicability) for age applicability details.

## See also

- [Schema Design](../schema-design/) -- naming, scoping, and modeling
- [Vocabulary Design](../vocabulary-design/) -- controlled value sets and system mappings
- [Versioning and Maturity](../versioning-and-maturity/) -- stability guarantees and evolution rules
- [Selective Disclosure](../selective-disclosure/) -- credential privacy design
