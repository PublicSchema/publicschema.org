# Methodology

## Why this page exists

PublicSchema makes claims about what public service delivery data means. Those claims need to be trustworthy. Trust depends on understanding how the schema is built, what is accelerated by tooling, and what is reviewed by humans. This page documents both.

## What PublicSchema synthesizes

The reference model is the result of a broad literature review, systematic analysis of open-source delivery systems, and alignment with international standards.

Sources include:

- **Open-source systems**: openIMIS (social health insurance), OpenSPP (social protection), OpenCRVS (civil registration), SEMIC (EU semantic interoperability), GovStack (digital government building blocks). Download and conversion scripts for each live in `external/`.
- **International standards**: ISO (3166 countries, 4217 currencies, 639-3 languages, 15924 scripts, 5218 sex codes), FHIR R4, UN M49 regions, ISCED education levels, W3C Verifiable Credentials, SD-JWT VC.
- **Domain initiatives**: DCI (Digital Convergence Initiative) for social protection data exchange, EU Core Person Vocabulary, CPSV-AP and HSDS/Open Referral for service catalogues, ILO and World Bank ASPIRE for indicators.
- **Literature**: academic and grey literature on social protection delivery, identity, and public service data models.

## Where AI helps

AI tooling accelerates research and drafting:

- **Reading at scale.** Comparing data models across six-plus systems, dozens of standards, and a broad literature base would be slow work for a small team.
- **Surfacing patterns and divergences.** Identifying where systems agree on meaning, where they diverge, and where gaps exist.
- **First drafts.** Initial passes of definitions, property lists, vocabulary value sets, and system mappings. Drafts are starting points for human review, not the output.

## What humans decide

Every concept definition, property, vocabulary entry, and cross-system mapping is reviewed by a human before it ships:

- **Definitions.** Rewritten for plain-language clarity. Definitions are the product, not a by-product.
- **Mappings.** Reviewed against source schemas and documentation. Each mapping carries a confidence level and a comment that flags uncertainty.
- **Design decisions.** Architectural choices (abstract supertypes, observation vs. scoring separation, domain namespacing) are recorded as Architecture Decision Records in `decisions/`. Each ADR states the question, the options considered, and the rationale for the choice.
- **Sensitive areas.** Topics that require domain expertise (legal definitions, protected categories, cultural variation) get additional review before moving out of draft.

## Verification layers

Claims are verifiable, not just stated:

- **Maturity flags.** Every concept, property, and vocabulary value carries a maturity level: draft, candidate, or normative. See [Versioning and Maturity](../versioning-and-maturity/). Draft content is explicitly marked so readers know what is still open.
- **Public decision records.** Every non-trivial architectural choice has an ADR in `decisions/` documenting what was considered and why.
- **Automated tests.** The build pipeline validates YAML structure, referential integrity, translation completeness, RDF graph invariants, export correctness, and system-mapping accuracy against external enums. Tests live in `tests/`.
- **Open source end-to-end.** YAML sources, build scripts, converted external schemas, tests, and the site are all public. Anyone can reproduce the build, audit a mapping, or propose a change.
- **Community feedback.** Feedback from domain experts and system implementers shapes what moves from draft to candidate to normative.

## What AI is not used for

- Accepting contributions without human review.
- Promoting concepts to normative maturity. Stability promises are made by humans.
- Decisions that require expert judgment: legal definitions, protected-category classifications, cultural variation, data sensitivity.
- Overriding community feedback or downstream adopter concerns.

## Known limits

- Parts of the schema are still at draft maturity and are explicitly waiting for expert review. These are flagged individually on each concept, property, and vocabulary page.
- Some system mappings are drafted from public documentation rather than hands-on system experience. Implementer feedback is actively sought.
- Bibliography coverage is improving iteratively.

If something looks wrong, please open an issue or propose a change.

## See also

- [Design Principles](../design-principles/) -- the philosophy the schema follows
- [Versioning and Maturity](../versioning-and-maturity/) -- how stability is earned
- [Schema Design](../schema-design/) -- naming, scoping, and modeling rules
