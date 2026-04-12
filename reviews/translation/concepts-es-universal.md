# Review: ES universal concepts

---

## person.yaml
Overall: Clean and accurate. Reads naturally. One minor terminology note.

### Issue 1
- **Current (es):** `los estados operacionales como solicitante o beneficiario son roles transitorios`
- **Source (en):** `operational statuses such as Registrant, Applicant, or Beneficiary are transient roles`
- **Issue:** The English lists three examples (Registrant, Applicant, Beneficiary) but the Spanish gives only two (solicitante, beneficiario), dropping "Registrant". This is missing nuance: "Registrant" is a distinct concept from "Applicant" in this domain and the omission weakens the example set.
- **Proposed:** `los estados operacionales como inscrito, solicitante o beneficiario son roles transitorios`
- **Rationale:** "Registrant" maps well to "inscrito" (or "registrado") in the social protection context. All three examples should be preserved because the sentence is making a conceptual argument, not giving an exhaustive list, and dropping one changes the rhetorical force.

---

## party.yaml
Overall: Acceptable. One minor word choice issue.

### Issue 1
- **Current (es):** `permitiendo referencias que aceptan cualquiera de los dos`
- **Source (en):** `enabling references that accept either`
- **Issue:** "Cualquiera de los dos" is fine but the construction leans slightly informal. More precisely, it reads as "either of the two (options)" which is accurate, but "ambos" (both) would be wrong here. The phrase is correct but could be tightened.
- **Proposed:** `que permite referencias que acepten cualquiera de los dos`
- **Rationale:** Minor: changing the participial construction to a relative clause with subjunctive is more idiomatic in this context ("que permite ... que acepten" rather than "permitiendo ... que aceptan"). The current form is not wrong but the subjunctive better signals possibility/capability rather than a statement of fact.

---

## group.yaml
Overall: Accurate with one terminology concern.

### Issue 1
- **Current (es):** `como Hogar, Familia y Granja`
- **Source (en):** `such as Household, Family, and Farm`
- **Issue:** "Granja" for "Farm" is acceptable in Spain but in LatAm agricultural policy contexts "explotación agrícola" or "unidad productiva" is the standard term. "Granja" typically denotes a small farmstead or poultry/livestock operation, not the broader agricultural unit concept used in social protection registries (which includes smallholders, family farms, plots). This is a terminology drift risk when the concept is presented to policy officers in agricultural-heavy LatAm contexts.
- **Proposed:** `como Hogar, Familia y Explotación Agrícola`
- **Rationale:** "Explotación agrícola" is the term used by FAO, ILO, and most national agricultural censuses across LatAm and Spain. It is neutral across regions and better matches the semantic scope of the concept (any agricultural production unit, not just a small farm building).

### Issue 2
- **Current (es):** `mediante enlaces de pertenencia`
- **Source (en):** `via membership links`
- **Issue:** Mild calque. "Enlaces de pertenencia" translates "membership links" word-for-word. In Spanish the concept reads more naturally as "vínculos de membresía" or simply "relaciones de pertenencia."
- **Proposed:** `a través de relaciones de pertenencia`
- **Rationale:** "Relaciones de pertenencia" is slightly more natural and consistent with the language used in group-membership.yaml ("vínculo" / "pertenezca"). Using "vínculos de membresía" would also be consistent with group-membership.yaml but "membresía" can feel technical; "relaciones de pertenencia" is plain-language friendly.

---

## group-membership.yaml
Overall: Good. Reads naturally. One minor issue.

### Issue 1
- **Current (es):** `(como jefe, cónyuge o dependiente)`
- **Source (en):** `(such as head, spouse, or dependent)`
- **Issue:** "Jefe" for "head" (of household) is common in LatAm administrative language ("jefe de hogar" is standard in census terminology) and is fine. No problem here. The translation is accurate and neutral.

No issues worth flagging beyond the terminology already noted under group.yaml.

---

## household.yaml
Overall: Clean. Accurate and natural.

No issues worth flagging.

---

## family.yaml
Overall: Clean. Accurate and natural.

No issues worth flagging.

---

## identifier.yaml
Overall: Accurate with one terminology inconsistency.

