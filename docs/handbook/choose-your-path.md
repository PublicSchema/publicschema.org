# Choose Your Path

PublicSchema can be adopted lightly or deeply. The right path depends on what you are trying to improve: reporting, integration, procurement, API harmonization, credentials, analytics, or governance.

Start with the smallest path that solves the real problem. You can always adopt more artifacts later.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A decision tree with five branches: common codes, system mapping, new system design, data exchange/API, and verifiable credentials. Reader task: help a policy lead or architect choose the smallest adoption path that solves the current problem. Each branch ends with the recommended handbook chapter and output package.
</aside>

## Quick decision table

| If your team needs to... | Start with... | Main output | Typical team | Sample data needed? |
|---|---|---|---|---|
| Make reports comparable across programs, countries, or donors | [Adopt Vocabularies](/handbook/adopt-vocabularies/) | Code crosswalks and canonical reporting values | Program owner, analyst | helpful |
| Connect existing systems without redesigning them | [Map Existing Systems](/handbook/map-existing-systems/) | Mapping package with field mappings, value crosswalks, gaps, validation notes | Data lead, source-system owner, reviewer | yes |
| Build or procure a new registry, MIS, API, or case management tool | [Design a New System](/handbook/design-new-system/) | Concept list, property checklist, vocabulary choices, export contract | Product owner, architect, vendor | synthetic examples |
| Buy or accept a vendor system | [Procurement and Vendor Acceptance](/handbook/procurement-vendor-acceptance/) | Tender annex, vendor evidence, acceptance test | Procurement lead, evaluator, technical reviewer | synthetic test scenario |
| Publish a common API, event stream, or exchange file | [Publish Exchanges and APIs](/handbook/publish-exchanges/) | Boundary contract using PublicSchema field names and vocabulary codes | Integration team, API owner | yes |
| Issue portable claims that can be verified across systems | [Issue Credentials](/handbook/issue-credentials/) | Credential schema, validation rules, disclosure design | Issuer, verifier, privacy reviewer | synthetic claims |
| Add local fields or local concepts | [Extend PublicSchema](/handbook/extend-publicschema/) | Local namespace and documented extension model | Domain steward, implementer | examples |
| Make adoption reviewable and maintainable | [Package and Validate Your Work](/handbook/validate-and-package/) | Complete adoption package with tests and governance notes | Project lead, reviewer | yes |

## Path 1: Vocabulary adoption

Choose this path when your main problem is inconsistent codes.

Example: one program uses `ACTV`, another uses `1`, and another uses `active` for active enrollment. The reports cannot be compared until everyone agrees what those values mean.

Vocabulary adoption does not require changing internal field names, database tables, or APIs. You only need a translation layer at the boundary.

Best for:

- Donor reporting templates.
- Dashboards across multiple programs.
- API value normalization.
- Quick wins before deeper integration.

Do not start here if your main problem is entity structure, missing identifiers, or unclear relationships between people, households, enrollments, payments, and programs. Those require mapping or model design.

## Path 2: Mapping existing systems

Choose this path when systems already exist and need to exchange data.

This is the most common PublicSchema adoption path. A ministry, implementer, or federation layer maps each system to PublicSchema once. After that, PublicSchema becomes the shared reference between systems.

Best for:

- Cross-program deduplication.
- Data migration.
- Master data consolidation.
- API federation.
- Data warehouse harmonization.
- Comparing a product or standard against PublicSchema.

The key output is not only a table of matches. It is a mapping package that includes scope, source and target characterization, field mappings, value crosswalks, known gaps, validation reports, and governance decisions.

## Path 3: Design a new system

Choose this path when you can influence a system before it is built or procured.

PublicSchema-compatible design does not mean copying the PublicSchema structure. It means local concepts, fields, and values can be exported or translated cleanly to PublicSchema.

Best for:

- New social registries.
- Case management platforms.
- Benefits management systems.
- Civil registration integrations.
- Vendor procurement.
- Multi-country program platforms.

The highest-value design choice is to adopt canonical vocabulary codes directly where possible. That one decision can remove a large amount of future integration work.

## Path 4: Publish exchanges and APIs

Choose this path when the main product is a boundary: an API, event stream, file exchange, canonical export, or analytics feed.

This path is about making PublicSchema visible at the interface. Internal systems can keep their own shape, but the boundary should use shared field meanings and vocabulary codes.

Best for:

- Federation layers across agencies.
- Batch exports to data warehouses.
- Event-driven integration.
- Partner data-sharing agreements.
- Canonical CSV or JSON exports.

## Path 5: Issue credentials

Choose this path when people, households, providers, or agencies need portable claims that can be verified outside the issuing system.

Credentials are powerful, but they should not be the default starting point. Use them when portability, offline verification, selective disclosure, or holder control is central to the use case.

Best for:

- Identity claims.
- Enrollment proofs.
- Eligibility proofs.
- Payment or voucher credentials.
- Displaced population scenarios.
- Offline point-of-service verification.

## A useful adoption sequence

Many programs can move in this order:

1. Align a few high-value vocabularies.
2. Map the core concepts and fields for one integration.
3. Validate sample data against JSON Schemas.
4. Publish a stable export or API boundary.
5. Add credentials only for use cases that need portable proof.
6. Package the mapping and governance notes so the work survives staff changes.

The sequence matters because it builds trust. Teams learn where their data fits, where it does not fit, and which gaps are semantic rather than merely technical.

## Next

- Read [Worked Example: Mapping a Program Export](/handbook/worked-example/) if you want to see the paths connected.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) when you already know which artifact you need to create.
- Use [Privacy and Data Protection](/handbook/privacy-data-protection/) before any path that shares person-level data.
