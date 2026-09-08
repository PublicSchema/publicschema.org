# Diseño de esquema

## 1. Convenciones de nomenclatura

El estilo de escritura indica el tipo de elemento:

| Tipo de elemento | Convención | Ejemplos |
|---|---|---|
| Conceptos | PascalCase | Person, Enrollment, GroupMembership |
| Propiedades | snake_case | given_name, date_of_birth |
| Códigos de valor de vocabulario | snake_case | never_married, bank_transfer |
| Identificadores de vocabulario | kebab-case | gender-type, enrollment-status |

Estas convenciones son aplicadas por validadores de expresiones regulares en los esquemas JSON. Una vez que un nombre se publica en uso experimental o superior, no puede cambiarse.

## 2. URIs con alcance de dominio

Algunos conceptos comparten un nombre entre dominios pero tienen semánticas diferentes ("Enrollment" en protección social frente a educación). Los elementos específicos de dominio obtienen un segmento de dominio en su URI; los elementos universales viven en la raíz:

- `publicschema.org/sp/Enrollment` (protección social)
- `publicschema.org/Person` (universal)

La prueba: un elemento es universal si la misma definición tiene el mismo significado independientemente del dominio. Si no es así, pertenece a un espacio de nombres de dominio.

Aplique la misma prueba basada en el significado a propiedades y vocabularios. Una forma primitiva portable no hace que una propiedad sea universal: un identificador fiscal y un identificador de vehículo pueden ser ambos cadenas y, sin embargo, nombrar hechos diferentes. Las propiedades compartidas como `start_date` conservan su URI raíz cuando las usa un concepto sectorial. Los términos existentes en estado candidato o normativo conservan sus identidades publicadas, incluidos los pares heredados de propiedad raíz y vocabulario de dominio; son restricciones de compatibilidad, no un precedente para asignar términos nuevos solo por su forma.

Los nombres públicos no necesitan abreviaciones de dominio: use `Enrollment`, no `SPEnrollment`. Sin embargo, los identificadores LinkML deben ser únicos dentro del compuesto. Por ejemplo, el `CrvsPerson` redactado representa `crvs/Person`, una instantánea de registro civil distinta de `Person` universal; `crvs/Parent` hereda de esa instantánea. Consulte [ADR-018](../decisions/018-crvs-person-rename.md).

| Código | Dominio | Alcance actual |
|---|---|---|
| `sp` | Protección social | Programas de prestaciones y relaciones de prestación |
| `crvs` | Registro civil y estadísticas vitales | Eventos vitales y roles de registro |
| `agri` | Agricultura | Explotaciones de producción, cultivos, establecimientos ganaderos, insumos y roles de producción |
| `land` | Administración de tierras | Unidades espaciales y administrativas, tenencia y límites |
| `environment` | Medio ambiente | Instalaciones, unidades técnicas, emisiones y autorizaciones de uso de agua |
| `transport` | Transporte | Vehículos, carreteras, restricciones de red y permisos de conducir |
| `edu` | Educación | Proveedores, programas, ofertas y centros educativos |
| `health` | Salud | Instalaciones físicas de atención sanitaria; el contenido médico se integra mediante FHIR nativo |
| `tax` | Administración tributaria | Registro tributario |
| `elections` | Administración electoral | Registro de votantes |

Estas etiquetas describen partes representadas, no estándares sectoriales completos. Un dominio es un espacio de nombres y una ayuda para el descubrimiento, no una superclase ni un límite de control de acceso. Cualquier dominio puede reutilizar un concepto compartido o referirse al concepto de otro dominio. Los nombres de archivos de módulo organizan la autoría y no determinan los espacios de nombres públicos.

`ServicePoint` permanece compartido. Sus subtipos provisionales `School` y `HealthFacility` usan `edu/School` y `health/HealthFacility`. `RegistrationOffice` permanece en la raíz porque su definición también cubre el registro de identidad y de personas refugiadas. `WaterPoint` conserva su identidad raíz existente como excepción de alcance declarada; no se ha diseñado un espacio de nombres completo para agua y saneamiento. Las identidades genéricas de animales y plantas permanecen compartidas cuando sus definiciones no requieren producción agrícola. Consulte [ubicación y migración de dominios](domain-migration.md) para disposiciones individuales.

Redacte valores explícitos de `class_uri`, `slot_uri`, `enum_uri` y `meaning` de valores permitidos, con `annotations.source_domain` coherentes. El renderizador usa el URI redactado de una propiedad para ubicar su página; añadir un nuevo consumidor no debe mover esa propiedad. Las rutas del catálogo de vocabularios siguen siendo `/vocab/<domain>/<kebab-case-id>`. `schema/publicschema.yaml` proporciona etiquetas de dominio mediante `annotations.domains_json`; el sitio muestra los dominios realmente presentes en cada colección y mantiene visibles los códigos desconocidos.

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

