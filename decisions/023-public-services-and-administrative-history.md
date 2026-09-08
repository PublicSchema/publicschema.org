# ADR-023: Separate public services, applications and administrative history

Status: accepted for the local draft.

A business permit cannot be represented faithfully by widening a social protection
enrollment or treating an organization as an existing `Party`. A service catalogue,
a submitted request, a determination, a permission and a request for review also
have different identities and lifetimes. Keeping only a current status would erase
the authority and legal context of earlier acts when institutions change.

Add five draft concepts with shared root URIs: `PublicService`, `ServiceApplication`,
`AdministrativeDecision`, `AdministrativeAppeal` and `OrganizationalChangeEvent`.
The four occurrence concepts specialize the existing `Event`; the service description
does not. Add reusable fields without changing the scope of `Party`, `Program`,
`Enrollment`, `EligibilityDecision` or `Grievance`, or promoting any new term to
candidate or normative maturity. Applications identify person or organization
applicants by URI. A consuming profile resolves those references and excludes actor
kinds that it does not support.

Reuse `PublicOrganization` for public functions, `RepresentationRole` for cited
representation, `Authorization` for a granted permission, `RegulatoryAction` for a
resulting suspension or other action, and `EvidenceAssertion` for attributed source
material. A decision links to these results instead of duplicating their meaning.
An appeal challenges a decision; a later decision can resolve the appeal. No link
alone creates a stay, cancellation, legal finality or a new permission.

Use scheme-qualified outcome codes rather than a universal administrative state
machine. Keep submission, determination, effective and recording times distinct.
An organizational change links multiple original and resulting organizations while
preserving previous identities and issuer links. It is an `Event`, not a subtype of
`RecordLifecycleEvent`, because a merger or split need not concern one registry subject
or supersede one record. Identity-preserving name corrections can still use
`RecordLifecycleEvent`.

The [source and field guide](../docs/public-services-draft.md) pins CPSV-AP 3.1.1 and
W3C ORG's 2014 Recommendation. It identifies conceptual alignments and their limits.
The native application, decision and appeal classes are PublicSchema design choices,
not classes attributed to CPSV-AP. Upstream catalogue exchange remains an explicit
adapter and conformance task.

The strongest alternative is to reuse CPSV-AP directly for the catalogue and keep all
transaction and legal history outside PublicSchema. That is appropriate for a portal
whose only job is catalogue exchange, but leaves the reusable applicant, decision,
output and appeal identity links absent from registry interoperability. Copying the
whole upstream profile would add channel, cost, requirement and catalogue constraints
that this journey does not need and still would not define its legal procedure.

Another alternative is an abstract `AdministrativeAct` family covering registration,
authorization, applications, determinations and regulatory actions. A request is not
an authority's act, and a permission is distinct from the decision that establishes
it. The existing `Authorization` hierarchy remains as decided in ADR-020; connected
events solve the demonstrated gap without replacing that foundation. Reconsider the
hierarchy when a concrete shared invariant cannot be expressed by these links.

A small synthetic profile verifies a person application, a represented business
application, a grant, institutional succession, permit-specific suspension, appeal
and review. It binds representation scope through separate reviewed fixture grants,
never by parsing free text. Tests exercise missing and misleading references,
representation mismatch and scope, output-subject mismatch, historical issuer
preservation and the actual public exports. These are demonstration constraints,
not a government workflow engine or national legal rules.

Revisit the draft when adopter evidence shows a missing distinction, a required
CPSV-AP exchange profile or a specific multi-stage legal procedure that cannot retain
its identities and evidence. Such evidence should include the applicable source and
a conflicting example rather than an unscoped list of possible case-management fields.
