# Spanish Translation Review: Properties B (complainant through family_name)

Reviewed 46 property files. Issues found in 19 files. Clean files not listed.

---

## complainant

**File:** `schema/properties/complainant.yaml`

| | |
|---|---|
| **Current** | `La persona que presentó el agravio. El reclamante no necesariamente es el beneficiario inscrito; miembros de la comunidad, solicitantes rechazados o cuidadores también pueden presentar agravios.` |
| **Source (en)** | `The person who submitted the grievance. The complainant need not be the enrolled beneficiary; community members, rejected applicants, or caretakers may also file grievances.` |

**Issue 1: Terminology drift — "agravio" for "grievance"**
"Agravio" means a personal affront or insult in standard Spanish. In social protection and administrative contexts, "grievance" translates as "queja" or "reclamación". "Agravio" introduces an inappropriate legal/moral charge. The same drift applies to "presentar agravios" at the end of the sentence.

- **Proposed:** Replace "el agravio" with "la queja" and "presentar agravios" with "presentar quejas".
- **Rationale:** "Queja" is the neutral, administrative register term used across social protection systems in Latin America and Spain.

**Issue 2: Calque on "need not be"**
"no necesariamente es" is a tolerable rendering but slightly awkward. The more natural phrasing is "no tiene que ser".

- **Proposed:** "El reclamante no tiene que ser el beneficiario inscrito"
- **Rationale:** Closer to natural Spanish spoken register for policy documents.

---

## country

**File:** `schema/properties/country.yaml`

| | |
|---|---|
| **Current** | `El pais, expresado como codigo ISO 3166-1 alfa-2 cuando sea posible.` |
| **Source (en)** | `The country, expressed as an ISO 3166-1 alpha-2 code where possible.` |

**Issue: Missing accents**
"pais" should be "país"; "codigo" should be "código".

- **Proposed:** `El país, expresado como código ISO 3166-1 alfa-2 cuando sea posible.`
- **Rationale:** Stripped accents are orthographic errors; both words carry stress on the stressed syllable and require the written accent.

---

## country_of_birth

**File:** `schema/properties/country_of_birth.yaml`

| | |
|---|---|
| **Current** | `El pais donde nacio la persona, expresado como codigo ISO 3166-1.` |
| **Source (en)** | `The country where the person was born, expressed as an ISO 3166-1 code.` |

**Issue: Missing accents**
"pais" → "país"; "nacio" → "nació"; "codigo" → "código".

- **Proposed:** `El país donde nació la persona, expresado como código ISO 3166-1.`
- **Rationale:** Three orthographic errors; accent marks are required by standard Spanish orthography.

---

## currency

**File:** `schema/properties/currency.yaml`

| | |
|---|---|
| **Current** | `El codigo de moneda ISO 4217 para un valor monetario.` |
| **Source (en)** | `The ISO 4217 currency code for a monetary value.` |

**Issue: Missing accent**
"codigo" → "código".

- **Proposed:** `El código de moneda ISO 4217 para un valor monetario.`
- **Rationale:** Orthographic error.

---

## deceased

**File:** `schema/properties/deceased.yaml`

| | |
|---|---|
| **Current** | `La persona cuyo fallecimiento se registra. Sigue siendo una entidad Persona para que los identificadores y atributos existentes puedan seguir siendo referenciados tras la defunción.` |
| **Source (en)** | `The person whose death is recorded. Remains a Person entity so that existing identifiers and attributes can still be referenced after death.` |

**Issue: Redundant "seguir siendo referenciados"**
"puedan seguir siendo referenciados" is clunky because of the double "seguir siendo" construction in close proximity to the earlier "Sigue siendo". The first "seguir siendo" is fine; the second is verbose.

- **Proposed:** `...para que los identificadores y atributos existentes puedan consultarse tras la defunción.`
- **Rationale:** "Consultarse" or "referenciarse" is leaner; avoids the awkward double construction without changing the meaning.

---

## decision_basis

**File:** `schema/properties/decision_basis.yaml`

| | |
|---|---|
| **Current** | `El evento de evaluación, puntuación o regla administrativa que formó la base de la decisión.` |
| **Source (en)** | `The assessment event, score, or administrative rule that formed the basis for the decision.` |

**Issue: Wordy calque on "formed the basis"**
"formó la base de la decisión" is a direct calque. More natural in Spanish: "que fundamentó la decisión" or "que sirvió de fundamento para la decisión".

- **Proposed:** `El evento de evaluación, puntuación o regla administrativa que fundamentó la decisión.`
- **Rationale:** "Fundamentar" is the standard administrative register verb for "to form the basis of"; the calque reads as translated rather than native.

---

## delivery_date

**File:** `schema/properties/delivery_date.yaml`

| | |
|---|---|
| **Current** | `La fecha en que los bienes o servicios fueron distribuidos al beneficiario.` |
| **Source (en)** | `The date on which the goods or services were distributed to the beneficiary.` |

**Issue: Clean but passive voice is heavier than needed**
This is marginal; the translation is correct. However, "en que los bienes o servicios fueron distribuidos" uses a passive voice that the active/nominalized form avoids more naturally in Spanish formal writing: "La fecha de distribución de los bienes o servicios al beneficiario." Flag for consideration only.

