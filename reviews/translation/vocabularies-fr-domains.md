# French vocabulary review — crvs + sp

## Summary
- Files reviewed: 26
- Files with issues: 14
- Files clean: 12
- Em dashes found: 0

---

## Per-file findings

### schema/vocabularies/crvs/adoption-type.yaml

No changes proposed. All French text is accurate, diacritics are correct, no em dashes, terminology is appropriate for a francophone civil-law audience.

---

### schema/vocabularies/crvs/annotation-type.yaml

No changes proposed. Translations are accurate, diacritics are correct, canonical civil-registration vocabulary is used throughout.

---

### schema/vocabularies/crvs/birth-attendant.yaml

#### Top-level definition
No change needed.

#### values

- `traditional_birth_attendant`.definition — current: `"Un membre de la communauté ou un praticien traditionnel qui fournit une assistance à l'accouchement, généralement sans formation médicale formelle."` — proposed: `"Un membre de la communauté ou un praticien traditionnel qui apporte une assistance à l'accouchement, généralement sans formation médicale formelle."` — reason: `fournit une assistance` is serviceable but `apporte une assistance` is the more natural collocate in French; minor but worth aligning. (Low priority: acceptable either way.)

No mandatory changes. File is substantively clean.

---

### schema/vocabularies/crvs/birth-type.yaml

No changes proposed. All translations are accurate and natural. Plural forms (Jumeaux, Triplés, Quadruplés, Quintuplés) are correct.

---

### schema/vocabularies/crvs/cause-of-death-method.yaml

#### Top-level definition
- Current: `"La méthode utilisée pour déterminer la cause du décès. Dans de nombreux contextes à faibles revenus, la cause du décès est établie par autopsie verbale plutôt que par certification médicale; les utilisateurs doivent savoir comment une cause rapportée a été déterminée."`
- Proposed: `"La méthode utilisée pour déterminer la cause du décès. Dans de nombreux contextes à ressources limitées, la cause du décès est établie par autopsie verbale plutôt que par certification médicale; les utilisateurs doivent savoir comment une cause déclarée a été déterminée."`
- Reason: `contextes à faibles revenus` is a calque of "low-income settings" and reads awkwardly in French. The standard neutral French expression is `contextes à ressources limitées`. Additionally, `cause rapportée` is a calque of "reported cause"; `cause déclarée` is more idiomatic in French public health.

#### values

No other mandatory changes. `Déclaration non professionnelle` for `lay_reporting` and its definition are accurate and natural.

---

### schema/vocabularies/crvs/certificate-document-type.yaml

No changes proposed. Terminology (`acte de naissance`, `acte de décès`, `acte de mariage`) correctly uses canonical état civil vocabulary.

---

### schema/vocabularies/crvs/certificate-format.yaml

#### Top-level definition
- Current: `"Le format d'un document de certificat d'état civil. Distinct du type d'événement qu'il atteste: une copie intégrale reproduit l'acte entier y compris ses mentions marginales, un extrait n'en contient qu'un résumé."`
- Proposed: No change needed. The colon usage is correct and matches the rule (colon, not em dash). Text is accurate.

No changes proposed.

---

### schema/vocabularies/crvs/civil-status-record-type.yaml

No changes proposed. Canonical terms (`acte de naissance`, `acte de décès`, `acte de mariage`, `jugement supplétif`, `décision judiciaire`) are correctly used throughout.

---

### schema/vocabularies/crvs/family-register-status.yaml

#### Top-level definition
- Current: `"Statut du cycle de vie d'un registre familial. Indique si le registre est actuellement actif, a été clôturé, ou a été scindé ou fusionné avec d'autres registres suite à des événements d'état civil."`
- Proposed: No change needed. Accurate and natural.

#### values

- `closed`.definition — current: `"Le registre a été clôturé, généralement parce que tous les membres sont décédés ou sont partis."` — proposed: `"Le registre a été clôturé, généralement parce que tous ses membres sont décédés ou ont quitté l'unité familiale."` — reason: `sont partis` is colloquial and vague. `ont quitté l'unité familiale` is more precise and appropriate for a policy audience. (Medium priority.)

---

### schema/vocabularies/crvs/manner-of-death.yaml

