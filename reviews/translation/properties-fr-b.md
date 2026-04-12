# French translation review: properties (batch B)

Files reviewed: complainant, conditionality_type, country, country_of_birth, court,
coverage_area, coverage_period_end, coverage_period_start, creation_date, currency,
cutoff_score, data_sources, date_of_birth, date_of_death, deceased, decision_basis,
decision_date, delivery_channel, delivery_date, delivery_location, delivery_status,
description, document_expiry_date, domicile, dwelling_type, education_level,
eligibility_decision_ref, eligibility_status, email_address, employment_status,
end_date, enrollment_date, enrollment_ref, enrollment_status, entitlement_ref,
entitlement_status, ethnic_group, event_date, event_date_estimated, event_location,
exit_date, exit_reason, expiry_date, failure_reason, family, family_name

---

## Systematic: fully de-accented translations (10 files)

Ten files have French definitions with no accented characters at all. Every word that
requires a diacritic is missing it. These are not individual typos; the text was almost
certainly generated or copied from a plain-ASCII source. Each file needs a full
re-accent pass.

Affected files and their stripped tokens:

### country

**File:** `schema/properties/country.yaml`
**Current:** `"Le pays, exprime sous forme de code ISO 3166-1 alpha-2 si possible."`
**Issue:** `exprime` missing accent.
**Proposed:** `"Le pays, exprimé sous forme de code ISO 3166-1 alpha-2 si possible."`
**Rationale:** `exprimé` is past participle; without the accent it reads as present tense ("expresses").

---

### country_of_birth

**File:** `schema/properties/country_of_birth.yaml`
**Current:** `"Le pays ou la personne est nee, exprime sous forme de code ISO 3166-1."`
**Issue:** Three stripped accents: `ou` (should be `où`), `nee` (should be `née`), `exprime` (should be `exprimé`).
**Proposed:** `"Le pays où la personne est née, exprimé sous forme de code ISO 3166-1."`
**Rationale:** `où` is required for locative/relative pronoun; `née` is feminine past participle; `exprimé` is past participle (same issue as `country`).

---

### coverage_period_end

**File:** `schema/properties/coverage_period_end.yaml`
**Current:** `"La date de fin de la periode couverte par ce droit."`
**Issue:** `periode` missing accent.
**Proposed:** `"La date de fin de la période couverte par ce droit."`
**Rationale:** Standard French noun; stripped accent is a plain spelling error.

---

### coverage_period_start

**File:** `schema/properties/coverage_period_start.yaml`
**Current:** `"La date de debut de la periode couverte par ce droit."`
**Issue:** `debut` (should be `début`) and `periode` (should be `période`).
**Proposed:** `"La date de début de la période couverte par ce droit."`
**Rationale:** Both require acute/circumflex accent; without them the words are misspelled.

---

### currency

**File:** `schema/properties/currency.yaml`
**Current:** `"Le code de devise ISO 4217 pour une valeur monetaire."`
**Issue:** `monetaire` missing accent.
**Proposed:** `"Le code de devise ISO 4217 pour une valeur monétaire."`
**Rationale:** Standard adjective; missing acute on the first `e`.

---

### date_of_death

**File:** `schema/properties/date_of_death.yaml`
**Current:** `"La date de deces de la personne."`
**Issue:** `deces` missing accent.
**Proposed:** `"La date de décès de la personne."`
**Rationale:** `décès` requires both an acute (é) and a grave (è); stripped form is unreadable as formal French.

---

### delivery_date

**File:** `schema/properties/delivery_date.yaml`
**Current:** `"La date a laquelle les biens ou services ont ete distribues au beneficiaire."`
**Issue:** Fully de-accented: `a` (à), `ete` (été), `distribues` (distribués), `beneficiaire` (bénéficiaire).
**Proposed:** `"La date à laquelle les biens ou services ont été distribués au bénéficiaire."`
**Rationale:** Every accented word is stripped; not readable as standard French.