- **Proposed (optional):** `La fecha de distribución de los bienes o servicios al beneficiario.`
- **Rationale:** Nominalized form is more idiomatic in Spanish administrative writing, but the current version is not wrong.

---

## delivery_location

**File:** `schema/properties/delivery_location.yaml`

| | |
|---|---|
| **Current** | `El lugar donde se realizo la distribucion, como un punto de distribucion, escuela o centro de salud.` |
| **Source (en)** | `The location where the distribution took place, such as a distribution point, school, or health facility.` |

**Issue: Missing accents**
"realizo" → "realizó"; "distribucion" (twice) → "distribución".

- **Proposed:** `El lugar donde se realizó la distribución, como un punto de distribución, escuela o centro de salud.`
- **Rationale:** Three orthographic errors.

---

## description

**File:** `schema/properties/description.yaml`

| | |
|---|---|
| **Current** | `Un resumen en texto libre que describe el evento, la situacion o el registro.` |
| **Source (en)** | `A free-text summary describing the event, situation, or record.` |

**Issue: Missing accent**
"situacion" → "situación".

- **Proposed:** `Un resumen en texto libre que describe el evento, la situación o el registro.`
- **Rationale:** Orthographic error.

---

## document_expiry_date

**File:** `schema/properties/document_expiry_date.yaml`

| | |
|---|---|
| **Current** | `La fecha en que el documento o credencial que representa el derecho expira, que puede diferir del periodo del derecho en si.` |
| **Source (en)** | `The date on which the document or credential representing the entitlement expires, which may differ from the entitlement period itself.` |

**Issue: Missing accents and awkward word order**
"credencial" is fine. "periodo" → "período" (both spellings are accepted by the RAE, so this is minor). "en si" → "en sí" (required accent on the reflexive pronoun to distinguish from the conditional conjunction). The trailing relative clause "que puede diferir" creates a double-"que" construction that is awkward.

- **Proposed:** `La fecha en que el documento o credencial que representa el derecho expira, la cual puede diferir del período del derecho en sí.`
- **Rationale:** "la cual" resolves the double-"que" ambiguity; "en sí" corrects the required accent.

---

## domicile

**File:** `schema/properties/domicile.yaml`

| | |
|---|---|
| **Current** | `El lugar que la persona considera como su domicilio permanente, que puede diferir de la direccion de su hogar actual.` |
| **Source (en)** | `The place that the person treats as their permanent home, which may differ from the address of their current household.` |

**Issue: Missing accent and double-"que"**
"direccion" → "dirección". The double-"que" ("lugar que... que puede diferir") is structurally the same issue as in `document_expiry_date`.

- **Proposed:** `El lugar que la persona considera su domicilio permanente, el cual puede diferir de la dirección de su hogar actual.`
- **Rationale:** "el cual" replaces the second "que" to eliminate ambiguity; "dirección" corrects the missing accent.

---

## email_address

**File:** `schema/properties/email_address.yaml`

| | |
|---|---|
| **Current** | `Una direccion de correo electronico a traves de la cual se puede contactar a la persona.` |
| **Source (en)** | `An email address through which the person can be contacted.` |

**Issue: Missing accents**
"direccion" → "dirección"; "electronico" → "electrónico"; "traves" → "través".

- **Proposed:** `Una dirección de correo electrónico a través de la cual se puede contactar a la persona.`
- **Rationale:** Three orthographic errors.

---

## employment_status

**File:** `schema/properties/employment_status.yaml`

| | |
|---|---|
| **Current** | `El estado de participación en la fuerza laboral de la persona: si está empleada, desempleada o fuera de la fuerza laboral.` |
| **Source (en)** | `The labour force participation status of the person: whether they are employed, unemployed, or outside the labour force.` |

**Issue: Terminology — "estado" for "status"**
Per established project convention, "Estatus" → "condición" or domain-appropriate noun. "Estado" is more ambiguous (it can also mean "state" as in political entity). For labour force participation, the established ILO/UN Spanish term is "situación laboral" or "condición de actividad".

- **Proposed:** `La situación laboral de la persona en cuanto a su participación en la fuerza de trabajo: si está empleada, desempleada o inactiva.`
- **Rationale:** "Situación laboral" aligns with ILO Spanish terminology. "Fuera de la fuerza laboral" → "inactiva" is more concise and widely used in Spanish-language labour statistics.

---

## entitlement_ref

**File:** `schema/properties/entitlement_ref.yaml`

| | |
|---|---|
| **Current** | `Referencia al derecho que este pago o vale cumple.` |
| **Source (en)** | `Reference to the entitlement that this payment or voucher fulfills.` |

**Issue: Awkward construction — "cumple"**
"cumple" here reads as "that this payment fulfills/completes", which is an unusual collocation. The more natural phrasing is "que este pago o vale satisface" or restructured as "al que corresponde este pago o vale".

- **Proposed:** `Referencia al derecho al que corresponde este pago o vale.`
- **Rationale:** "Corresponde" is the natural administrative verb for "fulfills/belongs to" in this context.

