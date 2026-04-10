# Vocabulary extraction from external systems

How to extract vocabularies (enums, value sets, coded fields) from an external system's codebase and map them to PublicSchema vocabularies.

## Why this exists

PublicSchema vocabularies need `system_mappings` that show how each external system represents the same concept. Extracting these mappings by hand is error-prone and hard to verify. This process uses AI subagents to read source code, extract vocabularies into a normalized format, and produce mappings we can review and verify.

## Prerequisites

- The external system's source code is cloned locally (under `external/<system>/raw/`)
- PublicSchema vocabularies exist in `schema/vocabularies/`

## Process overview

![Four-phase pipeline: Clone, Extract, Verify, Match, Write](/images/extraction-pipeline.svg)

## Phase 1: Extract

### Goal

Produce one JSON file per agent containing every vocabulary found in the assigned modules.

### Subagent setup

Split the codebase into clusters of related modules. Each cluster gets one subagent. The split should be by domain, not by size, so that a single agent has enough context to understand related vocabularies.

Example clustering for a Django project with 14 modules:

| Agent | Modules | Rationale |
|---|---|---|
| 1 | `social_protection`, `benefit_plan` | Enrollment and program lifecycle |
| 2 | `individual`, `insuree` | Person and group demographics |
| 3 | `payroll`, `payment`, `payment_cycle`, `contribution` | Financial flows |
| 4 | `claim`, `policy`, `grievance` | Claims and disputes |
| 5 | `location`, `product`, `core` | Infrastructure and config |

### Output contract

Each subagent writes a JSON file to `external/<system>/extracted/agent_<n>.json`.

The file must follow this exact schema:

```json
{
  "system": "<system-name>",
  "modules": ["<module-1>", "<module-2>"],
  "extracted_at": "<ISO 8601 timestamp>",
  "vocabularies": [
    {
      "name": "<ClassName or descriptive name>",
      "description": "<What this vocabulary represents, one line>",
      "source": {
        "module": "<module-name>",
        "file": "<relative path from raw/ directory>",
        "line": <line number where definition starts>,
        "pattern": "<TextChoices|IntegerChoices|choices_tuple|class_constants|graphene_enum|db_lookup_table|migration_data>",
        "raw_snippet": "<verbatim code block, max ~30 lines>"
      },
      "values": [
        {
          "code": "<the constant name, e.g. ACTIVE>",
          "db_value": "<the value stored in the database, e.g. 'ACTIVE' or 2>",
          "label": "<human-readable label if available>"
        }
      ]
    }
  ]
}
```

### Subagent prompt template

Each subagent receives a prompt like this (adapt per system):

```
You are extracting vocabularies from the <SYSTEM> codebase.

Your assigned modules are in these directories:
<list of directories>

A "vocabulary" is any set of named, coded values used as a controlled list:
- Django TextChoices or IntegerChoices classes
- choices= tuples on model fields
- Class-level constants that form a set (e.g., STATUS_ACTIVE = 2, STATUS_CLOSED = 4)
- Graphene Enum classes
- DB lookup table models (small reference tables with code/name fields)
- Seed data in migrations (RunSQL inserts, or initial_data in migration operations)

For each vocabulary you find:
1. Read the source file carefully.
2. Record the exact class name, file path, and starting line number.
3. Copy the raw code snippet verbatim (the class definition or choices tuple).
4. Extract each value with its code, database value, and label.
5. For DB lookup tables with no values in code, check migrations for seed data.

Do NOT invent values. If you cannot find the actual values, note that in the description
and set values to an empty array.

Do NOT include internal/infrastructure enums (file formats, module layers, signal types)
unless they represent domain concepts that could map to a shared vocabulary.

Write your output as JSON to: <output path>
```

### What to extract (inclusion criteria)

Extract vocabularies that represent **domain concepts**: statuses, types, roles, categories that describe people, enrollments, payments, groups, or other entities relevant to public service delivery.

### What to skip (exclusion criteria)

