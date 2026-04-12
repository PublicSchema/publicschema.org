# Review: ES property definitions — batch A (address to commodity_type)

Files reviewed: address, address_area, administrative_area, administrative_level, adoptee, adoption_type, adoptive_parents, affected_locations, affected_programs, age_at_event, altitude_max, altitude_min, amount, annotating_authority, annotation_date, annotation_text, annotation_type, annotations, applicant, area_description, assessed_entity, assessment_date, assessor, attendant_at_birth, beneficiary, benefit_description, benefit_modality, birth_order, birth_ref, birth_type, building_name, cause_of_death, cause_of_death_code, cause_of_death_coding_system, cause_of_death_method, cause_of_fetal_death, cause_of_fetal_death_code, cause_of_fetal_death_coding_system, certainty, certificate_document_type, certificate_format, certificate_number, child, city, civil_status_record, commodity_type

---

## address.yaml

No issues.

---

## address_area.yaml

### Issue 1
- **File:** `schema/properties/address_area.yaml`
- **Current:** `El nombre de un area geografica como un barrio o sector que agrupa direcciones por debajo del nivel de la ciudad.`
- **Source:** `The name of a geographic area such as a neighborhood, quarter, or ward that groups addresses below the city level.`
- **Issue:** Three accent marks stripped: "area" should be "área", "geografica" should be "geográfica". Also, the English lists three examples (neighborhood, quarter, ward) but the Spanish gives only two (barrio, sector), dropping "ward". "Sector" is a reasonable substitute but the omission is minor.
- **Proposed:** `El nombre de un área geográfica como un barrio, sector o circunscripción que agrupa direcciones por debajo del nivel de la ciudad.`
- **Rationale:** Restores accents and adds a third example ("circunscripción") to preserve the rhetorical weight of three distinct examples. "Circunscripción" is the standard Spanish term for administrative ward.

---

## administrative_area.yaml

### Issue 1
- **File:** `schema/properties/administrative_area.yaml`
- **Current:** `La primera subdivision administrativa (provincia, estado, region) que contiene la direccion.`
- **Source:** `The first-level administrative subdivision (province, state, region) containing the address.`
- **Issue:** Three accent marks stripped: "subdivisión", "región", "dirección".
- **Proposed:** `La primera subdivisión administrativa (provincia, estado, región) que contiene la dirección.`
- **Rationale:** Orthographic correction only.

---

## administrative_level.yaml

### Issue 1
- **File:** `schema/properties/administrative_level.yaml`
- **Current:** `El nivel numerico en la jerarquia administrativa, segun la convencion OCHA COD-AB: 0 = pais, 1 = primer nivel subnacional (estado, provincia, region), 2 = segundo nivel subnacional (distrito, condado, departamento), y asi sucesivamente. Sin profundidad maxima fija.`
- **Source:** `The numeric tier in the administrative hierarchy, following the OCHA COD-AB convention: 0 = country, 1 = first subnational (state, province, region), 2 = second subnational (district, county, department), and so on. No fixed maximum depth.`
- **Issue:** Eight accent marks stripped: "numérico", "jerarquía", "según", "convención", "país", "región", "así", "máxima".
- **Proposed:** `El nivel numérico en la jerarquía administrativa, según la convención OCHA COD-AB: 0 = país, 1 = primer nivel subnacional (estado, provincia, región), 2 = segundo nivel subnacional (distrito, condado, departamento), y así sucesivamente. Sin profundidad máxima fija.`
- **Rationale:** Orthographic correction only.

---

## adoptee.yaml

No issues.

---

## adoption_type.yaml

No issues.

---

## adoptive_parents.yaml

No issues.

---

## affected_locations.yaml

### Issue 1
- **File:** `schema/properties/affected_locations.yaml`
- **Current:** `Las areas geograficas o administrativas afectadas por este evento.`
- **Source:** `The geographic or administrative areas affected by this event.`
- **Issue:** Two accent marks stripped: "áreas", "geográficas".
- **Proposed:** `Las áreas geográficas o administrativas afectadas por este evento.`
- **Rationale:** Orthographic correction only.

---

## affected_programs.yaml

No issues.

---

## age_at_event.yaml

### Issue 1
- **File:** `schema/properties/age_at_event.yaml`
- **Current:** `La edad declarada de la persona al momento del evento vital. Utilizado en contextos de baja completitud donde la fecha de nacimiento es desconocida y la edad declarada es el único dato de edad disponible.`
- **Source:** `The stated age of the person at the time of the vital event. Used in low-completeness settings where date of birth is unknown and stated age is the only age data available.`
- **Issue:** "Utilizado" does not agree with the implied subject of the second sentence. The sentence opens a new clause and "Utilizado" functions as a past participle modifying an implicit subject; agreement with the sentence structure calls for "Utilizada" (agreeing with "la edad") or better yet a full verbal construction. Separately, "baja completitud" is a direct calque of the English technical term "low-completeness" and reads as jargon; the French version avoids this.
- **Proposed:** `La edad declarada de la persona al momento del evento vital. Se utiliza en contextos de registro incompleto donde se desconoce la fecha de nacimiento y la edad declarada es el único dato de edad disponible.`
- **Rationale:** "Se utiliza" removes the agreement ambiguity. "Contextos de registro incompleto" replaces the calque "baja completitud" with plain language that policy practitioners will recognise.

