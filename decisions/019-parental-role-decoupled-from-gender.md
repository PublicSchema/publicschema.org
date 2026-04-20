# ADR-019: Parental role vocabulary decoupled from gender

**Status:** Accepted

## Context

The `parental-role` vocabulary previously encoded both the role-nature of parenthood (biological, legal, adoptive, gestational) and the gender of the parent holder in a single code. Its seven values were: `biological_mother`, `biological_father`, `legal_mother`, `legal_father`, `adoptive_mother`, `adoptive_father`, `surrogate_mother`.

This design has three structural problems:

1. **It excludes valid family structures.** Same-sex couples, trans parents, and non-binary parents cannot be accurately represented without local extensions or workarounds. A same-sex adoptive couple cannot both be `adoptive_mother` or both be `adoptive_father`; a trans man who gives birth cannot be `biological_mother` without misrepresenting his gender identity.

2. **It duplicates information.** The parent's gender or sex is already modeled on the associated `crvs/Person` record via `Person.sex`. Encoding gender again in the parental-role code creates a redundant and potentially contradictory field.

3. **It conflates two independent dimensions.** Role-nature (how parenthood arose) and gender (the parent's identity) are orthogonal. A schema that conflates them breaks when one dimension changes or is uncertain.

### Standards reviewed

**Hague Convention on Intercountry Adoption (HCCH 1993, Articles 4, 16, 17, 23).** The treaty text uses "mother and father" in a small number of places; Article 23 specifies only timing and parties for the adoption certificate, not role labels. The 1994 model certificate (Annex C of the Special Commission Report) uses "adoptive father / adoptive mother" as template fields, but this is model guidance for printed certificates, not a treaty obligation on the data model. No treaty article requires gendered codes in a registry schema.

**UN DESA Principles and Recommendations for a Vital Statistics System, Rev 3 (2014), Table III.1.** Rev 3 organizes birth-statistics variables under "Characteristics of the mother" (subsection iii) and "Characteristics of the father" (subsection iv). Paragraph 108 refers to "age of mother and father for live births and foetal deaths." This is the primary residual tension. However, these are statistical tabulation categories, not schema-level identity fields. A system satisfies Rev 3 by exposing mother/father views over a gender-neutral underlying data model: a jurisdiction or statistical agency derives the "mother" tabulation category by mapping `parental_role: gestational` to "mother" and other roles accordingly. The `mother` convenience property on Birth and FetalDeath is retained precisely for this compatibility path, with an updated definition that makes the derivation rule explicit.

**FHIR v3 RoleCode (THO v7.0.1, used by FHIR R5).** `PRN` is the gender-neutral parent supertype; `ADOPTP` is a gender-neutral adoptive parent code; `GESTM` (gestational mother) is female-coded. No gender-neutral gestational code exists in FHIR RoleCode. Our `gestational` value fills this gap. Systems mapping to FHIR emit `GESTM` when the gestational parent is female; otherwise they use `PRN` with a local extension.

**Comparative jurisdictions.** Multiple civil registration systems have moved toward gender-neutral or multi-parent models:

- Ontario (Canada): *All Families Are Equal Act* (Bill 28, 2016) replaced "mother and father" with "parent"; up to four parents are legally recognized.
- British Columbia, Quebec, Manitoba: hybrid "birth mother and other parent" or "father or other parent" terminology.
- Sweden (Skatteverket, since 2022-01-01): `mor` / `far` / `förälder` (the last for same-sex parents).
- United Kingdom: `mother (parent 1)` / `father or parent 2` in administrative practice.
- Netherlands: `moeder` / `vader` for opposite-sex couples, `ouder 1` / `ouder 2` for same-sex couples.
- OpenCRVS: retains gendered form sections in its UI but the underlying FHIR model uses flexible `RelatedPerson` codes.

No jurisdiction reviewed requires gendered role codes at the data model layer. Jurisdictions that require gendered or positional labels on the printed certificate achieve this at the document generation layer, not in the registry schema.

## Decision

### i. Rewrite `parental-role` to four gender-neutral values

The vocabulary is rewritten to: `biological`, `gestational`, `legal`, `adoptive`.

- `biological`: the genetic origin of the child, regardless of who carried the pregnancy or holds legal parentage.
- `gestational`: the person who carried and gave birth to the child, regardless of genetic relationship or legal status. Fills the FHIR RoleCode gap (no gender-neutral gestational code exists; only `GESTM`, which is female-coded).
- `legal`: a person recognized by law as a parent, established by marital presumption, voluntary recognition, judicial declaration, or court order, regardless of biological connection.
- `adoptive`: a person who acquired parental rights through a formal adoption order.

System mappings are updated: `biological` maps broadly to FHIR `PRN`; `gestational` maps narrowly to `GESTM` (with a note that GESTM is female-coded and gender-neutral cases require a local extension); `legal` maps broadly to `PRN`; `adoptive` maps exactly to `ADOPTP`.

### ii. Add `parent-establishment-basis` vocabulary

A new vocabulary `crvs/parent-establishment-basis` is added with five values: `marital_presumption`, `voluntary_recognition`, `judicial_declaration`, `adoption_order`, `surrogacy_order`. This captures the legal mechanism by which parentage was established, which is orthogonal to role-nature. The `adoption_order` value cites the Hague Convention on Intercountry Adoption.

### iii. Add `establishment_basis` property

A new property `establishment_basis` is added, backed by the `crvs/parent-establishment-basis` vocabulary. It is added to the `Parent` concept. It complements `parental_role`: the role says *what kind* of parent; the establishment basis says *how* the legal relationship was created.

### iv. Add `certificate_label` property

A new property `certificate_label` is added as a free-text string on `Parent`. Jurisdictions that require gendered designations ("mother", "father") or positional labels ("parent 1", "parent 2") on the legal certificate store the required label here. This keeps the data model gender-neutral while providing a documented, typed escape hatch for certificate display requirements. The underlying role-nature remains on `parental_role`.

### v. `mother` property kept for UN DESA tabulation compatibility

The `mother` convenience property on `Birth` and `PaternityRecognition` is retained but its definition is updated to clarify that it is a statistical-tabulation helper. It returns the `Parent` instance whose `parental_role` is `gestational` (or, where no gestational parent is recorded, whose `certificate_label` indicates "mother"), for compatibility with UN DESA Rev 3 tabulation requirements. The definition explicitly states that this is not a modelling assertion that only one parent is a "mother" or that parenthood is gendered. A `father` counterpart is not added in this tranche; systems needing one for statistical tabulation can filter on `parental_role` or `certificate_label` directly.

## Parent concept snapshot semantics

The `Parent` concept definition is tightened to make event-scoped snapshot semantics explicit. A `Parent` instance is scoped to a single event context. The `parental_role`, `establishment_basis`, and `certificate_label` recorded on a `Parent` instance are the values asserted at the time of that event. Reusing the same `Parent` instance across multiple events would break snapshot semantics because the role or establishment basis may differ across event contexts. The canonical way to assert parenthood across contexts is via `Relationship` records between `Person` instances.

## Alternatives considered

**Keep gendered codes.** Rejected. The existing seven codes exclude same-sex parents, trans parents, and non-binary parents without local workarounds. No authoritative standard requires gendered codes at the data model layer.

**Split into two vocabularies: one for role-nature, one for gender.** Rejected. The parent's gender is already modeled on `Person.sex`. Adding a gender dimension to a parental-role vocabulary would duplicate that field and introduce a second location where gender must be kept consistent. The schema's principle of non-duplication applies.

**Add a `gestational_parent` flag or separate property instead of a new vocabulary value.** Rejected. Gestational parenthood is a role-nature in the same sense that biological, legal, and adoptive parenthood are. Modeling it as a boolean flag would be inconsistent with how the other role-natures are modeled.

**Remove `mother` entirely.** Rejected. The `mother` property provides a practical compatibility path for UN DESA Rev 3 statistical tabulation. Removing it would require implementing systems that follow Rev 3 to derive the equivalent from `parental_role` without any guidance. Keeping it with a clarified definition is lower friction.

## Consequences

- `schema/vocabularies/crvs/parental-role.yaml`: values rewritten from 7 gendered codes to 4 gender-neutral codes.
- `schema/vocabularies/crvs/parent-establishment-basis.yaml`: new vocabulary, 5 values.
- `schema/properties/establishment_basis.yaml`: new property, backed by `crvs/parent-establishment-basis`.
- `schema/properties/certificate_label.yaml`: new free-text string property.
- `schema/concepts/parent.yaml`: `establishment_basis` and `certificate_label` added to properties list; definition tightened to make snapshot semantics and property roles explicit.
- `schema/properties/parental_role.yaml`: definition rewritten to remove gendered language.
- `schema/properties/parents.yaml`, `adoptive_parents.yaml`, `previous_parents.yaml`, `recognizing_parent.yaml`: definitions updated to remove gender-implying phrasing.
- `schema/properties/mother.yaml`: definition updated to clarify statistical-tabulation purpose and UN DESA Rev 3 derivation rule.
- `schema/bibliography/hague-intercountry-adoption.yaml`: `Parent` concept and new vocabulary and property added to `informs`.
- `schema/bibliography/fhir-v3-role-code.yaml`: `Parent` concept and `parental-role` vocabulary added to `informs`.
- `schema/bibliography/un-vital-stats-rev3.yaml`: `mother` property added to `informs`.
- Breaking at the code level for any system that stored `biological_mother`, `biological_father`, `legal_mother`, `legal_father`, `adoptive_mother`, `adoptive_father`, or `surrogate_mother` as `parental_role` values. Because `parental-role` is `draft` maturity (per ADR-002, breaking changes to draft items require no deprecation path), no migration notice is required.

## References

- [ADR-002: Per-entity maturity plus release versioning](002-maturity-model.md)
- [ADR-003: Domain-scoped URIs, not prefixed names](003-domain-namespacing.md)
- Hague Conference on Private International Law (HCCH), Convention of 29 May 1993 on Protection of Children and Co-operation in Respect of Intercountry Adoption, Articles 4, 16, 17, 23: https://www.hcch.net/en/instruments/conventions/full-text/?cid=69
- United Nations Statistics Division, Principles and Recommendations for a Vital Statistics System, Revision 3 (ST/ESA/STAT/SER.M/19/Rev.3), 2014, Table III.1, paragraphs 65-66, 108: https://unstats.un.org/unsd/demographic-social/Standards-and-Methods/files/Principles_and_Recommendations/CRVS/M19Rev3-E.pdf
- Health Level Seven International, FHIR v3 RoleCode (THO v7.0.1): PRN (parent, gender-neutral), GESTM (gestational mother, female-coded), ADOPTP (adoptive parent, gender-neutral): https://terminology.hl7.org/CodeSystem-v3-RoleCode.html
- Ontario (Canada), All Families Are Equal Act, 2016 (Bill 28): https://www.ontario.ca/laws/statute/17c23
- Statistics Sweden (Skatteverket), changes to parenthood registration since 2022-01-01: https://www.skatteverket.se/
- OpenCRVS v1 FHIR model: RelatedPerson.relationship (flexible string, gendered form sections in UI): https://documentation.opencrvs.org/
