# Principios de diseño

## 1. Semántico, no estructural

Los conceptos tienen significado. Una Persona (Person) no es un conjunto de campos; es una entidad con nombre y una definición escrita para practicantes del dominio. El problema de interoperabilidad radica en la divergencia de vocabulario: los sistemas usan nombres diferentes para las mismas entidades del mundo real, y cuando esos nombres codifican decisiones semánticas distintas, las correspondencias entre ellos pierden información. PublicSchema provee definiciones compartidas que hacen explícitas las equivalencias y preservan el significado a través de los sistemas.

## 2. Descriptivo, no normativo

Nada es obligatorio. Los sistemas adoptan los conceptos, propiedades y vocabularios que les aplican. PublicSchema describe cómo se ven los datos de prestación en todos los sistemas; no impone qué debe recopilar ningún sistema.

## 3. Basado en evidencia e incremental

Los datos de convergencia impulsan las prioridades. Una propiedad presente en 6 de 6 sistemas vale la pena estandarizar antes que una presente en 2 de 6. Comience con lo que está confirmado y extiéndalo cuando la adopción revele una necesidad genuina.

## 4. Lenguaje sencillo para practicantes

Las definiciones están escritas para responsables de políticas y gestores de programas, no para desarrolladores. "Los estados del ciclo de vida de una inscripción en un programa" es preferible a "una enumeración de códigos de estado aplicables a la entidad de registro de personas beneficiarias".

## 5. Supertipos abstractos

Algunos conceptos existen solo como fundamentos compartidos para subtipos mas especificos. Agent, Event, Party y Profile llevan `abstract: true`, lo que significa que definen propiedades comunes pero nunca se instancian directamente. Los subtipos (por ejemplo, FunctioningProfile, ScoringEvent, Organization) heredan esas propiedades y agregan las suyas. Agent es el supertipo del lado del actor (Person, Organization, SoftwareAgent); Party es el supertipo del lado del beneficiario (Person, Group). Person pertenece a ambos. Consulte [ADR-006](../decisions/006-profile-hierarchy.md) y [ADR-008](../decisions/008-agent-organization.md).

## 6. Separacion entre observacion y puntuacion

La recopilacion y la puntuacion de datos son pasos distintos, con actores, marcas de tiempo y pistas de auditoria diferentes. Los subtipos de Profile registran las respuestas estructuradas de una administracion unica de instrumento y tambien pueden llevar resultados derivados de aplicar la regla de puntuacion canonica del instrumento (por ejemplo, z-scores y bandas de estado en AnthropometricProfile, el grupo de consumo FCS en FoodSecurityProfile, o el identificador de discapacidad WG-SS en FunctioningProfile). ScoringEvent registra el acto de aplicar una regla no estandar, un umbral alternativo o recalcular un puntaje tras una revision de regla. Esta separacion permite a los sistemas recalcular puntajes sin re-recopilar datos, manteniendo los resultados canonicos cerca de las observaciones que los produjeron. Consulte [ADR-006](../decisions/006-profile-hierarchy.md) y [ADR-010](../decisions/010-profile-derived-outputs.md).

## 7. Categorias de propiedades

Las propiedades se agrupan por categoria tematica (por ejemplo, funcionamiento, nutricion, vivienda) en lugar de listarse de forma plana. Las categorias se definen en `schema/categories.yaml` y se representan como agrupaciones visuales en las paginas de detalle de conceptos. Esto ayuda a los profesionales a localizar las propiedades relevantes en conceptos que llevan muchas.

## 8. Metadatos de instrumento

Las propiedades que registran el contexto de recopilacion (modo de administracion, respondiente, relacion con el respondiente, aplicabilidad por edad) acompanan los datos de observacion, sin un archivo de metadatos separado. Esto garantiza que un registro de Profile sea autodescriptivo: un consumidor puede determinar como se recopilaron los datos sin consultar un registro externo. Consulte [schema-design.md seccion 7](schema-design.md#7-age-applicability) para detalles de aplicabilidad por edad.

## Véase también

- [Diseño de esquema](../schema-design/): nomenclatura, alcance y modelado
- [Diseño de vocabulario](../vocabulary-design/): conjuntos de valores controlados y correspondencias de sistemas
- [Versionado y madurez](../versioning-and-maturity/): garantías de estabilidad y reglas de evolución
- [Divulgación selectiva](../selective-disclosure/): diseño de privacidad para credenciales