#### Top-level definition
- Current: `"La manière dont un décès est survenu, distincte de sa cause médicale sous-jacente. Aligné sur la classification OMS/CIM de la manière du décès."`
- Proposed: No change needed. `OMS/CIM` is the standard French abbreviation for WHO/ICD. Accurate.

#### values

- `intentional_self_harm`.label — current: `Lésions auto-infligées intentionnellement` — proposed: `Lésions auto-infligées` — reason: The WHO/ICD Manner of Death French designation is simply `Lésions auto-infligées`. Adding `intentionnellement` is redundant since "auto-infligées" in this medical context already means intentional; ICD-10 French uses the shorter form. The definition correctly adds `(suicide)` for clarity.

- `pending_investigation`.definition — current: `"La manière du décès n'a pas encore été déterminée parce qu'une enquête est en cours."` — proposed: `"La manière du décès n'a pas encore été établie, une enquête étant en cours."` — reason: `parce que` followed by `est en cours` is correct but somewhat blunt. The participial construction `une enquête étant en cours` is more idiomatic in formal French administrative writing. (Low priority: both are acceptable.)

- `could_not_be_determined`.definition — current: `"Après enquête, la manière du décès n'a pas pu être établie."` — proposed: No change. Accurate and concise.

---

### schema/vocabularies/crvs/marriage-type.yaml

#### values

- `civil`.definition — current: `"Mariage contracté devant un officier de l'état civil en droit laïque."` — proposed: `"Mariage contracté devant un officier de l'état civil sous le régime du droit civil."` — reason: `en droit laïque` is a literal translation of "under secular law" that is unusual in French legal writing. The standard expression is `sous le régime du droit civil` (or simply `selon le droit civil`). In French civil-law countries the contrast is between `mariage civil` and `mariage religieux`, not between secular and non-secular law as such.

- `common_law`.label — current: `Union de fait` — proposed: No change. `Union de fait` is the standard internationally neutral French term for a common-law relationship (used in France, Belgium, Canada, and Francophone Africa).

---

### schema/vocabularies/crvs/parental-role.yaml

No changes proposed. Terminology (`mère biologique`, `père biologique`, `mère légale`, `père légal`, `mère adoptive`, `père adoptif`, `mère porteuse`, `parents d'intention`) is accurate, canonical, and internationally neutral.

---

### schema/vocabularies/crvs/place-type.yaml

#### Top-level definition
- Current: `"La catégorie de lieu où un événement d'état civil (naissance ou décès) s'est produit. Distinct du lieu spécifique: saisit le type (établissement de santé, domicile, etc.) plutôt que le lieu nommé."`
- Proposed: `"La catégorie de lieu où un événement d'état civil (naissance ou décès) s'est produit. Distinct du lieu spécifique: indique le type (établissement de santé, domicile, etc.) plutôt que le lieu nommé."`
- Reason: `saisit` in this context is a calque of English "captures" in its technical/data sense. The cross-file consistency rule requires `Recueille` or `Enregistre` when translating "captures/records". However, the definition is referring to what the vocabulary describes conceptually (not what a system does at data entry), so `indique` is the more appropriate neutral term here.

#### values

No other changes needed.

---

### schema/vocabularies/crvs/registration-status.yaml

No changes proposed. `officier d'état civil` is the correct canonical term for "registrar" in French civil law. All status labels and definitions are accurate.

---

### schema/vocabularies/crvs/registration-type.yaml

No changes proposed. `Courant`, `Tardif`, `Ordonné par le tribunal`, `Reconstitution` are all appropriate and accurate.

---

### schema/vocabularies/sp/benefit-frequency.yaml

No changes proposed. Frequency labels (`Quotidien`, `Hebdomadaire`, `Mensuel`, `Trimestriel`, `Semestriel`, `Annuel`, `Ponctuel`) are correct standard French. `Selon les besoins` is natural. `Personnalisé` for `custom` is acceptable and clear.

---

### schema/vocabularies/sp/benefit-modality.yaml

#### Top-level definition
- Current: `La forme sous laquelle une prestation ou un droit est versé à un bénéficiaire.`
- Proposed: `La forme sous laquelle une prestation ou un droit est remis à un bénéficiaire.`
- Reason: `versé` means "paid out" (monetary payment) and carries a financial connotation. A benefit can be in-kind, a service, or a fee waiver, so `remis` (delivered/handed over) is more form-neutral. (Medium priority.)

