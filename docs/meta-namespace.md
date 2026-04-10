# The `ps:` Meta Namespace

## Overview

PublicSchema JSON-LD documents use terms prefixed with `ps:` for vocabulary-level metadata that does not map to existing RDF/RDFS/SKOS/schema.org predicates. The `ps:` prefix expands to `https://publicschema.org/meta/`.

These terms describe the vocabulary itself (maturity, domain, cardinality) rather than the data being exchanged. They are informational and do not affect JSON-LD expansion or compaction of domain data.

## Term definitions

| Term | Used on | Type | Description |
|---|---|---|---|
| `ps:maturity` | Concepts, properties, vocabularies, vocabulary values | `string` | Lifecycle stage: `draft`, `trial_use`, or `normative`. |
| `ps:domain` | Concepts, properties, vocabularies | `string` or `null` | Domain namespace code (`sp`, `edu`, `health`, `crvs`). Null for universal terms. |
| `ps:cardinality` | Properties | `string` | Whether the property accepts a single value (`single`) or multiple values (`multiple`). |
| `ps:vocabulary` | Properties | `URI` | URI of the controlled vocabulary that constrains this property's values. |
| `ps:references` | Properties | `URI` | URI of the concept that this property points to (for reference properties). |
| `ps:sensitivity` | Properties | `string` | Practitioner warning about the nature of the information: `standard` (default, no special handling), `sensitive` (reveals circumstances like health, poverty, or victimhood in most contexts), or `restricted` (should not appear in credentials at routine service points). This is not a compliance label or PII classification; whether a property constitutes personal data depends on the record it appears in, not the property itself. Optional; `standard` is assumed when absent. |
| `ps:standardReference` | Vocabularies | `object` | Reference to an international standard the vocabulary is based on. Contains `schema:name`, optional `@id` (standard URI), and optional `ps:notes`. |
| `ps:standardCode` | Vocabulary values | `string` | The code used by the referenced international standard for this value. |
| `ps:notes` | Various | `string` | Free-text notes, typically on standard references. |
| `ps:subtypes` | Concepts | `array of URIs` | Concepts that specialize this concept. |

## Context declaration

The `ps:` prefix is declared in the PublicSchema JSON-LD context:

```json
{
  "@context": {
    "ps": "https://publicschema.org/meta/"
  }
}
```

Any JSON-LD processor that loads the PublicSchema context will resolve `ps:maturity` to `https://publicschema.org/meta/maturity`, etc.

## Design rationale

These terms exist because no standard RDF vocabulary covers vocabulary-management metadata at the level PublicSchema needs. For example, `ps:sensitivity` has no equivalent in RDFS, SKOS, or schema.org. Rather than overload existing predicates or leave this metadata unstructured, PublicSchema defines a small, stable set of terms in its own namespace.

The `ps:` namespace is intentionally narrow. If a standard predicate exists for a concept (e.g., `rdfs:subClassOf` for type hierarchy), PublicSchema uses the standard predicate. `ps:` terms are only introduced when no standard alternative is available.
