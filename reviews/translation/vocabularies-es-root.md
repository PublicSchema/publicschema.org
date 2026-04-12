# Spanish vocabulary review — root + synced defs

## Summary
- Files reviewed: 25
- Files with issues: 12
- Files clean: 13
- Em dashes found: 0

**Clean files (no changes proposed):**
delivery-channel, education-level, group-role, literacy, marital-status, payment-status, relationship-type, sex, status-in-employment, country, currency, language, region, script

---

## Per-file findings

### schema/vocabularies/delivery-channel.yaml

No changes proposed.

---

### schema/vocabularies/education-level.yaml

No changes proposed.

---

### schema/vocabularies/employment-status.yaml

#### Top-level definition

- Current: `El estado de participación en la fuerza laboral de una persona, clasificado según el marco tripartito de la 19a Conferencia Internacional de Estadísticos del Trabajo (2013) de la OIT.`
- Proposed: `La situación laboral de una persona en la fuerza de trabajo, clasificada según el marco tripartito de la 19.ª Conferencia Internacional de Estadísticos del Trabajo (CIET, 2013) de la OIT.`
- Reason: Per cross-file consistency rule, "situación laboral" is the ILO Spanish canonical term (not "estado de participación"). Also, ordinal "19a" should be written "19.ª" in Spanish (feminine ordinal, refers to "Conferencia"). The English acronym ICLS → CIET in Spanish is the established OIT usage.

#### values

- `employed`.label — current: `Empleado` — proposed: `Empleado/a` — reason: The French uses the gender-neutral form "Employé". The English covers both. However since "Empleado" is the masculine unmarked form and is widely accepted in neutral administrative Spanish for this category, this is a judgment call; the file can stay as-is. No change required.
- No other value issues.

---

### schema/vocabularies/event-certainty.yaml

**Systemic issue: stripped accents throughout all Spanish (and French) text. This is the same authoring bug seen in other files — accents were stripped at some point.**

#### Top-level definition

- Current: `"La confianza de que un evento ha ocurrido o ocurrira. Los valores son compatibles con los codigos de certeza de OASIS CAP v1.2."`
- Proposed: `"La confianza de que un evento ha ocurrido o ocurrirá. Los valores son compatibles con los códigos de certeza de OASIS CAP v1.2."`
- Reason: Missing accents — "ocurrira" → "ocurrirá", "codigos" → "códigos".

#### values

- `observed`.label — current: `Observado` — proposed: no change — reason: correct.
- `observed`.definition — current: `"El evento ha sido observado o confirmado."` — proposed: no change — reason: correct.
- `likely`.label — current: `Probable` — proposed: no change — reason: correct.
- `likely`.definition — current: `"Es probable que el evento ocurra (probabilidad superior al 50%)."` — proposed: no change — reason: correct.
- `possible`.label — current: `Posible` — proposed: no change — reason: correct.
- `possible`.definition — current: `"El evento es posible pero poco probable (probabilidad inferior al 50%)."` — proposed: no change — reason: correct.
- `unlikely`.label — current: `Improbable` — proposed: no change — reason: correct.
- `unlikely`.definition — current: `"No se espera que el evento ocurra."` — proposed: no change — reason: correct.
- `unknown`.label — current: `Desconocida` — proposed: `Desconocido` — reason: "certeza" is the feminine noun being described by this adjective in context (e.g., "La certeza es desconocida"), but the label is a standalone term classifying a vocabulary code, so the grammatically unmarked/masculine form "Desconocido" is more appropriate as a standalone label — consistent with how other unknown/not-stated labels in the schema use the unmarked form. Parallel: `event-severity.unknown.label.es` is also "Desconocida" (flagged separately). Note: if the label is meant to read as shorthand for "certeza desconocida" then "Desconocida" is defensible; propose "Desconocido" for consistency with similar codes across files.
- `unknown`.definition — current: `"La certeza aun no se ha determinado."` — proposed: `"La certeza aún no se ha determinado."` — reason: Missing accent on "aún" (adverb meaning "still/yet").

---

### schema/vocabularies/event-severity.yaml

**Systemic issue: stripped accents throughout all Spanish (and French) text.**

#### Top-level definition

- Current: `La gravedad observada o esperada del impacto de un evento. Los valores son compatibles con los codigos de gravedad de OASIS CAP v1.2.`
- Proposed: `La gravedad observada o esperada del impacto de un evento. Los valores son compatibles con los códigos de gravedad de OASIS CAP v1.2.`
- Reason: Missing accent — "codigos" → "códigos".

