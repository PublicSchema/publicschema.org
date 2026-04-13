# Casos de uso

PublicSchema ofrece definiciones comunes para la prestación de servicios públicos. Hay muchas formas de usarlo, desde alinear códigos de vocabulario en hojas de cálculo hasta emitir credenciales verificables. Esta página describe escenarios concretos en los que PublicSchema ayuda a los programas a coordinarse, compartir datos y llegar a las personas a quienes sirven.

## Contenido

- [Deduplicación entre programas de distintos sectores](#deduplicación-entre-programas-de-distintos-sectores)
- [Credenciales portátiles para poblaciones desplazadas](#credenciales-portátiles-para-poblaciones-desplazadas)
- [Reporte estandarizado entre programas y donantes](#reporte-estandarizado-entre-programas-y-donantes)
- [Adquisición de sistemas interoperables](#adquisición-de-sistemas-interoperables)
- [Del registro de nacimiento a la inscripción multisectorial](#del-registro-de-nacimiento-a-la-inscripción-multisectorial)
- [Seguimiento de la transición escuela-trabajo](#seguimiento-de-la-transición-escuela-trabajo)
- [Verificación de elegibilidad en el punto de atención](#verificación-de-elegibilidad-en-el-punto-de-atención)
- [Coordinación de respuesta ante desastres](#coordinación-de-respuesta-ante-desastres)
- [Comparación de programas entre países e investigación de políticas](#comparación-de-programas-entre-países-e-investigación-de-políticas)
- [Armonización de APIs en una federación](#armonización-de-apis-en-una-federación)
- [Qué artefactos importan para cada caso de uso](#qué-artefactos-importan-para-cada-caso-de-uso)

## Deduplicación entre programas de distintos sectores

**Quién:** Un gobierno que gestiona protección social, alimentación escolar y seguro de salud como programas separados, cada uno en un sistema diferente.

**El problema:** Cada sistema tiene registros de las mismas familias, descritos de forma diferente. La base de datos del ministerio de educación los llama "estudiantes", el sistema de salud los llama "pacientes" y el sistema de transferencias monetarias los llama "beneficiarios". No existe una forma confiable de verificar si una persona ya está inscrita en otro lugar. Incluso cuando los campos coinciden en nombre, los códigos divergentes hacen la comparación poco confiable: "active" en un sistema puede no significar lo mismo que "active" en otro.

**Cómo ayuda PublicSchema:** El equipo de integración mapea los campos de cada sistema a las propiedades de PublicSchema (given_name, identifiers, date_of_birth, enrollment_status). Un registro compartido puede entonces cruzar registros entre sistemas usando un vocabulario común. Ningún sistema necesita cambiar su modelo de datos interno.

**Artefactos clave:** Conceptos (Person, Enrollment), propiedades, códigos de vocabulario, correspondencias de sistemas.

## Credenciales portátiles para poblaciones desplazadas

**Quién:** Una persona refugiada registrada en un país que llega a un país de acogida donde es necesario verificar su identidad y sus inscripciones previas en servicios.

**El problema:** Los registros de la persona existen en los sistemas del país de origen, pero el país de acogida no tiene acceso a esos sistemas. Consultar al sistema de origen puede ser poco práctico o imposible. La persona necesita una forma de demostrar quién es y qué servicios ha recibido.

**Cómo ayuda PublicSchema:** El país de origen emite una credencial verificable SD-JWT usando los tipos de credencial de PublicSchema (IdentityCredential, EnrollmentCredential). El país de acogida puede verificar la credencial sin conexión porque usa un esquema compartido. La divulgación selectiva permite a la persona revelar solo lo necesario (nombre, fecha de nacimiento, inscripción previa) sin exponer datos sensibles.

**Artefactos clave:** Tipos de credencial, contexto JSON-LD, reglas de divulgación selectiva, esquemas JSON.

## Reporte estandarizado entre programas y donantes

**Quién:** Un donante, organismo coordinador o tablero gubernamental que agrega datos de múltiples programas, sectores o países.

**El problema:** Cada programa reporta usando sus propios códigos y nombres de campo. Uno usa "ACTV" para la inscripción activa, otro usa "1", un tercero usa "enrolled". Agregar cifras entre programas requiere una traducción manual en cada ciclo de reporte. Cuando estas traducciones son inexactas o incompletas (porque los códigos de un programa no se corresponden limpiamente con los de otro), los números agregados son poco confiables.

**Cómo ayuda PublicSchema:** El organismo coordinador define una plantilla de reporte que referencia los códigos de vocabulario de PublicSchema (enrollment-status, payment-status, delivery-channel). Cada programa mapea sus códigos internos una sola vez. A partir de ese punto, la agregación es mecánica.

**Artefactos clave:** Códigos de vocabulario, definiciones de conceptos, definiciones de propiedades.

## Adquisición de sistemas interoperables

**Quién:** Un gobierno que adquiere un nuevo registro, SIG o sistema de gestión de casos en cualquier sector.

**El problema:** Las solicitudes de propuesta especifican que "el sistema debe ser interoperable", lo cual es demasiado vago como para evaluarlo. Los proveedores lo interpretan como quieren. No existe una norma concreta contra la cual hacer pruebas.

**Cómo ayuda PublicSchema:** La solicitud de propuesta referencia PublicSchema directamente: "El sistema debe poder exportar registros de Persona (Person) con estas propiedades: given_name, family_name, date_of_birth, identifiers. Los campos de estado deben usar códigos de los vocabularios de PublicSchema." Esto funciona tanto si se adquiere un registro social, un sistema de información estudiantil o una base de datos de establecimientos de salud. Los proveedores obtienen un objetivo concreto; los evaluadores obtienen algo que pueden probar.

**Artefactos clave:** Definiciones de conceptos, inventario de propiedades, definiciones de vocabularios, esquemas JSON.

## Del registro de nacimiento a la inscripción multisectorial

**Quién:** Una autoridad de registro civil que emite certificados de nacimiento, conectada a programas que inscriben automáticamente a los recién nacidos (seguro de salud, subsidios infantiles, seguimiento de vacunación).

**El problema:** Se registra un nacimiento, pero cada programa receptor debe ser notificado por separado, usando su propio formato de ingreso. Las integraciones bilaterales entre el registro civil y cada programa son costosas de construir y mantener.

**Cómo ayuda PublicSchema:** El registro civil publica un registro usando las propiedades de Persona (Person) de PublicSchema (date_of_birth, sex, location). El ministerio de salud toma lo que necesita para el calendario de vacunación. El sistema de protección social usa el mismo registro para inscribir automáticamente al niño en un subsidio infantil. Cada sistema receptor consume desde la misma representación canónica en lugar de requerir su propia integración.

**Artefactos clave:** Conceptos (Person, Identifier), propiedades, códigos de vocabulario, esquemas JSON.

## Seguimiento de la transición escuela-trabajo

**Quién:** Un ministerio de educación y un ministerio de trabajo, cada uno con sus propios sistemas, que intentan rastrear los resultados de los programas para jóvenes.

**El problema:** El sistema educativo registra a los estudiantes inscritos en formación vocacional. El ministerio de trabajo registra a los participantes en programas de empleo. Ninguno de los sistemas conoce al otro. No hay forma de medir si los egresados de la formación vocacional ingresan efectivamente a programas de empleo.

**Cómo ayuda PublicSchema:** Ambos sistemas mapean sus modelos de datos a los conceptos Persona (Person) e Inscripción (Enrollment) de PublicSchema. Un equipo de políticas puede entonces vincular registros entre sistemas y medir resultados: de los estudiantes que completaron la formación vocacional, ¿cuántos se inscribieron en un programa de empleo en los seis meses siguientes? El vocabulario compartido hace posible el cruce sin fusionar bases de datos.

**Artefactos clave:** Conceptos (Person, Enrollment, Program), propiedades, códigos de vocabulario.

## Verificación de elegibilidad en el punto de atención

**Quién:** Un agente de pagos, un establecimiento de salud o una escuela que verifica la elegibilidad de una persona en el punto de atención.

**El problema:** Verificar la elegibilidad actualmente requiere una conexión en vivo con el registro central. En zonas remotas o durante interrupciones del sistema, la prestación del servicio se detiene porque la elegibilidad no puede confirmarse.

**Cómo ayuda PublicSchema:** La persona tiene una credencial verificable en su teléfono o tarjeta inteligente. En el punto de atención, el dispositivo del agente verifica la firma de la credencial y comprueba que enrollment_status es "active" y que el monto de la prestación es correcto. La verificación funciona sin conexión porque es criptográfica, no una consulta a una base de datos. Los datos personales que van más allá de lo necesario para la transacción permanecen ocultos mediante la divulgación selectiva.

**Artefactos clave:** Tipos de credencial, reglas de divulgación selectiva, esquemas JSON.

## Coordinación de respuesta ante desastres

**Quién:** Múltiples agencias que responden a un desastre natural: gobierno, agencias de la ONU y ONG, cada una registrando de forma independiente a las poblaciones afectadas.

**El problema:** Tres organizaciones están registrando a las familias afectadas en el mismo distrito usando diferentes formularios de ingreso y sistemas. No hay forma de saber si una familia ya fue registrada por otra agencia, lo que lleva a ayuda duplicada para algunas y brechas para otras.

**Cómo ayuda PublicSchema:** Al alinear la recopilación de datos con los conceptos Persona (Person) y Hogar (Household) de PublicSchema, un organismo coordinador puede deduplicar en todas las listas de registro, identificar las familias que ninguna agencia ha alcanzado aún y asignar recursos sin doble conteo.

**Artefactos clave:** Conceptos (Person, Household, Group, GroupMembership, Location), propiedades, códigos de vocabulario, esquemas JSON.

## Comparación de programas entre países e investigación de políticas

**Quién:** Un analista de políticas, investigador u organización internacional que compara programas de prestación de servicios públicos entre países.

**El problema:** Cada país define conceptos como "inscripción", "prestación" y "queja" de forma diferente. La comparación requiere interpretar manualmente la documentación de cada país, que es inconsistente y a menudo incompleta.

**Cómo ayuda PublicSchema:** El analista usa el inventario de conceptos y propiedades de PublicSchema como marco estructurado de comparación. Para cada país y sector, mapea el modelo de datos del programa local frente a PublicSchema. El resultado hace visibles las divergencias y permite nombrarlas con precisión: el País A recopila coordenadas GPS del hogar, el País B no. El País A define la inscripción "inactive" como "suspended", el País B la usa para indicar "completed".

**Artefactos clave:** Definiciones de conceptos (con descripciones multilingües), inventario de propiedades, definiciones de vocabularios, correspondencias de sistemas.

## Armonización de APIs en una federación

**Quién:** Un sistema nacional o regional que agrega datos de múltiples agencias, ministerios o niveles de gobierno.

**El problema:** Cinco agencias exponen cada una una API REST: registro social, SIG de educación, sistema de información de salud, registro civil, base de datos de extensión agrícola. Los nombres de campo y los códigos de valor difieren entre los cinco. Construir adaptadores personalizados para cada API es costoso y frágil.

**Cómo ayuda PublicSchema:** La federación exige que todas las APIs alineen los nombres de campo a las propiedades de PublicSchema y usen los códigos de vocabulario de PublicSchema. Cada agencia mantiene su esquema interno; simplemente expone una API compatible con PublicSchema. La capa federada habla un solo idioma en lugar de cinco.

**Artefactos clave:** Propiedades (como nombres de campo compartidos), códigos de vocabulario (como conjuntos de valores compartidos), esquemas JSON (para validación de contratos).

## Qué artefactos importan para cada caso de uso

| Caso de uso | Conceptos | Propiedades | Vocabularios | Esquemas JSON | JSON-LD | Credenciales |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Deduplicación entre programas | x | x | x | | | |
| Credenciales portátiles | x | x | | x | x | x |
| Reporte estandarizado | x | x | x | | | |
| Adquisición de sistemas | x | x | x | x | | |
| Cascada de registro de nacimiento | x | x | x | x | | |
| Seguimiento escuela-trabajo | x | x | x | | | |
| Verificación en punto de atención | | | | x | | x |
| Coordinación ante desastres | x | x | x | x | | |
| Comparación entre países | x | x | x | | | |
| Federación de APIs | | x | x | x | | |

La mayoría de los casos de uso requieren solo conceptos, propiedades y códigos de vocabulario. JSON-LD y las credenciales verificables son necesarios para un subconjunto de escenarios. **Por dónde empezar:**

- Para alinear códigos de valor sin cambiar su modelo de datos, consulte la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/).
- Para mapear campos entre sistemas existentes, consulte la [Guía de interoperabilidad y correspondencia](/docs/interoperability-guide/).
- Para diseñar un nuevo sistema compatible, consulte la [Guía de diseño de modelo de datos](/docs/data-model-guide/).
- Para usar contextos JSON-LD o emitir credenciales verificables, consulte la [Guía de JSON-LD y credenciales verificables](/docs/jsonld-vc-guide/).