---

### delivery_location

**File:** `schema/properties/delivery_location.yaml`
**Current:** `"Le lieu ou la distribution a eu lieu, comme un point de distribution, une ecole ou un etablissement de sante."`
**Issue:** `ou` (should be `où`), `ecole` (école), `etablissement` (établissement), `sante` (santé).
**Proposed:** `"Le lieu où la distribution a eu lieu, comme un point de distribution, une école ou un établissement de santé."`
**Rationale:** Fully de-accented; `où` is the relative/locative pronoun, not the conjunction `ou`.

---

### description

**File:** `schema/properties/description.yaml`
**Current:** `"Un resume en texte libre decrivant l'evenement, la situation ou l'enregistrement."`
**Issue:** `resume` (résumé), `decrivant` (décrivant), `evenement` (événement).
**Proposed:** `"Un résumé en texte libre décrivant l'événement, la situation ou l'enregistrement."`
**Rationale:** Three stripped accents; `résumé` in particular changes meaning without the accent (résumé = summary; resume = to resume).

---

### document_expiry_date

**File:** `schema/properties/document_expiry_date.yaml`
**Current:** `"La date a laquelle le document ou le justificatif representant le droit expire, qui peut differer de la periode du droit elle-meme."`
**Issue:** `a` (à), `representant` (représentant), `differer` (différer), `periode` (période), `elle-meme` (elle-même).
**Proposed:** `"La date à laquelle le document ou le justificatif représentant le droit expire, qui peut différer de la période du droit elle-même."`
**Rationale:** Five stripped accents; systematic de-accenting throughout the sentence.

---

### domicile

**File:** `schema/properties/domicile.yaml`
**Current:** `"Le lieu que la personne considere comme son domicile permanent, qui peut differer de l'adresse de son menage actuel."`
**Issue:** `considere` (considère), `differer` (différer), `menage` (ménage).
**Proposed:** `"Le lieu que la personne considère comme son domicile permanent, qui peut différer de l'adresse de son ménage actuel."`
**Rationale:** Three stripped accents; fully de-accented text.

---

### email_address

**File:** `schema/properties/email_address.yaml`
**Current:** `"Une adresse electronique par laquelle la personne peut etre contactee."`
**Issue:** `electronique` (électronique), `etre` (être), `contactee` (contactée).
**Proposed:** `"Une adresse électronique par laquelle la personne peut être contactée."`
**Rationale:** Three stripped accents.

---

### entitlement_ref

**File:** `schema/properties/entitlement_ref.yaml`
**Current:** `"Reference au droit que ce paiement ou bon remplit."`
**Issue 1:** `Reference` missing accent (should be `Référence`).
**Issue 2:** `remplit` (fills) should be `honore` per the project convention "remplir un droit" -> "honorer un droit".
**Proposed:** `"Référence au droit que ce paiement ou bon honore."`
**Rationale:** Both accent stripping and terminology convention violation in the same sentence.

---

### entitlement_status

**File:** `schema/properties/entitlement_status.yaml`
**Current:** `"L'etat du cycle de vie de cette instance de droit."`
**Issue:** `etat` missing accent.
**Proposed:** `"L'état du cycle de vie de cette instance de droit."`
**Rationale:** `état` requires a circumflex; without it the word is misspelled.

---

### expiry_date

**File:** `schema/properties/expiry_date.yaml`
**Current:** `"La date a laquelle cet enregistrement ou document expire ou devient invalide."`
**Issue:** `a` should be `à`.
**Proposed:** `"La date à laquelle cet enregistrement ou document expire ou devient invalide."`
**Rationale:** `à laquelle` is the standard relative construction; `a` without accent is the verb "has."

---

### failure_reason

