# Normas relacionadas

PublicSchema se sitúa en un ecosistema de iniciativas adyacentes que operan en diferentes capas. Está diseñado para complementarlas, no para competir con ellas.

## Dónde se sitúa PublicSchema

![Panorama de normas: PublicSchema llena la capa de vocabulario del ciclo de vida de prestación](/images/standards-stack.svg)

| Capa | Qué existe | Qué falta |
|---|---|---|
| Confianza y transporte | EBSI, OpenID4VC, W3C VC Data Model | Ningún vocabulario de dominio dentro de las credenciales |
| Atributos de identidad | EU Core Person Vocabulary, W3C Citizenship Vocabulary | Cubre solo nombre/nacimiento/ciudadanía, no datos de prestación |
| Catálogos de servicios | CPSV-AP (EU), HSDS/Open Referral, schema.org/GovernmentService | Describe qué servicios existen, no quién recibe qué |
| Interoperabilidad de APIs | DCI, GovStack | Contratos de interfaz entre sistemas, no vocabulario semántico |
| Medición estadística | ILO/World Bank ASPIRE, ILOSTAT | Recuentos e indicadores, no modelos de datos para intercambio |
| **Vocabulario del ciclo de vida de prestación** | **Nada** | **Esta es la brecha que PublicSchema llena** |

## Iniciativas específicas

### DCI

La Digital Convergence Initiative construye normas de interoperabilidad de APIs entre sistemas de protección social (interfaces de registro social, pagos y registro civil), dirigida conjuntamente por GIZ, ILO y el Banco Mundial. PublicSchema es la capa de vocabulario semántico que las normas de API de DCI necesitan implícitamente pero no han construido. DCI define cómo fluyen los datos entre sistemas; PublicSchema define qué significan los datos. Ambos son complementarios.

### Vocabularios Core de la UE (SEMIC / Interoperable Europe)

El precedente técnico más cercano a cómo construir un vocabulario compartido. El Core Person Vocabulary, el Core Location Vocabulary y el Core Public Service Vocabulary Application Profile (CPSV-AP) son vocabularios RDF mínimos y reutilizables para la administración pública de la UE, publicados con formas de validación SHACL bajo CC-BY 4.0. PublicSchema se alinea con estos donde se superponen (persona, ubicación, dirección) en lugar de reinventar definiciones. Sin embargo, los Vocabularios Core de la UE cubren la identidad y el catálogo de servicios, no el ciclo de vida de prestación (inscripción, prestación, pago, quejas).

### GovStack

GovStack define especificaciones de bloque de construcción para servicios digitales de gobierno (identidad, pagos, mensajería). PublicSchema es el contraparte de modelo de datos: donde GovStack dice "necesita un bloque de construcción de pago", PublicSchema define cómo se ven los datos de pago en todos los sistemas y cómo traducir entre ellos. GovStack carece explícitamente de una capa semántica transversal, que es la brecha que PublicSchema aborda.

### FHIR

La norma de interoperabilidad del sector salud, que combina un modelo de datos con una especificación de API. PublicSchema toma inspiración del enfoque de FHIR (recursos, extensiones, conjuntos de valores, niveles de madurez) pero se orienta al espacio de servicios gubernamentales. El modelo de gobernanza de vocabulario de FHIR es una referencia útil.

### Schema.org

El modelo directo para cómo PublicSchema está estructurado y publicado. Schema.org tuvo éxito porque era simple, opcional y útil desde el primer día. Sus tipos de gobierno (GovernmentService, GovernmentOrganization) son extremadamente superficiales y orientados a SEO; no modelan datos de prestación.

### HSDS / Open Referral

La norma para directorios de servicios ("qué servicios existen y dónde"). PublicSchema es para datos de prestación ("quién recibe qué, cuándo, cómo"). Un servicio descrito en HSDS podría ser el mismo servicio descrito por un Programa (Program) de PublicSchema, pero los dos abordan extremos opuestos del ciclo de vida.

### W3C Verifiable Credentials

El W3C VC Data Model 2.0 provee la capa de confianza. El vocabulario de PublicSchema, publicado como contexto JSON-LD con URIs resolubles, sirve como el esquema que hace interoperables las credenciales de servicios gubernamentales entre fronteras y sistemas. Las especificaciones relacionadas incluyen SD-JWT VC para divulgación selectiva y OpenID4VCI/VP para emisión y presentación de credenciales.

### EBSI

La European Blockchain Services Infrastructure opera en la capa de confianza y transporte, no en la capa de vocabulario de dominio. Sin embargo, sus esquemas de credencial para identidad de persona (eIDAS PID), coordinación de seguridad social (Portable Document A1), seguro de salud (EHIC) y educación (Europass EDC / ELM 3.2) modelan muchas de las mismas entidades que cubre PublicSchema. PublicSchema usó los esquemas EBSI como insumo de diseño para identificar propiedades faltantes en Person, Address, Identifier, Enrollment y Entitlement.

### Registros de confianza

Una preocupación complementaria. El vocabulario define qué significan los términos, pero los verificadores también necesitan saber qué emisores son autorizados para qué afirmaciones. Esto está fuera del alcance del vocabulario en sí, pero cualquier despliegue necesitará un registro de confianza junto a él. OpenID Federation y el modelo de confianza EBSI son puntos de referencia.
