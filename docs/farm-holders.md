# Farm and agricultural holder responsibilities

Farm describes the production unit. Person, Organization and InformalGroup describe people or bodies responsible for it. A holding's identity is separate from the identity of its holder and any registration record.

AgriculturalHolderRole means **holder responsibility**: the key decisions on resource use and management control of a farm, alone or jointly, including its technical and economic responsibility. It does not mean ownership, employment or daily management alone. A holder can also be the daily manager, but being a manager does not establish holder responsibility. The typed variants (PersonAgriculturalHolderRole, OrganizationAgriculturalHolderRole and GroupAgriculturalHolderRole) name a Person, Organization or Group through `holder_person`, `holder_organization` or `holder_group`, and the farm through `holder_farm`, without admitting a software scheduler as the responsible subject. A Farm does not list its holder roles; find them through `holder_farm`.

The [synthetic example records](../examples/farm-operators/records.json) describe one holding, an earlier cooperative holder, two current joint individual holders and an earlier informal collective. Neither individual needs a national identifier. The collective has a name without a complete membership roster. The example gives the holding's total area, land tenure types and livestock kept, but no parcels. Farm's vocabulary does not require land ownership, a positive land area or a parcel list; a farm without land has a `farm_area` of zero. The dated succession is an explicit example of asserted unit continuity, not a universal rule for sales, mergers or splits.

