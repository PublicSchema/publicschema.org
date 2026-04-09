# Vocabulary Design Principles

How we decide what goes in a vocabulary, where it lives, what standards it references, and how it evolves as PublicSchema expands across domains.

## 1. Universal by default, domain-scoped by exception

A vocabulary lives at the root (`publicschema.org/vocab/gender-type/`) unless there is a clear reason to scope it to a domain (`publicschema.org/sp/vocab/targeting-approach/`).

**The test:** a vocabulary is universal if the same codes carry the same meaning regardless of which domain uses it. If domain X would need different values or different semantics for the same vocabulary name, it belongs in a domain namespace.

Examples:

- `payment-status` is universal. "Paid" means the same thing whether the payment is a social protection transfer, a health insurance reimbursement, or a scholarship disbursement.
- `targeting-approach` is domain-specific. "Proxy means testing" is social protection methodology. Health uses clinical criteria, education uses academic criteria. Other domains do not select beneficiaries this way.
- `severity` is ambiguous. In emergency alerting, severity means impact of a hazard event (OASIS CAP). In health, severity means disease progression (WHO scales). The word is the same; the semantics diverge. Disambiguate by renaming (`event-severity`) or scoping to a domain.

**When the same name means different things in different domains, rename or scope.** A vocabulary called `severity` at the root implies it works everywhere. If it only makes sense for hazard events, the name should say so.

**Definitions must match the scope.** A universal vocabulary's definition must not reference a specific domain. Write "the lifecycle states of an enrollment in a program," not "the lifecycle states of an enrollment in a social protection program." If the vocabulary is domain-scoped, the definition may reference the domain.

## 2. One concept per vocabulary

Each vocabulary answers one question. Do not combine orthogonal concerns into a single value set.

- **Status and outcome are different questions.** "Where is this process?" (pending, under review, completed) is distinct from "what was the result?" (eligible, ineligible, conditional). When both dimensions need to be tracked, use two properties with two vocabularies, not one overloaded vocabulary.
- **Channel and modality are different questions.** "How does the benefit reach the person?" (bank transfer, mobile money) is distinct from "what form does the benefit take?" (cash, voucher, in-kind). Keep them in separate vocabularies even when they feel related.

However: **do not split prematurely.** If a single vocabulary cleanly captures the lifecycle of a concept and all mapped systems treat it as one field, splitting into two vocabularies adds complexity without proven benefit. Split when cross-domain adoption surfaces a genuine semantic conflict, not when an architecture diagram suggests it might be cleaner.

When two vocabularies share values (e.g., `spouse` appears in both `group-role` and `relationship-type`), document the relationship with a `see_also` cross-reference and explain when to use which.

## 3. Reference existing standards; do not reinvent

**If a formal code system exists, reference it.** Even if we simplify the values for our audience, declare the relationship so implementers know where to find the full standard.

Three levels of standard reference:

| Level | When to use | YAML field |
|---|---|---|
| **Sync** | A machine-readable standard defines the authoritative value set. We download and convert it. | `standard` + `sync` |
| **Reference** | A standard exists but we don't sync from it (prose-only, partial overlap, structural pattern, or we deliberately simplify). | `references` |
| **None** | No relevant standard exists. We are the first to codify this vocabulary. | Neither field |

Every vocabulary should have at least one of these. A vocabulary with no `standard`, no `references`, and no `system_mappings` is entirely unvalidated. That is acceptable at draft maturity but should be resolved before trial use.

**Do not adopt a standard's codes when they don't serve the audience.** ISO 20022 payment status codes (RCVD, ACTC, ACSP) are designed for interbank messaging. Social protection program managers need "pending," "processing," "paid." Use readable codes; map to the standard.

## 4. Domain annotations on individual values

Sometimes a universal vocabulary contains one or two values that only make sense in a specific domain. Rather than splitting the vocabulary or creating a domain-scoped copy, annotate the value:

```yaml
- code: graduated
  domain: sp
  label:
    en: Graduated
  definition:
    en: The beneficiary has exited the program through program-defined graduation criteria.
```

A value with `domain: sp` signals to adopters in other domains: "this code exists but probably isn't relevant to you." A value without a `domain` annotation is universal.

**Use this sparingly.** If more than a third of a vocabulary's values carry domain annotations, the vocabulary is probably domain-specific and should move to a domain namespace.

## 5. Disambiguate names that could collide across domains

Vocabulary names live in a shared namespace (unless domain-scoped). Before naming a vocabulary, ask: "Could another domain reasonably define a vocabulary with this same name but different values?"

If yes, make the name specific enough to prevent collision:

- `severity` -> `event-severity` (prevents collision with disease severity, incident severity)
- `certainty` -> `event-certainty` (prevents collision with diagnostic certainty)
- `status` -> never use bare `status` as a vocabulary name; always qualify it (`enrollment-status`, `payment-status`)

If the vocabulary is domain-scoped, the domain prefix in the URI provides disambiguation naturally, so the vocabulary name itself can be shorter.

## 6. Vocabulary values for credentials

PublicSchema vocabularies are designed to work as the schema layer for Verifiable Credentials. This constrains vocabulary design in specific ways:

**Separate stable facts from transient states.** A VC should attest to facts that remain meaningful over time ("this person is eligible"), not to process states that change within hours ("this application is under review"). Both kinds of values may exist in the same vocabulary, but document which values are appropriate for credential claims and which are not.

