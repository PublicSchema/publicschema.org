# Spanish translation review: properties (batch E)

Files reviewed: recognizing_parent, record_id, record_type, redeemable_by, redeemed_by,
redemption_agent, redemption_date, referral_date, referral_reason, referral_status,
referred_person, referring_program, register_authority, register_number, registrar,
registration_date, registration_location, registration_number, registration_status,
registration_type, relationship_type, religion, resolution_date, role, schedule_ref,
scoring_method, serial_number, severity, sex, sex_at_birth, start_date,
status_in_employment, street_address, subject_person, submission_date,
targeting_approach, transaction_reference, triggering_event, type_of_marriage,
unit_of_measure, valid_until, vital_event, voucher_format, voucher_ref,
voucher_status, weight, weight_at_birth, witnesses

---

## redeemed_by

**File:** `schema/properties/redeemed_by.yaml`
**Current:** `"La persona que presento el vale para el canje."`
**Source:** `"The person who presented the voucher for redemption."`
**Issue:** Missing accent on "presentó" (preterite third-person singular). Stripped accent produces a different reading ("I present" vs. "they presented").
**Proposed:** `"La persona que presentó el vale para el canje."`
**Rationale:** Standard orthography; the accent is required to mark past tense.

---

## redemption_agent

**File:** `schema/properties/redemption_agent.yaml`
**Current:** `"El comerciante, vendedor o agente que acepto el vale para el canje."`
**Source:** `"The merchant, vendor, or agent who accepted the voucher for redemption."`
**Issue:** Missing accent on "aceptó" (preterite third-person singular). Same pattern as redeemed_by.
**Proposed:** `"El comerciante, vendedor o agente que aceptó el vale para el canje."`
**Rationale:** Required accent to mark past tense.

---

## redemption_date

**File:** `schema/properties/redemption_date.yaml`
**Current:** `"La fecha en que el vale fue canjeado en un vendedor o agente."`
**Source:** `"The date on which the voucher was redeemed at a vendor or agent."`
**Issue:** "canjeado en un vendedor" is awkward. One does not redeem something "at/in a vendor" (a person); the idiomatic preposition with a point of service is "ante" or the construction "por un vendedor o agente."
**Proposed:** `"La fecha en que el vale fue canjeado ante un vendedor o agente."`
**Rationale:** "Ante" is the correct preposition when the agent is a person or office receiving/processing something.

---

## referral_reason

**File:** `schema/properties/referral_reason.yaml`
**Current:** `"La base para la derivación."`
**Source:** `"The basis for the referral."`
**Issue:** "La base para la derivación" is a literal calque of "the basis for". In Spanish the idiomatic expression for stating grounds or reason is "el motivo de" or "el fundamento de la derivación." "Base" here reads oddly in context.
**Proposed:** `"El motivo de la derivación."`
**Rationale:** Matches the French "Le motif de l'orientation" and is more natural for a policy audience.

---

## referred_person

**File:** `schema/properties/referred_person.yaml`
**Current:** `"La persona que está siendo referida."`
**Source:** `"The person who is being referred."`
**Issue:** "Referida" is a calque of English "referred." In Spanish social-services and health registers, the correct term is "derivada" (consistent with the vocabulary used for referral_date, referral_reason, referral_status, etc. in this same file set) or "objeto de la derivación."
**Proposed:** `"La persona que es objeto de la derivación."`
**Rationale:** Consistent with the derivación terminology used across all other referral_* properties; avoids the English calque.

---

## resolution_date

**File:** `schema/properties/resolution_date.yaml`
**Current:** `"La fecha en que se emitió una decisión de resolución para el agravio."`
**Source:** `"The date on which a resolution decision was issued for the grievance."`
**Issue:** "Decisión de resolución" is redundant (both words carry the same root meaning in Spanish). Also, "agravio" is one valid translation of "grievance" in a legal wrong sense, but throughout this property set (see grievance_status, submission_date, complainant) the consistent Spanish term used is "queja" or "reclamación." Using "agravio" only in this property creates an inconsistency.
**Proposed:** `"La fecha en que se emitió la decisión de resolución de la queja."`
**Rationale:** Removes internal redundancy and aligns with the translation used in sibling grievance properties.