### Issue 1
- **Current (es):** `asignado a una parte (persona o grupo)`
- **Source (en):** `assigned to a party (person or group)`
- **Issue:** "Parte" is a literal translation of "party" (the concept name). However, "parte" in Spanish most commonly means "part" or "section," not "party" in the legal/administrative sense. A policy officer reading this in isolation may be confused. The concept is named "Party" (left in English elsewhere), but the parenthetical "(persona o grupo)" already disambiguates the meaning. The word "parte" could be dropped or replaced.
- **Proposed:** `asignado a una entidad (persona o grupo)`
- **Rationale:** "Entidad" (entity) is the standard term in administrative and legal Spanish for an actor that can hold rights or be registered. It is neutral across regions, clear to policy officers, and avoids the false cognate problem of "parte."

### Issue 2
- **Current (es):** `número de certificado de nacimiento`
- **Source (en):** `birth certificate number`
- **Issue:** Mildly awkward word order. In Spanish administrative language the standard phrase is "número de acta de nacimiento" (LatAm) or "número de certificado de nacimiento" (Spain). The current form matches Spain usage but "acta de nacimiento" is significantly more common across LatAm. This is a register/region issue.
- **Proposed:** `número de registro de nacimiento`
- **Rationale:** "Registro de nacimiento" is understood in both Spain and LatAm and avoids the acta/certificado split. Alternatively, if a single region term must be chosen, the French version uses "acte de naissance" which aligns with "acta de nacimiento" (LatAm). This is a low-priority flag but worth noting for cross-regional neutrality.

---

## relationship.yaml
Overall: Good. One calque issue.

### Issue 1
- **Current (es):** `apoderado de pago`
- **Source (en):** `payment proxy`
- **Issue:** "Apoderado de pago" is accurate and widely used in LatAm legal/financial contexts (apoderado = proxy/attorney-in-fact). This is fine in LatAm but in Spain "representante de pago" or "mandatario" is more common. "Apoderado" is comprehensible across regions but slightly LatAm-coded in formal administrative language.
- **Proposed:** Keep "apoderado de pago" — it is the most precise term for this concept and is understood in both regions. The slight regional coloring is acceptable given there is no fully neutral equivalent.
- **Rationale:** Flagged for awareness only; no change recommended.

### Issue 2
- **Current (es):** `Un vínculo que define la conexión social, legal o administrativa`
- **Source (en):** `A link defining the social, legal, or administrative connection`
- **Issue:** "Conexión" is a mild Anglicism in formal administrative Spanish. The more native term is "relación" or "vínculo." Using "vínculo" for the concept and then "conexión" within the definition creates inconsistency within the same sentence.
- **Proposed:** `Un vínculo que define la relación social, legal o administrativa entre un individuo y otra persona o grupo.`
- **Rationale:** "Relación" is the standard term in administrative Spanish for a legal or social link between persons. Replacing "conexión" with "relación" removes the Anglicism and is internally consistent with "vínculo."

---

## address.yaml
Overall: Missing accent marks throughout. This appears to be an encoding or authoring issue affecting the entire `definition.es` block. The translation content itself is accurate, but every word requiring an accent is missing it. This makes the text incorrect in Spanish orthography and unpublishable as-is.

### Issue 1
- **Current (es):** `Una ubicacion fisica o postal estructurada utilizada para contactar a una persona, hogar u organizacion. Las direcciones combinan componentes espaciales y administrativos como calle, localidad, distrito y codigo postal.`
- **Source (en):** `A structured physical or postal location used to reach a person, household, or organization. Addresses combine spatial and administrative components such as street, settlement, district, and postal code.`
- **Issue:** Missing accent marks: `ubicación`, `física`, `organización`, `direcciones`, `código`. All required diacritics are absent.
- **Proposed:** `Una ubicación física o postal estructurada utilizada para contactar a una persona, hogar u organización. Las direcciones combinan componentes espaciales y administrativos como calle, localidad, distrito y código postal.`
- **Rationale:** Standard Spanish orthography requires these accent marks. Their absence will render the text incorrect on the public site.

### Issue 2
- **Current (es):** `localidad` for `settlement`
- **Source (en):** `settlement`
- **Issue:** Minor terminology note. "Settlement" in this geographic/administrative sense is more precisely "localidad" (fine) or "núcleo poblacional." "Localidad" is the standard administrative term in Spain and most of LatAm (used by INE Spain, INEGI Mexico, INDEC Argentina) so this is a good choice. No change needed beyond fixing the accent on "código."

---

