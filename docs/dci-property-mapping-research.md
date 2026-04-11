# DCI Property-Level Mapping Research

Analysis of property-level `external_equivalents` between DCI (Digital Convergence Initiative) and PublicSchema.

## DCI entities used as source

Core: Person, Name, Address, Place, GeoCoordinates, Identifier, Group, Member, RelatedPerson
IBR extension: ibr/Beneficiary, ibr/Benefit, ibr/Programme

## Proposed mappings

### Exact matches (12)

| PublicSchema property | DCI entity.field | Rationale |
|---|---|---|
| `date_of_birth` | Person.birth_date | Same concept, same semantics |
| `date_of_death` | Person.death_date | Same concept, same semantics |
| `phone_number` | Person.phone_number | Same field, E.164 format |
| `sex` | Person.sex | Both record biological sex from official register |
| `given_name` | Name.given_name | Identical concept and name |
| `identifier_type` | Identifier.identifier_type | Same concept, same name |
| `identifier_value` | Identifier.identifier_value | Same concept, same name |
| `city` | Address.locality | Same concept (city/town component) |
| `postal_code` | Address.postal_code | Same concept, same name |
| `latitude` | GeoCoordinates.latitude | Same concept, same name, WGS 84 |
| `longitude` | GeoCoordinates.longitude | Same concept, same name, WGS 84 |
| `relationship_type` | RelatedPerson.relationship_type | Same concept, same name |

### Close matches (21)

| PublicSchema property | DCI entity.field | Rationale |
|---|---|---|
| `email_address` | Person.email | Same concept; different field names |
| `family_name` | Name.surname | Same concept; DCI calls it `surname` |
| `family_name_at_birth` | Name.maiden_name | `maiden_name` is a specific sub-case of birth family name |
| `name` | Person.name (Name object) | PS is flat string; DCI is structured Name object |
| `street_address` | Address.address_line_1 | PS single field; DCI splits into address_line_1/2 |
| `administrative_area` | Address.region_code | Both first-level subnational; DCI uses a code |
| `country` | Address.country_code | Both country of address, both coded |
| `location_name` | Place.name | Both human-readable location names |
| `parent_location` | Place.contained_in_place | Both hierarchical containment |
| `member_count` | Group.group_size | Same concept (integer count of members) |
| `group_type` | Group.group_type | Both classify group category; different vocabularies |
| `formation_date` | Group.registration_date | PS distinguishes formation from registration |
| `memberships` | Group.member_list | Both link group to its members; PS uses join records |
| `marital_status` | Member.marital_status | Same concept; lives on Member in DCI, Person in PS |
| `occupation` | Member.occupation | Same concept; DCI enum vs PS ISCO-08 reference |
| `education_level` | Member.education_level | Same concept; DCI enum vs PS ISCED reference |
| `preferred_language` | Member.language_code | DCI is languages spoken; PS is preferred language |
| `object_person` | RelatedPerson.related_member | Both the other party in a relationship |
| `enrollment_status` | ibr/Beneficiary.enrollment_status | Same concept, same name |
| `enrollment_date` | ibr/Beneficiary.enrollment_date | Same concept, same name |
| `benefit_description` | ibr/Benefit.benefit_description | Same concept, same name |

### Broad matches (7)

| PublicSchema property | DCI entity.field | Rationale |
|---|---|---|
| `given_name_at_birth` | Name.given_name | DCI has no birth-name distinction |
| `preferred_name` | Name.given_name | DCI has no preferred/chosen name concept |
| `patronymic_name` | Name.second_name | DCI's `second_name` covers middle names broadly |
| `matronymic_name` | Name.second_name | Same reasoning as patronymic |
| `subject_person` | (implicit in Member) | DCI embeds related_person on Member; subject is implicit |
| `exit_date` | ibr/Beneficiary.status_change_date | DCI covers any status change; PS is specifically exit |
| `benefit_modality` | ibr/Benefit.benefit_type | Both classify benefit form; vocabulary overlap unclear |

### Near-misses (excluded from mapping)

| PublicSchema property | DCI field | Why excluded |
|---|---|---|
| `raw_score` | Group.poverty_score | Structural mismatch: DCI puts scoring on Group; PS puts it on AssessmentEvent |
| `start_date` / `end_date` | Various *.start_date / *.end_date | PS properties are generic temporal bounds reused across all concepts; DCI instances are domain-specific |
| `payment_amount` | ibr/Benefit.benefit_value | Close but DCI uses a Currency composite type vs PS's separate amount + currency |
| `payment_date` | ibr/Benefit.benefit_date | Close for cash; for in-kind PS uses `delivery_date` instead |
| `implementing_agency` | ibr/Programme.implementing_institution | Close but neither side has stable URIs for these programme fields |
| `identifier_scheme_name` | Identifier.identifier_type (label) | DCI encodes scheme identity in enum, not a free-text name |

## DCI fields with no PublicSchema match (notable)

- `Member.income_level` (IncomeLevelEnum) - PS has no income bracket property
- `Member.is_disabled` / `Member.disability_info` - PS has no disability concept
- `Person.registration_date` / `*.last_updated` - PS does not carry audit timestamps as semantic properties
- `ibr/Programme.legal_status` / `social_protection_functions` / `contribution_type` / `programme_type` - PS does not classify programs this deeply
- `Address.address_line_2` - PS uses `street_address` as a single field

## PublicSchema domains with no DCI coverage

- Vouchers (entire concept absent)
- In-kind delivery mechanics
- Grievance / referral
- Assessment frameworks / eligibility decisions
- Disaster / hazard events
- Farm

## Open questions

1. **Broad matches worth including?** The 7 broad matches are quite loose (e.g., patronymic_name -> second_name). Should we include them or only exact + close?

2. **URI format for property-level mappings.** DCI JSON-LD uses URIs like `spdci:birth_date` which resolves to `https://schema.spdci.org/core/v1/data/birth_date`. Should we use these resolved URIs, or the entity-scoped form like `https://schema.spdci.org/core/v1/data/Person#birth_date`?

3. **Properties that live on different DCI entities.** `marital_status` lives on Person in PS but on Member in DCI. The note should explain this, but should the `vocabulary` field say "DCI Core" (the standard) or something that identifies the entity?
