# Glossary

This glossary defines terms used throughout the PublicSchema handbook.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A compact concept map showing relationships between term, concept, property, vocabulary, value, application profile, mapping, shape, credential, and extension. Reader task: help newcomers understand the vocabulary of the handbook before reading detailed methods.
</aside>

## Application profile

A constrained use of a broader vocabulary or schema for a particular implementation, exchange, credential, jurisdiction, or program. An application profile may make optional PublicSchema properties required for a specific boundary.

## Boundary contract

The externally visible agreement for an API, export, event, credential, or file exchange. A boundary contract names fields, values, formats, examples, validation rules, and version policy.

## Canonical code

A controlled vocabulary value used as the shared reference value. Local codes can map to canonical codes.

## Concept

A meaningful entity or relationship type in PublicSchema, such as `Person`, `Household`, `Program`, `Enrollment`, `Identifier`, or `PaymentEvent`.

## Credential subject

The claims object inside a credential that describes the person, household, organization, enrollment, payment, entitlement, or other subject of the credential.

## Concept mapping

A mapping between a source entity and a PublicSchema concept.

## Controlled vocabulary

A defined set of allowed values for a field. PublicSchema vocabularies include labels, definitions, codes, URIs, and sometimes references to external standards.

## Credential

A portable, cryptographically verifiable set of claims issued by one party and presented by a holder to a verifier. PublicSchema can define compatible claim meanings and validation shapes.

## Crosswalk

A table mapping values, fields, concepts, or codes from one system to another. In PublicSchema adoption, crosswalk often means a local code set mapped to a PublicSchema vocabulary.

## Data model

The structure a system uses to store, process, and exchange data. A data model can be conceptual, logical, physical, or implementation-specific.

## Canonical export

An API payload, event payload, file, view, or extract that uses PublicSchema-compatible meanings at the system boundary.

## Definition Excel

A downloadable workbook that presents a PublicSchema concept with metadata, properties, and referenced vocabularies in a format useful for human review.

## Extension

A local concept, property, vocabulary value, or constraint added outside the PublicSchema canonical namespace.

## Evidence

Documentation, examples, standards, system behavior, mappings, policies, or implementation experience used to justify a term, mapping, vocabulary value, or governance decision.

## Field mapping

A mapping between a source field and a PublicSchema property.

## Gap

A documented mismatch between source and target. A gap may be a missing field, missing concept, incompatible value, type mismatch, cardinality mismatch, or lifecycle mismatch.

## JSON-LD

A JSON-based format for linked data. PublicSchema uses JSON-LD contexts and exports to connect data fields to stable semantic identifiers.

## JSON Schema

A validation language for JSON data. PublicSchema provides JSON Schemas for validating JSON records and credential payloads.

## Mapping

A documented relationship between source and target terms, fields, concepts, or values. A mapping should include match level, notes, version information, and review status.

## Match level

The type of relationship between mapped items. PublicSchema commonly uses exact, close, broad, narrow, related, and no match.

## Maturity

The review status of a term or artifact, such as draft, candidate, or stable.

## Namespace

A URI space that identifies ownership of terms. PublicSchema canonical terms live in the PublicSchema namespace. Local extensions should use a local namespace.

## Property

A reusable attribute or relationship that can appear on one or more concepts, such as `given_name`, `date_of_birth`, `enrollment_status`, or `payment_amount`.

## Profile

A constrained package or application of PublicSchema for a specific implementation, jurisdiction, exchange, credential, or procurement requirement.

## PublicSchema-compatible

Able to map, export, validate, or exchange data using PublicSchema meanings. Compatibility does not require copying PublicSchema's internal structure.

## Semantic interoperability

The ability of systems to exchange data while preserving meaning. Field names, value codes, relationships, and definitions must be understood consistently.

## SHACL

Shapes Constraint Language, a validation language for RDF data. PublicSchema can provide SHACL shapes for linked data workflows.

## Source system

The system, schema, API, file, standard, or dataset being mapped from.

## Target

The model or artifact being mapped to. In this handbook, the target is often PublicSchema.

## Term

A named concept, property, vocabulary, vocabulary value, credential type, profile item, or extension that can be referenced and governed.

## Template Excel

A downloadable workbook for data entry or testing, with PublicSchema property identifiers and vocabulary dropdowns.

## Validation report

A record of validation checks, sample data, errors, warnings, accepted deviations, and unresolved issues.

## Validation shape

A schema, shape, rule set, or profile used to check whether data conforms to an expected structure, value set, or boundary contract.

## URI

A stable web identifier for a term, vocabulary value, schema, context, or artifact.

## Value crosswalk

A crosswalk between local values and canonical PublicSchema vocabulary values.

## Vocabulary-backed property

A property whose allowed values come from a controlled vocabulary.

## Version

A recorded release or source state used to make mappings, validation, and package review reproducible.

## Next

- Use [Introduction](/handbook/introduction/) for the full handbook framing.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) for practical artifacts using these terms.