## location.yaml
Overall: Same encoding problem as address.yaml. Missing accent marks throughout.

### Issue 1
- **Current (es):** `Una area geografica o administrativa con nombre, como una region, distrito, municipio o aldea. La ubicacion indica donde se situa un hogar o evento dentro de una jerarquia administrativa, distinta de una direccion postal.`
- **Source (en):** `A named geographic or administrative area, such as a region, district, commune, or village. Location captures where a household or event is situated within an administrative hierarchy, distinct from a street address.`
- **Issue:** Missing accent marks: `área`, `geográfica`, `región`, `ubicación`, `dónde`, `sitúa`, `jerarquía`, `dirección`. Also `distinta de una dirección postal` should end the sentence cleanly (already does).
- **Proposed:** `Una área geográfica o administrativa con nombre, como una región, distrito, municipio o aldea. La ubicación indica dónde se sitúa un hogar o evento dentro de una jerarquía administrativa, distinta de una dirección postal.`
- **Rationale:** Standard Spanish orthography. Additionally: "commune" in English is translated as "municipio" which is correct and neutral across regions. "Aldea" for "village" is also appropriate.

### Issue 2
- **Current (es):** `Una área`
- **Issue:** "Una área" should be "Un área" — "área" is a feminine noun that takes the masculine article in singular to avoid hiatus (same rule as "el agua"). This is a grammar error.
- **Proposed:** `Un área geográfica o administrativa con nombre`
- **Rationale:** Standard Spanish grammar rule: feminine nouns starting with stressed "a" or "ha" take "el/un" in singular. "Área" follows this rule. This is a clear grammatical error, not a style preference.

---

## geographic-area.yaml
Overall: Same encoding problem. Missing accent marks throughout.

### Issue 1
- **Current (es):** `Una region geografica definida por geometria de limites, codigos administrativos o ubicaciones con nombre. Se utiliza para especificar la extension espacial de alertas, cobertura de programas y otros conceptos vinculados a una ubicacion.`
- **Source (en):** `A defined geographic region described by boundary geometry, administrative codes, or named locations. Used to specify the spatial extent of alerts, program coverage, and other location-bounded concepts.`
- **Issue:** Missing accent marks: `región`, `geográfica`, `geometría`, `límites`, `códigos`, `extensión`, `ubicación`.
- **Proposed:** `Una región geográfica definida por geometría de límites, códigos administrativos o ubicaciones con nombre. Se utiliza para especificar la extensión espacial de alertas, cobertura de programas y otros conceptos vinculados a una ubicación.`
- **Rationale:** Standard Spanish orthography.

---

## event.yaml
Overall: Good. One minor issue.

### Issue 1
- **Current (es):** `Algo que ocurre en un momento específico o durante un período delimitado`
- **Source (en):** `Something that happens at a specific time or over a bounded period`
- **Issue:** "Algo" is grammatically correct but slightly informal for a formal definition. "Algo" (something) is fine in plain-language writing (which is the style goal here), so this is borderline. The French uses "Quelque chose" which is the equivalent, so the parallel is intentional. Acceptable as-is.

### Issue 2
- **Current (es):** `distintos de las entidades permanentes como personas, grupos o programas`
- **Source (en):** `as distinct from standing entities like persons, groups, or programs`
- **Issue:** Agreement error. "Distintos" is masculine plural but it should agree with "registros" (masculine plural, which is correct). Actually "distintos" is correctly agreeing with the implicit referent (los registros). This is fine.

No issues worth flagging beyond the accent marks already handled in other files (event.yaml itself has proper accents throughout).

---

## Cross-file consistency notes

1. **"Parte" vs. "entidad" for Party:** identifier.yaml uses "parte" as a translation of "Party." If this term appears elsewhere, it should be handled consistently. Recommend "entidad" as the standard translation of "party" in the administrative sense, or leave the English term "Party" untranslated (as done in party.yaml's own definition, which correctly leaves "Party" as the concept label).

2. **"Farm" / "Granja" vs. "Explotación agrícola":** group.yaml uses "Granja." If Farm appears as a concept label elsewhere in the schema, the translation should be consistent and use the more appropriate "Explotación agrícola."

3. **Accent marks in address.yaml, location.yaml, geographic-area.yaml:** All three files share the same problem. This suggests the text was entered or copied in an environment that stripped diacritics. These three files need a full orthographic pass before publication.
