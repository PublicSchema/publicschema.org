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
just build      # generate vocabulary data from YAML sources
just dev        # start the dev server
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup and how to add or modify vocabulary entries.

## Project structure

```
schema/           Vocabulary source files (YAML)
  concepts/       Concept definitions
  properties/     Property definitions
  vocabularies/   Controlled value sets
  credentials/    Verifiable Credential schemas
build/            Python build pipeline
site/             Astro static site
tests/            Python test suite
docs/             Documentation (rendered on the site)
examples/         Example Verifiable Credentials
```

## License

This project uses a dual license:

- **Vocabulary definitions** (everything under `schema/`): [Creative Commons Attribution-ShareAlike 4.0](LICENSE-VOCABULARY)
- **Code** (build tools, site, tests, configuration): [Apache License 2.0](LICENSE)

See [publicschema.org/terms/](https://publicschema.org/terms/) for full details.
