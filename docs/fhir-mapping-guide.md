# FHIR Mapping Guide

This guide explains how to exchange PublicSchema disability and functioning data over FHIR R4. It covers the two common shapes (`Observation` for processed results, `QuestionnaireResponse` for raw survey captures), the LOINC coding system, and where PublicSchema stops and implementer choice begins.

Scope: the Washington Group functioning properties (WG-SS, WG-ES, WG/UNICEF CFM) and the anthropometric and pregnancy properties that SP programs commonly receive from health-side systems. Other PublicSchema properties map to FHIR using the same general patterns documented here.

## Why FHIR matters for social protection

Disability and functional-status data often originates in health systems: clinic intake, health facility registries, census disability modules that health ministries administer. When that data flows into social protection programs (cash transfer eligibility, disability allowance screening, referral pathways), the wire format is frequently FHIR.

PublicSchema does not prescribe FHIR. It documents the mapping so implementers building FHIR ingress or egress for SP systems can align their code to LOINC-coded observations without inventing their own representation.

## The two patterns

### Pattern 1: `Observation` (processed result)

Use this when you hold a single functioning result for a person, regardless of how it was captured. It is the right shape for records sitting in an SP beneficiary registry, an IPS-style summary, or a clinical system's problem/status list.

Shape:

```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "functional-status"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "<LOINC item code>",
      "display": "<LOINC display>"
    }]
  },
  "subject": { "reference": "Patient/<id>" },
  "effectiveDateTime": "<ISO 8601>",
  "valueCodeableConcept": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "<LOINC answer code>"
    }],
    "text": "<label, e.g. A lot of difficulty>"
  }
}
```

`Observation.code` carries the LOINC code for the WG item. `valueCodeableConcept` carries the graded response from the relevant LOINC answer list (for WG severity: `no_difficulty`, `some_difficulty`, `a_lot_of_difficulty`, `cannot_do`).

`Observation.category = functional-status` tells consumers this is a functioning observation, not a lab or vital sign. Some jurisdictions use `social-history` instead; both are valid in FHIR R4.

### Pattern 2: `QuestionnaireResponse` (raw survey capture)

Use this when you have the full form as it was administered: all items in the panel, item order preserved, skip logic traces intact. This is the right shape for census disability modules, MICS/DHS imports, and any case where you need an auditable record of the questionnaire instrument.

Shape:

```json
{
  "resourceType": "QuestionnaireResponse",
  "status": "completed",
  "questionnaire": "http://loinc.org/q/90151-4",
  "subject": { "reference": "Patient/<id>" },
  "authored": "<ISO 8601>",
  "item": [
    {
      "linkId": "<LOINC item code>",
      "answer": [{
        "valueCoding": {
          "system": "http://loinc.org",
          "code": "<LOINC answer code>"
        }
      }]
    }
  ]
}
```

`QuestionnaireResponse.questionnaire` points at the LOINC panel URL (WG-SS panel: `90151-4`). Each `item.linkId` is the LOINC code for a WG question. LOINC publishes WG-SS as a FHIR Questionnaire via its terminology server; consumers generally do not redefine the Questionnaire locally.

### Choosing between them

| You have | Use |
|---|---|
| A final "yes, they have difficulty walking" fact recorded once | `Observation` |
| The full filled-in WG-SS panel as administered | `QuestionnaireResponse` |
| Both (rare but valid) | Both, linked via `Observation.derivedFrom` |

SP systems ingesting WG-SS from a survey typically receive `QuestionnaireResponse` and derive per-item `Observation` resources downstream when eligibility rules need the individual answers.

## LOINC codes

### WG-SS panel

The WG-SS panel groups the six core items (seeing, hearing, walking/climbing steps, cognition/remembering, self-care, communication). LOINC publishes this panel under code `90151-4` and makes it available as a FHIR Questionnaire at `http://loinc.org/q/90151-4`.

### Item-level codes

LOINC assigns individual codes to each WG-SS, WG-ES, and CFM question. This guide does not enumerate them: LOINC's release schedule and the Washington Group's item additions both move faster than PublicSchema's publication cadence. Consumers needing the current codes should:

1. Pull them from LOINC's release CSV (free account required at loinc.org).
2. Or use LOINC's FHIR terminology server at `https://fhir.loinc.org` (requires the same account).
3. Or consult the WG's own LOINC crosswalk under the "Links to related resources" sections on `washingtongroup-disability.com/question-sets/`.

If no LOINC code exists for a given item (common for newer WG-ES and CFM items), implementers use a local `CodeSystem` and document the gap in their IG. Do not invent LOINC codes.

### WG severity answer list

The WG four-point response scale (No difficulty / Some difficulty / A lot of difficulty / Cannot do at all) has its own LOINC answer list. PublicSchema's `functional-difficulty-severity` vocabulary aligns one-to-one with that scale: consumers map the LOINC answer codes to `no_difficulty`, `some_difficulty`, `a_lot_of_difficulty`, `cannot_do`.

## IPS and national profiles

The HL7 International Patient Summary (IPS) does not currently define a functioning section. Countries and projects that need to carry WG data in an IPS-style document either:

- Extend the IPS Social History section with functional-status `Observation` resources, or
- Define a national profile with a dedicated disability section (example: the Australian AU Core IG, Swiss eCH disability extensions).

The PublicSchema functioning properties are compatible with both approaches. The mapping is driven by LOINC codes on the `Observation.code`, not by the IPS composition structure.

## Anthropometric and other health properties

The same `Observation` pattern applies to:

- `height`, `body_weight`: LOINC body height / body weight codes; `valueQuantity` with `cm` / `kg` UCUM units.
- `muac`: LOINC mid-upper arm circumference code; `valueQuantity` in `cm`.
- `stunting_status`, `wasting_status`, `underweight_status`, `acute_malnutrition_status`: one `Observation` per index, with LOINC answer lists for the WHO Child Growth Standards categories.
- `pregnancy_status`: LOINC `82810-3` (Pregnancy status) with the LOINC `LL4129-4` answer list. See `schema/vocabularies/pregnancy-status.yaml` for the alignment.

## Related resources

- FHIR R4 Observation: `http://hl7.org/fhir/R4/observation.html`
- FHIR R4 QuestionnaireResponse: `http://hl7.org/fhir/R4/questionnaireresponse.html`
- LOINC FHIR terminology server: `https://fhir.loinc.org`
- WG question sets: `https://www.washingtongroup-disability.com/question-sets/`
- [Interoperability & Mapping Guide](/docs/interoperability-guide/)
- [Selective Disclosure](/docs/selective-disclosure/)
