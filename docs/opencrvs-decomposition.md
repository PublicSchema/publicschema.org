# Decomposing OpenCRVS Registrations into PublicSchema CRVS Records

This guide shows how to translate an OpenCRVS v1 `BirthRegistration` (or
`DeathRegistration` / `MarriageRegistration`) payload into the three
PublicSchema CRVS records it represents, and how to compose them back for
systems that expect the bundled form.

The decomposition is not optional. It is the price of the different modelling
choices in the two systems.

## Why two models disagree

OpenCRVS bundles three things into a single `*Registration` type:

1. The **vital event**: the occurrence itself (a birth, a death, a marriage).
2. The **civil status record**: the administrative entry in the register
   (tracking ID, registration number, page, book, workflow status).
3. The **workflow wrapper**: the audit trail (`RegWorkflow[]`, `history[]`)
   that shows how the record moved through declaration, validation, and
   registration.

PublicSchema keeps these separate, following the civil-law distinction
between `fait` (the fact), `acte` (the legal act that records it), and
`extrait` (the certificate issued on demand):

| Civil-law term | PublicSchema concept | OpenCRVS location |
|---|---|---|
| Fait | `Birth`, `Death`, `Marriage` (subtypes of `VitalEvent`) | The top-level `*Registration` fields about the event |
| Acte | `CivilStatusRecord` | The embedded `registration` sub-object |
| Extrait | `Certificate` | `registration.certificates[]` |

Neither model is wrong. OpenCRVS optimises for a single workflow payload;
PublicSchema optimises for tracking each aspect independently across time
(an acte can be corrected; new extraits can be issued long after the event).
The mapping is `broad` because OpenCRVS's `*Registration` is genuinely wider
than any one PublicSchema concept.

## A worked example: one BirthRegistration, three records

### The OpenCRVS payload

```json
{
  "id": "br-0a1c2f",
  "child": {
    "name": [{ "firstNames": "Ada", "familyName": "Baraka" }],
    "gender": "female",
    "birthDate": "2026-02-14",
    "multipleBirth": 1
  },
  "mother": {
    "name": [{ "firstNames": "Amina", "familyName": "Baraka" }],
    "nationality": ["KE"]
  },
  "father": {
    "name": [{ "firstNames": "Joseph", "familyName": "Baraka" }],
    "nationality": ["KE"]
  },
  "informant": {
    "relationship": "MOTHER",
    "name": [{ "firstNames": "Amina", "familyName": "Baraka" }]
  },
  "eventLocation": { "id": "loc-7", "type": "HEALTH_FACILITY" },
  "birthType": "SINGLE",
  "weightAtBirth": 3.2,
  "attendantAtBirth": "MIDWIFE",
  "registration": {
    "trackingId": "BXYZ12",
    "registrationNumber": "2026-KE-0001337",
    "type": "BIRTH",
    "status": [
      { "type": "DECLARED",   "timestamp": "2026-02-20T10:00:00Z" },
      { "type": "REGISTERED", "timestamp": "2026-02-22T14:15:00Z" }
    ],
    "certificates": [
      { "certificateTemplateId": "farajaland-birth-v2" }
    ]
  },
  "createdAt": "2026-02-20T10:00:00Z"
}
```

### Record 1: the `Birth`

```json
{
  "_concept": "Birth",
  "child": { "given_name": "Ada", "family_name": "Baraka", "sex_at_birth": "female" },
  "parents": [
    { "person": { "given_name": "Amina", "family_name": "Baraka", "nationality": ["KE"] },
      "parental_role": "biological_mother" },
    { "person": { "given_name": "Joseph", "family_name": "Baraka", "nationality": ["KE"] },
      "parental_role": "biological_father" }
  ],
  "informant": { "given_name": "Amina", "family_name": "Baraka" },
  "event_date": "2026-02-14",
  "event_location": "loc-7",
  "birth_type": "single",
  "birth_order": 1,
  "weight_at_birth": 3.2,
  "attendant_at_birth": "midwife"
}
```

Two transforms are worth calling out:

- **Parents are reified.** OpenCRVS gives you `mother: Person` and
  `father: Person` with the role implicit in the slot name. PublicSchema
  wraps each `Person` in a `Parent` link entity that carries an explicit
  `parental_role`. In v1 you can only produce `biological_mother` and
  `biological_father`; adoptive, legal, and surrogate roles are not
  representable.
- **The event date comes from the child.** `BirthRegistration` has no
  top-level `event_date`; use `child.birthDate`.

### Record 2: the `CivilStatusRecord`

```json
{
  "_concept": "CivilStatusRecord",
  "record_id": "2026-KE-0001337",
  "record_type": "birth",
  "registration_status": "registered",
  "originating_event": { "_ref": "Birth", "_opencrvs_id": "br-0a1c2f" }
}
```

This record is built from the `registration` sub-object:

- `registrationNumber` becomes `record_id`.
- `type` (a `RegistrationType` value, uppercase) is lower-cased and mapped
  through the `civil-status-record-type` vocabulary.
- The current `registration_status` is the `type` on the most recent entry
  in `registration.status[]`, mapped through the `registration-status`
  vocabulary (here `REGISTERED` → `registered`).

