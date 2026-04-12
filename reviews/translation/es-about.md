# Spanish translation review: AboutContent

**Scope:** Full review of `AboutContent.es.astro` against `AboutContent.en.astro`. Target register: neutral Spanish (Spain/Latin America), formal usted, international social-protection terminology (CEPAL/ILO/World Bank).

---

## Flags

---

**Line (approx):** 19
**Current:** `Inscripción`
**Issue:** "Inscripción" is the Spanish translation used for the concept name "Enrollment", but in social protection Spanish-language usage (CEPAL, ILO, World Bank) "inscripción" tends to cover the act of signing up, while the established term for the formal beneficiary status in a program is "afiliación" or "adscripción al programa". This is a concept name visible prominently in the UI list, so accuracy matters.
**Proposed:** `Afiliación` (or, if enrollment specifically means the act/event, `Inscripción` is defensible; but if it denotes the ongoing relationship, `Afiliación` is more precise)
**Rationale:** CEPAL and World Bank Spanish documents use "afiliación" for the beneficiary relationship in social protection programs; "inscripción" maps better to a registration event.

---

**Line (approx):** 19
**Current:** `profesionales de política pública`
**Issue:** "Política pública" is correct, but the established collocation in formal technical writing for this audience is "profesionales de políticas públicas" (plural) or "expertos en políticas públicas". The singular "política pública" sounds like a specific policy, not the field.
**Proposed:** `profesionales de políticas públicas`
**Rationale:** Standard collocation in CEPAL, ILO, and World Bank Spanish documents uses the plural "políticas públicas" when referring to the policy field, not a single policy.

---

**Line (approx):** 21
**Current:** `los referenciamos`
**Issue:** "Referenciar" as a verb meaning "to reference/cite" is an anglicism gaining traction in technical writing but still not standard in formal Spanish; "hacer referencia a ellos" or "los adoptamos" is more natural and appropriate for this register.
**Proposed:** `hacemos referencia a ellos`
**Rationale:** "Referenciar" in the sense of "to reference a standard" is a calque from English. The standard Spanish construction uses "hacer referencia a" or "remitir a".

---

**Line (approx):** 22
**Current:** `la divulgación selectiva de datos personales sensibles`
**Issue:** "Divulgación selectiva" is a calque of "selective disclosure". In privacy and credential contexts, the established Spanish term used by W3C and ISO Spanish documents is "revelación selectiva" or "divulgación selectiva de información"; "divulgación" can connote undesired leaking of data. "Revelación selectiva" better captures the controlled, intentional nature of the mechanism.
**Proposed:** `la revelación selectiva de datos personales sensibles`
**Rationale:** W3C Spanish documentation uses "revelación selectiva" for the selective disclosure mechanism; "divulgación" carries a connotation of unwanted disclosure in Spanish.

---

**Line (approx):** 26
**Current:** `extienden lo que falta`
**Issue:** This is a calque of "extend what they don't [have]". The source English is "extend what they don't", meaning they build on what is not already covered. The Spanish "extienden lo que falta" loses the reflexive ownership ("their own extension"). A more natural phrasing would make clear they extend it for their own use.
**Proposed:** `amplían lo que no cubre sus necesidades`
**Rationale:** The current phrasing is a compressed calque that omits the sense of "for themselves" and uses "falta" (is missing) ambiguously. The proposed phrasing restores the meaning while using natural Spanish vocabulary.

---

**Line (approx):** 35
**Current:** `La delimitación temporal es de primer orden`
**Issue:** "De primer orden" is a calque of "first-class" (from programming). In Spanish technical writing, "primera clase" is used in programming contexts but sounds odd in a policy-oriented text. A clearer phrase would be "es un aspecto central" or "ocupa un lugar central".
**Proposed:** `La dimensión temporal es un aspecto central del modelo`
**Rationale:** "First-class" in the English source is a programming metaphor that does not translate naturally into policy-practitioner Spanish; the proposed version conveys priority without the technical anglicism.

---

**Line (approx):** 47-48
**Current:** `la capa de datos de prestación: entre los estándares de identidad, la interoperabilidad de API y la infraestructura de confianza`
**Issue:** "Capa de datos de prestación" is an awkward noun chain calque of "delivery data layer". In Spanish, this type of noun-stacking is unnatural. "Capa de datos para la prestación de servicios" is clearer. Additionally, "interoperabilidad de API" lacks an article and reads as a direct calque; "interoperabilidad de interfaces de programación" or simply "interoperabilidad de APIs" (with article) is more natural.
**Proposed:** `la capa de datos para la prestación de servicios: entre los estándares de identidad, la interoperabilidad de APIs y la infraestructura de confianza`
**Rationale:** Noun chains translated literally from English produce awkward Spanish; unpacking "delivery data layer" makes the text readable for policy practitioners.

---

