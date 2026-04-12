# Spanish translation review: TermsContent

**Scope:** Review of `TermsContent.es.astro` against `TermsContent.en.astro` -- a terms/licensing page covering CC BY 4.0, Apache 2.0, third-party standards, and attribution guidance.

---

## Flags

---

**Line (approx):** 7

**Current:** `El software que lo construye y sirve está disponible bajo la Licencia Apache.`

**Issue:** "sirve" is a calque of "serves it" (serving web content). In Spanish technical writing, the standard phrasing is "distribuye" or "publica", not "sirve" in this sense.

**Proposed:** `El software que lo genera y distribuye está disponible bajo la Licencia Apache.`

**Rationale:** "Sirve" in the sense of "serving a website" is an anglicism; "distribuye" or "publica" are the natural Spanish equivalents in this context.

---

**Line (approx):** 27

**Current:** `construir sobre el modelo de referencia`

**Issue:** "Construir sobre" is a calque of "build upon." The official Spanish CC BY 4.0 deed uses "crear a partir de."

**Proposed:** `crear a partir del modelo de referencia`

**Rationale:** The Creative Commons official Spanish translation of "build upon" is "crear a partir de" (see https://creativecommons.org/licenses/by/4.0/deed.es). Aligning with the official CC deed wording avoids terminological inconsistency on a legal page.

---

**Line (approx):** 28

**Current:** `remezclar, transformar y construir sobre`

**Issue:** Same calque issue as above. The full official CC Spanish deed phrase for "remix, transform, and build upon" is "mezclar, transformar y crear a partir de."

**Proposed:** `mezclar, transformar y crear a partir del modelo de referencia`

**Rationale:** The CC BY 4.0 official Spanish deed (deed.es) uses "mezclar" (not "remezclar") and "crear a partir de" (not "construir sobre"). Using the official wording is essential on a licensing page.

---

**Line (approx):** 32

**Current:** `debe dar crédito apropiado`

**Issue:** "Crédito apropiado" is a calque of "appropriate credit." The official Spanish CC deed uses "reconocimiento adecuado" (or "crédito de manera adecuada" in some versions), not "crédito apropiado."

**Proposed:** `debe otorgar el reconocimiento adecuado`

**Rationale:** The CC BY 4.0 official Spanish deed renders "give appropriate credit" as "dar crédito de manera adecuada" or "reconocimiento adecuado." "Apropiado" in place of "adecuado" is not incorrect, but the official Spanish deed wording should be preferred on a licensing page.

---

**Line (approx):** 37-38

**Current:** `la canalización de construcción`

**Issue:** "Canalización de construcción" is a direct calque of "build pipeline." Neither word is standard in Spanish technical documentation for this concept.

**Proposed:** `el proceso de compilación y generación`

**Rationale:** "Pipeline de compilación" or "proceso de compilación" are the established Spanish technical terms. "Canalización" is the dictionary translation of "pipeline" (e.g., gas pipeline) but is not used in software contexts; "construcción" for "build" is also uncommon in technical Spanish, where "compilación" or "generación" are standard.

---

**Line (approx):** 54

**Current:** `legibles por máquina`

**Issue:** No issue here; "legible por máquina" is the correct and established Spanish term for "machine-readable." This is fine.

**Proposed:** (No change needed.)

**Rationale:** Included for completeness to confirm this common term is used correctly.

---

**Line (approx):** 84

**Current:** `sobre el licenciamiento o el uso de PublicSchema`

**Issue:** "Licenciamiento" is a valid Spanish word but is less natural and slightly bureaucratic compared to the more direct "sobre las licencias." The CC and Apache communities in Spanish typically say "sobre las licencias" rather than "sobre el licenciamiento."

**Proposed:** `sobre las licencias o el uso de PublicSchema`

**Rationale:** "Licenciamiento" is a legitimate nominalization but "licencias" is the more common and natural form in both Spain and Latin America for questions about licensing terms. It also reduces register formality without losing precision.

---

**Line (approx):** 85

**Current:** `abra un issue`

**Issue:** "Issue" is an English borrowing left untranslated. While it is widely understood by developers, this page also targets policy practitioners who may not recognize the term.

**Proposed:** `abra un reporte` or `abra una solicitud`

**Rationale:** "Issue" in the GitHub sense has no single perfect Spanish equivalent, but "reporte" (Latin America) or "solicitud" are widely understood alternatives. If the audience is strongly developer-focused, "issue" may be acceptable, but the page states its audience includes policy practitioners, so a Spanish term is preferable. Alternatively, the anchor text could be "abra una consulta" to match the heading "Preguntas."

---

## Overall impression

The translation is generally fluent and accurate, and the terminology choices are mostly sound. The most significant problem is that the CC BY 4.0 rights terms ("build upon," "appropriate credit") are translated as calques from English rather than using the wording from the official Spanish CC deed, which is a meaningful inconsistency on a legal page. The "build pipeline" rendering ("canalización de construcción") is also a clear calque that should be replaced with standard Spanish technical vocabulary. A small number of minor anglicisms ("sirve," "licenciamiento," "issue") round out the issues, but none of them impede comprehension.
