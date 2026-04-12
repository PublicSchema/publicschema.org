# Spanish translation review — integration docs

## integration-patterns.md

**Overall impression:** Generally readable and accurate. A few mechanical calques from English weaken the prose, and one parenthetical gloss is redundant given that "credenciales verificables" is already the established term in this document set. The section headings are clean.

### Flagged passages

**Line 3 — Current:** "credenciales verificables (verifiable credentials)"
**Issue:** Redundant gloss. The parenthetical English original adds nothing for a Spanish-speaking audience; "credenciales verificables" is the established term throughout this document set. Carrying the English in parentheses signals distrust in the translation.
**Proposed:** "credenciales verificables"
**Rationale:** The gloss would belong in a first-use glossary footnote if at all, not inline in a flowing sentence where the term has already been adopted.

**Line 30 — Current:** "Valide las cargas útiles de solicitud y respuesta con los esquemas JSON de PublicSchema en el límite de la API."
**Issue:** "límite de la API" is a literal calque of "API boundary." While "límite" is not wrong, "frontera" and "punto de entrada" are more natural in technical Spanish. "límite" here reads like a word-for-word translation.
**Proposed:** "Valide las cargas útiles de solicitud y respuesta con los esquemas JSON de PublicSchema en el punto de entrada de la API."
**Rationale:** "Punto de entrada" is idiomatic in Spanish-language API documentation; "límite" has a more mathematical/spatial feel that sounds odd in this context.

**Line 34 — Current:** "Los suscriptores de diferentes sistemas los consumen sin necesidad de una correspondencia de campos bilateral."
**Issue:** "correspondencia de campos bilateral" is technically correct but reads as a calque of "bilateral field mapping." In natural Spanish, "mapeo bidireccional" or "tabla de equivalencias entre sistemas" would be more idiomatic.
**Proposed:** "Los suscriptores de diferentes sistemas los consumen sin necesidad de un mapeo de campos bilateral."
**Rationale:** "Mapeo" is widely used in technical Spanish across the Americas and Spain for this concept; "correspondencia" is correct but sounds more formal and bureaucratic here than in the other documents where it is used as the primary term. Consistency with "correspondencia" used elsewhere in the doc set is acceptable, but "correspondencia bilateral de campos" is an unusual collocation; at minimum the word order could be improved.

**Line 51 — Current:** "El envoltorio del evento (tipo, marca de tiempo, metadatos de enrutamiento) es suyo."
**Issue:** "es suyo" is grammatically correct but oddly terse for this register. More importantly, "metadatos de enrutamiento" is a calque of "routing metadata"; "metadatos de enrutamiento" is used in some technical contexts but "metadatos de encaminamiento" or just "metadatos de ruta" read more naturally.
**Proposed:** "El envoltorio del evento (tipo, marca de tiempo, metadatos de enrutamiento) corresponde a su implementación."
**Rationale:** "Es suyo" could be misread as possessive ambiguity (whose?); "corresponde a su implementación" clarifies that the envelope is defined by the implementing system, matching the English intent "is yours."

**Line 79 — Current:** "Cualquier sistema con una correspondencia de PublicSchema puede importar el archivo sin análisis sintáctico personalizado."
**Issue:** "análisis sintáctico personalizado" is an overly literal calque of "custom parsing." "Análisis sintáctico" is the Spanish computing term for parsing, but "análisis sintáctico personalizado" in this context sounds awkward. "Procesamiento personalizado" or "transformaciones a medida" conveys the intent more naturally.
**Proposed:** "Cualquier sistema con una correspondencia de PublicSchema puede importar el archivo sin procesamiento personalizado."
**Rationale:** The English "custom parsing" means ad-hoc transformation logic; "procesamiento personalizado" captures this without the linguistic heaviness of "análisis sintáctico."

**Line 86 — Current:** "Sin API, sin infraestructura. Una tabla de correspondencias y un CSV bien nombrado."
**Issue:** "bien nombrado" is a calque of "well-named." In Spanish this sounds incomplete; "con nombres de columna bien definidos" or "correctamente nombrado" is more natural.
**Proposed:** "Sin API, sin infraestructura. Una tabla de correspondencias y un CSV con columnas bien definidas."
**Rationale:** "Bien nombrado" is not wrong, but the CSV's value comes specifically from its column names matching the standard; making that explicit improves both clarity and naturalness.

---

## interoperability-guide.md

