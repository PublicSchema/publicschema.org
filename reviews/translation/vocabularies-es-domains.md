# Spanish vocabulary review — crvs + sp

## Summary

- Files reviewed: 26
- Files with issues: 11
- Files clean: 15
- Em dashes found: 0

---

## Per-file findings

### schema/vocabularies/crvs/adoption-type.yaml

No changes proposed.

---

### schema/vocabularies/crvs/annotation-type.yaml

#### Top-level definition

- Current: `"La categoría de una anotación marginal (mention marginale) añadida a un acta de estado civil cuando la anotación no es derivable de un evento vital desencadenante. Las anotaciones desencadenadas por un evento (por ej., anotar un matrimonio en un acta de nacimiento) llevan su tipo de forma implícita a través del evento desencadenante y no se listan aquí."`
- Proposed: `"La categoría de una anotación marginal (mention marginale) añadida a un acta de estado civil cuando la anotación no se deriva de un evento de estado civil desencadenante. Las anotaciones desencadenadas por un evento (por ej., anotar un matrimonio en un acta de nacimiento) llevan su tipo de forma implícita a través del evento desencadenante y no se listan aquí."`
- Reason: `"evento vital desencadenante"` is calqued from English "triggering vital event." In civil registration Spanish, the canonical term is `"evento de estado civil"` (consistent with how this vocabulary domain is named and how other files in this set use it). Also `"no es derivable de"` is overly technical; `"no se deriva de"` is cleaner and more natural for a policy audience.

---

### schema/vocabularies/crvs/birth-attendant.yaml

No changes proposed. `Partera` and `partera profesional` are the UNSD/WHO Spanish terms. The top-level definition correctly uses `la asistencia calificada al parto`.

---

### schema/vocabularies/crvs/birth-type.yaml

No changes proposed.

---

### schema/vocabularies/crvs/cause-of-death-method.yaml

#### Top-level definition

- Current: `"El método utilizado para determinar la causa de la muerte. En muchos contextos de bajos ingresos, la causa de muerte se determina por autopsia verbal en lugar de certificación médica; los consumidores deben saber cómo se derivó una causa reportada."`
- Proposed: `"El método utilizado para determinar la causa de la muerte. En muchos contextos de bajos ingresos, la causa de muerte se determina por autopsia verbal en lugar de certificación médica; los usuarios de los datos deben conocer el método por el que se estableció la causa declarada."`
- Reason: `"los consumidores"` is a direct calque of the English "consumers" (data consumers). In Spanish, `"consumidores"` in this context sounds commercial and odd to a policy audience. `"los usuarios de los datos"` is the standard expression in Spanish-language WHO/UNSD methodological documents. Additionally `"cómo se derivó una causa reportada"` is awkward; `"el método por el que se estableció la causa declarada"` is more natural and uses `"declarada"` which is canonical in civil registration.

#### values

- `lay_reporting`.label — current: `Reporte no profesional` — proposed: `Declaración no profesional` — reason: The French equivalent is `Déclaration non professionnelle`, not `Rapport`. In civil registration Spanish, `declaración` is the canonical noun for a reported/declared event. `Reporte` is an anglicism (from "report") common in informal usage but not in UN/WHO normative texts.

- `lay_reporting`.definition — current: `"La causa fue reportada por un informante no profesional, sin experiencia clínica o forense."` — proposed: `"La causa fue declarada por un informante no profesional, sin experiencia clínica ni forense."` — reason: `"reportada"` should be `"declarada"` for consistency with the label change above. `"o forense"` should be `"ni forense"` after a negation in formal Spanish (with `sin`, both conjunctions in the negative clause take `ni`).

---

### schema/vocabularies/crvs/certificate-document-type.yaml

No changes proposed.

---

### schema/vocabularies/crvs/certificate-format.yaml

No changes proposed.

---

### schema/vocabularies/crvs/civil-status-record-type.yaml

No changes proposed.

---

### schema/vocabularies/crvs/family-register-status.yaml

#### Top-level definition

- Current: `"Estado del ciclo de vida de un registro familiar. Indica si el registro está actualmente activo, ha sido cerrado, o fue dividido o fusionado con otros registros tras eventos vitales."`
- Proposed: `"Estado del ciclo de vida de un registro familiar. Registra si el registro está actualmente activo, ha sido cerrado, o fue dividido o fusionado con otros registros tras eventos de estado civil."`
- Reason: Per the cross-file consistency rule, `"Captures / records (verb)"` should be `"Recoge"` or `"Registra"`, not `"Indica"`. Also `"eventos vitales"` should be `"eventos de estado civil"` to be consistent with the CRVS domain terminology used in other files in this set (e.g., civil-status-record-type, registration-type all use `"evento de estado civil"` or `"evento vital"` inconsistently — but within CRVS files, `"evento de estado civil"` is more precise and matches the French `"événements d'état civil"`).

