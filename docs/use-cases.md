# Use Cases

PublicSchema provides common definitions for public services and government registries. There are many ways to use it, from aligning vocabulary codes in spreadsheets to issuing verifiable credentials. This page describes concrete scenarios where PublicSchema helps programs and registries coordinate, share data, and reach the people they serve.

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
- [Linking the farm register to land records](#linking-the-farm-register-to-land-records)
- [One business, many registers](#one-business-many-registers)
- [Targeting agricultural input subsidies to registered farmers](#targeting-agricultural-input-subsidies-to-registered-farmers)
- [Which artifacts matter for which use case](#which-artifacts-matter-for-which-use-case)

## Cross-program deduplication across sectors

**Who:** A government running social protection, school feeding, and health insurance as separate programs, each on a different system.

**The problem:** Each system has records for the same families, described differently. The education ministry's database calls them "students," the health system calls them "patients," and the cash transfer system calls them "beneficiaries." There is no reliable way to check whether a person is already enrolled elsewhere. Even when fields can be matched by name, divergent codes make comparison unreliable: "active" in one system may not mean the same thing as "active" in another.

**How PublicSchema helps:** The integration team maps each system's fields to PublicSchema properties (given_name, identifiers, date_of_birth, enrollment_status). A shared registry can then match records across systems using a common vocabulary. No system needs to change its internal data model.

**Key artifacts:** Concepts (Person, Enrollment), properties, vocabulary codes, system mappings.

## Portable credentials for displaced populations

**Who:** A refugee registered in one country, arriving in a host country that needs to verify identity and prior service enrollment.

**The problem:** The person's records exist in the origin country's systems, but the host country has no access to those systems. Calling back to the origin system may be impractical or impossible. The person needs a way to prove who they are and what services they've received.

**How PublicSchema helps:** The origin country issues an SD-JWT Verifiable Credential using PublicSchema's credential types (IdentityCredential, EnrollmentCredential). The host country can verify the credential offline because it uses a shared schema. Selective disclosure lets the person reveal only what is needed (name, date of birth, prior enrollment) without exposing sensitive details.

**Key artifacts:** Credential types, JSON-LD context, selective disclosure rules, JSON Schemas.

## Standardized reporting across programs and donors

**Who:** A donor, coordinating body, or government dashboard aggregating data across multiple programs, sectors, or countries.

**The problem:** Every program reports using its own codes and field names. One uses "ACTV" for active enrollment, another uses "1," a third uses "enrolled." Aggregating numbers across programs requires manual translation every reporting cycle. When these translations are lossy (because one program's codes don't map cleanly to another's), the aggregated numbers are unreliable.

**How PublicSchema helps:** The coordinating body defines a reporting template that references PublicSchema vocabulary codes (enrollment-status, payment-status, delivery-channel). Each program maps its internal codes once. From that point on, aggregation is mechanical.

**Key artifacts:** Vocabulary codes, concept definitions, property definitions.

## Interoperable system procurement

**Who:** A government procuring a new registry, MIS, or case management system in any sector.

**The problem:** RFPs specify "the system must be interoperable," which is too vague to evaluate. Vendors interpret it however they like. There is no concrete standard to test against.

**How PublicSchema helps:** The RFP references PublicSchema directly: "The system must export Person records with these properties: given_name, family_name, date_of_birth, identifiers. Status fields must use codes from PublicSchema vocabularies." This works whether you are procuring a social registry, a student information system, or a health facility database. Vendors get a concrete target; evaluators get something testable.

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

## Linking the farm register to land records

**Who:** An agriculture ministry building a farm register, and a land agency that keeps the cadastre and records of land rights.

**The problem:** Both agencies talk about "parcels", but they mean different things. The farm register records the fields a farm actually works this season; the cadastre records surveyed units and the rights attached to them. A farmer may rent land from several owners, share common grazing, or work land whose rights are informal. When the two registers are joined naively, a farm's use of a field gets read as ownership, or a tenant disappears because the cadastre only knows the owner.

**How PublicSchema helps:** The draft [agriculture](/concepts/?domain=agri) and [land](/concepts/?domain=land) domains keep these statements apart. A [Farm](/agri/Farm/) uses an [AgriculturalParcel](/agri/AgriculturalParcel/), a land-use unit, through a dated [HoldingParcelLink](/agri/HoldingParcelLink/) that records the used area, the period and the arrangement the farm reports (owned, rented, sharecropped), without asserting a legal right. The parcel can name the [LandSpatialUnit](/land/LandSpatialUnit/) records, such as cadastral parcels, that it lies on, even when their boundaries do not coincide. On the land side, a [LandTenureAssertion](/land/LandTenureAssertion/) records who holds or claims a right over a land administrative unit, with its tenure category and evidence, without deciding between competing claims. Each agency keeps its own records; the shared definitions let an analyst follow a farmed field to the cadastral units under it and report, for example, how much farmed land has no recorded tenure, without collapsing use into ownership.

**Key artifacts:** Concepts (Farm, AgriculturalParcel, HoldingParcelLink, LandSpatialUnit, LandTenureAssertion), properties (land_spatial_units, parcel_tenure), vocabulary codes (land tenure, tenure category).

## One business, many registers

**Who:** A business registry, a tax authority, and an environmental regulator that each hold records about the same companies.

**The problem:** A company is registered once at the business registry, again for each tax it pays, and again when one of its sites needs an environmental permit. Each agency assigns its own number and keeps its own status. When a company merges, closes, or changes its name, the other agencies find out late or not at all. Joining the registers on company name produces false matches, and there is no record of who decided that two records describe the same company.

**How PublicSchema helps:** Each agency's record is modeled as a [Registration](/Registration/) of the same [Organization](/Organization/), naming the authority, jurisdiction, and purpose. A [TaxRegistration](/tax/TaxRegistration/) is one registration per tax. An environmental permit is an [Authorization](/Authorization/) whose authorized object is an [EnvironmentalFacility](/environment/EnvironmentalFacility/), so the site keeps its identity when the operator changes. Each agency's number is an [IdentifierAssignment](/IdentifierAssignment/) with its issuer and validity period. When agencies link their records, a [SubjectMatchAssertion](/SubjectMatchAssertion/) records who judged the match and how, without merging the records. Mergers and splits are recorded as an [OrganizationalChangeEvent](/OrganizationalChangeEvent/), so earlier companies and their past acts stay identifiable.

**Key artifacts:** Concepts (Organization, Registration, TaxRegistration, Authorization, EnvironmentalFacility, IdentifierAssignment, SubjectMatchAssertion, OrganizationalChangeEvent), properties, vocabulary codes (organization type).

## Targeting agricultural input subsidies to registered farmers

**Who:** An agriculture ministry running a fertilizer and seed subsidy, delivered through vouchers redeemed at agro-dealers, with support from the social protection agency on targeting.

**The problem:** The subsidy needs to reach farmers who are actually registered and eligible, once per season. Eligibility lists are drawn from the farm register, but vouchers are managed in a separate payment system and redemptions are reported by dealers in spreadsheets. Nobody can say with confidence which registered farmers received inputs, which products were collected, or whether the same farmer was served twice under different numbers.

**How PublicSchema helps:** The farmer's standing comes from a [FarmerRegistration](/agri/FarmerRegistration/) that names the farms it covers. The subsidy is an [sp/Program](/sp/Program/) with an [sp/EligibilityDecision](/sp/EligibilityDecision/) and an [sp/Enrollment](/sp/Enrollment/) for each farmer, the same pattern social protection uses for cash transfers. Entitlements are fulfilled through a [Voucher](/Voucher/) issued to the farmer, and each dealer visit is a [VoucherRedemption](/VoucherRedemption/) listing the items and quantities collected. The approved product list can be described with [AgriculturalInputProduct](/agri/AgriculturalInputProduct/), each with its regulatory input category. Because farmer, program, and voucher use shared definitions, the ministry can reconcile the register, the voucher system, and dealer reports, and the social protection agency can reuse its deduplication and targeting tools.

**Key artifacts:** Concepts (FarmerRegistration, Farm, Program, EligibilityDecision, Enrollment, Voucher, VoucherRedemption, AgriculturalInputProduct), properties, vocabulary codes (voucher status, agricultural input category), JSON Schemas.

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
| Farm register and land records | x | x | x | | | |
| One business, many registers | x | x | x | | | |
| Agricultural input subsidies | x | x | x | x | | |

Most use cases require only concepts, properties, and vocabulary codes. JSON-LD and Verifiable Credentials are needed for a subset of scenarios. **Where to start:**

- To align value codes without changing your data model, see the [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/).
- To map fields between existing systems, see the [Interoperability & Mapping Guide](/docs/interoperability-guide/).
- To design a new system for compatibility, see the [Data Model Design Guide](/docs/data-model-guide/).
- To use JSON-LD contexts or issue verifiable credentials, see the [JSON-LD & VC Guide](/docs/jsonld-vc-guide/).
