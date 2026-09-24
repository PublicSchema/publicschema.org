# Especificación de indicadores

**Estado:** Diseño en borrador, implementado parcialmente &middot; **Autoría:** grupo de trabajo de PublicSchema &middot; **Revisión del estado de implementación:** 7 de septiembre de 2026

## Implementación actual

El repositorio proporciona el modelo LinkML de métricas en `schema/metrics.yaml`, las fuentes del catálogo en borrador en `schema/metric_catalog/` y una proyección del catálogo para el sitio generada por `just build` (o por `just metrics-data` para esa proyección por sí sola). Los catálogos incluidos en el repositorio contienen actualmente 597 entradas en borrador: 580 entradas de DHS y 17 entradas de ILO. Solo tres entradas de DHS tienen bloques de cálculo redactados; las demás entradas son semillas de metadatos, no definiciones ejecutables de indicadores.

La compilación proyecta estas fuentes en `dist/metrics_catalog.json` para su consulta. No ejecuta SQL, VTL ni CQL, no establece la corrección de los cálculos ni proporciona una vinculación ModelInfo de CQL para PublicSchema. La publicación CSVW, SDMX y RDF Data Cube específica de métricas es un objetivo de diseño, no una exportación implementada. La cadena ordinaria de RDF del vocabulario, JSON Schema y descargas no establece esas capacidades de publicación de métricas.

Las secciones siguientes describen el modelo propuesto y los requisitos de conformidad. Las reglas sobre cálculos ejecutables, librerías predeterminadas, aceptación por las agencias y formatos de publicación son objetivos de diseño, salvo que se identifiquen explícitamente arriba como implementadas. El ejemplo desarrollado es ilustrativo; sus URLs de librería y de esquema no son artefactos publicados prometidos. Las versiones y fechas de la hoja de ruta registran la propuesta original, no un compromiso de publicación.

Esta especificación propone un nuevo dominio dentro de PublicSchema para **definiciones declarativas y ejecutables de indicadores derivables**: métricas agregadas calculadas a partir de conceptos de PublicSchema a nivel de registro (Person, Household, Enrollment, PaymentEvent, ScoringEvent, etc.). Complementa la capa existente a nivel de registro; no la reemplaza.

**Objetivo de diseño: solo indicadores derivables.** Una definición de métrica completa debe incluir un cálculo sobre microdatos mapeados a PS. Una semilla del catálogo sin ese cálculo todavía no cumple este objetivo. Los indicadores de origen externo (compilados a partir de tablas de origen de institutos nacionales de estadística (NSI) o de agencias, sin derivación desde microdatos) siguen siendo valiosos, pero quedan fuera del alcance aquí; corresponden a la capa de procedencia existente.

La forma se toma prestada de FHIR R5 Measure (cálculo) y de SDMX 3.0 (estructura). PublicSchema es la fuente de verdad en LinkML; los formatos derivados se obtienen mediante generadores.

## Por qué PublicSchema necesita esto

PublicSchema cubre hoy personas, hogares, programas, pagos, perfiles y ejecuciones de puntuación: la forma a nivel de registro de los sistemas de protección social y de prestación de servicios afines. Quienes financian, el personal estadístico, los equipos de seguimiento y evaluación (SyE) y quienes investigan políticas públicas no consumen esos datos registro por registro; consumen **indicadores** agregados: tasa de cobertura, adecuación, regularidad de los pagos, fugas, tasa de error, prestación media por beneficiario, proporción de mujeres entre las personas receptoras.

Tres problemas concretos de la situación actual:

1. **Cada programa reinventa los mismos indicadores**, con denominadores sutilmente distintos. La «cobertura de protección social» calculada sobre un denominador de inscripciones activas no es comparable con la calculada sobre un denominador de población elegible. Sin definiciones ejecutables compartidas, la comparación entre países es ficción.
2. **El mismo indicador se reempaqueta entre 4 y 6 veces** para alimentar a ILO ([ILOSTAT](https://ilostat.ilo.org/)), al Banco Mundial ([ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire)), a Eurostat ([ESSPROS](https://ec.europa.eu/eurostat/web/social-protection)), a OECD ([SOCX](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html)), a las Naciones Unidas ([SDG 1.3.1](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf)) y a la propia oficina de estadística del país. Cada consumidor quiere su propia Data Structure Definition (DSD).
3. **«¿Cómo se calculó esto?» rara vez tiene respuesta.** La metodología vive en un PDF, la fórmula en una hoja de cálculo y las tablas de consulta en una lista de códigos que nadie versiona.

La primitiva de métricas propuesta pretende resolver los tres: una **definición ejecutable canónica** por indicador, **URIs de alineación** que dirigen una única observación hacia muchos DSD de consumidores y un **bloque de cálculo declarativo** auditable y reejecutable.

## Alcance

**Dentro del alcance:**
- Definición declarativa de indicadores o métricas agregados derivables.
- Cálculo declarativo sobre conceptos de PublicSchema a nivel de registro.
- Metadatos dimensionales (qué desagregaciones admite una métrica).
- Metadatos de referencia (definición, metodología, fuente, responsable, licencia, versión).
- Observaciones (los valores efectivamente reportados, con valores de dimensión y atributos a nivel de observación).
- Correspondencias con marcos de indicadores externos (DSD de agencias SDMX, UN SDG, ASPIRE, ESSPROS, SOCX, DHIS2, IATI, HXL).

**Fuera del alcance:**
- **Indicadores de origen externo.** Si una «métrica» es solo una cita de un valor compilado por un NSI o una agencia de origen, sin derivación a nivel de microdatos, no pertenece aquí; permanece en la capa de procedencia que ya llevan los conceptos de PS a nivel de registro.
- Reemplazar la puntuación por registro. `ScoringEvent` sigue registrando la aplicación de una regla a un sujeto; las métricas agregan sobre muchos sujetos.
- Reemplazar las herramientas de las agencias estadísticas. La capa de publicación propuesta describe la métrica y emitiría SDMX; no ejecuta SDMX Web Services ni registros de agencias.
- Alojar datos brutos a nivel de registro. Una definición de métrica hace referencia a conceptos a nivel de registro mediante URI; las observaciones solo llevan el valor agregado.
- Definir un nuevo entorno de ejecución de cálculos. El lenguaje de criterios es intercambiable (identificado por tipo de medio IANA); las integraciones propuestas se dirigen a motores SQL, VTL y CQL existentes.
- Métricas de evaluación de modelos de IA / ML. Tema adyacente que merece una especificación aparte; no se incorpora aquí.

## Niveles de conformidad

El modelo de conformidad propuesto define tres niveles. No son certificaciones del catálogo ni de la compilación actuales:

| Nivel | Nombre | Capacidad |
|------|------|------------|
| **1** | Consumidor del catálogo | Lee definiciones de Metric de PS (LinkML / JSON Schema) y resuelve URIs de alineación. Sin emisión. |
| **2** | Publicador de observaciones | Emite JSON-LD y CSVW válidos de `MetricObservation` conforme a los esquemas de PS. El umbral mínimo para decir que «esta plataforma habla PS Metrics». |
| **3** | Publicador vinculado a SDMX | Nivel 2 más emisión SDMX-CSV v2.1 conforme a un DSD referenciado. El umbral para una publicación de nivel institucional ante ILO / WB / OECD / Eurostat. |

En el nivel 1 se sitúan la mayoría de las herramientas de investigación de solo lectura. En el nivel 2, las plataformas de prestación (OpenSPP, OpenIMIS, bases de datos de programas DHIS2). En el nivel 3, los institutos nacionales de estadística y las agencias custodias.

## Modelo conceptual

El modelo conceptual tiene siete clases principales, con auxiliares de cálculo y de valores estructurados en LinkML. La forma es el modelo de información de SDMX 3.0 (dimensiones, medidas, atributos, listas de códigos, observaciones) ampliado con la semántica de cálculo de FHIR Measure. La [separación entre observación y puntuación](/docs/design-principles/#6-separación-entre-observación-y-puntuación) (Principio 6) se extiende de la puntuación por registro a las métricas agregadas: una `MetricObservation` es a una `Metric` lo que un `ScoringEvent` es a una `ScoringRule`. Las métricas pueden llevar [`core: true`](/docs/design-principles/#9-core-and-extended-property-tiers) (Principio 9) para marcar el subconjunto imprescindible.

```text
                     +--------+
                     | Metric +--- family (slot, optional grouping)
                     +---+----+
                         | 1
                         | has
                         v
   +---------+    +------+------+   +------------+
   | Concept |<---+ Metric defs +-->| MetricCalc |
   | (skos)  |    +------+------+   +------------+
   +---------+           |
                         |
                         | declares
                         v
                  +------+------+      +------+------+
                  | MetricDim   |      | MetricAttr  |
                  +------+------+      +-------------+
                         ^
                         |  realises against
                         |
                  +------+------+         +------------+
                  | MetricObs   +-------->|   Period   |
                  +------+------+         +------------+
                         ^
                         | bundled in
                         |
                  +------+------+
                  | MetricRpt   |
                  +-------------+
```

### `Metric`

Un indicador con nombre, con URI estable, definición en prosa, tipo de valor, unidad, dimensiones declaradas, atributos declarados a nivel de observación, alineaciones externas declaradas y un cálculo (único y primario).

Slots principales:
- `id`: identificador opaco, fragmento de URI en forma de slug.
- `class_uri`: `publicschema:Metric`. Mapeo RDF propuesto: un `qb:MeasureProperty` y un `skos:Concept`.
- `title`, `description`: etiquetas multilingües llevadas en `annotations.label_es` / `label_fr` / `description_es` / `description_fr` (estilo propio de PS).
- `value_type`: vocabulario controlado (`count`, `proportion`, `ratio`, `currency_amount`, `index`, `duration`, `nominal`, `ordinal`, `qualitative`).
- `unit`: UCUM, ISO 4217 (moneda) o `unitless`.
- `multiplier`: `0` / `3` / `6` al estilo SDMX (unidades / miles / millones). Valor predeterminado: `0`.
- `decimals`: precisión de reporte.
- `dimensions`: lista ordenada de referencias a `MetricDimension`.
- `attributes`: lista de referencias a `MetricAttribute`.
- `calculation`: un `MetricCalculation` (véase [Modelo de cálculo](#modelo-de-cálculo)).
- `topic`: coverage / adequacy / expenditure / leakage / targeting / inclusion_error / exclusion_error / regularity / processing_time / satisfaction.
- `concept_uri`: URI de `skos:Concept` (para que varias Metrics puedan compartir un concepto).
- `family`: etiqueta URI opcional que agrupa métricas que comparten dimensiones (guía la generación del DSD cuando está presente; sin clase separada). Una clase `MetricFamily` de primer nivel se aplaza hasta que existan tres familias reales.
- `aligns_with`: lista de URIs externos.
- `core`: marcador booleano para el subconjunto imprescindible.
- `status`: `bibo:draft` / `bibo:published` / `bibo:deprecated`.
- `version`, `replaces`, `replaced_by`: slots de versionado, nuevos en este dominio; trasladarlos a `schema/common.yaml` si otros conceptos portadores de registros los adoptan.

`Metric` es una definición de catálogo, no un evento en el tiempo, por lo que no es subclase de `Event`.

### `MetricDimension`

Una dimensión tipada que desagrega una métrica. Slots:
- `id`, `title`, `description` (+ multilingües).
- `class_uri`: `publicschema:MetricDimension`; mapeo RDF propuesto: `qb:DimensionProperty`.
- `concept_uri`: concepto interdominio de SDMX cuando existe (`REF_AREA`, `SEX`, `AGE`, `UNIT_MEASURE`, `TIME_PERIOD`, `FREQ`). Se referencia por URN en la prosa; sin IRI RDF `sdmx:` ficticio.
- `range`: enum LinkML (vocabulario de PublicSchema) o URI de lista de códigos externa.
- `code_list_uri`: URN canónica de la lista de códigos (lista de códigos de la agencia SDMX cuando existe). Los vocabularios de PS son canónicos; el emisor SDMX los envuelve.
- `is_required`: booleano.
- `ordering`: entero (posición en el DSD).

La librería inicial propuesta de MetricDimensions incluye: país (ISO 3166-1 alfa-2 vinculado a `CL_AREA`), región / admin1 (OCHA COD-AB), sexo (vocabulario de sexo de PS vinculado a `CL_SEX(2.1)`), edad (año simple + tramos estándar, vinculada a `CL_AGE`), urbano / rural, quintil de riqueza, situación de discapacidad (WG-SS), tipo de programa (taxonomía de programas de PS), modalidad de la prestación, período de referencia, frecuencia (`FREQ`).

### `MetricAttribute`

Una anotación no clave sobre una observación, una serie o un conjunto de datos. La librería predeterminada propuesta refleja los [conceptos interdominio de SDMX](https://sdmx.org/sdmx_cdcl/) para dar soporte a un futuro emisor SDMX. Identificadores predeterminados y **niveles de adjunción correctos** (SDMX 3.0 IM):

- **A nivel de observación:** `OBS_STATUS` (lista de códigos `CL_OBS_STATUS(2.3)`), `CONF_STATUS` (`CL_CONF_STATUS(1.4)`), `COMMENT_OBS`, más las extensiones de PS `cell_count`, `confidentiality_status`, `data_quality_flag`.
- **A nivel de serie / grupo de dimensiones:** `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `REF_PERIOD`, `BASE_PER`, `EMBARGO_DATE`, `COMMENT_TS`.
- **A nivel de conjunto de datos:** `COMPILING_ORG`, `SOURCE_AGENCY`, `TITLE`, `TITLE_COMPL`, `CURRENCY`, `CURRENCY_DENOM`, `PRICE_BASE`. (`DATA_PROVIDER` se encuentra en el encabezado del Dataset SDMX, no como atributo.)
- **Flujo de trabajo de ruptura de serie:** `OBS_PRE_BREAK`, `BREAK_REASON` (`CL_BREAK_REASON`).

Notas:
- `OBS_VALUE` es el componente de medida de SDMX 3.0 (no un atributo); se lleva en `MetricObservation.value`.
- `TIME_FORMAT` está obsoleto en SDMX 3.0 (se asume ISO 8601) y no forma parte de la librería predeterminada.
- Se vincula a `qb:AttributeProperty` en la emisión RDF. El slot `attachment_level` (`dataset` / `series` / `observation`) determina dónde coloca cada atributo el emisor SDMX.

El alcance de la fase fundacional propuesta selecciona seis atributos predeterminados redactados por PS: `OBS_STATUS`, `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `cell_count`, `confidentiality_status`. Los demás atributos se aplazan hasta que un caso de uso concreto los necesite.

### `MetricCalculation`

El cálculo declarativo. Véase [Modelo de cálculo](#modelo-de-cálculo). Uno por Metric; las variantes más ricas se llevan mediante una referencia a una librería. El análogo por registro es [`ScoringRule`](/ScoringRule/) (`schema/misc.yaml`); `MetricCalculation` agrega entre sujetos.

### `MetricObservation`

Un valor reportado. Slots:
- `metric`: URI de la `Metric`.
- `period`: un `Period`.
- `dimension_values`: lista ordenada de pares `{dimension_uri, code}` (no un mapa; el orden importa para la ida y vuelta del DSD).
- `value`: número, con un tipo que coincide con el `value_type` de la métrica. La **escala está fijada por `Metric.unit` + `Metric.multiplier`**: para `value_type: proportion` con `unit: unitless`, el valor está en 0..1; para porcentajes, establezca `unit: PT` (código `UNIT_MEASURE` de SDMX) y el valor está en 0..100. Cuando `UNIT_MEASURE` también aparece en `attribute_values`, debe ser igual a `Metric.unit`; la observación no puede anular la escala.
- `attribute_values`: mapa de URI de `MetricAttribute` a valor.
- `calculation_uri`: URI de la definición `MetricCalculation` que esta observación realiza.
- `execution_uri`: URI opcional de un registro de ejecución (procedencia: agente de software, marca de tiempo de la ejecución, conjunto de parámetros). Se recomienda una alineación ligera con PROV-O; los detalles se aplazan.

Se vincula a `qb:Observation` y a la Observation de SDMX 3.0. `MetricObservation` es `is_a: Event` ([Principio 5](/docs/design-principles/#5-supertipos-abstractos)); hereda `identifiers` de `Event`.

### `MetricReport`

Un conjunto de observaciones con metadatos del editor: `publisher` (con rango sobre [`Agent`](/docs/design-principles/#5-supertipos-abstractos)), `published_at`, `reference_date`, `methodology_uri`, `license`, `contact_uri`, `observations[]`, `dsd_uri`. Se vincula a `qb:DataSet`.

### `Period`

La cobertura temporal de una MetricObservation. PS reifica el período (en lugar de llevar `start_date` / `end_date` en línea como otros subtipos de `Event`) porque el emisor SDMX / Data Cube necesita un único intervalo direccionable por URI para satisfacer la [restricción de integridad IC-11 de W3C Data Cube](https://www.w3.org/TR/vocab-data-cube/#wf). Slots: `period_type` (`point_in_time` / `span` / `cohort` / `fiscal_year` / `calendar_year`), `start_date`, `end_date`, `granularity` (year / quarter / month / day), `reference_period_type`, `frequency` (valor de la lista de códigos `FREQ`: A / Q / M / D / W / H). `end_date` es el último día cubierto, como en todo PublicSchema ([ADR-027](../../decisions/027-end-date-boundary.md)): el año civil 2024 va de `2024-01-01` a `2024-12-31`, del mismo modo que lo expresa un `Period` de FHIR o una cobertura temporal DCAT.

## Modelo de cálculo

Tomado de [FHIR R5 Measure](https://hl7.org/fhir/R5/measure.html) y traducido a URIs de slots de PS. FHIR Measure es el único estándar con adopción de nivel regulatorio (eCQM de CMS, medidas digitales HEDIS de NCQA) para «calcular un indicador agregado a partir de datos heterogéneos a nivel de registro, con definiciones auditables y procedencia reejecutable». Tomamos prestada la forma; no dependemos de los tipos de FHIR.

### Forma de `MetricCalculation`

```yaml
calculation:
  scoring: proportion | ratio | continuous-variable | cohort
  subject_class: <PS class URI>   # e.g., publicschema:Person, publicschema:Enrollment
  populations:
    - type: initial-population
      language: application/sql | application/vtl | text/cql
      criteria: <expression string OR @ref to library>
    - type: denominator
      language: ...
      criteria: ...
    - type: denominator-exclusion
      language: ...
      criteria: ...
    - type: numerator
      language: ...
      criteria: ...
    # optional: numerator-exclusion, denominator-exception,
    # measure-population, measure-population-exclusion, measure-observation
  stratifiers:
    - code: by-sex
      language: ...
      criteria: ...
      components:
        - code: by-sex-and-age
          language: ...
          criteria: ...
  rate_aggregation: average | sum | none
  improvement_notation: increase | decrease | policy_dependent
  libraries:
    - https://publicschema.org/metrics/library/sp-coverage-cql-1.0
```

`subject_class` es una divergencia respecto de `subject[x]` de FHIR Measure (que es `CodeableConcept | Reference(Group)`): los sujetos de PS son URIs de clases de PS. `improvement_notation` acepta `policy_dependent` para métricas no clínicas en las que la dirección deseable depende del enfoque de política pública (por ejemplo, gasto respecto del PIB).

### Tipos de población y validez del método de puntuación

Las nueve poblaciones de FHIR Measure y su aplicabilidad a cada método de puntuación:

| Tipo | Propósito |
|------|---------|
| `initial-population` | El universo de registros que la métrica considera. |
| `denominator` | Subconjunto de initial-population que reúne las condiciones para el denominador. |
| `denominator-exclusion` | Registros eliminados del denominador. |
| `denominator-exception` | Registros contados en el denominador pero exentos del numerador. |
| `numerator` | Subconjunto del denominador que cumple la condición de éxito. |
| `numerator-exclusion` | Registros eliminados del numerador. |
| `measure-population` | Registros cuya observación por registro se agrega. |
| `measure-population-exclusion` | Registros eliminados de `measure-population`. |
| `measure-observation` | El valor calculado por registro en `measure-population`. |

| Método de puntuación | Poblaciones obligatorias |
|---------|----------------------|
| `proportion` | initial-population, denominator, numerator (más exclusiones / excepción opcionales) |
| `ratio` | initial-population, denominator, numerator (independiente del denominador) |
| `continuous-variable` | initial-population, measure-population, measure-observation (más measure-population-exclusion opcional) |
| `cohort` | solo initial-population |

La validación de cálculos propuesta debe comprobar `populations[*].type` frente al valor `scoring` de la métrica. El proyector actual del catálogo no realiza esta validación semántica.

### Lenguaje de criterios

Cada campo `criteria` se empareja con un tipo de medio IANA en `language`. PublicSchema no elige un ganador; fija el tipo de medio para que los consumidores sepan qué motor invocar. **Se proponen tres lenguajes:**

1. **`application/sql`**: ligado al almacén de datos; la opción práctica por defecto para quienes implementan plataformas de prestación. Convención: marcadores `${ps.Enrollment}` para las referencias a clases, que resuelve el ejecutor. Se espera que cubra ~80 % de las métricas de v0.1.
2. **`application/vtl`**: el [Validation and Transformation Language](https://github.com/sdmx-twg/vtl) del SDMX-TWG (v2.1, 11 de abril de 2025). El encaje natural para agregaciones vinculadas a SDMX, correspondencias de listas de códigos, consolidaciones jerárquicas y aritmética de períodos. Para métricas cuyos consumidores destinatarios son agencias SDMX, se recomienda VTL. Realidad de los motores: **un solo motor activo** ([`vpinna80/VTL` de la Banca d'Italia](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). Véase [Riesgos](#riesgos).
3. **`text/cql`**: HL7 Clinical Quality Language ([especificación v1.5.3](https://cql.hl7.org/), adopción por CMS / HEDIS). Se recomienda para métricas que se cruzan con lo clínico o con la calidad de la atención (cobertura efectiva de la cobertura sanitaria universal (UHC), inmunización, salud materna, neonatal e infantil (MNCH)). Un XML **ModelInfo** de CQL propuesto vincularía CQL con las clases de PS, con destino al **[motor de referencia de HL7 `cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language)** (Apache-2.0, v4.8.0).

FHIRPath es demasiado débil para la agregación a nivel de conjunto y no es de primera clase. Quienes quieran expresar un estratificador en FHIRPath pueden hacerlo con `language: text/fhirpath`, pero PS no distribuye un subconjunto normativo ni un banco de pruebas.

### Resolución de librerías

`criteria: @ref:LibraryName.Symbol` se resuelve como `<library_uri>#<Symbol>`, donde `library_uri` aparece en la lista `calculation.libraries[]` de la métrica. Las librerías son dereferenciables por HTTPS; su contenido es el texto del lenguaje declarado por `language` (un archivo CQL, un archivo VTL, un archivo SQL). Los URIs de librería llevan etiqueta de versión; PS recomienda URIs direccionados por contenido (por ejemplo, `.../sp-coverage-cql-1.0`) para que el cálculo de una métrica sea estable bit a bit entre publicaciones.

Refleja la referencia `Measure.library = canonical(Library)` de FHIR Measure.

## URIs de alineación

`aligns_with` en `Metric`, `MetricDimension` y `MetricAttribute` lleva URIs externos que dirigen un único artefacto de PublicSchema hacia la cadena de procesamiento del consumidor adecuado. **Este es el mecanismo de deduplicación**: una definición de Metric de PS, muchos alias de agencias. Es la carga política de toda la especificación.

| Destino | Patrón de URI | Responsable |
|--------|-------------|-------|
| DSD de agencia SDMX | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)` (estructura de URN de [SDMX-IM](https://github.com/sdmx-twg/sdmx-im)) | SDMX TWG, emitido por la agencia |
| Concepto interdominio de SDMX | `urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=SDMX:CROSS_DOMAIN_CONCEPTS(2.0).REF_AREA` (verifique la versión en [registry.sdmx.org](https://registry.sdmx.org)) | SDMX TWG |
| Medida SDMX (SDMX 3.0) | `urn:sdmx:org.sdmx.infomodel.datastructure.Measure=<Agency>:<DSD>(<Version>).<Code>` | SDMX TWG |
| Indicador UN SDG | `https://unstats.un.org/sdgs/indicators/series/<SERIES_CODE>` | UN Statistics |
| DSD global UN SDG | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=IAEG-SDGs:SDG(1.0)` (verifique el ID exacto de la agencia en [unstats.un.org/sdgs/sdmx](https://unstats.un.org/sdgs/sdmx)) | UN Statistics |
| Familia ASPIRE | `https://datacatalog.worldbank.org/aspire/<family-code>` (patrón provisional; la forma de URL de la agencia puede cambiar) | Banco Mundial |
| Metadatos de referencia de ESSPROS | `https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm` | Eurostat |
| DSD de OECD SOCX | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=OECD.ELS.SPD:DSD_SOCX_AGG(1.0)` (activo, verificado en `sdmx.oecd.org`) | OECD |
| Indicador DHIS2 | `dhis2://indicator/<uid>` (local del programa) | Instancia local de DHIS2 |
| Resultado / indicador IATI | `https://iatistandard.org/en/iati-standard/203/codelists/IndicatorMeasure/` | IATI |
| Hashtag HXL | `https://hxlstandard.org/standard/hashtags/#indicator+value+num` | HXL |
| Medida RDF Data Cube | `<publicschema metric URI>` representado como `qb:MeasureProperty` | propio |

La alineación es semántica y unidireccional; PublicSchema no se sincroniza con estos registros. Un cambio en el DSD de ILO requiere una nueva versión del esquema de PS que actualice el URI de alineación.

**Referencia inversa desde un DSD de agencia hacia una Metric de PS.** SDMX no tiene una referencia nativa entre sistemas. Use el mecanismo `Annotation` de SDMX-IM en el DSD de la agencia: `AnnotationType = ps:alignedMetric`, `AnnotationURL = <PS Metric URI>`. Esto es normativamente correcto y hace la ida y vuelta sin pérdidas. En SDMX 3.0, «extends» significa herencia interna al DSD, no alineación externa, por lo que el mecanismo Annotation es la única vía válida.

## Destinos de emisión

LinkML es la fuente de verdad. Esta tabla enumera las salidas específicas de métricas propuestas y las posibles bases de implementación. La disponibilidad de un generador LinkML o del `rdf_export.py` existente no significa que el publicador de métricas correspondiente se haya integrado o verificado en este repositorio.

| Salida | Por qué | Estado | Prioridad |
|--------|-----|--------|----------|
| **JSON Schema** (por Metric, MetricObservation, MetricReport) | Formato predeterminado para consumidores; remitentes tabulares; integración con OpenAPI. | Publicación específica de métricas pendiente; `gen-jsonschema` de LinkML es una base posible | P0 |
| **Contexto JSON-LD** | Patrón existente de PS. | Publicación específica de métricas pendiente; `gen-jsonld-context` de LinkML es una base posible | P0 |
| **Formas SHACL** | Validación; patrón existente de PS. | Publicación específica de métricas pendiente; `gen-shacl` de LinkML es una base posible | P0 |
| **CSVW** (CSV on the Web, metadatos JSON-LD) | Publicación tabular con la menor fricción; umbral mínimo para el envío por analistas. | **Por construir** ([linkml/linkml#86](https://github.com/linkml/linkml/issues/86) abierto desde noviembre de 2020, sin PR) | P0 |
| **SDMX-CSV v2.1** | Umbral mínimo para los analistas de datos de WB / ILO / OECD / Eurostat. Especificación: [sdmx-twg/sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) (v2.1.0, 27 de agosto de 2025). | **Por construir** (no hay `gen-sdmx` en LinkML; no hay conversor de terceros) | P0 |
| **SDMX-ML v3.1 (mensajes estructurales)** | Envíos de DSD / Codelist / ConceptScheme a registros de agencias. Especificación: [sdmx-twg/sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) (v3.1.0, 16 de mayo de 2025). | **Por construir** | P0 |
| **SDMX-ML v3.1 (mensajes de datos)** | Intercambio completo de estructura y datos. | **Por construir** | P1 |
| **SDMX-JSON v2.1** | Formato web de difusión; las API de agencias (OECD, ECB, ILO) responden en JSON por defecto. Especificación: [sdmx-twg/sdmx-json](https://github.com/sdmx-twg/sdmx-json) (v2.1.0, 16 de mayo de 2025). | **Por construir** | P1 |
| **RDF Data Cube TTL** | Consumidores nativos de grafos; cadenas LOD; consultas SPARQL. | **Por construir** (~200 LOC; PS lo gestiona directamente) | P2 |
| **Excel** (por definición de Metric) | Libro de definición, en línea con las descargas Excel por concepto que PS ya ofrece. | Libros de definición de métricas pendientes; la cadena existente exporta conceptos del vocabulario | P2 |
| **JSON de indicadores DHIS2** | Importación directa en instancias DHIS2. Con pérdida: depende de la resolución local de UID. | **Por construir**; no existe una correspondencia pública | P3 |
| **Sugerencia de hashtags HXL** | Encabezado de hashtags en línea para exportaciones CSV. Mejor esfuerzo. | **Por construir** | P3 |
| **Fragmento XML de indicador IATI** | Para la integración de resultados reportados a donantes. | **Por construir** | P3 |

SDMX 3.0 convierte `Measure` en una lista de componentes de primer nivel (eliminó la `MeasureDimension` de SDMX 2.1). PS apunta solo a 3.0; la ida y vuelta con consumidores heredados de 2.1 queda fuera del alcance. Composición de la URN del DSD: `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)`. SDMX 3.0 permite semver extendido según [sdmx-twg/semver](https://github.com/sdmx-twg/semver). PublicSchema no acuña URNs de agencias; una agencia que reutiliza una métrica de PS acuña su propia URN y apunta de vuelta mediante una `Annotation` (véase [URIs de alineación](#uris-de-alineación)).

No existe un espacio de nombres RDF `sdmx:` canónico publicado por SDMX-TWG. El esquema solo lista `qb:` en `exact_mappings`, con referencias a URNs de SDMX en la prosa. El emisor TTL de Data Cube propuesto tendría que hacer cumplir: IC-1, IC-2, IC-3, IC-4, IC-5, IC-6, IC-11, IC-13, IC-14. IC-7 a IC-10 (slices) no aplican en v0.1; v0.2 podría añadir la generación de slices si algún consumidor lo pide. IC-12 (sin tuplas de dimensión duplicadas) también requeriría validación en el momento de la emisión; el proyector del catálogo no implementa esta validación.

## Corpus semilla

La propuesta original apuntaba a **~240 indicadores derivables de WB / ILO / UN / UNICEF**, cada uno con un `MetricCalculation` ejecutable y los URIs `aligns_with` pertinentes. Las estimaciones siguientes son una lista de investigación pendiente, no el corpus implementado actual; véase [Implementación actual](#implementación-actual).

| Fuente | Indicadores derivables (recuento aproximado) | Entrada legible por máquina |
|--------|-----------------------------------|------------------------|
| **UN SDG** (metadatos publicados por los custodios) | ~30 (1.1.1, 1.2.1, el conjunto 1.3.1, 3.8.x UHC, 5.2&ndash;5.6, 10.1.1, 16.9.1) | [metadata.un.org/sdg/ontology](https://metadata.un.org/sdg/ontology) + PDF por indicador |
| **ILO** (custodio de 14 indicadores SDG; serie SPSI) | ~50 (cobertura, adecuación, cobertura efectiva por tipo de programa) | [ILOSTAT SDMX](https://ilostat.ilo.org/resources/sdmx-tools/) + CSV masivo |
| **WB ASPIRE** | ~100 (cobertura, adecuación, incidencia de las prestaciones, reducción de la pobreza, por quintil) | [WB Indicators API](https://api.worldbank.org/v2/indicator?format=json) + metodología ASPIRE Quality Check |
| **WB Poverty &amp; Inequality Platform** | ~20 (tasa de pobreza extrema / nacional, brecha, severidad, Gini, crecimiento del 40 % más pobre) | [PIP API](https://pip.worldbank.org/) |
| **Derivados de UNICEF MICS** | ~40 (bienestar infantil, WASH, educación) | Informes MICS + diccionario de indicadores |

**Estimación original del corpus: ~240 indicadores.** v0.2 se extiende a indicadores derivables de OECD IDD / SOCX y de Eurostat EU-SILC. v0.3 se amplía a indicadores humanitarios (con forma HXL) y de gestión de programas (fugas, tiempo de tramitación) que carecen de un único custodio interinstitucional.

Vía práctica de ingesta: extraer el catálogo de indicadores legible por máquina de cada fuente, generar automáticamente un esqueleto de `Metric` por indicador (título, descripción, URL de la fuente, tema) y luego redactar a mano el `MetricCalculation` sobre las clases de PS para el subconjunto derivable. Los indicadores solo de origen externo (la mayor parte de los indicadores macro de WDI) se descartan de este ejercicio; siguen siendo citas válidas, pero no Metrics de PS.

## Proceso de revisión por los custodios

La propuesta mantendría una métrica en `bibo:draft` hasta la revisión por el custodio, con una transición de estado posterior para registrar esa revisión. Las semillas actuales están todas en borrador; su inclusión en el catálogo no implica respaldo de ninguna agencia. Encaminamiento propuesto hacia los custodios por dominio:

- Cobertura / adecuación de la protección social &rarr; ILO (custodio de SDG 1.3.1).
- Pobreza / desigualdad &rarr; Banco Mundial (PIP / ASPIRE; SDG 1.1.1 / 1.2.1).
- Bienestar infantil / nutrición &rarr; UNICEF (MICS).
- Salud / UHC &rarr; WHO (SDG 3.8.x).
- Registro civil / identidad jurídica &rarr; UNICEF / UNHCR / DESA (SDG 16.9.1).
- Igualdad de género &rarr; UN Women / UNSD (SDG 5.x).

El visto bueno del custodio es un contrato social, no una barrera técnica; PS no controla el espacio de nombres. La transición `bibo:draft` &rarr; `bibo:published` señala, métrica por métrica, que el custodio la ha revisado. Los URIs de Metric de PS firmados por el custodio pasan a ser citables en los propios metadatos del custodio.

## Ejemplo desarrollado: cobertura SDG 1.3.1

Indicador: *«Proporción de la población cubierta por niveles mínimos / sistemas de protección social»*, custodio ILO, SDG 1.3.1a (cobertura efectiva).

Definición en PublicSchema (conceptual):

```yaml
metric:
  id: sp_coverage_at_least_one_program
  title: Coverage by at least one social-protection program
  description: |
    Share of the resident population effectively covered by at least one
    social-protection cash benefit during the reference period, regardless
    of program type.
  value_type: proportion
  unit: PT                          # SDMX UNIT_MEASURE "Percentage", value in 0..100
  decimals: 1
  topic: coverage
  concept_uri: publicschema:concept/effective_coverage
  family: publicschema:metric_family/sp_coverage    # tag; drives DSD generation
  dimensions:
    - ps:dim/ref_area
    - ps:dim/time_period
    - ps:dim/freq
    - ps:dim/sex
    - ps:dim/age_band
    - ps:dim/urban_rural
    - ps:dim/wealth_quintile
  attributes:
    - ps:attr/unit_measure
    - ps:attr/obs_status
    - ps:attr/cell_count
    - ps:attr/confidentiality_status
  calculation:
    scoring: proportion
    subject_class: publicschema:Person
    populations:
      - type: initial-population
        language: text/cql
        criteria: "@ref:sp_coverage_lib.ResidentPopulation"
      - type: denominator
        language: text/cql
        criteria: "@ref:sp_coverage_lib.ResidentPopulation"
      - type: numerator
        language: text/cql
        criteria: "@ref:sp_coverage_lib.CoveredByAtLeastOneProgram"
    stratifiers:
      - code: by-sex
        language: application/sql
        criteria: "SELECT sex FROM ${ps.Person}"
      - code: by-age-band
        language: application/sql
        criteria: "SELECT age_band FROM ${ps.Person}"
    rate_aggregation: none
    improvement_notation: increase
    libraries:
      - https://publicschema.org/metrics/library/sp-coverage-cql-1.0
  aligns_with:
    - https://unstats.un.org/sdgs/indicators/series/SI_COV_BENFTS
    - urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=IAEG-SDGs:SDG(1.0)
    - https://datacatalog.worldbank.org/aspire/coverage   # placeholder; verify against live ASPIRE registry
  core: true
  status: bibo:draft
  version: 1.0.0
```

Ejemplo de observación:

```yaml
observation:
  metric: publicschema:metric/sp_coverage_at_least_one_program
  period:
    period_type: calendar_year
    start_date: 2024-01-01
    end_date: 2024-12-31
    granularity: year
    frequency: A
  dimension_values:
    - { dimension_uri: ps:dim/ref_area, code: "TH" }       # Thailand
    - { dimension_uri: ps:dim/time_period, code: "2024" }
    - { dimension_uri: ps:dim/freq, code: "A" }
    - { dimension_uri: ps:dim/sex, code: "_T" }            # Total
    - { dimension_uri: ps:dim/age_band, code: "_T" }
    - { dimension_uri: ps:dim/urban_rural, code: "_T" }
    - { dimension_uri: ps:dim/wealth_quintile, code: "_T" }
  value: 68.3
  attribute_values:
    ps:attr/unit_measure: "PT"
    ps:attr/obs_status: "A"
    ps:attr/cell_count: 4982104
    ps:attr/confidentiality_status: "F"
  calculation_uri: publicschema:metric/sp_coverage_at_least_one_program#calculation
  # execution_uri optional
```

El resultado buscado es reutilizar una misma observación en formatos de agencias, de grafos y de paneles. Este ejemplo no demuestra esas integraciones: siguen siendo necesarios los emisores, la ejecución de cálculos, las vinculaciones con los DSD de destino y la validación por los consumidores. Los URIs de alineación por sí solos no establecen la aceptación por ILOSTAT o ASPIRE.

Para quienes conocen menos el vocabulario de FHIR Measure: `initial-population` es «el universo de registros considerados» (todas las personas del registro de población residente); `denominator` es «la población *de* la que medimos la cobertura» (igual que initial-population para 1.3.1a); `numerator` es «quiénes decimos que *están* cubiertas» (personas con al menos una inscripción activa en protección social durante 2024); `denominator-exclusion` elimina registros contados por error (personas no residentes); `numerator-exclusion` elimina registros contados como cubiertos por error (inscripciones fraudulentas o duplicadas).

## Esquema LinkML

La fuente normativa es [`schema/metrics.yaml`](https://github.com/PublicSchema/publicschema.org/blob/main/schema/metrics.yaml), conectada al esquema compuesto mediante la entrada `metrics` de `schema/publicschema.yaml`. Once clases (`Metric`, `MetricDimension`, `MetricAttribute`, `MetricCalculation`, `PopulationCriterion`, `Stratifier`, `MetricObservation`, `MetricReport`, `Period`, más los auxiliares de pares estructurados `DimensionValue` y `AttributeValue`), los slots a los que hacen referencia y los enums (`ValueType`, `ScoringMethod`, `ImprovementNotation`, `RateAggregation`, `MetricTopic`, `AttachmentLevel`, `PopulationType`, `PeriodType`, `Granularity`, `Frequency`). Los códigos `ObsStatus` no se vuelven a publicar; se resuelven mediante la URN de SDMX `urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_OBS_STATUS(2.3)`.

Conviene señalar a quien lee dos ajustes relacionados con palabras clave de LinkML:

- `MetricDimension.range` y `MetricAttribute.range` (los nombres usados en la prosa de la especificación) se escriben `value_range` en el archivo LinkML para no ocultar la palabra clave `range`. El mapeo RDF específico de métricas propuesto usaría el `range` previsto; la proyección del catálogo no realiza ese mapeo.
- `MetricObservation.value` se escribe `metric_value` para evitar colisiones con slots `value` definidos en otras partes del compuesto. El JSON Schema ilustrativo siguiente usa `value`; no asuma que el exportador general de esquemas actual realiza este cambio de nombre.

`MetricObservation` es `is_a: Event`. `MetricReport.publisher` tiene como rango `Agent` (véase [Principio 5](/docs/design-principles/#5-supertipos-abstractos)). `dimension_values` y `attribute_values` se modelan como listas ordenadas de pares estructurados (`DimensionValue` y `AttributeValue`) en lugar de mapas, para que la ida y vuelta del DSD SDMX sea estable.

## JSON Schema (en línea)

La propuesta prevé `metric.schema.json`, `metric-observation.schema.json` y `metric-report.schema.json` en URIs de publicación estables. Estos artefactos específicos de métricas redactados a mano no se proporcionan actualmente. El esquema siguiente es indicativo y no es un contrato publicado; en particular, su mapa de atributos difiere de la lista de pares estructurados del modelo LinkML actual.

Esquema indicativo de `MetricObservation` (Draft 2020-12):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://publicschema.org/schemas/v1/metric-observation.schema.json",
  "title": "MetricObservation",
  "type": "object",
  "required": ["metric", "period", "dimension_values", "value", "calculation_uri"],
  "properties": {
    "metric": { "type": "string", "format": "uri" },
    "period": { "$ref": "period.schema.json" },
    "dimension_values": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["dimension_uri", "code"],
        "properties": {
          "dimension_uri": { "type": "string", "format": "uri" },
          "code": { "type": "string" }
        }
      }
    },
    "value": { "type": "number" },
    "attribute_values": {
      "type": "object",
      "additionalProperties": { "type": ["string", "number", "boolean"] }
    },
    "calculation_uri": { "type": "string", "format": "uri" },
    "execution_uri": { "type": "string", "format": "uri" }
  }
}
```

## Preguntas abiertas

Siguen abiertas tras la pasada de diseño de v0.1.

1. **Jerarquías y esquemas de categorías para las dimensiones.** Las dimensiones SDMX llevan jerarquías (M49 para REF_AREA, jerarquías de tramos de edad para AGE). El diseño inicial prevé listas de códigos planas; v0.2 añade jerarquías cuando un consumidor de la emisión lo requiera.
2. **Content Constraints.** Las agencias adjuntan artefactos `ContentConstraint` que indican «para este dataflow, REF_AREA está restringido a estos códigos». El diseño inicial propone DSD sin restricciones; v0.2 podría añadir una forma `MetricConstraint` si la emisión para agencias lo requiere.
3. **Puntuación por cohorte.** La retención de una cohorte (cobertura a 12 meses dada la inscripción en el mes 0) necesita aritmética de desplazamiento de Period y linaje a lo largo del tiempo. Excluida de v0.1; se revisará en v0.2.
4. **Privacidad / supresión de celdas pequeñas.** Es el modo de fallo más común en la publicación de indicadores públicos. `cell_count` y `confidentiality_status` forman parte de la librería predeterminada de `MetricAttribute`; las agencias fijan los umbrales en el momento de la emisión. La *lógica* de supresión es propia de cada agencia, no normativa.
5. **Métricas de modelos de IA / ML.** Fuera del alcance de esta especificación; se revisará cuando la taxonomía del AI Hub se estabilice.
6. **Métricas con varias medidas.** SDMX 3.0 permite varias Measures por DSD; el diseño inicial de PS apunta solo a la publicación de una única medida. Añadir la clase `MetricMeasure` en v0.2 si surge un caso de uso real.

## Riesgos

Catálogo franco de las dependencias y carencias de la especificación. Ninguna es fatal; cada una puede construirse.

1. **Monocultivo de herramientas VTL.** Se recomienda VTL para métricas vinculadas a SDMX, pero solo **un** motor de código abierto sigue activo ([`vpinna80/VTL` de la Banca d'Italia](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). El motor VTL de Eurostat está abandonado desde 2020. Mitigación: VTL **nunca es el único lenguaje para el cálculo primario de una métrica**. Quienes redactan métricas deben incluir al menos uno de {SQL, CQL} junto con cualquier criterio VTL, y el emisor SDMX debe aceptar equivalentes traducidos a SQL.
2. **Carga de generadores totalmente nuevos.** LinkML upstream tiene `gen-jsonschema`, `gen-shacl` y `gen-jsonld-context`. **No** tiene `gen-csvw`, `gen-sdmx` ni `gen-datacube`. La propuesta estimaba ~1500 LOC de generadores en `build/` para la fase fundacional (CSVW, SDMX-CSV, mensajes estructurales SDMX-ML, RDF Data Cube TTL). La tabla de destinos de emisión marca cada uno como `existing` o `to-build`. Incorporar `gen-csvw` a LinkML upstream está en la hoja de ruta de v0.2.
3. **El ModelInfo de CQL no FHIR es poco común en producción.** CQL como *lenguaje* admite XML ModelInfo personalizado; los *motores* CQL se distribuyen mayormente con vinculaciones solo para FHIR. El motor de referencia de HL7 [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language) (Apache-2.0, v4.8.0) acepta ModelInfo personalizado. La propuesta prevé `PublicSchema-ModelInfo.xml` conforme al esquema ModelInfo del motor de referencia de HL7 en v0.2; prevea una semana de trabajo con una persona especialista en CQL.
4. **El emisor DHIS2 parte de cero.** No existe ninguna correspondencia pública de definiciones de indicadores externos hacia DHIS2. El esquema de destino de DHIS2 es estable; la correspondencia es trabajo de PS. Aplazado a v0.3.
5. **El kit de herramientas HXL tiene un bus factor de 1.** [`HXLStandard/libhxl-python`](https://github.com/HXLStandard/libhxl-python) depende de una sola persona que lo mantiene de forma esporádica. La sugerencia de hashtags HXL sigue siendo un emisor P3 de mejor esfuerzo en v0.3.

## Hoja de ruta de implementación

Esta es la secuencia propuesta original. No es una lista de verificación de implementación ni una afirmación de que estos entregables se hayan publicado; el alcance admitido actualmente se indica al principio de esta página.

- **v0.1 (fase fundacional, objetivo: tercer trimestre de 2026).** [`schema/metrics.yaml`](https://github.com/PublicSchema/publicschema.org/blob/main/schema/metrics.yaml) con las siete clases del catálogo más los auxiliares estructurales. Entre 10 y 15 Metrics semilla que cubren SDG 1.3, cobertura / adecuación de ASPIRE, gasto de ESSPROS y áreas de política de SOCX. Archivos de alineación externa para SDMX, SDG, ASPIRE, ESSPROS y SOCX. Generadores P0 según la tabla de destinos de emisión. JSON Schemas redactados a mano en `publicschema.org/schemas/v1/`. Una librería CQL y una transformación VTL como ejemplos desarrollados para SDG 1.3.1a. ADR-020 recoge estas decisiones.
- **v0.2 (interoperabilidad, objetivo: primer trimestre de 2027).** Corpus semilla completo de ~240 indicadores, extendido a OECD IDD / Eurostat EU-SILC. Generadores P1 / P2. Puntuación por cohorte. Jerarquías de dimensiones cuando los consumidores las pidan. `PublicSchema-ModelInfo.xml` probado con `cqframework/clinical_quality_language`. Incorporar `gen-csvw` a LinkML upstream (cierra [linkml/linkml#86](https://github.com/linkml/linkml/issues/86)).
- **v0.3 (catálogo más amplio, objetivo: tercer trimestre de 2027).** Generadores P3 (DHIS2, HXL, IATI). Entre 30 y 50 Metrics adicionales de gestión de programas, inclusión y ámbito humanitario. Forma `MetricConstraint` si la emisión para agencias lo requiere.

## Referencias

- W3C. [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). Recomendación, 2014. (SDMX-TWG no mantiene ninguna vinculación SDMX-RDF en 2026; este es el mapeo RDF de facto, mantenido fuera del TWG.)
- SDMX TWG. [Portal de estándares SDMX 3.0](https://sdmx.org/standards-2/) y los repositorios canónicos del SDMX-TWG:
  - [sdmx-im](https://github.com/sdmx-twg/sdmx-im): modelo de información y estructura de URN.
  - [sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) v3.1.0 (16 de mayo de 2025): formato XML; XSD en [xml.sdmx.org](https://xml.sdmx.org).
  - [sdmx-json](https://github.com/sdmx-twg/sdmx-json) v2.1.0 (16 de mayo de 2025); documentación en [json.sdmx.org](https://json.sdmx.org).
  - [sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) v2.1.0 (27 de agosto de 2025).
  - [sdmx-rest](https://github.com/sdmx-twg/sdmx-rest) v2.2.2 (21 de agosto de 2025).
  - [vtl](https://github.com/sdmx-twg/vtl) v2.1 (11 de abril de 2025); documentación en [sdmx-twg.github.io/vtl](https://sdmx-twg.github.io/vtl/).
  - [sdmx-registry](https://github.com/sdmx-twg/sdmx-registry), [sdmx-tck](https://github.com/sdmx-twg/sdmx-tck), [urn-resolver](https://github.com/sdmx-twg/urn-resolver) ([urn.sdmx.io](https://urn.sdmx.io)), [semver](https://github.com/sdmx-twg/semver).
- SDMX. [Listas de códigos interdominio](https://sdmx.org/sdmx_cdcl/); [notas de la versión 2.3 de CL_OBS_STATUS](https://sdmx.org/news/version-2-3-of-cl_obs_status-released/) (6 de enero de 2026).
- BIS. [FMR (Fusion Metadata Registry)](https://www.sdmx.io/software/fmr/): implementación actual de registro SDMX; [bis-med-it/fmr-public](https://github.com/bis-med-it/fmr-public) v12.0.0 (8 de mayo de 2026).
- HL7. [Recurso Measure de FHIR R5](https://hl7.org/fhir/R5/measure.html); [CQF-Measures Implementation Guide v2.0.0](https://hl7.org/fhir/us/cqfmeasures/STU2/) (23 de julio de 2020, orientada a R4 / R4B; la 5.x en build.fhir.org es una compilación continua no publicada).
- HL7. [Especificación CQL v1.5.3](https://cql.hl7.org/).
- [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language): motor CQL de referencia de HL7, Apache-2.0, v4.8.0 (8 de mayo de 2026). Principal destino de ModelInfo no FHIR.
- [`vpinna80/VTL`](https://github.com/vpinna80/VTL): motor VTL de la Banca d'Italia, EUPL-1.2, v1.3.0 (24 de septiembre de 2025). Implementación de referencia de facto de VTL.
- ILO. [Herramientas SDMX de ILOSTAT](https://ilostat.ilo.org/resources/sdmx-tools/) y [World Social Protection Database](https://www.social-protection.org/gimi/WSPDB.action); [metadatos de SDG 1.3.1 (PDF)](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf).
- Banco Mundial. [ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire); [Poverty &amp; Inequality Platform](https://pip.worldbank.org/); [WB Indicators API](https://api.worldbank.org/v2/indicator?format=json).
- Eurostat. [Metodología ESSPROS](https://ec.europa.eu/eurostat/web/social-protection/methodology); [metadatos de referencia ESMS](https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm).
- OECD. [SOCX Social Expenditure Database](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html); [DSD de SOCX activo](https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.SPD/DSD_SOCX_AGG@DF_SOCX_AGG/1.0).
- UN Stats. [Metadatos de los indicadores SDG](https://unstats.un.org/sdgs/metadata/); [API de metadatos SDG (UN LDS)](https://metadata.un.org/sdg/ontology).
- UNICEF. [MICS](https://mics.unicef.org/) y diccionarios de indicadores.
- DHIS2. [Documentación de indicadores](https://docs.dhis2.org/en/implement/database-design/aggregate-system-design/indicators.html).
- OCHA. [Hashtags y atributos HXL](https://centre.humdata.org/learning-path/hxl/hashtags-attributes/).
- IATI. [Estándar de actividades: resultado / indicador](https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/).
- LinkML. [linkml/linkml#86 generador CSVW](https://github.com/linkml/linkml/issues/86) (abierto, sin PR); [linkml/linkml#901 exploración de DataCube](https://github.com/linkml/linkml/issues/901) (cerrado sin resolución).
- VLDB. [SDG-KG: Indicator Workflows as a Knowledge Graph](https://dl.acm.org/doi/10.14778/3750601.3750673), 2025.