#### values

- `extreme`.label — current: `Extrema` — proposed: no change — reason: correct.
- `extreme`.definition — current: `Amenaza extraordinaria para la vida o la propiedad.` — proposed: no change — reason: correct.
- `severe`.label — current: `Grave` — proposed: no change — reason: correct.
- `severe`.definition — current: `Amenaza significativa para la vida o la propiedad.` — proposed: no change — reason: correct.
- `moderate`.label — current: `Moderada` — proposed: no change — reason: correct.
- `moderate`.definition — current: `Amenaza posible para la vida o la propiedad.` — proposed: no change — reason: correct.
- `minor`.label — current: `Menor` — proposed: no change — reason: correct.
- `minor`.definition — current: `Amenaza minima o nula para la vida o la propiedad.` — proposed: `Amenaza mínima o nula para la vida o la propiedad.` — reason: Missing accent — "minima" → "mínima".
- `unknown`.label — current: `Desconocida` — proposed: `Desconocido` — reason: Same reasoning as event-certainty.unknown above; standalone label should use unmarked masculine form.
- `unknown`.definition — current: `La gravedad aun no se ha determinado.` — proposed: `La gravedad aún no se ha determinado.` — reason: Missing accent on "aún".

---

### schema/vocabularies/gender-type.yaml

**Mixed state: top-level definition and `other` code have proper accents; `male`, `female`, and `not_stated` definitions have stripped accents.**

#### Top-level definition

- Current: `El género administrativo de una persona tal como se registra en un registro o sistema de identidad. Distinto del sexo biológico (ver el vocabulario sex). Ninguna norma internacional única rige el vocabulario de género. Este vocabulario proporciona un conjunto mínimo común basado en lo que los sistemas administrativos registran.`
- Proposed: no change — reason: accents are correct, content is accurate.

#### values

- `male`.definition — current: `La persona se identifica o esta registrada como hombre.` — proposed: `La persona se identifica o está registrada como hombre.` — reason: Missing accent — "esta" → "está".
- `female`.definition — current: `La persona se identifica o esta registrada como mujer.` — proposed: `La persona se identifica o está registrada como mujer.` — reason: Missing accent — "esta" → "está".
- `other`.label — current: `Otro` — proposed: no change — reason: correct.
- `other`.definition — current: `Una identidad de género que no es exclusivamente masculina o femenina, incluyendo pero no limitándose a identidades no binarias, de tercer género o de género diverso según lo reconocido por el sistema de registro.` — proposed: no change — reason: accents are correct, content is accurate.
- `not_stated`.label — current: `No declarado` — proposed: no change — reason: correct.
- `not_stated`.definition — current: `El genero no ha sido registrado o la persona se nego a divulgarlo.` — proposed: `El género no ha sido registrado o la persona se negó a divulgarlo.` — reason: Missing accents — "genero" → "género", "nego" → "negó".

---

### schema/vocabularies/group-role.yaml

No changes proposed.

---

### schema/vocabularies/group-type.yaml

#### values

- `farm`.label — current: `Granja` — proposed: `Explotación Agrícola` — reason: Per cross-file consistency rule, "farm" → "Explotación Agrícola" (not "Granja"). "Explotación agrícola" is the standard UN/FAO Spanish term for a farm as an agricultural production unit, and is consistent with how this concept is referred to across the schema.
- `farm`.definition — current: `Una unidad de producción agrícola, generalmente basada en el hogar, utilizada para focalizar programas de apoyo agrícola.` — proposed: no change — reason: content and accents are correct. ("focalizar" = correct ILO/UN Spanish for "targeting".)

---

### schema/vocabularies/hazard-type.yaml

**Systemic issue: stripped accents throughout all Spanish (and French) text.**

#### Top-level definition

- Current: `"La categoria de peligro o evento perturbador, basada en la clasificacion del Marco de Sendai con extensiones para choques sociales y economicos."`
- Proposed: `"La categoría de peligro o evento perturbador, basada en la clasificación del Marco de Sendai con extensiones para choques sociales y económicos."`
- Reason: Missing accents — "categoria" → "categoría", "clasificacion" → "clasificación", "economicos" → "económicos".

#### values

