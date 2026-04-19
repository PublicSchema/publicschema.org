# ADR-008: Separate Agent supertype for actors, keep Party as the beneficiary-side abstraction

**Status:** Accepted

## Context

The schema has a single abstract `Party` supertype with subtypes `Person` and `Group` (Household, Family, Farm). Party was introduced as the common type for "entities that can be identified, enrolled in programs, and receive benefits or services." It is the shared range of beneficiary-side references like `beneficiary`, `recipient`, `subject`, `redeemable_by`, `issued_to`.

Three properties currently piggyback on Party but mean something different. They identify **who performed an action**, not who received one:

- `performed_by` on Profile: "The party (enumerator, field officer, or agency) accountable for administering the instrument or taking the measurement."
- `evaluator` on ScoringEvent: "The party (field officer or agency) accountable for the scoring."
- `publisher` on Instrument, ScoringRule, and SoftwareAgent: "The organization that publishes or maintains the instrument, software agent, or scoring rule."

Each of those definitions names an **agency** or an **organization** as a valid value. None of Party's current subtypes can carry that meaning. A Household is not a publisher. A Family does not administer a questionnaire. The definitions are promising a range that the type system does not admit.

A second, related problem: `performed_by`'s definition cross-references `software_used` as the place to record a software tool that captured or derived the data ("performed_by identifies who is responsible, not what ran the capture"). Profile does not list `software_used` among its properties. The cross-reference is dangling. ScoringEvent and EligibilityDecision already list `software_used`; Profile does not.

Conflating receivers and actors under one supertype also makes the RDF graph less honest. A reasoner following Party subclass edges infers that a Household could be the `evaluator` of a scoring event. Domain standards avoid this conflation. W3C PROV uses `prov:Agent` with subtypes `prov:Person`, `prov:Organization`, `prov:SoftwareAgent` for actors. FOAF uses `foaf:Agent` the same way. FHIR splits `Practitioner`, `Organization`, `Device`, `RelatedPerson`. Schema.org pairs `Person` and `Organization` as sibling `Thing` subtypes. None of these models makes "recipient of services" and "actor of services" the same abstraction.

## Decision

1. **Introduce an abstract `Agent` concept** at the root URI namespace (`publicschema.org/Agent`). Agent is the shared supertype for actors: parties that perform, publish, evaluate, decide, or execute.
2. **Add `Organization`** as a concrete concept at the root namespace. Organization represents a legally or administratively identifiable body (government agency, ministry, NGO, UN agency, statistical office, health facility, civil registration office, standards publisher). Minimum property set: `name`, `identifiers`, `location`. The `location` slot is the organization's own registered or primary site (single, optional). It is explicitly not "the place where an action performed by the organization happened" — event-level place remains a property of the event record. Single cardinality is a pragmatic minimum, not a resolved modelling question: real administrative bodies (national statistics offices, UN agencies, multi-branch NGOs) will be referenced long before anyone models their branch hierarchy. Multi-site modelling (plural `locations`, or a `parent_organization` hierarchy) is a follow-on decision. Other richer properties (legal form, jurisdiction, contact points) are also deferred.
3. **Agent subtypes:** `Person`, `Organization`, `SoftwareAgent`. `Person` is the only concept that belongs to both `Party` and `Agent` (a Person can both receive services and perform them). `SoftwareAgent` already exists; it becomes an Agent subtype.
4. **Party keeps its current scope and meaning.** Party remains the beneficiary-side abstraction. Subtypes stay `Person` and `Group` (Household, Family, Farm). Organizations are not Parties: grants or services to organizations, if ever modelled, will not be expressed through Party.
5. **Retype actor-side properties in the Profile/scoring stack:**
   - `performed_by` → `Agent`. The accountability narrative in the current definition is preserved: software never appears here in practice, because Profile records that were software-captured record the software through `software_used` instead. Typing as `Agent` keeps the schema honest (the range is the full actor hierarchy) while the property's own definition steers adopters toward Person or Organization.
   - `evaluator` → `Agent`. Same reasoning as `performed_by`.
   - `publisher` → `Agent`. Publishers are typically institutional bodies, but standards methodologies, individual research publications, and Verifiable Credential issuers can legitimately be named persons. schema.org's `publisher` accepts `Person | Organization`; Dublin Core `dct:publisher` is untyped; FHIR `ImplementationGuide.publisher` is a string. Typing publisher at `Agent` matches that precedent. The property's definition steers adopters toward Organization for the common case.
