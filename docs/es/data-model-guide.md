# Guía de diseño de modelo de datos

Esta guía es para equipos que construyen un nuevo sistema (un registro social, SIG, herramienta de gestión de casos o cualquier plataforma de prestación de servicios públicos) y desean que sea interoperable desde el inicio. En lugar de adaptar la compatibilidad después, diseñe su modelo de datos usando PublicSchema como referencia.

## Contenido

- [Cuándo usar este enfoque](#cuándo-usar-este-enfoque)
- [Qué significa "compatible"](#qué-significa-compatible)
- [Paso 1: Identifique los conceptos que necesita](#paso-1-identifique-los-conceptos-que-necesita)
- [Paso 2: Revise las propiedades de cada concepto](#paso-2-revise-las-propiedades-de-cada-concepto)
- [Paso 3: Adopte los vocabularios canónicos](#paso-3-adopte-los-vocabularios-canónicos)
- [Paso 4: Añada sus propios campos](#paso-4-añada-sus-propios-campos)
- [Paso 5: Valide su diseño](#paso-5-valide-su-diseño)
- [Uso de PublicSchema en la adquisición](#uso-de-publicschema-en-la-adquisición)
- [Patrones de diseño a tener en cuenta](#patrones-de-diseño-a-tener-en-cuenta)
- [Descargas disponibles](#descargas-disponibles)
- [Pasos siguientes](#pasos-siguientes)

## Cuándo usar este enfoque

Este enfoque funciona bien cuando:

- Está construyendo un nuevo sistema y desea que intercambie datos con plataformas existentes
- Está redactando una solicitud de propuesta y necesita requisitos concretos de interoperabilidad
- Está diseñando un modelo de datos para un programa multinacional o multisectorial
- Está reemplazando un sistema existente y desea que el nuevo sea más fácil de integrar

No se trata de importar PublicSchema en su sistema como dependencia. Se trata de usarlo como referencia para que sus decisiones de diseño sean compatibles con el vocabulario compartido.

## Qué significa "compatible"

Un modelo de datos compatible con PublicSchema:

1. **Usa los mismos conceptos.** Su tabla "beneficiario" se corresponde claramente con el concepto Persona (Person) de PublicSchema, aunque internamente lo llame de otra forma.
2. **Almacena las mismas propiedades.** Sus campos cubren las propiedades de PublicSchema que necesita, con tipos compatibles. Puede tener campos adicionales; eso está bien.
3. **Usa los mismos códigos de vocabulario.** Donde PublicSchema define un conjunto de valores controlados (estado de inscripción, género, canal de entrega), su sistema usa los mismos códigos o puede traducirlos de forma trivial.
4. **Puede exportar en formato canónico.** Dado lo anterior, su sistema puede producir exportaciones o respuestas de API que se alineen con los nombres de propiedad y los códigos de vocabulario de PublicSchema.

No necesita usar los nombres de campo exactos de PublicSchema internamente, adoptar JSON-LD ni cambiar su motor de base de datos. La compatibilidad se refiere a la alineación semántica, no a la conformidad estructural.

## Paso 1: Identifique los conceptos que necesita

Explore la [página de conceptos](/concepts/) e identifique cuáles aplican a su sistema. No todos los sistemas necesitan todos los conceptos.

Un registro social típicamente necesita: Person, Household, GroupMembership, Identifier, Address, Location.

Un sistema de gestión de prestaciones podría añadir: Program, Enrollment, Entitlement, EligibilityDecision, PaymentEvent.

Un sistema de quejas añade: Grievance.

Descargue el **Excel de definición** para cada concepto que planee implementar. El libro de trabajo de definición incluye:

- Metadatos del concepto (URI, dominio, nivel de madurez, definiciones en EN/FR/ES)
- Lista completa de propiedades con tipos, cardinalidad y definiciones
- Vocabularios de referencia con todos los códigos

Esto le proporciona un documento de referencia autocontenido para cada concepto.

## Paso 2: Revise las propiedades de cada concepto

Para cada concepto, revise la lista de propiedades y decida cuáles necesita su sistema. PublicSchema es descriptivo, no normativo: todo es opcional. Adopte las propiedades que sean relevantes para su caso de uso.

Para cada propiedad que adopte, alinee en:

- **Nombre.** Su nombre de campo interno puede diferir, pero documente la correspondencia. Si puede usar el nombre de PublicSchema directamente (p. ej., `given_name`, `enrollment_status`), la correspondencia es trivial.
- **Tipo.** Coincida con el tipo esperado. Si PublicSchema dice `date`, almacene una fecha, no una cadena de texto. Si dice `integer`, almacene un entero.
- **Cardinalidad.** PublicSchema marca las propiedades como de valor único o de valores múltiples. Si una propiedad tiene valores múltiples (p. ej., una persona puede tener varios identificadores), diseñe su esquema para soportarlo (por ejemplo, una tabla separada o un campo de tipo arreglo).

El **CSV** del concepto es útil como lista de verificación durante este paso.

## Paso 3: Adopte los vocabularios canónicos

Para cualquier propiedad respaldada por un vocabulario (códigos de estado, género, tipos de documento, etc.), use los códigos canónicos directamente si puede. Esta es la decisión de diseño de mayor valor porque elimina la necesidad de traducción de códigos en cada integración futura.

Si debe usar códigos internos diferentes (p. ej., su base de datos usa claves numéricas enteras), mantenga una tabla de correspondencia que vincule sus códigos a los canónicos. Diseñe esta correspondencia en su sistema desde el inicio, no como algo posterior.

Consulte la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/) para detalles sobre cómo trabajar con los vocabularios.

## Paso 4: Añada sus propios campos

Su sistema casi con certeza necesitará campos que PublicSchema no define. Eso es perfectamente normal. PublicSchema cubre el terreno común entre sistemas, no todos los campos posibles.

Al añadir campos personalizados:

- **No colisione con los nombres de propiedad de PublicSchema.** Consulte la [página de propiedades](/properties/) para asegurarse de que su nombre de campo personalizado no esté ya definido con semántica diferente.
- **Considere si el campo podría ser útil para otros.** Si representa un concepto común que PublicSchema aún no cubre, podría ser candidato para una contribución. Consulte el [Mecanismo de extensión](/docs/extension-mechanism/) para saber cómo definir propiedades personalizadas en su propio espacio de nombres.
- **Documente sus extensiones.** Los futuros socios de integración necesitarán saber qué campos son canónicos y cuáles son personalizados.

## Paso 5: Valide su diseño

Use los siguientes artefactos para verificar su diseño frente a PublicSchema:

- **Esquema JSON:** Valide registros de muestra frente al esquema JSON del concepto. Si sus datos exportados pasan la validación, su esquema es compatible.
- **Formas SHACL:** Si trabaja con RDF, los perfiles SHACL permiten la validación de restricciones para todos los conceptos.
- **Plantilla Excel:** Ingrese datos de muestra en la Plantilla Excel para cada concepto. Si los datos de su sistema llenan la plantilla de forma limpia, la correspondencia es sólida. Si las columnas están vacías o los valores no encajan en las listas desplegables, investigue las brechas.

## Uso de PublicSchema en la adquisición

Si está redactando una solicitud de propuesta para un nuevo sistema, PublicSchema le provee lenguaje concreto para los requisitos de interoperabilidad en lugar de aspiraciones vagas.

Ejemplo de lenguaje de requisito:

> El sistema debe ser capaz de exportar registros de Persona (Person) con las siguientes propiedades según la definición de PublicSchema (publicschema.org): given_name, family_name, date_of_birth, sex, identifiers. El estado de inscripción debe usar códigos del vocabulario enrollment-status de PublicSchema. El sistema debe soportar la exportación en formato CSV con los nombres de propiedad de PublicSchema como encabezados de columna.

Esto es verificable. Durante la evaluación, puede entregar a los proveedores una Plantilla Excel y pedirles que demuestren que su sistema puede producir una exportación compatible.

También puede referenciar directamente los libros de trabajo del Excel de definición en la solicitud de propuesta como especificación autorizada para cada entidad que el sistema debe soportar.

## Patrones de diseño a tener en cuenta

### Persona-a-Grupo es de muchos a muchos

PublicSchema modela la relación entre personas y grupos (hogares, familias, etc.) mediante un concepto GroupMembership que lleva un rol (cabeza de hogar, cónyuge, hijo, dependiente). No modele esto como una simple lista de miembros en el grupo. Una persona puede pertenecer a múltiples grupos, y el rol importa.

### Los identificadores son separados de Persona

PublicSchema modela los identificadores (número de identidad nacional, número de pasaporte, número de ID de programa) como un concepto Identificador (Identifier) separado vinculado a Persona (Person), no como campos directamente sobre Persona. Identificador lleva únicamente el valor codificado y su esquema; los documentos que portan identificadores (pasaportes, tarjetas de identidad nacional, tarjetas de beneficiario) se modelan como IdentityDocument, que lleva la autoridad emisora, la jurisdicción, la fecha de emisión y la expiración.

### La acotación temporal es un elemento central

Muchos conceptos llevan start_date y end_date. Una inscripción no es solo un estado; es una relación acotada en el tiempo. Diseñe su esquema para soportar este patrón en lugar de almacenar solo el estado actual.

### Espacio de nombres de dominio

Algunos conceptos son universales (Person, Location) y otros son específicos de dominio (Enrollment está bajo protección social, `/sp/Enrollment`). Si está construyendo para un sector específico, verifique a qué dominio pertenecen sus conceptos. Esto afecta a los URIs pero no a cómo usa las propiedades.

### Los datos de observación pertenecen a un Profile, no a Person o Household

Los ítems de funcionamiento del Washington Group (WG-SS, WG-ES, CFM), las mediciones antropométricas (talla, peso, perímetro braquial, z-scores, bandas de estado) y las respuestas de encuestas socioeconómicas (tipo de vivienda, servicio WASH, activos, TIC, ingresos) son registros puntuales producidos por un instrumento definido. Se modelan como registros `Profile` (`FunctioningProfile`, `AnthropometricProfile`, `SocioEconomicProfile`), no como columnas sobre Person o Household.

Un `Profile` lleva la información de quién fue observado, cuándo, con qué instrumento, bajo qué modo de administración y por quién. Los Profiles también pueden llevar resultados derivados de aplicar la regla de puntuación canónica del instrumento: por ejemplo, el grupo de consumo FCS en `FoodSecurityProfile`, el identificador de discapacidad WG-SS en `FunctioningProfile`, o las bandas de tamizaje PB en `AnthropometricProfile`. Estos resultados canónicos residen directamente en el Profile porque son producidos por una regla única y bien definida, inseparable del instrumento mismo. Person conserva pequeños indicadores de síntesis (`functioning_status`, `nutrition_status`) para que los sistemas operativos puedan consultar focalización y reportes sin recalcular desde cada aplicación; Household conserva igualmente `food_security_level`. Estos indicadores son desnormalizaciones de conveniencia, no clasificaciones. El Profile sigue siendo la fuente de verdad.

### La puntuación no canónica es un acto distinto de la aplicación del instrumento

Las metodologías de puntuación no canónicas (fórmulas PMT, PPI, índices de pobreza multidimensional, índices compuestos como CARI, umbrales alternativos o cortes definidos por investigadores) se catalogan como registros `ScoringRule`. Aplicar una regla no canónica a uno o más Profiles o datos en línea produce un `ScoringEvent`, que lleva el puntaje bruto y la banda. Separar la puntuación no canónica del Profile permite puntuar los mismos datos con múltiples reglas sin re-recopilar, manteniendo los resultados canónicos cerca de las observaciones que los produjeron. Consulte [ADR-010](../decisions/010-profile-derived-outputs.md).

## Descargas disponibles

**Por concepto:**

| Formato | Qué es | Mejor para |
|---|---|---|
| **Excel de definición** | Libro de trabajo de múltiples hojas con metadatos, propiedades y vocabularios de referencia en EN/FR/ES | Referencia principal durante el diseño del modelo de datos |
| **Plantilla Excel** | Libro de trabajo de entrada de datos con validación de listas desplegables | Probar compatibilidad, prototipar formularios, evaluación de adquisición |
| **CSV** | Propiedades con tipos y definiciones | Lista de verificación para revisión de diseño campo a campo |
| **JSON-LD** | Concepto como datos enlazados | Acceso legible por máquina |

**Por vocabulario:**

| Formato | Qué es | Mejor para |
|---|---|---|
| **CSV** | Códigos con etiquetas y definiciones multilingües | Carga inicial de tablas de búsqueda en su base de datos |
| **JSON-LD** | Vocabulario como SKOS ConceptScheme | Acceso programático |

**Validación:**

| Formato | Qué es | Mejor para |
|---|---|---|
| **Esquema JSON** (por concepto) | Esquema JSON Draft 2020-12 | Validación de registros exportados |
| **Formas SHACL** | Restricciones de validación RDF | Validación de datos RDF |

## Pasos siguientes

- Para alinear códigos de valor en un sistema existente, consulte la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/).
- Para conectar sistemas existentes usando PublicSchema como capa de traducción, consulte la [Guía de interoperabilidad y correspondencia](/docs/interoperability-guide/).
- Para usar contextos JSON-LD y emitir credenciales verificables, consulte la [Guía de JSON-LD y credenciales verificables](/docs/jsonld-vc-guide/).
