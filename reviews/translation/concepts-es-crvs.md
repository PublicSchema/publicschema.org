# Spanish translation review: CRVS concepts

Files reviewed: schema/concepts/adoption.yaml, annulment.yaml, birth.yaml,
certificate.yaml, civil-status-annotation.yaml, civil-status-record.yaml,
crvs-person.yaml, death.yaml, divorce.yaml, family-register.yaml,
fetal-death.yaml, legitimation.yaml, marriage.yaml, marriage-termination.yaml,
parent.yaml, paternity-recognition.yaml, vital-event.yaml

---

## adoption.yaml

**Issue 1**

- Current: `estatus de progenitores de un niño o niña`
- Source: `acquire the status of parent to a child`
- Issue: "estatus" is an anglicism. In legal Spanish, "condición" or "calidad" is standard ("calidad de progenitor" is the common legal formula in Spanish civil codes).
- Proposed: `la calidad de progenitores de un niño o niña`
- Rationale: "Calidad de progenitor" appears in Spanish, Mexican, and Colombian civil codes. "Estatus" reads as borrowed from English in a legal context.

**Issue 2**

- Current: `creando una relación paterno-filial`
- Source: `creating a parent-child relationship`
- Issue: "paterno-filial" is not wrong, but it has a masculine bias ("paterno" literally means fatherly). The standard neutral legal term is "relación paternofilial" or, more precisely, "relación de filiación". Since this covers adoptions involving two mothers or two fathers, "relación de filiación" is more accurate and inclusive.
- Proposed: `creando una relación de filiación`
- Rationale: "Filiación" is the canonical civil-law term used in the Hague Convention Spanish text and in Spanish, Mexican, Argentine, and Colombian civil codes for the legal parent-child bond regardless of gender.

**Issue 3**

- Current: `el Convenio de La Haya sobre adopción internacional`
- Source: `the Hague Convention on Intercountry Adoption`
- Issue: The official Spanish title of the treaty is "Convenio de La Haya relativo a la Protección del Niño y a la Cooperación en materia de Adopción Internacional". The shortened form most often seen in official documents is "Convenio de La Haya sobre Adopción Internacional". The current text is accurate enough as a short reference, but "adopción internacional" is lowercase here where it follows "sobre", which is correct. No action needed on capitalisation. The term itself is fine.
- No change required.

---

## annulment.yaml

No issues worth flagging.

---

## birth.yaml

**Issue 1**

- Current: `la expulsión o extracción completa del producto de la concepción del cuerpo de la madre`
- Source: `the complete expulsion or extraction of a product of conception from its mother`
- Issue: "del cuerpo de" is an addition not in the English. It is not wrong, but comparing with the WHO/UN Recommendations Spanish text, the standard formulation is simply "del seno de la madre" or "fuera del cuerpo de la madre". The French also uses this pattern ("hors du corps de la mère"). Consistency with the official UN/WHO Spanish text is preferable.
- Proposed: `la expulsión o extracción completa del producto de la concepción fuera del cuerpo de la madre`
- Rationale: The UN Principles and Recommendations for Vital Statistics (Spanish edition) uses "fuera del cuerpo de la madre". The current "del cuerpo de" reads like "from the body of", which could be parsed ambiguously. "Fuera del cuerpo de la madre" mirrors the source preposition "from" unambiguously.

**Issue 2**

- Current: `Captura al niño o niña, a los padres y los atributos utilizados por el registro civil y las estadísticas vitales`
- Source: `Captures the child, the parents, and attributes used by civil registration and vital statistics`
- Issue: "estadísticas vitales" is a correct calque, but in standard Spanish-language CRVS literature (UN, CELADE, OPS) the field is called "estadísticas vitales" or "estadísticas del registro civil". This is acceptable. However, "Captura" is a direct calque of the English technical verb "captures". In plain Spanish for a policy audience, "Recoge" or "Incluye" is more natural.
- Proposed: `Recoge al niño o niña, a los padres y los atributos utilizados por el registro civil y las estadísticas vitales`
- Rationale: "Captura" in Spanish primarily means to arrest or capture a person or signal; using it to mean "records/includes data fields" is an English calque that sounds jarring to a Spanish-speaking civil registrar. "Recoge" (collects, captures in the informational sense) is natural in this context. The same verb is used in crvs-person.yaml ("Lleva") and should be made consistent across files if possible.

---

## certificate.yaml

**Issue 1**