## 4a. Conceptos de tipo grupo

Tres conceptos de PublicSchema describen colecciones de personas pero tienen semánticas distintas. Elegir el concepto correcto es importante para la calidad de los datos y la interoperabilidad.

**Household (Hogar)** es una unidad económica corresidente. Los miembros comparten una vivienda y, por lo general, comparten alimentos y recursos. La definición operacional varía según el país y el programa (combinando criterios de corresidencia, presupuesto compartido, cocina común y parentesco), pero el criterio central siempre es la colocalización física y los medios de vida compartidos. Household es el concepto adecuado para registrar las unidades beneficiarias en programas de protección social.

**Family (Familia)** es una red de parentesco. Los miembros están unidos por lazos de sangre, matrimonio o adopción, independientemente de dónde residan. Una familia puede abarcar varios hogares y áreas geográficas. Los vínculos de parentesco entre miembros se modelan como registros Relationship entre instancias Person; Family en sí misma no lleva propiedades de parentesco dedicadas en esta etapa. Family es el concepto adecuado cuando la unidad de interés es una red relacional en lugar de un arreglo corresidente.

**FamilyRegister (Registro de familia)** es un documento administrativo, no un grupo. Es un acto de registro civil que da seguimiento a una unidad familiar a lo largo del tiempo a medida que ocurren eventos vitales (nacimientos, defunciones, matrimonios). Referencia una Family para exponer la composición actual. FamilyRegister es el concepto adecuado para modelar instrumentos administrativos al estilo del koseki, el hukou o el libro de familia.

### Cuándo usar cada concepto

| Quiere registrar... | Use |
|---|---|
| Una unidad beneficiaria que comparte vivienda y recursos | Household |
| Una red de personas unidas por sangre, matrimonio o adopción | Family |
| Un documento administrativo de registro civil que da seguimiento a una familia | FamilyRegister |

### Puente de interoperabilidad

Muchos sistemas usan el término "familia" coloquialmente para referirse a la unidad corresidente. Al intercambiar datos con esos sistemas, establezca `group_type: family` en el registro Household. Esto indica a los consumidores que el hogar se representa como una familia a efectos de interoperabilidad, sin distorsionar la semántica de PublicSchema.

## 5. Contexto temporal

Casi todo en la prestación de servicios públicos está acotado en el tiempo. Una instantánea de estado sin un período de validez está incompleta. Al diseñar un concepto o propiedad, pregúntese: ¿cambiará este valor con el tiempo? Si es así, modele el contexto temporal explícitamente (fechas de inicio/fin, períodos de validez).

### Convenciones para propiedades de fecha

Los conceptos de ciclo de vida usan fechas con nombre específico del dominio que describen el evento del dominio. Los conceptos de relación y membresía usan `start_date` / `end_date` genéricos.

| Tipo de concepto | Patrón de fecha | Ejemplos |
|---|---|---|
| Ciclo de vida (Enrollment) | Fechas con nombre específico del dominio | `enrollment_date`, `exit_date` |
| Ciclo de vida (Entitlement) | Período específico del dominio | `coverage_period_start`, `coverage_period_end` |
| Ciclo de vida (Grievance) | Fechas de evento específicas del dominio | `submission_date`, `resolution_date` |
| Evento único (PaymentEvent) | Fecha de evento único | `payment_date` |
| Relación (GroupMembership, Relationship) | Fechas genéricas | `start_date`, `end_date` |
| Validez calendaria de una aserción (RegistryEntry, Registration) | Primer y último día aplicable | `valid_from`, `valid_to` |

No mezcle ambos patrones en el mismo concepto. Un concepto de ciclo de vida no debe llevar tanto `enrollment_date` como `start_date`.

Los dos pares genéricos no son alias. `start_date` nombra la fecha en que comenzó la efectividad; `end_date` nombra la fecha en que cesó. Los `valid_from` y `valid_to` provisionales nombran el primer y último día calendario aplicables, incluido el último día. `recorded_at` registra en cambio cuándo la fuente introdujo la aserción. Las fechas ausentes siguen siendo desconocidas; un fin omitido no demuestra validez perpetua.

Use `start_date` / `end_date` para conceptos de relación y membresía. Los borradores HoldingParcelLink, AnimalResidence, AnimalResponsibility, ProducerMembership, AgriculturalServiceRole (incluidos InputSupplierRole, PesticideApplicatorRole y SeedOperatorRole), IdentifierAssignment, NameUsage y ContactPoint ahora siguen esta convención. AssetPartyRole y AssetAddressAssignment también la usan. Registration, RegistryEntry, AgriculturalParcel, AgriculturalCertification, LandTenureAssertion y RoadRestriction conservan su validez calendaria declarada. La [guía de migración de relaciones](relationship-date-migration.md) describe el contrato explícito de conversión y las asignaciones de instalaciones retiradas. Renombrar un `valid_to` inclusivo como `end_date` sin cambiar el límite pierde un día efectivo.