**Line (approx):** 68
**Current:** `Datos del ciclo de vida de la prestación más allá de nombre, nacimiento y ciudadanía`
**Issue:** Another heavy noun chain calque. "Datos del ciclo de vida de la prestación" stacks five nouns and reads as machine-translated. A cleaner construction: "Datos sobre el ciclo de vida de la prestación, más allá del nombre, la fecha de nacimiento y la ciudadanía".
**Proposed:** `Datos sobre el ciclo de vida de la prestación, más allá del nombre, la fecha de nacimiento y la ciudadanía`
**Rationale:** Adding the preposition "sobre" and definite articles restores natural Spanish syntax and improves readability for a non-technical policy audience.

---

**Line (approx):** 100-101
**Current:** `bloques de construcción para el gobierno digital`
**Issue:** "Bloques de construcción" is a literal calque of "building blocks". The established Spanish term in GovStack's own Spanish materials and CEPAL documents is "componentes reutilizables" or "bloques funcionales". GovStack itself uses "bloques de construcción" in some Spanish materials, so this flag is lower confidence; however, "bloques funcionales" reads more naturally to a policy audience.
**Proposed:** `bloques funcionales para el gobierno digital`
**Rationale:** "Bloques de construcción" is an established calque in the digital-government space, but "bloques funcionales" is more natural in Spanish policy writing and avoids the literal construction-site connotation.

---

**Line (approx):** 102-103
**Current:** `nos inspiramos en su enfoque pero apuntamos a los servicios públicos en general`
**Issue:** "Apuntamos a" is a calque of "target". In formal Spanish, "apuntamos a" is used in goal-setting contexts ("apuntamos a reducir la pobreza") but sounds casual when used with a noun object meaning "to be aimed at". A cleaner phrasing: "está orientado a los servicios públicos en general" or "se dirige a los servicios públicos en su conjunto".
**Proposed:** `nos inspiramos en su enfoque pero nuestro alcance abarca los servicios públicos en general`
**Rationale:** "Apuntamos a [noun]" is a calque of "we target [noun]" that reads as informal and inexact in formal policy-register Spanish.

---

**Line (approx):** 133
**Current:** `Proponga aguas arriba.`
**Issue:** "Proponga aguas arriba" is a direct calque of "Propose upstream", a software development term with no equivalent meaning in Spanish for a policy audience. The intended meaning is "propose it for inclusion in the common schema". This needs to be rewritten in plain language.
**Proposed:** `Proponga su inclusión en el modelo compartido.`
**Rationale:** "Aguas arriba" (upstream) is a technical open-source term that is opaque to policy practitioners; the meaning must be made explicit.

---

**Line (approx):** 143
**Current:** `Se busca activamente la retroalimentación`
**Issue:** "Retroalimentación" is a widely used latinoamericanism for "feedback" that is acceptable, but in formal institutional and policy-oriented Spanish (particularly in Spain and international bodies), "retroalimentación" can feel informal or corporate. "Se busca activamente la opinión de expertos" or "se reciben activamente comentarios y aportes de" is more appropriate to the register.
**Proposed:** `Se reciben activamente aportes de expertos en el dominio, implementadores de sistemas y organismos de normalización.`
**Rationale:** "Retroalimentación" is a valid term but "aportes" or "contribuciones" better fits the formal, multi-stakeholder register used by international organizations in Spanish.

---

**Line (approx):** 151
**Current:** `en progreso`
**Issue:** The badge label "en progreso" is a direct calque of "in progress". In Spanish, the natural phrasing for an ongoing phase is "en curso" (used by CEPAL, UN, and EU Spanish documents).
**Proposed:** `en curso`
**Rationale:** "En curso" is the standard Spanish expression for an ongoing activity in institutional and formal contexts; "en progreso" reads as a calque of English.

---

**Line (approx):** 159
**Current:** `Piloto con al menos un despliegue en un país`
**Issue:** "Despliegue" is a calque of "deployment" from software/military usage. In the context of social protection policy, the standard term is "implementación" or "puesta en marcha" (for a country rollout). "Despliegue" would be understood but sounds technical and not natural for a policy audience.
**Proposed:** `Experiencia piloto con al menos una implementación en un país`
**Rationale:** "Implementación" is the standard term in CEPAL and World Bank Spanish for rolling out a program or system in a country; "despliegue" is a technical anglicism in this context.

---

## Overall impression

The translation is competent and covers the full source text accurately. The main weakness is a recurring pattern of noun-chain calques from English (e.g., "capa de datos de prestación", "datos del ciclo de vida de la prestación") that produce awkward, machine-translated-sounding strings; these should be unpacked using prepositions and articles as Spanish syntax requires. A smaller but significant category of issues involves open-source and software terminology ("aguas arriba", "en progreso", "despliegue") that has no established equivalent for a policy-practitioner audience and must be replaced with plain-language alternatives. Vocabulary choices are generally neutral across regions, with no strongly country-specific terms, which is appropriate for the target register.
