# Spanish translation review -- UI dictionary (ui.ts)

Scope: all ~85 Spanish key-value pairs in the `es` object of `site/src/i18n/ui.ts`, reviewed for register consistency, terminology, naturalness, and pan-Hispanic neutrality.

---

## Part 1: Terminology glossary and consistency check

### Terms reviewed

**Concept / Concepts**

| Rendering | Keys |
|---|---|
| Concepto / Conceptos | `nav.concepts`, `common.concepts`, `concepts.page_title`, `concepts.table.concept`, `concept_detail.*`, `home.core_concepts`, `search.placeholder`, `search.browse_hint`, `properties.page_subtitle` |

No inconsistency. "Concepto" is the correct, internationally neutral term. Canonical: **Concepto / Conceptos**.

---

**Property / Properties**

| Rendering | Keys |
|---|---|
| Propiedad / Propiedades | `nav.properties`, `common.properties`, `properties.page_title`, `properties.table.property`, `property_detail.*`, `concept_detail.table.property`, `search.placeholder` |

No inconsistency. Canonical: **Propiedad / Propiedades**.

---

**Vocabulary / Vocabularies**

| Rendering | Keys |
|---|---|
| Vocabulario / Vocabularios | `nav.vocabularies`, `common.vocabularies`, `vocab.page_title`, `vocab.table.vocabulary`, `vocab_detail.*`, `home.vocabularies`, `search.browse_hint` |

No inconsistency. Canonical: **Vocabulario / Vocabularios**.

---

**System / Systems**

| Rendering | Keys |
|---|---|
| Sistema / Sistemas | `common.systems`, `footer.systems`, `systems.page_title`, `systems.table.system`, `system_detail.*`, `vocab_detail.system_mappings`, `vocab_detail.system_vocabulary`, `property_detail.system_mappings` |

No inconsistency. Canonical: **Sistema / Sistemas**.

---

**Mapping / Mappings**

| Rendering | Keys |
|---|---|
| Correspondencia / Correspondencias | `vocab_detail.system_mappings`, `systems.table.value_mappings`, `system_detail.relationship_value_mapping`, `system_detail.coverage_mapped`, `system_detail.report_button`, `property_detail.system_mappings`, `concept_detail.table.match` |
| sin correspondencia | `vocab_detail.same_standard_desc_suffix` |

The term "correspondencia" is internally consistent and appropriate. It is the standard CEPAL/OIT rendering of "mapping" in this domain. No inconsistency detected. Canonical: **Correspondencia / Correspondencias**.

Note: "mapeados" (see Part 2, below) appears in three evidence strings and breaks this consistency.

---

**Standard / Standards**

| Rendering | Keys |
|---|---|
| Norma / Normas | `vocab.table.standard`, `vocab_detail.standard_reference`, `vocab_detail.aligned_standards`, `vocab_detail.same_standard`, `vocab_detail.same_standard_desc_prefix`, `systems.table.same_standard`, `system_detail.relationship_same_standard`, `concept_detail.aligned_standards`, `concept_detail.table.standard` |

No inconsistency. "Norma" (not "estándar") is the correct institutional term (ISO, ITU, CEPAL all use "norma"). Canonical: **Norma / Normas**.

---

**Definition**

| Rendering | Keys |
|---|---|
| Definición | `concepts.table.definition`, `properties.table.definition`, `vocab.table.definition`, `vocab_detail.table.definition`, `concept_detail.table.definition` |

No inconsistency. Canonical: **Definición**.

---

**Search / Browse**

| Rendering | Keys |
|---|---|
| Buscar | `nav.search`, `search.placeholder`, `search.min_chars`, `search.close` |
| Explorar | `footer.explore`, `search.browse_hint`, `home.browse_schema`, `404.or_browse` |

"Buscar" (active keyword search) vs. "Explorar" (browse by category) -- the semantic split is correct and consistent. No issue.

---

**Used by**