- Current: `emitiendo un extracto de un acta conservada en el país de origen`
- Source: `issuing an extract of a record held in the country of origin`
- Issue: "emitiendo" is a present participle used as a reduced relative clause. In standard Spanish, the present participle is not used in this way to modify a noun phrase; it is restricted in Spanish grammar to expressing an action simultaneous with the main verb's subject. The correct construction is a relative clause.
- Proposed: `que emite un extracto de un acta conservada en el país de origen`
- Rationale: Spanish grammar does not allow a free-standing present participle as an English-style modifier ("an embassy issuing" = "una embajada que emite"). This is a recurring gallicism/anglicism pattern. The French text uses the same pattern ("une ambassade délivrant"), but French allows this; Spanish does not.

**Issue 2**

- Current: `Un documento emitido a partir de un acta de estado civil o un evento vital que acredita el evento para uso externo`
- Source: `A document issued from a civil status record or vital event that attests to the event for external use`
- Issue: The relative clause "que acredita el evento" is ambiguous: it could attach to "acta de estado civil o un evento vital" rather than to "Un documento". The original English is equally structured but less ambiguous because "issued from X" separates cleanly. In Spanish the sentence would benefit from a small restructuring.
- Proposed: `Un documento emitido a partir de un acta de estado civil o de un evento vital, que acredita dicho evento para uso externo`
- Rationale: Adding "de un" before "evento vital" and inserting a comma plus "dicho" makes the antecedent of "que acredita" unambiguous.

---

## civil-status-annotation.yaml

**Issue 1**

- Current: `Ejemplos incluyen`
- Source: `Examples include`
- Issue: "Ejemplos incluyen" is a calque of the English construction. In Spanish, the verb must agree with the subject but the construction "Ejemplos incluyen" without an article is not standard. The natural Spanish phrasing is "Entre los ejemplos se encuentran" or, more simply, "Por ejemplo:".
- Proposed: `Entre los ejemplos se encuentran:`
- Rationale: Spanish requires either an article ("Los ejemplos incluyen") or a restructuring. The article-less construction with verb directly following is an anglicism. A colon-introduced list is standard in Spanish definitions.

**Issue 2**

- Current: `una corrección ordenada por tribunal`
- Source: `a court-ordered correction`
- Issue: "Ordenada por tribunal" without an article is unusual in Spanish. Either "ordenada por un tribunal" (indefinite, one specific tribunal) or "ordenada judicialmente" is more natural.
- Proposed: `una corrección ordenada por un tribunal`
- Rationale: Dropping the article before "tribunal" is a direct calque of English's zero article. Spanish requires the indefinite article here.

---

## civil-status-record.yaml

**Issue 1**

- Current: `a demanda`
- Source: `on demand`
- Issue: "A demanda" is used in legal Spanish but can sound strange to readers outside Spain or the Southern Cone. The more universally understood phrase is "a solicitud" or "cuando se solicitan".
- Proposed: `a solicitud`
- Rationale: "A solicitud" is the standard neutral phrase used in UN/CELADE documentation and Spanish-language civil registration manuals across LatAm. "A demanda" is grammatically correct but less commonly encountered outside Spain.

---

## crvs-person.yaml

**Issue 1**

- Current: `pero congeladas en el momento del evento en lugar de reflejar valores actuales`
- Source: `but frozen at event time rather than reflecting current values`
- Issue: "Congeladas" is a calque of "frozen". In this administrative context, "fijadas" or "registradas" is more natural. "Congeladas" evokes food preservation or asset freezing, not data capture.
- Proposed: `pero fijadas en el momento del evento, en lugar de reflejar los valores actuales`
- Rationale: "Fijadas" conveys the sense of "fixed in time" without the frozen-food connotation. Adding a comma before "en lugar de" improves readability.

**Issue 2**

- Current: `Se utiliza en cualquier lugar donde un evento vital necesite registrar quién era una persona`
- Source: `Used wherever a vital event needs to record who a person was`
- Issue: "En cualquier lugar donde" is a literal translation of "wherever" in the locative sense. Here the meaning is logical/contextual, not spatial, so it reads awkwardly. The standard Spanish formulation is "En todos los casos en que" or "Siempre que".
- Proposed: `Se utiliza siempre que un evento vital necesite registrar quién era una persona`
- Rationale: "Siempre que" is the natural equivalent of "wherever" used in the non-spatial sense of "in any case where".

---

## death.yaml

**Issue 1**

- Current: `La desaparición permanente de toda evidencia de vida en cualquier momento tras haber ocurrido un nacimiento vivo`
- Source: `The permanent disappearance of all evidence of life at any time after a live birth has taken place`
- Issue: "Evidencia" is a false friend in this context. In Spanish, "evidencia" means proof or evidence (legal sense), not the observable presence of life. The official WHO/UN Spanish text uses "señales de vida" or "toda manifestación de vida". "Evidencia" reads as an anglicism.
- Proposed: `La desaparición permanente de toda manifestación de vida en cualquier momento tras haber ocurrido un nacimiento vivo`
- Rationale: The WHO definition (Spanish version) and UN Principles and Recommendations use "manifestación de vida" or "signos de vida". "Evidencia" is a common anglicism in Latin American Spanish but inappropriate in formal WHO-aligned CRVS text.

