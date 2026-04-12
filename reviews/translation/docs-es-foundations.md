# Spanish translation review — foundations docs

## design-principles.md

**Overall impression:** The translation is generally clean and reads naturally. Most choices are sound. There are a few passages where the phrasing is heavier than necessary in Spanish, and one construction borrows English word order in a way that feels stiff.

### Flagged passages

**Line 5 — Current:** "Los conceptos llevan significado."
**Issue:** Calque of "Concepts carry meaning." In Spanish "llevan" is not wrong, but "Los conceptos tienen peso semántico" or simply "Los conceptos tienen significado" is more idiomatic. "Llevar" in this abstract sense reads as a direct loan from English "carry."
**Proposed:** "Los conceptos tienen significado."
**Rationale:** "Llevar significado" is a calque. "Tener significado" is the natural Spanish construction for this kind of abstract property.

---

**Line 5 — Current:** "El problema de interoperabilidad es la divergencia de vocabulario"
**Issue:** Slightly stiff; reads as an English nominal structure pasted into Spanish.
**Proposed:** "El problema de interoperabilidad radica en la divergencia de vocabulario"
**Rationale:** "Radica en" is the standard Spanish construction for locating the source of a problem; it is used across all Spanish-speaking regions and registers.

---

**Line 13 — Current:** "Comience con lo que está confirmado; extienda cuando la adopción revele una necesidad genuina."
**Issue:** The imperative "Comience... extienda" is correct formal register, but the subject shift is jarring because the surrounding text uses impersonal/third-person constructions. The inconsistency makes it feel abrupt.
**Proposed:** "Comience con lo que está confirmado y extiéndalo cuando la adopción revele una necesidad genuina."
**Rationale:** Linking with "y" removes the abrupt semicolon break and makes the two commands read as one continuous instruction, which matches the flow of the English original ("Start with... extend when...").

---

**Line 17 — Current:** "'Los estados del ciclo de vida de una inscripción en un programa' es preferible a 'una enumeración de códigos de estado aplicables a la entidad de registro de personas beneficiarias'."
**Issue:** No issue with the content, but "códigos de estado" is a slightly technical calque for "status codes." In context it is acceptable because it is illustrating jargon to avoid, so no change needed. Flagging for awareness only.
**Proposed:** No change required.
**Rationale:** The jargon is intentional here; the sentence is showing what not to write.

---

## schema-design.md

**Overall impression:** Solid throughout. The decision tree section translates well. Two passages have calque issues, and one section was dropped entirely from the Spanish (the date property conventions subsection under section 5) without being noted, which may be intentional but should be confirmed.

### Flagged passages

**Line 5 — Current:** "El estilo de escritura codifica el tipo de elemento"
**Issue:** "Codifica" is a direct calque of "encodes." In this context it is comprehensible, but "determina" or "indica" reads more naturally in Spanish for a typographic convention.
**Proposed:** "El estilo de escritura indica el tipo de elemento"
**Rationale:** "Codificar" in Spanish primarily means to encrypt or to write code; using it in the sense of "encode information through visual convention" is an anglicism. "Indica" is unambiguous and natural.

---

**Line 14 — Current:** "Aplicado por validadores de expresiones regulares en esquemas JSON."
**Issue:** The sentence is a fragment (no subject), which can work in Spanish but here sounds abrupt because the preceding table is the subject and the connection is not obvious.
**Proposed:** "Estas convenciones son aplicadas por validadores de expresiones regulares en los esquemas JSON."
**Rationale:** Making the subject explicit ("estas convenciones") removes ambiguity and mirrors how Spanish technical prose normally handles such clarifying notes.

---

**Line 25 — Current:** "La estructura del URI maneja la disambiguación."
**Issue:** "Maneja" is a calque of "handles." It is common in Latin American technical writing but still reads as an anglicism in formal prose.
**Proposed:** "La estructura del URI se encarga de la disambiguación." or "La disambiguación recae en la estructura del URI."
**Rationale:** "Manejar" in this impersonal sense of "to take care of something" is an anglicism. "Encargarse de" or restructuring the sentence is more natural.

---

**Line 40 — Current:** "Use este árbol de decisión para determinar qué tipo de elemento crear."
**Issue:** The imperative "Use" (formal usted) is correct here. No issue.
**Proposed:** No change.
**Rationale:** Consistent with the rest of the document. Flagged and cleared.

---

**Lines 65-66 — Missing subsection:** The English original contains an entire subsection "### Date property conventions" (lines 68-81 of the EN file) with a table of lifecycle concepts and date patterns. This subsection is absent from the Spanish translation.
**Issue:** Omission, not a translation quality issue, but worth flagging so it is intentional or corrected.
**Proposed:** Add the missing subsection. Suggested rendering of the heading: "### Convenciones para propiedades de fecha"
**Rationale:** The omission means readers of the Spanish version receive less guidance than English readers. The table and rules in that section are practical, not redundant.