| Rendering | Keys |
|---|---|
| Usado por | `properties.table.used_by`, `property_detail.used_by` |

Grammatical issue flagged in Part 2 (gender agreement with "Propiedad"). See below.

---

**Evidence**

| Rendering | Keys |
|---|---|
| Evidencia | `concept_detail.evidence` |

"Evidencia" is a calque of the English "evidence" when used to mean "empirical data / presence data." Flagged in Part 2.

---

**Report (a problem)**

| Rendering | Keys |
|---|---|
| Reportar | `system_detail.report_button` |

"Reportar" is a common latinism in Latin America but a false cognate in formal Spanish. Flagged in Part 2.

---

**About**

| Rendering | Keys |
|---|---|
| Acerca de | `nav.about`, `footer.about`, `home.about_project` |

No inconsistency. "Acerca de" is standard and pan-Hispanic. Canonical: **Acerca de**.

---

**Source (on GitHub)**

| Rendering | Keys |
|---|---|
| Fuente en GitHub | `footer.source_github`, `home.source_github` |

"Fuente" for the source code repository is technically acceptable but slightly informal in a formal institutional context. "Código fuente" or simply "Repositorio en GitHub" is clearer. This is a borderline case -- see Part 2.

---

**Mapped (delivery systems)**

| Rendering | Keys |
|---|---|
| mapeados | `concept_detail.evidence.all_systems`, `concept_detail.evidence.none`, `concept_detail.evidence.partial` |

"Mapeados" is an anglicism (calque of "mapped"). The established Spanish institutional term in this context is "relevados" or "analizados" for surveyed systems, or simply "identificados". See Part 2.

---

**Coverage**

| Rendering | Keys |
|---|---|
| Cobertura | `system_detail.table.coverage`, `system_detail.coverage_all`, `system_detail.not_covered` |
| sin cobertura | `system_detail.not_covered` |

No inconsistency. "Cobertura" is the standard CEPAL/OIT term. Canonical: **Cobertura**.

---

**Gaps**

| Rendering | Keys |
|---|---|
| Brechas | `system_detail.table.gaps` |

"Brechas" is the standard CEPAL/World Bank term for policy/coverage gaps. Correct. Canonical: **Brechas**.

---

**Type / Data Types**

| Rendering | Keys |
|---|---|
| Tipo / Tipos | `properties.table.type`, `concept_detail.table.type`, `property_detail.type` |
| Tipos de datos | `common.data_types` |

No inconsistency. Canonical: **Tipo / Tipos de datos**.

---

**Label**

| Rendering | Keys |
|---|---|
| Etiqueta | `vocab_detail.table.label`, `property_detail.table.system_label` |

"Etiqueta" is the standard computing/UI term in Spanish. Correct. Canonical: **Etiqueta**.

---

**Cardinality**

| Rendering | Keys |
|---|---|
| Cardinalidad | `property_detail.cardinality` |

Accepted technical term (ISO/IEC, database literature). No issue.

---

**Abstract (badge/title)**

| Rendering | Keys |
|---|---|
| abstracto | `concept_detail.abstract_badge` |

Badge text should agree with the noun it modifies ("supertipo abstracto" is correct, but the badge alone reads "abstracto" as a bare adjective). See Part 2 for a minor note.

---

## Part 2: Line-by-line issues

---

**Key:** `properties.table.used_by` and `property_detail.used_by`

- **Current:** `Usado por`
- **Issue:** "Usado" is masculine, but the thing being used is "Propiedad" (feminine); within these two properties sections the column header describes a property being used by concepts, so gender should agree with "Propiedad."
- **Proposed:** `Utilizada por`
- **Rationale:** Agreement with "propiedad" (feminine); "utilizada" is also slightly more formal and matches institutional register better than "usada/usado."

---

**Key:** `property_detail.no_uses`

