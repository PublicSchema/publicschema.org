# PublicSchema: Common Definitions for Public Service Delivery

**publicschema.org**

## The problem

Service delivery systems collect and manage similar data about the same people, but they model it differently. A person in one system has a "gender" field with codes 1/2/3. Another uses "M/F/O". A third uses "male/female/non-binary/prefer_not_to_say".

This isn't just a technical annoyance. When systems can't understand each other's data, organizations can't:

- Identify who is receiving benefits across programs
- Refer beneficiaries between services
- Consolidate reporting across agencies
- Detect duplication or gaps in coverage

The usual response is to build integration middleware that translates between systems case by case. This is expensive, fragile, and doesn't scale.

Worse, many of these mappings are not just expensive but lossy. When one system tracks gender with three numeric codes and another distinguishes "non-binary" and "prefer_not_to_say," no translation can preserve the original meaning. Information is lost, and decisions downstream are made on distorted data.

## The insight

The structural differences between systems are surprisingly small. When we mapped 6 major systems across social protection (OpenSPP, openIMIS, DCI, DHIS2, FHIR R4, OpenCRVS), we found that all 6 had some version of Person, Enrollment, and Payment. The structures converge. The vocabularies diverge.

The real interoperability challenge is vocabulary alignment: agreeing on what values mean, not what fields exist. Shared definitions don't just reduce the effort required to connect systems; they make accurate data exchange possible in the first place.

## The vision

An open, composable vocabulary of concepts and properties for public services. Think schema.org, but for public service delivery.

Schema.org doesn't tell websites what data to collect. It provides a shared language: "here's what Person means, here are properties that can describe a Person, here are standard values for gender." Websites adopt the terms that apply to them.

Similarly, PublicSchema provides:

- **Concepts**: semantic entities with clear, human-readable definitions. A Person is a human being interacting with a service. An Enrollment is the act of registering someone into a program. These definitions are written for policy practitioners, not developers.
- **Properties**: named, typed fields that apply to one or more concepts. `date_of_birth` applies to Person. `start_date` applies to Enrollment, Entitlement, and Program. Properties are defined once and reused, keeping definitions consistent.
- **Vocabularies**: controlled value sets. Where international standards exist (ISO 5218 for gender, ISO 3166 for country, ISO 4217 for currency), we reference them. Where they don't (enrollment status, grievance type, benefit modality), we define a canonical set with clear definitions.
- **Vocabulary mappings**: how specific systems' codes correspond to canonical values. OpenIMIS gender code "M" = ISO 5218 "male". This is where the real interoperability work happens.

Every element gets a stable URI. Everything is optional. Systems adopt what they need.

A critical design target: the vocabulary must be directly usable as the schema layer for **Verifiable Credentials**. As governments move toward digitally signed, tamper-proof claims (proof of enrollment, proof of identity, proof of payment), they need a shared vocabulary that credential issuers and verifiers both understand. A Verifiable Credential that says "this person's enrollment_status is active" only works if both parties agree on what "enrollment_status" and "active" mean, and can resolve those terms to stable, machine-readable definitions. That is exactly what this vocabulary provides. By designing for VC compatibility from the start, the vocabulary becomes infrastructure not just for system integration, but for trusted, portable government service records.

## Design principles

**Semantic, not structural.** Concepts carry meaning. A Person is not a bag of fields. Definitions are written for domain practitioners, not for software developers. The vocabulary should be legible to a social protection policy officer.

