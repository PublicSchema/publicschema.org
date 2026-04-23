# OpenCRVS external mapping

Vocabulary and concept mapping between PublicSchema v2 and [OpenCRVS](https://github.com/opencrvs/opencrvs-core) v2 event service.

## What's here

- `matching.yaml`: the curated mapping, with `concept_matches:`, `matches:` (vocabularies), and `no_match:`.
- `repo/`: shallow clone of `opencrvs-core` (gitignored at repo root). The v2 event-service types are in `packages/commons/src/events/`.
- `repo-farajaland/`: shallow clone of the Farajaland reference country config (gitignored). Farajaland is the canonical example of a v2 country configuration, used to illustrate how birth and death events are defined.

PublicSchema-side value mappings (canonical codes to external codes) live on vocabulary YAMLs under `schema/vocabularies/*.yaml system_mappings.opencrvs`. The `matching.yaml` here is the editorial prose companion: prose notes, gaps, confidence levels, and citations back to v2 core types or Farajaland.

## Mapping target: v2 event service

`matching.yaml` targets the **v2 event service** exclusively. The v1 GraphQL mapping has been dropped (v1 is superseded; consult git history for the v1 mapping).

Rationale: OpenCRVS v2 is a near-total rewrite. The v1 `packages/gateway` GraphQL server proxied a FHIR-MongoDB backend and exposed typed domain fields (`BirthRegistration.child`, `DeathRegistration.deceased`, etc.). V2 replaces this with a generic event log built on PostgreSQL + Elasticsearch, with tRPC/OpenAPI at the API layer. V1 type definitions have been removed from the codebase; the `packages/client/src/tests/schema.graphql` anchor no longer exists.

## Architecture: v2 is envelope-only

The v2 event service defines:

- **`EventDocument`** (`packages/commons/src/events/EventDocument.ts`): the generic event envelope. Every registered event is an `EventDocument` with an `id`, `type` (a free string), `trackingId`, `createdAt`, `updatedAt`, and an ordered `actions` array.
- **`ActionDocument`** (`packages/commons/src/events/ActionDocument.ts`): a discriminated union of 18 action variants (CREATE, NOTIFY, DECLARE, REGISTER, REJECT, PRINT_CERTIFICATE, REQUEST_CORRECTION, APPROVE_CORRECTION, REJECT_CORRECTION, ARCHIVE, EDIT, ASSIGN, UNASSIGN, READ, DUPLICATE_DETECTED, MARK_AS_DUPLICATE, MARK_AS_NOT_DUPLICATE, CUSTOM). Each action carries a `declaration` field (a `Record<string, FieldValue>` keyed by country-specific strings) and an optional `annotation` field.
- **`EventStatus`** (`packages/commons/src/events/EventMetadata.ts`): a 5-value enum (CREATED, NOTIFIED, DECLARED, REGISTERED, ARCHIVED) derived from the action log.
- **`EventConfig`** (`packages/commons/src/events/EventConfig.ts`): the country-configurable event definition. Each country defines one `EventConfig` per event type (birth, death, marriage, etc.), specifying the `id` (the free-string type discriminator), `declaration` form fields, `actions`, and display configuration.

There are **no typed domain fields** at the v2 core level. Child name, cause of death, marriage parties, and similar data live in `EventConfig.declaration` as a `Record<string, FieldValue>` with country-specific key strings. This is why most field-level and event-type-specific mappings carry `country_config: true` in `matching.yaml`.

## Per-entry fields

| Field | Meaning |
|---|---|
| `surface` | `event_v2` (v2 core event service) or `country_config` (lives in per-country EventConfig) |
| `external_source` | Path relative to `source_repository` (event_v2 entries) or `country_config_reference.repository` (country_config entries) |
| `country_config: true` | The mapping depends on per-country EventConfig; not dictated by v2 core |
| `confidence` | `high`, `medium`, `low`, or `null` (country-configurable; cannot assess without a specific deployment) |

## Envelope-level mappings (surface: event_v2)

These concepts have clean mappings to v2 core types:

| PublicSchema concept/vocab | V2 type | Key file |
|---|---|---|
| `VitalEvent` | `EventDocument` | `packages/commons/src/events/EventDocument.ts` |
| `CivilStatusRecord` | `RegisterAction` (carries `registrationNumber`) | `packages/commons/src/events/ActionDocument.ts` |
| `Certificate` | `PrintCertificateAction` (carries `content.templateId`) | `packages/commons/src/events/ActionDocument.ts` |
| `crvs/registration-status` | `EventStatus` (5 values) | `packages/commons/src/events/EventMetadata.ts` |

`EventStatus` maps to `crvs/registration-status` more cleanly than v1 `RegStatus` did: the v2 model collapses 10 workflow states into 5 semantic statuses by separating status from audit granularity (which lives in `ActionType`).

## Country-configured mappings (surface: country_config)

These concepts have no fixed canonical type in v2 core; the Farajaland country config is cited as an example:

| PublicSchema concept/vocab | V2 pattern |
|---|---|
| `Birth`, `Death`, `Marriage` | `EventDocument.type = "BIRTH"/"DEATH"/"MARRIAGE"` (country-configured string) |
| `Person`, `Parent` | Declaration form fields in EventConfig; no dedicated type |
| `Location`, `GeographicArea` | Location service (separate from events); UUID reference in EventDocument |
| `crvs/birth-type`, `crvs/birth-attendant`, etc. | SELECT fields in EventConfig.declaration; country-defined options |
| `crvs/civil-status-record-type` | `EventDocument.type` (free string) |

The following CRVS concepts have no OpenCRVS v2 or Farajaland equivalent and are in `no_match`: `FetalDeath`, `MarriageTermination`, `Adoption`, `Legitimation`, `CivilStatusAnnotation`, `FamilyRegister`.

## Refreshing the clones

From the v2 root:

```bash
git clone --depth 1 --branch develop https://github.com/opencrvs/opencrvs-core external/opencrvs/repo
git clone --depth 1 --branch develop https://github.com/opencrvs/opencrvs-farajaland external/opencrvs/repo-farajaland
```

## Cross-references with the schema

Concept and vocabulary YAMLs in `schema/` that have `external_equivalents.opencrvs` entries carry URIs pointing at the v2 core files (`packages/commons/src/events/*.ts#Symbol`) or at Farajaland files (`src/events/birth/index.ts#birthEvent`). These URIs are emitted as RDF match triples in `dist/` by the build pipeline.

The `system_mappings.opencrvs` blocks on vocabulary YAMLs drive the value-level code mappings and are separate from `matching.yaml`.