#### values

- `insurance`.definition — current: `Inscription ou subvention d'un régime d'assurance (santé, récolte, social) comme prestation fournie au bénéficiaire.` — proposed: `Inscription à un régime d'assurance ou subvention de celui-ci (santé, récolte, social) comme prestation fournie au bénéficiaire.` — reason: The current French reads awkwardly because `ou subvention` hangs loosely after the preposition `d'`. Restructuring clarifies that both inscription and subvention apply to the same regime.

No em dashes found.

---

### schema/vocabularies/sp/conditionality-type.yaml

#### Top-level definition
- Current: `"Catégories décrivant si et comment un programme de protection sociale exige des bénéficiaires qu'ils remplissent des conditions comportementales pour recevoir ou continuer à recevoir des prestations."`
- Proposed: `"Catégories décrivant si et comment un programme de protection sociale exige des bénéficiaires qu'ils satisfassent à des conditions comportementales pour recevoir ou continuer à recevoir des prestations."`
- Reason: Per cross-file consistency rules, `remplissent des conditions` should be replaced with the more precise `satisfassent à des conditions`. The rule specifies `remplir un droit` (honorer) should not be used for "fulfill an entitlement", but more broadly `remplir des conditions` is weaker than `satisfaire à des conditions` in formal French administrative writing.

#### values

- `unconditional`.definition — current: `"Les prestations sont fournies sans exiger que le bénéficiaire remplisse des conditions comportementales."` — proposed: `"Les prestations sont accordées sans exiger que le bénéficiaire satisfasse à des conditions comportementales."` — reason: Same as above (`remplisse` → `satisfasse à`). Also, `accordées` is more natural than `fournies` for abstract entitlements.

- `conditional`.definition — current: `"Les prestations exigent que le bénéficiaire remplisse des conditions comportementales spécifiées, telles que la fréquentation scolaire, les bilans de santé ou la participation à des formations."` — proposed: `"Les prestations sont soumises à la satisfaction, par le bénéficiaire, de conditions comportementales définies, telles que la fréquentation scolaire, les bilans de santé ou la participation à des formations."` — reason: Avoids `remplisse des conditions`. The restructured phrase is the standard French administrative construction for conditionality.

- `soft_conditional`.definition — current: `"Les conditions sont encouragées et suivies mais le non-respect n'entraîne pas la suspension ou la fin des prestations."` — proposed: No change needed. Accurate and natural.

- `labelled`.label — current: `Étiqueté` — proposed: `Affecté à un usage désigné` — reason: `Étiqueté` is a direct calque of "labelled" and is not a recognized term in French social protection policy. The concept (transfers designated for a purpose but not strictly enforced) is typically described as `transfert affecté` or `prestation à usage désigné`. The longer label is acceptable since there is no single-word equivalent in canonical French SP vocabulary. Alternative shorter option: `À usage désigné`. (Medium priority.)

- `labelled`.definition — current: `"Les prestations sont désignées pour un usage spécifique (par ex., alimentation, éducation) mais les dépenses ne sont pas strictement contrôlées ou vérifiées."` — proposed: `"Les prestations sont affectées à un usage précis (par ex., alimentation, éducation) mais les dépenses ne sont pas strictement contrôlées ni vérifiées."` — reason: `désignées` is fine but `affectées` is the more standard French term for earmarking. Also `ou vérifiées` should be `ni vérifiées` after a negative construction with `pas` for grammatical correctness.

---

### schema/vocabularies/sp/eligibility-status.yaml

#### Top-level definition
- Current: `Les résultats possibles d'une détermination formelle d'éligibilité à un programme ou service.`
- Proposed: `Les résultats possibles d'une détermination formelle d'admissibilité à un programme ou service.`
- Reason: Cross-file consistency rule: `eligibility` → `admissibilité` (not `éligibilité`).

#### values

- `eligible`.label — current: `Éligible` — proposed: `Admissible` — reason: Cross-file consistency rule: `eligibility` → `admissibilité`; the adjective follows as `admissible`.

- `eligible`.definition — current: `Le sujet satisfait aux critères du programme et est approuvé pour recevoir des prestations.` — proposed: `Le sujet satisfait aux critères du programme et est admis à recevoir des prestations.` — reason: `admis à` is more consistent with the `admissibilité` term family.

