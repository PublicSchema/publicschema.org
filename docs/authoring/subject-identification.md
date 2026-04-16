# Subject Identification Patterns

Profile records (FoodSecurityProfile, FunctioningProfile, AnthropometricProfile, SocioEconomicProfile) reference their subject via the `subject` property. Three patterns cover the range of identification scenarios in field collection.

## Pattern 1: Reference

The subject is a Person or Group record that already exists in the system. The form stores a reference (identifier or URI).

**When to use:** registration-linked surveys, follow-up visits, any context where subjects are pre-enrolled.

```yaml
subject: "person/ETH-PSNP-2024-00142"
```

## Pattern 2: Inline

The subject is described inline on the Profile record itself with enough identifying information to link later (name, date of birth, location). No pre-existing Person record is required.

**When to use:** community screening, first-contact registration, mobile data collection in areas without prior enrollment.

## Pattern 3: Anonymous

The subject is not identified. The Profile captures observation data without linking it to a named individual.

**When to use:** population-level surveys (DHS, MICS, SMART), research, any context where individual identification is not needed or not appropriate.

```yaml
subject: null
```

## Choosing a pattern

| Context | Pattern | Notes |
|---|---|---|
| Follow-up visit in a program | Reference | Subject must exist before the form opens |
| Community MUAC screening | Inline | Create Person record from inline data after screening |
| SMART nutrition survey | Anonymous | No individual follow-up; data is aggregated |
| Household registration survey | Reference or Inline | Depends on whether the household was pre-registered |
