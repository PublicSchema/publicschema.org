# French Translation Review: SP/Delivery Concept Definitions

Scope: `definition.fr` in 16 concept YAML files under `schema/concepts/`.
Reviewer focus: register, SP terminology, calques, grammar, consistency, em dashes.

---

## Global findings (cross-file)

### 1. Missing accents throughout several files

Several files are missing all diacritics (accents, cedillas, etc.) -- every accented character is dropped. Affected files: `benefit-schedule.yaml`, `delivery-item.yaml`, `farm.yaml`, `hazard-event.yaml`, `in-kind-delivery.yaml`, `voucher.yaml`, `voucher-redemption.yaml`. All issues in those files stem from this root cause. They are called out individually below but the root fix is the same: re-encode or re-enter the French text with correct UTF-8 characters.

### 2. "éligibilité" vs "admissibilité" -- inconsistent across files

`enrollment.yaml` uses "éligible" / "l'éligibilité". `eligibility-decision.yaml` uses "d'éligibilité". "Admissibilité" / "admissible" is the internationally neutral SP term (used by the World Bank, FAO, UN agencies in French). "Éligibilité" is a widespread anglicism. The two terms appear inconsistently and neither file explains the choice. This should be standardised to "admissibilité" / "admissible" to match neutral Francophonie SP register.

### 3. "remplir un droit" (payment-event, in-kind-delivery, voucher) -- awkward calque

"remplir un droit" is a literal translation of "fulfill an entitlement". The natural French SP phrasing is "s'acquitter d'un droit" or "honorer un droit". Applies to: `payment-event.yaml`, `in-kind-delivery.yaml`, `voucher.yaml`.

---

## Per-file findings

---

### assessment-event.yaml

**No issues worth flagging.** Accents correct, SP terminology sound, no em dashes, natural phrasing.

---

### assessment-framework.yaml

**Issue 1**

- Current: `les tests de proxy des moyens`
- Source EN: `proxy means tests`
- Issue: Awkward literal calque. "Proxy means test" is a technical term. Its recognised French equivalent in SP literature is "test de substitution des ressources" or, more commonly in practice, left as "proxy means test (PMT)" on first use. "Tests de proxy des moyens" is neither natural French nor the accepted term.
- Proposed: `les tests de substitution des ressources (proxy means tests)`
- Rationale: Matches World Bank and UN Women French documentation. Keeps the English term in parentheses for practitioner recognition.

**Issue 2**

- Current: `les fiches d'évaluation communautaires`
- Source EN: `community scorecards`
- Issue: Acceptable, but "fiches de notation communautaires" or "cartes de performance communautaires" are more common in SP French documentation. Minor.
- Proposed: `les cartes de performance communautaires`
- Rationale: Closer to the term used in World Bank community scorecard guidance translated into French.

---

### benefit-schedule.yaml

**Root issue: all diacritics missing.** "definition", "specifie", "modalite", "frequence", "monetaire", "fournitures" should be "définition", "spécifie", "modalité", "fréquence", "monétaire", "fournitures".

**Issue 1 (once accents are fixed)**

- Current: `une definition au niveau du programme d'un flux de prestations`
- Source EN: `A program-level definition of a benefit stream`
- Issue: "flux de prestations" is a reasonable calque but "séquence de prestations" or "série de versements" is more natural in budgetary/SP French.
- Proposed: `Une définition au niveau du programme d'une série de prestations`
- Rationale: "Flux" suggests flow/stream in a more hydraulic sense; "série" matches how programme cycles are described in SP policy documents.

**Issue 2**

- Current: `par ex., un transfert monetaire mensuel et un kit de fournitures scolaires annuel`
- Issue: Accent on "monétaire" missing (root encoding issue). Also "annuel" agrees with "kit" (masculine) -- correct.
- Proposed: Restore `monétaire`.

---

### delivery-item.yaml

**Root issue: all diacritics missing.** "decrivant", "specifique", "Utilise", "representer", "alimentaires", "prestations composites" need accents throughout.

**Issue 1**

- Current: `ou plusieurs produits sont inclus a des quantites specifiees`
- Source EN: `where multiple commodities are included at specified quantities`
- Issue: "ou" should be "où" (relative adverb, not conjunction). This is a grammar error independent of the encoding problem.
- Proposed: `où plusieurs produits sont inclus à des quantités spécifiées`
- Rationale: "Où" is required here as a relative adverb introducing a clause. "Ou" means "or".

---

### eligibility-decision.yaml

