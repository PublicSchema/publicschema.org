# Review: ES properties (batch C: family_name_at_birth through latitude)

---

## farm_area_hectares.yaml
Overall: Issue with the known convention.

### Issue 1
- **File:** farm_area_hectares.yaml
- **Current (es):** `La superficie total de la granja en hectáreas.`
- **Source (en):** `The total area of the farm in hectares.`
- **Issue:** Uses "granja" instead of the established project convention "Explotación Agrícola". The French correctly uses "exploitation agricole".
- **Proposed:** `La superficie total de la explotación agrícola en hectáreas.`
- **Rationale:** Project convention explicitly flags "Granja" → "Explotación Agrícola". "Granja" carries a narrower connotation (a livestock or small farm) and is inconsistent with how the Farm concept is named across the project.

---

## gender.yaml
Overall: Missing accent marks throughout.

### Issue 1
- **File:** gender.yaml
- **Current (es):** `El genero de la persona tal como se registra en un registro de proteccion social o documento de identidad.`
- **Source (en):** `The gender of the person as recorded in a social protection registry or identity document.`
- **Issue:** Multiple missing accents: "genero" → "género", "proteccion" → "protección". The word "registro" is correct in this context (registry), but the accent omissions make the text look unfinished on a public website.
- **Proposed:** `El género de la persona tal como se registra en un registro de protección social o documento de identidad.`
- **Rationale:** "Género" and "protección" require written accents in Spanish. Without them the text fails basic orthographic standards.

---

## geocodes.yaml
Overall: Missing accents.

### Issue 1
- **File:** geocodes.yaml
- **Current (es):** `Codigos administrativos o estadisticos que identifican esta area dentro de un sistema de codificacion (FIPS, P-code, codigo postal, etc.).`
- **Source (en):** `Administrative or statistical codes that identify this area within a coding system (FIPS, P-code, postal code, etc.).`
- **Issue:** Missing accents: "Codigos" → "Códigos", "estadisticos" → "estadísticos", "area" → "área", "codificacion" → "codificación", "codigo" → "código".
- **Proposed:** `Códigos administrativos o estadísticos que identifican esta área dentro de un sistema de codificación (FIPS, P-code, código postal, etc.).`
- **Rationale:** Five accent errors in one sentence. All are standard orthographic requirements, not optional.

---

## geometry.yaml
Overall: Missing accent.

### Issue 1
- **File:** geometry.yaml
- **Current (es):** `El limite o forma geografica, expresado como un objeto GeoJSON Geometry (Point, Polygon, MultiPolygon, etc.).`
- **Source (en):** `The geographic boundary or shape, expressed as a GeoJSON Geometry object (Point, Polygon, MultiPolygon, etc.).`
- **Issue:** Missing accents: "limite" → "límite", "geografica" → "geográfica".
- **Proposed:** `El límite o forma geográfica, expresado como un objeto GeoJSON Geometry (Point, Polygon, MultiPolygon, etc.).`
- **Rationale:** Standard accent requirements.

---

## grievance_status.yaml
Overall: Terminology concern.

### Issue 1
- **File:** grievance_status.yaml
- **Current (es):** `El estado actual de procesamiento del agravio.`
- **Source (en):** `The current processing state of the grievance.`
- **Issue:** "Agravio" is a valid translation of "grievance" but in social protection administrative contexts, "reclamación" or "queja" is more commonly used. "Agravio" can imply personal offense or legal harm, which is stronger than the operational concept. Consistency also matters: other grievance properties use "agravio" (grievance_subject, grievance_type), so if a change is made it should be applied uniformly. Flag for project-level terminology decision.
- **Proposed (if convention changes):** `El estado actual de tramitación de la reclamación.`
- **Rationale:** "Tramitación" is more precise than "procesamiento" for administrative processing; "reclamación" is standard in social protection contexts across Spanish-speaking administrations. This is a terminology note for team review, not a clear-cut error.

---

## grievance_subject.yaml
Overall: Same "agravio" terminology note as above; otherwise clean.

### Issue 1
- **File:** grievance_subject.yaml
- **Current (es):** `Referencia a la persona, inscripción o evento de pago al que se refiere el agravio.`
- **Source (en):** `Reference to the person, enrollment, or payment event that the grievance concerns.`
- **Issue:** Redundant construction: "al que se refiere" repeats the idea already conveyed by "Referencia a". Minor readability issue.
- **Proposed:** `Referencia a la persona, inscripción o evento de pago que atañe al agravio.`
- **Rationale:** Eliminates the tautology. "Que atañe a" (that concerns) is concise and idiomatic. If "agravio" is changed project-wide, update here too.