- `geophysical`.label — current: `Geofisico` — proposed: `Geofísico` — reason: Missing accent.
- `geophysical`.definition — current: `"Terremotos, deslizamientos de tierra, tsunamis o actividad volcanica."` — proposed: `"Terremotos, deslizamientos de tierra, tsunamis o actividad volcánica."` — reason: "volcanica" → "volcánica".
- `meteorological`.label — current: `Meteorologico` — proposed: `Meteorológico` — reason: Missing accent.
- `meteorological`.definition — current: `"Inundaciones, tormentas, temperaturas extremas o sequia."` — proposed: `"Inundaciones, tormentas, temperaturas extremas o sequía."` — reason: "sequia" → "sequía".
- `biological`.label — current: `Biologico` — proposed: `Biológico` — reason: Missing accent.
- `biological`.definition — current: `"Brotes de enfermedades, epidemias, infestaciones de plagas o contaminacion biologica."` — proposed: `"Brotes de enfermedades, epidemias, infestaciones de plagas o contaminación biológica."` — reason: "contaminacion" → "contaminación", "biologica" → "biológica".
- `environmental`.label — current: `Ambiental` — proposed: no change — reason: correct.
- `environmental`.definition — current: `"Contaminacion, deforestacion, desertificacion o degradacion ecologica."` — proposed: `"Contaminación, deforestación, desertificación o degradación ecológica."` — reason: All four words missing accents.
- `technological`.label — current: `Tecnologico` — proposed: `Tecnológico` — reason: Missing accent.
- `technological`.definition — current: `"Accidentes industriales, fallas de infraestructura o derrames quimicos."` — proposed: `"Accidentes industriales, fallas de infraestructura o derrames químicos."` — reason: "quimicos" → "químicos".
- `conflict`.label — current: `Conflicto` — proposed: no change — reason: correct.
- `conflict`.definition — current: `"Conflicto armado, disturbios civiles o desplazamiento forzado."` — proposed: no change — reason: correct.
- `economic`.label — current: `Economico` — proposed: `Económico` — reason: Missing accent.
- `economic`.definition — current: `"Choques economicos como alzas de precios, colapso monetario o perturbacion de mercados."` — proposed: `"Choques económicos como alzas de precios, colapso monetario o perturbación de mercados."` — reason: "economicos" → "económicos", "perturbacion" → "perturbación".
- `other`.label — current: `Otro` — proposed: no change — reason: correct.
- `other`.definition — current: `"Eventos no cubiertos por ninguna otra categoria."` — proposed: `"Eventos no cubiertos por ninguna otra categoría."` — reason: "categoria" → "categoría".

---

### schema/vocabularies/identifier-type.yaml

**Systemic issue: stripped accents throughout all Spanish (and French) text.**

#### Top-level definition

- Current: `Categorias de documentos o numeros de identificacion utilizados para identificar personas en sistemas administrativos y de prestacion de servicios.`
- Proposed: `Categorías de documentos o números de identificación utilizados para identificar personas en sistemas administrativos y de prestación de servicios.`
- Reason: Missing accents — "Categorias" → "Categorías", "numeros" → "números", "identificacion" → "identificación", "prestacion" → "prestación".

#### values

