# Diseño de esquema

## 1. Convenciones de nomenclatura

El estilo de escritura codifica el tipo de elemento:

| Tipo de elemento | Convención | Ejemplos |
|---|---|---|
| Conceptos | PascalCase | Person, Enrollment, GroupMembership |
| Propiedades | snake_case | given_name, date_of_birth |
| Códigos de valor de vocabulario | snake_case | never_married, bank_transfer |
| Identificadores de vocabulario | kebab-case | gender-type, enrollment-status |

Aplicado por validadores de expresiones regulares en esquemas JSON. Una vez que un nombre se publica en uso experimental o superior, no puede cambiarse.

## 2. URIs con alcance de dominio

Algunos conceptos comparten un nombre entre dominios pero tienen semánticas diferentes ("Enrollment" en protección social frente a educación). Los elementos específicos de dominio obtienen un segmento de dominio en su URI; los elementos universales viven en la raíz:

- `publicschema.org/sp/Enrollment` (protección social)
- `publicschema.org/Person` (universal)

La prueba: un elemento es universal si la misma definición tiene el mismo significado independientemente del dominio. Si no es así, pertenece a un espacio de nombres de dominio.

Los nombres nunca se prefijan con una abreviación de dominio. Es `Enrollment`, no `SPEnrollment`. La estructura del URI maneja la disambiguación.

| Código | Dominio | Estado |
|---|---|---|
| `sp` | Protección social | Activo |
| `edu` | Educación | Futuro |
| `health` | Salud | Futuro |
| `crvs` | Registro civil y estadísticas vitales | Futuro |

## 3. Persistencia de URI

Cada elemento obtiene un URI estable. Una vez publicado en uso experimental o superior, un URI no será eliminado. Los términos obsoletos continúan resolviendo con metadatos que indican el reemplazo. Consulte [Versionado y madurez](../versioning-and-maturity/) para el modelo completo.

## 4. Concepto, propiedad o vocabulario

Use este árbol de decisión para determinar qué tipo de elemento crear.

![Árbol de decisión: identidad propia, conjunto de valores cerrado, el valor tiene identidad](/images/decision-tree.svg)

**Paso 1: ¿Tiene identidad propia?** ¿Esta cosa existe de forma independiente, se referencia desde múltiples lugares y tiene su propio ciclo de vida? Si es así, es un **concepto**.

*Ejemplo:* GroupMembership es un concepto, no una propiedad de Person o Group. Lleva sus propios datos (rol, fechas), tiene su propio ciclo de vida y se referencia desde ambos lados.

**Paso 2: ¿Es un atributo de un concepto?** ¿Un hecho sobre un concepto específico, sin identidad independiente? Si es así, es una **propiedad**. Los valores múltiples (p. ej., números de teléfono) siguen siendo una propiedad con cardinalidad `many`.

**Paso 3: ¿Se extrae el valor de un conjunto cerrado?** Si la propiedad acepta una respuesta de una lista definida con significados estables, el conjunto de valores es un **vocabulario**.

**Paso 4: ¿Referencia o en línea?** Si el valor tiene su propia identidad y propiedades, referencie un concepto (`concept: Location`). Si es un escalar simple, use un tipo primitivo en línea.

*Ejemplo:* `latitude` es un `decimal` en línea sobre Location. No tiene identidad independiente ni subpropiedades. Es un número.

| Situación | Tipo de elemento |
|---|---|
| Ciclo de vida propio, referenciado desde múltiples conceptos | Concepto |
| Atributo de un concepto, sin identidad independiente | Propiedad |
| Valor de un conjunto cerrado de opciones | Vocabulario |
| El valor tiene su propia identidad y subpropiedades | Propiedad que referencia un concepto |
| Escalar simple | Tipo primitivo en línea |

## 5. Contexto temporal

Casi todo en la prestación de servicios públicos está acotado en el tiempo. Una instantánea de estado sin un período de validez está incompleta. Al diseñar un concepto o propiedad, pregúntese: ¿cambiará este valor con el tiempo? Si es así, modele el contexto temporal explícitamente (fechas de inicio/fin, períodos de validez).

## 6. Independencia de propiedades

Una propiedad como `start_date` se define una sola vez y se reutiliza en varios conceptos. Cuando una propiedad compartida necesita conjuntos de valores específicos de concepto (p. ej., `status` en Enrollment frente a Grievance), se especializa mediante referencias a vocabularios diferentes en lugar de ignorar las diferencias.

## 7. Anotaciones de sensibilidad

Algunas propiedades revelan circunstancias sensibles independientemente de si identifican a una persona específica. `program_ref` revela la inscripción en un programa específico (que puede orientarse a VIH, discapacidad o pobreza). `grievance_type` revela que alguien presentó una queja.

| Nivel | Cuándo usar | Qué señala |
|---|---|---|
| `standard` | Predeterminado. Sin manejo especial más allá de la protección de datos normal. | Puede omitirse (se asume si está ausente). |
| `sensitive` | Revela circunstancias (salud, pobreza, condición de víctima) en la mayoría de los contextos. | Requiere justificación para recopilar o divulgar. |
| `restricted` | No debe aparecer en credenciales en puntos de servicio rutinarios. | Requiere una Evaluación de Impacto en la Protección de Datos. |

Esta es una advertencia para practicantes, no una etiqueta de cumplimiento. Si una propiedad constituye datos personales depende del registro en el que aparece, no de la propiedad en sí. Consulte [Divulgación selectiva](../selective-disclosure/) para la clasificación a nivel de credencial.
