# Spanish translation review — guides docs

## data-model-guide.md

**Overall impression:** The translation is solid overall and reads naturally for the most part. The register is correctly formal (usted, third-person plural). There are a handful of calques from English, a few awkward noun-phrase constructions, and one vocabulary choice that leans toward Spain usage. Nothing severe, but the flagged items would noticeably improve the document for a Latin American audience.

### Flagged passages

**Line 3 — Current:** "Esta guía es para equipos que construyen un nuevo sistema [...] y desean que sea interoperable desde el inicio. En lugar de adaptar la compatibilidad después, usted diseña su modelo de datos usando PublicSchema como referencia."
**Issue:** Register inconsistency. The opening two sentences use third-person plural ("equipos que construyen", "desean"), then the second sentence switches abruptly to "usted diseña". The shift is jarring; the whole document should stay with usted (or drop the subject pronoun entirely, which is natural in Spanish).
**Proposed:** "En lugar de adaptar la compatibilidad después, diseñe su modelo de datos usando PublicSchema como referencia."
**Rationale:** The imperative or a consistent usted construction is more natural here. The jarring subject pronoun "usted" mid-sentence reads like a translated English "you."

---

**Line 34 — Current:** "Su tabla 'beneficiario' se corresponde claramente con el concepto Persona (Person) de PublicSchema, aunque usted lo llame de otra forma internamente."
**Issue:** Calque / awkward pronoun. "aunque usted lo llame" is a direct calque of "even if you call it." In Spanish the reflexive pronoun is sufficient; "usted" is redundant and sounds stilted.
**Proposed:** "Su tabla 'beneficiario' se corresponde claramente con el concepto Persona (Person) de PublicSchema, aunque internamente lo llame de otra forma."
**Rationale:** Dropping "usted" and moving "internamente" forward is more natural. Spanish does not need the explicit subject pronoun unless there is contrastive emphasis.

---

**Line 67 — Current:** "diseñe su esquema para soportar eso (p. ej., una tabla separada o un campo de arreglo)."
**Issue:** Anglicism. "campo de arreglo" is a literal translation of "array field" that is not standard in Spanish technical writing. "Array" is widely understood as-is, or "campo de tipo arreglo / campo matricial" could be used, but the most natural phrasing simply uses "arreglo" as a loanword or restructures.
**Proposed:** "diseñe su esquema para soportarlo (por ejemplo, una tabla separada o un campo de tipo arreglo)."
**Rationale:** "campo de arreglo" as a noun phrase is an English calque. "campo de tipo arreglo" is slightly more natural. Also, "eso" as a pronoun antecedent for the whole preceding clause is fine, but "soportarlo" reads more fluidly here.

---

**Line 75 — Current:** "Si debe usar códigos internos diferentes (p. ej., su base de datos usa claves foráneas enteras), mantenga una tabla de búsqueda que mapee sus códigos a los canónicos."
**Issue:** Calque / register. "claves foráneas" is a direct calque of "foreign keys." The standard term in Spanish database contexts across Latin America is "claves externas" or "claves foráneas" (both are used, so this is borderline acceptable), but "enteras" (integer) placed after "foráneas" without a connector is syntactically clunky: "claves foráneas enteras" reads as foreign keys that are integer-valued, which is correct in meaning but awkward. Additionally, "que mapee" is a calque of "that maps"; "que relacione" or "que vincule" is more natural Spanish.
**Proposed:** "Si debe usar códigos internos diferentes (p. ej., su base de datos usa claves numéricas enteras), mantenga una tabla de correspondencia que vincule sus códigos a los canónicos."
**Rationale:** "tabla de correspondencia" (already used elsewhere in the document) is more consistent than mixing "tabla de búsqueda"/"tabla de correspondencias". "que vincule" avoids the anglicism "mapear/mapee."

---

**Line 81 — Current:** "Su sistema casi con certeza necesitará campos que PublicSchema no define. Eso es esperado y está bien."
**Issue:** Calque. "Eso es esperado" is a direct calque of "That is expected." The natural Spanish equivalent would be "Es algo normal" or "Eso es lo esperado y no es ningún problema" or simply restructuring.
**Proposed:** "Su sistema casi con certeza necesitará campos que PublicSchema no define. Eso es perfectamente normal."
**Rationale:** "Eso es esperado" is grammatically valid but reads as translated English. "Es perfectamente normal" or "es de esperar" are idiomatic and carry the same reassuring tone.

---

