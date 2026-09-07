# PublicSchema

**[publicschema.org](https://publicschema.org)**

Common definitions for public service delivery. Built so programs can coordinate, share data, and reach the people they serve.

## What this is

Service delivery systems collect similar data about the same people, but model it differently. PublicSchema provides a shared language: stable definitions, reusable properties, and standardized vocabularies that systems can adopt incrementally.

## What's in the vocabulary

- **Concepts**: semantic entities (Person, Enrollment, PaymentEvent, ...) with clear definitions written for policy practitioners, not developers.
- **Properties**: named, typed fields that apply to one or more concepts. Defined once and reused.
- **Vocabularies**: controlled value sets. References international standards (ISO, UN) where they exist. Defines canonical sets where they don't.
- **Credential schemas**: Verifiable Credential templates for secure data exchange.

Every element gets a stable URI. Everything is optional. Systems adopt what they need.

## Quick start

### Browse the vocabulary

Visit [publicschema.org](https://publicschema.org) to explore concepts, properties, and vocabularies.

### Build locally

Requires Python 3.12+ ([uv](https://docs.astral.sh/uv/)), Node.js 22.12+ and [just](https://just.systems/).

```bash
just setup      # install Python and Node dependencies
just build      # generate exports and site data from authored LinkML
just dev        # start the dev server
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup and how to add or modify vocabulary entries.

## Project structure

```
schema/                 Authored reference model and supporting data
  publicschema.yaml     Composite LinkML schema and module imports
  core.yaml, ...        Modular LinkML classes, slots, and enums
  credentials.yaml      Credential descriptors
  external/             LinkML partial schemas for external systems
  value_crosswalks/     Authored mappings between value sets
  metric_catalog/       Metric catalog sources
build/                  Python validation and build tools
dist/                   Generated exports (do not edit)
site/                   Astro site, including generated data and public artifacts
tests/                  Python test suite
docs/                   Documentation (rendered on the site)
examples/               Example Verifiable Credentials
```

For source conventions and examples, see [Authoring PublicSchema in LinkML](docs/authoring-linkml.md). Edit the source files and regenerate outputs with `just build`.

## License

This project uses a dual license:

- **Reference model** (everything under `schema/`): [Creative Commons Attribution 4.0](LICENSE-VOCABULARY)
- **Code** (build tools, site, tests, configuration): [Apache License 2.0](LICENSE)

See [publicschema.org/terms/](https://publicschema.org/terms/) for full details.