---

## grievance_type.yaml
Overall: Awkward participial phrase.

### Issue 1
- **File:** grievance_type.yaml
- **Current (es):** `La categoría de agravio o queja, clasificando la naturaleza del problema planteado.`
- **Source (en):** `The category of grievance or complaint, classifying the nature of the issue raised.`
- **Issue:** The participial phrase "clasificando la naturaleza del problema planteado" dangles slightly. In Spanish, a present participle used this way should describe an action by the subject, but a noun (categoría) cannot "classify". The French version avoids this: "classifiant la nature du problème soulevé" — but the same criticism applies there.
- **Proposed:** `La categoría de agravio o queja que clasifica la naturaleza del problema planteado.`
- **Rationale:** Converting to a relative clause ("que clasifica") makes the sentence grammatically sound. The category is what does the classifying.

---

## group_memberships.yaml
Overall: Missing accents; word choice note.

### Issue 1
- **File:** group_memberships.yaml
- **Current (es):** `Membresias de grupos que posee esta persona, vinculandola con hogares, familias u otros grupos.`
- **Source (en):** `Group memberships held by this person, linking them to households, families, or other groups.`
- **Issue:** Missing accents: "Membresias" → "Membresías", "vinculandola" → "vinculándola". Also "membresías" is a Latinism/anglicism; "pertenencias a grupos" or "afiliaciones a grupos" may be more natural in formal administrative Spanish.
- **Proposed:** `Membresías de grupos que posee esta persona, vinculándola con hogares, familias u otros grupos.`
- **Rationale:** Accent correction is required. "Membresías" is widely used in LatAm administrative contexts and is acceptable, so no change proposed to the noun itself — but the accents must be present.

---

## group_type.yaml
Overall: Missing accent.

### Issue 1
- **File:** group_type.yaml
- **Current (es):** `La categoria administrativa o social del grupo.`
- **Source (en):** `The administrative or social category of the group.`
- **Issue:** Missing accent: "categoria" → "categoría".
- **Proposed:** `La categoría administrativa o social del grupo.`
- **Rationale:** Standard accent requirement.

---

## hazard_type.yaml
Overall: Missing accent.

### Issue 1
- **File:** hazard_type.yaml
- **Current (es):** `La categoria de peligro o evento perturbador.`
- **Source (en):** `The category of hazard or disruptive event.`
- **Issue:** Missing accent: "categoria" → "categoría".
- **Proposed:** `La categoría de peligro o evento perturbador.`
- **Rationale:** Standard accent requirement.

---

## house_number.yaml
Overall: Missing accents.

### Issue 1
- **File:** house_number.yaml
- **Current (es):** `El numero de casa, edificio o parcela dentro de una calle o carretera.`
- **Source (en):** `The house, building, or plot number within a street or road.`
- **Issue:** Missing accent: "numero" → "número".
- **Proposed:** `El número de casa, edificio o parcela dentro de una calle o carretera.`
- **Rationale:** Standard accent requirement.

---

## identifier_scheme_id.yaml
Overall: Missing accent.

### Issue 1
- **File:** identifier_scheme_id.yaml
- **Current (es):** `Un URI o codigo que identifica el esquema o sistema bajo el cual se asigno el identificador.`
- **Source (en):** `A URI or code that identifies the scheme or system under which the identifier was assigned.`
- **Issue:** Missing accents: "codigo" → "código", "asigno" → "asignó".
- **Proposed:** `Un URI o código que identifica el esquema o sistema bajo el cual se asignó el identificador.`
- **Rationale:** Both require accents: "código" (noun) and "asignó" (preterite third-person singular, distinguishing it from "asigno" present first-person).

---

## identifier_scheme_name.yaml
Overall: Missing accents.

### Issue 1
- **File:** identifier_scheme_name.yaml
- **Current (es):** `El nombre legible del esquema de identificacion, como 'Numero de identidad nacional' o 'Numero de seguridad social'.`
- **Source (en):** `The human-readable name of the identifier scheme, such as 'National Identity Number' or 'Social Security Number'.`
- **Issue:** Missing accents: "identificacion" → "identificación", "Numero" → "Número" (appears twice).
- **Proposed:** `El nombre legible del esquema de identificación, como 'Número de identidad nacional' o 'Número de seguridad social'.`
- **Rationale:** Three accent errors. All standard orthographic requirements.