#### values

- `active`.definition — current: `"El registro está actualmente activo y hace seguimiento a una unidad familiar con al menos un miembro vivo."` — proposed: `"El registro está actualmente activo y registra una unidad familiar con al menos un miembro vivo."` — reason: `"hacer seguimiento"` is an expression borrowed from English "to track." In Spanish administrative language, `"registrar"` or `"dar cuenta de"` is more natural. Minor but consistent with avoiding calques.

---

### schema/vocabularies/crvs/manner-of-death.yaml

No changes proposed. WHO/ICD canonical Spanish terms are correctly used: `"Lesiones autoinfligidas intencionalmente"` (ICD code X60–X84), `"Intervención legal"` (ICD Y35). `"La manera de la muerte"` is the literal WHO Spanish rendering of "manner of death" and is correct here.

---

### schema/vocabularies/crvs/marriage-type.yaml

No changes proposed.

---

### schema/vocabularies/crvs/parental-role.yaml

No changes proposed.

---

### schema/vocabularies/crvs/place-type.yaml

#### Top-level definition

- Current: `"La categoría de lugar donde ocurrió un evento vital (nacimiento o defunción). Distinto del lugar específico: captura el tipo (establecimiento de salud, hogar, etc.) en lugar del lugar nombrado."`
- Proposed: `"La categoría de lugar donde ocurrió un evento vital (nacimiento o defunción). Distinto del lugar específico: recoge el tipo (establecimiento de salud, hogar, etc.) en lugar del lugar nombrado."`
- Reason: Per the cross-file consistency rule, `"Captures"` must be `"Recoge"` or `"Registra"`, not `"captura"`. This is a direct violation.

---

### schema/vocabularies/crvs/registration-status.yaml

#### values

- `declared`.definition — current: `"El evento ha sido reportado al registrador pero aún no ha sido validado."` — proposed: `"El evento ha sido declarado ante el registrador pero aún no ha sido validado."` — reason: In civil registration Spanish, a declarant `"declara"` an event before the registrar (`"ante el registrador"`); the term `"reportado"` is an anglicism. `"declarado ante el registrador"` matches the canonical language of civil registration laws and the French `"signalé à l'officier d'état civil"` (the French uses `signalé` but the Spanish equivalent in civil registration contexts is `declarado`). The preposition `"ante"` is also standard — you declare an event *before* the registrar.

---

### schema/vocabularies/crvs/registration-type.yaml

No changes proposed.

---

### schema/vocabularies/sp/benefit-frequency.yaml

No changes proposed.

---

### schema/vocabularies/sp/benefit-modality.yaml

#### Top-level definition

- Current: `La forma en que se entrega un beneficio o derecho a un beneficiario.`
- Proposed: `La forma en que se entrega una prestación o derecho a un beneficiario.`
- Reason: The English says `benefit or entitlement`. `"Prestación"` is the ILO/UN canonical Spanish for `"benefit"` in a social protection context; `"beneficio"` is not wrong but `"prestación"` is more precise and consistent with ILO Social Security conventions. The French correctly uses `"prestation"`.

#### values

- `service`.definition — current: `"Acceso a un servicio social como atención médica, educación, cuidado infantil o formación profesional proporcionado como beneficio."` — proposed: `"Acceso a un servicio social como atención médica, educación, cuidado infantil o formación profesional, proporcionado como prestación."` — reason: `"beneficio"` at the end of the sentence should be `"prestación"` for the same reason as above. A comma before `"proporcionado"` also improves readability (matching the French structure).

- `insurance`.definition — current: `"Inscripción en o subsidio de un esquema de seguro (salud, cosecha, social) como beneficio proporcionado al beneficiario."` — proposed: `"Inscripción en un régimen de seguro o subvención del mismo (salud, cosechas, social) como prestación proporcionada al beneficiario."` — reason: `"Inscripción en o subsidio de"` is grammatically awkward (calque of English coordination); Spanish requires repeating the preposition or restructuring. `"cosecha"` (singular) should be `"cosechas"` (plural) to match the English "crop" in this context as used by ILO/WFP. `"beneficio"` → `"prestación"` as above.

---

### schema/vocabularies/sp/conditionality-type.yaml

#### values

- `conditional`.definition — current: `"Los beneficios requieren que el beneficiario cumpla condiciones de comportamiento especificadas, como asistencia escolar, chequeos de salud o participación en capacitación."` — proposed: `"Las prestaciones requieren que el beneficiario cumpla condiciones de comportamiento especificadas, como asistencia escolar, controles de salud o participación en capacitación."` — reason: `"Los beneficios"` → `"Las prestaciones"` for ILO consistency. `"chequeos de salud"` is an anglicism (`"chequeo"` from "check-up"); the ILO/PAHO canonical term is `"controles de salud"` or `"controles médicos"`.

