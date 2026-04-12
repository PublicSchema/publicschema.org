# Spanish translation review: SP/delivery concept definitions

Scope: `definition.es` blocks across 16 concept YAML files in `schema/concepts/`.
Reviewer notes are grouped by file. Files with no issues are listed briefly at the end.

---

## assessment-event.yaml

**Issue 1**
- Current: `Los desencadenantes incluyen el registro inicial, la recertificación y la reevaluación ante un choque.`
- Source (EN): `Triggers include initial registration, recertification, and shock-response reassessment.`
- Issue: "ante un choque" (in the face of a shock) is not a natural equivalent for "shock-response reassessment". It loses the compound meaning: an event that both responds to a shock and involves reassessment. "Ante un choque" sounds like a one-time reaction rather than a formal process.
- Proposed: `Los desencadenantes incluyen el registro inicial, la recertificación y la reevaluación por respuesta a crisis.`
- Rationale: "reevaluación por respuesta a crisis" captures the structured, programmatic nature of "shock-response reassessment" more clearly. "Crisis" is neutral across regions; "choque" in the economic/shock sense is common in technical SP literature but sounds informal here.

---

## assessment-framework.yaml

**Issue 1**
- Current: `Los marcos de evaluación incluyen pruebas de proxy de medios, tarjetas de puntuación comunitarias e índices compuestos de bienestar.`
- Source (EN): `Assessment frameworks include proxy means tests, community scorecards, and composite welfare indices.`
- Issue: "pruebas de proxy de medios" is a calque of "proxy means tests". "Proxy means test" is a recognized technical term in SP; in Spanish it is almost always rendered as "prueba de verificación de medios de vida sustituta" or simply kept as "prueba proxy de medios de vida". "Proxy de medios" alone is awkward and opaque to a policy reader. "Tarjetas de puntuación comunitarias" is also unusual; the standard Spanish for community scorecard in SP is "tarjeta de calificación comunitaria".
- Proposed: `Los marcos de evaluación incluyen pruebas proxy de medios de vida, tarjetas de calificación comunitarias e índices compuestos de bienestar.`
- Rationale: "pruebas proxy de medios de vida" matches standard SP practice terminology. "Tarjetas de calificación comunitarias" follows World Bank and UNICEF Spanish publications on community scorecards.

---

## benefit-schedule.yaml

**Issue 1 (missing accents)**
- Current: `Una definicion a nivel de programa de un flujo de beneficios...` (and throughout: "especifica", "periodo", "mas", "utiles")
- Issue: The entire definition is missing diacritics. "definicion" should be "definición", "mas" should be "más", "utiles" should be "útiles", "periodo" should be "período". This is systematic, not a one-off typo.
- Proposed: `Una definición a nivel de programa de un flujo de beneficios que especifica la modalidad, el monto, la frecuencia y el período durante el cual se proporcionan los beneficios. Un programa puede tener uno o más calendarios de beneficios (por ej., una transferencia monetaria mensual y un kit de útiles escolares anual).`
- Rationale: Standard Spanish orthography. These omissions are likely an encoding or copy-paste artifact, not a deliberate choice.

**Issue 2**
- Current: `un flujo de beneficios`
- Source (EN): `a benefit stream`
- Issue: Terminology consistency. This file uses "beneficios" for both the stream and the individual benefits. Elsewhere in the schema (Entitlement, PaymentEvent, InKindDelivery) the concept of what is owed/delivered is also called "beneficio". That is fine, but "benefit stream" in a program design context is more precisely "flujo de prestaciones" in Spain-influenced SP vocabulary. However, "beneficio" is more universally understood in LatAm. The EN definition uses both "benefit stream" (design level) and "benefits are provided" (instances). Keeping "beneficios" is defensible but flagged for consistency review against other files (see cross-file note below).

---

## delivery-item.yaml

**Issue 1 (missing accents)**
- Current: `Una linea de detalle que describe un producto especifico y su cantidad dentro de una entrega o vale.` (and: "multiples", "canastas")
- Issue: "linea" should be "línea", "especifico" should be "específico", "multiples" should be "múltiples", "canastas" may be fine (no accent needed) but "canastas" is LatAm-specific; in Spain this would more likely be "cestas". See regional note below.
- Proposed: `Una línea de detalle que describe un producto específico y su cantidad dentro de una entrega o vale. Se utiliza para representar canastas/cestas de alimentos, kits de suministros y otros beneficios compuestos donde se incluyen múltiples productos en cantidades especificadas.`
- Rationale: Orthographic correction. "Canastas" is understood across Spanish-speaking regions even if "cestas" is preferred in Spain; flagged but not a hard error given LatAm reach of SP programs.

---

## eligibility-decision.yaml

No issues worth flagging.

---

## enrollment.yaml

No issues worth flagging. "Inscripción" is the correct neutral term for enrollment; "elegibilidad" and "beneficiario activo" are consistent with standard SP usage.

---

