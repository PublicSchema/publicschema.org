# ADR-020: Separate registry records, recognition, subjects and values

Status: accepted for the local draft.

The government and agriculture starters combine useful semantic distinctions with their own submission rules. PublicSchema's reference vocabulary must keep subjects distinct from register entries, legal recognition, evidence and operational constraints. Existing Person, Organization, Address and Group contracts cannot be widened merely to fit a starter payload.

The new root URIs `Register`, `RegistryEntry`, `RecordReference`, `Registration` and `Authorization` describe these separate things. A qualified key is a register URI plus a local string. Resolving it to a subject is an explicit checked operation with unresolved results. General subjects use URI ranges; narrower actor/object relationships retain typed class references. URI-valued JSON-LD relationships must have matching RDF and SHACL node semantics. Schema maturity is independent of instance lifecycle.

New CodedValue, QuantityValue and SpatialGeometry values preserve scheme, unit and encoding context. Native closed codes are reused only when semantics fit. Open codes are not mapped by label; an unavailable mapping leaves original code/scheme intact. Existing Identifier remains an identifier rather than becoming a generic classification value. No third-party standard vocabulary is copied wholesale.

New modules use root URIs like existing Farm, HealthFacility and Organization. These concepts are not alternate jurisdiction-specific versions of those terms, so a module filename does not create a domain namespace. New fields use global LinkML slots and the maintained composite/compiler. Example submission rules are small executable demonstrations beside examples, not a second profile compiler or product runtime.

The strongest alternative was copying registered-record base classes and all starter-required fields. It would produce quick apparent coverage but would imply that unregistered holdings or partial vocabulary descriptions cannot exist. A second alternative, only external alignments, would leave real shared semantic gaps. The adopted design delivers researched reference distinctions and keeps application-requiredness, live lookup, lifecycle enforcement and legal decisions with their profiles.

`Authorization` specializes `Registration` because this draft defines registration as
administrative recognition, not merely insertion into a database. A permission is the
more specific recognition of a subject for a permitted activity. The credible alternative
is an abstract `AdministrativeAct` with sibling `Registration` and `Authorization`
concepts. That would accommodate procedural acts beyond recognition, but it adds a
foundation whose wider meaning is not needed by the present examples. Retain the current
hierarchy while registration keeps this recognition meaning. Reconsider it if a concrete
authorization falls outside recognition, or a reusable administrative-act family is
established. DCAT does not prescribe this hierarchy. No URI or payload changes follow
from recording this alternative.

An issued licence number identifies the permission or document according to its issuing
scheme. It can be represented with `IdentifierAssignment` pointing to that subject.
`RegistryEntry.record_id` instead identifies the entry within its register; use a licence
number there only when the register actually uses it as the entry key. The two values
need not match, and neither should replace the identity of the licensed person or organization.

The [public evidence brief](../docs/registry-foundations-draft.md) distinguishes source-backed meanings from PublicSchema layout choices. [ADR-021](021-farm-production-unit.md) owns the intentional draft Farm hierarchy correction. No stronger-maturity field or code is repurposed. Revisit these decisions when concrete adopter payloads demonstrate a missing identity boundary, a wrongly reused meaning or necessary constraints that fail to survive the actual exports. Such evidence should include the conflicting example and its governing source, rather than only a preferred starter serialization.
