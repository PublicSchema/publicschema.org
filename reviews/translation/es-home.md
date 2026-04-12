# Spanish translation review -- HomepageContent

**Scope:** Full homepage (`HomepageContent.es.astro`), hero through "Where to start" personas. Reviewed against English source (`HomepageContent.en.astro`). Target register: neutral international Spanish, formal, CEPAL/OIT-aligned social-protection vocabulary.

---

## Flags

**Flag 1**
- **Line (approx):** 28
- **Current:** `adapte y extienda según el contexto de su país`
- **Issue:** "Extienda" used as a technical imperative (extend a schema) without a complement, which leaves it semantically vague in Spanish; "extiéndalo" or a restructured phrase reads more naturally.
- **Proposed:** `adáptelo y amplíelo según el contexto de su país`
- **Rationale:** "Ampliar" is more natural than "extender" in a schema/standard context when talking to a policy audience; the pronoun anchors the referent (PublicSchema) clearly.

---

**Flag 2**
- **Line (approx):** 32
- **Current:** `Ver cómo los programas usan esto`
- **Issue:** "Usan esto" is a calque of "use this" -- awkward and overly colloquial for a CTA button in a formal document.
- **Proposed:** `Ver casos de uso de programas`
- **Rationale:** Standard CTA phrasing for a policy audience; avoids the demonstrative "esto" dangling at the end of the clause.

---

**Flag 3**
- **Line (approx):** 44-45
- **Current:** `Proporciona definiciones acordadas donde cada concepto tiene peso semántico, no solo estructura.`
- **Issue:** "Acordadas" translates "agreed" literally; in professional Spanish the standard phrase is "definiciones consensuadas" or "definiciones convenidas."
- **Proposed:** `Proporciona definiciones consensuadas en las que cada concepto tiene peso semántico, no solo estructura.`
- **Rationale:** "Definiciones consensuadas" is the established CEPAL/OIT phrasing; "acordadas" reads as a business-meeting anglicism in this register.

---

**Flag 4**
- **Line (approx):** 47-48
- **Current:** `Cada definición recibe un URI estable, listo para usar en Credenciales Verificables.`
- **Issue:** "Credenciales Verificables" with capital letters is fine as a proper noun, but "listo para usar" (singular masculine) is a gender mismatch -- "URI" is generally treated as masculine in Spanish technical writing, but "listo" modifying a participial phrase dangling off the sentence is slightly ungrammatical. More importantly, "para usar" is an infinitive calque; native phrasing prefers "para su uso."
- **Proposed:** `Cada definición obtiene un URI estable, apto para su uso en Credenciales Verificables.`
- **Rationale:** "Obtiene" is more precise than "recibe" here; "apto para su uso" is the natural technical Spanish construction.

---

**Flag 5**
- **Line (approx):** 55
- **Current:** `Entidades como Persona, Inscripción y Pago reciben definiciones claras redactadas para gestores de programas.`
- **Issue:** "Inscripción" as the translation of "Enrollment" is a borderline choice. In social protection, "Enrollment" typically refers to the act of registering a beneficiary in a program; "inscripción" is used in Latin America but "afiliación" (CEPAL usage) or "incorporación" are equally valid and sometimes more precise. However, this is a proper concept name and may be intentional. More concretely, "gestores de programas" is a calque of "program managers" -- the natural Spanish title is "responsables de programas" or "coordinadores de programas."
- **Proposed:** `Entidades como Persona, Inscripción y Pago reciben definiciones claras redactadas para responsables de programas.`
- **Rationale:** "Gestores de programas" is used in Spain but feels mechanical elsewhere; "responsables de programas" is internationally neutral and used consistently in CEPAL and World Bank Spanish documents.

---

**Flag 6**
- **Line (approx):** 71-72
- **Current:** `los referenciamos`
- **Issue:** "Referenciar" is a false cognate of English "to reference" that has become common in technical Spanish but is not standard; the correct verb is "remitir a," "citar," or "hacer referencia a."
- **Proposed:** `los adoptamos` (or `hacemos referencia a ellos` if fidelity to "reference" is required)
- **Rationale:** "Referenciamos" appears twice in the document (also line 208) and is a documented anglicism flagged by the Real Academia Española. In context, the intent is "we point to / align with" those standards, so "adoptamos" or "nos remitimos a ellos" is more accurate and natural.

---

**Flag 7**
- **Line (approx):** 87
- **Current:** `Una madre inscrita en un programa de transferencias monetarias debería calificar automáticamente para un beneficio de salud materno.`
- **Issue:** "Calificar para" is a direct calque of "qualify for." The natural Spanish expression in this domain is "tener derecho a" or "cumplir los requisitos para."
- **Proposed:** `Una madre inscrita en un programa de transferencias monetarias debería tener acceso automático a un beneficio de salud materna.`
- **Rationale:** "Tener acceso automático a" captures the practical meaning (automatic qualification leading to access) and is the phrasing used in CEPAL social protection reports. Note also "salud materno" in the source should be "salud materna" (feminine agreement with "salud").