---

## divorce.yaml

**Issue 1**

- Current: `La disolución de un matrimonio válido mediante sentencia judicial o resolución administrativa. Distinto de la Anulación`
- Source: `The dissolution of a valid marriage by judicial or administrative decree. Distinct from Annulment`
- Issue: "Distinto" (masculine) does not agree with "La disolución" (feminine). The subject implied is "El divorcio" or the concept itself, but the opening sentence is feminine ("La disolución"). This is a gender agreement error.
- Proposed: `La disolución de un matrimonio válido mediante sentencia judicial o resolución administrativa. Distinta de la Anulación`
- Rationale: The adjective should agree with the implicit referent. Since the definition of the concept Divorce is expressed as a feminine noun phrase ("La disolución"), the predicate adjective must be "Distinta". The French uses "Distincte" (feminine) correctly.

---

## family-register.yaml

**Issue 1**

- Current: `Los miembros se alcanzan a través de la Familia vinculada`
- Source: `Members are reached through the linked Family`
- Issue: "Se alcanzan a través de" is a literal translation of "are reached through". In Spanish technical documentation, the natural phrase is "se accede a los miembros a través de" or "los miembros se acceden a través de". The English "reached" is a technical metaphor (graph traversal); in Spanish for a policy audience the clearest equivalent is "se accede".
- Proposed: `Se accede a los miembros a través de la Familia vinculada`
- Rationale: "Alcanzar" in Spanish means to reach physically or to attain a goal. "Acceder" is the standard verb for navigating to linked data or related records in administrative/registry contexts.

**Issue 2**

- Current: `libreta de familia en Francia`
- Source: `livret de famille in France`
- Issue: The French document is called "livret de famille". The Spanish equivalents vary by country: "libreta de familia" (Spain, historical), "libro de familia" (Spain, current standard). Neither is a direct translation error, but "libro de familia" is the more widely recognised term in Spanish-speaking countries that have an equivalent document, and in UN documentation on the topic.
- Proposed: `libro de familia en Francia`
- Rationale: "Libro de familia" is the term used in Spanish civil registration law and UN comparative documentation. "Libreta de familia" is understood but is less standard.

---

## fetal-death.yaml

No issues worth flagging. The text uses "muerte fetal", "CIE-PM", "edad gestacional" correctly. "Con independencia de" is a sound choice over "independientemente de" for formal register. "Abortos espontáneos" is the correct neutral term for miscarriages.

---

## legitimation.yaml

**Issue 1**

- Current: `generalmente tras el matrimonio posterior de los progenitores biológicos`
- Source: `typically following the subsequent marriage of the biological parents`
- Issue: No error. "Progenitores biológicos" is precise and correct. "Generalmente" for "typically" is fine.
- No change required.

**Issue 2**

- Current: `Relevante en jurisdicciones en las que el estatus del menor aún varía según el contexto marital`
- Source: `Relevant in jurisdictions where the status of the child still varies by marital context`
- Issue: "Estatus" is the anglicism noted in adoption.yaml. Here it refers to the child's legal standing. "Condición jurídica" is standard.
- Proposed: `Relevante en jurisdicciones en las que la condición jurídica del menor aún varía según el contexto marital`
- Rationale: Consistent with the "estatus" / "condición" note above. "Condición jurídica" is the phrase used in Spanish civil codes and international family law instruments.

---

## marriage.yaml

**Issue 1**

- Current: `Tratado como un evento vital y no como una relación permanente`
- Source: `Treated as a vital event rather than a standing relationship`
- Issue: "Tratado" (masculine) does not agree with "La unión legal" (feminine) established in the opening sentence. The implicit subject is "El matrimonio" but the sentence structure implies a continuation of the subject "La unión". This is the same gender agreement problem seen in divorce.yaml.
- Proposed: `Tratada como un evento vital y no como una relación permanente`
- Rationale: "Tratada" agrees with the feminine noun subject carried through the definition. The French text uses "Traité" (masculine, agreeing with "mariage"), which is consistent internally. The Spanish opens with "La unión" (feminine), so "Tratada" is correct.

---

## marriage-termination.yaml

**Issue 1**