---

**Line 71 — Current:** "en lugar de ignorar las diferencias"
**Issue:** Calque of "rather than pretending the differences don't exist." The English is stronger ("pretending they don't exist"), and the Spanish softens it to "ignoring." This is a legitimate translator choice, but "en lugar de disimular las diferencias" or "en lugar de ignorar que existen" is slightly more faithful.
**Proposed:** "en lugar de disimular las diferencias"
**Rationale:** "Ignorar" understates the English "pretending." "Disimular" captures the deliberate-avoidance sense.

---

**Line 82 — Current:** "Esta es una advertencia para practicantes, no una etiqueta de cumplimiento."
**Issue:** "Cumplimiento" as a rendering of "compliance" is an anglicism that has become common but can still be ambiguous in some Spanish-speaking contexts (where "cumplimiento" primarily means "fulfillment" of an obligation). "Conformidad normativa" or "etiqueta regulatoria" is clearer.
**Proposed:** "Esta es una advertencia para practicantes, no una etiqueta regulatoria."
**Rationale:** "Cumplimiento" alone can be misread. "Regulatoria" makes explicit that this is about regulatory/legal compliance, not general obligation fulfillment.

---

## vocabulary-design.md

**Overall impression:** The translation is accurate and reads well. The most significant issue is the omission of an entire subsection from the English original (the "Process and mechanism vocabularies" subsection under section 1, and the "Synced standard vocabularies" subsection under section 3). These are not minor; they contain substantive guidance not present in the Spanish version. The prose that is present is natural and only has minor improvements available.

### Flagged passages

**After line 15 — Missing subsection:** The English original contains a "### Process and mechanism vocabularies" block (lines 17-22 of the EN file) that explains when process vocabularies are universal by default. This is absent from the Spanish version.
**Issue:** Omission. Substantive guidance is missing.
**Proposed:** Add the subsection. Suggested heading: "### Vocabularios de proceso y mecanismo"
**Rationale:** This subsection explains a non-obvious rule (that process vocabularies are universal by default even when first used in a domain-specific context). Without it, Spanish readers lack a key decision criterion.

---

**After line 37 — Missing subsection:** The English original contains a "### Synced standard vocabularies" block (lines 42-44 of the EN file) explaining when `same_standard_systems` suffices instead of value-level `system_mappings`. This is absent from the Spanish version.
**Issue:** Omission of practical guidance specific to large code lists.
**Proposed:** Add the subsection. Suggested heading: "### Vocabularios sincronizados con normas"
**Rationale:** Without this guidance, practitioners working with large synced vocabularies (countries, currencies, languages) will not know when they can skip value-level mappings.

---

**Line 38 — Current:** "No adopte los códigos de una norma cuando no sirven a la audiencia."
**Issue:** "No adopte" is formally correct. However "sirven a la audiencia" is a mild calque of "serve the audience." In Spanish the natural phrasing is "no resultan útiles para los usuarios" or "no son adecuados para el público al que va dirigido."
**Proposed:** "No adopte los códigos de una norma cuando no resulten útiles para los usuarios."
**Rationale:** "Servir a la audiencia" is an anglicism borrowed from English "to serve an audience." "Resultar útiles para" is idiomatic.

---

**Line 39 — Current:** "Prefiera las normas legibles por máquina sobre las que solo tienen prosa."
**Issue:** No issue with the content, but "tienen prosa" reads oddly; the English says "prose-only." "Solo están disponibles en prosa" or "basadas únicamente en texto" is cleaner.
**Proposed:** "Prefiera las normas legibles por máquina sobre las que solo están disponibles en formato de texto."
**Rationale:** "Tienen prosa" is a compressed calque. "Disponibles en formato de texto" is more natural and explicit.

---

**Line 68 — Current:** "Las correspondencias de sistemas son el mecanismo de validación principal"
**Issue:** No issue. Clear and natural.
**Proposed:** No change.

---

## versioning-and-maturity.md

**Overall impression:** This is the strongest translation of the five files. It is fluent, well-structured, and reads like it was written in Spanish rather than translated. Only one passage needs attention.

### Flagged passages