**Properties are independent (until they aren't).** A property like `start_date` is defined once and used across multiple concepts. This avoids redundancy and mirrors how domain experts think. However, when a shared property needs concept-specific value sets (e.g., `status` means different things on an Enrollment vs. a Grievance), the property definition specializes rather than pretending the differences don't exist. FHIR learned this the hard way with `status` across resources.

**Temporally grounded.** Almost everything in public service delivery is time-bounded: enrollment periods, benefit cycles, eligibility windows, payment schedules. A status snapshot without a validity period is incomplete. Concepts and properties must support temporal context (when was this true? for how long?) as a first-class concern, not an afterthought.

**Vocabularies reference standards.** Never invent what already exists. For gender, marital status, country, currency: adopt existing international standards and map system-specific codes to them. Only define new value sets for domain-specific concepts where no standard exists.

**Everything is optional.** There is no "you must implement these fields to be compliant." Systems adopt the concepts, properties, and vocabularies that apply to them. The vocabulary is descriptive, not prescriptive.

**Evidence-based.** Convergence data (which systems implement which concepts and properties) informs priorities. A property present in 6 out of 6 systems is worth standardizing before one present in 2 out of 6. Real-world adoption drives the roadmap.

**VC-ready.** Vocabulary definitions must work as the schema layer for Verifiable Credentials. This means stable URIs that resolve to machine-readable definitions, JSON-LD contexts that map property names to those URIs, and vocabulary values that can serve as credential claim values. Credential schemas use SD-JWT VC (Selective Disclosure JWT Verifiable Credentials) format, since government credentials often contain sensitive personal data that should not be fully revealed in every presentation.

**Incremental.** Start with what we know, get it right, extend when ready. No grand architecture upfront.

## Relation to existing efforts

A landscape review of 10+ initiatives confirmed that no existing project provides a shared semantic vocabulary for the social protection delivery lifecycle. Several adjacent efforts exist at different layers, and PublicSchema is designed to complement, not compete with, each of them.

### Where PublicSchema sits

| Layer | What exists | What's missing |
|---|---|---|
| Trust and transport | EBSI, OpenID4VC, W3C VC Data Model | No domain vocabulary inside credentials (though EBSI's JSON Schemas for person identity, social security coordination, and education credentials informed property design; see below) |
| Identity attributes | EU Core Person Vocabulary, W3C Citizenship Vocabulary | Covers name/birth/citizenship only, not delivery data |
| Service catalogues | CPSV-AP (EU), HSDS/Open Referral, schema.org/GovernmentService | Describes what services exist, not who receives what |
| API interoperability | DCI, GovStack | Interface contracts between systems, not semantic vocabulary |
| Statistical measurement | ILO/World Bank ASPIRE, ILOSTAT | Counts and indicators, not data models for exchange |
| **Delivery lifecycle vocabulary** | **Nothing** | **This is the PublicSchema gap** |

### Specific initiatives

**DCI** (Digital Convergence Initiative) is the closest initiative and the most important relationship. DCI builds API interoperability standards between social protection systems (social registry, payment, civil registration interfaces), jointly steered by GIZ, ILO, and the World Bank. PublicSchema is the semantic vocabulary layer that DCI's API standards implicitly need but have not built. DCI defines how data flows between systems; PublicSchema defines what the data means. The two are complementary, and DCI is a natural partner.

**EU Core Vocabularies (SEMIC/Interoperable Europe)** are the closest technical precedent for how to build this. The Core Person Vocabulary, Core Location Vocabulary, and Core Public Service Vocabulary Application Profile (CPSV-AP) are minimal, reusable RDF vocabularies for EU public administration, published with SHACL validation shapes under CC-BY 4.0. PublicSchema should align with these where they overlap (person, location, address) rather than reinventing definitions. However, the EU Core Vocabularies cover identity and service cataloguing, not the delivery lifecycle (enrollment, entitlement, payment, grievance).

**GovStack** defines building block specifications for digital government services (identity, payments, messaging). PublicSchema is the data model counterpart: where GovStack says "you need a payment building block," PublicSchema defines what payment data looks like across systems and how to translate between them. GovStack explicitly lacks a cross-cutting semantic layer, which is the gap PublicSchema addresses.

**FHIR** is the health sector's interoperability standard, combining a data model with an API spec. We take inspiration from its approach (resources, extensions, value sets, maturity levels) but target the public services space. FHIR's vocabulary governance model is a useful reference.

**Schema.org** is the direct model for how we structure and publish the vocabulary. It succeeded because it was simple, optional, and useful from day one. Schema.org's government types (GovernmentService, GovernmentOrganization) are extremely thin and SEO-oriented; they do not model delivery data.

**HSDS/Open Referral** is the standard for service directories ("what services exist where"). PublicSchema is for delivery data ("who receives what, when, how"). A service described in HSDS could be the same service described by a PublicSchema Program, but the two address opposite ends of the lifecycle.

**W3C Verifiable Credentials** (VC Data Model 2.0) provide the trust layer. Our vocabulary, published as a JSON-LD context with resolvable URIs, serves as the schema that makes service delivery credentials interoperable across borders and systems. Related specs: SD-JWT VC for selective disclosure, OpenID4VCI/VP for credential issuance and presentation, and EBSI for the EU's approach to credential infrastructure.

**EBSI JSON Schemas** (European Blockchain Services Infrastructure) are the EU's official Verifiable Credential schemas. While EBSI operates at the trust and transport layer (not the domain vocabulary layer), its credential schemas for person identity (eIDAS PID), social security coordination (Portable Document A1), health insurance (EHIC), and education (Europass EDC / ELM 3.2) model many of the same entities PublicSchema covers. We used EBSI schemas as a design input to identify missing properties on Person (birth names, preferred name, patronymic), Address (house number, building name), Identifier (scheme metadata, issuing jurisdiction), Enrollment (governing jurisdiction), and Entitlement (document expiry distinct from entitlement period). EBSI is not part of the 6-system convergence analysis, but its legally grounded, production-deployed schemas provide useful validation of property choices.

**Trust registries** are a companion concern. The vocabulary defines what terms mean, but verifiers also need to know which issuers are authoritative for which claims. This is out of scope for the vocabulary itself, but any deployment will need a trust registry alongside it (see OpenID Federation or the EBSI trust model as reference points).

## Starting point: social protection

We begin with social protection because:

- It is a well-understood domain with active digital transformation across many countries
- Multiple open-source systems exist alongside emerging standards
- We already have convergence data from 6 systems covering 18+ concepts
- The interoperability pain is immediate and concrete

Initial concept coverage includes people and identity (Person, Household, Family, Group, Identifier, Address, Location), program delivery (Program, Enrollment, Entitlement, EligibilityDecision, Instrument, Profile with SocioEconomicProfile / FunctioningProfile / AnthropometricProfile subtypes, ScoringRule, ScoringEvent), payments (PaymentEvent), and accountability (Grievance, Referral).

Concepts that need further exploration based on practitioner feedback:

- **Targeting and conditionality.** Most SP programs enroll people who meet criteria: proxy means test scores, categorical indicators (pregnant women, children under 5), geographic prioritization. These are core business logic, not edge cases. Socioeconomic scoring may warrant its own concept rather than living as an annotation on EligibilityDecision.
- **Benefit modality and transfer value.** Whether a program delivers cash, food, vouchers, or in-kind goods is fundamental. Transfer values (per-person, per-household, scaled by household size) are tracked by every system.
- **Responsible actors.** Case workers, supervising officers, implementing partners: there is almost always a responsible staff member or organization attached to an enrollment, payment, or grievance.
- **Appeals and redress.** Distinct from initial grievance filing. The appeals subprocess is where much of the difficult data lives.

As the vocabulary matures, it will extend to adjacent domains: civil registration, health referrals, education, humanitarian response, land administration. The structure is the same; only the concepts and vocabularies change.

## Versioning and stability

Stable URIs are essential for VC compatibility: a credential issued today must remain verifiable years from now. The versioning strategy borrows from FHIR's maturity model:

- **Draft**: concept or property is proposed, open for feedback, may change significantly.
- **Trial use**: definition is stable enough for early adopters, but breaking changes are still possible with notice.
- **Normative**: definition is locked. Changes require a new URI, not an edit to the existing one.

Each concept and property carries its maturity level. The JSON-LD context is versioned (e.g., `https://publicschema.org/v1`, `https://publicschema.org/v2`), with older versions remaining resolvable indefinitely.

## Governance

The project starts under a single maintainer (benevolent dictator model) to move quickly and make opinionated decisions. Early feedback is actively sought from domain experts, system implementers, and standards bodies.

As adoption grows, governance will evolve: first to an advisory group of contributors and domain experts, then potentially to a formal multi-stakeholder organization. The key governance questions to resolve over time:

- Who approves new concepts and properties?
- How are disputes over definitions arbitrated?
- Who maintains the canonical URIs and JSON-LD contexts?

The right governance structure will emerge from who actually uses and contributes to the vocabulary. Designing it upfront before there are real stakeholders would be premature.

## Roadmap

### Phase 1: Vocabulary foundation

- Define concepts and properties with stable URIs, following the schema.org pattern
- Write each definition for domain practitioners, not developers
- Publish as a reference website where each concept and property has its own page
- Identify 1-2 champion systems for early validation

### Phase 2: Vocabulary standards and mappings

- Research and adopt existing international standards for each value set
- Define canonical value sets for domain-specific vocabularies where no standard exists
- Build cross-system vocabulary mappings (system code X = canonical code Y)
- Pilot with at least one country deployment to validate real-world fit

### Phase 3: Adoption and extension

- Formalize governance based on active contributors
- Validate mappings with system implementers and country deployments
- Document real-world adoption patterns
- Extend to adjacent public service domains
