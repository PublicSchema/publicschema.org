# Introduction

PublicSchema is a semantic reference model for public service delivery. It gives governments, implementers, donors, researchers, and product teams a shared set of concepts, properties, and controlled vocabularies that can be reused across registries, management information systems, payment platforms, credential issuers, reporting pipelines, and analytics systems.

The goal is practical interoperability. PublicSchema does not require every system to use the same database schema, API framework, credential stack, or data warehouse design. It gives teams a common semantic layer so they can describe equivalent things in compatible ways.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A full-width diagram showing several public service systems around a central PublicSchema layer. Reader task: help a mixed team understand that each system keeps its own internal database while shared concepts, properties, and vocabularies make exchange possible.
</aside>

## Who this handbook is for

This handbook is written for mixed teams. A ministry policy lead, social protection architect, health data engineer, civil registry product owner, donor data specialist, vendor, or standards contributor should all be able to find their path.

The handbook serves four overlapping audiences:

| Audience | What they need from the handbook |
|---|---|
| Program and policy teams | A clear explanation of what PublicSchema enables and how to specify it in procurement, data-sharing agreements, and reporting requirements. |
| Data and interoperability teams | A repeatable method for mapping systems, vocabularies, exports, APIs, and analytics pipelines to PublicSchema. |
| Product and engineering teams | Practical guidance for building compatible data models, exports, validation, APIs, credentials, and extension namespaces. |
| Standards and governance teams | A shared vocabulary for maturity, evidence, mappings, release management, and local stewardship. |

## What PublicSchema is

PublicSchema is:

- A reference vocabulary of [concepts](/concepts/) such as `Person`, `Household`, `Program`, `Enrollment`, `PaymentEvent`, `Identifier`, and `Location`.
- A [property inventory](/properties/) with reusable field meanings such as `given_name`, `date_of_birth`, `enrollment_status`, and `payment_amount`.
- A set of [controlled vocabularies](/vocab/) for values such as enrollment status, payment status, identifier type, document type, country, currency, and delivery channel.
- A set of downloadable artifacts on concept and vocabulary pages, including JSON Schema, CSV, Definition Excel, Template Excel, and machine-readable vocabulary data.
- A mapping surface for comparing PublicSchema to systems and standards such as OpenSPP, openIMIS, DHIS2, FHIR, OpenCRVS, DCI, GovStack, SEMIC, and others as coverage grows.

## What PublicSchema is not

PublicSchema is not a replacement for local system design. It does not tell a registry how to partition tables, which database to use, or how a case management workflow must behave.

PublicSchema is also not a claim that every public service system should expose every concept. Most teams should adopt only the subset that fits their use case. A reporting pipeline might need only vocabularies. A procurement specification might need a few concepts and property checklists. A credential issuer might need JSON Schema and selective disclosure rules.

The important distinction is this: PublicSchema is descriptive and semantic, not prescriptive and structural.

## How the handbook is organized

The handbook is organized around adoption work, not technology formats.

1. Start with [Choose Your Path](/handbook/choose-your-path/) if you are deciding how deeply to adopt PublicSchema.
2. Read [Use Cases](/handbook/use-cases/) if you want examples from delivery systems, reporting, credentials, procurement, and disaster response.
3. Read [Worked Example: Mapping a Program Export](/handbook/worked-example/) if you want to see one scenario from beginning to end.
4. Use [Adopt Vocabularies](/handbook/adopt-vocabularies/) for the lightest path: aligning local codes to canonical values.
5. Use [Map Existing Systems](/handbook/map-existing-systems/) when you need to connect systems already in production.
6. Use [Design a New System](/handbook/design-new-system/) and [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/) when building, buying, or accepting a new platform.
7. Use [Publish Exchanges and APIs](/handbook/publish-exchanges/) when exposing PublicSchema-compatible interfaces.
8. Use [Issue Credentials](/handbook/issue-credentials/) for portable claims and selective disclosure.
9. Use [Privacy and Data Protection](/handbook/privacy-data-protection/) before sharing sensitive service delivery data.
10. Use [Templates and Checklists](/handbook/templates-and-checklists/) and [Package and Validate Your Work](/handbook/validate-and-package/) when preparing an adoption package for review, publication, or handover.
11. Use [Extend PublicSchema](/handbook/extend-publicschema/) and [Governance, Versioning, and Methodology](/handbook/governance/) when maintaining local extensions or contributing back.

## Role-based entry points

| If you are... | Start with | Expected output |
|---|---|---|
| A policy or program lead | [Use Cases](/handbook/use-cases/) and [Choose Your Path](/handbook/choose-your-path/) | A scoped adoption goal and the first artifact to request |
| A procurement lead | [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/) | Tender language, vendor evidence list, and acceptance checklist |
| A data engineer or architect | [Map Existing Systems](/handbook/map-existing-systems/) | Field mappings, value crosswalks, validation samples, and gaps |
| A product team or vendor | [Design a New System](/handbook/design-new-system/) | Concept list, property checklist, and boundary contract |
| A credential issuer or verifier | [Issue Credentials](/handbook/issue-credentials/) | Credential claim design, validation checks, and disclosure policy |
| A governance or standards lead | [Governance, Versioning, and Methodology](/handbook/governance/) | Review process, owners, maturity decisions, and contribution candidates |

## What you can do quickly

| Timebox | Useful result |
|---|---|
| One hour | Pick a use case, choose an adoption path, and list the concepts or vocabularies likely in scope. |
| One week | Build a first crosswalk or mapping brief for one source system and review it with program owners. |
| One project | Publish a package with mappings, examples, validation results, privacy notes, and governance decisions. |

## The handbook pattern

Each adoption path follows the same pattern:

- Situation: when this path is useful.
- User story: who is doing the work and why.
- Outputs: what the team should have at the end.
- Method: the repeatable steps.
- Checks: how to know the work is good enough.
- Hand-off: how the result should be maintained.

This pattern is deliberate. PublicSchema should not be a site people admire and then leave. It should help a team make the next concrete decision.

## Next

- Use [Choose Your Path](/handbook/choose-your-path/) to decide how deeply to adopt PublicSchema.
- Use [Worked Example: Mapping a Program Export](/handbook/worked-example/) if you want a concrete end-to-end scenario first.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) when you are ready to create a work product.
