# Agricultural operations

These terms describe the physical facilities, machines, vessels and
irrigation works used in agriculture; the people and organizations that provide
agricultural services; producer organizations; and agricultural input products
with their declared composition. Agricultural concepts and properties use the
`agri/` namespace. Terms whose meaning is not specific to agriculture, such as
`ProductComponent` and `service_provider`, keep root URIs. The terms are at draft maturity.
Definitions are PublicSchema design choices informed by the sources below; they
do not claim equivalence with, or conformance to, any national register.

## Concepts and evidence

| Concept | Evidence | Meaning and boundary |
| --- | --- | --- |
| `AgriculturalFacility` | [FAO Global Soil Laboratory Network](https://www.fao.org/global-soil-partnership/glosolan/en/); [e-NAM FAQ](https://www.enam.gov.in/web/resources/FAQs-of-eNam), "How will e-NAM operate?" | A physical site, building or installation used for agricultural or aquaculture production or a related activity. It keeps its identity when its operator, holding or registration changes. `facility_function` states what happens there. |
| `AgriculturalLaboratory` | [FAO Global Soil Laboratory Network](https://www.fao.org/global-soil-partnership/glosolan/en/), network registration and proficiency disclaimer | A facility where agricultural materials are analyzed or tested. Network membership does not show accreditation or proficiency. |
| `AgriculturalMachine` | [FARMS Farm Machinery Solutions](https://agrimachinery.nic.in/Index/farmsapp), hiring and sale of machinery | An identifiable machine or implement used for agricultural work. It keeps its identity when its owner, operator or hiring service changes. Serial numbers are identifiers. |
| `FishingVessel` | [FAO Port State Measures Agreement](https://www.fao.org/fileadmin/user_upload/legal/docs/037t-e.pdf), Art. 1(j); [Global Record Unique Vessel Identifier](https://www.fao.org/global-record/background/unique-vessel-identifier/en/) | A vessel used, equipped or intended for fishing or fishing-related activities. Its IMO number or other unique vessel identifier stays with it across changes of name, flag and owner. Registration and authorization to fish are separate records. |
| `AgriculturalServiceRole` | [Register work involving pesticides](https://www.hse.gov.uk/pesticides/register.htm); [Public Register of Seeds Merchants, Processors and Packers](https://www.sasa.gov.uk/document-library/public-register-seeds-merchants-processors-packers); [FARMS](https://agrimachinery.nic.in/Index/farmsapp) | A dated relationship in which a person, organization or group offers or performs stated agricultural services. It does not show qualification, registration or permission. |
| `ProducerOrganization` | [Regulation (EU) No 1308/2013](https://eur-lex.europa.eu/eli/reg/2013/1308/oj), Art. 152; [Producer and interbranch organisations](https://agriculture.ec.europa.eu/common-agricultural-policy/agri-food-supply-chain/producer-and-interbranch-organisations_en) | An organization set up and controlled by agricultural producers to pursue shared aims in one or more sectors. Legal recognition is a separate Registration or Authorization. |
| `AgriculturalInputProduct` | [EU Pesticides Database](https://food.ec.europa.eu/plants/pesticides/eu-pesticides-database_en); [Regulation (EU) 2019/1009](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32019R1009); [Starting an animal feed business](https://www.gov.uk/government/publications/starting-an-animal-feed-business/starting-an-animal-feed-business); [FAOTERM pesticide](https://faoterm.fao.org/viewEntry.html?entryId=182628&language=en) | A product specification or marketed formulation used as an agricultural input. It is not a package, shipment, batch or product authorization. `input_product_category` states its regulatory category. |
| `ProductComponent` | [EU Pesticides Database](https://food.ec.europa.eu/plants/pesticides/eu-pesticides-database_en); [HL7 FHIR R5 Ingredient](https://hl7.org/fhir/R5/ingredient.html) | A declared constituent of a product with its role and, optionally, its amount on a stated basis. It describes composition, not use or dosage. |
| `IrrigationScheme` | [AQUASTAT irrigation and drainage methodology](https://www.fao.org/aquastat/en/overview/methodology/irrig-drainage/index.html), equipped area and water-source typology | A defined area in which water is controlled for irrigation, with the works that supply it. The equipped area differs from the area actually irrigated in a season, and from permission to use water. |

Regulatory sources explain distinctions; they are not legal advice or executable
eligibility rules. The WOAH reference is the 2024 edition of the Terrestrial
Animal Health Code, used as conceptual evidence.

## Kinds of facility, service and product are codes

A facility's kind, a service role's services and an input product's category
are values of closed vocabularies, not subclasses. None of these kinds adds
properties of its own, and a single record often needs several of them: a
livestock market is both a livestock establishment and a market, and a seed
business may process and pack seed.

| Property | Vocabulary | Values |
| --- | --- | --- |
| `facility_function` | `AgriculturalFacilityFunction` | `apiary`, `aquaculture_establishment`, `livestock_establishment`, `plant_nursery`, `storage`, `processing`, `market`, `other` |
| `agricultural_service` | `AgriculturalServiceType` | `input_supply`, `pesticide_application`, `seed_processing`, `seed_packing`, `seed_marketing`, `machinery_hire`, `advisory`, `animal_health_service`, `post_harvest`, `other` |
| `input_product_category` | `AgriculturalInputCategory` | `feed`, `fertilising_product`, `pesticide`, `other` |

A laboratory is an `AgriculturalLaboratory`, because it carries
`laboratory_capability`. `fertilising_product` follows the umbrella category of
Regulation (EU) 2019/1009, which includes fertilisers, liming materials, soil
improvers, growing media, inhibitors and plant biostimulants. `pesticide` covers plant protection
products and biocidal products, including plant growth regulators, defoliants
and desiccants. National categories and finer regulatory classes, such as the
EU product function categories, belong in a profile or in a separate coded
property.

## Operators, providers and members

Facilities, machines, vessels and irrigation schemes do not carry an operator
property. An operator, owner or other responsible party is an `AssetPartyRole`
whose `subject_uri` is the asset and whose `asset_role_type` states the
responsibility, with `start_date` and `end_date`. This keeps a change of
operator from changing the asset, and lets one business operate many sites.
See [facility roles](facility-roles.md).

`AgriculturalServiceRole` identifies its provider by URI through
`service_provider`, because the provider can be a person, an organization or a
group. A URI does not prove the kind of the target; a profile resolves it.
`service_equipment` names a machine offered or used without implying
ownership. `supplied_product` refers to a product specification by URI, so a
seed lot or a veterinary medicinal product keeps its own classification.
`service_area` describes geography, not a particular holding.

Membership of a producer organization is an `InstitutionalRole`: `role_actor`
identifies the member, `role_organization` the producer organization and
`institutional_role_type` the member role, from a published scheme. The member
may be a person, a group or an organization. Membership does not imply employment or
ownership.

## Composition and quantities

`component_substance`, `component_role` and `component_basis` are coded values.
Role distinguishes an active substance from a safener, synergist, co-formulant
or declared nutrient. The amount and the basis are read together: 10 % as a mass
fraction of the whole product differs from 10 % expressed as the oxide, and
250 g/L is a mass per volume. Quantities use UCUM units with
`unit_scheme` `ucum`: `%` for percentages, `g/L` for
concentrations, `m` for lengths and `har` for hectares.

`vessel_length_overall` is the length overall. Registered length and length
between perpendiculars are different measurements and are not recorded in this
property.

## Related records

The shared `Certification` records a scoped conformity assertion by a
certifying body; it is not a permission to operate. `WaterUseAuthorization`
records allowed quantities, each stated as a rate such as cubic metres per
day, not actual abstraction. Registrations and authorizations refer to
facilities, products and operators as their subjects; product identity is not
duplicated in them.

## Examples and counterexamples

The JSON files in `examples/agriculture-operations/` are synthetic. They
include facilities recorded by function, dated operator roles for a facility
and an irrigation scheme, service roles for machinery hire, input supply,
pesticide application and seed packing, feed and pesticide compositions with
explicit bases, and producer-organization membership held by a person and by
an organization.

Counterexamples: a laboratory directory entry is not accreditation; a suspended
authorization does not erase a product; an organic operation certificate does
not certify every product the business sells; an empty apiary remains a site;
moving bee colonies does not move the site; hectares equipped for irrigation
cannot stand in for cubic metres abstracted. Schema validation cannot determine
legal permission or whether a URI targets the intended real-world object.

## Scope

National profiles can tighten requiredness, code schemes and date ordering.
Laboratory samples and results, irrigation network topology, dosing
instructions, inspection workflows and transaction ledgers describe process or
observation models and are outside these terms.
