# ADR-022: Separate public services, applications and administrative history

**Status:** Accepted

## Context

A business permit cannot be represented faithfully by widening a social protection enrollment or by treating an organization as a `Party`. A service catalogue entry, a submitted request, a determination, a permission and a request for review have different identities and lifetimes. Keeping only a current status would erase the authority and legal context of earlier acts when institutions change. Inspections, enforcement measures and capacity observations have the same shape: something happened at a time, about a subject, under an authority.

[CPSV-AP 3.2.0](https://semiceu.github.io/CPSV-AP/releases/3.2.0/) separates a catalogue service from its individual uses and names competent authorities, legal resources and audiences, but leaves applications, decisions and appeals outside its scope. [W3C ORG](https://www.w3.org/TR/2014/REC-vocab-org-20140116/#org:ChangeEvent) provides a before-and-after pattern for organizational change.

## Decision

1. **Root concepts for the catalogue and for what happens.** `PublicService` describes a service (`service_competent_authorities`, `service_audience`, `legal_resources`). `ServiceApplication`, `AdministrativeDecision`, `AdministrativeAppeal` and `OrganizationalChangeEvent` are occurrences. The scope of `Party`, `Program`, `Enrollment`, `EligibilityDecision` and `Grievance` is unchanged.
2. **Occurrences specialize `Event`.** The four occurrence concepts above, and `ComplianceAssessment`, `RegulatoryAction` and `ServiceCapacityObservation`, are Events. [ADR-020](020-registry-foundations.md) records `RecordLifecycleEvent`, which is also an Event. A service description, a Certification and an Authorization are standing records, not Events.
3. **Shared slots across these records:**
   - `subject_uri` names what the record is about (the subject of an application, decision, assessment, action or capacity observation), as in ADR-020.
   - `authority` (Organization) names the organization responsible for the act: the body that receives an application, decides, reviews an appeal, inspects or takes a measure. [ADR-025](025-organizations-legal-personality-and-authority.md) records this slot and its separation from `assertion_authority`.
   - `legal_resources` (URIs) names the legal provisions or policy resources a service, decision, regulatory action or organizational change relies on. A link does not execute a rule or establish which version applies.
4. **Applicants and representatives.** `service_applicant` and `appellant` are URIs admitting a person, group or organization. `submitted_by` (Agent) is whoever submitted the request, and `submission_representation` links the RepresentationRole under which they acted.
5. **Distinct times.** `request_submission_date` and `decision_date` are dates. The request date is its own property because the published grievance `submission_date` also admits the date of registration, and a representative's authority is checked against the actual submission. `effective_at` is when a decision or change takes effect, and `recorded_at` is when it was entered into the source record. None of them is inferred from another.
6. **Results are linked, not duplicated.** A decision links to the application it decides, the Registrations it establishes, such as Authorizations (`decision_registrations`), the RegulatoryActions it takes (`decision_regulatory_actions`) and the appeal it resolves. An appeal names the decision it challenges. No link by itself creates a stay, a cancellation, legal finality or a new permission.
7. **Outcomes are codes from the source scheme.** `decision_outcome`, `assessment_result` and `action_type` are CodedValues, not a universal administrative state machine.
8. **Organizational change is its own event.** An OrganizationalChangeEvent links several original and resulting organizations and keeps their identities and the issuer links of earlier records. It is not a RecordLifecycleEvent, because a merger or split need not concern one register record. A change of name with the same identity is a NameUsage record.

The native application, decision and appeal classes are PublicSchema design choices, not classes attributed to CPSV-AP. Catalogue exchange with CPSV-AP remains an explicit adapter task.

## Alternatives considered

- **Reuse CPSV-AP for the catalogue and keep transactions and legal history outside PublicSchema.** Suitable for a portal whose only job is catalogue exchange, but it leaves the applicant, decision, output and appeal links absent from registry interoperability.
- **Copy the whole CPSV-AP profile.** Rejected. It adds channel, cost, requirement and catalogue constraints that registry records do not need, and still does not define a legal procedure.
- **An abstract `AdministrativeAct` covering registration, authorization, applications, determinations and regulatory actions.** Rejected. A request is not an act of the authority, and a permission is distinct from the decision that establishes it. The `Authorization` hierarchy remains as ADR-020 records. Reconsider when a concrete shared invariant cannot be expressed by these links.
- **Standalone assessment, action and observation classes outside the Event hierarchy.** Rejected. They record occurrences with a time, a subject and an authority, which is what Event describes, and consumers that already process Events can include them.
- **Datetimes for submission and decision.** Rejected. Administrative sources record these as dates, and the existing slots are dates; `recorded_at` carries the time of entry.

## Consequences

A permit journey maps to several linked records: the service, each application, each decision, the resulting Authorization, any RegulatoryAction, any appeal and its review decision. The [public services guide](../docs/public-services.md) walks through a synthetic journey and states which CPSV-AP and ORG alignments are close and where they stop.

The example profile checks missing and misleading references, representation scope, the subject of each output, and preservation of the historical issuer. It binds representation scope through separate fixture grants, never by parsing free text. These are demonstration constraints, not a government workflow engine or national legal rules.
