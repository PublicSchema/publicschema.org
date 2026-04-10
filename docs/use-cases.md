# Use Cases

PublicSchema provides common definitions for public service delivery. There are many ways to use it, from aligning vocabulary codes in spreadsheets to issuing verifiable credentials. This page describes concrete scenarios where PublicSchema helps programs coordinate, share data, and reach the people they serve.

## Contents

- [Cross-program deduplication across sectors](#cross-program-deduplication-across-sectors)
- [Portable credentials for displaced populations](#portable-credentials-for-displaced-populations)
- [Standardized reporting across programs and donors](#standardized-reporting-across-programs-and-donors)
- [Interoperable system procurement](#interoperable-system-procurement)
- [Birth registration to multi-sector enrollment](#birth-registration-to-multi-sector-enrollment)
- [School-to-work transition tracking](#school-to-work-transition-tracking)
- [Point-of-service eligibility verification](#point-of-service-eligibility-verification)
- [Disaster response coordination](#disaster-response-coordination)
- [Cross-country program comparison and policy research](#cross-country-program-comparison-and-policy-research)
- [API harmonization across a federation](#api-harmonization-across-a-federation)
- [Which artifacts matter for which use case](#which-artifacts-matter-for-which-use-case)

## Cross-program deduplication across sectors

**Who:** A government running social protection, school feeding, and health insurance as separate programs, each on a different system.

**The problem:** Each system has records for the same families, described differently. The education ministry's database calls them "students," the health system calls them "patients," and the cash transfer system calls them "beneficiaries." There is no reliable way to check whether a person is already enrolled elsewhere.

**How PublicSchema helps:** The integration team maps each system's fields to PublicSchema properties (given_name, national_id, date_of_birth, enrollment_status). A shared registry can then match records across systems using a common vocabulary. No system needs to change its internal data model.

**Key artifacts:** Concepts (Person, Enrollment), properties, vocabulary codes, system mappings.

## Portable credentials for displaced populations

**Who:** A refugee registered in one country, arriving in a host country that needs to verify identity and prior service enrollment.

**The problem:** The person's records exist in the origin country's systems, but the host country has no access to those systems. Calling back to the origin system may be impractical or impossible. The person needs a way to prove who they are and what services they've received.

**How PublicSchema helps:** The origin country issues an SD-JWT Verifiable Credential using PublicSchema's credential types (IdentityCredential, EnrollmentCredential). The host country can verify the credential offline because it uses a shared schema. Selective disclosure lets the person reveal only what is needed (name, date of birth, prior enrollment) without exposing sensitive details.

**Key artifacts:** Credential types, JSON-LD context, selective disclosure rules, JSON Schemas.

## Standardized reporting across programs and donors

**Who:** A donor, coordinating body, or government dashboard aggregating data across multiple programs, sectors, or countries.

**The problem:** Every program reports using its own codes and field names. One uses "ACTV" for active enrollment, another uses "1," a third uses "enrolled." Aggregating numbers across programs requires manual translation every reporting cycle.

**How PublicSchema helps:** The coordinating body defines a reporting template that references PublicSchema vocabulary codes (enrollment-status, payment-status, delivery-channel). Each program maps its internal codes once. From that point on, aggregation is mechanical.

**Key artifacts:** Vocabulary codes, concept definitions, property definitions.

## Interoperable system procurement

**Who:** A government procuring a new registry, MIS, or case management system in any sector.

**The problem:** RFPs specify "the system must be interoperable," which is too vague to evaluate. Vendors interpret it however they like. There is no concrete standard to test against.

**How PublicSchema helps:** The RFP references PublicSchema directly: "The system must export Person records with these properties: given_name, family_name, date_of_birth, national_id. Status fields must use codes from PublicSchema vocabularies." This works whether you are procuring a social registry, a student information system, or a health facility database. Vendors get a concrete target; evaluators get something testable.

**Key artifacts:** Concept definitions, property inventory, vocabulary definitions, JSON Schemas.

## Birth registration to multi-sector enrollment

**Who:** A civil registration authority issuing birth certificates, connected to programs that auto-enroll newborns (health insurance, child grants, immunization tracking).

**The problem:** A birth is registered, but each downstream program needs to be notified separately, using its own intake format. Bilateral integrations between civil registration and each program are expensive to build and maintain.

**How PublicSchema helps:** The civil registry publishes a record using PublicSchema's Person properties (date_of_birth, sex, location). The health ministry picks up what it needs for immunization scheduling. The social protection system uses the same record to auto-enroll the child in a child grant. Each downstream system consumes from the same canonical representation instead of requiring its own integration.

**Key artifacts:** Concepts (Person, Identifier), properties, vocabulary codes, JSON Schemas.

## School-to-work transition tracking

**Who:** A ministry of education and a ministry of labor, each with their own systems, trying to track outcomes for youth programs.

**The problem:** The education system tracks students enrolled in vocational training. The labor ministry tracks participants in employment programs. Neither system knows about the other. There is no way to measure whether vocational training graduates actually enter employment programs.

**How PublicSchema helps:** Both systems map their data models to PublicSchema's Person and Enrollment concepts. A policy team can then link records across systems and measure outcomes: of the students who completed vocational training, how many enrolled in an employment program within six months? The shared vocabulary makes the join possible without merging databases.

**Key artifacts:** Concepts (Person, Enrollment, Program), properties, vocabulary codes.

## Point-of-service eligibility verification

**Who:** A payment agent, health facility, or school verifying a person's eligibility at the point of service.

**The problem:** Verifying eligibility currently requires a live connection to the central registry. In remote areas or during system outages, service delivery stalls because eligibility cannot be confirmed.

**How PublicSchema helps:** The person holds a verifiable credential on their phone or smart card. At the point of service, the agent's device verifies the credential signature and checks that enrollment_status is "active" and the entitlement amount matches. The verification works offline because it is cryptographic, not a database lookup. Personal details beyond what is needed for the transaction stay hidden through selective disclosure.

**Key artifacts:** Credential types, selective disclosure rules, JSON Schemas.

## Disaster response coordination

**Who:** Multiple agencies responding to a natural disaster: government, UN agencies, and NGOs, each registering affected populations independently.

**The problem:** Three organizations are registering affected families in the same district using different intake forms and systems. There is no way to tell whether a family has already been registered by another agency, leading to duplicated aid for some and gaps for others.

**How PublicSchema helps:** By aligning data collection to PublicSchema's Person and Household concepts, a coordination body can deduplicate across all registration lists, identify families that no agency has reached yet, and allocate resources without double-counting.

**Key artifacts:** Concepts (Person, Household, Group, GroupMembership, Location), properties, vocabulary codes, JSON Schemas.

## Cross-country program comparison and policy research

**Who:** A policy analyst, researcher, or international organization comparing public service delivery programs across countries.

**The problem:** Each country defines concepts like "enrollment," "entitlement," and "grievance" differently. Comparison requires manually interpreting each country's documentation, which is inconsistent and often incomplete.

**How PublicSchema helps:** The analyst uses PublicSchema's concept and property inventory as a structured framework for comparison. For each country and sector, they map the local program's data model against PublicSchema. The result makes divergences visible and nameable: Country A collects household GPS coordinates, Country B does not. Country A defines "inactive" enrollment as "suspended," Country B uses it to mean "completed."

**Key artifacts:** Concept definitions (with multilingual descriptions), property inventory, vocabulary definitions, system mappings.

## API harmonization across a federation

**Who:** A national or regional system aggregating data from multiple agencies, ministries, or levels of government.

**The problem:** Five agencies each expose a REST API: social registry, education MIS, health information system, civil registry, agricultural extension database. Field names and value codes differ across all five. Building custom adapters for each API is expensive and fragile.

**How PublicSchema helps:** The federation mandates that all APIs align field names to PublicSchema properties and use PublicSchema vocabulary codes. Each agency keeps its internal schema; they just add a PublicSchema-aligned API surface. The federation layer speaks one language instead of five.

**Key artifacts:** Properties (as shared field names), vocabulary codes (as shared value sets), JSON Schemas (for contract validation).

## Which artifacts matter for which use case

| Use case | Concepts | Properties | Vocabularies | JSON Schemas | JSON-LD | Credentials |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Cross-program deduplication | x | x | x | | | |
| Portable credentials | x | x | | x | x | x |
| Standardized reporting | x | x | x | | | |
| System procurement | x | x | x | x | | |
| Birth registration cascade | x | x | x | x | | |
| School-to-work tracking | x | x | x | | | |
| Point-of-service verification | | | | x | | x |
| Disaster response coordination | x | x | x | x | | |
| Cross-country comparison | x | x | x | | | |
| API federation | | x | x | x | | |

Most use cases require only concepts, properties, and vocabulary codes. JSON-LD and Verifiable Credentials are needed for a subset of scenarios. **Where to start:**

- To align value codes without changing your data model, see the [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/).
- To map fields between existing systems, see the [Interoperability & Mapping Guide](/docs/interoperability-guide/).
- To design a new system for compatibility, see the [Data Model Design Guide](/docs/data-model-guide/).
- To use JSON-LD contexts or issue verifiable credentials, see the [JSON-LD & VC Guide](/docs/jsonld-vc-guide/).