The `originating_event` link is synthetic: OpenCRVS's `Registration` is
embedded inside the `*Registration`, so the relationship is structural
rather than a named reference field. You have to construct the link
yourself.

### Record 3: the `Certificate`

```json
{
  "_concept": "Certificate",
  "certificate_document_type": "birth_certificate",
  "vital_event": { "_ref": "Birth", "_opencrvs_id": "br-0a1c2f" },
  "civil_status_record": { "_ref": "CivilStatusRecord", "record_id": "2026-KE-0001337" }
}
```

Each entry in `registration.certificates[]` becomes a separate
`Certificate` record. OpenCRVS's `Certificate.certificateTemplateId` is a
free string that points at a country-configured template; mapping it to
`certificate_document_type` requires knowledge of the local template
catalogue. When the template is unknown, fall back to the coarse category
implied by the event (a `BirthRegistration` certificate is a
`birth_certificate`).

`issue_date`, `issuing_office`, and `certificate_format` have no OpenCRVS
source fields and are left unset in v1.

## Field routing reference

The full field-by-field routing lives in
[`external/opencrvs/matching.yaml`](../external/opencrvs/matching.yaml)
under `concept_matches[*].decomposition`. The yaml is the authoritative
source; this guide is a readable summary.

A condensed view for `BirthRegistration`:

| OpenCRVS field | Target concept | Target property |
|---|---|---|
| `child` | Birth | `child` |
| `mother` / `father` | Birth | `parents` (wrapped in `Parent`) |
| `informant` | VitalEvent | `informant` |
| `eventLocation` | VitalEvent | `event_location` |
| `birthType` | Birth | `birth_type` |
| `weightAtBirth` | Birth | `weight_at_birth` |
| `attendantAtBirth` | Birth | `attendant_at_birth` |
| `child.birthDate` | VitalEvent | `event_date` |
| `child.multipleBirth` | Birth | `birth_order` |
| `child.gender` | Birth | `sex_at_birth` |
| `registration.registrationNumber` | CivilStatusRecord | `record_id` |
| `registration.type` | CivilStatusRecord | `record_type` |
| `registration.status` | VitalEvent | `registration_status` |
| `registration.certificates` | Certificate | (one record each) |
| `foetalDeathsToMother` | (unmapped: statistical count) | (n/a) |
| `history` | (unmapped: audit trail) | (n/a) |

`DeathRegistration` and `MarriageRegistration` follow the same shape;
differences are documented in `matching.yaml`.

## Going the other way: composing a `BirthRegistration`

When sending data to an OpenCRVS endpoint, invert the routing:

1. Start from the `Birth`. Lift `child`, `informant`, `event_location`,
   `birth_type`, `weight_at_birth`, and `attendant_at_birth` to the
   top-level `BirthRegistration` fields.
2. Split `parents[]` by `parental_role`. Put the entry with
   `biological_mother` into `mother`; put `biological_father` into
   `father`. Drop any entry whose role cannot be mapped (adoptive, legal,
   surrogate); OpenCRVS v1 has no slot for it.
3. Write the child's `event_date` onto `child.birthDate`.
4. Build the embedded `registration` sub-object from the
   `CivilStatusRecord`: `record_id` → `registrationNumber`; `record_type`
   → `RegistrationType` (upper-cased); current `registration_status` →
   append a new entry to `status[]` with the mapped `RegStatus`.
5. For each `Certificate`, append an entry to `registration.certificates[]`
   using the locally resolved template id.

## An edge case: late registration

Consider a birth registered ten years after the event. In PublicSchema:

- The `Birth` carries `event_date: "2016-05-03"`, when the child was born.
- The `CivilStatusRecord` carries a current registration date in its
  workflow history and a `registration_type` of `late` (from our
  `registration-type` vocabulary).
- The `Certificate` is issued today, ten years after the birth.

In OpenCRVS v1, these three timelines collapse onto one payload. There is
no `registration_type` field for `late` vs `current`; `createdAt` gives
you when the record was created (i.e. when registration happened) and
`child.birthDate` gives you when the birth happened. The difference is
implicit.

This is exactly why PublicSchema separates the three concepts: a late
registration, a correction that edits the acte, and a reissued extract are
three distinct operations on different objects. Flattening them into one
bundled record makes the timeline harder to audit.

## What the mapping does not do

- It does not model **adoption, legitimation, paternity recognition, or
  fetal death registrations** as first-class events. OpenCRVS v1 does not
  have distinct registration types for these. In practice OpenCRVS handles
  paternity recognition and legitimation through the correction workflow
  (`RegAction: CORRECTED`); that operational fact is recorded in
  `matching.yaml` as a `related` link from `PaternityRecognition` to
  `RegAction`.
- It does not define a bundled convenience concept on the PublicSchema
  side. Implementations that want a single payload must compose one at the
  edge (see the previous section).
- It does not cover the OpenCRVS v2 event service or the Farajaland
  country-config. Those are separate mapping surfaces.

## See also

- [`external/opencrvs/matching.yaml`](../external/opencrvs/matching.yaml):
  authoritative field routing and vocabulary mappings.
- [`docs/vocabulary-extraction-process.md`](vocabulary-extraction-process.md):
  the four-phase process this mapping follows.
- [`docs/mapping-example.md`](mapping-example.md): simpler worked example
  for a single-vocabulary mapping.