**Issue 1**

- Current: `Une détermination formelle indiquant si un sujet satisfait aux critères d'un programme sur la base des conditions évaluées.`
- Source EN: `A formal determination of whether a subject meets a program's criteria based on assessed conditions.`
- Issue: Sound and grammatically correct. However, "éligibilité" is used later. See global finding on admissibilité/éligibilité.
- No structural change needed here beyond the terminology standardisation noted globally.

**Issue 2**

- Current: `Un événement d'évaluation peut produire plusieurs décisions d'éligibilité pour différents programmes.`
- Issue: "d'éligibilité" should be "d'admissibilité" to match recommended terminology. Otherwise well-formed.
- Proposed: `Un événement d'évaluation peut produire plusieurs décisions d'admissibilité pour différents programmes.`

---

### enrollment.yaml

**Issue 1**

- Current: `Le processus administratif d'inscription d'une personne ou d'un ménage éligible en tant que bénéficiaire actif d'un programme.`
- Source EN: `The administrative process of registering an eligible person or household as an active beneficiary of a program.`
- Issue: "inscription" for "enrollment" is correct SP French. "éligible" should be "admissible" per global finding.
- Proposed: `Le processus administratif d'inscription d'une personne ou d'un ménage admissible en tant que bénéficiaire actif d'un programme.`

**Issue 2**

- Current: `Les contraintes budgétaires et les limites de capacité signifient que l'éligibilité ne garantit pas l'inscription.`
- Issue: "l'éligibilité" should be "l'admissibilité".
- Proposed: `Les contraintes budgétaires et les limites de capacité font que l'admissibilité ne garantit pas l'inscription.`
- Rationale: "signifient que" is a calque of "mean that"; "font que" is more idiomatic French.

---

### entitlement.yaml

**Issue 1**

- Current: `Le droit référence à la fois l'inscription (qui) et le calendrier de prestations (ce qui a été promis).`
- Source EN: `The entitlement references both the enrollment (who) and the benefit schedule (what was promised).`
- Issue: "référence" used as a verb is an anglicism. French does not use "référencer" in this sense; the correct construction is "renvoie à" or "fait référence à".
- Proposed: `Le droit renvoie à la fois à l'inscription (qui) et au calendrier de prestations (ce qui a été promis).`
- Rationale: "Renvoie à" is the standard French construction for "references / points to" in data and policy texts.

**Issue 2**

- Current: `plusieurs droits peuvent exister pour la même inscription et des périodes chevauchantes`
- Source EN: `multiple entitlements may exist for the same enrollment and overlapping periods`
- Issue: "des périodes chevauchantes" is a calque; "des périodes qui se chevauchent" is more natural.
- Proposed: `plusieurs droits peuvent exister pour la même inscription et des périodes qui se chevauchent`

---

### farm.yaml

**Root issue: all diacritics missing.** "unite", "operationnelle", "agricole", "donnees", "exploitations", "fonciere", "sociale" need accents.

No additional issues beyond the encoding problem.

---

### grievance.yaml

**Issue 1**

- Current: `Le grief englobe les appels (demandes d'annulation d'une décision) et les plaintes`
- Source EN: `Grievance covers appeals (requests to reverse a decision) and complaints`
- Issue: "demandes d'annulation" translates "reverse" too strongly -- "annulation" implies cancellation, whereas an appeal typically requests revision or reconsideration. The standard SP term is "recours" or "demande de reconsidération".
- Proposed: `La réclamation englobe les recours (demandes de reconsidération d'une décision) et les plaintes`
- Rationale: "Recours" is the standard legal/administrative French for "appeal" in benefit adjudication contexts. Also, using "grief" as the subject noun is problematic: "grief" in French primarily means "grievance" in the emotional/legal sense and is less natural as the subject of a technical definition sentence. "La réclamation" (the record) better matches the EN "A record of...". The label "Grievance" can stay as the concept name, but the definition prose should use "réclamation" or "le présent enregistrement".

**Issue 2**

- Current: `d'insatisfaction ou de contestation`
- Source EN: `dissatisfaction or dispute`
- Issue: Acceptable, but in SP contexts "différend" is often preferred over "contestation" when referring to a formal dispute with a program. Minor.

---

### hazard-event.yaml

**Root issue: all diacritics missing.** "evenement", "bien-etre", "secheresses", "economiques", "definition", "interoperabilite" all need accents.

**Issue 1 (once accents fixed)**

