# Review: FR CRVS concepts

---

## adoption.yaml

Overall: Clean and accurate. The civil-law vocabulary (filiation, adoption plénière/simple, Convention de La Haye) is correct and reads naturally. No issues worth flagging.

---

## annulment.yaml

Overall: Accurate and concise. "Distincte du Divorce" preserves the concept label correctly. No issues worth flagging.

---

## birth.yaml

Overall: Mostly solid. The WHO-aligned definition phrase is well handled. Two issues.

### Issue 1

- **Current (fr):** `Saisit l'enfant, les parents et les attributs utilisés par l'état civil et les statistiques de l'état civil`
- **Source (en):** `Captures the child, the parents, and attributes used by civil registration and vital statistics`
- **Issue:** Two problems in one sentence. First, "Saisit" is a calque of "Captures" used to open a sentence describing what the concept includes; in French CRVS writing, "Inclut" or "Recueille" is more natural for listing the contents of a record. Second, "l'état civil et les statistiques de l'état civil" is redundant: the phrase repeats "état civil" within the same clause. The English distinguishes two things: "civil registration" (the administrative function) and "vital statistics" (the statistical function). In French the standard pairing is "l'enregistrement des faits d'état civil et les statistiques de l'état civil", but that too is long. The shorter conventional form is "l'état civil et les statistiques vitales".
- **Proposed:** `Recueille les données relatives à l'enfant, aux parents et aux attributs utilisés par l'état civil et les statistiques vitales (sexe à la naissance, ordre de naissance, personne ayant assisté à l'accouchement, poids, type de lieu).`
- **Rationale:** "Recueille" is the standard verb in French civil registration documentation for recording event data. "Statistiques vitales" avoids the redundancy and is widely used by French-speaking UN and WHO bodies. "Personne ayant assisté à l'accouchement" is also slightly expanded below (see Issue 2).

### Issue 2

- **Current (fr):** `personne ayant assisté`
- **Source (en):** `attendant`
- **Issue:** "Personne ayant assisté" is underspecified and could mean anyone present. The standard French term in civil registration for birth attendant is "personne ayant assisté à l'accouchement", or more precisely "accoucheur" / "personnel présent à l'accouchement" depending on context. Without "à l'accouchement", the phrase is ambiguous.
- **Proposed:** `personne ayant assisté à l'accouchement`
- **Rationale:** The qualifier "à l'accouchement" is what makes the term unambiguous in French civil registration practice. It corresponds to the UN standard field label.

---

## certificate.yaml

Overall: Terminology is well chosen ("copie intégrale", "extrait plurilingue", "CIEC"). One issue.

### Issue 1

- **Current (fr):** `Un document délivré à partir d'un acte d'état civil ou d'un événement d'état civil`
- **Source (en):** `A document issued from a civil status record or vital event`
- **Issue:** "D'état civil" appears twice in quick succession, creating a clunky repetition. The English distinguishes between a record ("civil status record") and the underlying occurrence ("vital event"). In French, "acte d'état civil" covers the record; the underlying occurrence can be called "fait d'état civil" or simply "événement vital" to break the repetition and sharpen the contrast.
- **Proposed:** `Un document délivré à partir d'un acte d'état civil ou d'un fait vital, attestant de cet événement pour un usage externe.`
- **Rationale:** "Fait vital" parallels "vital event" and avoids the repeated "d'état civil". The rest of the sentence is unchanged.

---

## civil-status-annotation.yaml

Overall: Mostly good. The canonical term "mention marginale" is introduced and used correctly throughout. Two issues.

### Issue 1

- **Current (fr):** `Le mécanisme des mentions est la manière dont les registres de droit civil maintiennent une identité civile cohérente`
- **Source (en):** `The annotation mechanism is how civil-law registries maintain a coherent civil identity`
- **Issue:** "La manière dont" is a calque of "how" in this construction. In French, this clause is better expressed as a purpose or result structure: "C'est par ce mécanisme que les registres d'état civil..." Also, "registres de droit civil" is non-standard: the institution is called "registres d'état civil" (or "officiers d'état civil"), not "registres de droit civil" ("registres de droit civil" would suggest registries of civil law, i.e., a law library).
- **Proposed:** `C'est par ce mécanisme des mentions que les registres d'état civil maintiennent une identité civile cohérente dans le temps sans réécrire l'acte original.`
- **Rationale:** "Registres d'état civil" is the correct institutional term. "C'est par ce mécanisme que" is the idiomatic French construction for "this is how/the mechanism by which".

### Issue 2

- **Current (fr):** `une correction ordonnée par tribunal`
- **Source (en):** `a court-ordered correction`
- **Issue:** "Ordonnée par tribunal" is a calque. In French legal prose, a court order issues from "le tribunal" (with article) or the phrase uses "par voie judiciaire" or "sur décision judiciaire".
- **Proposed:** `une correction ordonnée par le tribunal`
- **Rationale:** The article "le" is required in French before "tribunal" in this construction. Without it, the phrase reads as translated rather than composed.

---

## civil-status-record.yaml

Overall: Accurate, with good use of "acte", "pérenne", "mentions marginales". No issues worth flagging.

---

## crvs-person.yaml

Overall: Conceptually accurate. One grammar error.

### Issue 1