- Infrastructure enums: file formats, log levels, module configuration
- Internal process states: data upload pipeline states, mutation statuses
- System-specific concepts with no cross-system equivalent: ceiling types for insurance products, health facility sub-levels

When in doubt, extract it. It is easier to discard during matching than to re-run extraction.

## Phase 2: Verify

Three verification steps, in order of cost.

### Step 1: Schema validation (automated)

Check that every output file is valid JSON matching the schema above. Verify required fields are present, types are correct, and `values` arrays are non-empty (or explicitly noted as unavailable).

### Step 2: Source cross-reference (automated)

For each extracted vocabulary, grep the source file for key values to confirm they exist:

```bash
# For each vocabulary in the extracted JSON:
grep -n "<db_value>" "<raw_dir>/<source_file>"
```

Flag any value that does not appear in the referenced file. This catches hallucinated values.

### Step 3: Coverage check (automated)

Grep the entire codebase for vocabulary patterns the agents might have missed:

```bash
# Django TextChoices / IntegerChoices
grep -rn "models.TextChoices\|models.IntegerChoices" <raw_dir>/

# Inline choices tuples
grep -rn "choices=" <raw_dir>/ --include="models.py"

# Class constants that look like enums
grep -rn "STATUS_\|TYPE_\|ROLE_\|STAGE_" <raw_dir>/ --include="models.py"

# Graphene enums
grep -rn "graphene.Enum" <raw_dir>/
```

Compare the grep hits against what was extracted. Any unextracted hit needs a justification (either it was correctly excluded, or the agent missed it).

### Step 4: Human review

Open each `agent_<n>.json` file. For each vocabulary:
- Does the `description` make sense?
- Does `raw_snippet` match what you see at `source.file:source.line`?
- Are the `values` complete (not truncated)?
- Were any values invented that do not appear in the snippet?

This step takes ~5 minutes per agent file for a typical codebase.

## Phase 3: Match

### Goal

For each PublicSchema vocabulary, determine whether the external system has an equivalent, and if so, which extracted vocabulary it maps to.

### Matching criteria

A match exists when two vocabularies **describe the same real-world concept**, even if:
- They have different names (our `enrollment-status` vs. their `BeneficiaryStatus`)
- They have different granularity (our `child` vs. their `SON` + `DAUGHTER`)
- They split or merge values differently

A match does NOT exist when:
- The vocabularies happen to share a word but describe different domains
- The external vocabulary is purely internal/operational with no public-service equivalent

### Output

Produce a matching file at `external/<system>/matching.yaml`:

```yaml
system: <system-name>
matches:
  - v2_vocabulary: enrollment-status
    external_vocabulary: BeneficiaryStatus
    external_source: social_protection/models.py:42
    confidence: high
    notes: "Direct lifecycle equivalent. OpenIMIS POTENTIAL maps to our pending_verification."
    value_mapping:
      POTENTIAL: pending_verification
      ACTIVE: active
      GRADUATED: graduated
      SUSPENDED: suspended
    gaps:
      v2_only: [closed]
      external_only: []

  - v2_vocabulary: payment-status
    external_vocabulary: null
    confidence: null
    notes: "OpenIMIS splits payment across Payment.STATUS_CHOICES (legacy) and PayrollStatus (new). Neither maps cleanly."

no_match:
  - v2_vocabulary: benefit-frequency
    reason: "OpenIMIS does not have a vocabulary for benefit frequency; it is configured per product as numeric fields."
  - external_vocabulary: HealthFacilityStatus
    reason: "PublicSchema does not model health facility concepts."
```

### Doing the matching

This can be done by a single subagent or by hand. For ~30 vocabularies, manual matching is fast and more accurate. Use the subagent output and the v2 vocabulary files side by side.

## Phase 4: Write

### Goal

Update `system_mappings` in the relevant `schema/vocabularies/*.yaml` files using the enriched format.

### Format

System mappings use a structured format that shows each system's full vocabulary for a given concept: their code, their label, and the mapping to our canonical value. Gaps are explicit in both directions.

