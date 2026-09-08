# ILO SDG catalog calculation limits

`schema/metric_catalog/ilo_sdg.yaml` contains selected indicator definitions from
the ILO SDMX registry. `build/seed_metrics_from_ilo_sdmx.py` owns the explicit
selection of 17 dataflows. Catalog presence describes a measure and its source;
it does not establish that PublicSchema records contain every input required to
calculate that measure.

Before implementing a calculation, establish its population, reference period,
source definitions and available inputs. In particular:

- NEET measures need current education and training participation, not only
  educational attainment and employment status.
- Informal-employment measures require the applicable statistical definition;
  employment status and industry alone do not determine informality.
- Working-poverty measures need household income or consumption, the poverty-line
  vintage and compatible purchasing-power units. A source label does not perform
  those conversions.
- Child-labour measures need age-specific rules, time-use and hazardous-work
  information under the selected statistical standard.
- Social-protection coverage needs a compatible population denominator. Registry
  enrollment counts alone do not establish that denominator or complete coverage.

The seed excludes macroeconomic, injury-registry and country-level indicators
outside its selected record-level scope. The script lists the retained dataflows;
this catalog is not the full ILO SDG collection. These limits do not propose new
universal properties or claim an implemented calculation.

Ordinary builds use the checked-in catalog YAML offline. Running the refresh
script is a separate authoring operation that contacts the upstream service and
may update the source catalog. Its disposable `build/cache/` responses should not
be committed. See [Metrics specification](../metrics-spec.md) for the calculation
model and [Contributing](../../CONTRIBUTING.md) for build commands.