**Line 94 — Current:** "las formas SHACL proveen validación de restricciones para todos los conceptos."
**Issue:** Calque. "proveen" as a translation of "provide" in this technical context is acceptable but slightly formal-bureaucratic. More importantly, "validación de restricciones" is a clunky calque of "constraint validation." Throughout the document the heading uses "Formas SHACL" (line 94), which is also odd: "formas" for "shapes" is understandable but "perfiles" or simply "SHACL shapes" (leaving the technical term untranslated, as is done in the table on line 150) would be more consistent and natural.
**Proposed (inline text):** "los perfiles SHACL permiten la validación de restricciones para todos los conceptos."
**Rationale:** "Perfiles" or "formas" for "shapes" — the document is inconsistent: the heading says "Formas SHACL" but the table at line 150 says "Formas SHACL" again. Either commit to "formas SHACL" or "SHACL shapes" throughout; mixing is confusing. "Permiten" is more natural than "proveen."

---

**Line 95 — Current:** "Si sus datos exportados pasan la validación, su esquema es compatible."
**Issue:** No issue here; this is fine.

---

**Line 105 — Current:** "puede entregar a los proveedores una Plantilla Excel y pedirles que demuestren que su sistema puede producir una exportación conforme."
**Issue:** Calque. "exportación conforme" is a calque of "conforming export." In Spanish, "exportación que cumpla con los requisitos" or "exportación válida" or "exportación compatible" would be more natural.
**Proposed:** "puede entregar a los proveedores una Plantilla Excel y pedirles que demuestren que su sistema puede producir una exportación compatible."
**Rationale:** "Conforme" is not wrong, but "compatible" is already used as the key term throughout this document and is more idiomatic in this context.

---

**Line 119 — Current:** "La acotación temporal es de primer nivel"
**Issue:** Calque. "De primer nivel" is a calque of "first-class" (as in "first-class citizen" in software). This idiom does not exist in Spanish in this technical sense. The English original says "Time-boundedness is first-class."
**Proposed:** "La acotación temporal es un elemento central"
**Rationale:** "De primer nivel" will confuse Spanish-speaking practitioners who do not read the English source. "Un elemento central" or "un concepto fundamental" communicates the same idea in natural Spanish.

---

**Line 133 — Current (table cell):** "Libro de trabajo de múltiples hojas con metadatos, propiedades y vocabularios de referencia en EN/FR/ES"
**Issue:** Minor. "Libro de trabajo" is the standard translation for "workbook" and is fine. No issue.

---

**Line 143 — Current (table cell):** "Acceso legible por máquina"
**Issue:** Calque. "Legible por máquina" is a calque of "machine-readable." The standard Spanish term is "legible por máquina" (widely used in ISO/UN documents), so this is actually acceptable. No change needed.

---

**Line 144 — Current (table cell):** "Población de tablas de búsqueda en su base de datos"
**Issue:** Calque. "Población" as a translation of "seeding" (as in seeding lookup tables) is a calque that most practitioners will not recognize in this context. "Seeding" a database means initially populating it; "población" technically works but "carga inicial" or "carga" is more natural.
**Proposed:** "Carga inicial de tablas de búsqueda en su base de datos"
**Rationale:** "Carga inicial" is the standard term in database contexts across Latin America for the initial population of a table.

---

## vocabulary-adoption-guide.md

**Overall impression:** This is the cleanest of the three files. The register is consistent throughout, the vocabulary is appropriate, and the structure translates naturally. A few minor issues worth flagging, but none are severe.

### Flagged passages

**Line 3 — Current:** "El beneficio: sus datos se vuelven comparables con cualquier otro sistema que haga lo mismo."
**Issue:** Minor calque / punctuation structure. The colon after "El beneficio" mimics the English source ("The payoff:") and creates a slightly abrupt appositive that is not common in Spanish prose. The word "beneficio" is a mild calque of "payoff" — "payoff" in this context has a connotation of reward for effort; "beneficio" is fine, but "ventaja" or "resultado" would feel more idiomatic.
**Proposed:** "La ventaja es clara: sus datos se vuelven comparables con cualquier otro sistema que haga lo mismo."
**Rationale:** "La ventaja es clara:" flows more naturally than the English-derived fragment. Alternatively, this is a borderline case and could be left as-is.

---

**Line 24 — Current:** "Quiere un avance rápido antes de comprometerse con una integración más profunda"
**Issue:** Calque. "Avance rápido" is a calque of "quick win." In Spanish, "logro rápido" or "resultado rápido" would be more natural. "Avance rápido" sounds more like "fast forward" or "rapid progress" than "a quick, early win."
**Proposed:** "Quiere obtener un resultado concreto rápidamente antes de comprometerse con una integración más profunda"
**Rationale:** "Quick win" is a business-English idiom that doesn't translate directly. The proposed version conveys the same idea in plain Spanish.

