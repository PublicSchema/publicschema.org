# ADR-026: Dates known only to a year or a month

**Status:** Accepted

## Context

Some facts are routinely recorded without a full calendar date. Animal records often give a birth date as a year or a year and month when the exact day is unknown. Genebank passport data (FAO/Bioversity Multi-Crop Passport Descriptors) records a collecting date with missing parts, such as `1990----`. An `xsd:date` value cannot hold either: a producer must invent a day, and a consumer cannot tell an invented day from a recorded one.

The vocabulary already records a related but different fact. `crvs/event_date_estimated` is a boolean that says a civil registration event date is an estimate rather than a known exact date. An estimated date can be a full date, and a date known only to its year is not necessarily an estimate.

## Decision

1. **A slot whose source routinely records partial dates uses a string with an anchored ISO 8601 reduced-precision pattern.** The value is a year (`2021`), a year and month (`2021-05`) or a full date (`2021-05-14`), validated by the pattern `^[0-9]{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)?$`. Parts that were not recorded are left out, never invented. `animal_birth_date` and `accession_collection_date` follow this convention.
2. **One slot per fact.** A partial-date slot is not paired with a separate full-date slot or a precision flag for the same fact; the value's own length states its precision.
3. **Other date slots stay `date`.** Where sources record full dates, as for `animal_death_date` and `seed_lot_production_date`, the slot keeps the `date` range.
4. **Estimation is a separate fact.** When a source says that a date is estimated, that is recorded with a boolean such as `crvs/event_date_estimated`, whatever the precision of the date. A reduced-precision value does not by itself mean the date was estimated.

The pattern reaches both exports: the JSON Schema build carries `pattern`, and the SHACL export carries it as `sh:pattern`. Because both use unanchored regular-expression search, the pattern is anchored with `^` and `$`; [authoring LinkML](../docs/authoring-linkml.md) documents this.

## Alternatives considered

- **Keep `date` and document that an unknown month or day is set to 01.** Rejected. A consumer cannot distinguish 1 January from "unknown", and age or interval calculations silently treat invented days as facts.
- **A `date` slot plus a precision code.** Rejected. Two slots for one fact can disagree, and the invented day is still present in the date.
- **Earliest and latest possible dates.** Rejected as the default. It suits uncertain intervals, but a year or year and month is exactly what these sources record, and the bounds would be derived values.
- **The XSD types `gYear` and `gYearMonth` as a union with `date`.** Rejected. The JSON Schema build does not carry `any_of`, and a union would validate differently in the two exports.
- **Extended Date/Time Format (ISO 8601-2).** Deferred. It can express uncertainty and approximation as well as precision, but the sources behind the current slots need only reduced precision, which ISO 8601-1 covers.

## Consequences

Consumers that compute ages or intervals from these slots must handle values of three lengths. A consumer that needs a full date must decide how to treat a year or a year and month instead of receiving an invented day.

JSON-LD and RDF carry these values as plain strings, not `xsd:date` literals. A SPARQL query that compares them with dates needs to account for that.

A new slot uses the reduced-precision convention only when its sources routinely record partial dates. Existing `date` slots are not converted.
