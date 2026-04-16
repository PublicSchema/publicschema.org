# Interview Metadata

Every Profile record carries administrative context about how the data was collected. This guide explains how form authors should populate the key interview metadata properties.

## `observation_date`

The date the data was collected. For most field forms, this is today's date (auto-populated at form open or submission). When data entry happens after the fact (e.g., paper-to-digital transcription), the observation_date should be the original collection date, not the transcription date.

## `performed_by`

The agent who performed the data collection. This can be:

- **A reference to an Agent record** (Person or Organization) when the enumerator is a known, registered user in the system.
- **A display name string** when the system does not maintain an enumerator registry.

Form systems that authenticate enumerators should populate this automatically from the logged-in user. Systems without authentication can present a text field.

## `instrument_used`

A reference to the Instrument record describing the data-collection tool. For standard instruments (WG-SS, SMART, WFP FCS), use the canonical instrument identifier from the PublicSchema instrument registry.

## `administration_mode`

How the instrument was administered. Values from the `administration-mode` vocabulary:

- `self`: the subject completed the instrument themselves
- `proxy`: a caregiver or household member answered on behalf of the subject
- `assisted`: the subject answered with assistance from an enumerator
- `mixed`: some items were self-reported, others proxy-reported

For child instruments (CFM 2-4, CFM 5-17), the mode is always `proxy` since the caregiver responds.

## `respondent` and `respondent_relationship`

When the administration mode is `proxy` or `mixed`, record who responded and their relationship to the subject. `respondent` is a reference to or description of the person who answered. `respondent_relationship` uses the `relationship-type` vocabulary (e.g., parent, spouse, caregiver).
