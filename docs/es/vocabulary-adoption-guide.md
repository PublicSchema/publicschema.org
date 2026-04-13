# Guía de adopción de vocabulario

Esta es la forma más ligera de usar PublicSchema. Usted alinea los códigos y valores de campo de su sistema con el vocabulario canónico de PublicSchema, sin cambiar su modelo de datos, adoptar JSON-LD ni emitir credenciales. La ventaja es clara: sus datos se vuelven comparables con cualquier otro sistema que haga lo mismo.

## Contenido

- [Cuándo usar este enfoque](#cuándo-usar-este-enfoque)
- [Paso 1: Identifique los vocabularios que necesita](#paso-1-identifique-los-vocabularios-que-necesita)
- [Paso 2: Descargue el vocabulario](#paso-2-descargue-el-vocabulario)
- [Paso 3: Construya una tabla de correspondencias](#paso-3-construya-una-tabla-de-correspondencias)
- [Paso 4: Aplique la correspondencia](#paso-4-aplique-la-correspondencia)
- [Qué obtiene](#qué-obtiene)
- [Consejos](#consejos)
- [Descargas disponibles](#descargas-disponibles)
- [Pasos siguientes](#pasos-siguientes)

## Cuándo usar este enfoque

Este enfoque funciona bien cuando:

- Necesita reportes comparables entre programas, países o donantes
- Desea estandarizar los códigos de respuesta de la API entre agencias
- Está armonizando exportaciones de datos de múltiples sistemas
- Quiere obtener un resultado concreto rápidamente antes de comprometerse con una integración más profunda

No necesita cambiar su esquema de base de datos, sus nombres de campo internos ni el código de su aplicación. Solo necesita una capa de traducción entre sus códigos y los códigos canónicos.

## Paso 1: Identifique los vocabularios que necesita

Explore la [página de vocabularios](/vocab/) para ver todos los conjuntos de valores controlados disponibles. Puntos de partida comunes:

| Si su sistema almacena... | Consulte el vocabulario... |
|---|---|
| Estado de inscripción (activo, suspendido, etc.) | [enrollment-status](/vocab/enrollment-status/) |
| Estado de pago (completado, fallido, etc.) | [payment-status](/vocab/payment-status/) |
| Género | [gender-type](/vocab/gender-type/) |
| Canal de entrega (banco, móvil, efectivo) | [delivery-channel](/vocab/delivery-channel/) |
| Tipo de número de identificador (número de identidad nacional, número de pasaporte, P-code, etc.) | [identifier-type](/vocab/identifier-type/) |
| Tipo de documento de identidad (pasaporte, tarjeta de identidad nacional, tarjeta de beneficiario, etc.) | [document-type](/vocab/document-type/) |
| País | [country](/vocab/country/) |
| Divisa | [currency](/vocab/currency/) |

Cada página de vocabulario muestra los códigos canónicos, sus definiciones en inglés, francés y español, y la norma internacional a la que hace referencia (ISO, FHIR, etc.).

## Paso 2: Descargue el vocabulario

Cada página de vocabulario tiene un botón de descarga en formato **CSV**. El CSV incluye:

| Columna | Qué contiene |
|---|---|
| `code` | El código canónico de PublicSchema |
| `label_en` | Etiqueta en inglés |
| `label_fr` | Etiqueta en francés |
| `label_es` | Etiqueta en español |
| `standard_code` | Código de la norma internacional de referencia (si existe) |
| `uri` | URI estable para el valor |
| `definition_en` | Definición en inglés |

También puede descargar el vocabulario en **JSON-LD** para acceso legible por máquina.

## Paso 3: Construya una tabla de correspondencias

Compare los códigos de su sistema con los códigos canónicos y construya una tabla de correspondencias. Por ejemplo, si su sistema usa códigos numéricos para el género:

| Código de su sistema | Su etiqueta | Código de PublicSchema |
|---|---|---|
| `1` | Male | `male` |
| `2` | Female | `female` |
| `3` | Other | `other` |
| `9` | Unknown | `not_stated` |

Algunos aspectos a tener en cuenta:

- **Correspondencias de uno a varios.** Su sistema podría tener un código donde PublicSchema tiene varios. Por ejemplo, su sistema podría usar "inactive" tanto para inscripciones "suspended" como "completed". Documente estas situaciones y decida cómo manejarlas.
- **Valores sin correspondencia.** Su sistema podría tener valores que no tienen equivalente canónico, o viceversa. Documente las brechas; son información útil aunque no pueda resolverlas de inmediato.
- **Diferencias semánticas.** Dos códigos podrían parecer iguales pero significar cosas distintas. Lea las definiciones, no solo las etiquetas. Por ejemplo, "pending" en su sistema podría significar "pendiente de aprobación", mientras que el canónico "pending" significa "pendiente de pago".

## Paso 4: Aplique la correspondencia

La forma de aplicar la correspondencia depende de lo que esté intentando hacer:

**Para reportes:** Añada una columna a su exportación que traduzca los códigos internos a los códigos canónicos. Su plantilla de reporte referencia la columna canónica.

**Para respuestas de API:** Añada una capa de traducción que convierta los códigos internos a los códigos canónicos en la respuesta. Su base de datos interna no cambia.

**Para intercambio de datos:** Al exportar datos hacia otro sistema, pase los valores por su tabla de correspondencias. Al importar, ejecute la correspondencia inversa.

**Para paneles de control:** Mapee los códigos en la capa de visualización. Sus consultas devuelven códigos internos; el panel los traduce para la visualización.

En todos los casos, su sistema interno continúa usando sus propios códigos. La correspondencia se aplica únicamente en el punto de intercambio.

## Qué obtiene

Una vez que sus códigos estén alineados:

- **Cifras comparables entre sistemas.** "¿Cuántas inscripciones activas?" significa lo mismo en cualquier sistema.
- **Intercambio de datos más simple.** Dos sistemas que ambos mapean a códigos de PublicSchema pueden intercambiar datos sin traducción bilateral de códigos.
- **Brechas explícitas.** Donde los códigos de su sistema no coinciden con el conjunto canónico, la brecha es visible y documentada en lugar de estar oculta en traducciones ad hoc.
- **Una base para una integración más profunda.** Si más adelante desea alinear nombres de campo, adoptar esquemas JSON o emitir credenciales, la correspondencia de vocabulario ya está hecha.

## Consejos

- Empiece con uno o dos vocabularios, no con todos. El estado de inscripción y el estado de pago son puntos de partida comunes.
- Si su sistema ya usa códigos de una norma internacional (p. ej., ISO 3166 para países), verifique si PublicSchema referencia la misma norma. Si es así, su correspondencia puede ser trivial.
- Los vocabularios de PublicSchema que referencian normas internacionales incluyen el `standard_code` en el CSV. Puede mapear a través del código de norma si eso es más fácil que mapear a través de etiquetas.
- Algunos vocabularios incluyen correspondencias específicas de sistemas en sus archivos YAML de origen. Consulte la [página de vocabularios](/vocab/) para ver si su sistema ya está mapeado.

## Descargas disponibles

Cada página de vocabulario ofrece:

| Formato | Qué es | Mejor para |
|---|---|---|
| **CSV** | Archivo plano con códigos, etiquetas y definiciones | Hojas de cálculo, flujos de datos, referencia rápida |
| **JSON-LD** | Datos enlazados legibles por máquina | Acceso programático, entornos de herramientas RDF |

Para el vocabulario completo (todos los conceptos, propiedades y vocabularios en un solo archivo):

| Formato | URL |
|---|---|
| Vocabulario completo (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) |
| Vocabulario completo (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) |

## Pasos siguientes

- Para alinear nombres de campo (no solo códigos), consulte la [Guía de interoperabilidad y correspondencia](/docs/interoperability-guide/).
- Para diseñar un nuevo sistema compatible, consulte la [Guía de diseño de modelo de datos](/docs/data-model-guide/).
- Para usar contextos JSON-LD y emitir credenciales verificables, consulte la [Guía de JSON-LD y credenciales verificables](/docs/jsonld-vc-guide/).
