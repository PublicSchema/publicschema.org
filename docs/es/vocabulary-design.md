# Diseño de vocabulario

Reglas para vocabularios controlados. Complementa el [Diseño de esquema](../schema-design/).

## 1. Universal por defecto, con alcance de dominio por excepción

Un vocabulario vive en la raíz a menos que los mismos códigos tengan significados diferentes entre dominios.

Ejemplos:

- `payment-status` es universal. "Paid" significa lo mismo en protección social, salud y educación.
- `targeting-approach` es específico de dominio. "Proxy means testing" es metodología de protección social sin equivalente en otros dominios.
- `severity` es ambiguo. En alertas de emergencia significa impacto del peligro; en salud significa progresión de la enfermedad. Disambigue renombrando (`event-severity`) o acotando a un dominio.

Las definiciones deben coincidir con el alcance. La definición de un vocabulario universal no debe referenciar un dominio específico. Escriba "los estados del ciclo de vida de una inscripción en un programa", no "...en un programa de protección social".

### Vocabularios de proceso y mecanismo

Los vocabularios que describen procesos (ciclos de vida de inscripción, procesamiento de pagos, gestión de quejas) y mecanismos de entrega (canales, modalidades) son universales por defecto, incluso si el primer concepto que los utiliza es específico de un dominio. La prueba: ¿los mismos códigos tendrían significados diferentes en otro dominio? Si "active" en una inscripción significa lo mismo en protección social y en educación, el vocabulario es universal.

Los valores individuales que solo aplican a un dominio usan la anotación `domain` sobre el valor (véase la sección 4), no sobre el vocabulario en sí.

## 2. Un concepto por vocabulario

Cada vocabulario responde una pregunta. No combine preocupaciones ortogonales.

- Estado y resultado son preguntas diferentes. "¿Dónde está este proceso?" frente a "¿Cuál fue el resultado?"
- Canal y modalidad son preguntas diferentes. "¿Cómo llega la prestación a la persona?" frente a "¿Qué forma tiene la prestación?"

No divida de forma prematura. Si un solo vocabulario captura limpiamente el ciclo de vida y todos los sistemas mapeados lo tratan como un solo campo, dividirlo añade complejidad sin beneficio demostrado.

## 3. Referencie normas existentes

Si existe un sistema de códigos formal, referencíelo. Tres niveles:

| Nivel | Cuándo usar | Campo YAML |
|---|---|---|
| **Sincronización** | Una norma legible por máquina define el conjunto de valores autorizado. | `standard` + `sync` |
| **Referencia** | La norma existe pero no se sincroniza (solo prosa, superposición parcial, simplificación deliberada). | `references` |
| **Ninguno** | No existe ninguna norma relevante. | Ninguno de los campos |

### Vocabularios sincronizados con normas

Cuando un vocabulario se sincroniza desde una norma internacional y los sistemas utilizan directamente los códigos de esa norma, `same_standard_systems` es suficiente en lugar de `system_mappings` a nivel de valor. Esto aplica a listas de códigos extensas (países, divisas, idiomas) en las que la norma es la capa de interoperabilidad de facto.

Un vocabulario sin `standard`, sin `references` y sin `system_mappings` no está validado. Aceptable en madurez borrador; debe resolverse antes del uso experimental.

No adopte los códigos de una norma cuando no resulten útiles para los usuarios. Los códigos ISO 20022 (RCVD, ACTC, ACSP) son para mensajería interbancaria. Use códigos legibles; mapee a la norma.

Prefiera las normas legibles por máquina sobre las que solo están disponibles en formato de texto. Las normas legibles por máquina pueden sincronizarse automáticamente; las normas de solo prosa se desactualizan.

## 4. Anotaciones de dominio en valores individuales

Cuando un vocabulario universal contiene valores que solo aplican a un dominio, anote el valor en lugar de dividir el vocabulario:

```yaml
- code: graduated
  domain: sp
  label:
    en: Graduated
  definition:
    en: The beneficiary has exited through program-defined graduation criteria.
```

Úselo con moderación. Si más de un tercio de los valores llevan anotaciones de dominio, el vocabulario debería moverse a un espacio de nombres de dominio.

## 5. Disambigüe nombres propensos a colisión

Antes de nombrar un vocabulario, pregúntese: ¿podría otro dominio definir un vocabulario con este nombre pero con valores diferentes?

- `severity` -> `event-severity`
- `certainty` -> `event-certainty`
- Nunca use `status` sin calificar; siempre califíquelo (`enrollment-status`, `payment-status`)

## 6. El código `other` y las correspondencias de sistemas

`other` es aceptable en madurez borrador. Registre qué se mapea a él en despliegues reales. Cuando el mismo valor sin mapear aparece en 2 o más sistemas, promuévalo a un código con nombre.

Las correspondencias de sistemas son el mecanismo de validación principal:

- 3 o más sistemas mapeando a `other` = brecha de vocabulario. Promueva a un código con nombre.
- 4 o más códigos de sistema mapeando a un valor canónico = el vocabulario puede ser demasiado grueso.
- Código de sistema mapeando a `null` cuando existe un código canónico más amplio = error de correspondencia.

Un vocabulario con cero correspondencias de sistemas no está validado. Añada correspondencias antes de avanzar la madurez.
