# Spanish translation review: properties l–r (batch d)

Files reviewed: level_name, literacy, location, location_name, locations, longitude, manner_of_death, marital_status, marriage_ref, matronymic_name, medical_certifier, member_count, memberships, mother, name, nationality, nationality_at_birth, number_of_spouses, object_person, occupation, originating_event, parent_location, parental_role, parents, party_1, party_2, patronymic_name, payment_amount, payment_currency, payment_date, payment_status, person, phone_number, place_of_usual_residence, place_type, postal_code, preferred_language, preferred_name, previous_parents, primary_crop, program_ref, quantity, quantity_redeemed, raw_score, receiving_program, recipient

---

## location

**File:** `schema/properties/location.yaml`
**Current:** "La ubicación geográfica asociada a este hogar, capturando coordenadas o área administrativa."
**Source:** "The geographic location associated with this household, capturing coordinates or administrative area."
**Issue:** Calque. "Capturando" mirrors the English gerund "capturing" but sounds unnatural in Spanish. The convention established in earlier batches is "Recoge" for this verb.
**Proposed:** "La ubicación geográfica asociada a este hogar, que recoge las coordenadas o el área administrativa."
**Rationale:** Consistent with the "Captura → Recoge" convention. Adding "que" makes the relative clause grammatically clean.

---

## location_name

**File:** `schema/properties/location_name.yaml`
**Current:** "Un nombre de lugar legible para la ubicacion."
**Source:** "A human-readable place name for the location."
**Issue:** Missing accent on "ubicación". The phrase also drops the qualifier "human-readable" (legible por personas / legible por humanos); the current translation shortens this to just "legible", which loses the nuance.
**Proposed:** "Un nombre de lugar legible por humanos para la ubicación."
**Rationale:** Restores the technical qualifier that distinguishes human-readable from machine-readable, and fixes the missing accent.

---

## locations

**File:** `schema/properties/locations.yaml`
**Current:** "Ubicaciones con nombre dentro de o que representan esta area geografica."
**Source:** "Named locations within or representing this geographic area."
**Issue:** Missing accents on "área" and "geográfica". The phrase "dentro de o que" is also awkward; "o que" with no subject reads unnaturally.
**Proposed:** "Ubicaciones con nombre dentro de esta área geográfica o que la representan."
**Rationale:** Fixes accents and restructures the clause to avoid the ambiguous "o que" hanging construction.

---

## marital_status

**File:** `schema/properties/marital_status.yaml`
**Current:** "El estado civil o matrimonial de una persona tal como se registra en un sistema administrativo."
**Source:** "The marital or civil status of a person as recorded in an administrative system."
**Issue:** The English order is "marital or civil". In Spanish administrative and legal usage the standard compound is "estado civil" (covering both). Reversing it to "civil o matrimonial" is unusual and the added adjective is redundant. Minor but worth noting.
**Proposed:** "El estado civil de una persona tal como se registra en un sistema administrativo."
**Rationale:** "Estado civil" is the standard Spanish legal term and already covers both civil and marital status. The compound "civil o matrimonial" adds wordiness without precision.

---

## originating_event

**File:** `schema/properties/originating_event.yaml`
**Current:** "El evento vital que esta acta de estado civil acredita (el nacimiento detrás de un acta de nacimiento, el matrimonio detrás de un acta de matrimonio, etc.). Ancla el acta al suceso subyacente."
**Source:** "The vital event that this civil status record attests to (the birth behind a birth record, the marriage behind a marriage record, etc.). Anchors the record to its underlying occurrence."
**Issue:** "Ancla el acta al suceso subyacente" is grammatically fine but the metaphorical verb "ancla" (anchors) is informal in a formal administrative context. The English uses it deliberately; if the intent is to keep it, that is acceptable. Flagging for awareness. No change strictly required.
**Issue (secondary):** "detrás de" (literally "behind") is a direct calque of the English "behind". In Spanish the idiomatic phrase for "the event underlying the record" would use "que dio origen a" or "al que corresponde".
**Proposed:** "El evento vital que esta acta de estado civil acredita (el nacimiento que dio origen al acta de nacimiento, el matrimonio que dio origen al acta de matrimonio, etc.). Vincula el acta al suceso subyacente."
**Rationale:** Replaces the calqued "detrás de" with the natural Spanish construction "que dio origen a", and swaps "ancla" for the more neutral "vincula".

---

## parent_location

**File:** `schema/properties/parent_location.yaml`
**Current:** "La ubicacion padre en la jerarquia administrativa."
**Source:** "The parent location in the administrative hierarchy."
**Issue:** Missing accents on "ubicación" and "jerarquía". Also "ubicación padre" is a direct calque of "parent location"; in Spanish hierarchical terminology "ubicación superior" or "localización de nivel superior" is clearer, though "padre" is widely used in technical contexts. The missing accents are the hard defect.
**Proposed:** "La ubicación superior en la jerarquía administrativa."
**Rationale:** Fixes missing accents and replaces the technical calque "padre" with "superior", which is natural in Spanish administrative language. If "padre" is preferred for consistency with technical tooling, at minimum the accents must be restored.

---

## patronymic_name

