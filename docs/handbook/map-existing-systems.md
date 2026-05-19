# Map Existing Systems

Mapping existing systems is the flagship PublicSchema adoption path. It lets teams connect platforms already in production without forcing every platform to redesign its internal database.

The basic pattern is simple: each system maps to PublicSchema once. PublicSchema then acts as a shared semantic reference between systems.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A mapping lifecycle diagram with seven phases in a loop: staging, characterization, reuse, matching, alignment, validation, application. Reader task: help an interoperability team keep mapping work iterative and governed. Show PublicSchema as the target reference model and source systems feeding into the lifecycle.
</aside>

## User story

As an interoperability lead connecting existing delivery systems, I want to map each system's concepts, fields, and codes to PublicSchema, so that systems can exchange data through a shared semantic reference instead of maintaining one-off bilateral mappings.

## When to use this path

Use this path when:

- Two or more systems need to exchange data.
- A ministry is consolidating records across programs.
- A system migration needs a canonical intermediate model.
- A data warehouse must harmonize multiple sources.
- A national API federation is being built.
- A product or standard needs to be compared against PublicSchema.

This path works even when systems cannot change their internal structure. The mapping lives at the boundary.

## Outputs

A good mapping project produces a package, not just a spreadsheet.

| Output | Description |
|---|---|
| Mapping brief | Scope, purpose, source systems, target PublicSchema version, stakeholders, and success criteria. |
| Source characterization | Format, language, labels, definitions, versioning, code sets, data quality, and known constraints of the source system. |
| Target characterization | The PublicSchema concepts, properties, vocabularies, and validation artifacts in scope. |
| Concept mapping | Source entities mapped to PublicSchema concepts with match levels and notes. |
| Property mapping | Source fields mapped to PublicSchema properties with type, cardinality, transformation, and confidence notes. |
| Value crosswalks | Local code sets mapped to PublicSchema vocabularies. |
| Gap list | Source items with no PublicSchema equivalent, and PublicSchema items not represented by the source. |
| Validation report | Sample data results, JSON Schema or SHACL checks, mapping warnings, and unresolved issues. |
| Governance notes | Owner, review cycle, version policy, and triggers for remapping. |

Example package structure:

```text
mapping-package/
  scope.md
  mappings/
    concepts.csv
    properties.csv
  crosswalks/
    enrollment-status.csv
    payment-status.csv
  examples/
    source-record.json
    canonical-record.json
  validation/
    validation-report.md
  governance/
    gap-register.csv
    decisions.md
```

## Phase 1: Staging

Staging defines the work before anyone starts matching fields.

Answer these questions:

- What decision or integration will this mapping support?
- Which systems, APIs, files, reports, tables, or schemas are in scope?
- Is the mapping for transformation, comparison, procurement, reporting, migration, or documentation?
- Which PublicSchema version is the target?
- Which stakeholders must approve semantic decisions?
- What counts as good enough for the first release?

The output is a short mapping brief.

### Mapping brief template

| Field | Example |
|---|---|
| Purpose | Harmonize enrollment and payment exports from three programs into a national dashboard. |
| Source | Program A MIS export v3, Program B API v1, Program C warehouse table. |
| Target | PublicSchema draft release used by publicschema.org. |
| Scope | Person, Household, Program, Enrollment, PaymentEvent, identifier and status vocabularies. |
| Out of scope | Case notes, audit logs, internal workflow queues. |
| Users | Data warehouse team, program M&E team, interoperability architecture team. |
| Acceptance | Sample records validate, status code gaps documented, dashboard can group canonical values. |

## Phase 2: Characterization

Characterization is where teams learn what they are actually mapping.

For the source system, document:

- File or API format.
- Data model or schema documentation.
- Natural language of labels and definitions.
- Whether identifiers are stable.
- Whether values are controlled by code tables.
- Whether deprecated fields or codes remain in use.
- Whether fields are single-valued or multi-valued.
- Whether relationships are explicit or inferred.
- Version and release cycle.
- Known data quality issues.

For PublicSchema, identify:

- In-scope concepts.
- Relevant properties.
- Referenced vocabularies.
- Downloadable CSV, JSON Schema, SHACL, Definition Excel, and Template Excel artifacts.
- Maturity level and evidence status of relevant items.

Do not skip this phase. Many bad mappings happen because teams compare labels before understanding lifecycle, cardinality, time, and business rules.

## Phase 3: Reuse

Before creating new mappings, check whether reusable mappings already exist.

Look for:

- PublicSchema system mappings.
- Existing value crosswalks.
- Standards mappings from SEMIC, FHIR, DCI, GovStack, OpenSPP, openIMIS, OpenCRVS, DHIS2, or other relevant ecosystems.
- Local mapping spreadsheets from previous integrations.
- Data dictionaries from vendors or ministries.