- `ineligible`.label — current: `Non éligible` — proposed: `Non admissible` — reason: Same consistency rule.

- `ineligible`.definition — current: `Le sujet ne satisfait pas aux critères du programme et n'est pas approuvé pour recevoir des prestations.` — proposed: `Le sujet ne satisfait pas aux critères du programme et n'est pas admis à recevoir des prestations.` — reason: Consistency with `admissibilité` term family.

- `pending`.definition — current: `La détermination de l'éligibilité est en cours et une décision finale n'a pas encore été rendue.` — proposed: `La détermination de l'admissibilité est en cours et une décision finale n'a pas encore été rendue.` — reason: Consistency rule.

- `under_review`.definition — current: `L'évaluation de l'éligibilité est activement examinée par un agent de terrain ou un organe d'examen.` — proposed: `L'évaluation de l'admissibilité est activement conduite par un agent de terrain ou un organe d'examen.` — reason: Consistency rule for `éligibilité` → `admissibilité`. Also, `examinée` is redundant with `examen` (organe d'examen); `conduite` avoids the repetition.

- `conditional`.definition — current: `Le sujet est éligible à condition de remplir des conditions supplémentaires, telles que la fréquentation scolaire ou les examens médicaux.` — proposed: `Le sujet est admissible à condition de satisfaire à des conditions supplémentaires, telles que la fréquentation scolaire ou les examens médicaux.` — reason: Two issues: `éligible` → `admissible` (consistency rule); `remplir des conditions` → `satisfaire à des conditions` (consistency rule against `remplir`).

---

### schema/vocabularies/sp/enrollment-exit-reason.yaml

#### Top-level definition
- Current: `"La raison pour laquelle une inscription a été définitivement clôturée. S'applique lorsque le statut d'inscription est clos, pas lorsqu'il est gradué."`
- Proposed: `"La raison pour laquelle une inscription a été définitivement clôturée. S'applique lorsque le statut d'inscription est clos, et non lorsqu'il est gradué."`
- Reason: `pas lorsqu'il est gradué` is grammatically acceptable but `et non lorsqu'il est gradué` is the more precise and formal French construction for this contrastive use.

#### values

- `non_compliance`.label — current: `Non-conformité` — proposed: `Non-respect des conditions` — reason: `Non-conformité` is the standard French term in quality/standards contexts (ISO, etc.) but in social protection program contexts, the idiomatic French for failing to meet behavioral conditions is `non-respect des conditions` or `manquement aux conditions`. `Non-conformité` may confuse a policy officer who associates it with quality certification. (Medium priority.)

- `non_compliance`.definition — current: `"Le bénéficiaire n'a pas rempli les conditions continues du programme."` — proposed: `"Le bénéficiaire n'a pas satisfait aux conditions continues du programme."` — reason: `rempli les conditions` → `satisfait aux conditions` (consistency rule).

- `ineligibility`.definition — current: `"Le bénéficiaire a été déterminé comme n'étant plus éligible en raison d'un changement de circonstances tel que le revenu, l'âge ou la résidence."` — proposed: `"Le bénéficiaire a été reconnu comme n'étant plus admissible en raison d'un changement de circonstances, tel que le revenu, l'âge ou la résidence."` — reason: `éligible` → `admissible` (consistency rule); `déterminé comme` is a calque; `reconnu comme` is standard French administrative usage. A comma before `tel que` is also standard when the list is non-restrictive.

- `ineligibility`.label — current: `Inéligibilité` — proposed: `Non-admissibilité` — reason: Consistency with `admissibilité` term family.

---

### schema/vocabularies/sp/enrollment-status.yaml

#### Top-level definition
- Current: `Les états du cycle de vie d'une inscription dans un programme.`
- Proposed: No change needed.

#### values

- `waitlisted`.definition — current: `Le demandeur a été vérifié comme éligible mais attend une place disponible dans le programme en raison de contraintes de capacité ou de budget.` — proposed: `Le demandeur a été reconnu admissible mais attend une place disponible dans le programme en raison de contraintes de capacité ou de budget.` — reason: `éligible` → `admissible` (consistency rule); `vérifié comme éligible` is a calque; `reconnu admissible` is the standard French form.

- `graduated`.label — current: `Sorti avec succès` — proposed: No change. `Sorti avec succès` is a reasonable translation since there is no single canonical French term for "graduated" in SP contexts; `gradué` would be a calque. `Sorti avec succès` is clear and internationally neutral.

- `graduated`.definition — current: `Le bénéficiaire a quitté le programme avec succès selon les critères de graduation définis par le programme.` — proposed: `Le bénéficiaire a quitté le programme avec succès selon les critères de sortie définis par le programme.` — reason: `critères de graduation` is a calque of "graduation criteria". The standard French SP term is `critères de sortie` (exit criteria) or `critères de fin de programme`. Using `graduation` in French is non-standard for a policy audience outside North American French contexts.

---

### schema/vocabularies/sp/entitlement-status.yaml

#### Top-level definition
- Current: `Les états du cycle de vie d'une instance de droit à prestation, de la création à l'exécution ou la clôture.`
- Proposed: `Les états du cycle de vie d'une instance de droit à prestation, de la création à l'exécution ou à la clôture.`
- Reason: The second `à` must be repeated before `la clôture` in formal French (parallel preposition structure). `à l'exécution ou à la clôture` is grammatically required.

#### values

- `expired`.definition — current: `La période de validité du droit a expiré sans exécution. Contrairement à l'annulation, personne n'a activement retiré le droit ; il a expiré.` — proposed: `La période de validité du droit a expiré sans exécution. Contrairement à l'annulation, personne n'a activement retiré le droit; il a simplement échu.` — reason: The semicolon before `il a expiré` uses a space+semicolon (French typographic convention), which is correct in French. However, `il a expiré` repeats `expiré` from the first sentence. `il a simplement échu` (it simply lapsed) avoids the repetition and is the precise term for a right lapsing by operation of time. Note: the space before the semicolon is correct French typography but the YAML files otherwise use no-space semicolons consistently; recommend keeping the no-space convention for file consistency.

- `partially_fulfilled`.definition — current: `Une partie mais pas la totalité du montant du droit a été versée, par exemple une tranche d'un paiement à tranches multiples ou un bon émis mais pas encore échangé.` — proposed: No change needed. Accurate and natural.

---

### schema/vocabularies/sp/grievance-status.yaml

#### Top-level definition
- Current: `Les états du cycle de vie d'un dossier de grief dans un programme ou service.`
- Proposed: No change. `grief` is listed as the canonical French term in the consistency rules.

#### values

- `escalated`.label — current: `Escaladé` — proposed: `Transmis à un niveau supérieur` — reason: `Escaladé` is a calque of the English word "escalated". It is not standard French. The canonical French administrative term for escalation of a complaint is `renvoi à un niveau supérieur` or, as a past participle label, `Transmis à une autorité supérieure`. A shorter option is `Escalé` (used in some Canadian administrative French) but this is not internationally neutral. `Transmis à une instance supérieure` covers all Francophone jurisdictions. (High priority: `Escaladé` is a direct calque and will not be understood in West Africa or non-North-American contexts.)

- `escalated`.definition — current: `Le grief a été renvoyé à une autorité supérieure ou un organisme externe parce qu'il n'a pas pu être résolu au premier niveau.` — proposed: `Le grief a été transmis à une autorité supérieure ou à un organisme externe, n'ayant pas pu être résolu au premier niveau.` — reason: `parce qu'il n'a pas pu être résolu au premier niveau` is correct but the participial construction (`n'ayant pas pu être résolu`) is more idiomatic in formal administrative French. Also, the second preposition `à` should be repeated before `un organisme externe` (parallel structure).

---

### schema/vocabularies/sp/grievance-type.yaml

#### Top-level definition
- Current: `"Catégories décrivant la nature d'un grief ou d'une plainte reçu par un programme via son mécanisme de recours."`
- Proposed: `"Catégories décrivant la nature d'un grief ou d'une plainte reçus par un programme par le biais de son mécanisme de recours."`
- Reason: Two issues. First, `reçu` must agree with `un grief ou d'une plainte` — since the two nouns are joined by `ou`, the agreement follows the nearest noun (`plainte`, feminine) so it should be `reçue`, or if both are intended, the masculine plural `reçus` covering both is used in formal written French. `reçus` (plural) is the safest option covering the coordinated pair. Second, `via` is common in informal writing but `par le biais de` is the more register-appropriate form for policy documents.

#### values

- `exclusion_error`.definition — current: `"Une plainte indiquant qu'une personne ou un ménage éligible a été injustement exclu d'un programme, d'une prestation ou d'un service."` — proposed: `"Une plainte indiquant qu'une personne ou un ménage admissible a été injustement exclu d'un programme, d'une prestation ou d'un service."` — reason: `éligible` → `admissible` (consistency rule).

- `inclusion_error`.definition — current: `"Un signalement qu'une personne ou un ménage inéligible reçoit des prestations ou services auxquels il ne devrait pas avoir droit."` — proposed: `"Un signalement indiquant qu'une personne ou un ménage non admissible reçoit des prestations ou services auxquels il ne devrait pas avoir droit."` — reason: `inéligible` → `non admissible` (consistency rule). Also, `Un signalement qu'` is grammatically incomplete without a verb; `Un signalement indiquant que` is the correct construction.

- `appeal`.definition — current: `"Une demande formelle de révision d'une décision administrative, telle qu'une détermination d'éligibilité, un calcul de prestation ou une décision de sortie."` — proposed: `"Une demande formelle de révision d'une décision administrative, telle qu'une détermination d'admissibilité, un calcul de prestation ou une décision de sortie."` — reason: `éligibilité` → `admissibilité` (consistency rule).

- `information_request`.definition — current: `"Une demande d'information sur les règles du programme, les critères d'éligibilité, les droits aux prestations ou les procédures de plainte, lorsqu'elle est reçue par le canal d'accueil des griefs."` — proposed: `"Une demande d'information sur les règles du programme, les critères d'admissibilité, les droits aux prestations ou les procédures de plainte, lorsqu'elle est reçue par le canal d'accueil des griefs."` — reason: `éligibilité` → `admissibilité` (consistency rule).

- `misconduct`.label — current: `Mauvaise conduite` — proposed: `Manquement professionnel` — reason: `Mauvaise conduite` is a somewhat colloquial translation of "misconduct". In French administrative and HR usage, `manquement professionnel` or `comportement inapproprié` is preferred. The definition covers fraud, corruption, harassment etc., which collectively fall under `manquement professionnel` in French HR and public-service law. (Medium priority.)

---

### schema/vocabularies/sp/referral-status.yaml

#### Top-level definition
- Current: `"Les états du cycle de vie d'une orientation entre programmes ou services."`
- Proposed: No change. `orientation` is listed as the canonical term for `referral` in the consistency rules.

#### values

- `completed`.label — current: `Complétée` — proposed: `Terminée` — reason: Cross-file consistency rule: `completed` → `terminé(e)` (NOT `complété(e)`). `Complétée` is a Quebec French calque; the internationally neutral term is `Terminée`.

- `completed`.definition — current: `"La personne orientée a été inscrite ou prise en charge par le programme récepteur, et le processus d'orientation est terminé."` — proposed: No change needed in the definition body. The definition uses `terminé` correctly. Only the label needs updating.

- `cancelled`.definition — current: `"L'orientation a été retirée par le programme référant ou la personne orientée avant que le programme récepteur n'agisse."` — proposed: `"L'orientation a été retirée par le programme référent ou la personne orientée avant que le programme récepteur n'agisse."` — reason: `référant` (present participle, meaning "referring at this moment") should be `référent` (adjective, meaning "referring/sender program"). `Programme référent` is the standard French term for the referring program in an orientation/referral context. `Référant` is grammatically incorrect as a modifier here.

---

### schema/vocabularies/sp/targeting-approach.yaml

#### Top-level definition
- Current: `"Les méthodes utilisées pour identifier et sélectionner les bénéficiaires éligibles à un programme de protection sociale."`
- Proposed: `"Les méthodes utilisées pour identifier et sélectionner les bénéficiaires admissibles à un programme de protection sociale."`
- Reason: `éligibles` → `admissibles` (consistency rule).

#### values

- `means_tested`.definition — current: `"Éligibilité basée sur une évaluation vérifiée des revenus ou des actifs."` — proposed: `"Admissibilité fondée sur une évaluation vérifiée des revenus ou des actifs."` — reason: `Éligibilité` → `Admissibilité` (consistency rule). Also, `basée sur` is a common Quebec/informal form; `fondée sur` is the more standard formal French.

- `proxy_means_tested`.definition — current: `"Éligibilité basée sur un modèle statistique prédisant le bien-être à partir de caractéristiques observables du ménage."` — proposed: `"Admissibilité fondée sur un modèle statistique prédisant le niveau de vie à partir de caractéristiques observables du ménage."` — reason: `Éligibilité` → `Admissibilité` (consistency rule); `basée sur` → `fondée sur` (formality); `bien-être` is acceptable but `niveau de vie` is more precise in this context (the model predicts welfare/poverty status, i.e., standard of living).

- `categorical`.definition — current: `"Éligibilité basée sur une catégorie démographique telle que l'âge, le handicap, la grossesse ou l'état d'orphelin."` — proposed: `"Admissibilité fondée sur une catégorie démographique telle que l'âge, le handicap, la grossesse ou la situation d'orphelin."` — reason: `Éligibilité` → `Admissibilité`; `basée sur` → `fondée sur`; `état d'orphelin` is unusual; `situation d'orphelin` or `condition d'orphelin` is more natural in French social policy.

- `geographic`.definition — current: `"Éligibilité basée sur la résidence dans une zone géographique définie."` — proposed: `"Admissibilité fondée sur la résidence dans une zone géographique définie."` — reason: `Éligibilité` → `Admissibilité`; `basée sur` → `fondée sur`.

- `universal`.definition — current: `"Accessible à tous les individus au sein d'une population définie, indépendamment du revenu ou d'autres caractéristiques."` — proposed: No change needed. Accurate and natural.

- `community_based`.label — current: `Basé sur la communauté` — proposed: `Ciblage communautaire` — reason: `Basé sur la communauté` is a calque of "community-based". In French social protection vocabulary, the standard term is `ciblage communautaire`. This is consistent with the consistency rule that `targeting` → `ciblage`. (Medium priority.)

- `community_based`.definition — current: `"La communauté sélectionne les bénéficiaires en se basant sur la connaissance locale du bien-être relatif."` — proposed: `"La communauté sélectionne les bénéficiaires en s'appuyant sur la connaissance locale du bien-être relatif."` — reason: `en se basant sur` is informal/Quebec usage; `en s'appuyant sur` is the standard formal French equivalent.

- `self_targeting`.label — current: `Auto-ciblage` — proposed: No change. `Auto-ciblage` is used in French SP literature and is appropriate.

- `self_targeting`.definition — current: `"La conception du programme décourage la participation des non-pauvres, généralement en fixant des salaires inférieurs au taux du marché ou en exigeant une participation intensive en temps."` — proposed: `"La conception du programme décourage la participation des non-pauvres, généralement en fixant des rémunérations inférieures au taux du marché ou en exigeant une participation intensive en temps."` — reason: `salaires` (wages) is narrower than the concept intended; `rémunérations` covers wages and other compensation forms (e.g., food-for-work). Minor but more accurate.

---

## Open questions

1. **`labelled` (conditionality-type)**: No single standard French SP term for "labelled cash transfer" exists across all Francophone regions. `À usage désigné` or `Affecté à un usage désigné` are proposed. Jeremi should confirm which label is most recognizable to the intended audience (UNICEF/World Bank Francophone practitioners vs. national ministry staff).

2. **`escalated` (grievance-status)**: `Escaladé` is widely used in Quebec French administrative contexts but is not internationally neutral. `Transmis à une instance supérieure` is proposed. If the audience is primarily Quebec or Canada-based this may be relaxed, but given the West/Central Africa framing the calque should be avoided.

3. **`graduated` (enrollment-status)**: `Sorti avec succès` is the current label; the definition uses `critères de sortie` (proposed) vs. `critères de graduation` (current). If the program explicitly uses "graduation" as a technical term (e.g., in graduation programs per the BRAC model), retaining a French calque could be intentional. Confirmation needed.

4. **`basée sur` vs. `fondée sur`**: This review proposes replacing all instances of `basée sur` with `fondée sur` for register consistency. If any of these files target a specific Francophone region where `basée sur` is the house style, the replacements in targeting-approach.yaml can be relaxed.
