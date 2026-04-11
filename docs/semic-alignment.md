# SEMIC Core Vocabularies Alignment

How PublicSchema relates to the EU Core Vocabularies (SEMIC / Interoperable Europe), and what we plan to do about it.

## Background

The EU Core Vocabularies are minimal, reusable RDF vocabularies for European public administration. They are published as OWL ontologies with SHACL validation shapes under CC-BY 4.0. All terms live under the `http://data.europa.eu/m8g` namespace.

PublicSchema already identifies SEMIC as "the closest technical precedent" (see `docs/related-standards.md`). We align where they overlap (person, location, address) but extend into the delivery lifecycle (enrollment, entitlement, payment, grievance) which SEMIC does not cover.

The SEMIC repos are cloned in `external/semic/`.

## Relevant SEMIC vocabularies

| Vocabulary | Repo | Key classes | Overlap with PublicSchema |
|---|---|---|---|
| Core Person | `Core-Person-Vocabulary` | `person:Person`, `adms:Identifier`, `m8g:ContactPoint` | Person, Identifier, naming properties, gender/sex, birth/death dates |
| Core Location | `Core-Location-Vocabulary` | `locn:Address`, `locn:Geometry`, `m8g:AdminUnit`, `dc:Location` | Address, Location, GeographicArea, coordinates, admin hierarchy |
| Core Business | `Core-Business-Vocabulary` | `legal:LegalEntity`, `org:Organization` | Party (as supertype), implementing agencies |
| Core Public Organisation (CPOV) | `CPOV` | `m8g:PublicOrganisation` | Program implementing agencies, governing jurisdictions |
| Core Criterion and Evidence (CCCEV) | `CCCEV` | `m8g:Requirement`, `m8g:Criterion`, `m8g:Evidence` | AssessmentFramework, EligibilityDecision, scoring/evidence |
| Core Public Event | `Core-Public-Event-Vocabulary` | `m8g:PublicEvent`, `m8g:Participation` | Event supertype, HazardEvent (loosely) |

## What we want to achieve

### 1. Automated comparison report

**Status:** Next step

Parse the SEMIC Turtle files with `rdflib` and our YAML schema files, then produce a structured gap analysis:

- Which SEMIC classes have a PublicSchema equivalent (and vice versa)
- Which SEMIC properties overlap with ours, at what level of alignment
- Where SEMIC has properties we lack (potential additions)
- Where we have concepts SEMIC does not cover (our unique value)

This gives us an evidence-based picture before we commit to any mapping decisions.

**Output:** `reports/semic-comparison.md` (generated), plus a reusable script in `build/`.

### 2. Structured system_mappings to SEMIC

**Status:** After comparison report

Add SEMIC as a mapped system on our concept and property YAML files, using the same `system_mappings` structure we use for other external systems. This would document mappings like:

- `Person` maps to `person:Person` (exact match)
- `Address` maps to `locn:Address` (exact match)
- `given_name` maps to `foaf:givenName` (exact match)
- `Identifier` maps to `adms:Identifier` (close match, our model is simpler)
- `EligibilityDecision` maps to `m8g:Criterion` (broad match, different granularity)

This makes the alignment visible on the website and queryable by tooling.

### 3. JSON-LD context alignment

**Status:** Design phase

We already produce a JSON-LD context (`dist/context.jsonld`) with Schema.org aliases (e.g., `givenName` resolves to `ps:given_name`). We could add SEMIC aliases in the same context so that a single PublicSchema credential is intelligible to both Schema.org consumers and EU SEMIC-aware systems.

For example, the context could include:

```jsonld
{
  "foaf:givenName": "https://publicschema.org/given_name",
  "person:birthName": "https://publicschema.org/family_name_at_birth",
  "locn:fullAddress": "https://publicschema.org/street_address",
  "m8g:birthDate": "https://publicschema.org/date_of_birth"
}
```

This means a credential issued with PublicSchema terms would also be valid when processed by an EU system expecting SEMIC property names, with no translation layer needed.

**Trade-off:** Adding many aliases increases context size and complexity. We should be selective: only alias properties where SEMIC is widely deployed (EBSI/EUDI wallet ecosystem, EU interoperability frameworks).

### 4. CCCEV alignment for eligibility and assessment

**Status:** Design phase

CCCEV models eligibility as a hierarchy:
- `Requirement` (abstract), with subtypes `Criterion` (weighted scoring), `Constraint` (hard rules), `InformationRequirement` (documents needed)
- `Evidence` supports requirements, with `EvidenceType` classification
- `SupportedValue` carries the actual data for evaluation

Our model uses `AssessmentFramework` (defines criteria) and `EligibilityDecision` (records outcome). These are complementary perspectives:

- CCCEV models the *structure* of eligibility rules (what criteria, what evidence)
- PublicSchema models the *lifecycle* of eligibility (who was assessed, what was decided, what follows)

The alignment is not one-to-one. A realistic mapping would be:

| PublicSchema | CCCEV | Relationship |
|---|---|---|
| AssessmentFramework | Requirement + Criterion | Our framework bundles what CCCEV separates into a hierarchy |
| EligibilityDecision | (no direct equivalent) | CCCEV models rules, not outcomes |
| scoring_method | Criterion.weightingType | Close match |
| cutoff_score | Criterion.weight + Constraint | Partial overlap |
| decision_basis | Evidence | Broad match |

This is worth documenting even if we do not change our model, because EU social protection systems implementing CCCEV will need a mapping guide.

### 5. SEMIC as a reference alignment layer

**Status:** Future consideration

SEMIC already reuses well-known ontologies: FOAF for person names, Dublin Core for locations, W3C ORG for organizations, ISA Location Vocabulary (`locn:`) for addresses. Rather than mapping PublicSchema to each of those independently, we could map to SEMIC and inherit those alignments transitively.

Benefit: one mapping instead of five. Risk: SEMIC's choices may not match our semantics in every case (they made EU-specific decisions about address structure, for example).

### 6. Enrich convergence data

**Status:** Low-effort, can happen anytime

Add SEMIC as another data point in our existing convergence analysis on concept and property YAML files. Update `system_count` denominators and add notes about alignment quality. This is purely informational and does not change the schema.

## Sequencing

1. **Automated comparison report** (produces evidence)
2. **Structured system_mappings** (natural output of the comparison)
3. **JSON-LD context aliases** (high value for EU interop, depends on mapping decisions)
4. **CCCEV alignment guide** (can run in parallel with 2-3)
5. **Convergence data enrichment** (low effort, anytime)
6. **Reference alignment layer** (future, depends on adoption patterns)
