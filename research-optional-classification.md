# Research: Making data_classification optional

## Goal

Change `data_classification` from a required annotation on every property to an optional one. Only classify properties where the sensitivity is **inherent to the data itself**, not context-dependent. Properties whose sensitivity depends on usage context (e.g., latitude on a Location that could be a district or a beneficiary's home) are left unclassified.

## Principle

Sensitivity comes from the **association with a person**, not the data value itself. GPS coordinates aren't personal; GPS coordinates of someone's home are personal. The "personal" part comes from the Household->Location link, not from the coordinate values.

Three signals:
- `personal` / `special_category`: this data is always sensitive regardless of context
- `non_personal`: this is structurally never personal (positive assertion)
- absent: depends on usage context; implementer decides

## What needs to change

### 1. Property YAML files (remove classification from context-dependent properties)

Properties to **unclassify** (remove `data_classification` line):

| Property | Current | Why context-dependent |
|---|---|---|
| `latitude` | personal | Personal on Household/Farm, not on a district office |
| `longitude` | personal | Same |
| `street_address` | personal | Personal on a household address, not on an organization address |
| `house_number` | personal | Same |
| `building_name` | personal | Same |
| `city` | personal | Same |
| `postal_code` | personal | Same |
| `country` | personal | Same |
| `administrative_area` | personal | Same |

Properties to **keep classified**:

- `location` (concept:Location reference on Household/Farm): stays `personal` because it's the *link* that carries the sensitivity
- `address` (concept:Address reference on Household): stays `personal`, same reason
- `parent_location` (concept:Location reference on Location): stays `non_personal`, structural hierarchy
- `location_name`, `location_code`, `administrative_level`: stay `non_personal`, they describe the place structure
- All person names, DOB, identifiers, person references, etc.: stay as-is

### 2. Schema: `build/schemas/property.schema.json`

`data_classification` is already not in `required`. No schema change needed. The enum definition stays the same.

### 3. Tests: `tests/test_integration.py`

- **`test_data_classification_annotations_present`** (line 153): currently fails if ANY property has `data_classification: None`. Must be changed to allow None (i.e., remove this test or change it to only validate that the value is valid *when present*).
- **`test_data_classification_levels_are_valid`** (line 164): currently iterates all properties and fails if value not in the valid set. Must be changed to skip properties where classification is None/absent.

### 4. Build pipeline: `build/build.py`

- Line 102-103: `_embedded_property_jsonld()` already guards with `if prop_out.get("data_classification")`, so it will naturally skip emitting `ps:dataClassification` when absent. **No change needed.**
- Line 394: `build_vocabulary()` copies `data.get("data_classification")` which will be None if absent. **No change needed** (downstream consumers already handle None).

### 5. Export: `build/export.py`

- Line 171: CSV export uses `prop.get("data_classification") or ""`. **No change needed** (empty string for absent).
- Line 323: Excel export same pattern. **No change needed.**

### 6. Site TypeScript: `site/src/data/vocabulary.ts`

- Line 49: `data_classification: string | null`. **Already nullable. No change needed.**

### 7. Site rendering: `site/src/pages/[...slug].astro`

- Lines 148, 221-225: renders a badge for classification. Must check if it gracefully handles null. If not, add a conditional.

### 8. Site CSS: `site/src/styles/global.css`

- Badge classes exist for all three values. No change needed (if the badge isn't rendered, the CSS is irrelevant).

### 9. Documentation

- **`CONTRIBUTING.md`** (lines 79-86): update classification rules to explain the three-signal model (classified personal, classified non_personal, unclassified = context-dependent).
- **`docs/selective-disclosure.md`**: add guidance for unclassified properties (issuer decides based on context).
- **`CLAUDE.md`**: update the "Data classification rules" section.
- **`docs/meta-namespace.md`**: update description of `ps:dataClassification` to note it's optional.

### 10. Tests: `tests/test_export.py`

- Lines 43-53, 161-163, 172-181: test fixtures use explicit classification values. These should still work since the properties in the test data have classification set. **No change needed** unless we add a test for an unclassified property.

## Files to modify (ordered)

1. 9 property YAML files (remove `data_classification` line)
2. `tests/test_integration.py` (update 2 test functions)
3. `site/src/pages/[...slug].astro` (check null handling for badge)
4. `CONTRIBUTING.md` (update classification rules section)
5. `docs/selective-disclosure.md` (add unclassified guidance)
6. `docs/meta-namespace.md` (note optionality)
7. `CLAUDE.md` (update classification rules)
8. `plan-data-classification.md` (can be deleted or archived, it's a completed migration plan)

## What does NOT need to change

- `build/schemas/property.schema.json` (already optional)
- `build/build.py` (already guards with `if` / `.get()`)
- `build/export.py` (already handles None)
- `site/src/data/vocabulary.ts` (already nullable)
- `site/src/styles/global.css` (badge styles stay, just won't render for unclassified)