**File:** `schema/properties/failure_reason.yaml`
**Current:** `"Une description de la raison pour laquelle le paiement a echoue, a ete retourne ou a ete rejete."`
**Issue:** `echoue` (échoué), `ete` (été, twice), `retourne` (retourné), `rejete` (rejeté).
**Proposed:** `"Une description de la raison pour laquelle le paiement a échoué, a été retourné ou a été rejeté."`
**Rationale:** Five stripped accents; fully de-accented text.

---

## Terminology: "éligibilité" should be "admissibilité" (4 files)

Per project convention, `éligibilité` / `éligible` must be replaced with
`admissibilité` / `admissible` throughout. Four files in this batch are affected.

### cutoff_score

**File:** `schema/properties/cutoff_score.yaml`
**Current:** `"Le score seuil en dessous ou au-dessus duquel un demandeur est considéré éligible."`
**Issue:** `éligible` should be `admissible`.
**Proposed:** `"Le score seuil en dessous ou au-dessus duquel un demandeur est considéré admissible."`
**Rationale:** Terminology convention; `admissible` is the internationally neutral policy term.

---

### decision_date

**File:** `schema/properties/decision_date.yaml`
**Current:** `"La date à laquelle la décision d'éligibilité a été enregistrée."`
**Issue:** `éligibilité` should be `admissibilité`.
**Proposed:** `"La date à laquelle la décision d'admissibilité a été enregistrée."`
**Rationale:** Terminology convention.

---

### eligibility_decision_ref

**File:** `schema/properties/eligibility_decision_ref.yaml`
**Current:** `"Référence à la décision d'éligibilité qui a autorisé cette inscription."`
**Issue:** `éligibilité` should be `admissibilité`.
**Proposed:** `"Référence à la décision d'admissibilité qui a autorisé cette inscription."`
**Rationale:** Terminology convention.

---

### eligibility_status

**File:** `schema/properties/eligibility_status.yaml`
**Current:** `"Le résultat de la détermination de l'éligibilité."`
**Issue:** `éligibilité` should be `admissibilité`.
**Proposed:** `"Le résultat de la détermination de l'admissibilité."`
**Rationale:** Terminology convention.

---

## Other issues

### court

**File:** `schema/properties/court.yaml`
**Current:** `"... ou un autre événement d'état civil ordonné par tribunal."`
**Issue:** Missing article before `tribunal`. English "court-ordered" becomes `ordonné par le tribunal` or `ordonné par un tribunal` in French; the bare noun is ungrammatical.
**Proposed:** `"... ou un autre événement d'état civil ordonné par un tribunal."`
**Rationale:** French requires an article before a common noun in this prepositional construction.

---

### enrollment_date

**File:** `schema/properties/enrollment_date.yaml`
**Current:** `"La date à laquelle l'inscription est devenue active et la prestation de services a été autorisée."`
**Issue:** "la prestation de services" (service delivery) does not match the English "benefit delivery." Services are not the same as benefits (prestations) in social protection terminology.
**Proposed:** `"La date à laquelle l'inscription est devenue active et la distribution des prestations a été autorisée."`
**Rationale:** Preserves the intended meaning (authorizing benefit delivery, not service provision).

---

### ethnic_group

**File:** `schema/properties/ethnic_group.yaml`
**Current:** `"L'ONU recommande des catégories définies au niveau national basées sur l'auto-identification..."`
**Issue:** English source says "UNSD" (UN Statistics Division), not "ONU" (UN as a whole). The recommendation is specific to the Statistics Division; attributing it to the UN in general is imprecise for a policy audience.
**Proposed:** `"La Division de statistique des Nations Unies recommande des catégories définies au niveau national basées sur l'auto-identification..."`
**Rationale:** Preserves the precision of the source; a policy officer may want to trace the recommendation to the correct body.

---

## No issues

complainant, coverage_area, creation_date, data_sources, date_of_birth, deceased,
decision_basis, delivery_channel, delivery_status, dwelling_type, education_level,
employment_status, end_date, enrollment_ref, enrollment_status, event_date,
event_date_estimated, event_location, exit_date, exit_reason, family, family_name