These distinctions follow [FAO WCA 2020 Volume 1, Rome 2017](https://www.fao.org/4/i4913e/i4913e.pdf), paragraphs 6.2, 6.7–6.14 and 6.17–6.21. Class names, date slots and persistence are PublicSchema design choices. The FAO WCA 2030 [January 2026 master draft](https://unstats.un.org/UNSDWebsite/statcom/session_57/documents/BG-3g-1-Background_document_WCA_2030-E.pdf), paragraphs 4.21–4.24, also distinguishes unpaid daily managers. No census conformance is claimed.

## Summary fields and registration

`farm_area` is the total area the farm operates, whatever the title, as a QuantityValue with its unit (for example UCUM `har` for hectares). It is not the sum of the areas of parcels shared with other farms. `land_tenure` lists every kind of arrangement under which the farm operates land, following the land tenure types of WCA 2030 Item 0204; it describes how the farm uses land, not who holds rights over it, and it is sensitive because some values reveal precarious tenure. `livestock_type` lists the kinds of livestock kept on the farm, whether or not the farm owns them, grouped following the WCA 2030 livestock classes. These summary fields do not override detailed parcel, tenure or animal records.

A FarmerRegistration recognizes a person, organization or group as a farmer for a stated administrative purpose. `registered_farms` optionally names the farms it covers. The registration does not establish holder responsibility, land rights or program eligibility.

## Vocabulary and the local example profile

All vocabulary fields are optional so partial descriptions remain useful. Generated JSON Schema validates available fields but string references do not prove target identity, and a reference to an abstract role does not itself validate a concrete role's endpoint. Generated SHACL checks typed graph relationships with the class hierarchy supplied.

Run the independently named demonstration profile from the repository root:

```sh
uv run --locked python examples/farm-operators/validate_profile.py
```

The profile requires concrete holder roles to identify a Farm through `holder_farm` and exactly their own typed holder endpoint. It resolves strings and embedded objects locally, rejects missing or wrong-type targets, rejects the abstract AgriculturalHolderRole, checks effective-date order and rejects fields that the vocabulary no longer defines on Farm and WorkRelationship. Unknown dates stay absent and do not prove whether a responsibility is current. This profile supports the listed concrete types only; extending it to other group or person subtypes requires an explicit change.

The profile is a reproducible example, not an operational registry service. It does not establish ownership, registration, entitlement or disclosure permissions. A group's eligibility remains a program decision. Cooperative grants cannot be inserted into Party-ranged beneficiary fields without a separate contract.

## Migration from Group-based farms

Farm no longer inherits person-group membership fields. Preserve legacy source values before deciding which subject they describe. Normative GroupType/farm remains the classifier for external group records representing production units, including flat agricultural or social-protection models. It has not been redefined as a roster classifier. GroupRole/operator still describes its original daily-management membership function; do not automatically map it to a holder role. GroupMembership itself remains Person-to-Group.

[ADR-021](../decisions/021-farm-production-unit.md) records the alternatives considered.

## Work on a holding

Use `HoldingWorkAssignment` to connect a Person to a Farm where they work or are expected to work. It describes a worker or daily manager on the holding. A direct assignment needs no employer assertion, employment contract or second relationship. It can describe an unpaid daily manager, a family contribution or paid work without turning that person into a holder.

Use `WorkRelationship` when the economic relationship has its own identity: one person's work for one economic unit. That unit can be household production or an enterprise and need not be a legally incorporated organization. `work_economic_unit` holds its subject URI. The example profile resolves that URI locally to an Organization, Household, InformalGroup or Farm; asserting this endpoint means the subject is the relevant economic unit, not that every instance of those types is automatically one. When the party bound as employer differs from the economic unit, such as an employer-of-record agency, `legal_employer` names it; the example profile does not resolve that link.

A holding assignment can link to the work relationship using `assignment_work_relationship`. For example, an agency employee has one relationship with the staffing agency and two assignments to different holdings. An independent contractor can likewise have one relationship with their own enterprise and assignments for multiple clients. A client holding is not thereby the employer or a separate job. The assignment and linked relationship must identify the same Person. Neither implies a holder role.

The [synthetic work example](../examples/farm-operators/work-records.json) includes paid and unpaid daily managers, a holder who also manages, family production for own use, a contributing family worker in market production, an agency worker and a contractor. It retains distinct person, holding, economic relationship and assignment identities.

| Optional field | What it describes |
| --- | --- |
| `work_functions` | One or more functions, such as daily management or harvesting. Holding work assignments only. |
| `work_form` | Employment, own-use production or another identified form of work. |
| `work_status` | Status in a stated classification, such as status in employment or a broader status at work. |
| `work_remuneration` | Wage, fee, absence of regular remuneration or another stated payment arrangement. |
| `work_seasonality` | Seasonal pattern, independently of function, status, contract duration and working time. |

`work_form` takes a `FormOfWork` value; the other four use CodedValue records that name their scheme. All five are optional and describe the work in the containing relationship or assignment, not the person's overall labour force status. Missing classifications remain unknown; a linked relationship's classifications are not automatically copied onto assignments. Prefer putting economic-relationship classifications on the WorkRelationship when both are present; functions on a farm belong to the assignment. Classification disagreements require source review; this example does not adjudicate them. The existing Person employment fields and vocabulary codes are unchanged.

The example schemes under `https://example.org/farm-work/v1/` are synthetic local codes. Their labels illustrate independent dimensions; they are not official ILO codes or an ICSE conformance claim. A supplied classification needs its scheme URI and original code. Unknown/local values can be retained without guessing a standard equivalent. For a standard-binding profile, identify the exact scheme and edition and validate its applicability separately.

The [ILO ICSE-18 Manual, August 2023](https://webapps.ilo.org/ilostat-files/Documents/ICSE-18_manual.pdf), printed pp. 4–5 and 21, supplies the person/economic-unit distinction and explains why unpaid family contributions to market production can be employment, while own-use work is a different form. Employment does not always mean employee status. These distinctions motivate the model; ILO does not prescribe the assignment class or the five-field serialization. The [FAO January 2026 WCA 2030 master draft](https://unstats.un.org/UNSDWebsite/statcom/session_57/documents/BG-3g-1-Background_document_WCA_2030-E.pdf), §§4.21–4.24 and 7.9.16–7.9.18, informs the manager/holder and employee/contractor distinctions.

The final edition, [FAO WCA 2030, 2026](https://doi.org/10.4060/cd9437en), was published on 4 May 2026 according to FAO's [round page](https://www.fao.org/world-census-agriculture/wca-round/round-2030-%282026-2035%29/en). The land tenure types (Item 0204, paragraphs 7.2.38 to 7.2.47) and livestock classes (Annex 8) used by the vocabulary follow the final edition; the paragraph numbers above for work and management come from the January draft.

### Work profile boundaries and migration

The executable profile validates both example files. For WorkRelationship it requires Person and a locally resolved economic unit; for HoldingWorkAssignment it requires Person and Farm. An optional relationship link must resolve to WorkRelationship for that same person. Classification fields remain optional. Supplied dates must be valid and ordered. A linked assignment must fit within any known relationship bounds; absent dates do not become infinite intervals.

For these work examples, `start_date` is the first effective calendar day and `end_date` is the last. The profile rejects an end date before the start date when both dates are supplied. Amina's manager assignment ends on 2025-06-30 and the replacement starts on 2025-07-01, with no overlapping effective day. The holder responsibility remains unchanged. This implements the relationship-date convention. Converting source dates follows the [relationship date migration guide](relationship-date-migration.md), which requires confirming the source boundary and date precision first.

A legacy Person-to-Farm membership with a daily-manager or worker role can become a HoldingWorkAssignment once its work meaning and target identity are confirmed. Preserve the original role code and scheme in `work_functions` when appropriate; do not infer pay, form, status, seasonality or holder responsibility from that role. A GroupRole/operator code describes daily management and is not automatically a holder. A membership that describes ownership needs an ownership assertion, not a work assignment. GroupMembership remains Person-to-Group and cannot target Farm.

The strongest simpler alternative is a single FarmWorkerRole. It serves a roster but conflates the agency or contractor's economic relationship with each work site. Requiring WorkRelationship plus assignment for every participant introduces unnecessary records when only participation is known. The optional link supports both cases. No hours, employment-law entitlement or automatic census counts are claimed here.