**Overall impression:** This is the longest and most technically dense of the five files, and it handles the complexity well overall. The "Piedra de Rosetta" metaphor is well-rendered. There are a handful of calques and one awkward phrase in the challenges section, but the text is largely natural and would read comfortably to a policy practitioner.

### Flagged passages

**Line 3 — Current:** "construcción de intercambios de datos, consolidación de registros de múltiples fuentes o ejecución de canalizaciones ETL"
**Issue:** "ejecución de canalizaciones ETL" is a calque of "running ETL pipelines." "Canalizaciones" for "pipelines" is technically defensible but unusual in Spanish-language data engineering documentation; "flujos ETL" or "procesos ETL" are more widely understood across the region.
**Proposed:** "construcción de intercambios de datos, consolidación de registros de múltiples fuentes o ejecución de procesos ETL"
**Rationale:** "Canalizaciones" is used throughout this document set (see also integration-patterns.md line 3); consistency within the set is more important than replacing it everywhere, but flagging it here as potentially confusing to a general policy audience.

**Line 25 — Current:** "Está construyendo un almacén de datos o panel de control que agrega datos de múltiples fuentes"
**Issue:** "Está construyendo" (twice on lines 25 and 27) uses "estar + gerundio" for second-person address, which is natural. No issue here. However "panel de control" for "dashboard" is Spain-influenced; across Latin America "tablero" or "tablero de control" is more common and neutral.
**Proposed:** "Está construyendo un almacén de datos o tablero que consolida datos de múltiples fuentes"
**Rationale:** "Panel de control" has a hardware/cockpit connotation in many Latin American varieties; "tablero" is the more widely adopted term for a data dashboard in the region.

**Line 33 — Current:** "Sin un referente compartido, conectar N sistemas requiere N*(N-1)/2 correspondencias bilaterales. Con 5 sistemas, son 10 tablas de correspondencia separadas a mantener."
**Issue:** "a mantener" at the end is a calque of "to maintain" used as a postpositive infinitive adjective. This construction is grammatically acceptable in Spanish but sounds slightly bookish; "que hay que mantener" or "para mantener" is more fluid.
**Proposed:** "Con 5 sistemas, son 10 tablas de correspondencia separadas que hay que mantener."
**Rationale:** "Tablas... a mantener" is a Gallicism/calque from French/English infinitive constructions. "Que hay que mantener" is idiomatic and unambiguous.

**Line 62 — Current:** "La descarga **CSV** del concepto le da una lista plana de propiedades con tipos y definiciones, útil como punto de partida para su tabla de correspondencias."
**Issue:** "lista plana" is a calque of "flat list." In natural Spanish, "lista completa" or "listado" works better; "plano" in this sense of "non-hierarchical" is a technical calque that may confuse non-technical readers.
**Proposed:** "La descarga **CSV** del concepto le proporciona un listado de propiedades con tipos y definiciones, útil como punto de partida para su tabla de correspondencias."
**Rationale:** "Lista plana" is understood in technical circles but is not neutral; "listado" carries no risk of misreading.

**Line 95 — Current:** "Consulte el [caso de uso de armonización de APIs](/docs/use-cases/#armonización-de-apis-en-una-federación) para un escenario concreto."
**Issue:** No language issue; the link anchor may not match the English page slug but that is a content/technical issue, not a translation issue. The prose is fine.

**Line 117 — Current:** "Campos que no se mapearon correctamente (tipo incorrecto, contexto requerido faltante)"
**Issue:** "contexto requerido faltante" is a calque of "missing required context." In Spanish, "contexto obligatorio ausente" or "contexto requerido ausente" is more natural; "faltante" as an adjective is used in Latin America but carries a bureaucratic register that jars here.
**Proposed:** "Campos que no se mapearon correctamente (tipo incorrecto, contexto obligatorio ausente)"
**Rationale:** "Faltante" is not wrong, but "ausente" is more standard in this formal written register; "obligatorio" is clearer than "requerido" as a translation of "required."

**Line 125 — Current:** "La fila 1 tiene etiquetas de campo legibles para personas"
**Issue:** "legibles para personas" is a calque of "human-readable." The established Spanish term is "legibles por personas" or simply "legibles" in context; "para personas" sounds like the labels exist in order to be given to people, rather than being readable by people.
**Proposed:** "La fila 1 tiene etiquetas de campo legibles por personas"
**Rationale:** "Legible por personas" (or "legible por humanos") is the standard calque for "human-readable" across Spanish-language technical documentation. The preposition matters.

