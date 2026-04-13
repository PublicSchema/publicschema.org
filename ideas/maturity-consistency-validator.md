# Maturity consistency validation

## Problem

The validator (`build/validate.py`) does not check maturity consistency across
dependency chains. A candidate concept could depend on a draft supertype, or
reference a draft property/vocabulary, without any warning.

## Proposed rules

1. A candidate concept's **supertypes** must also be at candidate or normative.
2. A candidate concept's **properties** must also be at candidate or normative.
3. A candidate property's **vocabulary** (if any) must also be at candidate or normative.
4. Same rules apply at the normative level (normative cannot depend on draft or candidate).

## Where to implement

`build/validate.py`, as a new validation pass that runs after individual file
validation. It needs the full resolved dependency graph, so it should run after
all concept, property, and vocabulary files are loaded.

## Edge case: cross-concept type references

Properties like `program_ref` (typed as `Program`) or `schedule_ref` (typed as
`BenefitSchedule`) are references to other concepts. Whether a candidate concept
can have a property whose *value type* is a draft concept is debatable:

- Strict: the reference target must also be candidate.
- Pragmatic: the reference is just a URI/ID; the property's stability promise is
  about the property existing and being typed as a reference, not about the
  target concept's internal structure.

Recommend starting with the pragmatic interpretation and revisiting if it causes
real problems.

## Context

Identified during the 2026-04-11 maturity promotion of 14 concepts, 98
properties, and 19 vocabularies from draft to candidate. The dependency chain was
manually traced; this validator would automate that check going forward.
