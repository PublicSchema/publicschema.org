# ADR-021: Farm identifies a production unit, with separate holder responsibilities

**Status:** Accepted

## Context

Farm describes an agricultural production unit but inherited Group, a collection of persons. That inheritance made a cooperative-operated holding a person collection and admitted Farm to beneficiary references through Party. Registries also need to say who is responsible for a farm, who works on it, what land it uses and under which arrangements, and these facts change on different schedules from the farm's own identity.

FAO's World Census of Agriculture distinguishes the holding (an economic unit of agricultural production under single management), the household, the holder who makes the major decisions and carries the technical and economic responsibility, joint holders, and hired or unpaid managers ([WCA 2020 Volume 1, Rome 2017](https://www.fao.org/4/i4913e/i4913e.pdf), paragraphs 6.2, 6.7 to 6.14 and 6.17 to 6.21; [WCA 2030, 2026](https://doi.org/10.4060/cd9437en)). The ILO statistical standards separate forms of work, status at work and the economic unit for which work is done ([ICSE-18 Manual, August 2023](https://webapps.ilo.org/ilostat-files/Documents/ICSE-18_manual.pdf), pp. 4 to 5 and 21; 19th ICLS resolution on work statistics). These sources motivate the decision; they do not prescribe PublicSchema's classes, optionality or URI policy.

## Decision

1. **Farm stands alone.** `agri/Farm` no longer inherits Group. It keeps `name` and `identifiers` explicitly and adds summary fields: `farm_area` (a QuantityValue, zero for a farm without land), `land_tenure` (the LandTenure kinds of arrangement under which the farm operates land, following WCA 2030 Item 0204), `livestock_type` and `location`. Summary fields do not override detailed parcel, tenure or animal records. A continuing unit keeps its Farm URI when its holders change; splits, mergers and changes of management-unit boundaries need explicit registry identity decisions.
2. **Holder responsibility is a dated role.** Abstract `agri/AgriculturalHolderRole` means responsibility for the key decisions on resource use and for management control of a farm, alone or jointly, during a stated period. Its concrete variants name the holder with a typed slot: PersonAgriculturalHolderRole (`holder_person`), OrganizationAgriculturalHolderRole (`holder_organization`) and GroupAgriculturalHolderRole (`holder_group`). Every variant names the farm with `holder_farm`. Several simultaneous roles for one farm describe joint holders. A Farm does not list its holder roles; they are found through `holder_farm`.
3. **InformalGroup** is a collection of persons identified together for a shared purpose, without asserting a separate institutional body, co-residence or kinship. Its members need not be enumerated. Joint agricultural holders are one example.
4. **Farmer registration is recognition, not responsibility.** `agri/FarmerRegistration` specializes Registration and can list the farms it covers with `registered_farms`. It does not establish holder responsibility, land rights or program eligibility.
5. **Work on a holding is separate from holder responsibility.** `WorkRelationship` connects one Person to the economic unit for which the work is done (`work_economic_unit`, a URI). `agri/HoldingWorkAssignment` connects a Person to the Farm where the work happens and can link to the WorkRelationship. A standalone assignment is enough for simple participation; an agency worker or contractor has one relationship and assignments to several holdings. The work is described by independent optional dimensions:
   - `work_form` takes the closed `FormOfWork` enumeration: the five forms of work of the 19th ICLS resolution (own-use production, employment, unpaid trainee, volunteer and other work activities).
   - `work_status` is a CodedValue in a named classification, such as ICSaW-18 or ICSE-18.
   - `work_remuneration` and `work_seasonality` are CodedValues.
   - `work_functions`, such as daily management or harvesting, is on HoldingWorkAssignment only, because functions describe the work on a farm rather than the economic relationship.

   Daily management is a work function; holder responsibility is its own role, even when one person holds both. A change of manager does not close a holder role.
6. **Land rights are tenure assertions about land administrative units.** `land/LandTenureAssertion` has a `tenure_category` from the closed `TenureCategory` enumeration (right, restriction or responsibility, following the Land Administration Domain Model, ISO 19152-1) and a `tenure_object` typed as `land/LandAdministrativeUnit`, the unit to which rights apply. `tenure_holder` is a URI admitting a person, organization or group, and can be absent for a restriction attached to the land alone. Farm's `land_tenure` describes how the farm uses land; it is not a record of land rights.

Group, GroupMembership, Party, Agent, beneficiary and recipient keep their ranges and meanings. Normative GroupType/farm still classifies external group records representing agricultural production units, and its meaning is not narrowed to a roster. GroupRole/operator keeps its daily-management meaning within group membership and is not an exact mapping to holder responsibility.

## Alternatives considered

- **Keep Farm as a Group and add AgriculturalHolding.** Rejected. It preserves some old payloads but duplicates Farm's production-unit definition.
- **Move Farm under Party.** Rejected. It broadens a normative person and group abstraction to cover production units.
- **One holder role with a URI holder.** Rejected. The typed variants let JSON Schema and SHACL both check the holder's class without union ranges, which the JSON Schema build does not carry.
- **An inverse list of holder roles on Farm.** Rejected. The same fact would be kept in two places that can disagree.
- **A single FarmWorkerRole.** Rejected. It serves a roster but conflates the economic relationship of an agency worker or contractor with each place of work.
- **Require a WorkRelationship for every assignment.** Rejected. It adds a record when only participation is known, and it would suggest that every client site is another job.
- **A CodedValue for the form of work.** Rejected. The ICLS resolution fixes five forms, so a closed list lets validators and translations rely on them.

## Consequences

Old Farm payloads with inherited memberships, `group_type` or `identity_documents` need deliberate migration. Preserve the source values, then decide whether each describes people, the production unit or a registration. Membership operators are not converted into holders automatically, and holders are not converted into beneficiaries. A legacy Person-to-Farm membership describing daily management or other work becomes a HoldingWorkAssignment once its meaning and target are confirmed; the original role code can be kept in `work_functions`.

This ADR supersedes the Farm example in [ADR-008](008-agent-organization.md)'s list of Group subtypes. Organization remains outside Party.

All reference fields are optional. The [farm and holder guide](../docs/farm-holders.md) describes the example profile, which resolves local targets, dispatches concrete role types, checks that each work assignment and its linked relationship name the same person, and checks date order. It performs no remote resolution and no benefit inference.
