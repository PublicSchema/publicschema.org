# Farm and agricultural holder responsibilities

Farm describes the production unit. Person, Organization and InformalGroup describe people or bodies responsible for it. A holding's identity is separate from the identity of its holder and any registration record.

HoldingOperatorRole means **holder responsibility**: major resource decisions and management control, alone or jointly. It does not mean ownership, employment or daily management alone. A holder can also be the daily manager, but being a manager does not establish holder responsibility. The typed variants name a Person, Organization or Group without admitting a software scheduler as the responsible subject.

The [example records](/registry-draft/examples/farm-operators/records.json) describe one holding, an earlier cooperative holder, two current joint individual holders and an earlier informal collective. Neither individual needs a national identifier. The collective has a name without a complete membership roster. The example supplies no parcels or minimum land area: Farm's vocabulary does not require land ownership, a positive land area or a parcel list. The dated succession is an explicit example of asserted unit continuity, not a universal rule for sales, mergers or splits.

These distinctions follow [FAO WCA 2020 Volume 1, Rome 2017](https://www.fao.org/4/i4913e/i4913e.pdf), paragraphs 6.2, 6.7–6.14 and 6.17–6.21. Class names, date slots and persistence are PublicSchema draft design choices. The FAO WCA 2030 [January 2026 master draft](https://unstats.un.org/UNSDWebsite/statcom/session_57/documents/BG-3g-1-Background_document_WCA_2030-E.pdf), paragraphs 4.21–4.24, also distinguishes unpaid daily managers. No census conformance is claimed.

## Vocabulary and the local example profile

All vocabulary fields are optional so partial descriptions remain useful. Generated JSON Schema validates available fields but string references do not prove target identity, and a reference to an abstract role does not itself validate a concrete role's endpoint. Generated SHACL checks typed graph relationships with the class hierarchy supplied.

Run the independently named demonstration profile from the repository root:

```sh
.venv/bin/python examples/farm-operators/validate_profile.py
```

The profile requires concrete operator roles to identify a Farm and exactly their own typed operator endpoint. It resolves strings and embedded objects locally, rejects missing or wrong-type targets, checks effective-date order and checks that a role listed by a Farm identifies that Farm. Other roles can exist without appearing in the Farm's list. Unknown dates stay absent and do not prove whether a responsibility is current. This profile supports the listed concrete types only; extending it to other group or person subtypes requires an explicit change.

The profile is a reproducible example, not an operational registry service. It does not establish ownership, registration, entitlement or disclosure permissions. A group's eligibility remains a program decision. Cooperative grants cannot be inserted into Party-ranged beneficiary fields without a separate contract.

## Migration and review questions

Farm no longer inherits person-group membership fields. Preserve legacy source values before deciding which subject they describe. Normative GroupType/farm remains the classifier for external group records representing production units, including flat agricultural or social-protection models. It has not been redefined as a roster classifier. GroupRole/operator still describes its original daily-management membership function; do not automatically map it to the new holder role. GroupMembership itself remains Person-to-Group.

All new terms remain draft. Reviewers should supply counterexamples for collective identities, holder versus manager responsibilities, and continuity across transfers or restructuring. Evidence from real registry payloads can refine these choices. [ADR-021](/registry-draft/decisions/021-farm-production-unit.md) records alternatives and maturity handling.
