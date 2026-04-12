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

La madurez progresa en una sola dirección. Un concepto en uso experimental no regresará a borrador. Tres niveles (no cinco, como en el FMM 0-5 de FHIR) se corresponden con un modelo mental claro: experimental, adoptante temprano, estable.

La madurez aplica a los valores de vocabulario individuales, no solo a los vocabularios. Un vocabulario normativo puede contener un valor borrador. Los valores borrador no deben aparecer en credenciales de producción.

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

CC-BY-4.0 se eligió sobre CC0 (pierde el seguimiento de atribución) y CC-BY-SA (la cláusula de compartir igual desalienta la adopción por parte de gobiernos e integradores corporativos). Incrustar la URL del contexto JSON-LD satisface el requisito de atribución.