**File:** `schema/properties/patronymic_name.yaml`
**Current:** "Un nombre derivado del nombre de pila del padre de la persona o de un ancestro paterno, utilizado en convenciones de denominacion donde los patronimicos son un componente distinto del nombre completo."
**Source:** "A name derived from the given name of the person's father or a paternal ancestor, used in naming conventions where patronymics are a distinct component of a person's full name."
**Issue:** Missing accent on "denominación". Also "patronimicos" should be "patronímicos" (missing accent). "Ancestro" is acceptable but "antepasado paterno" is more natural in Spanish.
**Proposed:** "Un nombre derivado del nombre de pila del padre de la persona o de un antepasado paterno, utilizado en convenciones de denominación donde los patronímicos son un componente distinto del nombre completo."
**Rationale:** Fixes two missing accents and replaces the Latinism "ancestro" with the more common "antepasado".

---

## phone_number

**File:** `schema/properties/phone_number.yaml`
**Current:** "Un numero de telefono de contacto para la persona, incluido el prefijo del pais."
**Source:** "A contact phone number for the person, including country code."
**Issue:** Missing accents on "número", "teléfono", and "país".
**Proposed:** "Un número de teléfono de contacto para la persona, incluido el prefijo del país."
**Rationale:** Accent restoration only; the phrasing is otherwise natural.

---

## place_type

**File:** `schema/properties/place_type.yaml`
**Current:** "La categoría de lugar donde ocurrió el evento vital (establecimiento de salud, hogar, en camino, etc.). Complementa el Lugar específico al describir qué tipo de entorno era."
**Source:** "The category of place where the vital event occurred (health facility, home, en route, etc.). Complements the specific Location by describing what kind of setting it was."
**Issue:** "Complementa el Lugar específico" capitalises "Lugar" (matching the English "Location" as a concept label). This is inconsistent unless the convention in this project is to capitalise concept names in running Spanish text; in standard Spanish prose, common nouns are lowercase. Check whether capitalisation is intentional here.
**Proposed:** "La categoría de lugar donde ocurrió el evento vital (establecimiento de salud, hogar, en camino, etc.). Complementa la ubicación específica al describir qué tipo de entorno era."
**Rationale:** If concept capitalisation is intentional, keep "Lugar". Otherwise lower-case it and use "la ubicación específica" for natural flow. Flagging for a decision.

---

## postal_code

**File:** `schema/properties/postal_code.yaml`
**Current:** "El codigo postal o codigo zip de la direccion."
**Source:** "The postal or zip code of the address."
**Issue:** Missing accents on "código" (twice) and "dirección".
**Proposed:** "El código postal o código zip de la dirección."
**Rationale:** Accent restoration only.

---

## preferred_name

**File:** `schema/properties/preferred_name.yaml`
**Current:** "El nombre por el que una persona es comunmente conocida, cuando difiere de su nombre legal. Cubre nombres de uso, nombres profesionales y convenciones de denominacion donde nombre y apellido son insuficientes."
**Source:** "The name a person is commonly known by, when it differs from their legal name. Covers chosen names, professional names, and naming conventions where given name plus family name is insufficient."
**Issue:** Missing accent on "comúnmente" and "denominación". Also "nombres de uso" does not translate "chosen names"; "nombres elegidos" or "nombres de elección" is more precise.
**Proposed:** "El nombre por el que una persona es comúnmente conocida, cuando difiere de su nombre legal. Cubre nombres de elección, nombres profesionales y convenciones de denominación donde nombre y apellido son insuficientes."
**Rationale:** Fixes two missing accents and renders "chosen names" more accurately.

---

## primary_crop

**File:** `schema/properties/primary_crop.yaml`
**Current:** "El cultivo o actividad agrícola principal de la granja."
**Source:** "The primary crop or agricultural activity of the farm."
**Issue:** "Granja" is flagged in the project conventions as incorrect; the established term is "Explotación Agrícola".
**Proposed:** "El cultivo o actividad agrícola principal de la explotación agrícola."
**Rationale:** Applies the known convention: "Granja" → "Explotación Agrícola".

---

## recipient

**File:** `schema/properties/recipient.yaml`
**Current:** "La persona o grupo que recibió o está destinada a recibir el pago. El destinatario puede diferir del beneficiario inscrito, por ejemplo cuando un tutor, apoderado de pago o sobreviviente cobra en nombre del beneficiario."
**Source:** "The person or group that received or is intended to receive the payment. The recipient may differ from the enrolled beneficiary, for example when a guardian, payment proxy, or survivor collects on behalf of the beneficiary."
**Issue:** Gender agreement. "La persona o grupo... destinada" uses feminine agreement for "destinada", agreeing with "persona" but ignoring "grupo" (masculine). When the subject is a mixed-gender coordinated noun phrase, the neutral form would be "destinado/a" or the sentence can be restructured.
**Proposed:** "La persona o el grupo que recibió o está destinado a recibir el pago. El destinatario puede diferir del beneficiario inscrito, por ejemplo cuando un tutor, apoderado de pago o sobreviviente cobra en nombre del beneficiario."
**Rationale:** "destinado" agrees with "grupo" (the nearest noun in an or-coordination) and is the more natural choice when "grupo" is included. The rest of the translation is accurate and fluent.

---

## Files with no issues

Clean (no issues found): literacy, longitude, manner_of_death, marriage_ref, matronymic_name, medical_certifier, member_count, memberships, mother, name, nationality, nationality_at_birth, number_of_spouses, object_person, occupation, parental_role, parents, party_1, party_2, payment_amount, payment_currency, payment_date, payment_status, person, place_of_usual_residence, preferred_language, previous_parents, program_ref, quantity, quantity_redeemed, raw_score, receiving_program