---

## identifier_type.yaml
Overall: Missing accent.

### Issue 1
- **File:** identifier_type.yaml
- **Current (es):** `La categoria del documento o numero de identificacion.`
- **Source (en):** `The category of identifier document or number.`
- **Issue:** Missing accents: "categoria" → "categoría", "numero" → "número", "identificacion" → "identificación".
- **Proposed:** `La categoría del documento o número de identificación.`
- **Rationale:** Three accent errors in a short sentence.

---

## identifier_value.yaml
Overall: Missing accent.

### Issue 1
- **File:** identifier_value.yaml
- **Current (es):** `El valor alfanumerico del identificador tal como fue emitido o registrado.`
- **Source (en):** `The alphanumeric value of the identifier as issued or recorded.`
- **Issue:** Missing accent: "alfanumerico" → "alfanumérico".
- **Proposed:** `El valor alfanumérico del identificador tal como fue emitido o registrado.`
- **Rationale:** Standard accent requirement.

---

## is_active.yaml
Overall: Awkward construction.

### Issue 1
- **File:** is_active.yaml
- **Current (es):** `Si esto está actualmente activo.`
- **Source (en):** `Whether this is currently active.`
- **Issue:** "Si esto está actualmente activo" is a literal calque that reads as a yes/no question fragment rather than a definition. The English "whether" introduces a state, not a question. "Esto" is also overly vague in isolation. The French "Si ceci est actuellement actif" has the same problem.
- **Proposed:** `Indica si el registro está actualmente activo.`
- **Rationale:** Adding "Indica si" turns the fragment into a complete definitional sentence. "El registro" is more concrete than "esto", though this property is generic by design — "el elemento" or "el registro" can be substituted depending on context. The pattern matches other boolean properties in the schema (see is_enrolled.yaml and is_reconciled.yaml which use "Indica si").

---

## issue_date.yaml
Overall: Missing accent.

### Issue 1
- **File:** issue_date.yaml
- **Current (es):** `La fecha en que se emitio este registro o documento.`
- **Source (en):** `The date on which this record or document was issued.`
- **Issue:** Missing accent: "emitio" → "emitió" (preterite third-person singular).
- **Proposed:** `La fecha en que se emitió este registro o documento.`
- **Rationale:** Accent required to mark preterite, distinguishing from present "emitio" (not a valid form but the reader may misparse).

---

## issuing_authority.yaml
Overall: Missing accents.

### Issue 1
- **File:** issuing_authority.yaml
- **Current (es):** `La organizacion o entidad gubernamental que emitio el identificador.`
- **Source (en):** `The organization or government body that issued the identifier.`
- **Issue:** Missing accents: "organizacion" → "organización", "emitio" → "emitió".
- **Proposed:** `La organización o entidad gubernamental que emitió el identificador.`
- **Rationale:** Standard accent requirements on two words.

---

## issuing_jurisdiction.yaml
Overall: Missing accents.

### Issue 1
- **File:** issuing_jurisdiction.yaml
- **Current (es):** `La jurisdiccion geografica que emitio el identificador, expresada como un codigo de subdivision ISO 3166-2 o un codigo de pais ISO 3166-1.`
- **Source (en):** `The geographic jurisdiction that issued the identifier, expressed as an ISO 3166-2 subdivision code or ISO 3166-1 country code.`
- **Issue:** Missing accents: "jurisdiccion" → "jurisdicción", "geografica" → "geográfica", "emitio" → "emitió", "codigo" → "código" (twice), "subdivision" → "subdivisión", "pais" → "país".
- **Proposed:** `La jurisdicción geográfica que emitió el identificador, expresada como un código de subdivisión ISO 3166-2 o un código de país ISO 3166-1.`
- **Rationale:** Seven accent errors in one sentence. Systematic omission suggests this was produced without accent support and never proofread.

---

## items.yaml
Overall: Missing accents.

### Issue 1
- **File:** items.yaml
- **Current (es):** `La lista de lineas de productos en esta entrega o vale.`
- **Source (en):** `The list of commodity line items in this delivery or voucher.`
- **Issue:** Missing accent: "lineas" → "líneas".
- **Proposed:** `La lista de líneas de productos en esta entrega o vale.`
- **Rationale:** Standard accent requirement.

