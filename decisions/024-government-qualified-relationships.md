# ADR-024: Preserve qualified ownership, education delivery and release attribution

Status: accepted for the local draft.

## Decision

Add optional reference relationships for facts that exist independently of a consuming workflow: ownership bounds and identified arrangements, asserted ownership routes, education offerings and release installation attribution. Reuse Person, Organization, CodedValue, Registration, EvidenceAssertion and RegistryEntry without changing their hierarchies or established meanings.

`OwnershipInterest` retains its exact percentage and gains separate inclusive/exclusive percentage bounds informed by BODS 0.4. Its draft endpoints support an identified LegalArrangement as well as the existing appropriate person or organization subjects. `interest_entity` becomes a URI reference so an arrangement does not have to masquerade as an Organization. The consuming profile checks permitted resolved types. LegalArrangement has no Agent, Party or Organization parent.

`OwnershipChainAssertion` relates an indirect interest to its separately identified component interests. The component collection has no order semantics: the interests' endpoint relationships describe the route. This preserves meaning in JSON-LD and RDF without relying on array order that the current exporters do not publish as an RDF list. The example profile exercises one connected route of direct components and compatible known dates. It calculates no ownership percentage or legal conclusion. RegistryEntry and evidence describe the provenance of this assertion.

`edu/EducationOffering` identifies a programme delivered by a provider at specified provider sites for a period. Sites can be physical or virtual. The expected award can reference its existing catalog identity without duplicating a qualification model or an individual's awarded qualification. `environment/release_installation` preserves source-reported installation attribution alongside the existing facility-level release link. Neither relationship establishes accreditation or compliance.

The [public evidence brief](../docs/government-relationships-draft.md) identifies primary sources and concrete counterexamples. These are PublicSchema reference choices, not exact BODS, Schema.org or EU-reporting mappings.

## Alternatives

Keeping bounds, ownership routes, programme delivery and installation attribution only in free text preserves a document but prevents reliable questions about the represented identities. A universal percentage-value class was unnecessary for these ownership-specific fields. Separate numeric inclusive and exclusive bounds retain the BODS distinctions without an additional flag convention or replacing the existing exact field.

Treating arrangements as Organizations would change the organizational contract and obscure cases without an institutional body. Widening Agent or Party would also admit unrelated actors or change existing service-recipient meaning. The explicit draft LegalArrangement and URI endpoints leave those existing hierarchies intact.

An ordered route was credible, but its order would need a new RDF-list serialization contract. Explicit endpoint relationships plus an unordered component set express the supported route in both existing public representations. Rich ownership networks, recursive indirect components and unidentified actors remain supported by their selected source models until an exercised PublicSchema profile requires more.

Duplicating the programme for each campus would lose shared programme identity. A new qualification catalog would exceed the identified need. The offering relationship and an optional external award-definition URI preserve the needed distinctions. Replacing the facility link with a polymorphic release-source field was also possible; an optional typed installation link keeps source-reported facility aggregates recognizable and avoids inventing installation detail.

## Compatibility and limits

Every introduced concept and property is draft. Existing start_date and end_date retain their normative meanings, including the date an assertion ceases to be effective. The example uses inclusive start dates and first-inactive end dates. Existing inclusive valid_to semantics remain distinct. No candidate or normative class, property, enum or hierarchy is widened by this decision.

The draft OwnershipInterest endpoint refinement changes the JSON shape of `interest_entity` from an object-or-reference relationship to a subject URI. Existing draft examples and consumers must retain the same subject identity while changing embedded references to their URI. An issuer's record identifier remains distinct from that URI. Namespace corrections for domain terms are governed by the domain allocation decision, not by this module's filename.

Reference fields remain optional. The local example profile adds resolution, compatible periods, explicit amount qualification, route connectivity, site-provider consistency and installation-facility consistency. It is not a runtime enforcement layer. Undated installation containment does not prove historical attribution. Live source truth, legal eligibility, standards conformance and external interchange compatibility remain unverified by these synthetic fixtures.