Reuse can be direct, adapted, or rejected.

| Reuse decision | Meaning |
|---|---|
| Direct reuse | Existing mapping applies as-is. |
| Adapted reuse | Existing mapping is useful but needs local constraints, version updates, or missing fields added. |
| No reuse | Existing mapping is not suitable, so a new mapping is created. |

Record the decision. Reusing a mapping without recording its version and assumptions creates hidden risk.

## Phase 4: Matching

Matching proposes correspondences between source items and PublicSchema items.

Start manually for high-value fields. Automated matching can help with large inventories, but the final decision is semantic.

For each source entity, ask:

- Which PublicSchema concept is closest?
- Is the match exact, close, broad, narrow, or related?
- Does the source entity combine multiple PublicSchema concepts?
- Does PublicSchema separate something the source stores together?
- Is the source entity a transaction, relationship, observation, profile, document, or status?

For each source field, ask:

- Which PublicSchema property has the same meaning?
- Is the data type compatible?
- Is the cardinality compatible?
- Is the field current state or historical state?
- Does the value require a vocabulary crosswalk?
- Is transformation needed?

## Phase 5: Alignment

Alignment turns candidate matches into approved mapping assertions.

Use consistent match levels:

| Match | Use for |
|---|---|
| exact | Same meaning and compatible use. |
| close | Similar enough for the use case, but with caveats. |
| broad | Source item is broader than the PublicSchema item. |
| narrow | Source item is narrower than the PublicSchema item. |
| related | Semantically related, not safely interchangeable. |
| no match | No suitable PublicSchema item exists. |

Use confidence separately from match level. Match level describes the semantic relationship. Confidence describes how sure reviewers are, based on source documentation, examples, and owner confirmation. For example, a `close` match can have high confidence, and an apparent `exact` match can have low confidence until the source owner confirms it.

For property mappings, include transformation notes:

| Source field | PublicSchema property | Match | Transformation | Notes |
|---|---|---|---|---|
| `first_name` | `given_name` | exact | none | |
| `dob` | `date_of_birth` | exact | parse date | Source format is `DD/MM/YYYY`. |
| `hh_id` | `group_id` | close | prefix with system code | Local household IDs are not globally unique. |
| `inactive_reason` | `enrollment_status` | broad | lookup table | Local inactive reasons split across several canonical statuses. |

## Phase 6: Validation

Validation checks that the mapping works on real or representative data.

Validation should include:

- Sample records for common cases.
- Sample records for edge cases.
- JSON Schema validation for canonical exports.
- Vocabulary validation for mapped codes.
- Gap review with domain stakeholders.
- Round-trip review if data is imported back into a source system.
- Privacy and sensitivity review where personal data is involved.

Validation is not only a technical check. A syntactically valid export can still be semantically wrong.

## Phase 7: Application and governance

The mapping becomes useful when it is applied.

Applications include:

- ETL pipelines.
- API adapters.
- Data exchange files.
- Migration scripts.
- Dashboard transformations.
- Procurement evaluation.
- Standards comparison pages.

Governance should define:

- Who owns the mapping.
- How source system changes are detected.
- How PublicSchema version changes are reviewed.
- How no-match items are escalated.
- How downstream consumers are notified.
- How validation examples are refreshed.

## Common mapping problems

### Granularity mismatch

A source system may have one table called `beneficiary`, while PublicSchema separates `Person`, `Identifier`, `Enrollment`, `Household`, and `GroupMembership`.

Map meaning, not table names. A single source row may produce several PublicSchema-aligned records.

### Time mismatch

A source system may store only the current enrollment status, while PublicSchema can support time-bounded relationships.

Decide whether the mapping represents current state, event history, or both.

### One-to-many value mapping

A local code such as `inactive` may cover suspended, completed, exited, and deceased cases.

Do not hide the ambiguity. Map to the broadest safe value only if the use case allows it, and document the loss of precision.

### Missing concept

The source may contain a concept PublicSchema does not cover.

Document the gap. If the concept is local, use an extension. If it is broadly useful, propose it upstream.

## Done means

An existing system mapping is complete when:

- The scope is explicit.
- Source and target are characterized.
- Concept, property, and value mappings are documented.
- Gaps and ambiguous mappings are visible.
- Sample data validates or failures are explained.
- The mapping is owned and versioned.
- Downstream users know how to apply it.

## Next

- Use [Worked Example: Mapping a Program Export](/handbook/worked-example/) to compare your package with an end-to-end example.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) for copyable mapping tables and gap registers.
- Use [Privacy and Data Protection](/handbook/privacy-data-protection/) before applying mappings to person-level exports.
