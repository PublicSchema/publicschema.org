# Extend PublicSchema

PublicSchema covers common ground. Real systems will still need local concepts, properties, vocabulary values, and constraints.

Extension is normal. The goal is to extend without breaking interoperability.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A namespace diagram. Reader task: help a system architect see which terms are canonical, which are local, and which may become upstream contributions. PublicSchema canonical terms sit in the center. Local namespaces extend outward for country, program, vendor, or sector-specific fields, with clear lines showing which local terms map back to canonical concepts.
</aside>

## User story

As a system architect, I want to add local fields and concepts without colliding with PublicSchema, so that my system can support local needs while remaining interoperable at shared boundaries.

## When to extend

Extend when:

- A field is needed locally but is not common across systems.
- A concept is specific to a country, program, legislation, or vendor implementation.
- A local code value has no PublicSchema equivalent.
- A local constraint is stricter than PublicSchema's general reference model.
- A profile is needed for a particular exchange, credential, or procurement.

Do not extend when an existing PublicSchema term already has the same meaning. Reuse the existing term.

Do not propose upstream when:

- The term is required by only one local workflow.
- The definition depends on a private vendor implementation.
- The field is a temporary migration aid.
- The data should not leave the source system.
- The same need can be handled by a local application profile.

## Extension types

| Extension | Example |
|---|---|
| Local property | A program-specific case flag. |
| Local concept | A country-specific administrative process. |
| Local vocabulary value | A workflow status that only exists in one system. |
| Local application profile | A set of required fields for a specific API or credential. |
| Local validation constraint | A rule that a field is required for a national program. |

An application profile is a constrained use of PublicSchema for a specific boundary. For example, PublicSchema may treat `date_of_birth` as optional in the general `Person` reference model, while a specific enrollment API profile requires it or requires an age-band alternative.

## Step 1: Check for existing terms

Before extending, search:

- PublicSchema concepts.
- PublicSchema properties.
- PublicSchema vocabularies.
- Related standards and system mappings.
- Existing local extensions.

If a close term exists, compare definitions, not only names.

## Step 2: Decide whether the extension is local or candidate upstream

Use this decision table:

| Question | If yes |
|---|---|
| Is this field or concept common across several systems? | Consider proposing it upstream. |
| Is it required by a widely used standard? | Consider proposing it upstream or referencing the standard. |
| Is it specific to one law, program, workflow, or vendor? | Keep it local. |
| Does it duplicate a PublicSchema term with a new name? | Reuse PublicSchema instead. |
| Does it change the meaning of a PublicSchema term? | Do not overload the term. Create a local term and map it. |

## Step 3: Create a namespace

Extensions should live in a namespace that makes ownership clear.

Examples:

- `https://example.gov/schema/`
- `https://ministry.example/benefits/schema/`
- `https://vendor.example/publicschema-extension/`

Do not place local terms in the PublicSchema namespace.

## Step 4: Define the extension

Every extension should include:

- Identifier.
- Label.
- Definition.
- Owner.
- Type.
- Cardinality.
- Related PublicSchema concept or property.
- Vocabulary, if controlled.
- Sensitivity, if relevant.
- Examples.
- Mapping notes.

For vocabulary values, include:

- Code.
- Label.
- Definition.
- Whether the value is local-only.
- Closest PublicSchema value, if any.
- Match level.

## Step 5: Keep canonical boundaries clean

Local extensions can appear in internal systems, but canonical exports should clearly separate canonical and local fields.

For JSON, this may mean:

```json
{
  "given_name": "Amina",
  "family_name": "Diallo",
  "enrollment_status": "active",
  "examplegov:local_case_priority": "rapid_review"
}
```

The local field is allowed, but its namespace makes it clear that it is not a PublicSchema canonical property.

## Step 6: Review contribution candidates

If an extension appears useful beyond one implementation, prepare a contribution proposal.

The proposal should include:

- Problem statement.
- Proposed term.
- Definition.
- Evidence from systems or standards.
- Example data.
- Relationship to existing PublicSchema terms.
- Migration or compatibility concerns.

## Common mistakes

### Reusing a canonical name with a local meaning

Do not use `enrollment_status` for an internal workflow queue if it does not describe enrollment status. Create a local property.

### Hiding code lists in free text

If a field has repeatable values, make it a vocabulary. Free text makes mapping and validation much harder.

### Treating local constraints as global rules

A local API may require `date_of_birth`. That does not mean PublicSchema should make it globally required. Put local requirements in an application profile or boundary contract.

## Done means

An extension is well formed when:

- It uses a local namespace.
- It does not collide with PublicSchema names.
- It has definitions, types, and examples.
- Its relationship to PublicSchema is documented.
- It is clear whether the term is local-only or a candidate contribution.

## Next

- Use [Templates and Checklists](/handbook/templates-and-checklists/) for an extension proposal template.
- Use [Governance, Versioning, and Methodology](/handbook/governance/) when a local term may become a shared term.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) to include extensions in a release package.