```yaml
system_mappings:
  openimis:
    vocabulary_name: "BeneficiaryStatus"
    values:
      - code: "POTENTIAL"
        label: "Potential"
        maps_to: pending_verification
      - code: "ACTIVE"
        label: "Active"
        maps_to: active
      - code: "GRADUATED"
        label: "Graduated"
        maps_to: graduated
      - code: "SUSPENDED"
        label: "Suspended"
        maps_to: suspended
    unmapped_canonical: [closed]
```

### Fields

- `vocabulary_name` (optional): the name the system uses for this vocabulary (e.g., the enum class name)
- `values`: list of the system's values for this vocabulary
  - `code`: the identifier used in the system (what is stored in the database or sent over the wire)
  - `label`: human-readable label the system uses for this value
  - `maps_to`: our canonical value code, or `null` if the system value has no equivalent
- `unmapped_canonical` (optional): list of our canonical value codes that no system value maps to (reverse gaps)

### Rules

- Only add mappings where a match was confirmed in Phase 3
- The `code` field must be the external system's `db_value` (what is stored in their database), not the label
- When multiple external values map to one PublicSchema value, list each one separately (many-to-one is fine)
- System values with no canonical equivalent use `maps_to: null`
- Our canonical values with no system equivalent are listed in `unmapped_canonical`
- Do not delete existing mappings for other systems
- Get code and label from `enums.json` when available; fall back to matching.yaml or manual lookup

## Reuse for other systems

To run this process for a new system:

1. Clone the system's source code to `external/<system>/raw/`
2. Study the codebase to understand how it defines vocabularies (the patterns will differ per tech stack)
3. Adjust the subagent prompt template for the system's tech stack (e.g., Java enums, TypeScript unions, SQL reference tables)
4. Follow Phases 1 through 4

### Tech stack cheat sheet

| Stack | Where to look |
|---|---|
| Django | `models.py` (TextChoices, IntegerChoices, choices=), `enums.py`, migrations |
| Odoo | `fields.Selection` tuples, `_selection_*` methods, XML data files (`<record model="...">`) |
| Java/Spring | `enum` classes, `@Enumerated` fields, Flyway/Liquibase migrations |
| TypeScript | `enum` declarations, `as const` objects, Zod `z.enum()` schemas |
| .NET | `enum` classes, EF Core `HasConversion`, seed data in migrations |
| SQL-first | `CREATE TYPE ... AS ENUM`, `CHECK` constraints, reference/lookup tables |
| FHIR | CodeSystem JSON resources, ValueSet definitions |
| OpenAPI | `enum` arrays in schema definitions |
| GraphQL | `enum` type declarations in `.graphql` schema files |

### Reference standard equivalence

When both PublicSchema and the external system use the same international standard (e.g., both use ISO 3166-1 for countries), do not create value-level `system_mappings`. Instead, record the equivalence in the matching file:

```yaml
  - v2_vocabulary: country
    external_vocabulary: Country (ISO 3166-1)
    external_source: "vocabulary_country.xml"
    confidence: high
    same_standard: true
    notes: "Both use ISO 3166-1 alpha-2 codes. No value-level mapping needed."
```

The `same_standard: true` flag means: "these vocabularies are semantically identical because they both implement the same standard." No `value_mapping` or `system_mappings` entry is needed.

## File layout

After running for a system called `openimis`:

```
external/
  openimis/
    raw/                          # cloned source code (gitignored)
    extracted/
      agent_1.json                # Phase 1 output
      agent_2.json
      ...
    matching.yaml                 # Phase 3 output
```

The final mappings live in `schema/vocabularies/*.yaml` under `system_mappings.<system>`.

## System-specific notes

### OpenIMIS (Django)

**Source:** `external/openimis/raw/`

**Vocabulary patterns (6):**
1. `TextChoices` / `IntegerChoices` classes
2. Inline `choices=` tuples on model fields
3. Integer constants that form a set (e.g., `STATUS_ACTIVE = 2`)
4. DB lookup table models (small reference tables with code/name fields, values in test_helpers or migrations)
5. Graphene `Enum` classes
6. Seed data in migrations (`RunSQL` inserts)