**Line 166 — Current:** "esto no es solo un inconveniente de correspondencia; es una brecha de información"
**Issue:** "brecha de información" is a reasonable rendering of "information gap," but "pérdida de información" is more precise here since the English specifically says the distinction is *lost*. "Brecha" implies a gap that could be filled; "pérdida" correctly conveys that the distinction cannot be recovered.
**Proposed:** "esto no es solo un inconveniente de correspondencia; es una pérdida de información"
**Rationale:** The surrounding sentences (lines 166-168) explicitly describe losing precision that downstream systems cannot recover. "Pérdida" is semantically tighter.

---

## jsonld-vc-guide.md

**Overall impression:** Well-translated overall. Technical terms are handled consistently. A few minor calques in prose transitions, and one section title uses an unusual construction. The "retroceso" in "comportamiento de retroceso @vocab" is worth reconsidering.

### Flagged passages

**Line 5 — Current:** "Este es uno de varios caminos para usar PublicSchema."
**Issue:** "caminos" for "ways/paths" is a literal calque. "Vías" or "formas" is more natural in formal technical Spanish.
**Proposed:** "Esta es una de las varias formas de usar PublicSchema."
**Rationale:** "Camino" works in metaphorical Spanish but the context here is technical options, not a journey metaphor; "formas" is unambiguous.

**Line 31 — Current:** "Esto hace que sus datos sean legibles por máquina."
**Issue:** "legibles por máquina" is a standard calque of "machine-readable" and is fully established in technical Spanish. No issue.

**Line 154 — Current:** "## Comportamiento de retroceso `@vocab`"
**Issue:** "retroceso" is a calque of "fallback" that means "backward movement" or "setback" in most Spanish varieties. The intended meaning is "fallback behavior" in the programming sense. "Comportamiento por defecto" or "comportamiento de reserva" or "mecanismo de respaldo" are more accurate and natural.
**Proposed:** "## Comportamiento de respaldo de `@vocab`"
**Rationale:** "Respaldo" (backup, fallback) is widely used in Latin American and Spanish technical documentation for the programming concept of fallback. "Retroceso" would lead a Spanish reader to think something goes backwards, which is misleading.

**Line 156 — Current:** "el contexto de PublicSchema declara `\"@vocab\": \"https://publicschema.org/\"`. Esto significa que cualquier clave JSON que no esté explícitamente definida en el contexto se expandirá silenciosamente a `https://publicschema.org/{key}`."
**Issue:** "se expandirá silenciosamente" is a calque of "will silently expand." "Silenciosamente" is not wrong but "sin advertencia" or "sin emitir error" is more idiomatic in Spanish technical documentation for the concept of silent behavior.
**Proposed:** "se expandirá sin advertencia a `https://publicschema.org/{key}`"
**Rationale:** "Sin advertencia" is the standard phrasing for "silently" (i.e., without raising an error or notice) in Spanish-language programming docs.

**Line 162 — Current:** "el nombre con el que la persona prefiere ser llamada"
**Issue:** "ser llamada" is grammatically correct but "ser identificada" or "que prefiere usar" sounds more natural for a name preference in formal Spanish.
**Proposed:** "el nombre con el que la persona prefiere ser identificada"
**Rationale:** "Ser llamada" can work informally but in a formal policy document "ser identificada" better captures the administrative sense of "addressed by."

---

## related-standards.md

**Overall impression:** This is probably the strongest of the five translations. The prose is confident, the metaphors land well, and technical concepts are rendered consistently. Only two passages warrant attention.

### Flagged passages

**Line 30 — Current:** "PublicSchema es el contraparte de modelo de datos"
**Issue:** "contraparte" is masculine ("el contraparte" is used in Latin America, "la contraparte" in Spain) and here it is used as a noun modifier without an article before "de modelo de datos," making the phrase grammatically awkward. "El complemento en el modelo de datos" or "el equivalente en capa de datos" reads more naturally.
**Proposed:** "PublicSchema es el complemento en la capa de modelo de datos"
**Rationale:** "Contraparte" is typically used to mean counterpart in a negotiation or agreement; in this context of architectural layers, "complemento" or "equivalente" is more precise.

**Line 38 — Current:** "Sus tipos de gobierno (GovernmentService, GovernmentOrganization) son extremadamente superficiales y orientados a SEO"
**Issue:** "orientados a SEO" is a mixed-language phrase; "SEO" as an acronym is widely understood, but "orientados a SEO" reads as a calque. "Con fines de SEO" or "enfocados en posicionamiento web" is more natural.
**Proposed:** "Sus tipos de gobierno (GovernmentService, GovernmentOrganization) son extremadamente superficiales y están pensados para el posicionamiento web (SEO)"
**Rationale:** "Orientados a SEO" is an anglicism in construction; "pensados para el posicionamiento web" explains the concept to readers who may not know the acronym while keeping the acronym as a gloss for those who do. This is an audience of policy practitioners, not necessarily SEO specialists.