---

**Flag 8**
- **Line (approx):** 90-91
- **Current:** `La derivación requiere un ejercicio manual de correspondencia que tarda semanas e introduce errores.`
- **Issue:** "Correspondencia" here translates "mapping" in a data/technical sense. In professional social protection Spanish, "mapeo" (though a loanword) is now standard in technical documents (used by CEPAL, World Bank); "correspondencia" reads as an awkward paraphrase. Also "derivación" for "referral" is Spain-coded (particularly in health contexts); "remisión" or "referencia" is more neutral across the region.
- **Proposed:** `La remisión requiere un ejercicio manual de mapeo que puede llevar semanas e introduce errores.`
- **Rationale:** "Remisión" is the neutral cross-regional term for referral between services; "mapeo" is now accepted technical vocabulary in CEPAL and World Bank documents.

---

**Flag 9**
- **Line (approx):** 125-127
- **Current:** `Este es el costo de coordinación: cada vez que dos programas necesitan compartir datos, alguien dedica semanas a mapear campos y traducir códigos. Es costoso, frágil y vuelve a empezar cada vez que un sistema se actualiza.`
- **Issue:** "El costo de coordinación" is a translation of the coined English term "coordination tax." The English is deliberately metaphorical ("tax" as a burden). "Costo" loses the metaphor entirely. This is an acceptable trade-off only if "tax" as metaphor cannot work in Spanish, but "el impuesto de coordinación" or "el peaje de la coordinación" would preserve it. Separately, "vuelve a empezar" for "starts over" is correct but informal; a more formal rendering would be "el proceso se reinicia."
- **Proposed:** `Este es el peaje de la coordinación: cada vez que dos programas necesitan compartir datos, alguien dedica semanas a mapear campos y traducir códigos. Es costoso, frágil y el proceso se reinicia cada vez que un sistema se actualiza.`
- **Rationale:** "El peaje de la coordinación" preserves the metaphorical weight of "tax" (burden, toll) in neutral Spanish; "se reinicia" is appropriately formal.

---

**Flag 10**
- **Line (approx):** 130
- **Current:** `algunas correspondencias no son solo lentas sino que generan pérdida de información`
- **Issue:** "Correspondencias" again for "mappings" (see Flag 8). Consistency with the proposed "mapeo" / "correspondencias de datos" is needed. Also, "generan pérdida de información" is wordy; "son deficitarias" or "conllevan pérdida de información" is tighter.
- **Proposed:** `algunos mapeos no son solo lentos sino que conllevan pérdida de información`
- **Rationale:** Consistency with technical vocabulary used elsewhere; "conllevan" is the standard formal verb for "entail/result in."

---

**Flag 11**
- **Line (approx):** 156
- **Current:** `Correspondencia personalizada por par.`
- **Issue:** Diagram caption. Same "correspondencia" for "mapping" issue (Flag 8). "Por par" is a calque of "per pair" -- natural in Spanish but "entre cada par de sistemas" is clearer in context.
- **Proposed:** `Mapeo personalizado entre cada par de sistemas.`
- **Rationale:** Explicitness helps a non-technical policy reader; consistency with proposed "mapeo" throughout.

---

**Flag 12**
- **Line (approx):** 175
- **Current:** `Cada sistema se mapea una sola vez al vocabulario compartido`
- **Issue:** "Se mapea" is reflexive passive but slightly awkward; "se conecta una sola vez" or "realiza su mapeo una sola vez" is more natural in a diagram caption.
- **Proposed:** `Cada sistema realiza su mapeo una sola vez hacia el vocabulario compartido`
- **Rationale:** Active-voice construction is clearer for a diagram label and avoids the reflexive construction that sounds mechanical.

---

**Flag 13**
- **Line (approx):** 186-187
- **Current:** `bloques de construcción`
- **Issue:** "Building blocks" is a term of art in the GovStack / DPI context. The established Spanish translation used by GovStack themselves and by digital government documents is "bloques funcionales" or "componentes reutilizables," not "bloques de construcción" (which literally means construction/masonry blocks).
- **Proposed:** `bloques funcionales`
- **Rationale:** "Bloques funcionales" is the term used in GovStack's own Spanish materials and by CEPAL in DPI discussions; using a different translation in a document that names GovStack directly creates an inconsistency.

---

