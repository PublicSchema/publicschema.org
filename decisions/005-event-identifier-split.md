# ADR-005: Use `identifiers` uniformly for record and business references

**Status:** Accepted

## Context

Record-bearing concepts across the schema face the same need: a way to reference the record in the originating system, plus any externally meaningful business reference the record carries. Every new record concept raises two closely related questions:

- Does it need a system-assigned row id?
- Does it need a business reference (transaction id, registration number, certificate number, etc.)?

One plausible answer is per-concept slots: a `record_id: string` for the originating-system row and a domain-specific slot for the business reference (a `transaction_reference` on payment events, a `registration_number` on vital events, and so on). Each concept that needed a reference would declare one.

The other plausible answer is a uniform multi-valued property. `Party` already works this way: it carries `identifiers: Identifier[]`, where each `Identifier` is scheme-qualified and type-tagged via the `identifier-type` vocabulary. Once `Identifier` was reduced to its coded-value shape (`identifier_value`, `identifier_type`, `identifier_scheme_id`, `identifier_scheme_name`) and `IdentityDocument` took on the document-lifecycle fields, `Identifier` became generic enough to describe any externally-qualified coded reference. `Location.identifiers` already uses it for P-codes, ISO 3166 country codes, and UN/LOCODEs.

Per-concept slots have two costs. First, `record_id` would need to be replicated across every record-bearing concept (`CivilStatusRecord`, `Certificate`, `Voucher`, `Enrollment`, `Entitlement`, ...), repeating the same "originating system reference" idea under a fixed name. Second, single-string business-reference slots cannot hold more than one value: a payment event replicated across two rails has two references, a civil-status record that exists in two registries has two registration numbers. The fixed slot forces a choice.

`identifiers: Identifier[]` avoids both. It is multi-valued, scheme-qualified, and already the mechanism Party and Location use.

## Decision

1. **`identifiers: Identifier[]` is the single mechanism for record and business references on record-bearing concepts.** Party, Location, Event, and CivilStatusRecord carry it directly; other record-bearing concepts can adopt it on their own schedule.
2. **`Event` carries `identifiers`** (inherited by all Event subtypes). No separate row-id slot on Event.
3. **`CivilStatusRecord` carries `identifiers`.** No separate row-id slot.
4. **Event subtypes do not define their own business-reference strings.** Payment-rail references, civil registration numbers, and similar values are `Identifier` entries with an appropriate `identifier_type`.
5. **The `identifier-type` vocabulary covers the type codes needed for record and business references**, including `transaction_reference` for payment-rail identifiers and `birth_registration_number` / `marriage_registration_number` / `death_registration_number` for civil registration.
6. **Party behaviour is unchanged.** `Party.identifiers` already followed this pattern.

## Alternatives considered

- **Give Event a `record_id: string` and propagate it to every other record-bearing concept.** Rejected. Adds a second, redundant identifier mechanism to every such concept. Forces a choice at modeling time between "use `record_id`" and "use `identifiers`" when both are really the same operation.
- **Keep per-subtype business-reference strings (e.g., a `transaction_reference` on PaymentEvent, a `registration_number` on VitalEvent) alongside `identifiers`.** Rejected. They cannot hold multi-valued references, and the readability gain from a named slot is not worth the duplication. A typed entry in `identifiers` is self-describing (`identifier_type: transaction_reference`) and extensible.
- **Introduce a distinct concept for row ids (e.g., `RecordId`) separate from `Identifier`.** Rejected. `Identifier` already carries the scheme and type fields needed to distinguish "originating system row" from "payment-rail reference" from "civil registration number". A second concept for a single scalar is over-engineering.

## Consequences

Every record-bearing concept references the same mechanism. New concepts do not need to invent a naming convention for their row id or their business reference; they add `identifiers` and rely on the `identifier-type` vocabulary to disambiguate entries.

The `Identifier` concept's scope is uniform across the schema: it is the scheme-qualified, type-tagged, multi-valued way to carry any coded reference, whether on a Party, a Location, an Event, or a record. `IdentityDocument` remains the place for document-lifecycle metadata (issuing authority, issue date, expiry date); documents hold their own `identifiers` list for the numbers printed on them.

Consumers reading a payment-rail reference or civil-registration number dereference an `identifiers` entry by type (`identifiers[?identifier_type == 'transaction_reference'].identifier_value`) rather than a named slot. The extra indirection is the cost of the uniform mechanism.
