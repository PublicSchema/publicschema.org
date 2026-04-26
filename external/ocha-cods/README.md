# OCHA Common Operational Datasets (CODs)

## What this is

The Common Operational Datasets are the authoritative reference data
maintained under OCHA's Field Information Services Section (FISS) for
humanitarian response. They are published on the Humanitarian Data
Exchange (HDX) and maintained per country, with a global aggregation
layer.

The COD framework groups several products:

| Code | Product | Scope |
|------|---------|-------|
| COD-AB | Administrative Boundaries | Subnational admin polygons (admin 0..n) and their codes |
| COD-PS | Population Statistics | Population counts disaggregated by admin unit |
| COD-HP | Humanitarian Profile | Affected, displaced, in-need figures per admin unit |
| COD-EM | Emergency-specific | Crisis-bound datasets layered on COD-AB |

P-codes (place codes) are the identifier system shared across the
products and used as the join key.

## Scope of this mapping

This directory currently covers **COD-AB only**. The other COD products
(PS, HP, EM) publish *data about* administrative areas (population,
affected-people figures), which PublicSchema does not currently model
as concepts. They can be added later if and when corresponding
PublicSchema concepts exist.

Target PublicSchema concept: `Location`. (`Location` already carries
`administrative_level`, `parent_location`, `geocodes`, `geometry`, and
`location_name`, which is the bulk of the COD-AB attribute schema.)

## Source

- Landing page: <https://data.humdata.org/dataset/cod-ab-global>
- Per-country datasets: `https://data.humdata.org/dataset/cod-ab-<iso3>`
  (e.g., `cod-ab-sle`, `cod-ab-tcd`, `cod-ab-mli`).
- Global aggregations by admin level (FAO catalog mirror):
  - <https://data.apps.fao.org/catalog/dataset/hdx-ocha-administrative-boundaries-cods-national>
  - <https://data.apps.fao.org/catalog/dataset/hdx-ocha-administrative-boundaries-cods-admin-1>
  - <https://data.apps.fao.org/catalog/dataset/hdx-ocha-administrative-boundaries-cods-admin-2>
  - <https://data.apps.fao.org/catalog/dataset/hdx-ocha-administrative-boundaries-cods-admin-3>
  - <https://data.apps.fao.org/catalog/dataset/hdx-ocha-administrative-boundaries-cods-admin-4>
- COD-AB documentation:
  <https://knowledge.base.unocha.org/wiki/spaces/imtoolbox/pages/2557378679/Administrative+Boundaries+COD-AB>
- P-codes documentation:
  <https://humanitarian.atlassian.net/wiki/spaces/imtoolbox/pages/222265609/P-codes>

## Why we map a data product, not an API

COD-AB is not a software system; it is a published data convention.
Each country's COD-AB ships as Shapefile / GeoJSON / GeoPackage layers
with a consistent attribute schema that integrators read directly.
Mapping its attributes onto `Location` properties tells consumers how
to materialize PublicSchema records from a COD-AB layer without having
to re-derive the convention each time.

This is the same shape as `external/semic/` and `external/govstack-payments/`:
spec/data-format mappings, not API mappings.

## Remaining gaps

`Location` already covers admin level, parent, geocodes, and geometry,
which are the bulk of COD-AB. What remains:

1. **Multilingual names.** COD-AB carries `adm{n}_{lang}` per unit;
   `Location` has only `location_name` (single string).
2. **Temporal validity.** COD-AB carries `validon` / `validto`;
   `Location` has no effective-period properties. P-code joins across
   time are silently wrong without it.

Both are flagged inline in `matching.yaml`. Closing them is a separate
schema decision, not a side-effect of documenting the mapping.

## Files

- `matching.yaml` — attribute-level mapping from COD-AB layer fields
  to PublicSchema `Location` properties, with explicit gaps.
