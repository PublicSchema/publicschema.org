# Metrics Specification

**Status:** Draft &middot; **Author:** PublicSchema working group &middot; **Last updated:** 2026-05-14

This spec proposes a new domain inside PublicSchema for **declarative, executable definitions of derivable indicators** &mdash; aggregate metrics computed from PublicSchema record-level concepts (Person, Household, Enrollment, PaymentEvent, ScoringEvent, etc.). It complements the existing record-level layer; it does not replace it.

**Derivable-only.** Every PublicSchema Metric ships with a calculation that runs against PS-mapped microdata. If you cannot write the calculation, it is not a PS Metric &mdash; it is a citation. Sourced indicators (compiled from upstream NSI / agency tables with no microdata derivation) remain valuable but are out of scope here; they belong with the existing provenance layer.

The shape is borrowed from FHIR R5 Measure (computation) and SDMX 3.0 (structure). PublicSchema is the LinkML source of truth; downstream formats are generators.

## Why PublicSchema needs this

PublicSchema today covers people, households, programs, payments, profiles, scoring runs &mdash; the record-level shape of social-protection and adjacent delivery systems. Funders, statisticians, M&amp;E teams and policy researchers do not consume that data record by record; they consume aggregate **indicators**: coverage rate, adequacy, payment regularity, leakage, error rate, average benefit per beneficiary, share of women among recipients.

Three concrete problems with the status quo:

1. **Every program reinvents the same indicators**, with subtly different denominators. "Social-protection coverage" computed against an active-enrollment denominator is not comparable with one computed against an eligible-population denominator. Without shared executable definitions, cross-country comparison is fiction.
2. **The same indicator gets repackaged 4&ndash;6 times** to feed ILO ([ILOSTAT](https://ilostat.ilo.org/)), the World Bank ([ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire)), Eurostat ([ESSPROS](https://ec.europa.eu/eurostat/web/social-protection)), OECD ([SOCX](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html)), the UN ([SDG 1.3.1](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf)), and a country's own statistical office. Each consumer wants its own Data Structure Definition (DSD).
3. **"How was this computed?" is rarely answerable.** Methodology lives in a PDF, the formula in a spreadsheet, the lookups in a code list nobody versions.

The metrics primitive addresses all three: one **canonical executable definition** per indicator, **alignment URIs** that route a single observation into many consumer DSDs, and a **declarative computation block** that is auditable and re-runnable.

## Scope

**In scope:**
- Declarative definition of derivable aggregate indicators / metrics.
- Declarative computation against PublicSchema record-level concepts.
- Dimensional metadata (what disaggregations a metric supports).
- Reference metadata (definition, methodology, source, owner, license, version).
- Observations (the actual reported values, with dimension values and observation-level attributes).
- Cross-walks to external indicator frameworks (SDMX agency DSDs, UN SDG, ASPIRE, ESSPROS, SOCX, DHIS2, IATI, HXL).

**Out of scope:**
- **Sourced indicators.** If a "metric" is just a citation to an upstream NSI / agency-compiled value with no microdata-level derivation, it does not belong here; it stays with the provenance layer that PS record-level concepts already carry.
- Replacing per-record scoring. `ScoringEvent` continues to record one rule application against one subject; metrics aggregate across many subjects.
- Replacing statistical agency tooling. PublicSchema describes the metric and emits SDMX; it does not run SDMX Web Services or agency registries.
- Hosting raw record-level data. A metric definition references record-level concepts by URI; observations carry only the aggregate value.
- Defining a new computation runtime. The criteria language is pluggable (IANA-media-typed); reference implementations target existing SQL, VTL, CQL engines.
- AI / ML model evaluation metrics. Adjacent and worth a separate spec; not folded in here.

## Conformance tiers

A PublicSchema-Metrics conformant tool declares one of three tiers:

| Tier | Name | Capability |
|------|------|------------|
| **1** | Catalogue consumer | Reads PS Metric definitions (LinkML / JSON Schema), resolves alignment URIs. No emission. |
| **2** | Observation publisher | Emits valid `MetricObservation` JSON-LD and CSVW against PS schemas. The minimum bar for "this platform speaks PS Metrics". |
| **3** | SDMX-bound publisher | Tier 2 plus SDMX-CSV v2.1 emission against a referenced DSD. The bar for agency-grade publication to ILO / WB / OECD / Eurostat. |

Tier 1 is where most read-only research tools live. Tier 2 is where delivery platforms (OpenSPP, OpenIMIS, DHIS2 program databases) live. Tier 3 is where national statistical institutes and custodian agencies live.

## Conceptual model

Seven LinkML classes. The shape is the SDMX 3.0 information model (dimensions, measures, attributes, code lists, observations) extended with FHIR Measure's computation semantics. The [observation / scoring separation](design-principles.md#6-observation-and-scoring-separation) (Principle 6) extends from per-record scoring to aggregate metrics: a `MetricObservation` is to a `Metric` what a `ScoringEvent` is to a `ScoringRule`. Metrics may carry [`core: true`](design-principles.md#9-core-and-extended-property-tiers) (Principle 9) to mark the must-have subset.

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

A named indicator with a stable URI, a prose definition, a value type, a unit, declared dimensions, declared observation-level attributes, declared external alignments, and a (single, primary) computation.

Key slots:
- `id` &mdash; opaque identifier, slugified URI fragment.
- `class_uri` &mdash; `publicschema:Metric`. Emits one `qb:MeasureProperty` and one `skos:Concept` on RDF serialisation.
- `title`, `description` &mdash; multilingual labels carried in `annotations.label_es` / `label_fr` / `description_es` / `description_fr` (PS house style).
- `value_type` &mdash; controlled vocabulary: `count`, `proportion`, `ratio`, `currency_amount`, `index`, `duration`, `nominal`, `ordinal`, `qualitative`.
- `unit` &mdash; UCUM, ISO 4217 (currency), or `unitless`.
- `multiplier` &mdash; SDMX-style `0` / `3` / `6` (units / thousands / millions). Default `0`.
- `decimals` &mdash; reporting precision.
- `dimensions` &mdash; ordered list of `MetricDimension` references.
- `attributes` &mdash; list of `MetricAttribute` references.
- `calculation` &mdash; one `MetricCalculation` (see [Computation model](#computation-model)).
- `topic` &mdash; coverage / adequacy / expenditure / leakage / targeting / inclusion_error / exclusion_error / regularity / processing_time / satisfaction.
- `concept_uri` &mdash; `skos:Concept` URI (so multiple Metrics can share a concept).
- `family` &mdash; optional URI tag grouping metrics that share dimensions (drives DSD generation when present; no separate class). A first-class `MetricFamily` class is deferred until there are three real families.
- `aligns_with` &mdash; list of external URIs.
- `core` &mdash; boolean flag for the must-have subset.
- `status` &mdash; `bibo:draft` / `bibo:published` / `bibo:deprecated`.
- `version`, `replaces`, `replaced_by` &mdash; versioning slots, new in this domain; lift into `schema/common.yaml` if other record-bearing concepts adopt them.

`Metric` is a catalogue definition, not an event in time, so it does not subclass `Event`.

### `MetricDimension`

A typed dimension that disaggregates a metric. Slots:
- `id`, `title`, `description` (+ multilingual).
- `class_uri` &mdash; `publicschema:MetricDimension`; emits `qb:DimensionProperty`.
- `concept_uri` &mdash; SDMX cross-domain concept where one exists (`REF_AREA`, `SEX`, `AGE`, `UNIT_MEASURE`, `TIME_PERIOD`, `FREQ`). Referenced by URN in prose; no fictional RDF `sdmx:` IRI.
- `range` &mdash; LinkML enum (PublicSchema vocabulary) or external code list URI.
- `code_list_uri` &mdash; canonical code list URN (SDMX agency codelist when one exists). PS vocabularies are canonical; the SDMX emitter wraps them.
- `is_required` &mdash; boolean.
- `ordering` &mdash; integer (DSD position).

PublicSchema ships a small initial library of MetricDimensions: country (ISO 3166-1 alpha-2 bound to `CL_AREA`), region / admin1 (OCHA COD-AB), sex (PS sex vocab bound to `CL_SEX(2.1)`), age (single year + standard bands, bound to `CL_AGE`), urban / rural, wealth quintile, disability status (WG-SS), program type (PS program taxonomy), benefit modality, reference period, frequency (`FREQ`).

### `MetricAttribute`

A non-key annotation on an observation, series, or dataset. PublicSchema ships a small default library mirroring [SDMX Cross-Domain Concepts](https://sdmx.org/sdmx_cdcl/) so the SDMX emitter has zero translation work. Default identifiers and **correct attachment levels** (SDMX 3.0 IM):

- **Observation-level:** `OBS_STATUS` (codelist `CL_OBS_STATUS(2.3)`), `CONF_STATUS` (`CL_CONF_STATUS(1.4)`), `COMMENT_OBS`, plus PS extensions `cell_count`, `confidentiality_status`, `data_quality_flag`.
- **Series-level / dimension-group:** `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `REF_PERIOD`, `BASE_PER`, `EMBARGO_DATE`, `COMMENT_TS`.
- **Dataset-level:** `COMPILING_ORG`, `SOURCE_AGENCY`, `TITLE`, `TITLE_COMPL`, `CURRENCY`, `CURRENCY_DENOM`, `PRICE_BASE`. (`DATA_PROVIDER` lives in the SDMX Dataset header, not as an attribute.)
- **Break-in-series workflow:** `OBS_PRE_BREAK`, `BREAK_REASON` (`CL_BREAK_REASON`).

Notes:
- `OBS_VALUE` is the SDMX 3.0 measure component (not an attribute); it is carried on `MetricObservation.value`.
- `TIME_FORMAT` is deprecated in SDMX 3.0 (ISO 8601 assumed) and not in the default library.
- Bound to `qb:AttributeProperty` on RDF emission. The `attachment_level` slot (`dataset` / `series` / `observation`) drives where the SDMX emitter places each attribute.

For v0.1, only six attributes ship as PS-authored defaults: `OBS_STATUS`, `UNIT_MEASURE`, `UNIT_MULT`, `DECIMALS`, `cell_count`, `confidentiality_status`. The remaining ~20 are catalogued but not generated until a real use case lands them.

### `MetricCalculation`

The declarative computation. See [Computation model](#computation-model). One per Metric; richer variants carried by a library reference. The per-record analog is [`ScoringRule`](https://publicschema.org/concepts/ScoringRule/) (`schema/misc.yaml`); `MetricCalculation` aggregates across subjects.

### `MetricObservation`

One reported value. Slots:
- `metric` &mdash; URI of the `Metric`.
- `period` &mdash; one `Period`.
- `dimension_values` &mdash; ordered list of `{dimension_uri, code}` pairs (not a map; ordering matters for DSD round-trip).
- `value` &mdash; number, with type matching the metric's `value_type`. The **scale is fixed by `Metric.unit` + `Metric.multiplier`**: for `value_type: proportion` with `unit: unitless`, value is in 0..1; for percentages, set `unit: PT` (SDMX `UNIT_MEASURE` code) and value is in 0..100. When `UNIT_MEASURE` also appears in `attribute_values`, it must equal `Metric.unit`; the observation cannot override scale.
- `attribute_values` &mdash; map from `MetricAttribute` URI to value.
- `calculation_uri` &mdash; URI of the `MetricCalculation` definition this observation realises.
- `execution_uri` &mdash; optional URI of an execution record (provenance: software agent, run timestamp, parameter set). Light PROV-O alignment recommended; details deferred.

Bound to `qb:Observation` and SDMX 3.0 Observation. `MetricObservation` is `is_a: Event` ([Principle 5](design-principles.md#5-abstract-supertypes)); it inherits `identifiers` from `Event`.

### `MetricReport`

A bundle of observations with publisher metadata: `publisher` (ranges over [`Agent`](design-principles.md#5-abstract-supertypes)), `published_at`, `reference_date`, `methodology_uri`, `license`, `contact_uri`, `observations[]`, `dsd_uri`. Bound to `qb:DataSet`.

### `Period`

The temporal coverage of a MetricObservation. PS reifies the period (rather than carrying inline `start_date` / `end_date` like other `Event` subtypes) because the SDMX / Data Cube emitter needs a single URI-addressable interval to satisfy [W3C Data Cube integrity constraint IC-11](https://www.w3.org/TR/vocab-data-cube/#wf). Slots: `period_type` (`point_in_time` / `span` / `cohort` / `fiscal_year` / `calendar_year`), `start_date`, `end_date`, `granularity` (year / quarter / month / day), `reference_period_type`, `frequency` (`FREQ` codelist value: A / Q / M / D / W / H).

## Computation model

Borrowed from [FHIR R5 Measure](https://hl7.org/fhir/R5/measure.html), translated to PS slot URIs. FHIR Measure is the only standard with regulator-grade adoption (CMS eCQMs, NCQA HEDIS digital measures) for "compute an aggregate indicator from heterogeneous record-level data with auditable definitions and re-runnable provenance". We borrow the shape; we don't depend on FHIR types.

### `MetricCalculation` shape

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

`subject_class` is a divergence from FHIR Measure's `subject[x]` (which is `CodeableConcept | Reference(Group)`): PS subjects are PS class URIs. `improvement_notation` accepts `policy_dependent` for non-clinical metrics where the desirable direction depends on policy framing (e.g., expenditure-to-GDP).

### Population types and scoring validity

FHIR Measure's nine populations and their applicability to each scoring method:

| Type | Purpose |
|------|---------|
| `initial-population` | The universe of records the metric considers. |
| `denominator` | Subset of initial-population that qualifies for the denominator. |
| `denominator-exclusion` | Records removed from denominator. |
| `denominator-exception` | Records counted toward denominator but exempt from numerator. |
| `numerator` | Subset of denominator that meets the success condition. |
| `numerator-exclusion` | Records removed from numerator. |
| `measure-population` | Records whose per-record observation is aggregated. |
| `measure-population-exclusion` | Records removed from `measure-population`. |
| `measure-observation` | The value computed per record in `measure-population`. |

| Scoring | Required populations |
|---------|----------------------|
| `proportion` | initial-population, denominator, numerator (plus optional exclusions / exception) |
| `ratio` | initial-population, denominator, numerator (independent of denominator) |
| `continuous-variable` | initial-population, measure-population, measure-observation (plus optional measure-population-exclusion) |
| `cohort` | initial-population only |

Authors validate `populations[*].type` against the metric's `scoring` value at schema-load time.

### Criteria language

Every `criteria` field is paired with a `language` IANA media type. PublicSchema does not pick a winner; it pins the media type so consumers know which engine to invoke. **Three languages are first-class:**

1. **`application/sql`** &mdash; warehouse-bound; the practical default for delivery-platform implementers. Convention: `${ps.Enrollment}` placeholders for class references, resolved by the executor. Expected to cover ~80% of v0.1 metrics.
2. **`application/vtl`** &mdash; SDMX-TWG's [Validation and Transformation Language](https://github.com/sdmx-twg/vtl) (v2.1, 2025-04-11). The natural fit for SDMX-bound aggregations, codelist mappings, hierarchical roll-ups, and time-period arithmetic. For metrics whose target consumers are SDMX agencies, VTL is recommended. Engine reality: **one live engine** ([Banca d'Italia `vpinna80/VTL`](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). See [Risks](#risks).
3. **`text/cql`** &mdash; HL7 Clinical Quality Language ([spec v1.5.3](https://cql.hl7.org/), CMS / HEDIS adoption). Recommended for metrics that intersect clinical or quality-of-care (UHC effective coverage, immunisation, MNCH). PublicSchema publishes a CQL **ModelInfo** XML binding CQL to PS classes, targeted at the **[HL7 reference engine `cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language)** (Apache-2.0, v4.8.0).

FHIRPath is too weak for set-level aggregation and is not first-class. Authors who want to express a stratifier in FHIRPath may do so with `language: text/fhirpath`, but PS does not ship a normative subset or test harness.

### Library resolution

`criteria: @ref:LibraryName.Symbol` resolves to `<library_uri>#<Symbol>`, where `library_uri` appears in the metric's `calculation.libraries[]` list. Libraries are HTTPS-dereferenceable; content is the text of the language declared by `language` (a CQL file, a VTL file, a SQL file). Library URIs are version-tagged; PS recommends content-addressed URIs (e.g., `.../sp-coverage-cql-1.0`) so that a metric's calculation is bit-stable across publications.

Mirrors FHIR Measure's `Measure.library = canonical(Library)` reference.

## Alignment URIs

`aligns_with` on `Metric`, `MetricDimension`, and `MetricAttribute` carries external URIs that route a single PublicSchema artefact into the right consumer pipeline. **This is the dedup mechanism**: one PS Metric definition, many agency aliases. The political payload of the whole spec.

| Target | URI pattern | Owner |
|--------|-------------|-------|
| SDMX agency DSD | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)` (URN structure from [SDMX-IM](https://github.com/sdmx-twg/sdmx-im)) | SDMX TWG, agency-issued |
| SDMX cross-domain concept | `urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=SDMX:CROSS_DOMAIN_CONCEPTS(2.0).REF_AREA` (verify version against [registry.sdmx.org](https://registry.sdmx.org)) | SDMX TWG |
| SDMX measure (SDMX 3.0) | `urn:sdmx:org.sdmx.infomodel.datastructure.Measure=<Agency>:<DSD>(<Version>).<Code>` | SDMX TWG |
| UN SDG indicator | `https://unstats.un.org/sdgs/indicators/series/<SERIES_CODE>` | UN Statistics |
| UN SDG Global DSD | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=IAEG-SDGs:SDG(1.0)` (verify exact agency ID against [unstats.un.org/sdgs/sdmx](https://unstats.un.org/sdgs/sdmx)) | UN Statistics |
| ASPIRE family | `https://datacatalog.worldbank.org/aspire/<family-code>` (placeholder pattern; agency URL form may change) | World Bank |
| ESSPROS reference metadata | `https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm` | Eurostat |
| OECD SOCX DSD | `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=OECD.ELS.SPD:DSD_SOCX_AGG(1.0)` (live, verified at `sdmx.oecd.org`) | OECD |
| DHIS2 indicator | `dhis2://indicator/<uid>` (program-local) | Local DHIS2 instance |
| IATI result / indicator | `https://iatistandard.org/en/iati-standard/203/codelists/IndicatorMeasure/` | IATI |
| HXL hashtag | `https://hxlstandard.org/standard/hashtags/#indicator+value+num` | HXL |
| RDF Data Cube measure | `<publicschema metric URI>` rendered as `qb:MeasureProperty` | self |

Alignment is one-way semantic; PublicSchema does not synchronise with these registries. A change in ILO's DSD requires a new PS schema version that updates the alignment URI.

**Back-pointer from an agency DSD to a PS Metric.** SDMX has no native cross-system reference. Use the SDMX-IM `Annotation` mechanism on the agency DSD: `AnnotationType = ps:alignedMetric`, `AnnotationURL = <PS Metric URI>`. This is normatively correct and round-trips losslessly. In SDMX 3.0, "extends" means DSD-internal inheritance, not external alignment, so the Annotation mechanism is the only valid path.

## Emission targets

LinkML is the source of truth. Generators land in `build/` alongside the existing `rdf_export.py`. The status column is honest: most "must-have" generators do **not yet exist** in LinkML upstream and will be authored in PublicSchema's own build pipeline.

| Output | Why | Status | Priority |
|--------|-----|--------|----------|
| **JSON Schema** (per Metric, MetricObservation, MetricReport) | Default consumer format; tabular submitters; OpenAPI integration. | LinkML `gen-jsonschema` exists | P0 |
| **JSON-LD context** | Existing PS pattern. | LinkML `gen-jsonld-context` exists | P0 |
| **SHACL shapes** | Validation; existing PS pattern. | LinkML `gen-shacl` exists | P0 |
| **CSVW** (CSV on the Web, JSON-LD metadata) | Lowest-friction tabular publication; minimum bar for analyst submission. | **To build** ([linkml/linkml#86](https://github.com/linkml/linkml/issues/86) open since 2020-11, no PR) | P0 |
| **SDMX-CSV v2.1** | Minimum bar for WB / ILO / OECD / Eurostat data analysts. Spec: [sdmx-twg/sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) (v2.1.0, 2025-08-27). | **To build** (no LinkML `gen-sdmx`; no third-party converter) | P0 |
| **SDMX-ML v3.1 (structural messages)** | DSD / Codelist / ConceptScheme submissions to agency registries. Spec: [sdmx-twg/sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) (v3.1.0, 2025-05-16). | **To build** | P0 |
| **SDMX-ML v3.1 (data messages)** | Full structural-and-data exchange. | **To build** | P1 |
| **SDMX-JSON v2.1** | Dissemination web format; agency APIs (OECD, ECB, ILO) respond JSON by default. Spec: [sdmx-twg/sdmx-json](https://github.com/sdmx-twg/sdmx-json) (v2.1.0, 2025-05-16). | **To build** | P1 |
| **RDF Data Cube TTL** | Graph-native consumers; LOD pipelines; SPARQL queries. | **To build** (~200 LOC; PS owns this directly) | P2 |
| **Excel** (per Metric definition) | Definition workbook, matching PS's existing per-concept Excel downloads. | Existing PS pipeline | P2 |
| **DHIS2 indicator JSON** | Direct import to DHIS2 instances. Lossy: relies on local UID resolution. | **To build**; no public cross-walk exists | P3 |
| **HXL hashtag suggestion** | Inline hashtag header for CSV exports. Best-effort. | **To build** | P3 |
| **IATI XML indicator fragment** | For donor-reported results integration. | **To build** | P3 |

SDMX 3.0 makes `Measure` a first-class component list (it removed SDMX 2.1's `MeasureDimension`). PS targets 3.0 only; round-trip to legacy 2.1 consumers is out of scope. DSD URN composition: `urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=<Agency>:<ID>(<Version>)`. SDMX 3.0 permits extended semver per [sdmx-twg/semver](https://github.com/sdmx-twg/semver). PublicSchema does not mint agency URNs; an agency reusing a PS metric mints its own URN and points back via an `Annotation` (see [Alignment URIs](#alignment-uris)).

There is no canonical RDF `sdmx:` namespace published by SDMX-TWG. The schema lists only `qb:` in `exact_mappings`, with SDMX URN references in prose. The Data Cube TTL emitter enforces, in v0.1: IC-1, IC-2, IC-3, IC-4, IC-5, IC-6, IC-11, IC-13, IC-14. IC-7 through IC-10 (slices) are N/A in v0.1; v0.2 may add slice generation if a consumer asks. IC-12 (no duplicate dimension tuples) is data-author responsibility, validated at emission time.

## Seed corpus

The v0.1 deliverable that proves the primitive: **~240 derivable indicators across WB / ILO / UN / UNICEF**, each shipped as one PS Metric with one executable `MetricCalculation` plus `aligns_with` URIs to every container the indicator appears in.

| Source | Derivable indicators (rough count) | Machine-readable input |
|--------|-----------------------------------|------------------------|
| **UN SDG** (custodian-published metadata) | ~30 (1.1.1, 1.2.1, the 1.3.1 set, 3.8.x UHC, 5.2&ndash;5.6, 10.1.1, 16.9.1) | [metadata.un.org/sdg/ontology](https://metadata.un.org/sdg/ontology) + per-indicator PDFs |
| **ILO** (custodian for 14 SDG indicators; SPSI series) | ~50 (coverage, adequacy, effective coverage by program type) | [ILOSTAT SDMX](https://ilostat.ilo.org/resources/sdmx-tools/) + bulk CSV |
| **WB ASPIRE** | ~100 (coverage, adequacy, benefit-incidence, poverty-reduction, by quintile) | [WB Indicators API](https://api.worldbank.org/v2/indicator?format=json) + ASPIRE Quality Check methodology |
| **WB Poverty &amp; Inequality Platform** | ~20 (extreme / national poverty headcount, gap, severity, Gini, bottom-40 growth) | [PIP API](https://pip.worldbank.org/) |
| **UNICEF MICS-derived** | ~40 (child welfare, WASH, education) | MICS reports + indicator dictionary |

**Total: ~240 indicators for v0.1.** v0.2 extends to OECD IDD / SOCX-derivable and Eurostat EU-SILC. v0.3 broadens to humanitarian (HXL-shaped) and program-management (leakage, processing time) indicators that lack a single inter-agency custodian.

Practical ingestion path: scrape each source's machine-readable indicator catalogue, auto-generate one `Metric` skeleton per indicator (title, description, source URL, topic), then hand-author the `MetricCalculation` against PS classes for the derivable subset. Sourced-only indicators (most of WDI macro) are dropped from this exercise; they remain valid citations but not PS Metrics.

## Custodian-review process

A PS Metric ships `bibo:draft` until the indicator's custodian agency signs off, then ships `bibo:published`. Custodian by domain:

- Social protection coverage / adequacy &rarr; ILO (SDG 1.3.1 custodian).
- Poverty / inequality &rarr; World Bank (PIP / ASPIRE; SDG 1.1.1 / 1.2.1).
- Child welfare / nutrition &rarr; UNICEF (MICS).
- Health / UHC &rarr; WHO (SDG 3.8.x).
- Civil registration / legal identity &rarr; UNICEF / UNHCR / DESA (SDG 16.9.1).
- Gender equality &rarr; UN Women / UNSD (SDG 5.x).

Custodian sign-off is a social contract, not a technical gate; PS does not control the namespace. The `bibo:draft` &rarr; `bibo:published` transition signals reviewed-by-custodian on a per-metric basis. Custodian-signed PS Metric URIs become citable in the custodian's own metadata.

## Worked example: SDG 1.3.1 coverage

Indicator: *"Proportion of population covered by social protection floors / systems"*, ILO custodian, SDG 1.3.1a (effective coverage).

PublicSchema definition (conceptual):

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

Sample observation:

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

This single record, when emitted as SDMX-CSV with an agency DSD URN, drops directly into ILOSTAT or ASPIRE pipelines. When emitted as RDF Data Cube with the PS metric URI, it joins a country LOD graph. When emitted as JSON Schema-validated JSON, it lands in a generic dashboard. None of the three requires re-derivation; alignment URIs do the routing.

For practitioners less familiar with FHIR Measure's vocabulary: `initial-population` is "the universe of records considered" (everyone in the resident-population register); `denominator` is "who we're measuring coverage *of*" (same as initial-population for 1.3.1a); `numerator` is "who we're saying *is* covered" (people with at least one active SP enrolment during 2024); `denominator-exclusion` removes records counted in error (non-residents); `numerator-exclusion` removes records counted as covered in error (fraudulent or duplicate enrolments).

## LinkML schema

The normative source is [`schema/metrics.yaml`](../schema/metrics.yaml), wired into the composite schema via the `metrics` entry in `schema/publicschema.yaml`. Ten classes (`Metric`, `MetricDimension`, `MetricAttribute`, `MetricCalculation`, `PopulationCriterion`, `Stratifier`, `MetricObservation`, `MetricReport`, `Period`, plus structured-pair helpers `DimensionValue` and `AttributeValue`), the slots they reference, and the enums (`ValueType`, `ScoringMethod`, `ImprovementNotation`, `RateAggregation`, `MetricTopic`, `AttachmentLevel`, `PopulationType`, `PeriodType`, `Granularity`, `Frequency`). The `ObsStatus` codes are not republished; they resolve via the SDMX URN `urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_OBS_STATUS(2.3)`.

Two LinkML-keyword adjustments are worth flagging for readers:

- `MetricDimension.range` and `MetricAttribute.range` (the spec's prose names) are spelled `value_range` in the LinkML file to avoid shadowing the `range` keyword. RDF emission uses the intended `range`.
- `MetricObservation.value` is spelled `metric_value` to avoid colliding with `value` slots defined elsewhere in the composite. JSON Schema emission renames it back to `value`.

`MetricObservation` is `is_a: Event`. `MetricReport.publisher` ranges over `Agent` (see [Principle 5](design-principles.md#5-abstract-supertypes)). `dimension_values` and `attribute_values` are modelled as ordered lists of structured pairs (`DimensionValue` and `AttributeValue`) rather than maps, so SDMX DSD round-trip is stable.

## JSON Schema (inline)

Practitioners flagged JSON Schema as the single highest-leverage artefact, ahead of LinkML codegen. PublicSchema commits to publishing `metric.schema.json`, `metric-observation.schema.json`, and `metric-report.schema.json` at stable URIs under `https://publicschema.org/schemas/v1/`, hand-authored and tracked alongside the LinkML source so they ship from day one (not gated behind a `gen-jsonschema` build pass).

Indicative `MetricObservation` schema (Draft 2020-12):

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

## Open questions

These remain open after the v0.1 design pass.

1. **Hierarchy and category schemes for dimensions.** SDMX dimensions carry hierarchies (M49 for REF_AREA, age-band hierarchies for AGE). v0.1 ships flat codelists; v0.2 adds hierarchy when an emission consumer requires it.
2. **Content Constraints.** Agencies attach `ContentConstraint` artefacts saying "for this dataflow, REF_AREA is restricted to these codes". v0.1 emits unconstrained DSDs; v0.2 may add a `MetricConstraint` shape if agency emission requires it.
3. **Cohort scoring.** Cohort retention (12-month coverage given enrolment in month 0) needs Period offset math and lineage across time. Scoped out of v0.1; revisit in v0.2.
4. **Privacy / small-cell suppression.** Most common failure mode in public indicator publishing. `cell_count` and `confidentiality_status` are in the default `MetricAttribute` library; agencies set thresholds at emission time. Suppression *logic* is per-agency, not normative.
5. **AI / ML model metrics.** Out of scope for this spec; revisit when the AI Hub taxonomy stabilises.
6. **Multi-measure metrics.** SDMX 3.0 allows multiple Measures per DSD; PS v0.1 ships single-measure only. Add `MetricMeasure` class in v0.2 if a real use case arrives.

## Risks

Spec-honest catalogue of dependencies and gaps. None are fatal; each is buildable.

1. **VTL tooling monoculture.** VTL is recommended for SDMX-bound metrics but only **one** open-source engine is alive ([Banca d'Italia `vpinna80/VTL`](https://github.com/vpinna80/VTL), EUPL-1.2, v1.3.0). Eurostat's VTL engine has been abandoned since 2020. Mitigation: VTL is **never the only language for a metric's primary calculation**. Authors must ship at least one of {SQL, CQL} alongside any VTL criteria, and the SDMX emitter must accept SQL-translated equivalents.
2. **Net-new generator burden.** LinkML upstream has `gen-jsonschema`, `gen-shacl`, `gen-jsonld-context`. It does **not** have `gen-csvw`, `gen-sdmx`, or `gen-datacube`. PublicSchema will author ~1500 LOC of generators in `build/` for v0.1 (CSVW, SDMX-CSV, SDMX-ML structural messages, RDF Data Cube TTL). The emission-targets table marks each as `existing` vs. `to-build`. Upstreaming `gen-csvw` to LinkML is in the v0.2 roadmap.
3. **CQL non-FHIR ModelInfo is rare in production.** CQL the *language* supports custom ModelInfo XML; CQL *engines* mostly ship with FHIR-only bindings. The HL7 reference engine [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language) (Apache-2.0, v4.8.0) accepts custom ModelInfo. PublicSchema commits to publishing `PublicSchema-ModelInfo.xml` against the HL7 reference engine's ModelInfo schema in v0.2; budget one week with a CQL specialist.
4. **DHIS2 emitter is greenfield.** No public cross-walk of external indicator definitions into DHIS2 exists. The DHIS2 target schema is stable; the cross-walk is PS work. Deferred to v0.3.
5. **HXL toolkit bus factor is 1.** [`HXLStandard/libhxl-python`](https://github.com/HXLStandard/libhxl-python) is one-maintainer-sporadic. HXL hashtag suggestion stays a P3 best-effort emitter in v0.3.

## Implementation roadmap

- **v0.1 (foundation, target: 2026 Q3).** [`schema/metrics.yaml`](../schema/metrics.yaml) carrying the seven catalogue classes plus structural helpers. 10&ndash;15 seed Metrics covering SDG 1.3, ASPIRE coverage / adequacy, ESSPROS expenditure, SOCX policy areas. External alignment files for SDMX, SDG, ASPIRE, ESSPROS, SOCX. P0 generators per the emission-targets table. Hand-authored JSON Schemas at `publicschema.org/schemas/v1/`. One CQL library and one VTL transformation as worked examples for SDG 1.3.1a. ADR-020 captures these decisions.
- **v0.2 (interoperability, target: 2027 Q1).** Full ~240-indicator seed corpus, extended to OECD IDD / Eurostat EU-SILC. P1 / P2 generators. Cohort scoring. Dimension hierarchies where consumers ask. `PublicSchema-ModelInfo.xml` tested against `cqframework/clinical_quality_language`. Upstream `gen-csvw` to LinkML (closes [linkml/linkml#86](https://github.com/linkml/linkml/issues/86)).
- **v0.3 (broader catalogue, target: 2027 Q3).** P3 generators (DHIS2, HXL, IATI). 30&ndash;50 additional Metrics across program management, inclusion, humanitarian. `MetricConstraint` shape if agency emission requires.

## References

- W3C. [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). Recommendation, 2014. (No SDMX-RDF binding is maintained by SDMX-TWG in 2026; this is the de facto RDF mapping, maintained outside the TWG.)
- SDMX TWG. [SDMX 3.0 standards portal](https://sdmx.org/standards-2/), and the canonical SDMX-TWG repositories:
  - [sdmx-im](https://github.com/sdmx-twg/sdmx-im) &mdash; Information Model and URN structure.
  - [sdmx-ml](https://github.com/sdmx-twg/sdmx-ml) v3.1.0 (2025-05-16) &mdash; XML format; XSDs at [xml.sdmx.org](https://xml.sdmx.org).
  - [sdmx-json](https://github.com/sdmx-twg/sdmx-json) v2.1.0 (2025-05-16); docs at [json.sdmx.org](https://json.sdmx.org).
  - [sdmx-csv](https://github.com/sdmx-twg/sdmx-csv) v2.1.0 (2025-08-27).
  - [sdmx-rest](https://github.com/sdmx-twg/sdmx-rest) v2.2.2 (2025-08-21).
  - [vtl](https://github.com/sdmx-twg/vtl) v2.1 (2025-04-11); docs at [sdmx-twg.github.io/vtl](https://sdmx-twg.github.io/vtl/).
  - [sdmx-registry](https://github.com/sdmx-twg/sdmx-registry), [sdmx-tck](https://github.com/sdmx-twg/sdmx-tck), [urn-resolver](https://github.com/sdmx-twg/urn-resolver) ([urn.sdmx.io](https://urn.sdmx.io)), [semver](https://github.com/sdmx-twg/semver).
- SDMX. [Cross-Domain Code Lists](https://sdmx.org/sdmx_cdcl/); [CL_OBS_STATUS v2.3 release notes](https://sdmx.org/news/version-2-3-of-cl_obs_status-released/) (2026-01-06).
- BIS. [FMR (Fusion Metadata Registry)](https://www.sdmx.io/software/fmr/) &mdash; current SDMX registry implementation; [bis-med-it/fmr-public](https://github.com/bis-med-it/fmr-public) v12.0.0 (2026-05-08).
- HL7. [FHIR R5 Measure resource](https://hl7.org/fhir/R5/measure.html); [CQF-Measures Implementation Guide v2.0.0](https://hl7.org/fhir/us/cqfmeasures/STU2/) (2020-07-23, R4 / R4B-targeted; 5.x at build.fhir.org is unpublished continuous build).
- HL7. [CQL Specification v1.5.3](https://cql.hl7.org/).
- [`cqframework/clinical_quality_language`](https://github.com/cqframework/clinical_quality_language) &mdash; HL7 reference CQL engine, Apache-2.0, v4.8.0 (2026-05-08). Primary non-FHIR ModelInfo target.
- [`vpinna80/VTL`](https://github.com/vpinna80/VTL) &mdash; Banca d'Italia VTL engine, EUPL-1.2, v1.3.0 (2025-09-24). De facto reference VTL implementation.
- ILO. [ILOSTAT SDMX tools](https://ilostat.ilo.org/resources/sdmx-tools/) and [World Social Protection Database](https://www.social-protection.org/gimi/WSPDB.action); [SDG 1.3.1 metadata (PDF)](https://unstats.un.org/sdgs/metadata/files/Metadata-01-03-01a.pdf).
- World Bank. [ASPIRE](https://www.worldbank.org/en/data/datatopics/aspire); [Poverty &amp; Inequality Platform](https://pip.worldbank.org/); [WB Indicators API](https://api.worldbank.org/v2/indicator?format=json).
- Eurostat. [ESSPROS methodology](https://ec.europa.eu/eurostat/web/social-protection/methodology); [ESMS reference metadata](https://ec.europa.eu/eurostat/cache/metadata/en/spr_esms.htm).
- OECD. [SOCX Social Expenditure Database](https://www.oecd.org/en/data/datasets/social-expenditure-database-socx.html); [SOCX DSD live](https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.SPD/DSD_SOCX_AGG@DF_SOCX_AGG/1.0).
- UN Stats. [SDG indicators metadata](https://unstats.un.org/sdgs/metadata/); [SDG Metadata API (UN LDS)](https://metadata.un.org/sdg/ontology).
- UNICEF. [MICS](https://mics.unicef.org/) and indicator dictionaries.
- DHIS2. [Indicators documentation](https://docs.dhis2.org/en/implement/database-design/aggregate-system-design/indicators.html).
- OCHA. [HXL hashtags and attributes](https://centre.humdata.org/learning-path/hxl/hashtags-attributes/).
- IATI. [Activity standard: result / indicator](https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/indicator/).
- LinkML. [linkml/linkml#86 CSVW generator](https://github.com/linkml/linkml/issues/86) (open, no PR); [linkml/linkml#901 DataCube exploration](https://github.com/linkml/linkml/issues/901) (closed without resolution).
- VLDB. [SDG-KG: Indicator Workflows as a Knowledge Graph](https://dl.acm.org/doi/10.14778/3750601.3750673), 2025.
