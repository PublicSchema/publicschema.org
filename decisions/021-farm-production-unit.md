# ADR-021: Farm identifies a production unit, with separate holder responsibilities

Status: Accepted for draft vocabulary implementation.

Farm already describes an agricultural production unit but inherited Group, a collection of persons. That inheritance incorrectly made a cooperative-operated holding a person collection and admitted Farm to beneficiary references through Party.

Keep the draft Farm URI and remove its Group inheritance. Retain name and identifiers explicitly. Add draft HoldingOperatorRole with concrete person, organization and group variants. Their meaning is agricultural holder responsibility for major resource decisions and management control, including joint responsibility. The name preserves the familiar operator terminology, while the definition distinguishes holders from daily managers. One person can perform both functions.

InformalGroup is a concrete collection of persons with a shared purpose. It does not assert co-residence, kinship or a separate institutional body. Individual membership need not be enumerated. It can identify an informal collective without inventing an Organization or Household.

FAO WCA 2020 Volume 1 (Rome 2017), paragraphs 6.2, 6.7–6.14 and 6.17–6.21, distinguishes holding, household, joint holders and hired managers. See the [FAO source](https://www.fao.org/4/i4913e/i4913e.pdf). These semantics motivate the decision; FAO does not prescribe our typed classes, optionality or persistent URI policy. A continuing unit may retain its Farm URI when holders change. Splits, mergers and changes in management-unit boundaries require explicit registry identity decisions.

The alternative was retaining Farm as a group and introducing AgriculturalHolding. That would preserve some old payloads but duplicate Farm's existing production-unit definition. Another alternative, moving Farm directly under Party, would broaden a normative person/group abstraction. Neither is justified by this draft correction. Revisit if adopter evidence establishes a different Farm identity or an explicit production-unit benefit contract.

Group, GroupMembership, Party, Agent, beneficiary and recipient retain their ranges and meanings. Normative GroupType/farm still classifies external group records representing agricultural production units. Its meaning is not narrowed to a person roster. GroupRole/operator continues to mean daily management within its existing group-membership context; it is not an exact mapping to holder responsibility. Existing codes and meanings remain available for external models.

Old Farm payloads with inherited memberships, group_type or identity_documents need deliberate migration. Preserve source information and identify whether it describes people, the production unit or a registration. Do not automatically convert membership operators into holders or holders into beneficiaries. Organization remains outside Party. Historical ADR-008 records the earlier subtype list; this ADR supersedes its Farm-specific hierarchy examples only.

The [draft guide](../docs/farm-operators-draft.md) describes the local submission profile and its limits. Vocabulary fields remain optional. The profile resolves local targets, dispatches concrete role types, checks effective-date ordering and checks each Farm's listed role points back to that Farm. A complete inverse list is not required. No arbitrary remote resolution or benefit inference occurs.

## Follow-up: native work relationships and holding assignments

The first draft removed Farm membership without supplying a native representation for people working on the holding. That omission is corrected by `WorkRelationship` and `HoldingWorkAssignment`; preserving source information alone was not a complete migration path.

WorkRelationship connects one Person to the economic unit for which their work is undertaken. HoldingWorkAssignment connects a Person to the Farm where work occurs and can optionally link to the economic relationship. A standalone assignment is sufficient for simple participation. Agency workers and independent contractors can have one economic relationship and assignments to multiple holdings. Work relationships are not limited to employment or legally constituted employers. The typed Person endpoint identifies the worker; an organization providing services is not substituted for that worker.

Function, form of work, status at work, remuneration and seasonality remain independent, optional, scheme-qualified dimensions. Existing Person employment vocabulary codes retain their meaning. Daily management is a work function; holder responsibility remains its separate assertion, even when one person performs both. Manager changes do not close holder roles. The example profile checks local targets, same-person links and known period bounds, with start inclusive and cessation date exclusive for whole-day work intervals. No `valid_to` to `end_date` reinterpretation is made.

This follows the ILO ICSE-18 Manual (August 2023), pp. 4–5 and 21, and the explicitly draft WCA 2030 January 2026 text, §§4.21–4.24 and 7.9.16–7.9.18. FAO lists a final publication on 4 May 2026; the inspected January file is not that edition. See the [work guide](../docs/farm-operators-draft.md#work-on-a-holding) for exact links and evidence limits. Names, optional classification fields and URI serialization are PublicSchema design choices, not exact standard mappings.

A single FarmWorkerRole was considered but loses the economic-unit/site distinction. Making every holding assignment a WorkRelationship would incorrectly suggest that every client site identifies another job. Requiring two records for simple farm participation was also rejected. Revisit with concrete adopter cases that need different economic-unit boundaries or cannot preserve the optional relationship link. This additive draft slice preserves the Farm hierarchy correction and stronger GroupMembership, Party and code contracts.
