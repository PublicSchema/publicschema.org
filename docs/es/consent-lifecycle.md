# Guía del ciclo de vida del consentimiento

Esta guía trata las decisiones operativas para los programas que adoptan `ConsentRecord` y `PrivacyNotice`. Está dirigida a responsables de implementación y diseñadores de sistemas de información, no a asesores jurídicos. Nada de lo aquí expuesto constituye asesoramiento legal.

---

## 1. Elegir la base jurídica: cuándo el consentimiento no es la respuesta correcta

`ConsentRecord` almacena la base jurídica del tratamiento de datos personales. El consentimiento (`legal_basis = consent`) es solo una de las seis opciones posibles. La mayoría de los programas de protección social recurren al consentimiento por defecto y terminan con expedientes que no superan una auditoría regulatoria o una reclamación de un beneficiario.

Antes de establecer `legal_basis = consent`, responda honestamente a las tres preguntas siguientes:

1. ¿Puede el beneficiario rechazar de manera realista sin perder el acceso al servicio?
2. ¿El aviso de privacidad (privacy notice) indica explícitamente que la participación es voluntaria?
3. ¿La retirada del consentimiento implica la cancelación del servicio?

Si las tres respuestas son sí, el consentimiento es la opción honesta. Si alguna respuesta es no, el tratamiento no es genuinamente voluntario y se aplica otra base jurídica.

### Qué usar en su lugar

| Situación | Base jurídica honesta |
|---|---|
| El registro es una condición para recibir una prestación | `public_interest` (interés público, RGPD art. 6(1)(e)) |
| El tratamiento lo exige una ley, un reglamento o una resolución judicial | `legal_obligation` (obligación legal, RGPD art. 6(1)(c)) |
| El tratamiento es estrictamente necesario para proteger la vida de alguien | `vital_interest` (interés vital, RGPD art. 6(1)(d)) |
| Un contrato con el beneficiario lo requiere | `contract` (contrato, RGPD art. 6(1)(b)) |
| El responsable tiene un interés legítimo que no queda anulado por los derechos del interesado | `legitimate_interest` (interés legítimo, RGPD art. 6(1)(f)); usar con precaución |

En la práctica, la mayoría de las inscripciones en programas de protección social se basan en `public_interest` o `legal_obligation`. Un ministerio que gestiona un programa de asistencia social legal casi nunca obtiene un consentimiento genuinamente voluntario en la fase de inscripción.

Los códigos del vocabulario `legal_basis` corresponden a `dpv-gdpr:A6-1-a` hasta `dpv-gdpr:A6-1-f`. Rellene `legal_basis_reference` con la cita a la ley nacional aplicable (por ejemplo, `"Ley de Protección de Datos de Kenia 2019, art. 30(1)(b)"`).

### Categorías especiales de datos

Si algún valor de `personal_data_categories` es una subclase de `dpv:SpecialCategoryPersonalData` (datos de salud, datos biométricos, origen étnico, creencia religiosa, etc.), también debe completar `special_category_basis`. La base jurídica del art. 6 y la base especial del art. 9 son dos requisitos independientes; ambos campos son necesarios.

---

## 2. Transiciones de estado para consent-status

El vocabulario `consent-status` define nueve valores. No todas las transiciones son válidas.

```
requested (solicitado)
  |-- (acuerdo del interesado) --> given (otorgado)
  |-- (negativa del interesado) --> refused (rechazado) [terminal]
  |-- (expiración del sistema) --> invalidated (invalidado) [terminal]

given (otorgado)
  |-- (reconfirmación antes de la expiración) --> renewed (renovado)
  |-- (retirada a iniciativa del interesado) --> withdrawn (retirado) [terminal]
  |-- (revocación a iniciativa del responsable) --> revoked (revocado) [terminal]
  |-- (fin del periodo de validez) --> expired (expirado) [terminal]

renewed (renovado)
  |-- (retirada a iniciativa del interesado) --> withdrawn (retirado) [terminal]
  |-- (revocación a iniciativa del responsable) --> revoked (revocado) [terminal]
  |-- (fin del periodo de validez) --> expired (expirado) [terminal]

unknown (desconocido)
  (importación heredada donde el estado original no puede determinarse; tratar como no vigente)
```

Los estados terminales (`refused`, `withdrawn`, `revoked`, `expired`, `invalidated`) no deben revertirse a un estado activo. En su lugar, debe crearse un nuevo `ConsentRecord`.