---

## altitude_max.yaml

### Issue 1
- **File:** `schema/properties/altitude_max.yaml`
- **Current:** `La altitud maxima del area, en metros sobre el nivel del mar (datum WGS84).`
- **Source:** `The maximum altitude of the area, in meters above sea level (WGS84 datum).`
- **Issue:** Two accent marks stripped: "máxima", "área".
- **Proposed:** `La altitud máxima del área, en metros sobre el nivel del mar (datum WGS84).`
- **Rationale:** Orthographic correction only.

---

## altitude_min.yaml

### Issue 1
- **File:** `schema/properties/altitude_min.yaml`
- **Current:** `La altitud minima del area, en metros sobre el nivel del mar (datum WGS84).`
- **Source:** `The minimum altitude of the area, in meters above sea level (WGS84 datum).`
- **Issue:** Two accent marks stripped: "mínima", "área".
- **Proposed:** `La altitud mínima del área, en metros sobre el nivel del mar (datum WGS84).`
- **Rationale:** Orthographic correction only.

---

## amount.yaml

No issues.

---

## annotating_authority.yaml

No issues.

---

## annotation_date.yaml

No issues.

---

## annotation_text.yaml

No issues.

---

## annotation_type.yaml

### Issue 1
- **File:** `schema/properties/annotation_type.yaml`
- **Current:** `La categoría de anotación: corrección ordenada por tribunal, cambio de nacionalidad u otras modificaciones administrativas que afectan el alcance del acta.`
- **Source:** `The category of annotation: a court-ordered correction, a nationality change, or similar administrative modifications to the record's meaning.`
- **Issue:** "Alcance" means scope or reach; the English says "meaning" ("the record's meaning"). "Alcance del acta" implies the record's coverage or jurisdiction, not its semantic content. This is a subtle but meaningful drift for domain practitioners who distinguish a record's scope from its meaning.
- **Proposed:** `La categoría de anotación: corrección ordenada por tribunal, cambio de nacionalidad u otras modificaciones administrativas que afectan el contenido o significado del acta.`
- **Rationale:** "Contenido o significado" more faithfully renders "meaning" in the context of a civil status record.

---

## annotations.yaml

No issues.

---

## applicant.yaml

No issues.

---

## area_description.yaml

### Issue 1
- **File:** `schema/properties/area_description.yaml`
- **Current:** `Una descripcion legible del area geografica, como un nombre de region o una etiqueta de limite administrativo.`
- **Source:** `A human-readable description of the geographic area, such as a region name or administrative boundary label.`
- **Issue:** Four accent marks stripped: "descripción", "área", "geográfica", "región", "límite".
- **Proposed:** `Una descripción legible del área geográfica, como un nombre de región o una etiqueta de límite administrativo.`
- **Rationale:** Orthographic correction only.

---

## assessed_entity.yaml

No issues.

---

## assessment_date.yaml

No issues.

---

## assessor.yaml

No issues.

---

## attendant_at_birth.yaml

### Issue 1
- **File:** `schema/properties/attendant_at_birth.yaml`
- **Current:** `El tipo de persona que atendió el parto (médico, partera, enfermería, partera tradicional, otro o ninguno).`
- **Source:** `The type of person who attended the delivery (physician, midwife, nurse, traditional birth attendant, other, or none).`
- **Issue (a):** "Enfermería" is the nursing profession or ward, not a nurse. The English lists a person type ("nurse"), not a discipline. The French correctly uses "infirmier" (a person). "Enfermería" here reads as a category error.
- **Issue (b):** The English uses two distinct terms: "midwife" and "traditional birth attendant". The Spanish renders these as "partera" and "partera tradicional". In much of Latin America "partera" already implies a traditional birth attendant, making the distinction between the two entries harder to read. The French avoids this by using "sage-femme" (trained midwife) versus "accoucheuse traditionnelle" (traditional attendant).
- **Proposed:** `El tipo de persona que atendió el parto (médico, partera profesional, enfermero/a, partera tradicional, otro o ninguno).`
- **Rationale:** "Partera profesional" distinguishes the trained midwife from the traditional attendant. "Enfermero/a" designates the person, not the discipline. Both fixes align with the French model and preserve the intended clinical distinction.

---

## beneficiary.yaml

No issues.

---

## benefit_description.yaml

No issues.

