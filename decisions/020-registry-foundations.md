# ADR-020: Separate registry records, recognition, subjects and values

**Status:** Accepted

## Context

Government and agricultural registries hold records about persons, organizations, holdings, facilities, land and products. A register, a record in it, the thing the record describes, the legal recognition the record evidences, and the evidence behind it all have different identities and lifetimes. Registry payloads often flatten them into one object with an ID, a status and a subject. Doing the same in the vocabulary would force existing Person, Organization, Address and Group contracts to widen until they could carry register keys, permission conditions and submission rules.

Registry records also carry coded values, quantities and geometries whose meaning depends on a scheme, a unit or an encoding. A bare string or number loses that context, and mapping an open code by its label invents an equivalence that no source asserted.

## Decision

### Records, recognition and subjects

Root concepts keep the separate identities apart:

- `Register` is the register itself. `register_owner` names the organization that establishes it and answers for it.
- `RegistryEntry` is one record in a register. Its qualified key is a register URI (`register_uri`) plus the register's local string (`record_id`). `RecordReference` points at such a record from another statement.
- `Registration` is administrative recognition of a subject (`registered_subject`) by an organization (`registration_authority`). `Authorization` specializes it as recognition of a subject for a permitted activity.
- `IdentifierAssignment` records who issued an identifier (`identifier_issuer`) to which subject, for what period. The existing `Identifier` remains the value and scheme; it does not become a generic classification value.
- `EvidenceAssertion` and `SubjectMatchAssertion` are attributed statements about sources and about whether a record describes a subject.
- `NameUsage` and `ContactPoint` record names and contact channels with purpose and dates, without modifying the personal name or household address contracts.

Resolving a qualified key to a subject is an explicit, checked operation that can end unresolved. Two registers with the same local ID never identify one record. Schema maturity is independent of the lifecycle of any instance.

Statements that are about a thing use one slot, `subject_uri`. The class of the statement says what kind of statement it is; the slot does not repeat it. `IdentifierAssignment`, `NameUsage`, `ContactPoint`, `AssetPartyRole`, `AssetAddressAssignment`, `RegistryEntry` and `RecordReference` use it, as do the public administration records in [ADR-022](022-public-services-and-administrative-history.md). A slot keeps its own name only when it means something narrower: `registered_subject` is the recipient of recognition and `matched_subject` is the subject a record is proposed to describe.

Organizations appear in these records in distinct roles, each with its own slot: `register_owner` on Register, `registration_authority` on Registration, `identifier_issuer` on IdentifierAssignment and `assertion_authority` on EvidenceAssertion and SubjectMatchAssertion. `assertion_authority` is the organization accountable for a statement, which can differ from the person or software that entered it. The organization responsible for an event is `authority`, recorded in [ADR-025](025-organizations-legal-personality-and-authority.md).

A change in the standing of a record is a `RecordLifecycleEvent`, which specializes `Event`. `affected_record` names the record as a RecordReference and `record_change_kind` says what happened to it. Changes to the subject itself, such as a death or a dissolution, are domain events, and an organizational merger or split is an `OrganizationalChangeEvent`. `effective_at` and `recorded_at` are separate because a change can take effect before or after it is recorded.

`Authorization` specializes `Registration` because registration here means administrative recognition, not insertion into a database, and a permission is a more specific recognition. An issued license number identifies the permission or document within its issuing scheme and is represented with `IdentifierAssignment`. `RegistryEntry.record_id` identifies the entry within its register; it holds a license number only when the register uses that number as its entry key. Neither value replaces the identity of the licensed person or organization.

### Actor and subject ranges

A relationship is typed with a class when one class fits: `Agent` for persons, organizations and software, or `Organization`. When groups must be admitted alongside persons and organizations, the slot is a URI and its definition names the admitted kinds. `asset_actor`, for example, admits a person, an organization or a group. General subjects that can be of any kind use URI ranges. URI-valued JSON-LD relationships have matching RDF and SHACL node semantics.

### Values

`CodedValue`, `QuantityValue` and `SpatialGeometry` keep the scheme, unit or encoding with the value:

- A CodedValue keeps the original code and scheme and adds a meaning URI only when known. An open code is never mapped by its label; when no mapping exists, the original code and scheme stay intact. No third-party vocabulary is copied wholesale.
- A QuantityValue keeps the amount, the unit code and the unit system without implicit conversion or rounding. A limit that applies per period uses a rate unit that carries the period, such as cubic metres per day; several simultaneous limits are several values.
- A SpatialGeometry keeps the encoding, the literal and the coordinate reference system. `spatial_geometry` gives a feature one or more of them. The existing `Location.geometry` holds a GeoJSON geometry object for a named place. A SpatialGeometry encoded as GeoJSON with no stated reference system carries the same shape as a `Location.geometry` value, so moving between them is a parse or serialization step. Other encodings or reference systems have no lossless `Location.geometry` form.

Where a standard fixes a short list, the slot uses a closed enumeration: `EvidenceRole`, `ContactChannel`, `GeometryEncoding`, `UnitSystem`, `MatchOutcome` and `RecordChangeKind`. Lists that are local policy, such as asset roles, address purposes, name uses and building uses, stay CodedValue so that the source scheme and its unknown or retired codes survive.

### Placement and examples

New modules use root URIs like existing Farm, HealthFacility and Organization. These concepts are not alternate jurisdiction-specific versions of those terms, so a module filename does not create a domain namespace.

> **Amended by [ADR-024](024-domain-and-external-model-boundaries.md).** Namespaces are chosen by the meaning of a term. Farm is `agri/Farm` and HealthFacility is `health/HealthFacility`; sector terms introduced alongside these foundations use their domain namespaces, and the generic registry, value and relationship concepts above stay at root. The rule that a module filename does not create a namespace stands.

New fields use global LinkML slots and the maintained build. Example submission rules are small executable demonstrations beside the examples, not a second profile compiler or a product runtime. All reference fields are optional; application requiredness, live lookup, lifecycle enforcement and legal decisions belong to the profiles that need them.

## Alternatives considered

- **Copy registered-record base classes and all fields a registry requires.** Rejected. It gives quick apparent coverage but implies that an unregistered holding, or a partial description of a subject, cannot exist.
- **Publish only external alignments.** Rejected. Real shared semantic gaps, such as a record distinct from its subject or recognition distinct from both, would stay unrepresented.
- **An abstract `AdministrativeAct` with sibling `Registration` and `Authorization`.** This would accommodate procedural acts beyond recognition, but it adds a foundation whose wider meaning the vocabulary does not need while registration keeps its recognition meaning. Reconsider if a concrete authorization falls outside recognition or a reusable administrative-act family is established. DCAT does not prescribe either hierarchy.
- **A separate subject slot per statement class** (for example one for identifier assignments and one for contact points). Rejected. The slots would all mean "the thing this statement is about" and differ only by the class that carries them.
- **Union ranges such as Person or Organization or Group.** Deferred. The custom JSON Schema build does not carry `any_of`, so a union would validate in SHACL and not in JSON Schema. A URI range with the admitted kinds in its definition keeps both exports consistent.
- **CodedValue everywhere.** Rejected for lists a standard fixes. A closed enumeration gives validators and translators a fixed set; keeping CodedValue there would invite local synonyms for standard values.

## Consequences

Registry payloads map to several records instead of one. A national business register row, for example, becomes a RegistryEntry, the Organization it describes, a Registration, and possibly an IdentifierAssignment for the registration number. Adopters gain the ability to keep these apart when their lifetimes diverge, at the cost of more links.

`subject_uri` alone does not reveal what a record is about. `register_uri` and `registered_subject` are sensitive, because appearing in a particular register can reveal a person's circumstances.

JSON Schema accepts any string for a URI reference and so proves neither existence nor identity. Resolution and type checks for URI-ranged slots belong to profiles; SHACL checks typed relationships when the class hierarchy is supplied.

The [registry foundations guide](../docs/registry-foundations.md) lists the sources behind each distinction and the worked examples. [ADR-021](021-farm-production-unit.md) records the Farm hierarchy correction.