- Current: `Aligne sur la definition large du Cadre de Sendai`
- Source EN: `Aligned with the Sendai Framework's broad definition of hazard`
- Issue: "Aligné" here is a participle used as a standalone clause, which reads as a sentence fragment in French. A relative clause is cleaner.
- Proposed: `Conforme à la définition élargie du Cadre de Sendai et compatible avec OASIS CAP v1.2 pour l'interopérabilité des alertes.`
- Rationale: "Conforme à" is the standard French for alignment with a framework. "Élargie" (broad) is more natural than "large" (which in French primarily means "wide" in a physical sense).

---

### in-kind-delivery.yaml

**Root issue: all diacritics missing.** "beneficiaire", "implique", "Couvre", "agricoles", "livraisons" need accents.

**Issue 1**

- Current: `Plusieurs livraisons en nature peuvent remplir un seul droit.`
- Issue: "remplir un droit" -- see global finding. Should be "honorer un seul droit" or "s'acquitter d'un seul droit".
- Proposed: `Plusieurs livraisons en nature peuvent s'acquitter d'un seul droit.`

**Issue 2**

- Current: `sans instrument financier implique`
- Issue: Accent missing ("impliqué"), plus this is a calque. More natural French: "sans recours à un instrument financier" or "sans intermédiaire financier".
- Proposed: `sans recours à un instrument financier`

---

### payment-event.yaml

**Issue 1**

- Current: `Couvre les canaux de virement bancaire, monnaie mobile, espèces, réseau d'agents et carte prépayée.`
- Source EN: `Covers bank transfer, mobile money, cash, agent network, and prepaid card channels.`
- Issue: The list items lack parallelism and articles. In the English, "channels" applies to the whole list. In the French, some items have articles and some don't, creating an uneven list. Also "monnaie mobile" is used; "argent mobile" is more widely used in Francophone Africa SP contexts.
- Proposed: `Couvre les canaux suivants: virement bancaire, argent mobile, espèces, réseau d'agents et carte prépayée.`
- Rationale: "Canaux suivants:" makes the list structure explicit. "Argent mobile" is the standard term in West/Central Africa SP French (UNCDF, World Bank Africa region documents).

**Issue 2**

- Current: `Plusieurs événements de paiement peuvent remplir un seul droit`
- Issue: "remplir un droit" -- see global finding.
- Proposed: `Plusieurs événements de paiement peuvent honorer un seul droit`

---

### program.yaml

**Issue 1**

- Current: `une agence de mise en oeuvre`
- Issue: Missing accent on "oeuvre" -- should be "oeuvre" or more precisely "uvre" needs the ligature: "mise en uvre" (with the oe ligature) is typographically correct in French, but "mise en oeuvre" without the ligature is widely accepted. However, the cedilla is correct here and this is acceptable in most publishing contexts. Minor.
- Proposed: `une agence de mise en uvre` (with oe ligature) or retain "oeuvre" as is -- this is low priority.

**Issue 2**

- Current: `qui fournit des prestations aux individus ou aux ménages éligibles`
- Issue: "éligibles" should be "admissibles" per global finding.
- Proposed: `qui fournit des prestations aux individus ou aux ménages admissibles selon des critères définis`

---

### referral.yaml

**Issue 1**

- Current: `Les orientations vont d'un simple partage d'information passif à une mise en lien active avec suivi.`
- Source EN: `Referrals span a spectrum from passive information sharing to active service linkage with follow-up.`
- Issue: "un simple partage d'information passif" -- "simple" and "passif" are both qualifying the same noun "partage", which is redundant and awkward. The EN uses "passive" to modify "information sharing", so the French should be "un simple partage passif d'informations" or cleaner: "un simple partage d'informations à une mise en relation active avec suivi".
- Proposed: `Les orientations vont d'un simple partage d'informations à une mise en relation active avec suivi.`
- Rationale: "Passif" is implicit when contrasted with "active"; the repetition weakens the sentence. "Mise en relation" is more natural than "mise en lien" in this context.

---

### voucher.yaml

**Root issue: all diacritics missing.** "echangeable", "emis", "beneficiaire", "execution", "electronique", "numerique", "expiration", "differer" need accents.

**Issue 1 (once accents fixed)**

