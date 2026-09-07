# Adopt Vocabularies

Vocabulary adoption is the lightest way to use PublicSchema. You align local codes and field values to canonical PublicSchema vocabularies without changing your internal data model.

This path is often the fastest way to create visible value. It can make reports comparable, simplify dashboards, reduce bilateral code translation, and prepare the ground for deeper mapping later.

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A before-and-after code mapping visual. Reader task: help an analyst see how local codes become comparable reporting values. The left side shows three systems using different local codes for enrollment status. The right side shows each local code mapped to canonical PublicSchema values such as active, suspended, completed, and pending.
</aside>

## User story

As a data manager coordinating reports across programs, I want each program to map its local status codes to PublicSchema vocabulary values, so that cross-program reporting uses the same meaning for each value.

## When to use this path

Use vocabulary adoption when:

- You need comparable reporting across programs, regions, countries, or donors.
- You want a shared set of API response codes.
- You are harmonizing exports from multiple systems.
- You need a quick win before deeper integration.
- Your internal data model is stable and cannot be changed soon.

Do not use vocabulary adoption alone when the problem is field structure, missing identifiers, unclear person-to-household relationships, or inconsistent enrollment models. Those require system mapping or new model design.

## Outputs

At the end of this path, you should have:

| Output | Purpose |
|---|---|
| Vocabulary inventory | The PublicSchema vocabularies relevant to your use case. |
| Local code inventory | The local code sets used by your system or reporting template. |
| Code crosswalk | A table mapping each local code to a PublicSchema code. |
| Gap list | Local values that have no PublicSchema equivalent, or PublicSchema values your system cannot represent. |
| Application rule | Where the mapping is applied: export, API response, dashboard, ETL, reporting template, or import pipeline. |
| Stewardship owner | The team responsible for updating the mapping when local codes or PublicSchema vocabularies change. |

## Step 1: Identify the vocabularies you need

Start with the business question. Do not map every vocabulary just because it exists.

Common starting points:

| If your system stores... | Look at... |
|---|---|
| Enrollment status | `enrollment-status` |
| Payment status | `payment-status` |
| Delivery channel | `delivery-channel` |
| Gender or sex values | `gender-type` or the relevant demographic vocabulary |
| Identifier types | `identifier-type` |
| Identity document types | `document-type` |
| Country | `country` |
| Currency | `currency` |

For each chosen vocabulary, download the CSV from the vocabulary page. The CSV is the most useful artifact for spreadsheet review and mapping workshops.

## Step 2: Inventory local values

Collect the local codes exactly as they appear in the source system.

Include:

- Code.
- Label.
- Definition, if available.
- Active or deprecated status.
- Example records.
- Source table, API field, report column, or form field.
- Any business rules attached to the value.

Labels are not enough. Two systems may both use "pending" while meaning different things. Read definitions, workflow rules, and example records.

## Step 3: Build the crosswalk

Create one row per local value.

| Local code | Local label | PublicSchema code | Match | Notes |
|---|---|---|---|---|
| `1` | Active | `active` | exact | Same operational meaning. |
| `2` | Suspended | `suspended` | exact | Temporary pause. |
| `3` | Closed | `completed` | close | Local code includes completed and administratively closed cases. |
| `4` | Archived | | no match | Historical storage status, not an enrollment status. |

Use match levels consistently:

| Match | Meaning |
|---|---|
| exact | The local value and PublicSchema value have the same meaning. |
| close | The values are close enough for the current use case, but not identical. |
| broad | The local value is broader than the PublicSchema value. |
| narrow | The local value is narrower than the PublicSchema value. |
| related | The values are related but should not be automatically substituted. |
| no match | No suitable PublicSchema value exists. |

For maintainable crosswalks, use the fuller template from [Templates and Checklists](/handbook/templates-and-checklists/):

| source_system | source_version | source_field | source_value | publicschema_vocabulary | publicschema_value | match_level | review_status | owner |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  | exact/close/broad/narrow/no match | draft/reviewed/approved |  |

## Step 4: Decide where mapping happens

Vocabulary mapping can be applied in several places:

| Location | Use when... |
|---|---|
| Export script | You need a canonical report or file extract. |
| API response layer | External consumers should see canonical values. |
| ETL pipeline | A warehouse or analytics platform is harmonizing multiple sources. |
| Dashboard layer | You cannot alter upstream data, but want comparable display values. |
| Lookup table | The product can store local and canonical values side by side. |
| Import adapter | Your system receives canonical values and must translate them inward. |

Document the choice. Future teams need to know whether canonical values are stored internally or generated at the boundary.

## Step 5: Validate examples

Take sample records from each local value and run them through the mapping. Confirm that the canonical value still makes sense in context.

Pay special attention to:

- Values that combine several meanings.
- Deprecated values still present in historical data.
- "Other" values that hide important local categories.
- Null, blank, unknown, refused, and not applicable values.
- Values that changed meaning over time.

## Step 6: Govern the crosswalk

Every crosswalk needs an owner and an update rule.

At minimum, record:

- Who approves mapping changes.
- Which version of PublicSchema was used.
- Which version of the local code set was mapped.
- When the mapping was last reviewed.
- Which downstream reports, APIs, or pipelines depend on it.

## Done means

Vocabulary adoption is complete when:

- Each in-scope local code has a documented PublicSchema mapping or documented no-match.
- The crosswalk is used in the agreed boundary.
- Sample outputs show canonical values.
- Ambiguous mappings are flagged, not hidden.
- A named owner can update the crosswalk.

## Next

- Use [Map Existing Systems](/handbook/map-existing-systems/) if the work reveals entity, field, or relationship problems.
- Use [Publish Exchanges and APIs](/handbook/publish-exchanges/) if the crosswalk will appear in a public boundary.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) when the crosswalk is ready for review or handover.