- **Current (fr):** `figées au moment de l'événement plutôt que reflétant les valeurs actuelles`
- **Source (en):** `frozen at event time rather than reflecting current values`
- **Issue:** In French, "plutôt que" followed by a verb requires either the infinitive ("plutôt que de refléter") or, when the subjects differ, a subjunctive. Here the subjects are the same, so the infinitive form is required. "Plutôt que reflétant" is a grammatical error.
- **Proposed:** `figées au moment de l'événement plutôt que de refléter les valeurs actuelles`
- **Rationale:** This is a grammar rule, not a style preference. "Plutôt que de + infinitif" is the required construction in standard French when the same subject is implied.

---

## death.yaml

Overall: Accurate, aligned with WHO vocabulary. One issue with a dangling participial phrase.

### Issue 1

- **Current (fr):** `Aligné sur la définition de l'OMS et la structure CIM pour la classification des causes de décès.`
- **Source (en):** `Aligned with the WHO definition and the ICD structure for cause-of-death classification.`
- **Issue:** "Aligné" is a masculine singular past participle used as a freestanding sentence fragment. It has no clear grammatical anchor in French: the subject of the paragraph is "La disparition permanente..." (feminine), so agreement should be "Alignée" if it modifies that. As a dangling participial fragment, it also reads as directly translated. A brief restructuring resolves both the agreement issue and the calque.
- **Proposed:** `Conforme à la définition de l'OMS et à la structure de la CIM pour la classification des causes de décès.`
- **Rationale:** "Conforme à" is the standard French legal and normative term for "aligned with" or "in accordance with", and it avoids the agreement problem by being an adjective clause that can stand on its own in a definition context. Note also that "CIM" takes the article ("la CIM") in French, and "à la structure de la CIM" requires the preposition "de" before the article.

---

## divorce.yaml

Overall: Concise and correct. No issues worth flagging.

---

## family-register.yaml

Overall: Good. The examples (koseki, hukou, livret de famille) are well placed. "GroupMembership" is correctly left in English as a concept identifier. No issues worth flagging.

---

## fetal-death.yaml

Overall: Mostly accurate. "Mortinaissance" is used correctly as the French standard term. One issue.

### Issue 1

- **Current (fr):** `Saisit l'âge gestationnel, le poids et la cause codée de mortinaissance, en utilisant la CIM-PM lorsqu'elle est disponible.`
- **Source (en):** `Captures gestational age, weight, and coded cause of fetal death using ICD-PM where available.`
- **Issue:** Two problems. First, "Saisit" is again a calque of "Captures" (same issue as birth.yaml Issue 1; see consistency note below). Second, "la cause codée de mortinaissance" is grammatically strained: "mortinaissance" is a noun (stillbirth/fetal death event), not an adjective, so "cause de mortinaissance" reads as "cause of stillbirth" rather than "cause coded as fetal death". The English "coded cause of fetal death" maps to "cause codée de décès fœtal" in French.
- **Proposed:** `Recueille l'âge gestationnel, le poids et la cause codée de décès fœtal, en utilisant la CIM-PM lorsqu'elle est disponible.`
- **Rationale:** "Cause codée de décès fœtal" is the standard French WHO/ICD term for this field. "Recueille" is consistent with the fix proposed for birth.yaml.

---

## legitimation.yaml

Overall: Accurate in meaning. One terminology issue.

### Issue 1

- **Current (fr):** `dans les juridictions où le statut de l'enfant varie encore selon le contexte marital`
- **Source (en):** `in jurisdictions where the status of the child still varies by marital context`
- **Issue:** "Contexte marital" is a calque of "marital context". In French civil and family law, the standard term is "le cadre du mariage" or "la situation matrimoniale des parents". "Marital" exists in French but is less common and more formal than its English cognate; "matrimonial" is the preferred adjective in French legal texts for marriage-related matters.
- **Proposed:** `dans les juridictions où le statut de l'enfant varie encore selon la situation matrimoniale des parents`
- **Rationale:** "Situation matrimoniale" is the canonical French legal term (used in civil codes and civil registration law across the Francophonie). It also makes the reference more precise: it is the parents' marital situation, not an abstract "marital context", that determines the child's status.

---

## marriage.yaml

Overall: Accurate. "De fait" for "common law" is a reasonable choice. "Traité comme un événement d'état civil plutôt que comme une relation permanente" is idiomatic. No issues worth flagging.

---

## marriage-termination.yaml

Overall: Legally accurate. "Du vivant des deux parties" is excellent French legal phrasing. "MarriageTermination" left in English as the concept identifier is consistent. No issues worth flagging.

---

## parent.yaml

Overall: Good. "Reçue" agreement for "utilisée" is handled correctly. The civil-role vocabulary (mère porteuse, père adoptif) is complete and correct. No issues worth flagging.

---

## paternity-recognition.yaml

Overall: Excellent. "Reçu par un officier d'état civil" correctly uses the French civil-law term for an act received before an official. "Consigné en mention marginale" is precise. No issues worth flagging.

---

## vital-event.yaml

Overall: Accurate. The UN document title reference is close enough. No issues worth flagging.

---

## Cross-file consistency note

**"Saisit" as translation of "Captures"**

Files affected: birth.yaml, death.yaml, fetal-death.yaml (and implicitly crvs-person.yaml which uses "Utilisé").

The verb "Saisit" is used to translate "Captures" in the sense of "records / encompasses / includes". In French civil registration documentation, "saisit" has a primary meaning of "seizes" (as in a court seizing jurisdiction) or "inputs data". Using it to mean "covers / includes / records" is an English calque that may confuse domain readers. The consistent fix is "Recueille" (collects, gathers) or "Comprend" (includes) depending on whether the emphasis is on recording or on scope. The choice should be made once and applied consistently across all affected files.