- `national_id`.label — current: `Documento de identidad nacional` — proposed: no change — reason: correct.
- `national_id`.definition — current: `Un numero o tarjeta de identidad nacional emitido por el gobierno.` — proposed: `Un número o tarjeta de identidad nacional emitido por el gobierno.` — reason: "numero" → "número".
- `birth_certificate`.label — current: `Certificado de nacimiento` — proposed: no change — reason: correct.
- `birth_certificate`.definition — current: `Un registro oficial de nacimiento emitido por un registro civil.` — proposed: no change — reason: correct.
- `passport`.label — current: `Pasaporte` — proposed: no change — reason: correct.
- `passport`.definition — current: `Un documento de viaje emitido por el gobierno que tambien sirve como prueba de identidad y nacionalidad.` — proposed: `Un documento de viaje emitido por el gobierno que también sirve como prueba de identidad y nacionalidad.` — reason: "tambien" → "también".
- `voter_id`.label — current: `Tarjeta de votante` — proposed: no change — reason: correct.
- `voter_id`.definition — current: `Un documento de identidad emitido con fines de registro electoral.` — proposed: no change — reason: correct.
- `program_id`.label — current: `ID de programa` — proposed: no change — reason: acceptable; "ID" is the standard administrative abbreviation in Spanish.
- `program_id`.definition — current: `Un identificador de beneficiario asignado por un programa especifico.` — proposed: `Un identificador de beneficiario asignado por un programa específico.` — reason: "especifico" → "específico".
- `household_id`.label — current: `ID de hogar` — proposed: no change — reason: acceptable; see program_id note.
- `household_id`.definition — current: `Un identificador asignado a un hogar en lugar de a una persona individual.` — proposed: no change — reason: correct.
- `social_security_number`.label — current: `Numero de seguridad social` — proposed: `Número de seguridad social` — reason: "Numero" → "Número".
- `social_security_number`.definition — current: `Un numero asignado por una administracion de seguridad social o seguro social, distinto del numero de identidad nacional en muchos paises.` — proposed: `Un número asignado por una administración de seguridad social o seguro social, distinto del número de identidad nacional en muchos países.` — reason: "numero" → "número" (×2), "administracion" → "administración", "paises" → "países".
- `tax_id`.label — current: `Identificacion fiscal` — proposed: `Identificación fiscal` — reason: "Identificacion" → "Identificación".
- `tax_id`.definition — current: `Un numero de identificacion fiscal asignado por una autoridad tributaria o fiscal.` — proposed: `Un número de identificación fiscal asignado por una autoridad tributaria o fiscal.` — reason: "numero" → "número", "identificacion" → "identificación".
- `drivers_license`.label — current: `Licencia de conducir` — proposed: no change — reason: correct.
- `drivers_license`.definition — current: `Un permiso emitido por el gobierno para operar vehiculos motorizados, comúnmente utilizado como identificacion.` — proposed: `Un permiso emitido por el gobierno para operar vehículos motorizados, comúnmente utilizado como identificación.` — reason: "vehiculos" → "vehículos", "identificacion" → "identificación". (Note: "comúnmente" has its accent already — this was one of the few surviving accents in the file.)
- `marriage_certificate`.label — current: `Certificado de matrimonio` — proposed: no change — reason: correct.
- `marriage_certificate`.definition — current: `Un registro oficial de matrimonio emitido por un registro civil o una autoridad religiosa.` — proposed: no change — reason: correct.
- `death_certificate`.label — current: `Certificado de defuncion` — proposed: `Certificado de defunción` — reason: "defuncion" → "defunción".
- `death_certificate`.definition — current: `Un registro oficial de defuncion emitido por un registro civil o una autoridad sanitaria.` — proposed: `Un registro oficial de defunción emitido por un registro civil o una autoridad sanitaria.` — reason: "defuncion" → "defunción".
- `other`.label — current: `Otro` — proposed: no change — reason: correct.
- `other`.definition — current: `Un tipo de identificador no cubierto por las otras categorias.` — proposed: `Un tipo de identificador no cubierto por las otras categorías.` — reason: "categorias" → "categorías".

---

### schema/vocabularies/literacy.yaml

No changes proposed.

---

### schema/vocabularies/marital-status.yaml

No changes proposed.

---

### schema/vocabularies/payment-status.yaml

No changes proposed.

---

### schema/vocabularies/relationship-type.yaml

No changes proposed.

---

### schema/vocabularies/sex.yaml

No changes proposed.

---

### schema/vocabularies/status-in-employment.yaml

No changes proposed.

---

### schema/vocabularies/unit-of-measure.yaml

**Systemic issue: stripped accents throughout Spanish (and French) text.**

#### Top-level definition

- Current: `Unidades de medida para las cantidades de bienes distribuidos o canjeables a traves de programas de beneficios.`
- Proposed: `Unidades de medida para las cantidades de bienes distribuidos o canjeables a través de programas de beneficios.`
- Reason: "traves" → "través".

#### values