**Module clustering:** Split by domain (social_protection + benefit_plan, individual + insuree, payroll + payment, claim + grievance, location + core).

**Gotchas:**
- DB lookup tables (Gender, Education, Profession, Relation) have no values in `models.py`. Check `test_helpers.py` and migrations for seed data.
- The system has both legacy health insurance modules and newer social protection modules. Both may define vocabularies for similar concepts (e.g., Payment.STATUS_CHOICES vs. PayrollStatus).

### OpenSPP (Odoo / Python)

**Source:** `external/openspp/raw/OpenSPP2/`

**Vocabulary patterns (3):**

1. **`spp.vocabulary` / `spp.vocabulary.code` database records** (primary system).
   Defined in XML data files under `spp_vocabulary/data/` and `spp_farmer_registry_vocabularies/data/`. Each vocabulary has a `namespace_uri` (e.g., `urn:iso:std:iso:5218`). Values are `<record model="spp.vocabulary.code">` elements with `code`, `display`, `definition`, `sequence` fields.

2. **JSON vocabulary source files** in `openspp-vocabularies/vocabularies/`.
   10 JSON files with `codes` arrays. These document the same vocabularies as the XML but in a more parseable format. Use these as the primary extraction source when available.

3. **`fields.Selection` tuples** on Odoo models.
   Used for workflow states and configuration flags. Found in `models/` directories across modules. Sub-patterns include `selection="_selection_method"` (dynamic) and `selection_add=[...]` (inheritance extension).

**Two-pass extraction:**
- **Pass A:** Parse JSON vocabulary files + XML data files for the structured vocabulary system.
- **Pass B:** Scrape `fields.Selection` from model files for workflow/status vocabularies.

**Module exclusions:** Skip all `spp_demo_*` modules (demo/test data only).

**Module clustering for Pass B:**
| Agent | Modules | Rationale |
|---|---|---|
| 1 | `spp_programs`, `spp_approval` | Program lifecycle, entitlements, cycles |
| 2 | `spp_registry`, `spp_change_request_v2`, `spp_consent` | Registry, change requests, consent management |
| 3 | `spp_grm`, `spp_case_base`, `spp_graduation` | Grievance, case management, graduation |
| 4 | `spp_hazard`, `spp_scoring`, `spp_event_data`, `spp_farmer_registry` | Hazards, scoring, events, agriculture |

**Reference standard vocabs (same standard as v2):**
- ISO 3166-1 (countries), ISO 4217 (currencies), ISO 639 (languages): record as `same_standard: true`, no value-level mapping.

**Agriculture vocabs:** Track farm type, crop classification, livestock, land tenure, etc. as no-match entries. PublicSchema does not yet have dedicated agriculture vocabularies.

### OpenCRVS (TypeScript / Node.js)

**Source:** `external/opencrvs/raw/repo/`

**Vocabulary patterns (5):**

1. **`const ... as const` objects** (modern pattern, in `packages/commons/src/events/`).
   Example: `export const ActionType = { DELETE: 'DELETE', ... } as const`

2. **Zod `z.enum()` schemas** (modern v2 pattern, same locations).
   Example: `export const EventStatus = z.enum(['CREATED', 'NOTIFIED', ...])`

3. **TypeScript `enum` declarations** (legacy, in `packages/client/`, `packages/user-mgnt/`).
   Example: `export enum RegStatus { IN_PROGRESS, DECLARED, ... }`

4. **GraphQL `enum` types** (in schema files and auto-generated gateway types).
   Example: `enum Gender { male, female, other, unknown }`

5. **Mongoose schema `enum` arrays** (database-level validation in `packages/user-mgnt/`, `packages/config/`).

**Canonical source selection:** Many vocabularies are defined redundantly across patterns 1-5. Pick the canonical source in this priority order:
1. `packages/commons/src/` (shared library, authoritative)
2. `packages/events/src/` (event service)
3. `packages/user-mgnt/src/` (user management)
4. `packages/config/src/` (configuration)
5. `packages/client/src/` (frontend, often auto-generated or duplicated)

