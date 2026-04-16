# Diseño de divulgación selectiva para credenciales PublicSchema

## Descripción general

Las credenciales de PublicSchema están diseñadas para usarse con SD-JWT VC (credenciales verificables JWT de divulgación selectiva), lo que permite a las personas titulares revelar solo las afirmaciones necesarias para una interacción específica.

## Enfoque de clasificación de datos

PublicSchema no asigna una clasificación de datos fija a propiedades individuales. Si una propiedad constituye datos personales depende del registro en el que aparece, no de la propiedad en sí. Por ejemplo, `date_of_birth` en un registro de Persona constituye un dato personal; el mismo campo en una tabla estadística agregada no lo es.

En cambio, el comportamiento de divulgación se define a nivel de **credencial**. Cada tipo de credencial a continuación especifica qué afirmaciones se divulgan siempre y cuáles son divulgables selectivamente.

Para las anotaciones de sensibilidad a nivel de propiedad, consulte [Diseño de esquema: Anotaciones de sensibilidad](../schema-design/#9-sensitivity-annotations).

## Valores de vocabulario en credenciales

No todos los valores de vocabulario pertenecen a las credenciales.

**Hechos estables, no estados transitorios.** Una credencial verificable debe atestiguar hechos que permanecen significativos con el tiempo ("esta persona es elegible"), no estados de proceso que cambian en horas ("esta solicitud está bajo revisión").

**Sin valores borrador en credenciales de producción.** El significado de un valor en borrador puede cambiar. Los emisores solo deben usar valores en madurez de uso experimental o normativa.

**El tipo de identificador solo no es suficiente.** `identifier_type: national_id_number` no tiene significado sin la jurisdicción emisora y el esquema de identificación. Los vocabularios usados en credenciales deben documentar qué contexto adicional se necesita.

## Estructura de credencial para SD-JWT VC

![Matriz de divulgación: qué afirmaciones se divulgan siempre frente a las divulgables selectivamente por tipo de credencial](/images/credential-disclosure.svg)

### IdentityCredential

Siempre divulgado:
- `type` (Person)

Divulgable selectivamente:
- `given_name`, `family_name`, `name`
- `date_of_birth`
- `gender`, `sex`
- `nationality`, `marital_status`, `education_level`
- `phone_number`
- `identifiers` (cada identificador puede divulgarse de forma independiente)

**Caso de uso**: Verificación de edad sin revelar la identidad completa. Un verificador necesita confirmar que la persona titular tiene más de 18 años. La titular divulga solo `date_of_birth`, manteniendo ocultos `given_name`, `phone_number` y otros datos personales.

### EnrollmentCredential

Siempre divulgado:
- `type` (Person + Enrollment)
- `enrollment_status`
- `is_enrolled`
- `enrollment_date`, `start_date`

Divulgable selectivamente:
- `program_ref`
- Afirmaciones de identidad de persona (given_name, family_name, date_of_birth)
- Referencia `beneficiary`

**Caso de uso**: Comprobante de inscripción activa para acceso a servicios. Un verificador de clínica de salud necesita confirmar que la persona titular está inscrita en un programa. La titular divulga enrollment_status (active) e is_enrolled (true), manteniendo oculta la identidad del programa y los datos personales.

### PaymentCredential

Siempre divulgado:
- `type` (Person + PaymentEvent)
- `payment_status`
- `payment_date`

Divulgable selectivamente:
- `entitlement_ref`
- `enrollment_ref`
- `payment_amount`, `payment_currency`
- `delivery_channel`
- `identifiers` (incluidas las entradas transaction_reference)
- `failure_reason`
- Afirmaciones de identidad de persona

**Caso de uso**: Comprobante de recibo de pago. Un auditor necesita verificar que se realizaron los pagos. La titular divulga payment_amount, payment_date y la entrada transaction_reference de identifiers, pero no su identidad personal. En caso de pagos fallidos, failure_reason puede divulgarse para apoyar la resolución de disputas.

### VoucherCredential

Siempre divulgado:
- `type` (Voucher)
- `voucher_status`
- `document_number`
- `expiry_date`

Divulgable selectivamente:
- `entitlement_ref`
- `issued_to`
- `redeemable_by`
- `amount`, `currency`
- `voucher_format`
- `items` (cada artículo de entrega puede divulgarse de forma independiente)
- `issue_date`
- `redemption_date`, `redeemed_by`, `redemption_agent`

**Caso de uso**: Redención de vale en un proveedor. La persona titular presenta la credencial de vale. El proveedor necesita confirmar que el vale es válido (estado), identificarlo (número de serie) y comprobar que no ha expirado (fecha de vencimiento). La titular puede divulgar selectivamente el valor nominal o la cesta de bienes (items) mientras mantiene su identidad oculta. Los campos posteriores a la redención (redemption_date, redeemed_by) apoyan la auditoría sin necesidad de presentar nuevamente las afirmaciones de identidad.

### EntitlementCredential

Siempre divulgado:
- `type` (Entitlement)
- `entitlement_status`
- `coverage_period_start`, `coverage_period_end`

Divulgable selectivamente:
- `enrollment_ref`
- `schedule_ref`
- `benefit_modality`
- `benefit_description`
- `amount`, `currency`
- `document_expiry_date`
- Afirmaciones de identidad de persona (a través de la cadena de inscripción)

**Caso de uso**: Comprobante de derecho a prestación. Una persona beneficiaria necesita demostrar que tiene derecho a una prestación por un período específico (p. ej., para acceder a un servicio complementario). La titular divulga entitlement_status (approved) y el período de cobertura, manteniendo ocultos los detalles del programa y la identidad. Nota: los derechos por ciclo son de corta duración, por lo que la rotación de credenciales es frecuente; `document_expiry_date` controla la validez de la credencial verificable con independencia del período de cobertura.

## Estructura de carga útil SD-JWT VC

Una carga útil SD-JWT VC separa las afirmaciones siempre divulgadas de las divulgables selectivamente mediante el mecanismo `_sd`. A continuación se muestra cómo se mapea una EnrollmentCredential:

```json
{
  "iss": "did:web:registry.example.gov.sn",
  "sub": "did:web:registry.example.gov.sn:persons:4421",
  "iat": 1706745600,
  "nbf": 1706745600,
  "exp": 1738435200,
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "_sd_alg": "sha-256",
  "cnf": {
    "jwk": { "kty": "EC", "crv": "P-256", "x": "...", "y": "..." }
  },

  "credentialSubject": {
    "type": "Person",
    "_sd": [
      "...hash(given_name)...",
      "...hash(family_name)...",
      "...hash(date_of_birth)...",
      "...hash(gender)..."
    ],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "start_date": "2025-02-01",
      "_sd": [
        "...hash(program_ref)...",
        "...hash(beneficiary)..."
      ]
    }
  }
}
```

Nota: los esquemas de credencial de PublicSchema usan exclusivamente el formato SD-JWT VC. Las cargas útiles SD-JWT VC usan `vct` (tipo de credencial verificable) en lugar del `@context` y los arreglos `type` del W3C VCDM. La afirmación `cnf` vincula la credencial a la clave de la persona titular como prueba de posesión de clave. Los esquemas JSON generados en `dist/schemas/credentials/` validan cargas útiles SD-JWT VC, no envoltorios W3C VCDM.

El arreglo `_sd` contiene hashes de las afirmaciones divulgables. Los valores reales se proveen por separado como divulgaciones que la persona titular puede elegir incluir u omitir al presentar la credencial.

## Orientación sobre el manejo de datos tradicional

Los requisitos de manejo de datos dependen del contexto de la credencial o del conjunto de datos, no de las definiciones de propiedades individuales. Los implementadores deben evaluar cada despliegue y aplicar protecciones según si los datos, en ese contexto, identifican o se relacionan con una persona natural.

Orientación general:
- **Los metadatos estructurales** (parámetros de programa, estados, fechas) típicamente no requieren manejo especial más allá de la protección de datos normal.
- **Los datos vinculados a personas** (afirmaciones de identidad, registros específicos de personas) requieren protecciones estándar: control de acceso, cifrado en reposo, períodos de retención definidos.
- **Los datos sensibles** (propiedades que revelan circunstancias como estado de salud, pobreza o condición de víctima en la mayoría de los contextos) requieren justificación para recopilarlos o divulgarlos. Consulte la anotación `sensitivity` en [Diseño de esquema](../schema-design/#9-sensitivity-annotations).
- **Los datos restringidos** (puntajes de evaluación, índices de vulnerabilidad) requieren protecciones mejoradas: registro de auditoría, limitación de propósito, Evaluación de Impacto en la Protección de Datos.

### Credencial de recibo de consentimiento (Consent Receipt VC)

Un `ConsentRecord` con `consent_record_type = receipt` es un candidato natural para una credencial verificable (Verifiable Credential), especialmente para los programas que avanzan hacia una gobernanza de datos basada en carteras digitales. Este patrón está alineado con la decisión 24 del ADR-009 y está listo para futuros despliegues con carteras digitales; no es una expectativa inmediata.

La credencial de recibo de consentimiento (Consent Receipt VC) permite a un interesado llevar consigo la prueba de lo que se acordó, el aviso que se presentó y quiénes son los responsables del tratamiento, sin depender de que el registro del programa esté disponible en línea en el momento de la verificación. Este patrón es coherente con la intención de la especificación Kantara Consent Receipt v1.1 y la semántica de recibo de la norma ISO/IEC TS 27560:2023. Usa el formato SD-JWT VC definido en otras partes de este documento.

**Afirmaciones de divulgación obligatoria** (el titular no puede ocultarlas):

- `data_subject` (la identidad del interesado, como identificador; las afirmaciones de identidad completas están en el IdentityCredential)
- `controllers` (las organizaciones responsables del tratamiento)
- `purposes` (los URI de finalidades DPV que fueron acordados)
- `legal_basis` (el código de base jurídica, p. ej., `consent`, `public_interest`)
- `signed_date` (la fecha en que el interesado indicó su acuerdo)
- `status` (el estado actual del consentimiento, p. ej., `given`, `withdrawn`)

**Afirmaciones divulgables selectivamente:**

- `evidence_ref` (el titular puede no desear exponer dónde se almacenan los documentos probatorios)
- `witnessed_by` (las identidades de los testigos; el titular puede elegir no divulgarlas)
- Los valores individuales dentro de `personal_data_categories` (cada URI DPV puede divulgarse de forma independiente; el titular podría divulgar las categorías de datos de salud a un proveedor de salud sin exponer las categorías de datos financieros)
- `recipients` (las identidades de las organizaciones destinatarias específicas; es posible la divulgación por destinatario)
- `expiry_date` y `effective_date` (las fechas de validez pueden divulgarse de forma independiente)
- `notice_ref` y `notice_version` (referencia al aviso; un titular puede divulgar estas informaciones a un verificador que necesita inspeccionar el aviso completo)
- `special_category_basis` (solo relevante cuando se involucran datos de categoría especial)
- `jurisdiction`

**Nota de implementación.** En la versión 1, la mayoría de los programas emitirán credenciales de recibo de consentimiento como registros en su sistema, no como credenciales almacenadas en carteras digitales. La estructura de afirmaciones anterior está diseñada para que, cuando la infraestructura de carteras esté disponible, la misma serialización de `ConsentRecord` se asigne directamente a la carga útil de la credencial sin reestructuración. El valor `vct` para un ConsentReceiptCredential será `https://publicschema.org/schemas/credentials/ConsentReceiptCredential` una vez que ese tipo de credencial se publique formalmente.

## Orientación de implementación

1. **Los emisores** deben consultar las definiciones de tipos de credencial anteriores al construir credenciales verificables SD-JWT. Las afirmaciones listadas como "siempre divulgadas" van en claro; las afirmaciones "divulgables selectivamente" van en `_sd`. Para propiedades no cubiertas por un tipo de credencial definido, el emisor determina el comportamiento de divulgación según el contexto de la credencial.

2. **Las personas titulares** (aplicaciones de cartera) deben presentar una interfaz de selección de divulgación que distinga las afirmaciones siempre divulgadas de las divulgables selectivamente. Las afirmaciones inherentemente sensibles (puntajes de evaluación, índices de vulnerabilidad) deben requerir confirmación explícita. En caso de duda, use por defecto la divulgación selectiva para priorizar la privacidad.

3. **Los verificadores** deben solicitar solo las afirmaciones que necesitan. Una solicitud de afirmaciones inherentemente sensibles debe incluir una justificación (p. ej., referencia a autoridad de auditoría).

4. **La canalización de construcción** genera metadatos de propiedades en `vocabulary.json`. Las billeteras digitales y los verificadores deben usar las definiciones de tipos de credencial de este documento para configurar las políticas de divulgación.