Un perfil consumidor debe declarar los límites de sus intervalos antes de comparar o convertir fechas. Por ejemplo, bajo una convención de días completos acordada explícitamente, `valid_to: 2026-06-30` corresponde a un cese con `end_date: 2026-07-01`. Renombrar la clave y conservar el 30 de junio cambiaría el significado. No aplique esta conversión cuando la precisión de la fuente o la semántica de sus límites sea desconocida. El ejemplo de trabajo agrícola documenta su propia convención de días completos; no cambia las definiciones normativas de propiedades de fecha.

## 6. Independencia de propiedades

Una propiedad como `start_date` se define una sola vez y se reutiliza en varios conceptos. Cuando una propiedad compartida necesita conjuntos de valores específicos de concepto (p. ej., `status` en Enrollment frente a Grievance), se especializa mediante referencias a vocabularios diferentes en lugar de disimular las diferencias.

### Reutilización de propiedades entre conceptos

La independencia de propiedades no se limita a campos estructurales repetidos. También pueden reutilizarse observables sustantivos entre conceptos. `water_source`, `sanitation_facility` y `dwelling_type` aparecen tanto en `SocioEconomicProfile` (contexto de registro de base) como en `DwellingDamageProfile` (evaluación posterior a un choque). En cada caso la propiedad se declara una sola vez y figura en la lista `properties` de cada concepto.

Las reglas que mantienen la coherencia:

1. **Un slot reutilizable por hecho nombrado.** `water_source` se declara una vez bajo `slots:` y se referencia desde ambos perfiles.
2. **El encuadre contextual vive en el concepto, no en la propiedad.** La definición de la propiedad nombra el observable ("la fuente principal de agua potable del hogar"). La definición de cada concepto nombra cómo se interpreta ese observable en ese concepto (registro de base o posterior al choque).
3. **La reutilización debe anunciarse en la definición narrativa de ambos conceptos.** Un lector en cualquiera de las dos páginas debe poder ver que el campo aparece también en otro lugar y por qué.
4. **La reutilización no hace que los registros sean compatibles en tipo.** Un registro `SocioEconomicProfile` y un registro `DwellingDamageProfile` son cosas distintas aun cuando sus valores de propiedad se solapen. Los adoptantes deben consultar la página del concepto, no la lista de propiedades, al serializar hacia una forma fuertemente tipada.
5. **Divida cuando la redacción diverge.** Si la definición propia de la propiedad necesita un texto distinto en cada contexto, cree dos propiedades. `location` y `location_of_assessment` se dividen así: `location` es la ubicación administrativa o por coordenadas registrada del hogar; `location_of_assessment` es el lugar donde se llevó a cabo físicamente una evaluación de daños posterior al choque, que puede diferir tras un desplazamiento.

`triggering_hazard_event` (en `DwellingDamageProfile`) y `triggering_vital_event` (en `CivilStatusAnnotation`) siguen el mismo principio. Inicialmente unificadas en una única propiedad `triggering_event` cuyo tipo se había ampliado a `concept:Event`, se dividieron porque el subtipo esperado tiene significado para validadores y profesionales; cada consumidor declara ahora su propia referencia tipada. Consulte [ADR-007](../../decisions/007-profile-property-reuse.md) para ver la argumentación completa.

## 7. Aplicabilidad por edad

Algunas propiedades con alcance en Person solo son significativas para grupos de edad específicos. El módulo corto y el módulo extendido del Washington Group se aplican a adultos; el módulo de funcionamiento infantil (CFM) se aplica a niños de 2-4 años y de 5-17 años. Los estándares de crecimiento de la OMS se aplican a menores de 5 años. En lugar de codificar estas reglas únicamente en el texto de definición (que las máquinas no pueden interpretar), las propiedades llevan un array opcional `age_applicability` de etiquetas controladas.

| Etiqueta | Rango numérico | Fuente del tramo |
|---|---|---|
| `infant_0_1` | 0-23 meses | Infancia general (cubre los módulos de lactantes MICS, crecimiento temprano OMS) |
| `child_2_4` | 2-4 años (24-59 meses) | Variante CFM 2-4; normas de crecimiento infantil OMS |
| `child_5_17` | 5-17 años | Variante CFM 5-17; también la definición CDN de "niño" |
| `adolescent` | 10-19 años | Definición de la OMS (deliberadamente transversal con child_5_17 y adult) |
| `adult` | 18 años o más | WG-SS / WG-ES |

