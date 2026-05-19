# Templates and Checklists

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A practical toolkit board with cards for mapping brief, crosswalk, gap register, validation report, extension proposal, and release checklist. Reader task: help implementation teams pick the template they need for the next meeting or handover.
</aside>

This page collects lightweight templates you can copy into a spreadsheet, issue tracker, repository, or shared document. Keep them small enough that program teams can maintain them after the first mapping exercise.

## Artifact decision table

| Artifact | Use it when | Primary reader | Usually lives in |
|---|---|---|---|
| Mapping brief | A team needs to agree scope before mapping starts | Program owner, data lead | `scope.md` or a shared brief |
| Field mapping table | Source fields need to be aligned to PublicSchema properties | Data engineer, vendor | `mappings/*.csv` |
| Vocabulary crosswalk | Local codes need canonical values | Program owner, analyst | `crosswalks/*.csv` |
| Gap register | A source system has missing, ambiguous, or extra concepts | Product owner, governance lead | `governance/gap-register.csv` |
| Boundary contract | An API, event, or export is being published | Implementer, integrator | OpenAPI, JSON Schema, README |
| Validation report | A package is ready for review or release | Reviewer, consumer | `validation/validation-report.md` |
| Extension proposal | A local term may become reusable | Domain steward | Issue, pull request, or `extensions/*.md` |
| Release checklist | A package is being handed over | Project lead | `manifest.json`, changelog, release notes |

## Mapping brief template

| Field | Answer |
|---|---|
| Adoption goal | |
| Source systems | |
| PublicSchema concepts in scope | |
| Consumers | |
| Data products | |
| Out of scope | |
| Personal or sensitive data | |
| Source documentation | |
| Reviewers | |
| Target review date | |

## Field mapping table

| source_system | source_version | source_field | source_definition | publicschema_target | transform | required | match_level | confidence | owner | review_status | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  | yes/no | exact/close/broader/narrower/no_match | high/medium/low |  | draft/reviewed/approved |  |

Use `match_level` for the semantic relationship and `confidence` for reviewer certainty. Do not use confidence to hide a weak match.

## Vocabulary crosswalk table

| source_system | source_version | source_field | source_value | source_label | publicschema_vocabulary | publicschema_value | match_level | review_status | owner | notes |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | exact/close/broader/narrower/no_match | draft/reviewed/approved |  |  |

Add one row per source value. If a source value maps to more than one canonical value, document the rule that chooses between them.

## Gap register

| gap_id | source_system | gap_type | description | impact | decision | owner | target_date | status |
|---|---|---|---|---|---|---|---|---|
| GAP-001 |  | missing_target/missing_source/ambiguous_value/privacy_risk/local_extension |  | low/medium/high |  |  |  | open/accepted/resolved |

A gap is not a failure. It is a decision that needs visibility.

## Boundary contract checklist

| Check | Done |
|---|---|
| The boundary names the concepts included and excluded | |
| Required and optional fields are documented | |
| Canonical vocabulary values are listed or linked | |
| Example payloads include normal and edge cases | |
| Error responses explain validation failures without exposing sensitive data | |
| Version and compatibility rules are stated | |
| A contact or owner is listed | |

## Validation report template

```markdown
# Validation report

Package:
PublicSchema version:
Source systems:
Validation date:
Reviewer:

## Summary

- Records tested:
- Passed:
- Failed:
- Warnings:

## Checks run

| Layer | Result | Notes |
|---|---|---|
| Shape validation | pass/fail | |
| Vocabulary validation | pass/fail | |
| Mapping review | pass/fail | |
| Privacy review | pass/fail | |
| Package completeness | pass/fail | |

## Findings

| id | severity | location | finding | decision |
|---|---|---|---|---|

## Release decision

Accepted / accepted with conditions / not accepted.
```

## Extension proposal template

| Field | Answer |
|---|---|
| Proposed term | |
| Term type | concept/property/vocabulary value/profile constraint |
| Definition | |
| Why existing terms are not enough | |
| Evidence sources | |
| Example records | |
| Local or candidate upstream | |
| Privacy or sensitivity concerns | |
| Proposed owner | |

## Release checklist

| Check | Done |
|---|---|
| Scope and out-of-scope are documented | |
| Mappings and crosswalks have owners | |
| Examples validate or failures are explained | |
| Gap register is current | |
| Privacy review is recorded | |
| Artifact paths and versions are listed in `manifest.json` | |
| Change log explains user-visible changes | |
| Consumers have migration notes if behavior changed | |

## Next

- Use [Worked Example: Mapping a Program Export](/handbook/worked-example/) to see these templates filled in.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) to turn templates into a release package.
- Use [Extend PublicSchema](/handbook/extend-publicschema/) when a template reveals a recurring gap.