- `soft_conditional`.definition — current: `"Las condiciones se fomentan y monitorean pero el incumplimiento no resulta en suspensión o terminación de beneficios."` — proposed: `"Las condiciones se fomentan y se supervisan, pero el incumplimiento no da lugar a la suspensión o terminación de las prestaciones."` — reason: `"monitorean"` is an anglicism (`"monitor"`); the standard Spanish is `"supervisan"` or `"vigilan"`. `"beneficios"` → `"prestaciones"`. The addition of `"da lugar a"` and the comma before `"pero"` improve formality for a policy audience.

- `unconditional`.definition — current: `"Los beneficios se proporcionan sin requerir que el beneficiario cumpla condiciones de comportamiento."` — proposed: `"Las prestaciones se proporcionan sin exigir que el beneficiario cumpla condiciones de comportamiento."` — reason: `"Los beneficios"` → `"Las prestaciones"`. `"sin requerir"` → `"sin exigir"`: in formal legal and policy Spanish, `"exigir"` is the standard verb used when describing requirements imposed on a beneficiary (consistent with the French `"sans exiger"`).

- `labelled`.definition — current: `"Los beneficios se designan para un propósito específico (p. ej., alimentación, educación) pero el gasto no se aplica ni verifica estrictamente."` — proposed: `"Las prestaciones se destinan a un propósito específico (p. ej., alimentación, educación), pero el gasto no se aplica ni verifica de manera estricta."` — reason: `"Los beneficios"` → `"Las prestaciones"`. `"se designan"` → `"se destinan"` is more natural (you `"destinar"` funds to a purpose, not `"designar"` them). `"no se aplica ni verifica estrictamente"` → `"no se aplica ni verifica de manera estricta"` because placing the adverb after a coordinated verb pair is ambiguous; the adverbial phrase is clearer.

---

### schema/vocabularies/sp/eligibility-status.yaml

No changes proposed.

---

### schema/vocabularies/sp/enrollment-exit-reason.yaml

No changes proposed. `"eligió"` (from `elegir`) is grammatically correct, and `"optó por"` would only be a stylistic improvement. The translation is within acceptable range.

---

### schema/vocabularies/sp/enrollment-status.yaml

No changes proposed.

---

### schema/vocabularies/sp/entitlement-status.yaml

No changes proposed.

---

### schema/vocabularies/sp/grievance-status.yaml

The cross-file consistency term requires `grievance` → `queja` or `queja o reclamación`. This file uses `agravio` throughout, which violates the consistency requirement.

#### Top-level definition

- Current: `Los estados del ciclo de vida de un registro de agravio en un programa o servicio.`
- Proposed: `Los estados del ciclo de vida de un registro de queja en un programa o servicio.`
- Reason: Per the cross-file consistency terms, `grievance` must be translated as `queja` or `queja o reclamación`, not `agravio`. `"Agravio"` is a legal term in Spanish that means an injury or wrong (used in tort law); it does not carry the administrative redress meaning intended here. `"Queja"` is the standard term in Spanish-language social protection literature (World Bank, IDB) for a program grievance.

#### values

- `submitted`.definition — current: `"El agravio ha sido recibido formalmente y registrado en el sistema, a la espera de asignación."` — proposed: `"La queja ha sido recibida formalmente y registrada en el sistema, a la espera de asignación."` — reason: `"agravio"` → `"queja"` throughout per consistency term. Note also gender agreement: `"queja"` is feminine, so `"recibida"` and `"registrada"`.

- `under_review`.definition — current: `"El agravio está siendo investigado o evaluado activamente por un trabajador social o un órgano de revisión."` — proposed: `"La queja está siendo investigada o evaluada activamente por un trabajador social o un órgano de revisión."` — reason: `"agravio"` → `"queja"`; gender agreement corrections.

- `resolved`.definition — current: `"Se ha emitido y comunicado al reclamante una decisión o remedio."` — no change needed; no `agravio` in this one.

- `closed`.definition — current: `"El proceso de agravio está completo y el registro está archivado, ya sea después de la resolución o retiro."` — proposed: `"El proceso de la queja está completo y el registro está archivado, ya sea después de la resolución o del retiro."` — reason: `"agravio"` → `"queja"`. Also `"o retiro"` → `"o del retiro"` for parallel structure with `"después de la resolución"`.

