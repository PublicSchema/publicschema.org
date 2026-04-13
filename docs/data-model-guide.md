# Data Model Design Guide

This guide is for teams building a new system (a social registry, MIS, case management tool, or any public service delivery platform) who want it to be interoperable from the start. Instead of retrofitting compatibility later, you design your data model with PublicSchema as a reference.

## Contents

- [When to use this approach](#when-to-use-this-approach)
- [What "compatible" means](#what-compatible-means)
- [Step 1: Identify the concepts you need](#step-1-identify-the-concepts-you-need)
- [Step 2: Review properties for each concept](#step-2-review-properties-for-each-concept)
- [Step 3: Adopt canonical vocabularies](#step-3-adopt-canonical-vocabularies)
- [Step 4: Add your own fields](#step-4-add-your-own-fields)
- [Step 5: Validate your design](#step-5-validate-your-design)
- [Using PublicSchema in procurement](#using-publicschema-in-procurement)
- [Design patterns to be aware of](#design-patterns-to-be-aware-of)
- [Available downloads](#available-downloads)
- [Next steps](#next-steps)

## When to use this approach

This approach works well when:

- You are building a new system and want it to exchange data with existing platforms
- You are writing an RFP and need concrete interoperability requirements
- You are designing a data model for a multi-country or multi-sector program
- You are replacing an existing system and want the new one to be easier to integrate

This is not about importing PublicSchema into your system as a dependency. It is about using it as a reference so your design choices are compatible with the shared vocabulary.

## What "compatible" means

A PublicSchema-compatible data model:

1. **Uses the same concepts.** Your "beneficiary" table maps clearly to PublicSchema's Person concept, even if you call it something different internally.
2. **Stores the same properties.** Your fields cover the PublicSchema properties you need, with compatible types. You may have additional fields; that is fine.
3. **Uses the same vocabulary codes.** Where PublicSchema defines a controlled value set (enrollment status, gender, delivery channel), your system uses the same codes or can translate to them trivially.
4. **Can export in a canonical format.** Given the above, your system can produce exports or API responses that align with PublicSchema property names and vocabulary codes.

You do not need to use PublicSchema's exact field names internally, adopt JSON-LD, or change your database engine. Compatibility is about semantic alignment, not structural conformity.

## Step 1: Identify the concepts you need

Browse the [concepts page](/concepts/) and identify which concepts apply to your system. Not every system needs every concept.

A social registry typically needs: Person, Household, GroupMembership, Identifier, Address, Location.

A benefits management system might add: Program, Enrollment, Entitlement, EligibilityDecision, PaymentEvent.

A grievance system adds: Grievance.

Download the **Definition Excel** for each concept you plan to implement. The definition workbook includes:

- Concept metadata (URI, domain, maturity level, definitions in EN/FR/ES)
- Complete property list with types, cardinality, and definitions
- Referenced vocabularies with all codes

This gives you a self-contained reference document for each concept.

## Step 2: Review properties for each concept

For each concept, review the property list and decide which ones your system needs. PublicSchema is descriptive, not prescriptive: everything is optional. Adopt the properties that matter for your use case.

For each property you adopt, align on:

- **Name.** Your internal field name can differ, but document the mapping. If you can use the PublicSchema name directly (e.g., `given_name`, `enrollment_status`), the mapping is trivial.
- **Type.** Match the expected type. If PublicSchema says `date`, store a date, not a string. If it says `integer`, store an integer.
- **Cardinality.** PublicSchema marks properties as single-valued or multi-valued. If a property is multi-valued (e.g., a person can have multiple identifiers), design your schema to support that (e.g., a separate table or an array field).

The concept **CSV** is useful as a checklist during this step.

## Step 3: Adopt canonical vocabularies

For any property backed by a vocabulary (status codes, gender, document types, etc.), use the canonical codes directly if you can. This is the single highest-value design choice because it eliminates the need for code translation in every future integration.

If you must use different internal codes (e.g., your database uses integer foreign keys), maintain a lookup table that maps your codes to the canonical codes. Design this mapping into your system from the start, not as an afterthought.

See the [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/) for details on working with vocabularies.

## Step 4: Add your own fields

Your system will almost certainly need fields that PublicSchema does not define. That is expected and fine. PublicSchema covers the common ground across systems, not every possible field.

When adding custom fields:

- **Do not collide with PublicSchema property names.** Check the [properties page](/properties/) to make sure your custom field name is not already defined with different semantics.
- **Consider whether the field might be useful to others.** If it represents a common concept that PublicSchema does not yet cover, it may be a candidate for contribution. See the [Extension Mechanism](/docs/extension-mechanism/) for how to define custom properties in your own namespace.
- **Document your extensions.** Future integration partners will need to know which fields are canonical and which are custom.

## Step 5: Validate your design

Use the following artifacts to check your design against PublicSchema:

- **JSON Schema:** Validate sample records against the concept's JSON Schema. If your exported data passes validation, your schema is compatible.
- **SHACL shapes:** If you work with RDF, the SHACL shapes provide constraint validation for all concepts.
- **Template Excel:** Enter sample data in the Template Excel for each concept. If your system's data fills the template cleanly, the mapping is solid. If columns are empty or values do not fit the dropdowns, investigate the gaps.

## Using PublicSchema in procurement

If you are writing an RFP for a new system, PublicSchema gives you concrete language for interoperability requirements instead of vague aspirations.

Example requirement language:

> The system must be capable of exporting Person records with the following properties as defined by PublicSchema (publicschema.org): given_name, family_name, date_of_birth, sex, identifiers. Enrollment status must use codes from PublicSchema's enrollment-status vocabulary. The system must support export in CSV format with PublicSchema property names as column headers.

This is testable. During evaluation, you can hand vendors a Template Excel and ask them to demonstrate that their system can produce a conforming export.

You can also reference the Definition Excel workbooks directly in the RFP as the authoritative specification for each entity the system must support.

## Design patterns to be aware of

### Person-to-Group is many-to-many

PublicSchema models the relationship between people and groups (households, families, etc.) through a GroupMembership concept that carries a role (head, spouse, child, dependent). Do not model this as a simple list of members on the group. A person can belong to multiple groups, and the role matters.

### Identifiers are separate from Person

PublicSchema models identifiers (national ID number, passport number, program ID number) as a separate Identifier concept linked to Person, not as fields directly on Person. Identifier holds just the coded value and its scheme; the documents that carry identifiers (passports, national ID cards, beneficiary cards) are modeled as IdentityDocument, which holds the issuing authority, jurisdiction, issue date, and expiry.

### Time-boundedness is first-class

Many concepts carry start_date and end_date. Enrollment is not just a status; it is a time-bounded relationship. Design your schema to support this pattern rather than storing only current state.

### Domain namespacing

Some concepts are universal (Person, Location) and some are domain-specific (Enrollment is under social protection, `/sp/Enrollment`). If you are building for a specific sector, check which domain your concepts belong to. This affects URIs but not how you use the properties.

## Available downloads

**Per concept:**

| Format | What it is | Best for |
|---|---|---|
| **Definition Excel** | Multi-sheet workbook with metadata, properties, and referenced vocabularies in EN/FR/ES | Primary reference during data model design |
| **Template Excel** | Data entry workbook with dropdown validation | Testing compatibility, prototyping forms, procurement evaluation |
| **CSV** | Properties with types and definitions | Checklist for field-by-field design review |
| **JSON-LD** | Concept as linked data | Machine-readable access |

**Per vocabulary:**

| Format | What it is | Best for |
|---|---|---|
| **CSV** | Codes with multilingual labels and definitions | Seeding lookup tables in your database |
| **JSON-LD** | Vocabulary as SKOS ConceptScheme | Programmatic access |

**Validation:**

| Format | What it is | Best for |
|---|---|---|
| **JSON Schema** (per concept) | Draft 2020-12 JSON Schema | Validating exported records |
| **SHACL shapes** | RDF validation constraints | Validating RDF data |

## Next steps

- To align value codes in an existing system, see the [Vocabulary Adoption Guide](/docs/vocabulary-adoption-guide/).
- To connect existing systems using PublicSchema as a translation layer, see the [Interoperability & Mapping Guide](/docs/interoperability-guide/).
- To use JSON-LD contexts and issue verifiable credentials, see the [JSON-LD & VC Guide](/docs/jsonld-vc-guide/).
