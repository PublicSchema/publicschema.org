# Referencia del vocabulario DPV para programas públicos

Este documento es una lista de inicio seleccionada de URI del W3C Data Privacy Vocabulary (DPV) para las tres propiedades con valor URI en `ConsentRecord` y `PrivacyNotice`: `purposes` (finalidades), `personal_data_categories` (categorías de datos personales) y `processing_operations` (operaciones de tratamiento).

Es una guía, no un artefacto del esquema. Los valores listados aquí son clases DPV; los adoptantes los establecen como cadenas URI en sus expedientes. PublicSchema no valida en tiempo de ejecución que un URI dado sea una clase DPV válida.

**Los adoptantes deben reducir esta lista al alcance real de su programa.** Un programa de procesamiento de pagos no necesita finalidades de investigación o marketing. Un registro de un solo país no necesita operaciones de transferencia internacional. Comience con el subconjunto aplicable y añada solo lo que sea operativamente necesario.

Cuando la taxonomía nacional sea más rica que lo que proporciona DPV, el mecanismo de extensión DPV permite definir subclases. Por ejemplo, si su país tiene una categoría legal «verificación de identidad para asistencia social» que DPV no nombra directamente, puede definir `https://su.registro/purpose/VerificacionIdentidadAsistenciaSocial` como subclase de `dpv:IdentityVerification` y usar su URI en los expedientes.

---

## Finalidades (subclases de `dpv:Purpose`)

Use estos valores para `ConsentRecord.purposes` y `PrivacyNotice.purposes`.

| URI | Descripción |
|---|---|
| `dpv:ServiceProvision` | Tratamiento necesario para prestar un servicio al interesado (finalidad más amplia; usar una subclase más precisa cuando sea posible). |
| `dpv:ServicePersonalisation` | Adaptación de un servicio en función de las características o el historial de una persona. |
| `dpv:ServiceRegistration` | Registro de una persona para acceder a un servicio o recibirlo. |
| `dpv:ServiceUsageAnalytics` | Análisis del uso de los servicios para mejorar su prestación. |
| `dpv:IdentityVerification` | Verificación de que una persona es quien dice ser. |
| `dpv:FraudPreventionAndDetection` | Detección, prevención o investigación del fraude. |
| `dpv:LegalCompliance` | Cumplimiento de una obligación legal. |
| `dpv:MaintainCreditCheckingDatabase` | Mantenimiento de registros que informan decisiones de elegibilidad financiera. |
| `dpv:CommunicationForCustomerCare` | Contacto con personas para la gestión de casos o el apoyo. |
| `dpv:SocialSecurityBenefitAdministration` | Administración de prestaciones de seguridad social (inscripción, pago, recursos). |
| `dpv:PublicBenefitAdministration` | Administración de cualquier programa de ayuda o prestación pública. |
| `dpv:EligibilityDetermination` | Determinación de si una persona cumple los requisitos para una prestación o servicio. |
| `dpv:BenefitPaymentProcessing` | Procesamiento del pago de una prestación a un beneficiario elegible. |
| `dpv:ProgramMonitoring` | Seguimiento de si un programa llega a los beneficiarios previstos y logra sus objetivos. |
| `dpv:MandatedDataSharing` | Intercambio de datos exigido por ley con otra autoridad. |
| `dpv:ResearchAndDevelopment` | Investigación, incluida la investigación sobre políticas, la evaluación de impacto y el diseño de programas. |
| `dpv:Statistics` | Producción de estadísticas; los datos se usan para análisis agregado, no para decisiones individuales. |
| `dpv:AcademicResearch` | Investigación realizada en una institución académica o de investigación. |
| `dpv:HumanitarianAssistance` | Tratamiento en el contexto de una respuesta humanitaria o asistencia de emergencia. |
| `dpv:DisasterRecovery` | Tratamiento para apoyar la recuperación tras un desastre natural o emergencia. |
| `dpv:AuditAndAccountability` | Tratamiento para funciones de auditoría, control o rendición de cuentas. |

---

## Categorías de datos personales (subclases de `dpv-pd:PersonalData`)

Use estos valores para `ConsentRecord.personal_data_categories` y `PrivacyNotice.data_categories`.

### Identificadores

| URI | Descripción |
|---|---|
| `dpv-pd:Name` | Nombre que identifica a una persona física (nombre, apellido o combinado). |
| `dpv-pd:Identifier` | Cualquier identificador asignado a una persona (número de DNI, número de caso, identificador de registro). |
| `dpv-pd:NationalIdentificationNumber` | Número de identidad nacional (p. ej., DNI, NIF, CUIL). |
| `dpv-pd:DateOfBirth` | Fecha de nacimiento de la persona. |
| `dpv-pd:Age` | Edad de la persona, ya sea exacta o como rango. |

### Datos demográficos

| URI | Descripción |
|---|---|
| `dpv-pd:Gender` | Género según lo declarado por la propia persona. |
| `dpv-pd:Sex` | Sexo biológico de la persona. |
| `dpv-pd:HouseholdComposition` | Número y características de las personas que componen un hogar. |
| `dpv-pd:MaritalStatus` | Estado civil o de pareja. |
| `dpv-pd:Nationality` | Nacionalidad o ciudadanía. |
| `dpv-pd:Ethnicity` | Origen étnico o racial. Es una categoría especial según el RGPD art. 9. |
| `dpv-pd:Religion` | Creencia religiosa. Es una categoría especial según el RGPD art. 9. |
| `dpv-pd:PoliticalOpinion` | Opiniones o afiliaciones políticas. Es una categoría especial según el RGPD art. 9. |
| `dpv-pd:Disability` | Estado o tipo de discapacidad. Es una categoría especial (datos de salud) según el RGPD art. 9. |

