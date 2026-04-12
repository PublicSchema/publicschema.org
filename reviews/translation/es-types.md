# Spanish translation review: TypesContent

Scope: review of the Spanish (`es`) translation of the Types reference page (`TypesContent.es.astro`) against the English source (`TypesContent.en.astro`), covering data types used across the PublicSchema vocabulary (string, integer, decimal, boolean, date, datetime, uri, geojson_geometry).

---

## Flags

**Line 16**
- **Current:** `Un número entero sin componente fraccional.`
- **Issue:** "componente fraccional" is a calque of "fractional component"; the established Spanish technical phrasing is "parte decimal" or "parte fraccionaria".
- **Proposed:** `Un número entero sin parte decimal.`
- **Rationale:** "parte decimal" is the term used in Spanish-language computing and mathematics education across both regions; "componente fraccional" reads as translated from English.

---

**Line 19**
- **Current:** `Entero con signo (sin punto decimal)`
- **Issue:** Minor but noteworthy: "entero con signo" is technically correct and widely used; no change needed here. However, the parenthetical "(sin punto decimal)" is a calque of "(no decimal point)" and the more natural Spanish phrasing would clarify the absence of a fractional separator.
- **Proposed:** `Entero con signo (sin parte fraccionaria)`
- **Rationale:** "sin punto decimal" could be read as "does not use a period as separator" (ambiguous in regions that use a comma as decimal separator); "sin parte fraccionaria" is semantically unambiguous.

---

**Line 28**
- **Current:** `Un valor numérico que puede incluir un componente fraccional.`
- **Issue:** Same calque as line 16: "componente fraccional" for "fractional component".
- **Proposed:** `Un valor numérico que puede incluir una parte fraccionaria.`
- **Rationale:** Consistent with the fix proposed for line 16; "parte fraccionaria" is the standard Spanish term.

---

**Line 34**
- **Current:** `Para montos monetarios, combinar con una propiedad <code>currency</code> (código ISO 4217).`
- **Issue:** The verb "combinar" is an infinitive used as an imperative, which is acceptable in instructional Spanish but is slightly impersonal; more critically, the sentence has no subject, making it an implicit command that lacks the formal register established by the rest of the text. The English source uses "pair with", an imperative addressed to the implementer.
- **Proposed:** `Para montos monetarios, combine esta propiedad con <code>currency</code> (código ISO 4217).`
- **Rationale:** Using the formal imperative "combine" (usted) maintains the formal register; adding "esta propiedad" clarifies the referent, which is missing in the current version.

---

**Line 41**
- **Current:** `Un valor verdadero/falso.`
- **Issue:** "verdadero/falso" is a calque of "true/false". In Spanish technical documentation, the standard rendering is "verdadero o falso" (using "o" rather than a slash) or, where the literal code values matter, leaving them in English as `true`/`false`. Using a slash here mimics English typographic convention.
- **Proposed:** `Un valor de tipo verdadero o falso.`
- **Rationale:** "verdadero o falso" reads naturally in Spanish; "de tipo" clarifies it is describing a data type, which matches the technical register of the surrounding entries.

---

**Line 52**
- **Current:** `Una fecha de calendario sin componente de hora.`
- **Issue:** "componente de hora" is a calque of "time-of-day component". The natural Spanish term for the time portion of a date-time value is "componente horario" or simply "hora".
- **Proposed:** `Una fecha de calendario sin componente horario.`
- **Rationale:** "componente horario" is the standard adjective form used in Spanish-language technical and standards documentation (ISO translations included).

---

**Line 64**
- **Current:** `Una fecha combinada con un componente de hora.`
- **Issue:** Same issue as line 52: "componente de hora" is a calque; also inconsistency risk if line 52 is fixed but this line is not.
- **Proposed:** `Una fecha combinada con un componente horario.`
- **Rationale:** Consistency with the fix to line 52 and natural Spanish technical vocabulary.

