# Consent Record: Minimum Viable Set

When a form collects consent before proceeding with a survey or registration, the following PublicSchema properties provide a minimum viable ConsentRecord. Programs may add more fields, but these five capture the essential who-what-when chain that audit and data protection frameworks require.

## Properties

| Property | Type | Purpose |
|---|---|---|
| `consent_given` | boolean | Whether the subject gave consent. Gate for proceeding. |
| `consenting_party` | reference (Person) | Who gave consent (the subject, or a guardian for minors). |
| `consent_date` | date | When consent was given. |
| `purpose` | string (vocabulary: `consent-purpose`) | What the consent covers (e.g., registration, data sharing, research). |
| `privacy_notice_version` | string | Which version of the privacy notice was presented. |

## Usage notes

- If consent is refused (`consent_given: false`), the form should stop or branch. The ConsentRecord still gets created to document refusal.
- For household surveys, create one ConsentRecord per household (not per member) unless members are surveyed individually.
- `privacy_notice_version` lets auditors verify that the correct notice was shown. Store the version identifier, not the full notice text.

## See also

- [ADR-009: ConsentRecord and data governance layer](../../decisions/009-consent.md)
- [ConsentRecord concept](../../schema/concepts/consent-record.yaml)
