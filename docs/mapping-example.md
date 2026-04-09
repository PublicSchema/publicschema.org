# Worked Example: Using Vocabulary Mappings

This walkthrough shows how to convert a status value from a real system into its canonical PublicSchema equivalent, and back again.

## Scenario: Converting an OpenIMIS enrollment record

You are building an integration that reads enrollment data from OpenIMIS and normalizes it for a cross-program dashboard. OpenIMIS returns a beneficiary record like this:

```json
{
  "beneficiary_id": "B-00421",
  "program_id": "CCT-NORTH-2024",
  "BeneficiaryStatus": "POTENTIAL",
  "enrollment_date": "2024-03-15"
}
```

The field `BeneficiaryStatus` uses OpenIMIS's own vocabulary. To store or compare this value in a system-neutral way, you need to map it to the canonical `enrollment-status` vocabulary.

## Step 1: Look up the system mapping

Open `schema/vocabularies/enrollment-status.yaml` and find the `openimis` block under `system_mappings`:

```yaml
system_mappings:
  openimis:
    vocabulary_name: BeneficiaryStatus
    values:
    - code: POTENTIAL
      label: Potential
      maps_to: pending_verification
    - code: ACTIVE
      label: Active
      maps_to: active
    - code: GRADUATED
      label: Graduated
      maps_to: graduated
    - code: SUSPENDED
      label: Suspended
      maps_to: suspended
    unmapped_canonical:
    - waitlisted
    - closed
```

Each entry in `values` is a direct one-to-one code mapping. `unmapped_canonical` lists canonical values that have no OpenIMIS equivalent.

## Step 2: Find the canonical value

The incoming value is `POTENTIAL`. Looking at the table above:

| OpenIMIS code | Canonical code |
|---|---|
| POTENTIAL | `pending_verification` |

The canonical value is `pending_verification`.

What does that mean? From the vocabulary definition:

> The application is awaiting document or data verification before enrollment is confirmed.

So `POTENTIAL` in OpenIMIS represents a beneficiary who has applied but whose documents or eligibility data have not yet been confirmed. The canonical label makes that intent explicit for any system reading it.

## Step 3: Reverse direction (canonical to system)

Now suppose you are writing data back to OpenIMIS and you have a canonical value of `active`. You reverse the lookup: find the row where `maps_to` equals `active`, and use its `code`.

| Canonical code | OpenIMIS code |
|---|---|
| `active` | `ACTIVE` |

That gives you `ACTIVE` to send back.

But not every canonical value has an OpenIMIS equivalent. The `unmapped_canonical` list tells you which ones fall through:

```yaml
unmapped_canonical:
- waitlisted
- closed
```

If you have a record with canonical status `closed` and need to write it to OpenIMIS, there is no direct code to use. You will need to decide how to handle it in your integration (skip the record, flag it for review, use a default, etc.). The vocabulary does not make that decision for you, but it tells you explicitly that a gap exists.

## Where mappings require judgment

Most of the codes above are clean lookups: one code in, one code out. A few cases require more thought.

**GRADUATED maps cleanly.** OpenIMIS `GRADUATED` maps to `graduated`, which is a social-protection-specific canonical value meaning the beneficiary exited through program-defined graduation criteria. DHIS2 has no equivalent at all (`graduated` is in its `unmapped_canonical` list), so if you are normalizing records from both systems, you will only see `graduated` coming from OpenIMIS or OpenSPP sources.

**`closed` is the tricky one.** OpenIMIS has no code for `closed`. In DHIS2, both `COMPLETED` and `CANCELLED` map to `closed`. This means the reverse direction is ambiguous: if you have a canonical `closed` record and need to write it into DHIS2, you cannot determine from the canonical value alone whether it should be `COMPLETED` or `CANCELLED`. That distinction carries real meaning (a program that completed versus one that was cancelled) but it is lost during normalization.

This is where domain expertise matters, not just code. When mapping from canonical back to a system that has finer-grained distinctions, you will need additional context, either from the original source record, the program's business rules, or a human reviewer. The vocabulary makes the gap visible; it does not paper over it.