- **Current:** `No usado por ningún concepto aún.`
- **Issue:** Same gender mismatch as above; "No usado" should agree with "propiedad" (feminine). Also, "aún" at the end reads slightly abrupt; a more natural placement is before the verb phrase.
- **Proposed:** `Aún no utilizada por ningún concepto.`
- **Rationale:** Fixes gender agreement and improves natural word order.

---

**Key:** `concept_detail.evidence`

- **Current:** `Evidencia`
- **Issue:** "Evidencia" as a section header is a direct calque of English "evidence." In standard Spanish, "evidencia" most naturally means "obvious truth" (as in "es evidente"), not "empirical data." The CEPAL/OIT term for data-backed evidence in policy contexts is "datos" or "respaldo empírico." In a UI context, "Datos de presencia" or simply "Presencia en sistemas" is more precise and natural.
- **Proposed:** `Presencia en sistemas`
- **Rationale:** Describes what this section actually shows (which delivery systems contain this concept), avoids the calque, and is unambiguous.

---

**Key:** `concept_detail.evidence.all_systems`

- **Current:** `Presente en los {total} sistemas de prestación mapeados.`
- **Issue:** "Mapeados" is an anglicism (calque of "mapped"). The established institutional term is "relevados" (surveyed/catalogued) or "analizados" (analysed). "Mapeados" does appear in some Latin American technical contexts, but it is not the preferred term in CEPAL/OIT/World Bank Spanish documentation.
- **Proposed:** `Presente en los {total} sistemas de prestación relevados.`
- **Rationale:** "Relevados" (from "relevar": to survey, to catalogue) is the standard CEPAL term for systems that have been surveyed or catalogued for analysis.

---

**Key:** `concept_detail.evidence.none`

- **Current:** `Aún no encontrado en los sistemas de prestación mapeados.`
- **Issue:** Same anglicism ("mapeados") as above; also "encontrado" agrees with the wrong noun (it should agree with "concepto", which is masculine -- this is fine -- but the phrasing is passive and somewhat awkward).
- **Proposed:** `Aún no identificado en los sistemas de prestación relevados.`
- **Rationale:** "Identificado" is more precise and natural than "encontrado" in this context; replaces "mapeados" with "relevados".

---

**Key:** `concept_detail.evidence.partial`

- **Current:** `Presente en {count} de {total} sistemas de prestación mapeados.`
- **Issue:** Same anglicism ("mapeados").
- **Proposed:** `Presente en {count} de {total} sistemas de prestación relevados.`
- **Rationale:** Consistency with proposed fix to the other two evidence strings.

---

**Key:** `system_detail.report_button`

- **Current:** `Reportar un problema con estas correspondencias`
- **Issue:** "Reportar" is a widespread latinism but is still considered an anglicism in formal written Spanish; the academically preferred verb is "informar (de)" or "notificar." For a UI button, "Notificar un problema" or "Informar de un problema" is more appropriate in a formal pan-Hispanic register.
- **Proposed:** `Notificar un problema con estas correspondencias`
- **Rationale:** "Notificar" is universally understood across Spain and Latin America in a formal UI context, and is the term used in ISO/CEPAL technical documentation.

---

**Key:** `footer.source_github` and `home.source_github`

- **Current:** `Fuente en GitHub`
- **Issue:** "Fuente" in the sense of source code repository is understood but slightly ambiguous (it also means "font" or "source" in other senses). In institutional technical Spanish, "Repositorio en GitHub" is unambiguous and more precise.
- **Proposed:** `Repositorio en GitHub`
- **Rationale:** Removes ambiguity; "repositorio" is the standard term in Spanish-language open-source and institutional technical contexts.

---

**Key:** `nav.about` and `footer.about`

- **Current:** `Acerca de`
- **Issue:** This is correct and standard, but note that `home.about_project` renders as `Acerca del proyecto` -- the inconsistency is intentional (short label vs. full label) and acceptable. No change needed.
- **Proposed:** No change.
- **Rationale:** Noted for completeness; the two-form pattern is correct.