Cuando el estado pasa a `withdrawn`, complete `withdrawal_channel` y, si es posible, `withdrawal_reason`. Esto satisface el requisito de documentación del RGPD art. 7(3): el responsable puede demostrar no solo que la retirada era posible, sino que ocurrió y por qué canal.

---

## 3. El aviso de privacidad como límite

El alcance de un `ConsentRecord` debe estar contenido dentro del alcance declarado del `PrivacyNotice` al que hace referencia (mediante `notice_ref`). El alcance comprende:

- Las `purposes` del expediente deben ser un subconjunto de las `purposes` del aviso.
- Las `personal_data_categories` del expediente deben ser un subconjunto de las `data_categories` del aviso.
- Los `recipients` y `allowed_recipient_categories` del expediente deben estar incluidos en las `recipient_categories` o `recipients_described` del aviso.

Si el expediente necesita superar el alcance del aviso, el aviso debe actualizarse primero, emitirse una nueva `notice_version` y recogerse un nuevo consentimiento del interesado. No es posible ampliar el aviso retroactivamente y afirmar que el expediente anterior cubre el nuevo alcance.

El campo `notice_version` del `ConsentRecord` es una instantánea de la versión fijada en el momento del acuerdo. Aunque el aviso se corrija posteriormente, el expediente sigue referenciando la versión que se presentó efectivamente.

---

## 4. Condiciones que requieren nuevo consentimiento

| Tipo de cambio | ¿Se requiere nuevo consentimiento? | Acción |
|---|---|---|
| Se añade una nueva finalidad al aviso | Sí | Actualizar el aviso, incrementar la versión, recoger nuevo consentimiento |
| Se añade una nueva organización destinataria | Sí | Actualizar el aviso, incrementar la versión, recoger nuevo consentimiento |
| Se recopila una nueva categoría de datos personales | Sí | Actualizar el aviso, incrementar la versión, recoger nuevo consentimiento |
| Actualización de traducción o corrección tipográfica | No | Incrementar la versión del aviso; los expedientes existentes siguen siendo válidos |
| Cambio de datos de contacto del DPO (delegado de protección de datos) | No | Incrementar la versión del aviso; los expedientes existentes siguen siendo válidos |
| Actualización de la descripción de conservación (sin cambio en la retención real) | No | Incrementar la versión del aviso; los expedientes existentes siguen siendo válidos |
| Reclasificación de la jurisdicción sin cambio de alcance jurídico real | No | Incrementar la versión del aviso; los expedientes existentes siguen siendo válidos |

El criterio es semántico, no textual: si el interesado tendría derecho a oponerse al cambio en virtud del derecho aplicable, se requiere nuevo consentimiento.

Véase la sección 11 sobre el coste operativo de las campañas de nuevo consentimiento antes de planificar un cambio que lo desencadene.

---

## 5. Transiciones al alcanzar la mayoría de edad

Para un menor cuyo consentimiento fue otorgado por un padre, madre o tutor (`delegation_type ∈ {parent, legal-guardian}`), establezca `expiry_date` en la fecha en que el interesado alcance la mayoría de edad en la `jurisdiction` aplicable.

Antes de esa fecha, contacte a la persona, ahora adulta, preséntele el aviso y recoja un nuevo expediente con `delegation_type = self`. El expediente parental expirado no es válido para continuar el tratamiento tras la mayoría de edad.

Esta es una solución provisional para la versión 1. ADR-017 introducirá un campo formal `capacity_basis` para las transiciones relacionadas con la mayoría de edad y la capacidad legal, que reemplazará este procedimiento.

Conserve un registro del intento de contacto. Si la persona no puede ser localizada, el tratamiento debe cesar o apoyarse en una base jurídica que no requiera un acuerdo individual renovado (`legal_obligation`, `public_interest`).

---

## 6. Consentimiento frente a elegibilidad

Son cuestiones distintas y expedientes distintos.

Un `ConsentRecord` documenta la base jurídica del tratamiento de datos personales. Un `EligibilityDecision` documenta si una persona cumple los requisitos para un programa. Son artefactos independientes:

- Una persona puede ser elegible pero aún no haber dado su consentimiento. La inscripción no debe realizarse hasta que exista un expediente válido.
- Una persona que ha dado su consentimiento puede ser evaluada y declarada no elegible. El `ConsentRecord` sigue siendo válido; el tratamiento para el que se otorgó el consentimiento se realizó legalmente aunque el resultado fuera un rechazo.
- Una persona puede retirar su consentimiento después de haberse inscrito. La retirada no revierte la inscripción; rige los tratamientos futuros. La supresión es un proceso distinto (véase el ADR-010 sobre `DataSubjectRightsRequest`).

No confunda estos conceptos. Los sistemas que vinculan directamente el estado del consentimiento al estado de inscripción crean expedientes que ninguno de los dos conceptos puede representar correctamente.

---

## 7. Rendimiento e indexación

Para cualquier sistema que gestione más de unos pocos miles de expedientes, dos prácticas reducen significativamente el coste de las consultas:

**Indexar en `(status, expiry_date)`.** Los barridos de expiración (encontrar todos los expedientes cuya `expiry_date` ha pasado y que aún muestran `given`) se encuentran entre los trabajos por lotes más frecuentes. Un índice compuesto en estos dos campos convierte el barrido en un recorrido por rango en lugar de un análisis completo de la tabla.

**Mantener cachés de resumen para las agregaciones habituales.** Consultas como «¿cuántos expedientes de consentimiento activos tiene este programa?» o «¿cuál es la tasa de cobertura de consentimiento por comunidad?» se realizan con frecuencia en el seguimiento y la generación de informes. Calcularlas bajo demanda sobre el conjunto completo de expedientes es costoso. Una tabla de resumen actualizada por un proceso por lotes (cada hora o diariamente según el volumen) sirve para los informes sin tocar el almacén operativo.

El esquema no dicta la arquitectura de almacenamiento, pero estos dos puntos aparecen sistemáticamente en los despliegues de campo.

---

## 8. Consentimiento verbal sin testigo

Cuando `collection_medium = verbal` o `consent_expression` es `opt-in-witnessed` u `opt-in-biometric`, al menos una entrada en `witnessed_by` debería estar completada.

Es una regla que los adoptantes deben aplicar por sí mismos. El esquema no la valida. La razón por la que no se aplica a nivel de esquema es que una validación de este tipo bloquearía expedientes válidos de sistemas que no siempre pueden identificar un testigo en el momento de la digitalización (por ejemplo, retrasos en la digitalización de papel). Sin embargo, un campo `witnessed_by` ausente en un expediente verbal o biométrico debilita considerablemente el valor probatorio legal del expediente.

Orientación práctica:

- Forme a los enumeradores para que registren el nombre y la función del testigo en el momento de la recogida, no durante la digitalización.
- Incluya una entrada en `witnessed_by` aunque el testigo sea el propio enumerador (es una prueba más débil, pero mejor que ninguna).
- Para el consentimiento verbal por teléfono, registre la referencia de la llamada en `evidence_ref` y el agente del centro de llamadas en `witnessed_by`.

---

## 9. Consentimiento biométrico: dos ejes ortogonales

Los datos biométricos aparecen en dos lugares de un `ConsentRecord`. Son cosas diferentes que no deben confundirse.

**Eje 1: cómo se expresó el consentimiento.** `consent_expression = opt-in-biometric` significa que el interesado utilizó un elemento biométrico (normalmente una huella dactilar o un escáner de iris) como acto de firma. Se trata del método de captación. El expediente puede o no implicar el tratamiento de datos biométricos como datos personales.

**Eje 2: qué datos se tratan.** Si `personal_data_categories` incluye un URI que es una subclase de `dpv:BiometricData` (por ejemplo, `dpv-pd:Fingerprint`, `dpv-pd:IrisScan` o `dpv-pd:FacialImage`), entonces los datos biométricos están dentro del alcance del tratamiento. Se trata de las categorías de datos. El consentimiento puede haberse expresado biométricamente o no.

Un expediente puede tener uno, el otro, ambos o ninguno:

| consent_expression | personal_data_categories incluye biométrico | Situación |
|---|---|---|
| `opt-in-biometric` | No | Huella dactilar usada como firma; no se recogen datos biométricos |
| No biométrico | Sí | Imagen facial recogida; consentimiento firmado en papel |
| `opt-in-biometric` | Sí | Huella como firma Y datos de huella recogidos |
| No biométrico | No | Ninguna implicación biométrica |

Cuando se tratan datos biométricos como categoría especial, asegúrese de que `special_category_basis` también esté completado (véase sección 1).