---

## submission_date

**File:** `schema/properties/submission_date.yaml`
**Current:** `"La fecha en que el agravio fue presentado o registrado."`
**Source:** `"The date on which the grievance was submitted or registered."`
**Issue:** Same "agravio" inconsistency as resolution_date (see above). If the site uses "queja" or "reclamación" in other grievance properties, this should match.
**Proposed:** `"La fecha en que la queja fue presentada o registrada."`
**Rationale:** Terminological consistency across grievance properties; grammatical gender agreement ("presentada" not "presentado" when the noun is feminine).

---

## role

**File:** `schema/properties/role.yaml`
**Current:** `"El rol de la persona dentro del grupo (por ejemplo, jefe, conyuge, hijo, dependiente)."`
**Source:** `"The role of the person within the group (e.g., head, spouse, child, dependent)."`
**Issue:** Missing accent on "cónyuge." Also, "rol" is an anglicism widely used in LatAm but marked as informal in Spain; "función" or "papel" is more neutral. The accent omission is the harder error.
**Proposed:** `"El rol de la persona dentro del grupo (por ejemplo, jefe de hogar, cónyuge, hijo, dependiente)."`
**Rationale:** Accent on "cónyuge" is required. "Jefe de hogar" is the conventional welfare/social-protection term (matches the vocabulary in related concepts).

---

## serial_number

**File:** `schema/properties/serial_number.yaml`
**Current:** `"Un identificador publico para el vale, impreso en el documento fisico o comunicado por SMS o aplicacion."`
**Source:** `"A public identifier for the voucher, printed on the physical document or communicated via SMS or application."`
**Issue:** Three stripped accents: "público," "físico," "aplicación."
**Proposed:** `"Un identificador público para el vale, impreso en el documento físico o comunicado por SMS o aplicación."`
**Rationale:** Required orthographic accents.

---

## street_address

**File:** `schema/properties/street_address.yaml`
**Current:** `"El nombre de la calle, numero y cualquier identificador de apartamento o edificio."`
**Source:** `"The street name, number, and any apartment or building identifiers."`
**Issue:** Missing accent on "número."
**Proposed:** `"El nombre de la calle, número y cualquier identificador de apartamento o edificio."`
**Rationale:** Required orthographic accent.

---

## weight

**File:** `schema/properties/weight.yaml`
**Current:** `"El peso del feto al momento de la muerte fetal, registrado en gramos. Combinado con la edad gestacional, se utiliza para clasificar la viabilidad y el tipo de mortinato."`
**Source:** `"The weight of the fetus at the time of a fetal death, recorded in grams. Combined with gestational age, used to classify viability and stillbirth type."`
**Issue:** "Mortinato" means a stillborn child (the noun), not "stillbirth" (the event). "Stillbirth type" refers to a classification of the event, not the child. The established Spanish term for the event is "mortinatalidad" or "nacido muerto"; for the classification it is "tipo de mortinatalidad" or "tipo de muerte fetal."
**Proposed:** `"El peso del feto al momento de la muerte fetal, registrado en gramos. Combinado con la edad gestacional, se utiliza para clasificar la viabilidad y el tipo de muerte fetal."`
**Rationale:** "Tipo de muerte fetal" is precise and avoids the event/person conflation in "mortinato."

---

## Notes on clean files

The following files were reviewed and are clean (no issues found): recognizing_parent, record_id, record_type, redeemable_by, referral_date, referral_status, referring_program, register_authority, register_number, registrar, registration_date, registration_location, registration_number, registration_status, registration_type, relationship_type, religion, schedule_ref, scoring_method, severity, sex, sex_at_birth, start_date, status_in_employment, subject_person, targeting_approach, transaction_reference, triggering_event, type_of_marriage, unit_of_measure, valid_until, vital_event, voucher_format, voucher_ref, voucher_status, weight_at_birth, witnesses.
