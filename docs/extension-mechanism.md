# Extending PublicSchema

## Principles

PublicSchema is descriptive, not prescriptive. Systems adopt the concepts, properties, and vocabularies that apply to them. When a system needs something PublicSchema does not provide, they extend it using their own namespace.

JSON-LD makes this straightforward: any term not in the PublicSchema context can be defined in an additional context.

## How to extend

### Adding custom properties to a PublicSchema concept

Use a second `@context` entry with your own namespace:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "beneficiary_category": "myorg:beneficiary_category",
      "proxy_score_v2": {
        "@id": "myorg:proxy_score_v2",
        "@type": "xsd:decimal"
      }
    }
  ],
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "beneficiary_category": "ultra_poor",
  "proxy_score_v2": 23.7
}
```

PublicSchema terms (`given_name`, `family_name`) resolve to PublicSchema URIs. Your custom terms (`beneficiary_category`, `proxy_score_v2`) resolve to your namespace. Both coexist cleanly.

### Adding custom vocabulary values

If a PublicSchema vocabulary does not cover your system's codes, extend it:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/"
    }
  ],
  "type": "Enrollment",
  "beneficiary": "...",
  "program_ref": "...",
  "enrollment_status": "myorg:waitlisted"
}
```

The verifier sees that `enrollment_status` has a value from your namespace, not from PublicSchema's canonical set. They can choose to accept it, map it to a canonical value, or flag it for review.

### Adding entirely new concepts

Define your concept in your own namespace:

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "CaseManagementRecord": "myorg:CaseManagementRecord",
      "case_worker": {"@id": "myorg:case_worker", "@type": "@id"},
      "case_notes": "myorg:case_notes"
    }
  ],
  "type": "CaseManagementRecord",
  "beneficiary": "did:web:example.gov/persons/123",
  "case_worker": "did:web:example.gov/staff/456",
  "case_notes": "Follow-up visit scheduled for 2025-04-15"
}
```

Note that `beneficiary` still resolves to the PublicSchema definition, even though it's used on a custom concept. Reuse PublicSchema terms where they apply.

## Rules of thumb

1. **Reuse before inventing.** Check PublicSchema's property list before defining a custom property. If a property exists with the right semantics, use it.

2. **Namespace your extensions.** Never define a bare term that could collide with a future PublicSchema addition. Always use a namespace prefix (`myorg:custom_field`).

3. **Document your extensions.** Publish your extended context at a stable URL so other systems can understand your data.

4. **Propose upstream.** If your extension turns out to be useful across multiple systems, propose it for inclusion in PublicSchema. The vocabulary grows through real-world usage, not committee design.

## For credential issuers

When issuing a Verifiable Credential that uses extensions:

- List your context URL after the PublicSchema context in the `@context` array
- Use the PublicSchema credential type (e.g., `EnrollmentCredential`) plus your own type if needed
- Extended properties follow the same data classification guidelines: annotate them as `non_personal`, `personal`, or `special_category` in your documentation

Verifiers who understand your context will process the extensions. Verifiers who don't will still understand all the PublicSchema terms.