### Datos de contacto

| URI | Descripción |
|---|---|
| `dpv-pd:PhoneNumber` | Número de teléfono fijo o móvil. |
| `dpv-pd:EmailAddress` | Dirección de correo electrónico. |
| `dpv-pd:Address` | Dirección postal o residencial. |
| `dpv-pd:Location` | Datos de ubicación, incluidas coordenadas GPS y área geográfica. |

### Datos financieros

| URI | Descripción |
|---|---|
| `dpv-pd:Income` | Ingresos, salarios u otras ganancias. |
| `dpv-pd:FinancialAccount` | Número de cuenta bancaria, cuenta de dinero móvil (mobile money) u identificador financiero similar. |
| `dpv-pd:FinancialStatus` | Situación financiera general, incluido el nivel de pobreza o el estatus socioeconómico. |
| `dpv-pd:BankAccount` | Datos bancarios específicamente. |
| `dpv-pd:AssetData` | Propiedad de tierras, ganado, bienes inmuebles u otros activos. |

### Datos biométricos (todos son categoría especial según el RGPD art. 9)

| URI | Descripción |
|---|---|
| `dpv-pd:Biometric` | Cualquier dato biométrico (categoría más amplia; usar una subclase más precisa cuando sea posible). |
| `dpv-pd:Fingerprint` | Datos de huellas dactilares o palmares. |
| `dpv-pd:FacialImage` | Fotografía facial o plantilla de reconocimiento facial. |
| `dpv-pd:IrisScan` | Datos de iris o reconocimiento de iris. |
| `dpv-pd:VoiceSignature` | Grabación de voz utilizada para identificación. |

### Datos de salud (categoría especial según el RGPD art. 9)

| URI | Descripción |
|---|---|
| `dpv-pd:HealthData` | Cualquier dato relativo a la salud física o mental. Usar con `special_category_basis`. |
| `dpv-pd:MedicalHistory` | Historial de diagnósticos, tratamientos o enfermedades. |
| `dpv-pd:Disability` | Estado de discapacidad (véase también en la sección de Datos demográficos). |
| `dpv-pd:Nutrition` | Estado nutricional, incluidas las mediciones antropométricas. |

### Datos específicos de programas

| URI | Descripción |
|---|---|
| `dpv-pd:SocialBenefitData` | Datos relativos a la percepción o elegibilidad para una prestación de protección social. |
| `dpv-pd:SocialMediaData` | Datos procedentes de perfiles de redes sociales (menos habitual en protección social). |

---

## Operaciones de tratamiento (subclases de `dpv:Processing`)

Use estos valores para `ConsentRecord.processing_operations` y `PrivacyNotice.processing_operations`.

| URI | Descripción |
|---|---|
| `dpv:Collect` | Recopilación de datos del interesado o de un tercero. |
| `dpv:Record` | Creación de un registro persistente de los datos. |
| `dpv:Store` | Conservación de datos en un sistema de almacenamiento. |
| `dpv:Use` | Uso de datos en un proceso (sentido amplio; combinar con una finalidad específica). |
| `dpv:Retrieve` | Recuperación de datos de un sistema de almacenamiento o de un tercero. |
| `dpv:Organise` | Estructuración u ordenación de datos (archivado, clasificación, etiquetado). |
| `dpv:Analyse` | Análisis de datos para extraer conclusiones o información. |
| `dpv:Derive` | Producción de nuevos datos a partir de datos existentes (puntuación, agregación, inferencia). |
| `dpv:Profile` | Elaboración de un perfil de una persona a partir de varios puntos de datos. |
| `dpv:Share` | Comunicación de datos a un tercero dentro del ámbito del responsable. |
| `dpv:Disclose` | Puesta a disposición de datos a un tercero fuera del ámbito inmediato del responsable. |
| `dpv:Transfer` | Traslado de datos a otra jurisdicción o sistema externo. |
| `dpv:Transmit` | Envío de datos por una red (subcaso más específico de Transfer o Disclose). |
| `dpv:Disseminate` | Publicación o distribución amplia de datos. |
| `dpv:Erase` | Supresión o destrucción de datos. |
| `dpv:Anonymise` | Eliminación o transformación de identificadores de modo que los datos ya no puedan vincularse a una persona. |
| `dpv:Pseudonymise` | Sustitución de identificadores directos por un seudónimo manteniendo una clave de re-identificación. |
| `dpv:Align` | Combinación o conciliación de datos procedentes de dos o más fuentes. |
| `dpv:Copy` | Duplicación de datos de un sistema o soporte a otro. |

---

## Referencia cruzada con OpenSPP

El módulo `spp_consent` de OpenSPP incluye datos de inicio (seed data) para finalidades y categorías de datos personales en sus archivos de migración de base de datos. En el estado actual de los datos OpenSPP extraídos en `external/openspp/`, no hay valores de enumeración específicos del consentimiento disponibles. Consulte directamente la documentación de OpenSPP en https://docs.openspp.org/en/latest/ para los valores actuales al integrarse con despliegues de OpenSPP.

---

## Usar como guía, no como esquema

Estos URI son puntos de partida. No copie la lista completa en sus expedientes. Establezca solo los URI que describan fielmente el tratamiento de su programa. Sobrestimar el alcance del tratamiento en un expediente de consentimiento es un problema de cumplimiento, no un margen de seguridad.

La jerarquía DPV es mucho más amplia que esta lista. Esta lista cubre el ámbito relevante para los programas de protección social, asistencia humanitaria y registro civil. Para otros dominios, consulte el DPV completo en https://w3id.org/dpv.
