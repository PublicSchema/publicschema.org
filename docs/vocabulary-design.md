# Vocabulary Design

Rules for controlled vocabularies. Builds on [Schema Design](../schema-design/).

## 1. Universal by default, domain-scoped by exception

A vocabulary lives at the root unless the same codes would carry different meanings across domains.

Examples:

- `payment-status` is universal. "Paid" means the same thing in social protection, health, and education.
- `targeting-approach` is domain-specific. "Proxy means testing" is social protection methodology with no equivalent in other domains.
- `severity` is ambiguous. In emergency alerting it means hazard impact; in health it means disease progression. Disambiguate by renaming (`event-severity`) or scoping to a domain.

Definitions must match scope. A universal vocabulary's definition must not reference a specific domain. Write "the lifecycle states of an enrollment in a program," not "...in a social protection program."

## 2. One concept per vocabulary

Each vocabulary answers one question. Do not combine orthogonal concerns.

- Status and outcome are different questions. "Where is this process?" vs. "What was the result?"
- Channel and modality are different questions. "How does the benefit reach the person?" vs. "What form does the benefit take?"

Do not split prematurely. If a single vocabulary cleanly captures the lifecycle and all mapped systems treat it as one field, splitting adds complexity without proven benefit.

## 3. Reference existing standards

If a formal code system exists, reference it. Three levels:

| Level | When to use | YAML field |
|---|---|---|
| **Sync** | Machine-readable standard defines the authoritative value set. | `standard` + `sync` |
| **Reference** | Standard exists but we don't sync (prose-only, partial overlap, deliberate simplification). | `references` |
| **None** | No relevant standard exists. | Neither field |

A vocabulary with no `standard`, no `references`, and no `system_mappings` is unvalidated. Acceptable at draft maturity; must be resolved before trial use.

Do not adopt a standard's codes when they don't serve the audience. ISO 20022 codes (RCVD, ACTC, ACSP) are for interbank messaging. Use readable codes; map to the standard.

Prefer machine-readable standards over prose-only ones. Machine-readable standards can be synced automatically; prose standards drift.

## 4. Domain annotations on individual values

When a universal vocabulary contains values that only apply to one domain, annotate the value rather than splitting the vocabulary:

```yaml
- code: graduated
  domain: sp
  label:
    en: Graduated
  definition:
    en: The beneficiary has exited through program-defined graduation criteria.
```

Use sparingly. If more than a third of values carry domain annotations, the vocabulary should move to a domain namespace.

## 5. Disambiguate collision-prone names

Before naming a vocabulary, ask: could another domain define a vocabulary with this name but different values?

- `severity` -> `event-severity`
- `certainty` -> `event-certainty`
- Never use bare `status`; always qualify (`enrollment-status`, `payment-status`)

## 6. The `other` code and system mappings

`other` is acceptable at draft maturity. Track what maps to it in real deployments. When the same unmapped value appears in 2+ systems, promote it to a named code.

System mappings are the primary validation mechanism:

- 3+ systems mapping to `other` = vocabulary gap. Promote to a named code.
- 4+ system codes mapping to one canonical value = vocabulary may be too coarse.
- System code mapping to `null` when a broader canonical code exists = mapping bug.

A vocabulary with zero system mappings is unvalidated. Add mappings before advancing maturity.
