# PublicSchema site

The Astro site renders the reference model and documentation from this repository. Run the supported workflow from the repository root so generated data is prepared before Astro starts:

```bash
just setup          # install Python and site dependencies
just dev            # generate data and start the development server
just site-build     # validate, generate data, and build the production site
just site-preview   # preview the production build
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for prerequisites and content checks. `npm run build` inside `site/` only runs Astro; use `just site-build` when source data may have changed or when building a fresh checkout.

## Source and generated files

- `src/pages/`, `src/components/`, and `src/styles/` contain site code.
- `../dist/metrics_catalog.json` is generated from `schema/metric_catalog/` by repository-local build tools.
- The site reads the generated vocabulary and other exports under the repository's `dist/` directory.
- `public/` contains maintained static assets and generated public downloads and schemas prepared by `just build`.
- `../docs/` contains documentation rendered on the site.
- `site/dist/` is the production site output.

Edit vocabulary content in the modular LinkML files under `../schema/` and value mappings under `../schema/value_crosswalks/`, then regenerate with `just build`. Do not edit generated JSON, schemas, or downloads directly. See the [LinkML authoring guide](../docs/authoring-linkml.md).