## entitlement.yaml

**Issue 1**
- Current: `Cada derecho corresponde típicamente a un período de desembolso`
- Source (EN): `Each entitlement typically corresponds to one disbursement period`
- Issue: "corresponde típicamente" is grammatically correct but reads slightly awkwardly due to the adverb position; in natural Spanish prose the adverb usually follows the verb more closely. Minor.
- Proposed: `Cada derecho corresponde típicamente a un período de desembolso` — actually acceptable as is. No change strictly required; flagged for awareness only.

**Issue 2**
- Current: `El derecho referencia tanto la inscripción (quién) como el calendario de beneficios (lo que se prometió).`
- Source (EN): `The entitlement references both the enrollment (who) and the benefit schedule (what was promised).`
- Issue: "referencia" used as a verb ("El derecho referencia") is a calque from English ("references"). In Spanish, "referencia" is a noun. The correct verb is "hace referencia a" or "remite a".
- Proposed: `El derecho hace referencia tanto a la inscripción (quién) como al calendario de beneficios (lo que se prometió).`
- Rationale: "referencias" as a verb is a common Anglicism in technical translation. Fixing it makes the sentence read naturally.

---

## farm.yaml

**Issue 1 (missing accents)**
- Current: `Una unidad organizativa y operativa de produccion agricola bajo gestion unica. Los registros de fincas aparecen en registros agricolas, administracion de tierras, proteccion social y programas de adaptacion climatica.`
- Issue: Systematic missing diacritics: "produccion" → "producción", "agricola" → "agrícola", "gestion" → "gestión", "agricolas" → "agrícolas", "administracion" → "administración", "proteccion" → "protección", "adaptacion" → "adaptación", "climatica" → "climática".
- Proposed: `Una unidad organizativa y operativa de producción agrícola bajo gestión única. Los registros de fincas aparecen en registros agrícolas, administración de tierras, protección social y programas de adaptación climática.`
- Rationale: Orthographic correction; likely an encoding artifact.

---

## grievance.yaml

**Issue 1**
- Current: `El agravio abarca los recursos (solicitudes para revertir una decisión) y las quejas (insatisfacción con la calidad del servicio).`
- Source (EN): `Grievance covers appeals (requests to reverse a decision) and complaints (dissatisfaction with service quality).`
- Issue: "agravio" is used as the Spanish translation of "grievance". In SP program contexts, "agravio" means a personal wrong or injury in a legal/moral sense and carries a strong emotional register. The standard SP vocabulary for a formal complaint/grievance mechanism is "reclamación", "queja", or in LatAm "reclamo". Some systems use "solicitud de apelación y queja" or just "mecanismo de quejas y reclamos (MQR)". Using "agravio" as the concept label is unusual and would confuse practitioners.
- Proposed: Consider "reclamación" (Spain-neutral) or "queja o reclamo" as the concept-level term. For the definition sentence: `La queja o reclamación abarca los recursos (solicitudes para revertir una decisión) y las quejas (insatisfacción con la calidad del servicio).`
- Rationale: "Agravio" is a legal term meaning "grievance" in the sense of a harm suffered, not a formal complaint channel. Practitioners reading a social protection schema would expect "queja", "reclamación", or "reclamo". This is a significant terminology error that could cause confusion.

**Issue 2**
- Current: `Un registro de la expresión formal de insatisfacción o disputa de un beneficiario o solicitante con respecto a cualquier aspecto de la cadena de prestación.`
- Issue: "con respecto a" works but is wordy. Minor. Not a hard flag.

---

## hazard-event.yaml

**Issue 1 (missing accents)**
- Current: `Un evento o condicion que puede interrumpir la prestacion de servicios publicos...` (and throughout: "condicion", "prestacion", "publicos", "poblacion", "sequias", "economicos", "definicion", "Alineado", "amplia")
- Issue: Systematic missing diacritics throughout the entire definition block: "condición", "prestación", "públicos", "población", "sequías", "económicos", "definición". "Alineado" is correct as-is.
- Proposed: `Un evento o condición que puede interrumpir la prestación de servicios públicos o afectar el bienestar de una población. Cubre riesgos naturales (inundaciones, sequías, terremotos), emergencias sanitarias, conflictos y choques económicos. Alineado con la definición amplia del Marco de Sendai y compatible con OASIS CAP v1.2 para la interoperabilidad de alertas.`
- Rationale: Orthographic correction; likely encoding artifact.

---

## in-kind-delivery.yaml

**Issue 1 (missing accents)**
- Current: `Un registro de una distribucion fisica directa de bienes o servicios...` (and: "distribucion", "fisica", "involucrado", "agricolas", "alimentacion", "especie")
- Issue: "distribucion" → "distribución", "fisica" → "física", "agricolas" → "agrícolas", "alimentacion" → "alimentación". "involucrado" and "especie" do not need accents.
- Proposed: `Un registro de una distribución física directa de bienes o servicios de un programa a un beneficiario, sin instrumento financiero involucrado. Cubre la distribución de alimentos, kits de suministros, insumos agrícolas, alimentación escolar y prestación directa de servicios. Varias entregas en especie pueden cumplir un solo derecho.`
- Rationale: Orthographic correction.

