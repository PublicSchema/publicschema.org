# Use Cases

PublicSchema helps when multiple programs, systems, or institutions need to coordinate around people, households, programs, payments, services, locations, credentials, and reporting.

This page summarizes common use cases and points each one to an adoption path.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A matrix-style visual with use cases down the left side and PublicSchema artifacts across the top: concepts, properties, vocabularies, JSON Schema, JSON-LD, credentials, mappings, and Excel templates. Reader task: help a team identify the first artifact to create for its use case. Highlight the minimum artifact set for each use case.
</aside>

## Use case summary

| Use case | Primary reader | First artifact to create |
|---|---|---|
| Cross-program deduplication | Data coordination lead | Mapping brief |
| Standardized reporting | Program or donor reporting lead | Vocabulary crosswalk |
| Interoperable procurement | Procurement lead | PublicSchema tender annex |
| API harmonization | Integration architect | Boundary contract |
| Portable credentials | Credential issuer or verifier | Claim and disclosure design |
| Disaster response coordination | Coordination cell or cluster lead | Shared concept and vocabulary list |
| Birth registration to service enrollment | Civil registration integration lead | Event boundary contract |
| Cross-country comparison and research | Research or policy team | Concept comparison table |

## Cross-program deduplication

**Situation:** Social protection, education, health, agriculture, and humanitarian systems hold records for overlapping populations.

**Problem:** Each system describes people and households differently. One system has beneficiaries, another has patients, another has students, and another has affected persons. Different code sets make matching even harder.

**How PublicSchema helps:** Each system maps its person, household, identifier, enrollment, and status fields to PublicSchema. A registry or data warehouse can compare records through shared definitions without forcing every system to redesign itself.

**Start with:** [Map Existing Systems](/handbook/map-existing-systems/).

**Key artifacts:** Concepts, properties, vocabularies, system mappings, validation samples.

## Standardized reporting

**Situation:** A donor, ministry, or coordination body aggregates data across programs, regions, countries, or implementers.

**Problem:** Programs report the same measure with different codes, labels, and denominator assumptions. Manual harmonization repeats every reporting cycle.

**How PublicSchema helps:** Reporting templates reference PublicSchema vocabulary codes and field meanings. Programs map once, then produce comparable exports.

**Start with:** [Adopt Vocabularies](/handbook/adopt-vocabularies/).

**Key artifacts:** Vocabulary CSVs, code crosswalks, canonical reporting columns, metric definitions where applicable.

## Interoperable procurement

**Situation:** A government is procuring a registry, MIS, payment platform, credential issuer, or case management system.

**Problem:** RFP language such as "must be interoperable" is too vague to test. Vendors interpret it differently.

**How PublicSchema helps:** Procurement documents can name PublicSchema concepts, properties, vocabularies, export formats, and validation requirements. Evaluation teams can test sample exports against expected artifacts.

**Start with:** [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/), then [Design a New System](/handbook/design-new-system/).

**Key artifacts:** Concept list, property checklist, vocabulary requirements, JSON Schema, Template Excel, sample export.

## API harmonization

**Situation:** A federation layer or national platform connects multiple agency APIs.

**Problem:** Each API exposes different field names and value codes. Custom adapters multiply quickly as the number of agencies grows.

**How PublicSchema helps:** Each agency can expose a PublicSchema-compatible API surface while keeping its internal database unchanged. The federation layer speaks one shared language.

**Start with:** [Publish Exchanges and APIs](/handbook/publish-exchanges/).

**Key artifacts:** PublicSchema-aligned API contract, field mappings, value crosswalks, validation tests.

## Portable credentials

**Situation:** A person needs to prove identity, enrollment, eligibility, entitlement, or payment status outside the issuing system.

**Problem:** The verifier may not have online access to the issuer. Sharing a full record would expose more personal data than needed.

**How PublicSchema helps:** The issuer creates a credential using PublicSchema-compatible fields and validates it with JSON Schema. Selective disclosure lets the holder reveal only the necessary claims.

**Start with:** [Issue Credentials](/handbook/issue-credentials/).

**Key artifacts:** Credential type, JSON Schema, JSON-LD context, disclosure design, verifier checks.

## Disaster response coordination

**Situation:** Government agencies, UN agencies, NGOs, and service providers collect data on affected populations during a crisis.

**Problem:** Parallel registrations create duplicate records, inconsistent vulnerability categories, and unclear coverage.

**How PublicSchema helps:** PublicSchema provides a common reference for people, households, groups, locations, profiles, assistance, and program enrollment. Agencies can map data after collection or use shared templates before collection.

**Start with:** [Map Existing Systems](/handbook/map-existing-systems/) if data already exists, or [Design a New System](/handbook/design-new-system/) if forms are still being designed.

**Key artifacts:** Concepts, properties, vocabularies, Template Excel, field mappings, gap list.

## Birth registration to service enrollment

**Situation:** A civil registry sends birth information to programs that provide immunization, health insurance, child grants, school registration, or social services.

**Problem:** Each downstream program wants a different intake format. Bilateral integrations become expensive and fragile.

**How PublicSchema helps:** A civil registration event can be translated to common person, identifier, location, and relationship fields. Downstream systems can consume the common representation or map from it.

**Start with:** [Publish Exchanges and APIs](/handbook/publish-exchanges/).

**Key artifacts:** Person, Identifier, Location, relationship concepts, vocabulary codes, event contract.

## Cross-country comparison and research

**Situation:** A policy team or researcher compares public service delivery programs across countries or sectors.

**Problem:** Local terms differ. A concept such as enrollment, entitlement, household, disability status, grievance, or payment may not mean the same thing everywhere.

**How PublicSchema helps:** PublicSchema gives a structured comparison frame. Local program models can be mapped to common concepts and documented gaps.

**Start with:** [Map Existing Systems](/handbook/map-existing-systems/).

**Key artifacts:** Concept mappings, property inventory, vocabulary crosswalks, documented semantic gaps.

## Minimum artifacts by use case

| Use case | Minimum PublicSchema artifacts |
|---|---|
| Vocabulary-only reporting | Vocabulary CSV, code crosswalk, canonical reporting column |
| Existing system integration | Concept list, field mapping, value crosswalk, gap list, validation samples |
| New system design | Concept list, property checklist, vocabulary choices, export contract |
| API federation | Boundary schema, field mapping, value mapping, contract tests |
| Credential issuance | Credential type, JSON Schema, JSON-LD context, disclosure rules |
| Data collection template | Template Excel, vocabulary dropdowns, import validation |
| Standards comparison | Concept matches, property matches, vocabulary matches, match levels, evidence |

## Next

- Use [Choose Your Path](/handbook/choose-your-path/) to choose the smallest adoption path for a use case.
- Use [Worked Example: Mapping a Program Export](/handbook/worked-example/) to see one use case carried through the whole workflow.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) when you are ready to create the first artifact.
