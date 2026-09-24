# ADR-025: Organizations carry legal form, public status and acting authority

**Status:** Accepted

## Context

[ADR-008](008-agent-organization.md) introduced Organization with a minimum property set (`name`, `identifiers`, `location`) and deferred richer properties: `parent_organization`, `legal_form`, `jurisdiction`, multi-site `locations`, contact points and a PractitionerRole layer. Government and agricultural registries need several of them. Business and cooperative registers record a legal form and a formation or registration date. Public administration records name the body that received an application, decided a case or took a measure. Registers of public bodies record which organizations are part of, supervised by or affiliated with which others.

Two shapes were available for legal personality. A separate LegalEntity class, following SEMIC Core Business, would sit beside Organization and hold legal form and formation. Alternatively, Organization can carry those facts directly. SEMIC Core Business uses LegalEntity for bodies with legal rights and obligations; PublicSchema's Organization already covers public and private bodies that can act in a delivery process, and it is the range of every organization-valued slot in the vocabulary.

Records also name organizations in several roles. The body that owns a register, the body that issued an identifier, the body that attests a statement and the body that decided a case are different roles, and a single generic "organization" slot would hide which one a record means.

## Decision

1. **No LegalEntity class.** Organization carries `legal_form` (a CodedValue under the law the organization was formed under, such as a limited company, cooperative or statutory body) and `formation_date` (the existing slot, reused). Organization has a close mapping to `legal:LegalEntity`. An organization without legal personality, such as a government department, is still an Organization; leaving `legal_form` empty does not assert that it has none. A trust or nominee arrangement without legal personality is a `LegalArrangement`, recorded in [ADR-023](023-government-qualified-relationships.md).
2. **PublicOrganization specializes Organization** for bodies a law or other legal framework places in the public sector, at any level of government. It carries `legal_resources` (the legal provisions it relies on), `public_functions` and `competence_areas`. Being public does not settle whether the body has its own legal personality. It is an exact mapping of `cpov:PublicOrganisation`.
3. **Relationships between organizations and roles in them are dated records**, not properties of Organization:
   - `InstitutionalRelationship` relates two organizations (`institution_from`, `institution_to`) with a type that fixes the direction and meaning, such as part of, supervised by, affiliated with or member of. It covers what ADR-008 deferred as `parent_organization`. None of these relationships expresses ownership or control by itself; ownership is an `OwnershipInterest`.
   - `InstitutionalRole` assigns a person, group or organization (`role_actor`, a URI with those admitted kinds) to a role in an organization, such as member, director or officer. Membership of a producer organization or cooperative is an institutional role with a member role type.
   - `RepresentationRole` records that a person or organization (`representative`, an Agent) acts on behalf of a person, organization, group or legal arrangement (`represented`, a URI with those admitted kinds) within a stated scope.
   - `PracticeRole` records a person practicing a profession for an organization, optionally at service points. It is the practitioner layer ADR-008 deferred; an office held by a person or an organization is an InstitutionalRole instead.
   - Contact points and names over time are `ContactPoint` and `NameUsage` records about the organization, recorded in [ADR-020](020-registry-foundations.md).
4. **One slot for the organization acting in an event.** `authority` (range Organization) names the organization responsible for the act or event a record describes: the body that receives an application, decides a case, reviews an appeal, inspects a subject, takes a measure, changes a record's standing or carries out an organizational change. It is used on ServiceApplication, AdministrativeDecision, AdministrativeAppeal, OrganizationalChangeEvent, ComplianceAssessment, RegulatoryAction and RecordLifecycleEvent, and each class states which role applies.
5. **Separate slots for other organizational roles.** `assertion_authority` is the organization accountable for a statement (EvidenceAssertion, SubjectMatchAssertion), which can differ from the person or software that entered it and from the body that acted in the event the statement describes. `register_owner`, `registration_authority`, `identifier_issuer`, `certifying_organization` and `service_competent_authorities` keep their own names because each is a standing responsibility with its own meaning, not an act.

This amends ADR-008's deferral of legal form, parent organization, contact points and the practitioner layer. Multi-site `locations` and a jurisdiction property on Organization stay deferred: sites are service points or provider sites with their own identity, and `competence_areas` on PublicOrganization covers the areas a public body serves.

## Alternatives considered

- **A LegalEntity class beside Organization.** Rejected. Every organization-valued slot would have to choose between the two or accept both, and a registry record for a cooperative would need two linked records for one body. The distinction LegalEntity draws (legal personality) is a fact about an organization, which `legal_form` records.
- **LegalEntity as a subclass of Organization.** Rejected. Whether a body has legal personality depends on the law it was formed under and can change with reorganization; a class boundary would force re-typing the record when that happens.
- **One authority slot per class** (for example a deciding authority on decisions and a receiving authority on applications). Rejected. The slots would share one meaning, the organization responsible for the act, and differ only by the class that carries them. The class definition already says which act it is.
- **One slot for every organizational role, including statements and standing responsibilities.** Rejected. The organization that attests a statement is often not the one that acted, and register ownership or identifier issuance is a standing responsibility rather than an act. Merging them would lose which role a record means.
- **`parent_organization` on Organization.** Rejected in favour of InstitutionalRelationship. Real hierarchies change over time and have several kinds (part of, supervised by, affiliated with), which a single undated slot cannot express.

## Consequences

Organization gains two optional slots and keeps its concept identity. Existing Organization payloads remain valid.

Records that need to distinguish the organization acting in an event from the one attesting it use both `authority` and `assertion_authority` on the relevant records. Consumers looking for "who decided" read `authority` on the decision, not on the evidence.

Applicants, appellants and role actors that can be groups use URI slots with their admitted kinds stated in the definition, as [ADR-020](020-registry-foundations.md) records for actor ranges. Representation, submission and practice use typed Agent or Person ranges.
