# ILO SDG seed -- PublicSchema derivability gaps

The ILO SDG seed at `schema/metric_catalog/ilo_sdg.yaml` was trimmed from 25 to 17
indicators by `build/seed_metrics_from_ilo_sdmx.py`. Four kept indicators require
small PS slot additions before calculation blocks can be hand-authored (see
`docs/metrics-spec.md` line 310). Item 5 is a boundary fact, not a gap.

---

## 1. NEET status (SDG 8.6.1)

| Field | Detail |
|---|---|
| Indicator(s) | `sdg_0861_sex_rt` |
| Gap | `EmploymentStatus` (vocabularies.yaml line 6822, 19th ICLS) covers the employment leg; `education_level` (identity.yaml line 1205) records attainment only. No slot for current enrollment in education or training. |
| Standard | SDG 8.6.1 indicator metadata; ILO/UNESCO/UIS NEET definition (see ILO ICLS resolution text) |
| Proposed slot | `currently_in_education_or_training: boolean` on `Person`. Boolean over enum: avoids null-semantics complexity; minimum needed for the NEET exclusion criterion. |
| Class | `Person` |
| Notes | Age band 15-24 filters on existing `date_of_birth`. |

---

## 2. Informal employment (SDG 8.3.1)

| Field | Detail |
|---|---|
| Indicator(s) | `sdg_0831_sex_eco_rt`, `sdg_b831_sex_eco_rt` (18th and 19th ICLS variants) |
| Gap | `status_in_employment` (line 2489) classifies the relationship type; `industry` (line 1803, ISIC Rev.4) covers sector. Neither captures formal/informal status. |
| Standard | ILO 17th ICLS Resolution on informal employment (2003); ILO 19th ICLS Resolution (2013) (see ILO ICLS resolution text) |
| Proposed slot | `informal_employment: boolean` on `Person`. Cleaner than an `employment_arrangement` enum: both ICLS variants use a binary numerator/denominator split; avoids a third employment enum. |
| Class | `Person` |

---

## 3. Working poverty inputs (SDG 1.1.1)

| Field | Detail |
|---|---|
| Indicator(s) | `sdg_0111_sex_age_rt` (dataflow title: US$3 PPP, line 39 of seed) |
| Gap | `income_source` (line 1795) is categorical. No per-household income/consumption quantum for poverty-line comparison. |
| Standard | SDG 1.1.1; World Bank poverty line ($2.15/day 2017 PPP, Sep 2022 update). Dataflow title cites $3 PPP -- verify vintage before authoring the calculation block. |
| Proposed slots | Option A: `household_consumption_per_capita_ppp: decimal` on `Household` (constant 2017 USD PPP/day) -- self-contained but requires PS to manage PPP deflation metadata. Option B: external join to LSMS microdata via a survey-wave identifier -- lean but non-self-contained calculation. Resolve the LSMS ingestion question first. |
| Class | `Household` (Option A) or external join (Option B) |

---

## 4. Child labour (SDG 8.7.1)

| Field | Detail |
|---|---|
| Indicator(s) | `sdg_a871_sex_age_rt` (18th ICLS: economic activity); `sdg_b871_sex_age_rt` (19th ICLS: economic activity + household chores) |
| Gap | No slot for weekly hours worked or hazardous-work status. Both required by ICLS 18/19: hours thresholds differ by age band; hazardous work triggers classification regardless of hours. |
| Standard | ILO 18th ICLS Resolution on statistics of child labour (2008); SDG 8.7.1 metadata (see ILO ICLS resolution text) |
| Proposed slots | `weekly_hours_worked: decimal` and `hazardous_work: boolean` on `Person`. Preferred over a `ChildLabourAssessment` event class; reference-week interpretation belongs in the calculation block. For `sdg_b871`, flag `weekly_household_chores_hours: decimal` as a TODO. |
| Class | `Person` |

---

## 5. SP coverage denominator (SDG 1.3.1) -- boundary fact

| Field | Detail |
|---|---|
| Indicator(s) | `sdg_0131_sex_soc_rt` |
| Gap | None. Numerator is derivable from `Enrollment` + `Program`. |
| Standard | ILO/ISSA/WHO Social Protection Platform, SDG 1.3.1 methodology |
| Proposed slot | None |
| Notes | Denominator (total population by sex, age, administrative area) comes from a national statistics office. The calculation block must reference an external population table; do not add a PS slot to resolve it. |

---

## Out of scope

Eight dataflows removed from the pre-trim 25, covering six distinct SDG indicators (8.2.1 and 8.8.1 each have two dataflow variants). The exact dataflow ids are listed in the comment block above `RELEVANT_SDG_DATAFLOWS` in `build/seed_metrics_from_ilo_sdmx.py`.

- **SDG 8.2.1** -- Annual growth rate of output per worker; macro national accounts. (Dropped: `DF_SDG_0821_NOC_RT` 18th ICLS, `DF_SDG_B821_NOC_RT` 19th ICLS.)
- **SDG 8.5.1** -- Average hourly earnings of employees by sex; PS does not model wages. (Dropped: `DF_SDG_0851_SEX_OCU_NB`.)
- **SDG 8.8.1** -- Fatal and non-fatal occupational injuries per 100,000 workers; requires injury registry, no PS event model. (Dropped: `DF_SDG_F881_SEX_MIG_RT` fatal, `DF_SDG_N881_SEX_MIG_RT` non-fatal.)
- **SDG 8.8.2** -- Level of national compliance with labour rights; country-level qualitative rating. (Dropped: `DF_SDG_0882_NOC_RT`.)
- **SDG 8.b.1** -- Existence of a developed and operationalized national strategy for youth employment; country-level Yes/No. (Dropped: `DF_SDG_08B1_NOC_NB`.)
- **SDG 10.4.1** -- Labour income share as a percent of GDP; macro national accounts. (Dropped: `DF_SDG_1041_NOC_RT`.)