---

## payment-event.yaml

**Issue 1**
- Current: `reintentos tras fallo`
- Source (EN): `retries after failure`
- Issue: "fallo" is Spain Spanish; in LatAm the standard term is "falla". Since this schema targets both regions, "fallo" may feel out of place for LatAm readers. Either term is understood, but consistency with regional neutrality is worth noting.
- Proposed: `reintentos tras un error` or `nuevos intentos tras un fallo` — "error" is fully neutral across regions.
- Rationale: Minor regional drift. "fallo" is not wrong but "error" or "falla" would be broader.

---

## program.yaml

**Issue 1**
- Current: `un enfoque de focalización`
- Source (EN): `targeting approach`
- Issue: "Focalización" is the standard LatAm SP term for targeting (World Bank, IDB, CEPAL all use it). In Spain "focalización" is also used but somewhat less common than "focalización de la ayuda" or simply "enfoque selectivo". "Focalización" here is the best neutral choice and is already in wide use — no change needed. Flagged only to confirm the intent was deliberate.

No issues worth flagging.

---

## referral.yaml

**Issue 1**
- Current: `Las derivaciones abarcan un espectro que va desde el intercambio pasivo de información hasta la vinculación activa de servicios con seguimiento.`
- Source (EN): `Referrals span a spectrum from passive information sharing to active service linkage with follow-up.`
- Issue: "vinculación activa de servicios" is a calque. In natural Spanish, "service linkage" in a case management context is rendered as "vinculación activa con servicios" (linkage with services, not of services). A person is linked with a service, not services are linked.
- Proposed: `Las derivaciones abarcan un espectro que va desde el intercambio pasivo de información hasta la vinculación activa con servicios y el seguimiento posterior.`
- Rationale: Prepositional correction and slight restructuring for natural flow. "seguimiento posterior" is clearer than "con seguimiento" appended at the end.

---

## voucher.yaml

**Issue 1 (missing accents)**
- Current: `Un instrumento canjeable emitido a un beneficiario como cumplimiento de un derecho a prestacion.` (and: "prestacion", "creacion", "emision")
- Issue: "prestacion" → "prestación", "creacion" → "creación", "emision" → "emisión".
- Proposed: `Un instrumento canjeable emitido a un beneficiario como cumplimiento de un derecho a prestación. Un vale tiene un ciclo de vida distinto: creación, emisión, canje, vencimiento o cancelación.`
- Rationale: Orthographic correction.

---

## voucher-redemption.yaml

**Issue 1 (missing accents)**
- Current: `Un registro de una transaccion de canje unica contra un vale.` (and: "transaccion", "unica", "comun", "multiples")
- Issue: "transaccion" → "transacción", "unica" → "única", "comun" → "común", "multiples" → "múltiples".
- Proposed: `Un registro de una transacción de canje única contra un vale. Cada VoucherRedemption captura una visita a un vendedor o agente donde se recogió parte o la totalidad del valor del vale o de los productos a los que da derecho. Para vales de uso único, hay un solo VoucherRedemption. Para el canje incremental (común en los programas de vales de valor del PMA), múltiples registros VoucherRedemption rastrean cada visita.`
- Rationale: Orthographic correction.

**Issue 2**
- Current: `donde se recogio parte o la totalidad`
- Issue: "recogio" → "recogió" (missing accent on preterite).
- Proposed: already corrected in Issue 1 proposed text above.

---

## Cross-file terminology consistency notes

These are not per-file errors but patterns worth aligning before any fix pass:

1. **"beneficio" vs. "prestación"**: "Beneficio" is used consistently across all files for the English concept "benefit". This is fine and understandable across regions. However, in formal SP policy writing in Spain and some LatAm contexts, "prestación" is the standard for a social protection benefit (as opposed to "beneficio" which is broader). The schema is consistent internally, which matters more than Spain/LatAm preference. No change required, but the choice should be documented in a style note.

2. **"derecho" for "entitlement"**: Used in Entitlement, Voucher, and InKindDelivery. Consistent and correct.

3. **"inscripción" for "enrollment"**: Used consistently in Enrollment and referenced elsewhere. Correct and neutral.

4. **"agravio" for "Grievance"**: Flagged above under grievance.yaml as a significant terminology issue. "Queja", "reclamación", or "reclamo" are the standard SP terms.

5. **Missing diacritics pattern**: Affects benefit-schedule.yaml, delivery-item.yaml, farm.yaml, hazard-event.yaml, in-kind-delivery.yaml, voucher.yaml, and voucher-redemption.yaml. The pattern is consistent with a UTF-8 encoding issue during authoring, not random typos. All affected files should be fixed in a single pass.