- Current: `Un instrument echangeable emis au benefice d'un beneficiaire en execution d'un droit a prestation.`
- Source EN: `A redeemable instrument issued to a beneficiary as fulfillment of a benefit entitlement.`
- Issue: "émis au bénéfice d'un bénéficiaire" is awkward -- "bénéfice" and "bénéficiaire" clash. "Au bénéfice de" means "for the benefit of" and is correct legally, but the word collision is inelegant. Better: "délivré à un bénéficiaire".
- Proposed: `Un instrument échangeable délivré à un bénéficiaire en exécution d'un droit à prestation.`

**Issue 2**

- Current: `Un bon a un cycle de vie distinct: creation, emission, echange, expiration ou annulation.`
- Issue: "distinct" is a calque of "distinct" -- acceptable, but "propre" is more idiomatic: "un cycle de vie propre". Also the colon after "distinct" introduces a list, which requires a space before it in French typography (a non-breaking space before ":"). This is a typography rule, not just style. The missing accents on "création", "émission", "échange", "expiration" are the encoding issue.
- Proposed: `Un bon a un cycle de vie propre : création, émission, échange, expiration ou annulation.`

**Issue 3**

- Current: `Plusieurs bons peuvent remplir un seul droit`
- Issue: "remplir un droit" -- see global finding.
- Proposed: `Plusieurs bons peuvent honorer un seul droit`

---

### voucher-redemption.yaml

**Root issue: all diacritics missing.** All accented characters absent throughout.

**Issue 1**

- Current: `Un enregistrement d'une transaction de canje unique contre un bon.`
- Issue: "canje" is Spanish, not French. The French for "redemption" in the voucher/financial instrument sense is "encaissement" or "utilisation", and for voucher programs specifically "échange" or "rachat". "Canje" has no place in French text.
- Proposed: `Un enregistrement d'une transaction d'échange unique contre un bon.`
- Rationale: "Transaction d'échange" is the standard French for voucher redemption in WFP and humanitarian logistics French documentation.

**Issue 2**

- Current: `Chaque VoucherRedemption capture une visite chez un vendeur ou agent ou une partie ou la totalite de la valeur du bon ou des produits auxquels il donne droit a ete collectee.`
- Issue: "ou" used three times in quick succession, creating ambiguity. The first "ou" (vendeur ou agent) is a disjunction. The second and third "ou" (ou une partie ou la totalite) try to construct "where part or all of... was collected" but the sentence structure is broken. "Où" (relative adverb with accent) is needed for the relative clause. Also "a ete collectee" needs accents ("a été collectée").
- Proposed: `Chaque VoucherRedemption enregistre une visite chez un vendeur ou un agent, lors de laquelle une partie ou la totalité de la valeur du bon ou des produits auxquels il donne droit a été collectée.`
- Rationale: "lors de laquelle" makes the relative clause unambiguous and reads naturally. "Enregistre" (records) is more active than "capture" (calque).

**Issue 3**

- Current: `Pour le canje incremental (courant dans les programmes de bons de valeur du PAM)`
- Issue: "canje" again (Spanish). "PAM" is correct (Programme Alimentaire Mondial). "Incrémental" needs the accent. "Courant dans" is a calque of "common in"; "fréquent dans" is more natural.
- Proposed: `Pour l'échange incrémental (fréquent dans les programmes de bons de valeur du PAM)`

---

## Summary of priority fixes

| Priority | File(s) | Issue |
|---|---|---|
| Critical | `voucher-redemption.yaml` | "canje" (Spanish word) in French text, broken relative clause |
| High | `benefit-schedule.yaml`, `delivery-item.yaml`, `farm.yaml`, `hazard-event.yaml`, `in-kind-delivery.yaml`, `voucher.yaml`, `voucher-redemption.yaml` | All diacritics missing (encoding) |
| High | `enrollment.yaml`, `eligibility-decision.yaml`, `program.yaml` | "éligible/éligibilité" should be "admissible/admissibilité" |
| High | `payment-event.yaml`, `in-kind-delivery.yaml`, `voucher.yaml` | "remplir un droit" calque |
| Medium | `entitlement.yaml` | "référence" as a verb (anglicism); "périodes chevauchantes" calque |
| Medium | `assessment-framework.yaml` | "tests de proxy des moyens" (non-standard term) |
| Medium | `grievance.yaml` | "annulation" for "reverse"; "grief" as prose subject noun |
| Medium | `referral.yaml` | Redundant "simple...passif" |
| Medium | `hazard-event.yaml` | "Aligné" as fragment; "large" for "broad" |
| Low | `voucher.yaml` | Typography: space before colon in list; "distinct" vs "propre" |
| Low | `program.yaml` | "oeuvre" ligature (very minor) |
