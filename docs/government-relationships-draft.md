# Qualified government relationships: draft

An ownership band, a programme offered at one campus and a release from one technical installation each need a precise relationship. These draft terms preserve those facts without deciding beneficial ownership, educational accreditation or environmental compliance. The reference fields remain optional; the accompanying example profile checks a complete, locally resolved exchange.

## Meanings and source boundaries

| Relationship | Reference meaning | Primary source and scope |
| --- | --- | --- |
| Ownership bounds | `OwnershipInterest` retains exact `interest_percentage`. Four separate fields preserve inclusive or exclusive lower and upper bounds. Missing amounts remain unknown. | [BODS 0.4 Share](https://standard.openownership.org/en/0.4.0/standard/reference.html#share) distinguishes exact values and these four boundary meanings. |
| Arrangement and indirect route | `LegalArrangement` identifies a mechanism without inventing an Organization. `OwnershipChainAssertion` connects a separately asserted indirect interest to the component interests offered as its route. | [BODS 0.4 entity types and relationship details](https://standard.openownership.org/en/0.4.0/standard/reference.html) include arrangements and component records. PublicSchema references interest identities; BODS references record identifiers. These are different contracts. |
| Education offering | `edu/EducationOffering` connects programme, provider, sites, period, optional mode and expected award-definition URI. | [Schema.org CourseInstance](https://schema.org/CourseInstance) distinguishes delivery by time, place or mode. [Course](https://schema.org/Course) can identify an expected educational award. PublicSchema chooses its narrower provider/site relationships. |
| Installation attribution | `environment/release_installation` identifies the technical installation behind an `EnvironmentalRelease`, where the source reports that detail. | [Regulation (EU) 2024/1244](https://eur-lex.europa.eu/eli/reg/2024/1244/oj/eng), Articles 3, 5 and 6, distinguishes installations and facilities and describes installation-level release reporting. This field implements no EU reporting obligations. |

These sources were consulted on 8 September 2026. They support the distinctions, not exact mappings or implemented BODS, Schema.org or regulatory interchange compatibility. All new concepts and properties are draft. Domain-specific education and environment meanings use `edu/` and `environment/`; shared ownership and legal arrangement meanings use root URIs. The module filename does not determine the URI namespace.

## Ownership: amounts, arrangements and asserted routes

Use `interest_percentage` only when the source asserts an exact value. “More than 25%, at most 50%” becomes `interest_exclusive_minimum_percentage: 25` and `interest_maximum_percentage: 50`. The profile rejects an exact value mixed with bounds, two competing boundary conventions on one side, percentages outside zero to one hundred, and empty intervals. A missing lower or upper bound is preserved as missing; validation does not fill it in. An inclusive interval with equal bounds is representable, though the exact field is preferable when the source supplies an exact amount.

`LegalArrangement` is separate from Person, Organization, Group and Party. The source's treatment determines whether an identified trust-like subject is an arrangement or a LegalEntity. Arrangement participation uses scheme-qualified ownership or control interests, including appropriate source codes. Nothing about this class establishes legal title or a participant's status as a beneficial owner. Unknown or withheld identities require their source-specific treatment; this example does not fabricate identified actors for them.

`OwnershipChainAssertion.component_interests` is unordered. Each component has its own holder, entity and dates, so the example profile reconstructs one connected route independently of array position. That bounded profile requires identified, explicitly direct components, rejects branches, unused edges, cycles and duplicate components, and checks known periods. Unspecified dates remain unspecified. The route can mix trustee control and share interests; multiplying the percentages would be misleading and is deliberately absent. Multiple routes can be recorded as separate assertions about the same indirect interest.

An associated `RegistryEntry` identifies the record, recording time and source evidence of a chain assertion. Recording the chain never verifies its truth. Components remain separately identifiable claims, so a later record can correct one without silently replacing other subjects. BODS package ordering, replacement rules, anonymous records, control determination and legal thresholds require an explicitly selected BODS profile or adapter.

## Education: the offering carries the site and intake

The fixture gives one programme a campus offering and a later online offering. Both reference the same external award definition. One Registration recognizes only the campus offering. An application can follow that explicit subject relationship; recognition is not copied to every programme, provider or site sharing a link.

`offering_award` identifies the expected qualification or award definition in a source catalog. It is distinct from ProfessionalQualification, which describes an award already made to a person. The example retains the definition URI without fetching it or verifying its external meaning. It does not introduce another qualification catalog or infer that any student completed the programme.

The local profile checks programme, provider and site identities, the site's provider, supplied modes and a coherent offering period. A physical School is connected through ProviderSite, while a virtual site needs no invented premises. Joint providers, session timetables, actual enrolments and accreditation criteria remain outside this bounded example. An offering can be a registration or authorization subject where the applicable scheme recognizes or permits that offering.

## Environment: preserve the reported level

The example records releases of the same substance from a boiler and furnace within one facility. The quantity remains attached to the reported installation. A source reporting only a facility total can omit `release_installation`; an installation-level source can identify the installation without repeating `release_facility`. When both are supplied, the profile checks that their facility identities agree.

The current installation-to-facility link is undated. This example checks consistency with that supplied link, not historical containment, source completeness or reporting-period coverage. It does not allocate a facility total across installations, add totals at different aggregation levels, compare a release with a permit limit or infer a violation. A historical or regulatory exchange must establish those additional contracts.

## Runnable example and verification

From the repository root:

```sh
uv run python examples/government-relationships/validate_profile.py --negative
uv run pytest tests/test_government_relationships.py
```

`records.json` contains the synthetic exchange. `negative-cases.json` describes independent changes that must be rejected, including conflicting percentage bounds, unresolved and disconnected ownership routes, incompatible periods, the wrong site provider and mismatched installation attribution. The validator runs without remote lookups or authority decisions.

The tests also use the production catalog, JSON Schema, RDF, JSON-LD context and SHACL exporters. Invalid decimal and installation values fail in both public representations. JSON requires array syntax for `offering_sites`; RDF preserves the site relationships without retaining scalar-versus-array syntax, so this constraint is checked at the JSON boundary. Semantic counterexamples exercise the separately named example profile. Passing these checks establishes local fixture behavior. Independent domain review, reviewed translations and adopter exchanges remain necessary before maturity promotion. See [ADR-024](../decisions/024-government-qualified-relationships.md) for alternatives and compatibility boundaries.
