# French translation review: properties r–w

Files reviewed: `recognizing_parent`, `record_id`, `record_type`, `redeemable_by`, `redeemed_by`,
`redemption_agent`, `redemption_date`, `referral_date`, `referral_reason`, `referral_status`,
`referred_person`, `referring_program`, `register_authority`, `register_number`, `registrar`,
`registration_date`, `registration_location`, `registration_number`, `registration_status`,
`registration_type`, `relationship_type`, `religion`, `resolution_date`, `role`, `schedule_ref`,
`scoring_method`, `serial_number`, `severity`, `sex`, `sex_at_birth`, `start_date`,
`status_in_employment`, `street_address`, `subject_person`, `submission_date`,
`targeting_approach`, `transaction_reference`, `triggering_event`, `type_of_marriage`,
`unit_of_measure`, `valid_until`, `vital_event`, `voucher_format`, `voucher_ref`,
`voucher_status`, `weight`, `weight_at_birth`, `witnesses`

---

## Stripped accents (systematic batch issue)

The following files have French definitions entirely stripped of accents. Every accented character (é, è, ê, à, â, î, ô, û, ù, ç, œ) has been replaced with its unaccented ASCII equivalent. This is incorrect and must be fixed in all of them.

### `redeemable_by`

| | |
|---|---|
| **Current** | `La personne ou le groupe autorise a echanger ce bon au nom du beneficiaire.` |
| **Source** | `The person or group authorized to redeem this voucher on behalf of the beneficiary.` |
| **Issue** | Stripped accents throughout: `autorisé`, `à`, `échanger`, `bénéficiaire`. |
| **Proposed** | `La personne ou le groupe autorisé à échanger ce bon au nom du bénéficiaire.` |

### `redeemed_by`

| | |
|---|---|
| **Current** | `La personne qui a presente le bon pour l'echange.` |
| **Source** | `The person who presented the voucher for redemption.` |
| **Issue** | Stripped accents: `présenté`, `l'échange`. |
| **Proposed** | `La personne qui a présenté le bon pour l'échange.` |

### `redemption_agent`

| | |
|---|---|
| **Current** | `Le commercant, vendeur ou agent qui a accepte le bon pour l'echange.` |
| **Source** | `The merchant, vendor, or agent who accepted the voucher for redemption.` |
| **Issue** | Stripped accents: `commerçant`, `accepté`, `l'échange`. |
| **Proposed** | `Le commerçant, vendeur ou agent qui a accepté le bon pour l'échange.` |

### `redemption_date`

| | |
|---|---|
| **Current** | `La date a laquelle le bon a ete echange aupres d'un vendeur ou d'un agent.` |
| **Source** | `The date on which the voucher was redeemed at a vendor or agent.` |
| **Issue** | Stripped accents: `à laquelle`, `été`, `échangé`, `auprès`. |
| **Proposed** | `La date à laquelle le bon a été échangé auprès d'un vendeur ou d'un agent.` |

### `role`

| | |
|---|---|
| **Current** | `Le role de la personne au sein du groupe (par exemple, chef, conjoint, enfant, dependant).` |
| **Source** | `The role of the person within the group (e.g., head, spouse, child, dependent).` |
| **Issue** | Stripped accents: `rôle`, `dépendant`. Note also: `chef` translates EN `head` but in household contexts `chef de ménage` is the established term; abbreviating to `chef` is ambiguous. |
| **Proposed** | `Le rôle de la personne au sein du groupe (par exemple, chef de ménage, conjoint, enfant, dépendant).` |
| **Rationale** | Restores accents; clarifies `chef` with established household head term. |

### `serial_number`

| | |
|---|---|
| **Current** | `Un identifiant public pour le bon, imprime sur le document physique ou communique par SMS ou application.` |
| **Source** | `A public identifier for the voucher, printed on the physical document or communicated via SMS or application.` |
| **Issue** | Stripped accents: `imprimé`, `communiqué`. |
| **Proposed** | `Un identifiant public pour le bon, imprimé sur le document physique ou communiqué par SMS ou application.` |

### `severity`

| | |
|---|---|
| **Current** | `La gravite observee ou attendue de l'impact de l'evenement.` |
| **Source** | `The observed or expected severity of the event's impact.` |
| **Issue** | Stripped accents: `gravité`, `observée`, `l'événement`. |
| **Proposed** | `La gravité observée ou attendue de l'impact de l'événement.` |

### `street_address`

| | |
|---|---|
| **Current** | `Le nom de la rue, le numero et tout identifiant d'appartement ou de batiment.` |
| **Source** | `The street name, number, and any apartment or building identifiers.` |
| **Issue** | Stripped accents: `numéro`, `bâtiment`. |
| **Proposed** | `Le nom de la rue, le numéro et tout identifiant d'appartement ou de bâtiment.` |

### `unit_of_measure`

| | |
|---|---|
| **Current** | `L'unite dans laquelle la quantite est exprimee.` |
| **Source** | `The unit in which the quantity is expressed.` |
| **Issue** | Stripped accents: `L'unité`, `quantité`, `exprimée`. |
| **Proposed** | `L'unité dans laquelle la quantité est exprimée.` |

### `voucher_format`

| | |
|---|---|
| **Current** | `La forme physique ou numerique du bon.` |
| **Source** | `The physical or digital form of the voucher.` |
| **Issue** | Stripped accent: `numérique`. |
| **Proposed** | `La forme physique ou numérique du bon.` |

### `voucher_ref`

| | |
|---|---|
| **Current** | `Une reference au bon auquel cet enregistrement se rapporte.` |
| **Source** | `A reference to the voucher that this record relates to.` |
| **Issue** | Stripped accent: `référence`. |
| **Proposed** | `Une référence au bon auquel cet enregistrement se rapporte.` |

