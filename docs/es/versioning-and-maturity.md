# Versionado y madurez

## Por qué importa la estabilidad

Los URIs estables son esenciales para la compatibilidad de las credenciales verificables. Una credencial emitida hoy debe seguir siendo verificable años después. Si un URI cambia o desaparece, cada credencial que lo referencie se vuelve irresoluble.

## Dos ejes de versionado

"¿Es seguro usar este elemento?" y "¿contra qué instantánea estoy construyendo?" son preguntas distintas. PublicSchema las responde de forma independiente.

![Una versión es una instantánea heterogénea que contiene entidades en diferentes niveles de madurez](/images/versioning-axes.svg)

### Madurez por entidad

Cada concepto, propiedad y valor de vocabulario lleva un nivel de madurez:

| Nivel | Significado | Qué puede cambiar |
|---|---|---|
| **Borrador** | Propuesto, abierto a comentarios. | Puede renombrarse, reestructurarse o eliminarse. |
| **Uso experimental** | Suficientemente estable para adoptantes tempranos. | Los cambios incompatibles requieren aviso previo. |
| **Normativo** | Bloqueado. Apto para producción. | Los cambios requieren un nuevo URI. |

La madurez progresa en una sola dirección. Un concepto en uso experimental no regresará a borrador. Tres niveles (no cinco, como en el FMM 0-5 de FHIR) corresponden a un modelo mental claro: experimental, primeros adoptantes, estable.

La madurez aplica a los valores de vocabulario individuales, no solo a los vocabularios. Un vocabulario normativo puede contener un valor borrador. Los valores borrador no deben aparecer en credenciales de producción.

**Madurez a nivel de vocabulario frente a madurez a nivel de valor.** Son dos cosas distintas. La madurez a nivel de vocabulario (el campo `maturity` en el archivo YAML del vocabulario) rige el contrato para el vocabulario en su conjunto: ¿pueden los códigos ser renombrados, eliminados o cambiar su significado? La madurez a nivel de valor rige cada código individual dentro de ese vocabulario. Un vocabulario marcado como `candidate` (uso experimental) puede seguir creciendo de forma acumulativa: se pueden añadir nuevos valores (añadir nunca es un cambio incompatible) aunque los valores existentes estén bloqueados en su significado actual. Los cambios incompatibles en los valores existentes, como renombrar un código, eliminarlo o cambiar lo que significa, aplican la disciplina de cambios incompatibles de todo el vocabulario, independientemente del marcador de madurez propio del valor. Concretamente: `consent-status` está actualmente en `draft` (borrador) a nivel de vocabulario porque se espera que el conjunto de valores crezca con el tiempo (valores como `suspended`, `pending-verification` o `pending-witness` podrían añadirse a medida que los programas de campo informen sus necesidades). Los valores individuales que lo componen, como `given` y `withdrawn`, tienen significados fijados por el alineamiento DPV y no cambiarán semánticamente aunque el vocabulario crezca.

**La madurez es por elemento, no por cadena de dependencia.** La madurez de una propiedad o de un vocabulario depende de la estabilidad del contrato de ese elemento, no de la madurez de los conceptos que lo referencian. Un campo de fecha como `enrollment_date` puede ser normativo aun cuando el concepto `Enrollment` que lo usa siga siendo candidate: el contrato de la propiedad es "una fecha en formato ISO 8601 que marca cuándo comenzó una inscripción", lo cual es estable independientemente de cuántas propiedades más pueda adquirir `Enrollment`. De igual modo, un vocabulario controlado como `sp/grievance-type` puede ser normativo mientras el concepto `Grievance` sea candidate, porque el contrato del vocabulario es el conjunto de códigos y sus significados, no la forma más amplia del concepto que lo usa. Lo que una propiedad/un vocabulario normativo fija es su propia forma y semántica; lo que permanece candidate a nivel de concepto es el conjunto global de propiedades y relaciones del concepto. Romper la forma del concepto no rompe la propiedad normativa: añadir, quitar o renombrar propiedades en `Grievance` no invalida el URI, la definición ni el conjunto de valores de `grievance_type`. Si la propia definición de la propiedad debe cambiar, eso sigue activando las reglas de madurez de la propiedad (ADR + nuevo URI si es normativa).

### Versionado de versiones

Semver en `_meta.yaml`:

- **Parche** (0.1.1): corregir definiciones, añadir traducciones, corregir correspondencias de sistemas.
- **Menor** (0.2.0): añadir conceptos, propiedades o vocabularios. Promover niveles de madurez.
- **Mayor** (1.0.0): cambios incompatibles en entidades de uso experimental o normativas.

Una versión es una instantánea heterogénea: la versión 0.3.0 puede contener entidades normativas, de uso experimental y borrador. El número de versión no dice nada sobre la estabilidad de las entidades individuales; el campo de madurez sí lo hace.

## Cómo evolucionan las cosas

**Añadir valores es seguro.** Los consumidores existentes que no reconozcan un nuevo código lo ignorarán.

**Renombrar o eliminar valores es un cambio incompatible.** En borrador: aceptable con aviso. En uso experimental: requiere un período de obsolescencia. En normativo: requiere una nueva versión del vocabulario.

**Cuando se añade un nuevo dominio:**

1. Revise los vocabularios universales para detectar valores que tendrían un significado diferente en el nuevo dominio.
2. Cree vocabularios con alcance de dominio solo cuando sea necesario, no de forma preventiva.

## Versionado del contexto

El contexto JSON-LD está versionado: `ctx/draft.jsonld` durante la pre-versión, luego `ctx/v0.1.jsonld`, `ctx/v1.jsonld`, etc. Las versiones anteriores permanecen resolubles indefinidamente. Dentro de una versión, solo se hacen cambios aditivos. Eliminar o renombrar un término requiere una nueva versión del contexto.

## Persistencia de URI

Cada elemento obtiene un URI estable:

- Conceptos: `https://publicschema.org/Person`, `https://publicschema.org/sp/Enrollment`
- Propiedades: `https://publicschema.org/given_name`
- Vocabularios: `https://publicschema.org/vocab/gender-type`

Una vez publicado en uso experimental o superior, un URI no será eliminado. Los términos obsoletos continúan resolviendo con metadatos que indican el reemplazo.

## Licencia

El modelo de referencia en `schema/` está licenciado bajo **CC-BY-4.0**. Las herramientas de construcción y las pruebas bajo **Apache-2.0**.

CC-BY-4.0 se eligió sobre CC0 (pierde el seguimiento de atribución) y CC-BY-SA (la cláusula CompartirIgual desalienta la adopción por parte de gobiernos e integradores corporativos). Incrustar la URL del contexto JSON-LD satisface el requisito de atribución.
