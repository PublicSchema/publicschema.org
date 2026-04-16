# ADR-011: Document and Specification abstract supertypes

**Status:** Accepted

## Context

The schema accumulated two clusters of concepts that shared structure without a named supertype.

The first cluster is issued artefacts: `Certificate`, `CivilStatusRecord`, `FamilyRegister`, `IdentityDocument`, `Voucher`. Each carries a face reference, a bundle of cross-system identifiers, an issuing party, an issue date, and typically an expiry. Each implemented this by hand: `certificate_number`, `register_number`, `serial_number` were near-duplicates of the same concept, and the issuer was captured inconsistently (sometimes as a structured `issuing_authority` string, sometimes absent, sometimes a custom `issuer` slot).

The second cluster is registry publications: `Instrument`, `ScoringRule`, `BenefitSchedule`. Each is a persistent definition, published by an agent, versioned, with a canonical URL. Each listed these properties explicitly, and the `publisher` property's own definition enumerated the subtypes by hand.

Three problems followed. Renaming one property (e.g., `certificate_number` → something more general) required touching five concepts and three separately named properties. The RDF graph had no `Document` or `Specification` node, so external peers like CPSV-AP Evidence, CCCEV ReferenceFramework, PROV-O Plan, FHIR DocumentReference could not attach at the right level of abstraction. And future additions (birth certificate credentials, tax payment receipts, new scoring methodologies) had no natural parent to inherit from.

## Decision

1. **Introduce two abstract concepts at the root namespace:**
   - `Document` (abstract: true, supertypes: []). Shared properties: `document_number`, `identifiers`, `issuer`, `issue_date`. Subtypes: `Certificate`, `CivilStatusRecord`, `FamilyRegister`, `IdentityDocument`, `Voucher`. `expiry_date` is **not** hoisted onto Document: permanent records (`CivilStatusRecord`, `FamilyRegister`) do not expire, so the property lives only on the three subtypes where it applies (`Certificate`, `IdentityDocument`, `Voucher`).
   - `Specification` (abstract: true, supertypes: []). Shared properties: `name`, `version`, `publisher`, `publication_url`. Subtypes: `Instrument`, `ScoringRule`, `BenefitSchedule`.

2. **Retire three near-duplicate properties** in favour of a single `document_number`: `certificate_number`, `register_number`, `serial_number`. All Document subtypes use `document_number` uniformly.

3. **Add one new property, `issuer`** (type: `Agent`, cardinality: single). All Document subtypes inherit it. The existing string-typed `issuing_authority` is preserved for cases where only a textual name is available; its definition now cross-references `issuer` as the structured form.

4. **Distinguish `document_number` from `identifiers`.** `document_number` is the single face reference printed or displayed on the document itself. `identifiers` is the multi-system bundle of cross-references used to look the document up (database primary keys, registry lookup codes, external system keys). Both slots coexist on every Document subtype.

5. **Keep `creation_date` on `FamilyRegister`.** A register's creation date is distinct from its issue date and belongs on the concept, not on Document.

6. **Generalise `publisher` and `name` definitions** to cover BenefitSchedule alongside Instrument, ScoringRule, and SoftwareAgent.

7. **Populate external_equivalents on the two new abstracts** with citable peers:
   - `Document`: CPSV-AP `Evidence` (close), FHIR `DocumentReference` (broad), schema.org `CreativeWork` (related).
   - `Specification`: CCCEV `ReferenceFramework` (related), PROV-O `prov:Plan` (close), schema.org `CreativeWork` (related).
   - `document_number`: ICAO Doc 9303 `Document Number` (exact), W3C VC (related).
   - `issuer`: CPSV-AP `hasCompetentAuthority` (related), FHIR `Credential.issuer` (close), Dublin Core `publisher` (related).

8. **No backward-compatibility shims.** No adopters are on the v2 schema yet. Retired properties are deleted, not aliased.

## Alternatives considered

- **Keep the five Document subtypes with bespoke properties.** Rejected: the rename cost is already paid (three duplicate `*_number` properties), and the RDF graph loses its natural attachment point for external peers that target the abstract (CPSV-AP Evidence, PROV-O Plan).
- **Make `Document` and `Specification` concrete, not abstract.** Rejected: there is no record type that is "just a Document" without being a Certificate, Voucher, etc. Abstract is the honest statement.
- **Collapse `identifiers` into `document_number` (or vice versa).** Rejected: they answer different questions. The face reference on a passport is one string; the set of keys that systems use to look the passport up is a bundle. Both are needed and both are cited by distinct external standards (ICAO 9303 for document number, DCI and FHIR for identifiers).
- **Split `document_number` per subtype (`certificate_number`, `voucher_number`, …).** That is what the schema had. Unwinding it is the point of this ADR.
- **Drop `issuing_authority` now that `issuer` exists.** Deferred. `issuing_authority` holds a free-text name and is legitimate when only that is available. The two can coexist; the definitions cross-reference each other.
- **Make `issuer` string-typed like `issuing_authority`.** Rejected: the whole point is to give Document records a structured Agent reference, matching FHIR `Credential.issuer` and schema.org `publisher`.

## Consequences

The RDF graph gains two named supertypes. Downstream validators, JSON-LD contexts, and VC schema generators can constrain or select on `Document` or `Specification` directly.

Five concept files (Certificate, CivilStatusRecord, FamilyRegister, IdentityDocument, Voucher) now inherit five properties from `Document` and list fewer properties of their own. Three concept files (Instrument, ScoringRule, BenefitSchedule) inherit four properties from `Specification`. Property duplication is removed.

External peers attach at the right level: CPSV-AP Evidence, CCCEV ReferenceFramework, PROV-O Plan, FHIR DocumentReference, schema.org CreativeWork cite `Document` or `Specification` directly rather than being repeated on every subtype page.

`Person` still belongs to `Party` and `Agent` (ADR-008). Adding Document and Specification does not change that. Neither abstract overlaps with the existing Party/Agent hierarchies.

Future additions are cheap. A birth certificate credential, tax receipt, or benefit-card document extends Document. A new scoring methodology or benefit schedule template extends Specification. No new duplicate properties are needed.

The `name` property's definition now lists five example concept categories (person/group, program, instrument, scoring rule, benefit schedule, software product); the `publisher` property's definition now enumerates the Specification subtypes alongside SoftwareAgent. Both changes are narrative only.

## References

- ADR-006: Profile hierarchy (pattern for abstract supertypes)
- ADR-008: Agent/Party separation (pattern for typing properties at an abstract supertype)
- CPSV-AP v3.2: `Evidence`
- CCCEV v2.1: `ReferenceFramework`
- PROV-O: `prov:Plan`
- FHIR R4: `DocumentReference`, `Credential`
- ICAO Doc 9303: document number
- W3C VC Data Model 2.0
- schema.org: `CreativeWork`
- Dublin Core: `dc:publisher`
- FOAF
