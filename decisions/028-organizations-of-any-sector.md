# ADR-028: Organizations of any sector, as actors and as receivers

**Status:** Accepted

## Context

[ADR-008](008-agent-organization.md) introduced Organization as an Agent: a body that acts in a delivery process. Its definition listed only public and non-profit bodies (ministries, NGOs, UN agencies, courts). [ADR-025](025-organizations-legal-personality-and-authority.md) already said Organization covers public and private bodies and gave it `legal_form`, but the definition still read as public-sector only.

ADR-008 kept Organization out of Party, the supertype of entities that are enrolled in programs and receive benefits or services. It recorded that the question would return "if provider-side or institution-recipient workflows later enter scope". They have. Agricultural support is paid to companies and cooperatives that hold farms, producer organizations receive grants, and registers issue licences and credentials to businesses. With Organization outside Party, `beneficiary`, `recipient`, `redeemable_by` and `issued_to` could not name a company, so these records could not be expressed.

Business and cooperative registers also record what an organization does (its economic activities, coded with ISIC, NACE, NAICS or a national version) and when it ceased to exist. Organization had `formation_date` but neither of these.

Finally, the line between a person and a business is drawn differently by each jurisdiction. In many countries a sole trader has no legal personality separate from the person; elsewhere the register gives a sole proprietorship its own entry and number, and some laws ring-fence its assets. PublicSchema is adapted to each country through application profiles and local extensions (see the handbook chapter on extending PublicSchema), so the core should not settle this for every country at once.

## Decision

1. **Organization covers bodies of any sector.** Its definition names public and private, for-profit and not-for-profit bodies, including companies, cooperatives, associations, NGOs and government agencies, and drops the restriction to bodies acting in a public delivery process.
2. **Organization is a Party as well as an Agent.** Its primary supertype stays Agent and Party is added as a mixin, mirroring Person (Party first, Agent as mixin). Party's definition becomes "a person, an organized group of persons or an organization that can be identified, enrolled in programs and receive benefits or services". SoftwareAgent stays an Agent only.
3. **Receiver-side slots name organizations.** `beneficiary`, `recipient`, `redeemable_by` and `issued_to` keep their Party range; their definitions now name organizations. Two Party-ranged slots do not apply to organizations and say so in their definitions: `data_subject`, because data protection law protects natural persons, and `subject` on profiles and scoring events, because those observe persons and groups. `identity_documents`, inherited from Party, also covers documents such as a certificate of registration.
4. **Organization gains `economic_activities` and `dissolution_date`.** `economic_activities` is a repeatable CodedValue with no code list bound in the core; ISIC is the international reference, and application profiles bind NACE, NAICS or a national classification. `dissolution_date` is the date the organization ceased to exist or was removed from the register, the counterpart of `formation_date`. A size class (micro, small, medium) is deferred: thresholds differ by jurisdiction and no single definition is useful across them.
5. **Sole proprietorships follow the jurisdiction.** The core admits two patterns and says when each applies:
   - The **person pattern**: a Person with the business identifier (an IdentifierAssignment from the business register), the trading name (a NameUsage with name use `trading`) and the person's `industry`. This fits where the business has no existence separate from the person.
   - The **organization pattern**: an Organization whose `legal_form` is a sole proprietorship, linked to the person through an InstitutionalRole. This fits where the jurisdiction's register treats the business as a body distinct from the person.

   An application profile states which pattern a jurisdiction uses. Data in either pattern is valid against the core, and the role link lets a consumer that receives both convert one into the other.
6. **A record is a person or an organization, never both.** No concept, in the core or in a local extension, should be a subtype of both Person and Organization.

## Alternatives considered

- **Widen the receiver-side slots to a URI that admits persons, groups and organizations, leaving Party unchanged.** Rejected. It would leave four slots without type checking and spread the same list of admitted kinds across several definitions, while ADR-008 had already identified Party as the place to change.
- **Keep Organization outside Party.** Rejected. Company subsidies, grants to cooperatives and business credentials would remain unrepresentable, or each country would invent its own term for them.
- **Record a sole proprietorship always as a Person, or always as an Organization.** Rejected. Either rule contradicts some jurisdiction's law, and a country that disagrees would have to overload or fork the term. The core states the criterion; profiles apply it.
- **A concept that is both a Person and an Organization for sole proprietorships.** Rejected. PublicSchema maps Person and Organization exactly to `foaf:Person` and `foaf:Organization`, which FOAF declares disjoint, so such a record is inconsistent under those mappings. A person also outlives, and can run several, successive businesses; merging the two would confuse `dissolution_date` with `date_of_death` and lose which business a registration belongs to. Person carries sensitivity annotations for personal data, which a business-register reading of the same record would drop.
- **A bound vocabulary for economic activity.** Rejected. Countries use national adaptations of ISIC, NACE or NAICS, and binding one in the core would force every other country to override it.

## Consequences

Party now has three direct subtypes: Person, Group and Organization. Adopters who wrote SHACL or code on the assumption that every Party is a person or a group of persons must revisit it. ADR-008 named this cost and noted that it is free while no adopter depends on the v2 schema.

Party and Agent still share subtypes, now Person and Organization, so they remain non-disjoint. The type hierarchy page shows Organization under Agent with a `+Party` badge, as it shows Person under Party with a `+Agent` badge.

Organization inherits `identity_documents` from Party. Its definition and IdentityDocument's definition now cover organizations.

Records that link a program to a company use the same Enrollment, Entitlement, PaymentEvent and credential concepts as records for persons and households. Programs that serve only persons or households narrow `beneficiary` in their application profile.

## References

- [ADR-008](008-agent-organization.md): Agent supertype and Organization concept
- [ADR-020](020-registry-foundations.md): identifier assignments and name usages
- [ADR-025](025-organizations-legal-personality-and-authority.md): legal form, public organizations and institutional roles
- W3C Registered Organization Vocabulary: `rov:orgActivity`
- SEMIC Core Business Vocabulary: `legal:LegalEntity`
- UN Statistics Division, ISIC Rev.4
- UK Companies House Public Data API: `sic_codes`, `date_of_cessation`
- FOAF: `foaf:Person` and `foaf:Organization` are disjoint classes
