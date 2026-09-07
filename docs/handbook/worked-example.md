# Worked Example: Mapping a Program Export

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> An end-to-end storyboard for a cash transfer reporting exchange. Reader task: help a delivery team see how one scenario moves from source files to mappings, validation, publication, and governance. Show three programs on the left, a PublicSchema mapping package in the center, and a dashboard, API, and partner report on the right.
</aside>

This example follows one realistic adoption scenario across the handbook. It is intentionally small: three cash transfer programs want to compare enrollment and payment delivery without replacing their case management systems.

## Scenario

The ministry has three programs:

| Program | Current system | Need |
|---|---|---|
| Family Support | MIS database export | Monthly household enrollment and payment report |
| Disability Benefit | Vendor API | Active beneficiary and payment status feed |
| Emergency Cash | Spreadsheet collection | Rapid coordination with partners |

Each program already has working operations. The goal is not to merge systems. The goal is to publish a common, validated exchange package that partners can understand.

## Step 1: Define the useful boundary

The team chooses a small boundary:

| Boundary question | Decision |
|---|---|
| Who is included? | People or households enrolled in one of the three programs |
| Which events matter? | Enrollment status changes and payment events |
| Which period? | Current reporting month plus previous month for corrections |
| Which consumers? | Ministry dashboard, finance reconciliation, partner coordination |
| Which data is excluded? | Case notes, disability details, grievance descriptions, bank account numbers |

The boundary is deliberately narrower than the internal systems. It includes only the data needed for coordination and reporting.

## Step 2: Select concepts

The first concept set is:

| PublicSchema concept | Used for |
|---|---|
| `Person` | Individual recipient or household member |
| `Household` | Household-level enrollment when the program pays the household |
| `Enrollment` | Link between a person or household and a program |
| `Program` | Program metadata used by reports |
| `PaymentEvent` | Payment amount, status, period, and delivery channel |
| `Location` | Administrative area or delivery location |

If a source system has no household entity, the mapping can still publish person-level enrollment. If a source uses only household heads, the team documents that limitation in the gap register.

## Step 3: Build the vocabulary crosswalk

The source systems use different enrollment and payment status values:

| Source system | Source field | Source value | PublicSchema vocabulary | PublicSchema value | Match level | Note |
|---|---|---|---|---|---|---|
| Family Support | `hh_status` | `A` | `enrollment_status` | `active` | exact | Confirmed in MIS codebook |
| Family Support | `hh_status` | `S` | `enrollment_status` | `suspended` | exact | Suspension may be temporary |
| Disability Benefit | `beneficiaryState` | `eligible_paid` | `enrollment_status` | `active` | close | Combines eligibility and payment history |
| Emergency Cash | `status` | `approved` | `enrollment_status` | `pending` | close | Approved but not enrolled until payment list is signed |
| All | `payment_status` | `failed` | `payment_status` | `failed` | exact | Used for reconciliation |

The crosswalk is reviewed by program owners before any data is transformed. Ambiguous values become questions, not silent mappings.

## Step 4: Map fields

The team creates a field mapping for each source:

| Source system | Source field | PublicSchema target | Transform | Required? | Confidence |
|---|---|---|---|---|---|
| Family Support | `national_id_hash` | `Person.identifier` | Keep hashed identifier and declare identifier type | yes | high |
| Family Support | `district_code` | `Location.administrativeAreaCode` | Map local district code to canonical location reference | yes | medium |
| Disability Benefit | `case_id` | `Enrollment.identifier` | Prefix with source system id | yes | high |
| Disability Benefit | `monthlyAmount` | `PaymentEvent.amount` | Keep numeric amount and currency | yes | high |
| Emergency Cash | `recipient_name` | `Person.name` | Split only when source has structured names | no | medium |

Confidence is a review signal. Match level describes the semantic relationship. A close match can have high confidence if the team has strong evidence, and an exact-looking match can have low confidence if the source definition is unclear.

## Step 5: Publish a canonical export

The canonical export is the public boundary contract. It can be a file, API payload, event payload, or database view. For the first release, the team chooses CSV plus JSON examples.

Example package:

```text
cash-transfer-reporting/
  README.md
  manifest.json
  scope.md
  mappings/
    family-support.fields.csv
    disability-benefit.fields.csv
    emergency-cash.fields.csv
  crosswalks/
    enrollment-status.csv
    payment-status.csv
  examples/
    enrollment.example.json
    payment-event.example.json
    reporting-sample.csv
  validation/
    validation-report.md
    errors.csv
  governance/
    owners.md
    decisions.md
    gap-register.csv
```

The package is not a data dump. It is a documented contract that explains how data becomes PublicSchema-compatible.

## Step 6: Validate examples

Validation checks should cover:

| Layer | Check |
|---|---|
| Shape | Required fields, types, date formats, and nested object structure |
| Vocabulary | Only approved canonical values appear in vocabulary-backed fields |
| Mapping | Every required target field has a source, transform, or documented gap |
| Privacy | Excluded sensitive fields do not appear in examples or exports |
| Governance | Owners, source versions, and PublicSchema version are recorded |

The first validation run usually finds missing values, ambiguous code mappings, and local fields with no clear target. That is useful evidence for the gap register.

## Step 7: Govern the release

The release record should answer:

| Question | Example answer |
|---|---|
| Who owns the package? | Social protection data coordination unit |
| Which source versions were mapped? | MIS 3.4, Vendor API 2026-04, Emergency Cash template 2026-Q2 |
| Which PublicSchema version was used? | PublicSchema draft release available at the time of validation |
| What changed since the last release? | Added payment failure reason crosswalk, excluded free-text case notes |
| What remains unresolved? | Disability Benefit combines eligibility and payment history in one status |

Treat the package as a living interoperability asset. It needs an owner, review rhythm, and change log.

## What this example teaches

- Start with a boundary that is useful to a real workflow.
- Map source systems without redesigning them.
- Separate field mappings from value crosswalks.
- Keep privacy decisions visible in the package.
- Validate examples before asking partners to consume the exchange.
- Govern gaps instead of hiding them.

## Next

- Use [Templates and Checklists](/handbook/templates-and-checklists/) to copy the package skeletons.
- Use [Map Existing Systems](/handbook/map-existing-systems/) when you need a full mapping lifecycle.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) before sharing the package with another team.