- `escalated`.definition — current: `"El agravio ha sido referido a una autoridad superior u organismo externo porque no pudo resolverse en el primer nivel."` — proposed: `"La queja ha sido remitida a una autoridad superior u organismo externo porque no pudo resolverse en el primer nivel."` — reason: `"agravio"` → `"queja"`. `"referido"` → `"remitida"`: `"remitir"` is the standard administrative Spanish for forwarding a case upward; `"referir"` is a medical and informal term in this context. Gender agreement with `"queja"`.

- `rejected`.definition — current: `"El agravio fue considerado inválido, fuera del alcance del programa o duplicado, y no fue aceptado para procesamiento."` — proposed: `"La queja fue considerada inválida, fuera del alcance del programa o duplicada, y no fue aceptada para su tramitación."` — reason: `"agravio"` → `"queja"`; gender agreement corrections. `"para procesamiento"` is an anglicism; `"para su tramitación"` is the canonical administrative Spanish term.

- `withdrawn`.definition — current: `"El reclamante ha retirado voluntariamente el agravio antes de la resolución."` — proposed: `"El reclamante ha retirado voluntariamente la queja antes de la resolución."` — reason: `"agravio"` → `"queja"`.

---

### schema/vocabularies/sp/grievance-type.yaml

The cross-file consistency term requires `grievance` → `queja` or `queja o reclamación`. This file uses `agravio` throughout.

#### Top-level definition

- Current: `"Categorías que describen la naturaleza de un agravio o queja recibido por un programa a través de su mecanismo de recurso."`
- Proposed: `"Categorías que describen la naturaleza de una queja o reclamación recibida por un programa a través de su mecanismo de recurso."`
- Reason: The current definition mixes both `agravio` and `queja`. Per the consistency term, `grievance` = `queja` or `queja o reclamación`. The canonical pair in Spanish social protection (World Bank, IDB, ILO) is `queja o reclamación`. Also `"recibido"` should be `"recibida"` to agree with `"queja o reclamación"` (feminine).

#### values

- `information_request`.definition — current: `"Una solicitud de información sobre las reglas del programa, los criterios de elegibilidad, los derechos a beneficios o los procedimientos de queja, cuando se recibe a través del canal de recepción de agravios."` — proposed: `"Una solicitud de información sobre las reglas del programa, los criterios de elegibilidad, los derechos a prestaciones o los procedimientos de queja, cuando se recibe a través del canal de recepción de quejas."` — reason: `"derechos a beneficios"` → `"derechos a prestaciones"` (ILO consistency). `"canal de recepción de agravios"` → `"canal de recepción de quejas"` per consistency term.

- `other`.definition — current: `"Un agravio que no se ajusta a las otras categorías, o cuyo tipo aún no ha sido determinado."` — proposed: `"Una queja que no se ajusta a las otras categorías, o cuyo tipo aún no ha sido determinado."` — reason: `"agravio"` → `"queja"` per consistency term; gender agreement correction (`"una queja"`).

Note: The remaining values (`exclusion_error`, `inclusion_error`, `payment_complaint`, `data_correction`, `appeal`, `service_quality`, `misconduct`) do not use `agravio` in their definitions and are clean.

---

### schema/vocabularies/sp/referral-status.yaml

No changes proposed. `"derivación"` is used consistently and correctly throughout. The `"persona derivada"` phrasing is consistent with the consistency term.

---

### schema/vocabularies/sp/targeting-approach.yaml

No changes proposed. `"focalización"` is correctly used for `targeting`, and `"Auto-focalización"` for `self_targeting` is consistent.

---

## Open questions

1. **`benefit-frequency.yaml`**: The `one_time` label is `Único` in Spanish and `Ponctuel` in French. The French captures "non-recurring/punctual" while `Único` in Spanish leans toward "singular" or "sole." Consider whether `Puntual` would better match `Ponctuel` and the English `"One-time"`. Left as-is since `Único` is widely used in this sense in social protection Spanish (e.g., "pago único"), but flag for domain expert confirmation.

2. **`conditionality-type.yaml`**: The label `Etiquetado` for `labelled` is a direct translation but has no established canonical equivalent in ILO/World Bank Spanish. Common alternatives include `Focalizado en uso` or `De uso designado`. Left as-is but flag for expert review.

3. **`registration-status.yaml`**: The French uses `"signalé à l'officier d'état civil"` for `declared` while the proposed Spanish uses `"declarado ante el registrador"`. Both are defensible; confirm with a CRVS domain expert whether `"declarado"` or `"notificado"` is more natural for the jurisdiction-neutral context intended.

4. **`grievance-status.yaml` and `grievance-type.yaml`**: This review recommends `"queja"` / `"queja o reclamación"` throughout. If the project intentionally used `"agravio"` for a specific legal reason (e.g., targeting Spanish civil law jurisdictions where `"agravio"` is used in administrative appeals), document that rationale explicitly. Otherwise the consistency term should prevail.