Skip auto-generated files (e.g., `packages/client/src/utils/gateway.ts`) unless the vocabulary is not defined elsewhere.

**Country-configurable vocabularies:** Some domain vocabularies (marital status, education level, birth type, manner of death, attendant at birth) are NOT defined in the core codebase. They are `String` fields whose values come from country-level deployment configuration. Record these as:

```yaml
  - v2_vocabulary: marital-status
    external_vocabulary: null
    confidence: null
    notes: "OpenCRVS does not define marital status values in core. Values are country-configurable at deployment time."
    country_config: true
```

**CRVS-specific vocabularies:** Most OpenCRVS vocabularies are civil registration workflow states (DECLARED, REGISTERED, CERTIFIED, ISSUED) with no social protection equivalent. Track these as no-match entries.

**FHIR alignment:** Note when OpenCRVS values follow FHIR code systems (Gender follows AdministrativeGender, TelecomSystem/TelecomUse follow FHIR ContactPoint).

### DHIS2 (Java / OpenAPI)

**Source:** `external/dhis2/`

**Pre-extracted data:** Vocabularies are already extracted by the `convert.py` script into two files:
- `enums.json`: 8 core enums from the OpenAPI spec (EnrollmentStatus, EventStatus, Gender, Civil status, ValueType, FeatureType, AccessLevel, RelationshipEntity, ProgramType)
- `option-sets.json`: 221 option sets from the demo instance metadata API

Phase 1 (Extract) and Phase 2 (Verify) are already done. Start directly at Phase 3 (Match).

**Key characteristics:**
- DHIS2 is a platform, not a product. Most domain vocabularies are configurable per instance via option sets, not hardcoded in the core.
- The `enums.json` contains only structural/core enums. Of these, only EnrollmentStatus, Gender, and Civil status map to PublicSchema domain vocabularies.
- The `option-sets.json` is from a demo instance and contains health-program-specific option sets (ICD codes, malaria treatments, ARV drugs). These are not representative of all DHIS2 deployments.
- Gender has only Male/Female (no "other" or "unknown") in the demo instance.
- Civil status has only 2 values ("Single or widow", "Married (conjugal cohabitation)"), a minimal subset.

**Matching approach:** Match against `enums.json` only. Option sets are instance-specific and should not be treated as DHIS2 core vocabularies.

### FHIR R4 (HL7 / JSON)

**Source:** `external/fhir-r4/`

**Pre-extracted data:** Vocabularies are already extracted by the `convert.py` script:
- `enums.json`: 104 value sets from FHIR R4 StructureDefinitions and bound ValueSets

Phase 1 (Extract) and Phase 2 (Verify) are already done. Start directly at Phase 3 (Match).

**Key characteristics:**
- FHIR is both a standard and a data exchange format. Some PublicSchema vocabularies use FHIR code systems as their source standard (marital-status uses FHIR v3-MaritalStatus, gender-type syncs from FHIR AdministrativeGender).
- When our vocabulary's `standard` or `sync.source_url` references a FHIR code system, use `same_standard_systems: [fhir_r4]` rather than value-level mappings, since our values are derived from FHIR.
- When a FHIR value set covers the same domain but uses different codes or granularity, use value-level `system_mappings.fhir_r4`.
- Many FHIR enums are health-care-specific (dental sites, diagnosis codes, claim types) with no social protection equivalent.
- FHIR's Identifier Type Codes use HL7 v2 table codes (DL, PPN, BRN, TAX, etc.) which map to our identifier types.
- FHIR's PatientRelationshipType is a large superset (45 codes) covering clinical, insurance, and family relationships. Only the family relationship subset maps to our relationship-type.

**Matching approach:** Review all 104 enums. Most are health-specific no-matches. Focus on: AdministrativeGender, Marital Status Codes, Identifier Type Codes, PatientRelationshipType, SubscriberRelationshipCodes, PaymentStatusCodes, CommonLanguages, GroupType.
