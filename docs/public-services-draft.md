# Public services and administrative history

This draft describes a public service, an application to use it, an authority's
decision, an appeal and a material organizational change as separate things.
The native terms use shared root URIs, including
`https://publicschema.org/PublicService`. They can be used across public-service
sectors. They do not change `Party`, social protection `Program`, `Enrollment`,
`EligibilityDecision` or `Grievance` into general business-service contracts.

The [synthetic permit journey](../examples/public-services/records.json) includes
an individual applying directly and a business applying through a representative.
The business receives a permit. A successor authority later suspends that specific
permit, the business appeals, and a separate review decision upholds the suspension.
Every person, organization, service, submission, decision, permission and action has
its own identity. All names, laws, source documents and code schemes are synthetic.

## Research and reuse

[CPSV-AP 3.1.1](https://semiceu.github.io/CPSV-AP/releases/3.1.1/) distinguishes a
catalogue service from its individual uses and recognizes individual, business and
public-authority audiences. Its service properties describe responsible authorities,
legal resources, evidence requirements and outputs. Its Rule description leaves
detailed executable rules outside the profile. These distinctions inform the native
`PublicService`; they do not define the new application, decision or appeal classes.

[W3C ORG, Recommendation of 16 January 2014](https://www.w3.org/TR/2014/REC-vocab-org-20140116/#org:ChangeEvent)
provides a before/after organizational pattern for material changes involving distinct
identity. An original organization need not cease to exist. The native
`OrganizationalChangeEvent` uses this pattern for mergers, splits and succession.
A name correction with the same identity can use `RecordLifecycleEvent` instead.

| Native concept or field | Reuse and boundary |
|---|---|
| `PublicService` | Close alignment to `cpsv:PublicService`; a smaller native description with its own scope and optional fields. |
| `service_competent_authorities` | Close alignment to `m8g:hasCompetentAuthority`; references existing `PublicOrganization` records. |
| `service_audience`, `legal_resources` | Native scheme-qualified audience values and legal-resource URIs. No upstream code list is copied or silently normalized. |
| `ServiceApplication`, `AdministrativeDecision`, `AdministrativeAppeal` | Native administrative events. No CPSV-AP class equivalence or universal legal procedure is claimed. |
| `OrganizationalChangeEvent`, `original_organizations`, `resulting_organizations` | Close alignment to the ORG change pattern; native recording/effective timestamps do not implement a PROV activity interval or ORG inference rules. |

Generated JSON, JSON-LD and RDF retain PublicSchema terms. A CPSV-AP exchange adapter
must map terms, text, identifiers, classes and cardinalities and then validate its
own output against the pinned upstream profile. Native validation does not establish
CPSV-AP wire conformance. Applications and their private supporting evidence should
not be added to a public service catalogue merely because the catalogue description
is public.

## Fields and history

| Record | Main fields and meaning |
|---|---|
| `PublicService` | `name`, `identifiers`, `description`, `service_competent_authorities`, `service_audience`, `legal_resources` describe the offered service. Its current authority need not be the authority on an earlier decision. |
| `ServiceApplication` | `public_service`, `service_applicant`, `application_subject`, `submitted_by`, `submission_representation`, `receiving_authority`, `submitted_at`, `recorded_at`, `evidence_assertions` separate the request, subject, applicant, submitter and recipient. |
| `AdministrativeDecision` | `decision_subject`, `decision_authority`, `decision_outcome`, `decision_made_at`, `effective_at`, `recorded_at`, `legal_resources`, `evidence_assertions` record the determination. `decides_application`, `decision_authorizations`, `decision_regulatory_actions` and `resolves_appeal` connect its context and results. |
| `AdministrativeAppeal` | `challenged_decision`, `appellant`, `submitted_by`, `submission_representation`, `reviewing_authority`, `submitted_at`, `recorded_at`, `evidence_assertions` describe the filing and requested review. |
| `OrganizationalChangeEvent` | `original_organizations`, `resulting_organizations`, `lifecycle_kind`, `effective_at`, `recorded_at`, `event_authority`, `legal_resources`, `evidence_assertions` retain participants, timing and basis without replacing historical actors. |

Applicant, appellant and submitter URI fields allow a person or organization without
widening the existing recipient hierarchy. A local profile resolves the target and
checks its kind. A `RepresentationRole` reference identifies a claimed relationship;
it does not prove the actor can file this particular request. Identity, period and
the applicable scope require separate checking.

The permit remains an `Authorization` originally issued by the former office.
The suspension is a `RegulatoryAction` whose `action_subject` is the permit URI.
The decision links to that action. This represents a limit on one permission without
describing its holder as globally suspended. The appeal and review keep the original
determination accessible; filing alone does not establish a stay or reversal.

`decision_made_at`, `effective_at` and `recorded_at` answer different questions.
The example succession takes effect before it is recorded. The grant retains the
former authority's identity after the service catalogue points to the successor.
Organizational continuity does not automatically reissue permissions, transfer every
mandate, merge records or assign earlier decisions to a new body.

## Run the bounded example

From the repository root after the documented development setup:

```bash
uv run --locked python examples/public-services/profile.py
uv run --locked pytest -q tests/test_public_services.py
```

The first command runs `SyntheticPermitJourneyProfileV1` on the supplied records.
The focused tests also validate the records against the production JSON Schemas and
JSON-LD context plus SHACL exports. They do not fetch example URIs or upstream schemas.

Reference fields remain optional so partial descriptions are useful. The example
profile requires complete local service, submission, decision and succession links;
timezone-qualified timestamps; resolved actor types; consistent permit subjects and
issuers; and a distinct identity for a material successor. It rejects missing or
mis-typed targets, duplicate identities, empty or reversed representation periods, an appeal
that precedes its challenged determination and a historical authority assigned before
its synthetic creation event.

The [profile sidecar](../examples/public-services/profile.json) binds reviewed synthetic
grants to a `RepresentationRole` URI, a service URI and allowed submission classes.
It is trusted test configuration, not a caller-supplied claim. A correspondence-only
grant cannot authorize either filing. Changing `representation_scope` prose does not
change this result; an explicit matching grant is required. A grant for applications
alone does not authorize an appeal. The example's authority checks demonstrate the
binding, without proving the legal validity of a representation instrument.

Representation periods use whole UTC calendar days in this synthetic profile:
`start_date` is included and `end_date` is the first inactive day. An appeal submitted
at `2026-09-03T10:00:00Z` therefore cannot use a role ending on `2026-09-03`.
Equal start and end dates describe an empty role interval and are rejected.
The submission timestamp is converted to UTC before choosing its calendar day.
Deployments must choose the calendar and time zone appropriate to their own rules.
The permission's existing `valid_from` and `valid_to` remain inclusive, so a one-day
authorization can have equal validity dates.

The profile understands the example's grant, permit suspension and upheld-review
codes. Unknown local codes remain valid reference data but require a profile that
understands their scheme before determining an effect. The existing JSON exporter
also permits a string identifier reference for a class-valued field. The profile
resolves identified targets in either URI-string or `@id` form, including decision
outputs, evidence assertions and coded values. Inline evidence and coded values are
also accepted. A decision outcome must supply its code and scheme inline or through
a resolved `CodedValue`; a bare `"granted"` string is not treated as that local code.
Missing or wrongly typed targets produce addressed profile errors. The original permit is never
mutated, and these checks do not compute its current legal validity. Country-specific
standing, appeal deadlines, stays, notice, reasons, fees, delegation, retention,
disclosure and enforceable transition rules remain explicit deployment decisions.

The choice of native boundaries and the rejected alternatives are recorded in
[ADR-023](../decisions/023-public-services-and-administrative-history.md).
