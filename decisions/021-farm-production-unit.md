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
