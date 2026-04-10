# Schema Design

## 1. Naming conventions

Casing encodes element type:

| Element type | Convention | Examples |
|---|---|---|
| Concepts | PascalCase | Person, Enrollment, GroupMembership |
| Properties | snake_case | given_name, date_of_birth |
| Vocabulary value codes | snake_case | never_married, bank_transfer |
| Vocabulary identifiers | kebab-case | gender-type, enrollment-status |

Enforced by JSON Schema regex validators. Once a name is published at trial-use or above, it cannot be changed.

## 2. Domain-scoped URIs

Some concepts share a name across domains but carry different semantics ("Enrollment" in social protection vs. education). Domain-specific elements get a domain segment in their URI; universal elements live at the root:

- `publicschema.org/sp/Enrollment` (social protection)
- `publicschema.org/Person` (universal)

The test: an element is universal if the same definition carries the same meaning regardless of domain. If not, it belongs in a domain namespace.

Names are never prefixed with a domain abbreviation. It is `Enrollment`, not `SPEnrollment`. The URI structure handles disambiguation.

| Code | Domain | Status |
|---|---|---|
| `sp` | Social protection | Active |
| `edu` | Education | Future |
| `health` | Health | Future |
| `crvs` | Civil registration and vital statistics | Future |

## 3. URI persistence

Every element gets a stable URI. Once published at trial-use or above, a URI will not be removed. Deprecated terms continue to resolve with metadata indicating the replacement. See [Versioning and Maturity](../versioning-and-maturity/) for the full model.

## 4. Concept, property, or vocabulary

Use this decision tree to determine what kind of element to create.

**Step 1: Does it have its own identity?** Does this thing exist independently, get referenced from multiple places, and have its own lifecycle? If yes, it is a **concept**.

*Example:* GroupMembership is a concept, not a property on Person or Group. It carries its own data (role, dates), has its own lifecycle, and is referenced from both sides.

**Step 2: Is it an attribute of a concept?** A fact about a specific concept, with no independent identity? If yes, it is a **property**. Multiple values (e.g., phone numbers) still make it a property with cardinality `many`.

**Step 3: Is the value drawn from a closed set?** If the property accepts one answer from a defined list with stable meanings, the value set is a **vocabulary**.

**Step 4: Reference or inline?** If the value has its own identity and properties, reference a concept (`concept: Location`). If it is a simple scalar, use an inline primitive.

*Example:* `latitude` is an inline `decimal` on Location. It has no independent identity, no sub-properties. It is a number.

| Situation | Element type |
|---|---|
| Own lifecycle, referenced from multiple concepts | Concept |
| Attribute of a concept, no independent identity | Property |
| Value from a closed set of options | Vocabulary |
| Value has its own identity and sub-properties | Property referencing a concept |
| Simple scalar | Inline primitive type |

## 5. Temporal context

Almost everything in public service delivery is time-bounded. A status snapshot without a validity period is incomplete. When designing a concept or property, ask: will this value change over time? If yes, model the temporal context explicitly (start/end dates, validity periods).

## 6. Property independence

A property like `start_date` is defined once and reused across concepts. When a shared property needs concept-specific value sets (e.g., `status` on Enrollment vs. Grievance), it specializes via different vocabulary references rather than pretending the differences don't exist.

## 7. Sensitivity annotations

Some properties reveal sensitive circumstances regardless of whether they identify a specific person. `program_ref` reveals enrollment in a specific program (which may target HIV, disability, or poverty). `grievance_type` reveals that someone filed a complaint.

| Level | When to use | What it signals |
|---|---|---|
| `standard` | Default. No special handling beyond normal data protection. | Can be omitted (assumed if absent). |
| `sensitive` | Reveals circumstances (health, poverty, victimhood) in most contexts. | Requires justification to collect or disclose. |
| `restricted` | Should not appear in credentials at routine service points. | Requires a Data Protection Impact Assessment. |

This is a practitioner warning, not a compliance label. Whether a property constitutes personal data depends on the record it appears in, not the property itself. See [Selective Disclosure](../selective-disclosure/) for credential-level classification.