---

**Key:** `vocab_detail.external_values_note_suffix`

- **Current:** `La lista completa de valores está disponible en las descargas anteriores`
- **Issue:** "Anteriores" (above/previous) is a calque of English "above" used for spatial position on a page. In Spanish, "anteriores" refers to temporal "previous," not spatial "above." The correct spatial reference is "en las descargas que figuran arriba" or simply "en la sección de descargas."
- **Proposed:** `La lista completa de valores está disponible en la sección de descargas`
- **Rationale:** Removes the spatial calque; "que figuran arriba" is also correct but wordier; "sección de descargas" is cleaner for a UI label.

---

**Key:** `vocab_detail.same_standard_desc_suffix`

- **Current:** `para este vocabulario, por lo que los valores son directamente compatibles sin correspondencia:`
- **Issue:** "Sin correspondencia" here means "without needing a mapping," but read in isolation it could be interpreted as "without a match" (i.e., incompatible). The French version uses "sans correspondance" with the same ambiguity, but in Spanish the risk of misreading is higher because "sin correspondencia" is more commonly used to mean "no match found."
- **Proposed:** `para este vocabulario, por lo que los valores son directamente compatibles sin necesidad de correspondencia:`
- **Rationale:** Adding "sin necesidad de" eliminates the ambiguity and clarifies the intended meaning.

---

**Key:** `concept_detail.abstract_badge`

- **Current:** `abstracto`
- **Issue:** Minor: as a standalone badge label modifying "supertipo" (masculine), "abstracto" is grammatically correct. However, the full tooltip (`concept_detail.abstract_title`) uses "Supertipo abstracto," so the badge and tooltip are consistent. No change needed, but note that if the badge ever appears next to a feminine noun, the rendering will need to change.
- **Proposed:** No change.
- **Rationale:** Correct as-is given current context.

---

**Key:** `banner.not_translated`

- **Current:** `Esta página aún no está disponible en español. El contenido a continuación está en inglés.`
- **Issue:** "A continuación" is correct and natural. No issue. This is one of the better-written strings in the dictionary.
- **Proposed:** No change.
- **Rationale:** Correct.

---

**Key:** `search.no_results`

- **Current:** `Sin resultados para`
- **Issue:** This string is used as a prefix (e.g., "Sin resultados para 'query'"). "Sin resultados para" is understandable but slightly terse; the more natural Spanish phrasing would be "Ningún resultado para" or "No se encontraron resultados para." However, given that this is a short UI label prefix that must work at any length, "Sin resultados para" is acceptable. The French equivalent uses "Aucun résultat pour," which has the same terse structure.
- **Proposed:** `Ningún resultado para`
- **Rationale:** More idiomatic than "Sin resultados para" as a standalone UI prefix; avoids the slightly English-calqued "sin resultados" pattern.

---

**Key:** `docs.category.landscape`

- **Current:** `Panorama`
- **Issue:** No issue. "Panorama" is the correct and standard CEPAL/World Bank translation of "landscape" in the sense of an overview of the policy or technology environment. No change needed.
- **Proposed:** No change.
- **Rationale:** Correct.

---

**Key:** `home.closing`

- **Current:** `PublicSchema se mantiene como un proyecto abierto.`
- **Issue:** No issue. Natural, neutral, and formally correct.
- **Proposed:** No change.
- **Rationale:** Correct.

---

## Part 3: Overall impression

The Spanish translation is competent and internally consistent: key terms (norma, correspondencia, cobertura, brecha) align well with CEPAL/OIT/World Bank institutional vocabulary, and the register is appropriately formal throughout. The most significant systemic issue is the use of "mapeados" in three evidence strings -- it is the clearest anglicism in the dictionary and should be replaced uniformly with "relevados." A secondary pattern is gender agreement: "usado por" appears twice where "utilizada por" would be more precise. The translation is close to shippable with a handful of targeted corrections; it does not need to be redone.