**Flag 14**
- **Line (approx):** 197
- **Current:** `PublicSchema se extiende al ciclo de vida de la prestación más allá del nombre y la fecha de nacimiento.`
- **Issue:** "La prestación" translates "delivery" (service delivery) but "prestación" in Spanish primarily means "benefit" (a payment or in-kind transfer), not "delivery" of a service. "Entrega de servicios" or "provisión de servicios" is the correct term for service delivery.
- **Proposed:** `PublicSchema se extiende al ciclo de vida de la provisión de servicios, más allá del nombre y la fecha de nacimiento.`
- **Rationale:** "Prestación" as service delivery is a documented false friend in social protection Spanish; it will be read as "benefit" by a domain expert, introducing semantic confusion.

---

**Flag 15**
- **Line (approx):** 229-231
- **Current:** `Necesita cifras consolidadas, listas de beneficiarios deduplicadas o vías de derivación entre servicios.`
- **Issue:** "Vías de derivación" for "referral pathways." "Derivación" is Spain-coded in health/social services contexts (redirection of a patient). Across Latin America, "mecanismos de referencia y contrarreferencia" or simply "rutas de atención" are used. "Vías de derivación" would be understood but reads as a Peninsular Spanish term.
- **Proposed:** `Necesita cifras consolidadas, listas de beneficiarios deduplicadas o rutas de referencia entre servicios.`
- **Rationale:** "Rutas de referencia" is used by PAHO, CEPAL, and ILO in Spanish-language documents on social protection coordination; it is the neutral term across the region.

---

**Flag 16**
- **Line (approx):** 243
- **Current:** `cada otro sistema mapeado se vuelve interoperable`
- **Issue:** "Cada otro" is a direct calque of "every other" (meaning "each additional one"), but "cada otro" in Spanish most naturally means "every second one" (alternating). The correct expression for "every other mapped system" in the intended sense is "cualquier otro sistema mapeado" or "todos los demás sistemas mapeados."
- **Proposed:** `todos los demás sistemas mapeados se vuelven interoperables`
- **Rationale:** "Cada otro" is a systematic false-friend calque that changes the meaning; this is a genuine comprehension risk, not a style preference.

---

**Flag 17**
- **Line (approx):** 268-269
- **Current:** `para que las divergencias sean visibles y nombrabiles`
- **Issue:** "Nombrabiles" does not exist in standard Spanish. The English "nameable" has no direct equivalent; the correct adaptation is "identificables" or "describibles" or the phrase "puedan ser identificadas y descritas."
- **Proposed:** `para que las divergencias sean visibles e identificables`
- **Rationale:** "Nombrabiles" is a nonce word formed by direct morphological calque; it will read as an error to any native speaker.

---

**Flag 18**
- **Line (approx):** 269-270
- **Current:** `le ofrece una cuadrícula común contra la cual mapear`
- **Issue:** "Cuadrícula" means a grid in the visual/cartographic sense (graph paper, coordinate grid). The English "common grid" is used metaphorically to mean a shared framework or reference matrix. "Marco de referencia común" or "matriz de comparación común" is the natural Spanish equivalent in this analytical context.
- **Proposed:** `le ofrece un marco de referencia común sobre el cual realizar el mapeo`
- **Rationale:** "Cuadrícula" for a conceptual/analytical framework is a visual calque that will confuse readers; the analytical meaning requires "marco" or "matriz."

---

**Flag 19**
- **Line (approx):** 279
- **Current:** `códigos de focalización por variables proxy`
- **Issue:** "Variables proxy" is an anglicism. In CEPAL and World Bank Spanish social protection literature, the established term is "variables indirectas" or "indicadores sustitutos" (though "indicadores proxy" appears increasingly). The phrase "focalización por variables proxy" is intelligible in technical circles but "focalización mediante indicadores indirectos" or "focalización por aproximación" (PMT-based targeting) is more neutral.
- **Proposed:** `códigos de focalización mediante indicadores indirectos`
- **Rationale:** "Variables proxy" is an anglicism; while common in technical documents, "indicadores indirectos" is the neutral preferred form in CEPAL and ILO Spanish publications.

---

## Overall impression

The translation is largely functional and accurate at the propositional level, and there are genuine strengths: the usted register is correctly maintained throughout, the macro-structure mirrors the source cleanly, and most domain-specific terms are handled competently. However, the text shows a consistent pattern of structural calques (especially "cada otro," "cuadrícula," "nombrabiles," "calificar para") and terminology inconsistencies ("correspondencia" vs. "mapeo," "derivación" vs. "remisión/referencia," "prestación" as delivery vs. benefit) that would be immediately noticeable to a domain expert reader at CEPAL, the World Bank, or a national social protection ministry. Flag 17 ("nombrabiles") is an outright error that must be fixed. The text needs targeted polish across roughly 10-12 passages before it is shippable; it does not need to be redone from scratch.
