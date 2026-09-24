# ADR-024: Domain placement, asset responsibilities and external medical models

**Status:** Accepted

## Context

PublicSchema supports domain namespaces, but a module file is only a unit of authoring and navigation. Placing a term by the module it is written in, by its primitive shape or by the application that first uses it would narrow generic identities and move catalog paths when a consumer changes. [ADR-003](003-domain-namespacing.md) introduced the namespaces; this decision states how terms are placed in them.

Physical assets such as facilities, buildings, vehicles and machines have owners, operators, keepers and addresses that change over time, while the asset keeps its identity. Several sector terms carried their own snapshot operator or address slots, which cannot record when a responsibility began or ended. Animals have the same shape of responsibility, but animal health law attaches duties to keeping and operating that do not depend on ownership.

Healthcare has mature external models. [FHIR R5](https://hl7.org/fhir/R5/) defines medicinal product definitions and healthcare directory resources in detail. A parallel native model would be a second place to maintain regulated medical meaning.

## Decision

1. **Domains are chosen by definition.** A term goes in a domain namespace when its meaning belongs to that sector: `agri/`, `land/`, `environment/`, `transport/`, `edu/`, `health/`, `tax/` and `elections/`, alongside the existing `sp/` and `crvs/`. Generic identities and cross-sector relationships stay at root, even when they are authored in a sector module and used first by sector classes. For example, `service_provider` and `component_role` are root slots on `agri/` classes because their definitions do not depend on agriculture, while `facility_function` and `supplied_product` are `agri/`. Existing candidate and normative URIs are preserved, including historical placement exceptions.
2. **Authored URIs govern catalog placement.** A property's page path follows its authored URI. Reusing a property from another domain does not change its identity or path. Domain labels come from `domains_json` in `schema/publicschema.yaml`, and the site shows only domains present in a collection, keeping unknown codes visible.
3. **Responsibilities for physical assets are dated AssetPartyRole records.** `asset_actor` is a URI admitting a person, organization or group; `asset_role_type` is a CodedValue such as ownership, operation, upkeep or registered keeping; `start_date` and `end_date` bound the period. Operators of agricultural and environmental facilities are AssetPartyRoles. Facility classes carry no snapshot operator slot. A facility therefore keeps its identity when its operator changes, which deliberately differs from reporting schemes that group installations by operator.
4. **Addresses of physical assets are AssetAddressAssignment records** with an `assigned_address`, an `address_purpose` (such as postal delivery or site access) and dates. A change of address does not create a new asset or change its owner.
5. **Animal responsibility stays separate from asset responsibility.** `AnimalResponsibility` has the same shape (subject, actor, role, dates) but its subject is an animal or animal group and `animal_responsible_actor` is a URI admitting a person, organization or group, as for `asset_actor`. Animals are not physical assets in this vocabulary: pets and captive wild animals are covered, and [Regulation (EU) 2016/429](https://eur-lex.europa.eu/eli/reg/2016/429/oj) (Article 4) gives keepers and operators, who have animals under their responsibility even for a limited time, legal duties that ownership does not carry.
6. **Certification is a root concept.** `Certification` is a dated attestation by a certifying organization that a subject conforms to a scheme within a scope. It is not a Registration, because a certification body attests conformity as a third party rather than recognizing the subject administratively. `certification_scope` is a multivalued CodedValue under the scheme. When the status of one part of a scope diverges, each part is its own Certification.
7. **Kinds without their own properties are closed codes, not subclasses.** Kinds of agricultural facility, service and input product are values of closed enumerations (`AgriculturalFacilityFunction`, `AgriculturalServiceType`, `AgriculturalInputCategory`), each with an `other` value, so that a code exchanged as `apiary` resolves to one published meaning. A subclass exists only when it carries its own slots, as `agri/AgriculturalLaboratory` does with `laboratory_capability`. Membership of a producer organization is an `InstitutionalRole` with a member role code.
8. **FHIR is the model for medical detail.** Medicinal product definitions and healthcare directory resources (Organization, Location, HealthcareService and related resources) use native FHIR R5 5.0.0. PublicSchema supplies qualified registry links and separately asserted subject identity; it does not define native medicinal product or healthcare service classes, relabel JSON-LD as FHIR, or claim that a base-profile example meets a jurisdictional implementation guide. `health/HealthFacility` remains a PublicSchema ServicePoint with a close mapping to FHIR Location, because facility identity, type and level are needed by registries that do not exchange FHIR.
9. **Capacity observations are cross-sector.** `ServiceCapacityObservation` is a root Event about a subject, informed by [SOSA](https://www.w3.org/TR/2017/REC-vocab-ssn-20171019/) without asserting representation equivalence.

Relationship records in these modules follow the existing `start_date` and `end_date` convention. Inclusive calendar end dates from a source are converted only under an explicit source contract; registration, tenure and certification validity keep their own `valid_from` and `valid_to` meanings.

## Alternatives considered

- **A flat catalog with every new term at root.** Rejected. It avoids namespace decisions but hides the sector meaning that domain namespaces exist to express.
- **Namespace by source module.** Rejected. It would narrow generic identities, asset relationships and observations to the module that happened to define them.
- **Snapshot operator and address slots on each facility class.** Rejected. They cannot hold dates, so a change of operator or address overwrites history.
- **AnimalResponsibility as an AssetPartyRole.** Rejected. It would make animals physical assets and hide the keeping and operating duties that animal health law defines independently of ownership. The two shapes can be reconsidered together if a shared responsibility record is needed; both would then need the same actor typing.
- **Certification as a Registration.** Rejected. Registration is administrative recognition by an authority; certification is a conformity attestation by a certifying body.
- **Empty subclasses for each facility, service or product kind.** Rejected. A class with no properties of its own adds hierarchy without adding structure, and every consumer must dispatch on it.
- **CodedValue for those kinds.** Rejected for the core kinds, because they would remain unpublished meanings. National or scheme-specific refinements can be added by profiles.
- **Parallel native medical classes, or FHIR for every facility fact.** Rejected. The first duplicates regulated meaning; the second would make an external medical representation a prerequisite for a school or farm estate record.

## Consequences

A facility operator or address history maps to several dated records rather than a field on the facility. Consumers looking for the current operator filter AssetPartyRoles by role and date.

Adding a facility, service or product kind means adding an enumeration value and its translations, not a class. A national establishment type that matches no published value uses `other`; a profile that needs the national type records it separately.

The [FHIR integration guide](../docs/fhir-registry-integration.md) identifies the selected resources, official artifacts, mapping losses and validation boundaries. The [domain migration guide](../docs/domain-migration.md) lists affected identities and payloads.
