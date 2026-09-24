# ADR-023: Qualified ownership interests and education delivery

**Status:** Accepted

## Context

Beneficial ownership registers rarely publish exact shares. They report bands such as "more than 25%, at most 50%", and they name trusts and nominee arrangements that are not organizations with their own legal personality. An indirect interest is held through a route of direct interests, each with its own holder, entity and dates. [BODS 0.4](https://standard.openownership.org/en/0.4.0/standard/reference.html) distinguishes exact values from inclusive and exclusive bounds, identifies arrangements, and relates an indirect relationship to its component records.

Education registers describe a program once and deliver it through several offerings, such as one campus intake and a later online intake. ISCED 2011 defines an education program as a coherent set of learning activities, and the [European Learning Model](https://europass.europa.eu/en/stakeholders/information-developers) LearningOpportunity is a provider's offering with its location, mode and the achievement it leads to. The qualification a program leads to is a definition in a qualifications register, distinct from an award already made to a person.

Kept only in free text, these facts cannot be queried: which interests fall in a band, which direct interests make up an indirect one, which site delivers an intake.

## Decision

1. **Ownership amounts keep their qualification.** `OwnershipInterest` keeps `interest_percentage` for an exact asserted value and adds four separate bounds: `interest_minimum_percentage` and `interest_maximum_percentage` (inclusive), `interest_exclusive_minimum_percentage` and `interest_exclusive_maximum_percentage` (exclusive). A missing bound is unknown and is not filled in. Details the slots cannot express go in `interest_description`.
2. **Legal arrangements are their own class.** `LegalArrangement` identifies a trust, nominee agreement or similar arrangement without legal personality (`name`, `identifiers`, `arrangement_type`). It has no Agent, Party or Organization parent. A trust with legal personality is an Organization. `interest_holder` is a URI admitting a person, organization or legal arrangement, and `interest_entity` is a URI admitting an organization or legal arrangement, never a person.
3. **An indirect interest lists its direct components.** `component_interests` on an OwnershipInterest whose `interest_directness` is `indirect` lists the direct interests that make up its route. The list is unordered: each component's own holder and entity describe the route, so the meaning survives in JSON-LD and RDF without an RDF list. Each indirect interest record carries one route; an alternative route is another indirect interest with its own components. Listing components verifies nothing and calculates no effective share.
4. **Programs and offerings are separate.** `edu/EducationProgram` is the program (`program_level`, `program_field`). `edu/EducationOffering` is a provider's offering of it (`offering_program`, `offering_provider`, `offering_sites`, `offering_mode`, `start_date`, `end_date`). Sites are ProviderSites and can be physical or virtual. An offering is not an enrollment and does not show accreditation.
5. **One slot names the qualification a program leads to.** `edu/qualification_awarded` is a multivalued URI to a qualification definition, such as an entry in a qualifications register. It is carried by EducationProgram, and by EducationOffering only when an offering leads to a different qualification from its program. `AwardedQualification` is the separate root record of a qualification already awarded to a person.

Shared ownership and arrangement meanings use root URIs; education meanings use `edu/`, following [ADR-024](024-domain-and-external-model-boundaries.md). These are PublicSchema choices informed by BODS, ELM and Schema.org, not exact mappings or interchange compatibility with them.

## Alternatives considered

- **Keep bounds, routes and delivery details in free text.** Rejected. It preserves the document but prevents reliable questions about the identities involved.
- **A general percentage-range value type, or one bound pair plus an inclusive flag.** Rejected. The four fields keep the BODS distinctions without a flag convention and without replacing the existing exact field.
- **Treat arrangements as Organizations, or widen Agent or Party to include them.** Rejected. It would change the organizational contract, obscure arrangements without an institutional body, and admit unrelated actors to service recipient slots.
- **A separate ownership chain assertion relating an indirect interest to its components.** Rejected. The indirect interest is already the statement that a route exists; a second record for the same route could disagree with it.
- **An ordered route.** Rejected. Order would need an RDF list serialization contract, and the component interests' endpoints already describe the route.
- **One program record per campus or intake.** Rejected. It loses the shared program identity.
- **A qualification catalog in PublicSchema.** Rejected. Qualifications registers already publish qualification definitions; a URI to their entry is enough.

## Consequences

Beneficial ownership conclusions, control determination, legal thresholds, BODS package ordering, replacement rules and anonymous records stay with an explicitly selected BODS profile or adapter. Rich ownership networks and unidentified actors stay in their source models until a profile needs them.

`interest_entity` is a URI, so embedded organization objects in earlier payloads become references with the same subject identity.

Joint providers, session timetables, enrollments and accreditation criteria are outside this decision. An offering can be the subject of a Registration or Authorization where a scheme recognizes or permits individual offerings.

The [ownership and education guide](../docs/government-relationships.md) walks through a synthetic exchange. Its example profile checks resolution, compatible periods, the qualification of amounts, route connectivity and site-provider consistency; it is a demonstration, not runtime enforcement.