---

## latitude.yaml
Overall: Missing accents.

### Issue 1
- **File:** latitude.yaml
- **Current (es):** `La latitud geografica en grados decimales (WGS84).`
- **Source (en):** `The geographic latitude in decimal degrees (WGS84).`
- **Issue:** Missing accent: "geografica" → "geográfica".
- **Proposed:** `La latitud geográfica en grados decimales (WGS84).`
- **Rationale:** Standard accent requirement.

---

## Files reviewed without issues

The following files had clean Spanish translations with no issues to flag:

- **family_name_at_birth.yaml** — Accurate, fluent, accents correct.
- **family_register_status.yaml** — Accurate, fluent, accents correct.
- **formation_date.yaml** — Acceptable; accent-free text is simple enough not to have any.
- **framework_used.yaml** — Clean.
- **frequency.yaml** — Clean. "única vez" for "one-time" is idiomatic.
- **frequency_rule.yaml** — Clean. Technical tokens (RRULE, RFC 5545, 'custom') correctly preserved.
- **full_address.yaml** — Missing accents ("direccion" → "dirección", "componentes...de la direccion" → "de la dirección") but let me note these were not caught initially.
- **gestational_age.yaml** — Clean, accents correct. "CIE-PM" correctly used over "ICD-PM".
- **given_name.yaml** — Clean. "Nombre de pila" is the correct idiomatic term.
- **given_name_at_birth.yaml** — Clean.
- **governing_jurisdiction.yaml** — Clean. Accents absent but source text had none to require.
- **group.yaml** — Clean.
- **head_of_household.yaml** — Clean. Correct accent placement throughout.
- **identifiers.yaml** — Clean. Accents present and correct.
- **implementing_agency.yaml** — Clean.
- **income_source.yaml** — Clean. "Focalización" for "targeting" and "pruebas de medios indirectos" for "proxy means testing" are acceptable.
- **industry.yaml** — Clean. "CIIU Rev.4" correctly used for the Spanish-language name of ISIC.
- **informant.yaml** — Clean. "Padre o madre" (not "padre" alone) for "parent" is good inclusive usage.
- **is_enrolled.yaml** — Clean. Consistent pattern with "Indica si".
- **is_reconciled.yaml** — Clean. "Cotejado" for "matched/reconciled" is precise.
- **issued_to.yaml** — Clean.
- **issuing_authority_location.yaml** — Clean. Accents correct, technical terms preserved.
- **issuing_office.yaml** — Clean.
- **judgment_date.yaml** — Clean. Accents correct.
- **judgment_reference.yaml** — Clean. Accents correct.

---

## Addendum: full_address.yaml (missed above)

### Issue 1
- **File:** full_address.yaml
- **Current (es):** `La direccion completa escrita como una sola cadena de texto. Coexiste con los componentes estructurados de la direccion para los sistemas que almacenan direcciones como texto libre.`
- **Source (en):** `The complete address written as a single text string. Coexists with structured address components for systems that store addresses as free text.`
- **Issue:** Missing accents: "direccion" → "dirección" (three times).
- **Proposed:** `La dirección completa escrita como una sola cadena de texto. Coexiste con los componentes estructurados de la dirección para los sistemas que almacenan direcciones como texto libre.`
- **Rationale:** Standard accent requirement, missed in initial scan.

---

## Summary

The dominant problem across this batch is **systematic omission of required accent marks** across many files, strongly suggesting these translations were generated without accent support and not proofread. Files affected: gender, geocodes, geometry, group_memberships, group_type, hazard_type, house_number, identifier_scheme_id, identifier_scheme_name, identifier_type, identifier_value, issuing_authority, issuing_jurisdiction, items, latitude, full_address, issue_date.

Other issues:
- **farm_area_hectares:** "granja" violates the established "Explotación Agrícola" convention.
- **grievance_type:** Dangling participle ("clasificando").
- **is_active:** Literal calque fragment; inconsistent with the "Indica si" pattern used in is_enrolled and is_reconciled.
- **grievance_status / grievance_subject / grievance_type:** "Agravio" vs. "reclamación" is a project-level terminology decision worth making explicitly.
- **grievance_subject:** Tautological "Referencia ... al que se refiere".