---

## 10. Inmutabilidad de los campos de condiciones

Las siguientes propiedades son inmutables una vez que el `status` alcanza `given`. Están anotadas con `ps:immutableAfterStatus "given"` en la salida RDF del esquema:

`data_subject`, `controllers`, `recipients`, `recipient_role`, `allowed_recipient_categories`, `purposes`, `personal_data_categories`, `processing_operations`, `legal_basis`, `special_category_basis`, `notice_ref`, `notice_version`, `effective_date`, `jurisdiction`, `collection_medium`, `consent_expression`

No es una preferencia de interfaz ni una decisión de diseño arbitraria. Es un requisito legal. El RGPD art. 7(1) exige que los responsables puedan demostrar que se otorgó el consentimiento. Si las condiciones del consentimiento pueden modificarse a posteriori, el expediente no puede servir como prueba. El mismo principio se aplica en virtud de la Ley de Protección de Datos de Kenia art. 29(2), la LGPD brasileña art. 8(3) y disposiciones equivalentes en otras jurisdicciones.

El esquema emite `ps:immutableAfterStatus "given"` como anotación legible por máquina en cada una de estas propiedades, así como un `rdfs:comment` en lenguaje natural en la salida Turtle. Actualmente no emite una restricción SHACL, porque una forma SHACL basada únicamente en un comentario representaría mal la aplicación efectiva. Los adoptantes deben aplicar esta regla en la capa de aplicación. Un ADR futuro la promoverá a una restricción SHACL SPARQL.

Campos que permanecen modificables tras `given`:

- `status` (debe cambiar para registrar la retirada, la expiración, etc.)
- `withdrawal_channel`, `withdrawal_reason`, `refusal_reason` (se completan a medida que avanza el ciclo de vida)
- `evidence_ref` (solo acumulativo: se pueden añadir nuevos adjuntos, no eliminar los existentes)
- `verified_by`, `verified_date` (la verificación de la entrada de datos puede ocurrir después de la digitalización)
- `collection_session_ref` (correlación operativa, no una condición del acuerdo)

---

## 11. Coste operativo de las campañas de nuevo consentimiento

Cuando un cambio sustancial desencadena la necesidad de nuevo consentimiento (véase sección 4), tenga en cuenta que una campaña de recogida de nuevo consentimiento en un programa de campo es una operación de varios meses, no una transacción en base de datos.

Lo que esto suele implicar:

- Actualización del aviso y de todas sus versiones localizadas
- Impresión o distribución de los materiales del aviso actualizado
- Formación de los trabajadores comunitarios y enumeradores sobre el cambio y su motivo
- Revisita de las comunidades, a veces en varias ocasiones para llegar a los beneficiarios ausentes o móviles
- Recogida de nuevos consentimientos (en papel o electrónicos)
- Digitalización de formularios en papel y cotejo con los expedientes existentes
- Gestión de un periodo de reconciliación en que algunos expedientes están actualizados y otros aún no

Los programas han experimentado ciclos de nuevo consentimiento de 6 a 12 meses en despliegues a gran escala. Planifique esto antes de realizar un cambio que lo desencadene. Si el cambio puede formularse como editorial (una mejora de traducción, una actualización de contacto) en lugar de sustancial, verifique que realmente lo es antes de tomar el camino más fácil.

El coste operativo es una de las razones por las que el árbol de decisión de la sección 1 es importante: un programa que originalmente alegó el consentimiento pero se habría servido mejor de `public_interest` puede encontrarse ante una campaña de nuevo consentimiento para corregir la base jurídica en cada expediente existente, mientras que actualizar la base jurídica en un aviso que referencia `public_interest` no requiere ningún nuevo consentimiento.

---

## 12. Implementación de referencia

El módulo `spp_consent` de OpenSPP es una implementación de calidad productiva del modelo de expediente de consentimiento, alineada con W3C DPV v2 e ISO/IEC TS 27560:2023. Incluye exportación JSON-LD y la gestión del ciclo de vida del estado mediante una máquina de estados.

Documentación: https://docs.openspp.org/en/latest/

El módulo `spp_consent` no cubre todos los campos del `ConsentRecord` de PublicSchema (por ejemplo, los campos de flujo en papel y la presentación multilingüe de avisos son extensiones de PublicSchema), pero constituye la referencia más cercana para la lógica de aplicación en tiempo de ejecución y los patrones de serialización.
