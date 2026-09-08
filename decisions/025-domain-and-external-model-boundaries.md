# ADR-025: Domain placement and external medical model boundaries

**Status:** Accepted for draft implementation. Clarifies ADR-003; no maturity promotion.

## Context

The government and agriculture draft introduced sector concepts at root even though PublicSchema already supports domain namespaces. Properties inferred from their current consumers could also move catalog paths when a concept changed domain. Healthcare draft classes overlapped mature external resource designs, while facility responsibility and address history had useful meanings outside healthcare.

## Decision

Choose domains by definition, not by authoring module, primitive shape or consuming application. Place the reviewed agriculture, land, environment, transport, education, healthcare-premises, tax and electoral terms in their explicit namespaces. Keep generic identities and cross-sector relationships at root. Preserve every candidate and normative definition and URI, including historical placement exceptions.

Keep authored property URIs authoritative for catalog placement. Reusing a property from a new domain must not change its identity or page path. Store display labels in the existing composite metadata and show represented domains in navigation without an unclassified bucket that hides unknown codes.

Use native FHIR R5 5.0.0 for the selected medicinal definitions and healthcare directory resources. PublicSchema supplies qualified registry links and separately asserted subject identity. Do not manufacture native medical substitutes, relabel JSON-LD as FHIR, or claim that a base-profile example meets a jurisdictional implementation guide. The [integration guide](../docs/fhir-registry-integration.md) identifies selected resources, official artifacts, mapping losses and validation boundaries.

Reuse AssetPartyRole for separately stated Person/Organization responsibilities toward a physical asset. Introduce shared AssetAddressAssignment with an explicit purpose. Retain ServiceCapacityObservation as a cross-sector observation, informed by [SOSA](https://www.w3.org/TR/2017/REC-vocab-ssn-20171019/) without asserting representation equivalence. Retire the duplicated medical and ambiguous facility draft shapes with individual dispositions.

Apply the existing relationship date convention to the reviewed draft associations. Convert inclusive calendar ends only under an explicit source contract; do not reinterpret registration, tenure or certification validity. The [migration guide](../docs/domain-migration.md) and its disposition file identify affected identities and payloads.

## Alternatives and consequences

A flat catalog would avoid draft URI churn but conceal the sector meaning that existing namespaces were designed to express. Scoping every term by source module would incorrectly narrow generic animal identities, asset relationships and observations. Both alternatives were rejected.

Keeping parallel native medical models would simplify one serialization while creating a second place to maintain complex regulated meanings. Using FHIR for every cross-sector facility fact would instead make an external medical representation the prerequisite for a school or farm estate record. Native FHIR medical detail plus independently justified shared identities and asset assertions keeps those responsibilities distinct.

These are intentional breaking draft changes. No blanket equivalence or automatic conversion is asserted for retired terms. The unresolved boundaries include premises-only accreditation, adopter terminology and profile selection, and a future water and sanitation domain. Evidence from a conflicting definition, real exchange or independently designed registry can justify revisiting individual placements. External adoption and normative promotion remain separate work.
