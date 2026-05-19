# Governance, Versioning, and Methodology

PublicSchema is useful only if teams can trust what its terms mean, understand how they change, and see why mappings or vocabulary choices were made.

Governance is the work that keeps the reference model stable enough to depend on and flexible enough to improve.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A governance workflow showing proposal, evidence review, draft term, candidate term, implementation feedback, stable term, and versioned release. Reader task: help a steward understand how terms and mappings change without surprising implementers. Include side paths for deprecation and extension proposals.
</aside>

## Governance principles

PublicSchema governance follows a few practical principles:

| Principle | Meaning |
|---|---|
| Semantic, not structural | PublicSchema defines shared meanings, not one mandatory database structure. |
| Descriptive, not prescriptive | It describes common delivery data patterns and lets local systems adopt what they need. |
| Evidence-based | Terms should be supported by real systems, standards, policies, or implementation demand. |
| Incremental | Coverage grows as use cases and evidence mature. |
| Plain language | Definitions should be usable by practitioners, not only ontology specialists. |
| Reviewable | Claims, mappings, and changes should be traceable. |

## Maturity levels

PublicSchema terms can move through maturity levels.

| Maturity | Meaning |
|---|---|
| Draft | Useful but still under active design. Expect changes. |
| Candidate | Broad shape is likely stable. Implementation feedback is wanted. |
| Stable | Intended for durable use with stronger change control. |

Maturity is per term or artifact, not only per release. A stable vocabulary can coexist with a draft concept.

Use "stable" for maturity. Use "normative" only when a separate governance decision makes a term binding for a particular specification, procurement, or profile.

## Versioning

A PublicSchema adoption package should always record the PublicSchema version it uses.

Versioning matters because:

- New terms may be added.
- Definitions may be clarified.
- Maturity may change.
- Mappings may be improved.
- Deprecated terms may remain available but no longer recommended.

Local systems should avoid silently changing mappings when PublicSchema changes. Review the difference, update examples, rerun validation, and record the decision.

## URI persistence

Stable URIs make references durable.

Do not use a URI as a temporary label. If a term is renamed for readability but its meaning is unchanged, the URI should remain stable where possible. If the meaning changes substantially, a new term may be needed.

## Evidence

Evidence can come from:

- Existing delivery systems.
- International standards.
- Sector standards.
- Data dictionaries.
- Public APIs.
- Procurement specifications.
- Implementation mappings.
- Research datasets.
- Practitioner review.

Evidence does not mean every system agrees. It means a term is grounded in observed need and can be reviewed.

## Mapping governance

Mappings need governance separate from term governance.

For each mapping, record:

- Source system and version.
- Target PublicSchema version.
- Mapping author.
- Reviewers.
- Match level.
- Confidence or review status.
- Notes and assumptions.
- Validation examples.
- Date reviewed.

Mappings should be revisited when either side changes.

## Deprecation

Deprecation should be explicit.

A deprecated term should say:

- Why it is deprecated.
- What to use instead, if applicable.
- Whether existing data remains valid.
- Whether exports should continue to emit it.
- When support may end.

Avoid deleting terms abruptly. Interoperability depends on persistence.

## Local governance

Every adopting organization should define local governance for:

- Who approves mappings.
- Who owns code crosswalks.
- Who reviews extensions.
- Who updates validation examples.
- Who monitors upstream PublicSchema changes.
- How downstream consumers are notified.

This can be lightweight. The important thing is that ownership is explicit.

## Methodology for new terms

A good term proposal includes:

- Name.
- Definition.
- Use case.
- Evidence.
- Examples.
- Related PublicSchema terms.
- Related standards.
- Expected properties or values.
- Known privacy or sensitivity concerns.
- Open questions.

For vocabulary proposals, include value definitions, not only labels.

## Lifecycle examples

| Change | Expected governance record |
|---|---|
| New term proposal | Use case, definition, evidence, examples, privacy concerns, reviewer decision |
| Vocabulary value addition | Value definition, source evidence, mapping impact, downstream compatibility note |
| Mapping update | Source version, target version, changed rows, validation result, reviewer |
| Deprecation notice | Reason, replacement, migration advice, support expectations |
| Extension contribution | Local namespace term, usage evidence, proposed canonical definition |

## Done means

Governance is healthy when:

- Terms have maturity and evidence.
- Changes are versioned.
- Mappings record source and target versions.
- Extensions are clearly local or proposed upstream.
- Deprecated items remain understandable.
- Adoption packages have owners and review triggers.

## Next

- Use [Extend PublicSchema](/handbook/extend-publicschema/) for local namespaces and contribution candidates.
- Use [Templates and Checklists](/handbook/templates-and-checklists/) for proposal and release templates.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) to make governance decisions visible in adoption packages.