---

**Line 73 — Current:** "Su sistema podría tener un código donde PublicSchema tiene varios. Por ejemplo, su sistema podría usar 'inactive' tanto para inscripciones 'suspended' como 'completed'. Documéntelas y decida cómo manejarlas."
**Issue:** Pronoun antecedent ambiguity. "Documéntelas" — the "las" refers to the correspondencias (mappings), but that noun hasn't appeared in this sentence. The sentence before talks about "un código" and "inscripciones." The antecedent of "las" is unclear.
**Proposed:** "Documente estas situaciones y decida cómo manejarlas."
**Rationale:** Making the antecedent explicit removes the ambiguity.

---

**Line 87 — Current:** "En todos los casos, su sistema interno continúa usando sus propios códigos. La correspondencia se aplica en el límite."
**Issue:** Calque. "En el límite" is a calque of "at the boundary" (a software architecture concept). This will be opaque to non-technical readers and even many technical readers unfamiliar with English-language architecture docs.
**Proposed:** "En todos los casos, su sistema interno continúa usando sus propios códigos. La correspondencia se aplica únicamente en el punto de intercambio."
**Rationale:** "En el punto de intercambio" or "en la capa de intercambio" conveys the same meaning without requiring the reader to import the English idiom "at the boundary."

---

**Line 95 — Current:** "Cifras comparables entre sistemas. '¿Cuántas inscripciones activas?' significa lo mismo en todos lados."
**Issue:** Minor. "En todos lados" is informal; "en todos los sistemas" or "en cualquier sistema" would be more precise and consistent with the formal register of the document.
**Proposed:** "'¿Cuántas inscripciones activas?' significa lo mismo en cualquier sistema."
**Rationale:** "En todos lados" is colloquial. The formal register used throughout warrants "en cualquier sistema" or "en todos los sistemas."

---

**Line 98 — Current:** "Si más adelante desea alinear nombres de campo, adoptar esquemas JSON o emitir credenciales, la correspondencia de vocabulario ya está hecha."
**Issue:** No issue. This is natural and clear.

---

**Line 113 — Current (table cell):** "Hojas de cálculo, canalizaciones de datos, referencia rápida"
**Issue:** Calque. "Canalizaciones de datos" is a calque of "data pipelines." This is a borderline case — "canalizaciones" is used in some Spanish-language technical documentation, but "flujos de datos" or "procesos de datos" is more widely understood across the Spanish-speaking world, and "pipelines de datos" (untranslated) is also common in technical contexts.
**Proposed:** "Hojas de cálculo, flujos de datos, referencia rápida"
**Rationale:** "Flujos de datos" is more universally understood than "canalizaciones de datos."

---

**Line 114 — Current (table cell):** "Acceso programático, cadenas de herramientas RDF"
**Issue:** Calque. "Cadenas de herramientas" is a calque of "toolchains." "Ecosistemas RDF" or "herramientas RDF" or simply "entornos RDF" would be more natural. "Cadena de herramientas" is intelligible but sounds translated.
**Proposed:** "Acceso programático, entornos de herramientas RDF"
**Rationale:** "Entornos RDF" or "herramientas RDF" avoids the awkward compound noun that is a direct calque from English.

---

## use-cases.md

**Overall impression:** This is the strongest of the three files in terms of natural Spanish. The use-case structure (Quién / El problema / Cómo ayuda / Artefactos clave) translates cleanly and the prose is fluid. The issues are fewer and mostly minor: one awkward calque in the intro, a couple of word choices, and one slightly Spain-coded verb.

### Flagged passages

**Line 3 — Current:** "PublicSchema provee definiciones comunes para la prestación de servicios públicos."
**Issue:** Register / vocabulary. "Provee" as a translation of "provides" is grammatically correct but tends toward bureaucratic register and is less common in Latin America than "ofrece" or "brinda." "Brinda" is neutral and natural across the region. The same verb appears in data-model-guide.md line 94 ("proveen").
**Proposed:** "PublicSchema ofrece definiciones comunes para la prestación de servicios públicos."
**Rationale:** "Ofrece" or "brinda" is more natural than "provee" across Latin America. "Proveer" reads as a slightly formal / Spain-coded calque of "to provide."

---

**Line 22 — Current:** "La base de datos del ministerio de educación los llama 'estudiantes', el sistema de salud los llama 'pacientes' y el sistema de transferencias monetarias los llama 'beneficiarios'."
**Issue:** No issue. Reads naturally.

