# Procurement and Vendor Acceptance

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A procurement acceptance workflow. Reader task: help a ministry, funder, or prime contractor see how PublicSchema requirements move from tender language to vendor evidence, sample exports, validation, and acceptance. Show tender, vendor build, test package, review, and sign-off.
</aside>

PublicSchema can make procurement more concrete. Instead of asking vendors to "support interoperability," ask them to publish named concepts, fields, vocabularies, examples, and validation evidence.

Use this page when procuring or accepting a registry, MIS, case management system, payment integration, reporting warehouse, API gateway, or data collection tool.

## Procurement principle

Ask for compatibility at the boundary, not a forced internal data model.

A vendor may keep its own database structure, workflow objects, and UI. The acceptance requirement is that the product can produce and consume agreed PublicSchema-compatible artifacts at defined boundaries.

## Tender language

Use language like:

> The supplier must provide PublicSchema-compatible exchange artifacts for the concepts and use cases listed in this tender. Compatibility means that the supplier can produce documented API payloads, event payloads, files, or validation packages that use the agreed PublicSchema concepts, properties, and vocabulary values at the system boundary. The supplier is not required to use PublicSchema as its internal database model.

Add the concept list, required use cases, and acceptance artifacts in the tender annex.

## Requirements table

| Requirement | Evidence required from vendor |
|---|---|
| Concept coverage | Table mapping product entities to PublicSchema concepts |
| Field coverage | Field mapping table for required properties |
| Vocabulary support | Crosswalk from product codes to canonical PublicSchema values |
| API or export boundary | OpenAPI fragment, JSON Schema, CSV template, or file specification |
| Examples | Synthetic sample payloads or files for normal and edge cases |
| Validation | Validation report showing pass/fail results and unresolved issues |
| Privacy controls | Field minimization note and sample data assurance |
| Versioning | Compatibility policy for changes to exports or APIs |
| Handover | Package manifest with artifact paths and owners |

## Acceptance levels

| Level | Meaning | Suitable for |
|---|---|---|
| Level 1: Vocabulary alignment | Local codes can be mapped to canonical PublicSchema values | Reporting and analytics |
| Level 2: Export compatibility | The system can produce PublicSchema-compatible files or views | Periodic exchange and dashboards |
| Level 3: API compatibility | The system exposes documented payloads with validation examples | System integration |
| Level 4: Governed package | Mappings, examples, validation, privacy notes, and change policy are maintained | Production interoperability |

Name the required level in the procurement. Do not leave it implicit.

## Vendor response checklist

Ask vendors to submit:

| Item | Expected response |
|---|---|
| Supported PublicSchema concepts | List of concepts and product modules |
| Unsupported required concepts | Gap explanation and proposed workaround |
| Field mappings | Mapping table using the handbook template |
| Vocabulary crosswalks | Crosswalk table for every required vocabulary-backed field |
| Sample exports | Synthetic examples for each boundary |
| Validation approach | Tools, checks, error reporting, and review process |
| Change management | How boundary changes are versioned and communicated |
| Data protection | How sensitive fields are minimized or excluded |

The response should include evidence, not only a statement of compliance.

## Acceptance test

Run an acceptance test before sign-off:

1. Give the vendor a small synthetic scenario with required concepts and values.
2. Ask for the API payload, event payload, file, or package the product would produce.
3. Validate the shape against the agreed schema or contract.
4. Validate vocabulary values and crosswalks.
5. Review privacy exclusions and sample data.
6. Confirm that errors are clear enough for implementers to fix.
7. Record gaps and decide whether they block acceptance.

## Red flags

| Red flag | Why it matters |
|---|---|
| "We are compatible" without mappings or examples | No reviewable evidence |
| Free-text fields for controlled values | Reporting and validation will be fragile |
| Export fields that change without versioning | Consumers will break silently |
| Real personal data in test samples | Protection failure before production starts |
| No owner for the boundary contract | Compatibility will decay after delivery |

## Acceptance note template

```markdown
# PublicSchema acceptance note

Product:
Vendor:
Procurement requirement:
Acceptance level:
Concepts tested:
Artifacts reviewed:
Validation result:
Open gaps:
Conditions:
Accepted by:
Date:
```

## Next

- Use [Design a New System](/handbook/design-new-system/) to define the product boundary.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) for the mapping and validation tables.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) for final handover.
