# ADR-005: Separate event record IDs from party identifiers

**Status:** Accepted

## Context

Two different concepts were conflated under a single property.

The `identifiers` property was attached to both `Party` (supertype of Person and Group) and `Event` (supertype of PaymentEvent, VitalEvent, AssessmentEvent, etc.). In both cases it referenced the `Identifier` concept, which models an externally-meaningful business identifier (value, scheme id, scheme name, type).

That shape fits Party. A person carries multiple such identifiers (national ID number, passport number, program beneficiary number, household registration number, farmer code), each issued under a different scheme. A Person record may legitimately carry a list of `Identifier` objects.

That shape does not fit Event. An event is a record that happened in a delivery system, and what systems actually track is a single system-assigned reference: a transaction ID, a case number, a registration number. There is no external scheme (the originating system is the authority), and treating it as a scheme-qualified identifier misstates what the value is.

The mismatch was visible in practice:

- Event subtypes that already modeled their own business reference used a single string, not an `Identifier` structure: `PaymentEvent.transaction_reference`, `VitalEvent.registration_number`. (Non-Event record concepts show the same shape, e.g., `Certificate.certificate_number`, `Voucher.serial_number`, but they are out of scope for this ADR.)
- PaymentEvent and VitalEvent inherited `identifiers` from Event AND defined their own string-typed reference, giving two parallel ID mechanisms on the same concept.
- The `Identifier` concept's own scope is the externally-meaningful numbers a party carries, which does not match what an event record needs.

External standards handle this split explicitly. FHIR gives every resource a `Resource.id` (a single system-assigned string, the logical id) and a separate `Resource.identifier[]` (business identifiers with type, system, value, period). Two properties, two concepts, one clear distinction: system-assigned row ID vs. externally-meaningful business identifier.

ADR-002 (Decision 17 in the candidate audit) kept Event thin with only `identifiers`, on the rationale that Event is an abstract marker whose subtypes define their own specifics. That reasoning stands; this ADR refines what the thin marker should carry.

## Decision

1. **Remove `identifiers` from `Event`.** Event no longer carries the `Identifier` concept.
2. **Add `record_id: string` to `Event`.** A single-string property representing the system-assigned identifier for this event record in the originating system. Inherited by all Event subtypes.
3. **Keep `identifiers` on `Party`.** The `Identifier` concept remains the right shape for the business numbers a Person or Group carries.
4. **Keep subtype-specific business references as-is.** `PaymentEvent.transaction_reference` and `VitalEvent.registration_number` continue to represent externally-meaningful domain references, distinct from `record_id`. A PaymentEvent can legitimately carry both: `record_id` for the internal row, `transaction_reference` for the payment-rail reference. The same two-tier split (internal system id vs. external business reference) applies to non-Event record concepts like `Certificate`, `Voucher`, and `FamilyRegister` that already carry their own business-reference field; extending `record_id` to those concepts is a separate decision (see "Scope" below).

## Alternatives considered

- **Generalize the wording of `identifiers` to cover Event.** Rejected. The underlying data shapes genuinely differ: Party identifiers are multi-valued, scheme-qualified business numbers; event identifiers are single system-assigned strings. Broadening the text would hide the mismatch rather than fix it.
- **Remove `identifiers` from Event and add nothing.** Rejected. Six of eight Event subtypes (AssessmentEvent, EligibilityDecision, HazardEvent, InKindDelivery, Referral, VoucherRedemption) currently have no ID property at all other than the inherited one. Leaving them with no way to reference a record would be a regression.
- **Keep `identifiers` on Event, add `record_id` as well.** Rejected. Introduces two parallel ID mechanisms at the supertype level. Adopters would have to guess which to use.
- **Move `identifiers` down to Party only but introduce a richer `EventIdentifier` concept.** Rejected. A separate concept for a single string is over-engineering. If business references on specific event subtypes need richer metadata later, that can be modeled per subtype.

## Scope

This ADR decides only the Event side of the split. Non-Event record concepts (`Party`, `Enrollment`, `Entitlement`, `Grievance`, `Program`, `Voucher`, `Certificate`, `FamilyRegister`, `CivilStatusRecord`, `AssessmentFramework`, `BenefitSchedule`, `Relationship`, `GroupMembership`, `DeliveryItem`, `Parent`, `CivilStatusAnnotation`) are also stored records and likely benefit from a `record_id` slot, but the argument for each varies (Party already carries `identifiers`; some value-object-shaped concepts may not need a row id at all). A follow-up ADR should decide whether to propagate `record_id` across those concepts or to define a narrower set of "record-bearing" classes. Until then, the `record_id` property is defined generically (the definition does not hard-code "event") so that follow-up work can attach it to other concepts without a property rename.

## Consequences

The semantic tension between Party-scoped business identifiers and event row IDs disappears. `Identifier` stays clearly scoped to Party. `Event.record_id` is small, obvious, and matches how every mapped system tracks the event records it originates.

Subtype-specific business references remain, because they carry semantics that `record_id` does not (a `transaction_reference` is meaningful to the payment rail; `record_id` is only meaningful inside the originating system).