---

## exit_reason

**File:** `schema/properties/exit_reason.yaml`

| | |
|---|---|
| **Current** | `La razón por la cual la inscripción fue cerrada permanentemente. Se aplica cuando el estado de inscripción es cerrado, no cuando es graduado.` |
| **Source (en)** | `The reason the enrollment was permanently closed. Applies when enrollment status is closed, not when graduated.` |

**Issue: Predicative use of "cerrado" and "graduado" without noun**
"cuando el estado de inscripción es cerrado, no cuando es graduado" reads awkwardly because "cerrado" and "graduado" are hanging predicate adjectives without a referent noun. In Spanish it is cleaner to say "cuando el estado es de cierre, no de graduación" or to name the status values explicitly.

- **Proposed:** `La razón por la cual la inscripción fue cerrada permanentemente. Se aplica cuando el estado de inscripción es "cerrado", no cuando es "graduado".`
- **Rationale:** Quoting the status values (as the English implicitly does) signals that these are controlled vocabulary terms, and the sentence reads naturally.

---

## expiry_date

**File:** `schema/properties/expiry_date.yaml`

| | |
|---|---|
| **Current** | `La fecha en que este registro o documento expira o deja de ser valido.` |
| **Source (en)** | `The date on which this record or document expires or becomes invalid.` |

**Issue: Missing accent**
"valido" → "válido".

- **Proposed:** `La fecha en que este registro o documento expira o deja de ser válido.`
- **Rationale:** Orthographic error.

---

## failure_reason

**File:** `schema/properties/failure_reason.yaml`

| | |
|---|---|
| **Current** | `Una descripcion de por que el pago fallo, fue devuelto o fue rechazado.` |
| **Source (en)** | `A description of why the payment failed, was returned, or was rejected.` |

**Issue: Missing accents**
"descripcion" → "descripción"; "por que" → "por qué" (interrogative embedded clause requires accent); "fallo" → "falló".

- **Proposed:** `Una descripción de por qué el pago falló, fue devuelto o fue rechazado.`
- **Rationale:** Three orthographic errors; "por que" without accent is a different construction (causal/relative).

---

## family

**File:** `schema/properties/family.yaml`

| | |
|---|---|
| **Current** | `El grupo familiar al que da seguimiento un registro familiar. Modelado como un Grupo para que los conceptos a nivel de hogar y a nivel de familia puedan compartir la misma estructura.` |
| **Source (en)** | `The family group tracked by a family register. Modeled as a Group so that household-level and family-level concepts can share structure.` |

**Issue: "da seguimiento" is a Latinamerican calque from English "tracks"**
"dar seguimiento a" is widely used in Latin America but is considered a calque by Spanish style guides. In Spain and in formal international Spanish, "registra" or "lleva el seguimiento de" or simply "sigue" would be used. For a global neutral register, a cleaner option is available.

- **Proposed:** `El grupo familiar registrado en un registro familiar. Modelado como un Grupo para que los conceptos a nivel de hogar y a nivel de familia puedan compartir la misma estructura.`
- **Rationale:** "Registrado en" is unambiguous and universally understood. Alternatively "al que pertenece un registro familiar" is closer to the English.

---

## family_name

**File:** `schema/properties/family_name.yaml`

| | |
|---|---|
| **Current** | `El apellido o nombre de familia de la persona.` |
| **Source (en)** | `The family (last) name or surname of the person.` |

**Issue: Inverted term order creates ambiguity**
"El apellido o nombre de familia" puts "apellido" first and "nombre de familia" second. In Spanish, "nombre de familia" is a less common phrasing and risks being read as "family's name" rather than "family name". The standard term is simply "apellido"; "nombre de familia" is a redundant calque.

- **Proposed:** `El apellido de la persona.`
- **Rationale:** "Apellido" fully and unambiguously covers "family name / last name / surname" in all Spanish-speaking regions. The English definition includes a parenthetical "(last) name" for clarity but the Spanish term needs no such gloss.

---

## Summary

| File | Issue type |
|---|---|
| complainant | Terminology ("agravio" for "grievance"), awkward negation |
| country | Missing accents (país, código) |
| country_of_birth | Missing accents (país, nació, código) |
| currency | Missing accent (código) |
| deceased | Redundant double "seguir siendo" |
| decision_basis | Calque "formó la base de" |
| delivery_date | Heavy passive (minor, optional) |
| delivery_location | Missing accents (realizó, distribución x2) |
| description | Missing accent (situación) |
| document_expiry_date | Missing accent (sí), double-que construction |
| domicile | Missing accent (dirección), double-que construction |
| email_address | Missing accents (dirección, electrónico, través) |
| employment_status | "Estado" vs. established ILO term "situación laboral" |
| entitlement_ref | Awkward "cumple" colocation |
| exit_reason | Hanging predicates without noun ("cerrado", "graduado") |
| expiry_date | Missing accent (válido) |
| failure_reason | Missing accents (descripción, por qué, falló) |
| family | Regional calque "da seguimiento" |
| family_name | Redundant calque "nombre de familia" |