6. **Add `software_used` to Profile.** The cross-reference in `performed_by`'s definition becomes resolvable. No new property: the existing `software_used` (type `SoftwareAgent`) is added to Profile's property list and inherited by all Profile subtypes.
7. **Keep the accountability/tooling split in the narrative.** `performed_by`, `evaluator`, and analogous accountability slots are ranged at `Agent` but document themselves as the human or organizational entity responsible. Software tools are recorded alongside via `software_used`. This preserves the principle already encoded in today's property definitions: who is responsible vs. what ran the capture.
8. **Generalise the `location` property definition.** Today `location`'s en/fr/es definitions are household-specific ("associated with this household"). Rephrase them so `location` applies to any concept that has a site (Household, Organization, and any future concept with a place). The convergence notes stay as-is (they describe where convergence was measured, on Household). This rephrase is a prerequisite for placing `location` on Organization and carries no semantic regression for existing Household usage.
9. **PractitionerRole layer deferred.** Reifying "Dr. Smith acting as registrar for Office X" (Person + Organization + role) is a legitimate future need but is not required to honestly type the fields in scope here. Revisit when a concrete use case appears (e.g., a Verifiable Credential whose evidence includes role-qualified issuer).
10. **No backward-compatibility shims.** No adopters are on the v2 schema yet. Old property ranges are replaced cleanly.

## Alternatives considered

- **Broaden Party to include Organization.** Rejected: conflates two orthogonal roles (receiver vs. actor) under one supertype. A Ministry is not the same kind of thing as a Household. It also makes the SEMIC mapping note on Party ("ours is specifically persons and organized groups in social protection") untrue and removes a meaningful distinction that standards bodies preserve.
- **Narrow `performed_by` to Person only; add a separate `performing_organization` property.** Rejected: many records name an organization without naming an individual (census fieldwork logged at team or agency level; administrative certificates signed at an office rather than by a named officer). Splitting per-range multiplies properties and makes downstream consumers join them back together. A single `Agent`-ranged property covers both cases.
- **Use a `Person | Organization` union range rather than `Agent`.** Rejected: inline unions are opaque to readers of individual property pages and do not give the RDF graph a named supertype. A named abstract is cheaper long term and gives the graph a reusable supertype for `performed_by`, `evaluator`, `publisher`, and the SoftwareAgent-adjacent slots. Software never appearing in the accountability slot is a narrative constraint in the property definition, not a type-system constraint — the same pattern the current schema uses to document sensitivity distinctions that type systems cannot express.
- **Skip `location` on Organization.** Rejected: Organizations have a primary site in every jurisdiction we've looked at, and readers reach for it when resolving references to authorities, facilities, and offices. Adding it at minimum shape is cheaper than bolting it on later and generalising `location` is a one-line definition change with no semantic regression for Household.
- **Generalise `address` alongside `location`.** Deferred: `address` has the same household-specific framing and will eventually need the same rephrase, but it is not required to ship Organization with a single `location` slot. Out of scope here.
- **Add multi-site `locations` (plural) to Organization now.** Deferred: multi-site organizations are best modelled as a hierarchy of child organizations with their own single `location`. `parent_organization` and `locations` can come later.
- **Replace both Party and Agent with a single `Actor`/`Agent` root.** Rejected: collapses the receiver/actor distinction rather than honouring it. Beneficiary-side properties (`beneficiary`, `recipient`, `subject`) have different semantics, different disclosure profiles, and different reviewer audiences than actor-side properties; keeping the two supertypes lets each carry its own documentation, convergence notes, and external equivalents.
- **Introduce a `PractitionerRole` layer (FHIR-style) now.** Deferred. Capturing "Dr. Smith acting as registrar for Office X" is a legitimate future need, but it is a modelling layer on top of Agent (Person + Organization + role) rather than a replacement for Agent. Not blocking on this ADR.

## Consequences

`Person` inherits from two abstract concepts: `Party` (receiver side) and `Agent` (actor side). LinkML, JSON-LD, and OWL all handle multiple inheritance at the abstract level without ambiguity. The property-level consequence is that Person-typed references resolve for both Party-ranged and Agent-ranged properties, which is the intent.

`Party` and `Agent` are intentionally **not disjoint**. Person is in both. SHACL shapes, OWL reasoners, and generated SHACL validators must target the specific class (`sh:targetClass Party` or `sh:targetClass Agent`) and must not emit a disjointness axiom between the two. A test invariant asserting no `owl:disjointWith` is generated between Party and Agent will guard this at build time.