**Line 23 — Current:** "Tres niveles (no cinco, como en el FMM 0-5 de FHIR) se corresponden con un modelo mental claro: experimental, adoptante temprano, estable."
**Issue:** "Adoptante temprano" is a calque of "early adopter" and is not natural in Spanish. The concept is understood but "adoptante" is not standard vocabulary; the common rendering is "primeros adoptantes" or "adopción temprana" used attributively.
**Proposed:** "Tres niveles (no cinco, como en el FMM 0-5 de FHIR) corresponden a un modelo mental claro: experimental, primeros adoptantes, estable."
**Rationale:** "Adoptante temprano" (singular used as a category label) is an anglicism. "Primeros adoptantes" is the standard rendering used in technology and policy contexts across Latin America and Spain.

---

**Line 23 — Current:** "se corresponden con"
**Issue:** Minor. "Corresponden a" is more natural than "se corresponden con" in this context (mapping to a model). "Se corresponden con" implies a bilateral correspondence; here the mapping is one-directional.
**Proposed:** Already folded into the previous fix above ("corresponden a un modelo mental claro").
**Rationale:** "Corresponden a" is the idiomatic choice when describing what something maps to or represents.

---

**Line 66 — Current:** "la cláusula de compartir igual desalienta la adopción por parte de gobiernos e integradores corporativos"
**Issue:** "Compartir igual" is a calque translation of the ShareAlike concept from Creative Commons. The standard Spanish-language rendering used by Creative Commons in its official materials is "CompartirIgual" (one word, as a proper name). Since this is referring to a specific license clause, use the official term.
**Proposed:** "la cláusula CompartirIgual desalienta la adopción por parte de gobiernos e integradores corporativos"
**Rationale:** Creative Commons uses "CompartirIgual" as the official Spanish name of the share-alike clause. Using it ensures readers can recognize and verify the clause being discussed.

---

## extension-mechanism.md

**Overall impression:** The translation is accurate and flows well. The technical content is faithfully reproduced. Two passages contain mild calques, and one word choice carries a slight register issue.

### Flagged passages

**Line 6 — Current:** "cuando un sistema necesita algo que PublicSchema no provee, lo extiende usando su propio espacio de nombres."
**Issue:** "Provee" is increasingly accepted but remains a Latinism-via-English calque. "No proporciona" or "no ofrece" is more neutral across all Spanish-speaking regions.
**Proposed:** "cuando un sistema necesita algo que PublicSchema no ofrece, lo extiende usando su propio espacio de nombres."
**Rationale:** "Proveer" has been standardized by the RAE but "ofrecer" or "proporcionar" remains the more natural and universally unmarked choice in formal prose.

---

**Line 36 — Current:** "Los términos de PublicSchema (`given_name`, `family_name`) resuelven a URIs de PublicSchema. Sus términos personalizados (`beneficiary_category`, `proxy_score_v2`) resuelven a su espacio de nombres. Ambos coexisten de forma limpia."
**Issue:** "Resuelven a" is a calque of "resolve to" (technical DNS/URI sense). In Spanish technical documentation, "se resuelven como" or "apuntan a" is more idiomatic for URI resolution. "Coexisten de forma limpia" is also a calque of "coexist cleanly."
**Proposed:** "Los términos de PublicSchema (`given_name`, `family_name`) se resuelven como URIs de PublicSchema. Sus términos personalizados (`beneficiary_category`, `proxy_score_v2`) se resuelven como URIs de su espacio de nombres. Ambos coexisten sin conflicto."
**Rationale:** "Resuelven a" (without reflexive) reads as an English calque. "Se resuelven como" is the standard Spanish phrasing for URI/identifier resolution. "Sin conflicto" replaces the calque "de forma limpia."

---

**Line 97 — Current:** "en el arreglo `@context`"
**Issue:** "Arreglo" as a rendering of "array" is Latin American technical slang (common in Mexico and some other countries) but is not universally understood. "La matriz" is technically correct but uncommon. "El array" (borrowed term, used in most technical communities) or "el arreglo (array)" on first use would be clearer across regions.
**Proposed:** "en el arreglo (`@context` array)"
**Rationale:** If the audience includes practitioners from Spain or formal institutional contexts, "arreglo" may not be recognized. Using "array" alongside it or using "el array" directly is safer. The simplest fix is to add the English term in parentheses on first use: "el arreglo `@context`" is fine if followed by "(array)" for clarity, or simply use "la lista `@context`" which is universally understood.
**Alternative:** "en la lista `@context`"

---

**Line 91 — Current:** "El vocabulario crece a través del uso en el mundo real, no del diseño por comité."
**Issue:** "Diseño por comité" is a calque of "committee design." The phrase is widely understood in technical circles but the more natural Spanish rendering would be "del diseño a cargo de comités" or simply "del diseño en comité."
**Proposed:** "El vocabulario crece a través del uso en el mundo real, no del diseño en comité."
**Rationale:** "Por comité" as a preposition phrase modifying "diseño" is an anglicism. "En comité" is the standard Spanish prepositional construction for describing committee-based processes.