---

## benefit_modality.yaml

No issues.

---

## birth_order.yaml

No issues.

---

## birth_ref.yaml

No issues.

---

## birth_type.yaml

No issues.

---

## building_name.yaml

### Issue 1
- **File:** `schema/properties/building_name.yaml`
- **Current:** `El nombre de un edificio, finca o complejo, utilizado en contextos donde las ubicaciones se identifican por nombre en lugar de por numero de calle.`
- **Source:** `The name of a building, estate, or compound, used in contexts where locations are identified by name rather than street number.`
- **Issue:** Accent mark stripped: "número".
- **Proposed:** `El nombre de un edificio, finca o complejo, utilizado en contextos donde las ubicaciones se identifican por nombre en lugar de por número de calle.`
- **Rationale:** Orthographic correction only.

---

## cause_of_death.yaml

No issues.

---

## cause_of_death_code.yaml

### Issue 1
- **File:** `schema/properties/cause_of_death_code.yaml`
- **Current:** `La causa subyacente de la defunción en forma codificada, típicamente un código CIE-10 o CIE-11.`
- **Source:** `The coded underlying cause of death, typically an ICD-10 or ICD-11 code.`
- **Issue:** "Típicamente" is correct here but the accent is present, so no orthographic issue. The translation is otherwise accurate. No issues.
- **Proposed:** N/A
- **Rationale:** No action needed. (Recorded here for completeness since it was flagged for review.)

No issues.

---

## cause_of_death_coding_system.yaml

No issues.

---

## cause_of_death_method.yaml

No issues.

---

## cause_of_fetal_death.yaml

No issues.

---

## cause_of_fetal_death_code.yaml

No issues.

---

## cause_of_fetal_death_coding_system.yaml

No issues.

---

## certainty.yaml

### Issue 1
- **File:** `schema/properties/certainty.yaml`
- **Current:** `La confianza de que el evento ha ocurrido o ocurrira.`
- **Source:** `The confidence that the event has occurred or will occur.`
- **Issue:** Accent mark stripped: "ocurrirá".
- **Proposed:** `La confianza de que el evento ha ocurrido o ocurrirá.`
- **Rationale:** Orthographic correction only.

---

## certificate_document_type.yaml

No issues.

---

## certificate_format.yaml

No issues.

---

## certificate_number.yaml

No issues.

---

## child.yaml

No issues.

---

## city.yaml

### Issue 1
- **File:** `schema/properties/city.yaml`
- **Current:** `El componente ciudad, pueblo o aldea de la direccion.`
- **Source:** `The city, town, or village component of the address.`
- **Issue:** Accent mark stripped: "dirección".
- **Proposed:** `El componente ciudad, pueblo o aldea de la dirección.`
- **Rationale:** Orthographic correction only.

---

## civil_status_record.yaml

### Issue 1
- **File:** `schema/properties/civil_status_record.yaml`
- **Current:** `Una referencia a un CivilStatusRecord. Utilizada en las anotaciones para apuntar al acta que se anota, y en los certificados para apuntar al acta a partir de la cual se emite el certificado.`
- **Source:** `A reference to a CivilStatusRecord. Used on annotations to point to the record being annotated, and on certificates to point to the record from which the certificate is issued.`
- **Issue:** "Apuntar" (to point, to aim, to jot down) is a calque of the English "point to" and reads as informal or technical jargon in this context. In Spanish legal and administrative writing, the standard construction is "hacer referencia a" or "remitir a".
- **Proposed:** `Una referencia a un CivilStatusRecord. Se utiliza en las anotaciones para remitir al acta que se anota, y en los certificados para remitir al acta a partir de la cual se emite el certificado.`
- **Rationale:** "Remitir a" is the standard formal Spanish construction for cross-referencing documents. It reads naturally to a civil registrar or policy officer.

---

## commodity_type.yaml

No issues.

---

## Summary of issues by type

| Type | Count | Files |
|---|---|---|
| Missing accent marks | 9 | address_area, administrative_area, administrative_level, affected_locations, altitude_max, altitude_min, area_description, building_name, certainty, city |
| Terminology drift / calque | 3 | age_at_event ("baja completitud"), annotation_type ("alcance"), civil_status_record ("apuntar") |
| Person vs. discipline confusion | 1 | attendant_at_birth ("enfermería") |
| Ambiguous term collision | 1 | attendant_at_birth ("partera" used for two distinct roles) |
| Gender/agreement | 1 | age_at_event ("Utilizado") |

**Total issues: 12 across 10 files.**

The most impactful fixes are: (1) attendant_at_birth, where two distinct clinical roles are conflated; (2) age_at_event, where a calque obscures plain-language intent; (3) annotation_type, where "alcance" quietly changes the meaning. The accent-mark issues are widespread and appear to originate from a single stripping pass during generation; they should be fixed in bulk.