### `voucher_status`

| | |
|---|---|
| **Current** | `L'etat du cycle de vie du bon.` |
| **Source** | `The lifecycle state of the voucher.` |
| **Issue** | Stripped accent: `L'état`. |
| **Proposed** | `L'état du cycle de vie du bon.` |

---

## Terminology

### `valid_until` — "éligibilité" should be "admissibilité"

| | |
|---|---|
| **File** | `valid_until.yaml` |
| **Current** | `La date jusqu'à laquelle la décision d'éligibilité reste valide.` |
| **Source** | `The date until which the eligibility decision remains valid.` |
| **Issue** | Project convention: `éligibilité` → `admissibilité`. Consistent with the convention applied elsewhere (e.g. `admissibilité` in non-reviewed files). |
| **Proposed** | `La date jusqu'à laquelle la décision d'admissibilité reste valide.` |

### `targeting_approach` — "éligibles" should be "admissibles"

| | |
|---|---|
| **File** | `targeting_approach.yaml` |
| **Current** | `La méthode utilisée pour identifier les bénéficiaires éligibles.` |
| **Source** | `The method used to identify eligible beneficiaries.` |
| **Issue** | Same convention: `éligibles` → `admissibles`. |
| **Proposed** | `La méthode utilisée pour identifier les bénéficiaires admissibles.` |

### `referral_status` — "complétée" is Quebec French

| | |
|---|---|
| **File** | `referral_status.yaml` |
| **Current** | `L'état actuel de l'orientation (en attente, acceptée, refusée, complétée).` |
| **Source** | `The current state of the referral (pending, accepted, declined, completed).` |
| **Issue** | `Complétée` in the sense of "finished/closed" is a Québécois usage. In internationally neutral French the appropriate term is `terminée` or `conclue`. |
| **Proposed** | `L'état actuel de l'orientation (en attente, acceptée, refusée, terminée).` |

### `registration_location` — "registre" for an office

| | |
|---|---|
| **File** | `registration_location.yaml` |
| **Current** | `Souvent un registre municipal ou de district, distinct du lieu où l'événement s'est produit.` |
| **Source** | `Often a municipal or district-level registry distinct from the place of occurrence.` |
| **Issue** | `Registre` in French designates the ledger/book, not the institution. The EN `registry` means the office. The correct term is `bureau d'état civil` (or `bureau d'enregistrement`). |
| **Proposed** | `Le bureau d'état civil où l'événement a été enregistré. Souvent un bureau municipal ou de district, distinct du lieu où l'événement s'est produit.` |
| **Rationale** | Preserves the first sentence (already correct) and fixes the calque in the second. |

### `type_of_marriage` — "ruptures" for legal terminations

| | |
|---|---|
| **File** | `type_of_marriage.yaml` |
| **Current** | `la manière dont les ruptures ultérieures sont traitées.` |
| **Source** | `how subsequent terminations are handled.` |
| **Issue** | `Rupture` is colloquial (a breakup). In civil law context, "termination of a marriage" is `dissolution` (divorce, annulation, décès). `Ruptures` undersells the legal register. |
| **Proposed** | `la manière dont les dissolutions ultérieures sont traitées.` |

---

## Register / naturalness

### `start_date` — "effectif" is awkward

| | |
|---|---|
| **File** | `start_date.yaml` |
| **Current** | `La date à laquelle ceci est devenu effectif.` |
| **Source** | `The date on which this became effective.` |
| **Issue** | `Est devenu effectif` is a literal calque of "became effective". The natural French administrative phrase is `est entré en vigueur` (for legal/regulatory validity) or `a pris effet` (for operational entries). The Spanish translation already uses the more idiomatic `entró en vigor`. |
| **Proposed** | `La date à laquelle ceci a pris effet.` |
| **Rationale** | `A pris effet` is concise, idiomatic, and domain-neutral; `est entré en vigueur` is also correct but implies a more formal legal instrument. |

### `subject_person` — "détient la relation" is unnatural

| | |
|---|---|
| **File** | `subject_person.yaml` |
| **Current** | `La personne qui détient la relation décrite (le sujet de l'énoncé de relation).` |
| **Source** | `The person who holds the described relationship (the subject of the relationship statement).` |
| **Issue** | `Détenir une relation` is not natural French. One does not "hold" a relationship in French; one "entretient" or "est partie à" one. The parenthetical is also technical/developer-facing rather than policy-officer language. |
| **Proposed** | `La personne qui entretient la relation décrite (le sujet de l'énoncé de relation).` |
| **Rationale** | `Entretenir une relation` is idiomatic. The parenthetical is preserved as it mirrors the EN. |

### `record_id` — "à portée externe" is awkward

| | |
|---|---|
| **File** | `record_id.yaml` |
| **Current** | `distinct de toute référence métier à portée externe` |
| **Source** | `distinct from any externally meaningful business reference` |
| **Issue** | `À portée externe` is not a standard French phrase. `Externe` alone, or `visible en dehors du système`, would be clearer. |
| **Proposed** | `distinct de toute référence métier externe` |
| **Rationale** | `Référence métier externe` is concise and clear for a policy reader. |

---

## Clean files (no issues)

`recognizing_parent`, `record_type`, `referral_date`, `referral_reason`, `referred_person`,
`referring_program`, `register_authority`, `register_number`, `registrar`, `registration_date`,
`registration_number`, `registration_status`, `registration_type`, `relationship_type`,
`religion`, `resolution_date`, `schedule_ref`, `scoring_method`, `sex`, `sex_at_birth`,
`status_in_employment`, `submission_date`, `transaction_reference`, `triggering_event`,
`vital_event`, `weight`, `weight_at_birth`, `witnesses`