---

**Line 70**
- **Current:** `Las horas locales sin zona horaria son ambiguas.`
- **Issue:** The source says "Bare local times are ambiguous." The word "bare" carries a specific technical connotation (a local time with no timezone annotation). "Las horas locales sin zona horaria" is technically correct but slightly redundant: a local time is by definition without a timezone. The more precise term used in standards contexts is "hora local no calificada" or "sin indicador de zona horaria".
- **Proposed:** `Las horas locales sin indicador de zona horaria son ambiguas.`
- **Rationale:** "indicador de zona horaria" (timezone indicator/offset) is more precise and mirrors the phrasing used in Spanish translations of RFC and ISO 8601 materials; it makes clear that the problem is the absence of an annotation, not the time value itself.

---

**Line 70 (also)**
- **Current:** `Incluir siempre un desplazamiento de zona horaria o usar UTC (<code>Z</code>).`
- **Issue:** "desplazamiento de zona horaria" is a literal calque of "timezone offset". The standard Spanish term is "desfase horario" or "desplazamiento horario" (without "de zona"); "desfase de zona horaria" also appears in standards contexts but "desplazamiento de zona horaria" is the most calqued form.
- **Proposed:** `Incluir siempre un desfase horario o usar UTC (<code>Z</code>).`
- **Rationale:** "desfase horario" is the term used in Spanish-language RFC and ISO translations for UTC offset; it is shorter and unambiguous.

---

**Line 77**
- **Current:** `Un Identificador Uniforme de Recursos.`
- **Issue:** This is technically correct and matches the official Spanish expansion of "URI" used by W3C and IANA documentation in Spanish. No substantive error, but it is worth noting that "Identificador de Recursos Uniforme" (IRU) also appears in some Spanish standards documents. The W3C Spanish translation uses "Identificador Uniforme de Recursos", so the current rendering is acceptable and consistent with that authority.
- **Proposed:** No change required.
- **Rationale:** Confirmed against W3C Spanish terminology.

---

**Line 89**
- **Current:** `Una forma geográfica expresada como un objeto Geometry de <a ...>GeoJSON</a>. Admite Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon y GeometryCollection.`
- **Issue:** Leaving all GeoJSON geometry type names untranslated is correct and expected (they are proper names defined by the GeoJSON spec). "Admite" is accurate and natural. No issue here.
- **Proposed:** No change required.
- **Rationale:** Technical proper nouns from a named specification are appropriately left in English.

---

**Line 58 (date Note)**
- **Current:** `Los sistemas que solo conocen el año de nacimiento pueden usar <code>YYYY</code> o <code>YYYY-01-01</code> con un calificador de precisión.`
- **Issue:** "calificador de precisión" is a near-calque of "precision qualifier". In Spanish-language metadata and data quality standards, "indicador de precisión" or "cualificador de precisión" are both used; "cualificador" is more commonly found in ISO metadata translations (ISO 19115, DCAT-AP-ES). Both are acceptable but "cualificador" is more standard in this domain.
- **Proposed:** `Los sistemas que solo conocen el año de nacimiento pueden usar <code>YYYY</code> o <code>YYYY-01-01</code> con un cualificador de precisión.`
- **Rationale:** "cualificador" aligns with ISO metadata vocabulary in Spanish; "calificador" is not wrong but is less standard in this technical context.

---

## Overall impression

The translation is solid overall: the structure is faithful, the formal register is maintained throughout, and the technical proper nouns (GeoJSON types, RFC references, ISO standard names) are handled correctly by leaving them in English. The main recurring weakness is the use of "componente fraccional" / "componente de hora" where established Spanish technical terms ("parte fraccionaria", "componente horario") are available and preferable. A smaller secondary issue is the use of the bare infinitive as an imperative in the decimal Note (line 34), which loses the formal usted register that the surrounding text implies; switching to the formal imperative form resolves this consistently.