- Current: `La defunción de un cónyuge pone fin al matrimonio pero se registra como una Defunción, no como una MarriageTermination`
- Source: `Death of a spouse ends the marriage but is recorded as a Death, not a MarriageTermination`
- Issue: Keeping "MarriageTermination" untranslated in the middle of an otherwise Spanish sentence is inconsistent. Annulment is translated as "Anulación", Divorce as "Divorcio", Death as "Defunción". "MarriageTermination" should either be translated here or at least followed by a clarifying phrase. The English source does keep the identifier, but in a Spanish text aimed at policy officials, the untranslated concept name breaks register.
- Proposed: `La defunción de un cónyuge pone fin al matrimonio pero se registra como una Defunción, no como una Terminación de matrimonio (MarriageTermination)`
- Rationale: Other concept names in the CRVS cluster are translated inline (e.g., "Divorcio", "Anulación", "Defunción"). Keeping one concept in English only is inconsistent and will read oddly to a policy audience. Parenthetical form preserves the identifier for technical readers.

---

## parent.yaml

**Issue 1**

- Current: `Utilizada en Nacimiento, Adopción, Reconocimiento de paternidad y Legitimación para que la filiación biológica y la jurídica puedan representarse de forma explícita en lugar de colapsarse en un único campo de progenitor`
- Source: `Used on Birth, Adoption, PaternityRecognition, and Legitimation so that biological and legal parentage can be captured explicitly rather than collapsed into a single parent slot`
- Issue: "Colapsarse en un único campo de progenitor" is a calque of "collapsed into a single parent slot". In Spanish administrative writing, "concentrarse en un único campo" or "reducirse a un único campo" is more natural. "Colapsarse" carries the sense of collapsing structurally (like a building collapsing) rather than merging data fields.
- Proposed: `en lugar de reducirse a un único campo de progenitor`
- Rationale: "Reducirse a" is the natural Spanish metaphor for data/information being condensed into a single field. "Colapsarse" is a direct calque and reads as jargon.

---

## paternity-recognition.yaml

**Issue 1**

- Current: `mediante el cual un progenitor, típicamente el padre`
- Source: `in which a parent, typically a father`
- Issue: "Típicamente" is an anglicism. The natural Spanish adverb is "habitualmente" or "por lo general" or "generalmente".
- Proposed: `mediante el cual un progenitor, habitualmente el padre`
- Rationale: "Típicamente" exists in Spanish dictionaries but is marked as a calque and is rarely used in formal legal or administrative writing. "Habitualmente" or "generalmente" carries the same meaning with better register.

**Issue 2**

- Current: `Se efectúa ante un funcionario de registro civil, un notario o un tribunal`
- Source: `Takes place before a registrar, notary, or court`
- Issue: "Funcionario de registro civil" is a reasonable translation of "registrar" in the CRVS sense, but the canonical Spanish term is "oficial del registro civil" or "encargado del registro civil". "Funcionario" is generic (it covers any public official). "Oficial del registro civil" is the term used in Spanish civil codes and international CRVS instruments.
- Proposed: `Se efectúa ante un oficial del registro civil, un notario o un tribunal`
- Rationale: "Oficial del registro civil" is the standard designation used in the Spanish texts of the UN Principles and Recommendations and in the civil codes of Spain, Mexico, Colombia, and Argentina. It is more precise and recognisable to practitioners.

---

## vital-event.yaml

**Issue 1**

- Current: `Alineado con los Principios y Recomendaciones de las Naciones Unidas sobre estadísticas vitales`
- Source: `Aligned with the UN Principles and Recommendations for Vital Statistics`
- Issue: The official title of the document in Spanish is "Principios y Recomendaciones para un Sistema de Estadísticas Vitales" (UN, 2014, Rev. 3). The current translation is a reasonable short form but drops "para un Sistema de" which is part of the official title.
- Proposed: `Alineado con los Principios y Recomendaciones de las Naciones Unidas para un Sistema de Estadísticas Vitales`
- Rationale: Where a document has an official Spanish title, use it. The extra words help practitioners locate the correct reference.

---

## Cross-file consistency issues

1. **"Captura" vs. other verbs.** birth.yaml uses "Captura" (calque of "captures"). death.yaml also uses "Captura". family-register.yaml uses the more natural "da seguimiento" and "expone". A consistent verb should be chosen: "Recoge" works for both birth.yaml and death.yaml.

2. **"Estatus" appearing in adoption.yaml and legitimation.yaml.** Should be "calidad" (legal standing / status as parent) or "condición jurídica" (legal standing of a child) as noted above.

3. **"Distinto/Distinta" agreement.** divorce.yaml uses "Distinto" (wrong) and marriage.yaml uses "Tratado" (wrong). annulment.yaml uses "Distinta" correctly. These should be audited and made consistent.

4. **Concept identifier handling.** marriage-termination.yaml leaves "MarriageTermination" untranslated. Other files translate concept names (Defunción, Anulación, Divorcio). A consistent policy should be applied: either always parenthesise the identifier ("Terminación de matrimonio (MarriageTermination)") or always translate without the identifier. The parenthetical approach is recommended to serve both policy and technical readers.