- `kg`.label — current: `Kilogramo` — proposed: no change — reason: correct.
- `kg`.definition — current: `Unidad de masa igual a 1.000 gramos.` — proposed: no change — reason: correct (Spanish uses period as thousands separator).
- `g`.label — current: `Gramo` — proposed: no change — reason: correct.
- `g`.definition — current: `Unidad de masa igual a una milesima de kilogramo.` — proposed: `Unidad de masa igual a una milésima de kilogramo.` — reason: "milesima" → "milésima".
- `l`.label — current: `Litro` — proposed: no change — reason: correct.
- `l`.definition — current: `Unidad de volumen igual a 1.000 centimetros cubicos.` — proposed: `Unidad de volumen igual a 1.000 centímetros cúbicos.` — reason: "centimetros" → "centímetros", "cubicos" → "cúbicos".
- `ml`.label — current: `Mililitro` — proposed: no change — reason: correct.
- `ml`.definition — current: `Unidad de volumen igual a una milesima de litro.` — proposed: `Unidad de volumen igual a una milésima de litro.` — reason: "milesima" → "milésima".
- `unit`.label — current: `Unidad` — proposed: no change — reason: correct.
- `unit`.definition — current: `Un articulo contable discreto (por ej., un libro de texto, un paquete de semillas).` — proposed: `Un artículo contable discreto (por ej., un libro de texto, un paquete de semillas).` — reason: "articulo" → "artículo".
- `kit`.label — current: `Kit` — proposed: no change — reason: correct (accepted loanword in Spanish).
- `kit`.definition — current: `Un paquete preensamblado de multiples articulos (por ej., kit de higiene, kit educativo).` — proposed: `Un paquete preensamblado de múltiples artículos (por ej., kit de higiene, kit educativo).` — reason: "multiples" → "múltiples", "articulos" → "artículos".
- `meal`.label — current: `Comida` — proposed: no change — reason: correct.
- `meal`.definition — current: `Una porcion de comida preparada (utilizada en programas de alimentacion escolar e institucionales).` — proposed: `Una porción de comida preparada (utilizada en programas de alimentación escolar e institucionales).` — reason: "porcion" → "porción", "alimentacion" → "alimentación".
- `mt`.label — current: `Tonelada metrica` — proposed: `Tonelada métrica` — reason: "metrica" → "métrica".
- `mt`.definition — current: `Unidad de masa igual a 1.000 kilogramos. Utilizada para el seguimiento de productos a granel.` — proposed: no change — reason: correct.

---

### schema/vocabularies/voucher-format.yaml

**Systemic issue: stripped accents throughout Spanish (and French) text.**

#### Top-level definition

- Current: `La forma fisica o digital de un vale.`
- Proposed: `La forma física o digital de un vale.`
- Reason: "fisica" → "física".

#### values

- `electronic`.label — current: `Electronico` — proposed: `Electrónico` — reason: Missing accent.
- `electronic`.definition — current: `Un codigo o token digital entregado por SMS, aplicacion movil, codigo QR u otro medio electronico.` — proposed: `Un código o token digital entregado por SMS, aplicación móvil, código QR u otro medio electrónico.` — reason: "codigo" → "código" (×2), "aplicacion" → "aplicación", "movil" → "móvil", "electronico" → "electrónico".
- `paper`.label — current: `Papel` — proposed: no change — reason: correct.
- `paper`.definition — current: `Un documento impreso que el beneficiario presenta fisicamente en un vendedor o punto de distribucion.` — proposed: `Un documento impreso que el beneficiario presenta físicamente en un vendedor o punto de distribución.` — reason: "fisicamente" → "físicamente", "distribucion" → "distribución".

---

### schema/vocabularies/voucher-status.yaml

**Systemic issue: stripped accents throughout Spanish (and French) text.**

#### Top-level definition

- Current: `Los estados del ciclo de vida de un instrumento de vale, desde la creacion hasta el canje o vencimiento.`
- Proposed: `Los estados del ciclo de vida de un instrumento de vale, desde la creación hasta el canje o vencimiento.`
- Reason: "creacion" → "creación".

#### values

- `created`.label — current: `Creado` — proposed: no change — reason: correct.
- `created`.definition — current: `El vale ha sido generado pero aun no ha sido distribuido al beneficiario.` — proposed: `El vale ha sido generado pero aún no ha sido distribuido al beneficiario.` — reason: "aun" → "aún".
- `issued`.label — current: `Emitido` — proposed: no change — reason: correct.
- `issued`.definition — current: `El vale ha sido distribuido al beneficiario o su representante autorizado.` — proposed: no change — reason: correct.
- `suspended`.label — current: `Suspendido` — proposed: no change — reason: correct.
- `suspended`.definition — current: `El vale ha sido temporalmente desactivado y no puede ser canjeado hasta su reactivacion. Las razones incluyen sospecha de fraude, verificaciones o bloqueos administrativos.` — proposed: `El vale ha sido temporalmente desactivado y no puede ser canjeado hasta su reactivación. Las razones incluyen sospecha de fraude, verificaciones o bloqueos administrativos.` — reason: "reactivacion" → "reactivación".
- `partially_redeemed`.label — current: `Parcialmente canjeado` — proposed: no change — reason: correct.
- `partially_redeemed`.definition — current: `Se ha canjeado parte pero no la totalidad del valor del vale o de los productos a los que da derecho. El vale permanece activo para uso posterior hasta el canje completo o vencimiento.` — proposed: no change — reason: correct.
- `redeemed`.label — current: `Canjeado` — proposed: no change — reason: correct.
- `redeemed`.definition — current: `El vale ha sido completamente utilizado en un vendedor o agente.` — proposed: no change — reason: correct.
- `expired`.label — current: `Vencido` — proposed: no change — reason: correct.
- `expired`.definition — current: `El periodo de validez del vale ha pasado sin canje.` — proposed: `El período de validez del vale ha pasado sin canje.` — reason: "periodo" → "período".
- `cancelled`.label — current: `Cancelado` — proposed: no change — reason: correct.
- `cancelled`.definition — current: `El vale ha sido anulado por el programa antes del canje.` — proposed: no change — reason: correct.