---

## selective-disclosure.md

**Overall impression:** This is a technically complex document and the translation handles the complexity competently. The vocabulary for SD-JWT concepts (afirmaciones, titular, divulgación) is consistent and well-chosen. There are a few calques in the implementation guidance section and one instance of an anglicism that a native reader would notice.

### Flagged passages

**Line 9 — Current:** "`date_of_birth` en un registro de Persona es dato personal; el mismo campo en una tabla estadística agregada no lo es."
**Issue:** "dato personal" (singular) is slightly unusual; the expected plural "datos personales" is the standard legal and administrative term in Spanish (matching GDPR/RGPD and Latin American data protection law usage).
**Proposed:** "`date_of_birth` en un registro de Persona constituye un dato personal; el mismo campo en una tabla estadística agregada no lo es."
**Rationale:** In data protection law as applied across the Spanish-speaking world, "dato personal" (singular) is actually correct referring to a single datum, but the collocation "constituye un dato personal" sounds more natural than the abrupt "es dato personal" (which drops the article). Both "dato personal" and "datos personales" are used in legal contexts; adding "constituye" resolves the register awkwardness.

**Line 42 — Current:** "manteniendo ocultos `given_name`, `phone_number` y otro PII"
**Issue:** "otro PII" mixes Spanish with the English acronym without translation. PII (Personally Identifiable Information) is not a standard Spanish-language term; the Spanish equivalents are "información de identificación personal" (IIP) or more commonly in legal contexts "datos de carácter personal" or simply "datos personales."
**Proposed:** "manteniendo ocultos `given_name`, `phone_number` y otros datos personales"
**Rationale:** The English source uses "PII" as a technical shorthand, but in a Spanish document aimed at a policy audience, "datos personales" is the appropriate and legally recognized term in all Spanish-speaking jurisdictions.

**Line 95 — Current:** "Los campos posteriores a la redención (redemption_date, redeemed_by) apoyan la auditoría sin requerir una nueva presentación de afirmaciones de identidad."
**Issue:** "sin requerir una nueva presentación" is a calque of "without requiring re-presentation." "Re-presentación" / "nueva presentación" is awkward; "sin necesidad de presentar nuevamente las afirmaciones de identidad" is more idiomatic.
**Proposed:** "Los campos posteriores a la redención (redemption_date, redeemed_by) apoyan la auditoría sin necesidad de presentar nuevamente las afirmaciones de identidad."
**Rationale:** "Nueva presentación" as a nominalized form of "re-presentation" is understandable but sounds translated; the verbal construction with "sin necesidad de" is standard in formal Spanish.

**Line 155 — Current:** "La afirmación `cnf` vincula la credencial a la clave de la persona titular para la prueba de vinculación de clave."
**Issue:** "prueba de vinculación de clave" is a calque of "key binding proof." In Spanish cryptographic documentation, "prueba de posesión de clave" or "prueba de vinculación de clave" are both used, but "vinculación" repeated twice ("vincula... vinculación") in the same sentence creates an awkward echo.
**Proposed:** "La afirmación `cnf` vincula la credencial a la clave de la persona titular como prueba de posesión de clave."
**Rationale:** "Prueba de posesión de clave" avoids the repeated root and is a standard expression in Spanish-language cryptography and digital identity documentation.

**Line 173 — Current:** "Las implementaciones de cartera y verificador deben usar las definiciones de tipos de credencial de este documento para configurar las políticas de divulgación."
**Issue:** "implementaciones de cartera y verificador" is a calque of "wallet and verifier implementations." In Spanish, either "las billeteras digitales y los verificadores" (more natural, using the standard terms) or "las implementaciones de billetera y verificador" reads better. "Cartera" for digital wallet is used in some contexts but "billetera digital" is more widely understood across Latin America for this specific concept.
**Proposed:** "Las billeteras digitales y los verificadores deben usar las definiciones de tipos de credencial de este documento para configurar las políticas de divulgación."
**Rationale:** "Cartera" is used in Spain for wallet and is valid, but in the context of digital identity and credentials, "billetera digital" is the more internationally neutral and recognized term across the Spanish-speaking world. Since this document targets a neutral register, "billetera" is preferable.
