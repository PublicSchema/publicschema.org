# Package and Validate Your Work

PublicSchema adoption should leave behind a reviewable package. A future team should be able to understand what was mapped, why decisions were made, how sample data was validated, and who owns the result.

This page defines what "done" means across adoption paths.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A checklist-style package diagram. Reader task: help a project lead see the complete handover package before release. Show folders or cards for scope brief, mappings, value crosswalks, examples, validation report, gaps, governance notes, and release metadata.
</aside>

## Why packaging matters

Many interoperability projects fail slowly. The first integration works, but the mapping spreadsheet sits in someone's inbox, source systems change, code values drift, and no one knows which version was used.

A package prevents that. It makes adoption inspectable, testable, and maintainable.

## Package types

| Adoption path | Package name | Main contents |
|---|---|---|
| Vocabulary adoption | Vocabulary alignment package | Vocabulary inventory, local code inventory, crosswalks, examples, owner |
| Existing system mapping | System mapping package | Scope, characterization, concept mappings, property mappings, value crosswalks, gaps, validation |
| New system design | Compatibility design package | Concept list, property checklist, vocabulary decisions, extension namespace, export/API examples |
| Exchange or API | Boundary contract package | Schema, examples, validation rules, version policy, consumer notes |
| Credential issuance | Credential design package | Claim set, schema, examples, disclosure rules, verifier checks, lifecycle policy |

## Core package contents

Every package should include:

| Item | Why it matters |
|---|---|
| Purpose and scope | Prevents future readers from using the package outside its intended context. |
| PublicSchema version | Makes mappings and validation reproducible. |
| Source version | Identifies the system, schema, API, export, or code list that was mapped. |
| Concepts in scope | Names the semantic surface being adopted. |
| Properties in scope | Shows field-level decisions. |
| Vocabularies in scope | Shows controlled values and code mappings. |
| Gaps | Makes non-alignment visible. |
| Examples | Helps humans and tests understand the package. |
| Validation report | Shows what was checked and what failed. |
| Owner | Keeps the package alive after publication. |

Example manifest:

```json
{
  "package_name": "cash-transfer-reporting",
  "package_version": "0.1.0",
  "publicschema_version": "draft",
  "source_systems": [
    {"name": "Family Support MIS", "version": "3.4"},
    {"name": "Disability Benefit API", "version": "2026-04"}
  ],
  "artifacts": [
    {"path": "mappings/properties.csv", "type": "field_mapping"},
    {"path": "crosswalks/enrollment-status.csv", "type": "value_crosswalk"},
    {"path": "examples/enrollment.example.json", "type": "example"},
    {"path": "validation/validation-report.md", "type": "validation_report"}
  ],
  "owner": "data-coordination-unit"
}
```

## Validation layers

Use more than one validation layer. Each catches a different class of problem.

| Layer | Catches |
|---|---|
| Schema validation | Missing fields, wrong types, malformed structures, invalid vocabulary codes. |
| Crosswalk validation | Local codes without canonical mappings, canonical values not represented locally. |
| Sample data review | Edge cases, ambiguous mappings, data quality issues. |
| Domain review | Semantically wrong mappings that pass technical validation. |
| Privacy review | Excessive disclosure, sensitive fields, inappropriate reuse. |
| Version review | Mappings tied to obsolete source or target versions. |

## JSON Schema validation

Use JSON Schema when producing JSON records, API responses, exchange files, or credential payloads.

The validation report should include:

- Schema used.
- PublicSchema version.
- Sample files checked.
- Errors and warnings.
- Known accepted deviations.
- Date of validation.

## Vocabulary validation

For each vocabulary-backed field:

- Confirm every emitted value is a valid PublicSchema code.
- Confirm local values have a crosswalk or documented no-match.
- Confirm "unknown", "not stated", "not applicable", and blanks are handled consistently.
- Confirm deprecated local values are either excluded or mapped with notes.

## Mapping review

Mapping review should involve both technical and domain people.

Technical reviewers check:

- Data types.
- Cardinality.
- Transformation rules.
- Validation behavior.
- Automation feasibility.

Domain reviewers check:

- Whether matched concepts mean the same thing.
- Whether local workflow states were misunderstood.
- Whether broad or close mappings are acceptable for the use case.
- Whether gaps have operational consequences.

## Gap register

Do not hide gaps. They are one of the most valuable outputs.

Gap types:

| Gap | Example |
|---|---|
| Source extra | The local system has a field PublicSchema does not cover. |
| PublicSchema missing locally | PublicSchema has a property the local system cannot produce. |
| Ambiguous value | One local code maps to several canonical values. |
| Type mismatch | Local field is text, PublicSchema expects a date or number. |
| Cardinality mismatch | Local field is single-valued, PublicSchema expects repeatable values. |
| Lifecycle mismatch | Local status stores current state only, target model expects history. |

## Release metadata

Every package should record:

- Package name.
- Package version.
- PublicSchema version.
- Source system name and version.
- Date.
- Authors or maintainers.
- Reviewers.
- License or sharing restrictions.
- Change log.

## Validation report template

Use a short report that a future maintainer can read quickly:

| Section | Contents |
|---|---|
| Summary | Package, versions, date, reviewer, decision |
| Checks run | Shape, vocabulary, mapping, privacy, package completeness |
| Findings | Severity, location, finding, decision |
| Accepted deviations | Known issues that do not block release |
| Open gaps | Items requiring follow-up |
| Release decision | Accepted, accepted with conditions, or not accepted |

## Done means

An adoption package is complete when:

- It can be read without private context.
- It names source and target versions.
- It includes mappings, gaps, examples, and validation results.
- It distinguishes exact, close, broad, narrow, related, and no-match decisions.
- It has an owner and update trigger.
- It is stored somewhere durable.

## Next

- Use [Templates and Checklists](/handbook/templates-and-checklists/) for copyable package tables.
- Use [Governance, Versioning, and Methodology](/handbook/governance/) to decide owners, review cycles, and deprecation rules.
- Use [Extend PublicSchema](/handbook/extend-publicschema/) when unresolved gaps appear across more than one project.