---

### schema/vocabularies/country.yaml (Group B — top-level definition only)

#### Top-level definition

- Current: `Países y territorios según la norma ISO 3166-1, utilizando códigos alfa-2.`
- Proposed: no change — reason: accents are correct, content is accurate.

---

### schema/vocabularies/currency.yaml (Group B — top-level definition only)

#### Top-level definition

- Current: `Códigos de moneda según la norma ISO 4217.`
- Proposed: no change — reason: accents are correct, content is accurate.

---

### schema/vocabularies/language.yaml (Group B — top-level definition only)

#### Top-level definition

- Current: `Códigos de idiomas según la norma ISO 639-3, que abarca todos los idiomas humanos conocidos.`
- Proposed: no change — reason: accents are correct, content is accurate.

---

### schema/vocabularies/region.yaml (Group B — top-level definition only)

#### Top-level definition

- Current: `Regiones geográficas y agrupaciones de países según la norma M49 de las Naciones Unidas.`
- Proposed: no change — reason: accents are correct, content is accurate.

---

### schema/vocabularies/script.yaml (Group B — top-level definition only)

#### Top-level definition

- Current: `Códigos de sistemas de escritura según la norma ISO 15924.`
- Proposed: no change — reason: accents are correct, content is accurate.

---

### schema/vocabularies/occupation.yaml (Group B — top-level definition only, flag for stripped accents)

#### Top-level definition

- Current: `Categorias que describen la ocupacion de una persona, basadas en la clasificacion jerarquica completa ISCO-08 (grandes grupos, subgrupos principales, subgrupos y grupos primarios).`
- Proposed: `Categorías que describen la ocupación de una persona, basadas en la clasificación jerárquica completa ISCO-08 (grandes grupos, subgrupos principales, subgrupos y grupos primarios).`
- Reason: **Stripped accents — systemic authoring bug.** "Categorias" → "Categorías", "ocupacion" → "ocupación", "clasificacion" → "clasificación", "jerarquica" → "jerárquica". This is a full rewrite of the affected text, not individual word replacements.

---

## Open questions

1. **`employment-status` top-level definition:** The current text uses "El estado de participación en la fuerza laboral" while the cross-file consistency rule specifies "situación laboral". However, the existing text is a direct calque of the ILO English ("labour force participation status"). The ILO's own Spanish publications use both phrasings. A confirmed ILO canonical source should be checked before editing; the proposal above is a recommendation, not a certainty.

2. **`event-certainty` and `event-severity` `unknown` label:** "Desconocida" vs. "Desconocido" — the feminine form is grammatically justified when read as an adjective modifying "certeza/gravedad", and the masculine is justified as a standalone administrative code label. The files should be internally consistent (both should use the same convention). Recommend "Desconocido" for standalone code labels, but confirming against the schema's convention for unknown/not-stated labels across all files would be ideal before editing.

3. **`group-type` `farm` label:** The cross-file consistency rule says "Explotación Agrícola" (capitalized). When used as a label (not a heading), sentence case ("Explotación agrícola") is standard in Spanish administrative usage. Confirm intended capitalization convention before editing.

4. **Systemic stripped-accent bug:** At least 8 files (event-certainty, event-severity, hazard-type, identifier-type, unit-of-measure, voucher-format, voucher-status, occupation) show the same pattern of stripped accents in both French and Spanish. This is likely a single authoring event (copy-paste from a non-Unicode source or ASCII normalization). The French text in these files should be reviewed in a separate pass.