**Values at draft maturity should not appear in production credentials.** A draft value's meaning may change. The maturity model (draft, trial use, normative) applies to individual values, not just vocabularies. Document this constraint for credential issuers.

**Identifier type is not enough for a credential.** A credential that says `identifier_type: national_id` is meaningless without the issuing jurisdiction and identifier scheme. Vocabularies that serve as building blocks for credentials should document what additional context is needed.

## 7. Machine-readable standards are preferred

When choosing between two standards that cover the same domain, prefer the one that publishes a machine-readable artifact (JSON, XML, CSV, RDF) over one that exists only as a PDF or prose document.

Machine-readable standards can be synced automatically. Prose standards require manual maintenance, which means they drift.

If only a prose standard exists, reference it and maintain the vocabulary by hand. But note the maintenance cost in the vocabulary's metadata.

## 8. The `other` code

Most vocabularies include an `other` catch-all value. This is acceptable at draft maturity. It signals "we know the vocabulary is incomplete."

Track what `other` maps to in real deployments. When the same unmapped value appears in 2+ systems, promote it to a named code. The goal is to shrink `other` over time, not to eliminate it (there will always be edge cases).

## 9. How vocabularies evolve

**Adding values is safe.** A new code can be added at any maturity level. Existing consumers that don't recognize it will ignore it (or fall through to a default).

**Renaming or removing values is breaking.** At draft maturity, it's acceptable with notice. At trial use, it requires a deprecation period. At normative maturity, it requires a new vocabulary version.

**When a new domain is added:**

1. Review all universal vocabularies. If any value would mean something different in the new domain, either rename the vocabulary for disambiguation or annotate the conflicting value with a domain.
2. If the new domain needs a vocabulary that no other domain shares, create it in the domain's namespace (e.g., `schema/vocabularies/health/`).
3. Do not create domain subfolders preemptively. Wait until a domain actually has vocabularies that need scoping.

## 10. System mappings validate vocabulary design

System mappings (`system_mappings` in the YAML) are not just documentation. They are the primary validation mechanism for vocabulary design:

- If 3+ systems independently implement the same concept and it maps to `other`, the vocabulary has a gap. Promote it to a named code.
- If a system has 4+ codes that all map to the same canonical value, the vocabulary may be too coarse at that point. Consider whether a finer distinction is needed.
- If a system code maps to `null` when a broader canonical code exists, the mapping has a bug. Fix it.

A vocabulary with zero system mappings is unvalidated. Prioritize adding mappings from real systems before advancing maturity.

## 11. When to create a concept, property, or vocabulary value

PublicSchema has three kinds of building blocks: concepts, properties, and vocabulary values. Choosing the right one early saves significant rework later. Use this decision tree.

### Step 1: Does the notion have its own identity?

Ask: "Does this thing exist independently, get referenced from multiple places, and have its own lifecycle (created, updated, closed)?"

If yes, it is a concept. A concept gets its own YAML file, its own URI, and is referenced by name from other concepts.

If no, proceed to Step 2.

**Worked example: GroupMembership**

GroupMembership is a concept, not a property on Person or Group. Three reasons:

1. It carries its own data (role, start date, end date). It is not a simple pointer.
2. It has its own lifecycle. A membership can be created, suspended, and ended independently of the Person or the Group still existing.
3. Multiple concepts reference it. Person has group memberships; Group has memberships. Flattening it onto either side would lose the other direction and lose the temporal data.

### Step 2: Is this a single-valued attribute of one concept?

Ask: "Is this a fact about a specific concept, with a single value at any point in time, and no independent identity of its own?"

If yes, it is a property. Properties live in the concept's `properties` list and get their own URI within the concept's namespace.

If the answer is "it has multiple values" (e.g., a person can have many phone numbers), it is still a property but its cardinality is `many`. Do not create a concept just because cardinality is greater than one.

### Step 3: Is the property's value drawn from a closed set of options?

Ask: "Does this property accept one answer from a defined list, where each option has a stable meaning?"

If yes, the value set is a vocabulary. Create a vocabulary YAML file and reference it from the property with `vocabulary: vocab-name`.

If the set is open-ended (e.g., a free-text description), the type is a primitive (`string`, `date`, `decimal`, etc.), not a vocabulary.

### Step 4: Should the property reference a concept or use an inline primitive?

Ask: "Does the value being stored have its own identity and properties, or is it a simple scalar?"

Reference a concept (`concept: Location`) when the target is a full concept with its own URI, its own properties, and is referenced from multiple places. A Location has coordinates, administrative levels, and is shared across Persons, Programs, and Events. It warrants a reference.

Use an inline primitive when the value is a simple scalar with no independent identity.

**Worked example: `latitude`**

`latitude` is an inline `decimal` on Location, not a reference to some `Latitude` concept. It has no independent identity. Nothing else references a latitude independently of its location. There are no "latitude properties." It is a number. Model it as a number.

### Summary table

| Situation | What to create |
|---|---|
| Has its own lifecycle, referenced from multiple concepts | Concept |
| Single attribute of a concept, no independent identity | Property |
| Property value is one of a closed set of options | Vocabulary |
| Property value has its own identity and sub-properties | Property referencing a concept (`concept: X`) |
| Property value is a simple scalar (number, date, string) | Inline primitive type |