---

**Line 24 — Current:** "Incluso cuando los campos pueden coincidirse por nombre, los códigos divergentes hacen la comparación poco confiable"
**Issue:** Grammatical calque. "Pueden coincidirse" is not natural Spanish. "Coincidir" is intransitive; "coincidirse" is not standard. The intended meaning is "even when fields can be matched by name."
**Proposed:** "Incluso cuando los campos coinciden en nombre, los códigos divergentes hacen la comparación poco confiable"
**Rationale:** "Coincidir en nombre" or "pueden hacerse coincidir por nombre" (with a reflexive construction) is needed. The simplest fix is "coinciden en nombre."

---

**Line 42 — Current:** "Un organismo coordinador o panel de control gubernamental que agrega datos de múltiples programas"
**Issue:** Minor calque. "Panel de control" for "dashboard" is commonly used but "tablero" or "tablero de control" is more widely natural across Latin America for a government monitoring context. "Panel de control" leans toward Spain-coded computing vocabulary.
**Proposed:** "Un donante, organismo coordinador o tablero gubernamental que agrega datos de múltiples programas"
**Rationale:** "Tablero" or "tablero de control" is the more neutral term for "dashboard" across Latin America. "Panel de control" is more Spain-coded.

---

**Line 43 — Current:** "Agregar cifras entre programas requiere una traducción manual en cada ciclo de reporte. Cuando estas traducciones son imprecisas (porque los códigos de un programa no se corresponden limpiamente con los de otro), los números agregados son poco confiables."
**Issue:** Calque. "Traducciones imprecisas" is used here as a translation of "lossy" (as in "lossy translation" / imperfect mapping). "Imprecisas" is technically correct but "lossy" in this technical sense means "with information loss," not simply "imprecise." Readers may not understand the intended meaning.
**Proposed:** "Cuando estas traducciones son inexactas o incompletas (porque los códigos de un programa no se corresponden limpiamente con los de otro), los números agregados son poco confiables."
**Rationale:** "Inexactas o incompletas" more faithfully captures the English "lossy" without requiring readers to import the technical anglicism.

---

**Line 51 — Current:** "lo cual es demasiado vago para evaluar"
**Issue:** Calque / incomplete. "Demasiado vago para evaluar" is an elliptical calque of "too vague to evaluate." In Spanish the infinitive needs a direct object: "demasiado vago para ser evaluado" or "demasiado vago como para evaluarlo."
**Proposed:** "lo cual es demasiado vago como para evaluarlo."
**Rationale:** In Spanish, the bare infinitive without an implicit subject or object is unnatural here. "Como para evaluarlo" is the standard construction.

---

**Line 83 — Current:** "El sistema de protección social usa el mismo registro para inscribir automáticamente al niño en un subsidio infantil."
**Issue:** No issue. Reads naturally.

---

**Line 85 — Current:** "En el punto de atención, el dispositivo del agente verifica la firma de la credencial y comprueba que enrollment_status es 'active' y que el monto de la prestación es el correcto."
**Issue:** Minor. "El monto de la prestación es el correcto" is slightly awkward. More natural: "el monto de la prestación corresponde al registrado" or "el monto de la prestación es correcto."
**Proposed:** "comprueba que enrollment_status es 'active' y que el monto de la prestación es correcto."
**Rationale:** "Es el correcto" (with the article) is grammatically valid but adds unnecessary emphasis. "Es correcto" reads more cleanly.

---

**Line 105 — Current:** "El resultado hace visibles y nombrables las divergencias"
**Issue:** Calque. "Nombrables" is a calque of "nameable" (as in "visible and nameable divergences"). "Nombrable" is not a natural Spanish adjective in this context. The intended meaning is that the divergences become identifiable / can be explicitly named.
**Proposed:** "El resultado hace visibles las divergencias y permite nombrarlas con precisión"
**Rationale:** "Permite nombrarlas" is more idiomatic than the adjective "nombrables," which reads as a coined translation of an English adjective.

---

**Line 115 — Current:** "simplemente añade una superficie de API alineada con PublicSchema"
**Issue:** Calque. "Superficie de API" is a calque of "API surface" (a software architecture term). While used in some Spanish technical docs, it is not widely understood outside of developer circles, and this document targets a broader audience including policy practitioners.
**Proposed:** "simplemente expone una API compatible con PublicSchema"
**Rationale:** "Exponer una API" is the standard Spanish technical expression for publishing/exposing an API surface. "Superficie de API" will confuse non-developer readers.