### Relevancia temática, no elegibilidad

`age_applicability` responde a la pregunta: "¿a qué grupos de edad concierne esta propiedad?" No es un primitivo de filtro de elegibilidad. El filtrado por edad es responsabilidad del consumidor, calculado a partir de `date_of_birth`. Bajo este enfoque, la superposición entre etiquetas es una característica, no un defecto: una propiedad sobre salud reproductiva adolescente lleva tanto `child_5_17` como `adolescent` porque el tema concierne genuinamente tanto al tramo de menores de 18 años como al tramo OMS de 10-19 años.

Un consumidor que pregunta "¿es este campo relevante para un menor de 15 años?" evalúa la edad del menor frente a todos los tramos de la propiedad y verifica si alguno coincide. Un consumidor que pregunta "¿es este tema específico de la adolescencia?" comprueba la presencia de la etiqueta `adolescent`.

### Reglas de población

- Rellenar únicamente en propiedades que se adjuntan a `Person`. La aplicabilidad por edad carece de sentido en conceptos sin edad.
- No es obligatorio. La ausencia significa que la propiedad se aplica de forma amplia a cualquier edad.
- El validador impone la cobertura implicada por la bibliografía: las propiedades citadas por `washington-group-ss` o `washington-group-es` deben incluir `adult`; las propiedades citadas por `washington-group-cfm` deben incluir al menos uno de los tramos infantiles (`child_2_4` o `child_5_17`). Las propiedades pueden restringir la cobertura CFM cuando el texto de definición explica a qué variante corresponden.

## 8. Equivalentes externos frente a enlaces de serialización

El campo `external_equivalents` en las propiedades fue concebido originalmente para equivalentes en otras *ontologías* (vocabularios básicos SEMIC, DCI Core): una propiedad como `given_name` corresponde exactamente a `http://www.w3.org/ns/person#firstName`. La correspondencia es semántica: ambas describen el mismo concepto en una ontología alternativa.

El mismo campo también se usa para **enlaces de serialización** como FHIR R4 Observation con códigos LOINC. Estos no son equivalentes en el sentido SEMIC/DCI; son instrucciones sobre cómo serializar esta propiedad en un formato de interoperabilidad específico. La distinción importa al leer una página de detalle de propiedad: una fila SEMIC dice "este concepto existe en otra ontología"; una fila FHIR/LOINC dice "cuando serialice estos datos en FHIR, use este código."

Convención:
- Los códigos LOINC por elemento pertenecen a la **propiedad** (cada elemento WG tiene su propio código LOINC).
- Las referencias a una lista de respuestas LOINC para un vocabulario completo pertenecen al **vocabulario** (`standard.uri`). Ejemplo: `pregnancy-status` lleva un URI de lista de respuestas LOINC para todo el conjunto de valores.

## 9. Anotaciones de sensibilidad

Algunas propiedades revelan circunstancias sensibles independientemente de si identifican a una persona específica. `program_ref` revela la inscripción en un programa específico (que puede orientarse a VIH, discapacidad o pobreza). `grievance_type` revela que alguien presentó una queja.

| Nivel | Cuándo usar | Qué señala |
|---|---|---|
| `standard` | Predeterminado. Sin manejo especial más allá de la protección de datos normal. | Puede omitirse (se asume si está ausente). |
| `sensitive` | Revela circunstancias (salud, pobreza, condición de víctima) en la mayoría de los contextos. | Requiere justificación para recopilar o divulgar. |
| `restricted` | No debe aparecer en credenciales en puntos de servicio rutinarios. | Requiere una Evaluación de Impacto en la Protección de Datos. |

Esta es una advertencia para practicantes, no una etiqueta regulatoria. Si una propiedad constituye datos personales depende del registro en el que aparece, no de la propiedad en sí. Consulte [Divulgación selectiva](../selective-disclosure/) para la clasificación a nivel de credencial.


## 10. Mecanismos de escape para visualización

Algunas propiedades llevan semántica a nivel de esquema que está desacoplada intencionalmente de los requisitos de visualización específicos de cada jurisdicción. La propiedad `certificate_label` en `Parent` es un ejemplo: el modelo de datos almacena la naturaleza del rol (biológico, gestacional, legal, adoptivo) en `parental_role`, desacoplada del género, pero algunas jurisdicciones están obligadas por ley a imprimir etiquetas de género o posicionales ("madre", "padre", "progenitor 1", "progenitor 2") en el certificado civil. En lugar de forzar al esquema a llevar códigos de género, `certificate_label` proporciona un campo de texto libre para la etiqueta tal como debe aparecer en el documento impreso. La naturaleza del rol subyacente permanece legible por máquina y neutral en cuanto al género; el requisito de la capa de visualización se satisface sin contaminar el modelo de datos.
