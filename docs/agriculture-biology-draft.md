# Agricultural biology draft review

This draft distinguishes biological identity, managed populations, cultivation episodes and physical plant material. All eleven concepts and their new properties are draft. The seven source families are implemented; no registry dataset containers or application-required fields are imported. See [synthetic records](/registry-draft/examples/agriculture-biology/records.json) and `tests/test_agriculture_biology.py`.

| Family | Decision and boundary |
| --- | --- |
| Individual animal | `IndividualAnimal` persists when a tag is replaced. Reuse `Identifier`, not the human `Person` or its sex vocabulary. Birth year preserves uncertain precision. `AnimalResponsibility` separates dated keeper and owner roles; `AnimalResidence` separately dates the place where the animal is kept. |
| Animal group | `AnimalGroup` is independent of the human `Group` hierarchy. `AnimalGroupCount` dates population observations. A partial known-member list does not assert complete membership. Predecessors can describe splits or merges but are not a movement ledger. |
| Animal breed | `AnimalBreed` identifies a source-contextual breed concept. A national breed population and its risk assessment are observations, not timeless breed properties. |
| Crop planting | `CropPlanting` is cultivation, not an administrative declaration or permanent land attribute. `CropPlantingComponent` supports mixed crops with distinct dates. Area components may overlap. Season, parcel, dates and area remain optional. |
| Plant variety | `PlantVariety` distinguishes biological identity from national listing, protection and denomination approval. Multiple names do not imply multiple varieties. |
| Genetic resource accession | `GeneticResourceAccession` covers plant collection accessions. Collection-scoped numbers and holding institute remain distinct. Neither a variety nor a physical sample is identical to an accession. Animal and microbial accession specialization is outside this plant family. |
| Seed lot | `SeedLot` identifies physical material. Multiple lots may represent one accession; mixtures can refer to multiple varieties, accessions and source lots. Quantity does not claim a current inventory balance. |

## Evidence and alternatives

[WOAH Terrestrial Code 2024, chapter 4.3, article 4.3.3, identification and registration](https://www.woah.org/fileadmin/Home/eng/Health_standards/tahc/2024/en_chapitre_ident_design.htm) supports individual and group identification, replacement identifiers and registration of changes. Registration section 3(c) explicitly includes owner or keeper changes without establishment changes. Separate responsibility and residence associations preserve that distinction. Our association shapes, count observation and optionality are vocabulary design choices. Copying mandatory traceability fields would imply an operational program the vocabulary cannot enforce.

[FAO DAD-IS data](https://www.fao.org/dad-is/data/en/) distinguishes breed information, population size and structure, and risk information. We retain a contextual breed concept instead of treating a breed name as a globally unique key or importing current population status into its identity.

[FAO WCA 2010, chapter 11, crop concepts](https://www.fao.org/4/a0135e/a0135e05.htm) discusses successive, interplanted and mixed crops and area attribution. This is historical conceptual evidence, not current census conformance. Components permit mixed episodes without mandating that crop areas sum to parcel area. A single primary-crop field would lose this information.

[UPOV 1991 Convention Article 1(vi)](https://www.upov.int/documents/d/upov/docs-en-publications-upov_pub_221.pdf) supplies the variety distinction. The actual [PLUTO TAG data format, pages 5–6, tags 010, 540–543 and 600](https://www.upov.int/documents/d/upov/docs-en-pluto-contribute-pluto-tag-format-description.pdf) separates national-list and rights records and supports differing denominations across countries. PublicSchema retains identity and names; approval history belongs to a jurisdictional registration profile. No equivalence to an entire PLUTO record is claimed.

The [Genesys API manual, sections 3.1–3.4](https://www.genesys-pgr.org/documentation/apis) provides an actual accession JSON model with institute, accession number, taxonomy and incomplete collection dates. Section 3.2 explicitly labels its JSON model outdated. It is used as historical implementation evidence, not a current API contract. Preserving the original date string avoids turning `1990----` into a fabricated January date. We do not copy its identity triplet as a universal uniqueness constraint.

[CFIA QSP 152.1, definitions and sections 4.6–4.9](https://inspection.canada.ca/en/plant-health/seeds/seed-inspection-procedures/oecd-and-eu) distinguishes lots, blends, mixtures and certification, including differing domestic and OECD terminology. Generic source-lot links are preferable to importing a jurisdiction-specific mixture enum. Composition proportions and certification rules require an explicit scheme profile; source links alone cannot reconstruct a regulated mixture declaration.

The supplied agriculture starter was compared with these sources. Its global registry inheritance, closed animal vocabularies, required season year and exact-looking field alignments were not carried over. Native global slots, typed relationships and open `CodedValue` classifications support review without locking one registry's operating rules into the vocabulary.

## Examples, counterexamples and export limits

The animal example changes keeper while retaining one animal identity, one continuing residence and the same owner. Separate dated relationship records preserve this distinction; changing a keeper never implies a sale or movement. The synthetic herd has twelve animals but only one known individual. Summing both as thirteen double-counts livestock. The mixed planting has two independently dated components and no fabricated season. Two seed lots refer to one accession and variety; merging these three identities destroys physical traceability. A partial variety with no protection is valid vocabulary data.

JSON Schema exports check primitive types and arrays, but accept additional properties and unresolved string references. SHACL additionally checks typed RDF relationships when target nodes and their types are supplied. URI-only residence subjects, sites and actors require a consuming profile to resolve and check their stated target types. Neither export proves identity, pedigree, varietal purity, completeness or chronological consistency. The vocabulary does not encode submission-requiredness or numeric bounds. Focused tests distinguish structural export validation from an explicit small count-submission profile that requires a nonnegative count and observation date. No whole-starter or RegistryStack compatibility claim is made.

No external standard enum or exact mapping is asserted. Original local or unmapped codes can be carried in `CodedValue` without fabricating an external meaning URI. Translation and independent terminology review remain prerequisites for maturity promotion.

## Contribution brief

Please provide contradictory examples or source-backed alternatives for breed recognition across communities, perennial planting episode boundaries, uncertain parentage, accession identity after transfer, and mixed-lot composition. Denomination approval history, pedigree confidence, seed tests, access-and-benefit-sharing status and complete movement/inventory systems remain adjacent profiles or future specialized vocabulary, not claims delivered by these identity concepts. External review has not yet occurred.
