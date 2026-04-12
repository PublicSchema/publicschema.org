# Guía de interoperabilidad y correspondencia

Esta guía es para equipos que conectan sistemas existentes: mapeo de campos entre plataformas, construcción de intercambios de datos, consolidación de registros de múltiples fuentes o ejecución de canalizaciones ETL. PublicSchema actúa como punto de referencia compartido (una piedra de Rosetta) de modo que cada sistema solo necesita una correspondencia en lugar de una correspondencia hacia cada otro sistema.

## Contenido

- [Cuándo usar este enfoque](#cuándo-usar-este-enfoque)
- [El patrón Piedra de Rosetta](#el-patrón-piedra-de-rosetta)
- [Paso 1: Mapee sus campos a las propiedades de PublicSchema](#paso-1-mapee-sus-campos-a-las-propiedades-de-publicschema)
- [Paso 2: Mapee sus códigos a los vocabularios de PublicSchema](#paso-2-mapee-sus-códigos-a-los-vocabularios-de-publicschema)
- [Paso 3: Use la correspondencia para el intercambio de datos](#paso-3-use-la-correspondencia-para-el-intercambio-de-datos)
- [Paso 4: Valide con esquemas JSON](#paso-4-valide-con-esquemas-json)
- [Uso de la plantilla Excel para recopilación de datos](#uso-de-la-plantilla-excel-para-recopilación-de-datos)
- [Correspondencias de sistemas en los archivos de vocabulario](#correspondencias-de-sistemas-en-los-archivos-de-vocabulario)
- [Desafíos comunes de correspondencia](#desafíos-comunes-de-correspondencia)
- [Descargas disponibles](#descargas-disponibles)
- [Pasos siguientes](#pasos-siguientes)

## Cuándo usar este enfoque

Este enfoque funciona bien cuando:

- Dos o más sistemas necesitan intercambiar datos pero usan diferentes nombres de campo y códigos
- Está deduplicando registros entre programas o sectores
- Está construyendo un almacén de datos o panel de control que agrega datos de múltiples fuentes
- Está migrando datos de una plataforma a otra
- Está construyendo una capa de federación entre APIs de agencias

No necesita cambiar el modelo de datos interno de ningún sistema. La correspondencia vive entre los sistemas, no dentro de ellos.

## El patrón Piedra de Rosetta

Sin un referente compartido, conectar N sistemas requiere N*(N-1)/2 correspondencias bilaterales. Con 5 sistemas, son 10 tablas de correspondencia separadas a mantener.

Con PublicSchema como referente compartido, cada sistema mapea a PublicSchema una sola vez. Conectar un nuevo sistema significa una correspondencia, no N-1. Más importante aún, dado que cada sistema mapea a las mismas definiciones compartidas, el significado se preserva a través de la traducción. Sin un vocabulario compartido, las correspondencias bilaterales suelen ser imprecisas: los códigos de un sistema pueden no tener equivalentes en otro.

![Cada sistema mapea a PublicSchema una sola vez](/images/rosetta-stone.svg)

Este patrón funciona tanto para nombres de campo (propiedades) como para códigos de valor (vocabularios).

## Paso 1: Mapee sus campos a las propiedades de PublicSchema

Comience identificando qué concepto de PublicSchema corresponde a la entidad en su sistema. Explore la [página de conceptos](/concepts/) o descargue el **Excel de definición** de un concepto para ver todas sus propiedades en un solo lugar.

Para cada campo de su sistema, encuentre la propiedad de PublicSchema correspondiente:

| Campo de su sistema | Su tipo | Propiedad de PublicSchema | Tipo PS |
|---|---|---|---|
| `first_name` | varchar(100) | `given_name` | string |
| `last_name` | varchar(100) | `family_name` | string |
| `dob` | date | `date_of_birth` | date |
| `enroll_date` | datetime | `enrollment_date` | date |
| `status` | int (FK) | `enrollment_status` | vocabulary |
| `gps_lat`, `gps_lon` | decimal | `geo_location` | geojson_geometry |

Algunos aspectos a tener en cuenta:

- **No todos los campos tendrán una coincidencia.** Algunos campos son específicos de su sistema y no tienen equivalente canónico. Eso está bien; documente la brecha.
- **Algunos campos pueden dividirse o combinarse.** Su sistema podría almacenar un nombre completo en un solo campo donde PublicSchema tiene `given_name` y `family_name` por separado, o viceversa.
- **Las diferencias de tipo son esperables.** Su base de datos podría usar enteros o claves foráneas donde PublicSchema usa códigos de vocabulario. La correspondencia maneja la traducción.

La descarga **CSV** del concepto le da una lista plana de propiedades con tipos y definiciones, útil como punto de partida para su tabla de correspondencias.

## Paso 2: Mapee sus códigos a los vocabularios de PublicSchema

Para cualquier campo respaldado por un conjunto de valores controlados (códigos de estado, género, tipos de documento, etc.), mapee sus códigos al vocabulario canónico. Consulte la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/) para un recorrido detallado.

El resultado clave es una tabla de correspondencia de códigos para cada vocabulario:

| Su código | Código de PublicSchema | Notas |
|---|---|---|
| `1` | `active` | |
| `2` | `suspended` | |
| `3` | `completed` | Su "closed" corresponde a PS "completed" |
| `4` | *(sin correspondencia)* | Su "archived" no tiene equivalente en PS |

## Paso 3: Use la correspondencia para el intercambio de datos

Una vez que tenga las correspondencias de campos y códigos, puede usarlas de varias maneras:

### Intercambio de datos directo entre dos sistemas

El Sistema A exporta en su propio formato. Una capa de traducción mapea los campos y códigos de A a las propiedades y códigos de vocabulario de PublicSchema. Una segunda capa de traducción mapea de PublicSchema al formato del Sistema B.

![El Sistema A mapea a PublicSchema, luego al Sistema B](/images/data-exchange-flow.svg)

### Consolidación de datos (ETL)

Múltiples fuentes se mapean al formato canónico de PublicSchema y se cargan en un almacén de datos compartido:

![Múltiples fuentes mapean a PublicSchema, luego consolidan](/images/etl-consolidation.svg)

### Federación de APIs

Cada agencia expone una superficie de API alineada con PublicSchema. La capa de federación consulta todas las APIs usando los mismos nombres de campo y códigos de vocabulario. Consulte el [caso de uso de armonización de APIs](/docs/use-cases/#armonización-de-apis-en-una-federación) para un escenario concreto.

## Paso 4: Valide con esquemas JSON

PublicSchema provee un esquema JSON por concepto. Úselos para validar los datos después de la correspondencia y antes de la carga:

```python
import json
import jsonschema

schema = json.load(open("Person.schema.json"))
record = {
    "given_name": "Amina",
    "family_name": "Diallo",
    "date_of_birth": "1988-03-15",
    "gender": "female"
}
jsonschema.validate(record, schema)
```

La validación detecta:

- Campos que no se mapearon correctamente (tipo incorrecto, contexto requerido faltante)
- Códigos de vocabulario que no están en el conjunto canónico
- Problemas estructurales (arreglos donde se esperan valores únicos, o viceversa)

## Uso de la plantilla Excel para recopilación de datos

Cada página de concepto ofrece una descarga de **Plantilla Excel**. Se trata de un libro de trabajo de entrada de datos donde:

- La fila 1 tiene etiquetas de campo legibles para personas
- La fila 2 tiene los IDs de propiedad de PublicSchema
- Los campos respaldados por vocabulario tienen validación de lista desplegable (solo se aceptan códigos canónicos)
- Los comentarios de celda incluyen definiciones de propiedad

Esto es útil cuando:

- Recopila datos de equipos de campo que trabajan con hojas de cálculo
- Necesita un formato canónico para la ingesta de datos sin construir una aplicación personalizada
- Desea prototipar un formulario de recopilación de datos antes de comprometerse con un sistema

Los datos ingresados en la plantilla ya están alineados con PublicSchema, por lo que pueden cargarse en cualquier sistema que tenga una correspondencia con PublicSchema.

## Correspondencias de sistemas en los archivos de vocabulario

Algunos vocabularios incluyen correspondencias preconstruidas para sistemas específicos (OpenIMIS, DCI, etc.) en sus archivos YAML de origen. Estas correspondencias listan los códigos, las etiquetas de cada sistema y cómo se mapean a los códigos canónicos.

Consulte las páginas de vocabulario para ver si su sistema ya está mapeado. Si es así, puede usar la correspondencia directamente en lugar de construir una desde cero.

Por ejemplo, el vocabulario gender-type incluye correspondencias para OpenIMIS y DCI, mostrando que OpenIMIS usa `"M"/"F"/"O"` y DCI usa `"1"/"2"/"0"` para los mismos valores canónicos.

Consulte el [Ejemplo de correspondencia](/docs/mapping-example/) para un recorrido completo de las correspondencias de sistemas.

## Desafíos comunes de correspondencia

### Diferencias de granularidad

Su sistema podría tener una sola entidad "Person" donde PublicSchema separa Persona (Person), Identificador (Identifier) y Dirección (Address) en conceptos distintos. O viceversa: su sistema podría tener tablas separadas que se mapean a propiedades de un solo concepto de PublicSchema.

Enfoque: mapee los campos a la propiedad de PublicSchema correcta independientemente de en qué entidad se encuentren en su sistema. Los límites de concepto en PublicSchema son semánticos, no requisitos estructurales.

### Diferencias temporales

Su sistema podría almacenar un solo campo de estado donde PublicSchema espera un patrón acotado en el tiempo (start_date, end_date, status). O su sistema podría tener una tabla de historial completo donde PublicSchema modela un solo estado actual.

Enfoque: decida si está mapeando el estado actual o el historial completo. Para el estado actual, mapee el registro más reciente. Para el historial, cada fila se mapea a un registro de PublicSchema separado con su propio rango de fechas.

### Correspondencias de valores de uno a varios

Su sistema usa "inactive" para casos que PublicSchema divide en "suspended", "completed" y "exited".

Esto no es solo un inconveniente de correspondencia; es una brecha de información. Cuando mapea "inactive" a un solo código, pierde la distinción entre alguien cuyas prestaciones están temporalmente pausadas y alguien que ha salido definitivamente. Los sistemas que consumen los datos mapeados no pueden recuperar la precisión perdida.

Enfoque: si no puede distinguir entre ellos a partir de sus datos, mapee al código más amplio aplicable y documente la ambigüedad. Si puede distinguir (p. ej., consultando campos relacionados), añada lógica a la correspondencia. Cuantos más sistemas adopten directamente los códigos de vocabulario compartidos, menos se presentará este problema.

### Conceptos faltantes

Su sistema tiene entidades que PublicSchema no cubre, o PublicSchema tiene conceptos que su sistema no implementa.

Enfoque: documente la brecha. Para sus entidades adicionales, considere si podrían modelarse como extensiones (consulte el [Mecanismo de extensión](/docs/extension-mechanism/)). Para la cobertura faltante, es posible que no necesite cada concepto.

## Descargas disponibles

**Por concepto:**

| Formato | Qué es | Mejor para |
|---|---|---|
| **CSV** | Propiedades con tipos y definiciones | Punto de partida para tablas de correspondencia de campos |
| **Excel de definición** | Libro de trabajo de múltiples hojas con metadatos, propiedades y vocabularios de referencia en EN/FR/ES | Entender un concepto en su totalidad, compartir con partes interesadas no técnicas |
| **Plantilla Excel** | Libro de trabajo de entrada de datos con validación de listas desplegables | Recopilación de datos, prototipado, formato intermedio canónico |
| **JSON-LD** | Concepto como datos enlazados | Acceso legible por máquina, cadenas de herramientas RDF |

**Por vocabulario:**

| Formato | Qué es | Mejor para |
|---|---|---|
| **CSV** | Códigos con etiquetas y definiciones multilingües | Tablas de correspondencia de códigos |
| **JSON-LD** | Vocabulario como SKOS ConceptScheme | Acceso programático |

## Pasos siguientes

- Si solo necesita alinear códigos de valor (no nombres de campo), la [Guía de adopción de vocabulario](/docs/vocabulary-adoption-guide/) es un punto de partida más ligero.
- Si está diseñando un nuevo sistema desde cero, consulte la [Guía de diseño de modelo de datos](/docs/data-model-guide/).
- Si desea usar contextos JSON-LD o emitir credenciales verificables, consulte la [Guía de JSON-LD y credenciales verificables](/docs/jsonld-vc-guide/).