`performed_by`, `evaluator`, and `publisher` are ranged at `Agent` and therefore admit `SoftwareAgent` by the type system alone. The accountability narrative ("who is responsible, not what ran the capture") is carried by the property definitions, not by the type. If that narrative needs to be hardened into validation, a SHACL shape can exclude `SoftwareAgent` (`sh:not [sh:class SoftwareAgent]`) on the accountability slots. This ADR defers that hardening; the narrative constraint is explicit in the definitions and adopters who need type-system enforcement can apply it locally.

Actor-side properties in the Profile and scoring stack gain an honest type. `performed_by`, `evaluator`, and `publisher` stop promising a range that includes Households. Downstream validators (SHACL, JSON-LD context, VC schema generators) can constrain these properties to the Agent hierarchy.

`software_used` on Profile closes the cross-reference in `performed_by`'s definition. Profile records can now capture the tool that ran a capture or derivation step (e.g., an ODK form, a CommCare app, a biometric SDK version) without overloading `performed_by`.

The `location` property becomes concept-agnostic. Household continues to use it exactly as before; Organization uses it for its registered or primary site. Future concepts that have a site (facility records, program offices, etc.) can reuse the same property without a second rephrase.

Party remains a beneficiary-side-only supertype. If provider-side or institution-recipient workflows later enter scope (health facility receiving a grant, NGO receiving a block transfer, school receiving funding), a follow-on ADR may revisit Party's subtype list. The current decision does not close that door; it records that Organization is an Agent today and is not claimed as a Party, and the question of whether institutions can be Parties is left for when a concrete use case arrives.

Revisiting Party's subtype list post-v1.0 would be a breaking change for adopters who built SHACL on the Party subtype closure ("Party has Person or Group subtypes, nothing else"). No adopters are on the v2 schema today, so the closure can be extended for free now; the moment adopters appear, any addition to Party's subtype list becomes a breaking-change beat in the schema's compatibility policy. The no-adopters-yet window is the free move, and the ADR does not commit to any future behaviour beyond flagging this cost.

Downstream renderers (the site and any external schema browser) now distinguish two hierarchies under the same page tree. The navigation needs to reflect this: Party keeps its subtype list (Person, Group, Household, Family, Farm); Agent gains one (Person, Organization, SoftwareAgent). Person appears under both, with a cross-reference note.

Property detail pages render one extra row in the type panel for shared concepts. `Person`'s page shows both supertype memberships. That is intentional.

The convergence count on Agent is non-trivial: PROV, FOAF, schema.org, FHIR, SEMIC Core Person all have an Agent-equivalent. External equivalents on the Agent concept page can cite them directly, which strengthens the VC-alignment story.

## Follow-on work

- **Organization richer properties.** `parent_organization` (for organizational hierarchy), `legal_form`, `jurisdiction`, multi-site `locations`, and contact points (phone, email, website) are deferred to a later ADR. Start minimal.
- **Organization identifier schemes.** Which identifier schemes are recognised for organizations (DUNS, LEI, GS1, national agency registries, UN agency codes)? The `identifiers` slot accepts any, but a recommended vocabulary is out of scope here.
- **PractitionerRole layer.** Reified role assignments (Person in role at Organization) are deferred. Revisit when a concrete use case appears (e.g., a credential whose evidence includes "issued by Person acting as registrar at Office").
- **External equivalents on Agent.** Populate `external_equivalents` with `prov:Agent`, `foaf:Agent`, `schema:Thing` (Person+Organization sibling pattern), FHIR's practitioner/organization split, and SEMIC Core Person as part of the implementation.

## References

- ADR-006: Extract observation-shaped data into a Profile hierarchy (introduces `performed_by`, `software_used`, and the accountability-vs-tooling distinction)
- ADR-007: Cross-concept property reuse across Profile subtypes
- W3C PROV-O: `prov:Agent`, `prov:Person`, `prov:Organization`, `prov:SoftwareAgent`
- FOAF: `foaf:Agent`, `foaf:Person`, `foaf:Organization`
- schema.org: `Person` and `Organization` as sibling subtypes of `Thing`
- FHIR R4: `Practitioner`, `PractitionerRole`, `Organization`, `Device`
- FOAF: `foaf:Agent`, `foaf:Person`, `foaf:Organization` (cited separately from SEMIC; they are distinct precedents)
- SEMIC Core Person (`w3.org/ns/person#Person`). The existing Party concept's `external_equivalents.semic` note flags that SEMIC's broader Agent vocabulary is not identical to Party's scope; this ADR resolves that by moving the Agent semantics onto the new Agent concept.
- schema.org, Dublin Core, and FHIR precedents for `publisher` accepting a person, not only an organisation, which drives the choice of `Agent` over `Organization` as its range.
