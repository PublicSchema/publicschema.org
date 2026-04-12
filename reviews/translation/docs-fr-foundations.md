# French translation review — foundations docs

## design-principles.md

**Overall impression:** The file reads clearly and accurately. One passage has a slight calque from English, and the heading "Sémantique, pas structural" carries a grammatical awkwardness worth resolving.

### Flagged passages

**Line 3 — Current:** "## 1. Sémantique, pas structural"
**Issue:** Calque / grammatical mismatch. In French, adjectives agree in gender with the noun they modify. Here the English structure "Semantic, not structural" is transposed directly. The implicit noun is something like "approche" or "conception" (feminine), but the heading floats without a noun, making "structural" feel unanchored. More idiomatic alternatives pair the adjectives symmetrically or nominalise.
**Proposed:** "## 1. Sémantique, non structurel" or "## 1. Le sens avant la structure"
**Rationale:** "Sémantique, pas structural" is not how a French speaker would phrase a contrastive heading. "Non structurel" is the standard negation in such constructions. Alternatively, nominalising ("Le sens avant la structure") matches the rhythm of principle headings and avoids the agreement issue entirely.

---

**Line 5 — Current:** "Le problème d'interopérabilité est la divergence de vocabulaire : les systèmes utilisent des noms différents pour les mêmes entités du monde réel, et lorsque ces noms encodent des choix sémantiques différents, les correspondances entre eux perdent de l'information."
**Issue:** "encodent" is an anglicism for this sense. In French technical writing, "encoder" is used for binary/data encoding. The intended meaning here is "expriment" or "traduisent".
**Proposed:** "...et lorsque ces noms expriment des choix sémantiques différents, les correspondances entre eux perdent de l'information."
**Rationale:** "Encoder un choix sémantique" is a direct calque of "encode a semantic choice." French would say "exprimer", "traduire", or "refléter" in this context.

---

**Line 13 — Current:** "Commencer par ce qui est confirmé, étendre lorsque l'adoption fait surface un besoin réel."
**Issue:** Calque. "Faire surface" is a direct translation of the phrasal verb "to surface." It is not idiomatic in French.
**Proposed:** "Commencer par ce qui est confirmé, étendre lorsque l'adoption révèle un besoin réel."
**Rationale:** "Faire surface" is occasionally found in Québécois journalistic French but reads as an anglicism to most Francophones. "Révèle" is neutral, precise, and pan-Francophone.

---

## schema-design.md

**Overall impression:** Generally well translated and technically accurate. Two passages contain anglicisms, one section heading was dropped entirely compared to the English source (the "Date property conventions" subsection under section 5), and one phrasing is awkward.

### Flagged passages

**Line 14 — Current:** "Appliqué par des validateurs regex dans les schémas JSON."
**Issue:** Minor register issue. "Appliqué" (past participle without auxiliary) opens a nominal sentence in French, which is acceptable in technical writing, but "regex" is used as a bare adjective here ("validateurs regex"), which is slightly awkward. More importantly, the sentence reads as a fragment hanging after the table. The English original has the same structure; in French it reads better with a small recast.
**Proposed:** "Ces conventions sont appliquées par des validateurs d'expression régulière dans les schémas JSON."
**Rationale:** Spelling out the subject avoids the floating participle. "Expression régulière" is the correct French technical term; "regex" is fine as inline code but not as an adjective modifying a French noun.

---

**Lines 66 (end of section 5) — Missing content:** The English version of section 5 ("Temporal context") includes a full subsection titled "### Date property conventions" with explanatory prose and a table covering how lifecycle vs. relationship concepts handle dates, and a rule about not mixing both patterns. This entire subsection is absent from the French file.
**Issue:** Omission, not a translation quality issue per se, but a meaningful gap in coverage. The subsection contains normative guidance ("Do not mix both patterns on the same concept") that practitioners need.
**Proposed:** Translate and add the missing subsection after line 66. The subsection heading would be "### Conventions pour les propriétés de date" and the final rule: "Ne combinez pas les deux modèles sur un même concept. Un concept à cycle de vie ne doit pas porter à la fois `enrollment_date` et `start_date`."
**Rationale:** The omission leaves French readers without guidance that English readers have. This should be flagged for the translator to fill in.

---

**Line 70 — Current:** "Une propriété comme `start_date` est définie une seule fois et réutilisée entre concepts."
**Issue:** "Entre concepts" is a calque of "across concepts." The French preposition for this sense is "entre" only when there is reciprocity between discrete items; for distribution across a set, "d'un concept à l'autre" or "pour l'ensemble des concepts" is more natural.
**Proposed:** "Une propriété comme `start_date` est définie une seule fois et réutilisée pour l'ensemble des concepts."
**Rationale:** "Réutilisée entre concepts" sounds like the property is exchanged back and forth between concepts, which is not the intended meaning. "Pour l'ensemble des concepts" conveys shared reuse across the schema.

---

**Line 74 — Current:** "`grievance_type` révèle que quelqu'un a déposé une réclamation."
**Issue:** Register. "Réclamation" is the word used throughout this document for "grievance" (the concept), so the usage is consistent, but worth flagging: in Francophone administrative contexts, "réclamation" often means a claim for a benefit (e.g., a reimbursement claim), while "plainte" or "doléance" more clearly signals a complaint. For an international audience, "plainte" is less ambiguous.
**Proposed:** "`grievance_type` révèle que quelqu'un a déposé une plainte."
**Rationale:** If the concept "Grievance" is consistently translated as "Réclamation" elsewhere in the project, maintain consistency here and flag this as a project-level terminology choice to revisit. If there is no binding precedent, "plainte" is safer for a pan-Francophone audience.

---

## vocabulary-design.md

**Overall impression:** This file reads well overall. One heading retains an English word untranslated ("scoped"), and a few phrasings are slightly awkward but not wrong. Two cases of "effectuant leur correspondance vers" are clunky and should be simplified.

### Flagged passages

**Line 5 — Current:** "## 1. Universel par défaut, scoped par domaine par exception"
**Issue:** "Scoped" is left in English. The rest of the heading is in French, making the code-switch jarring for a prose heading (as opposed to inline code).
**Proposed:** "## 1. Universel par défaut, délimité par domaine par exception"
**Rationale:** "Délimité" (or "limité") conveys the scoping concept without borrowing the English technical term in a prose heading. "Scoped" in YAML/code is fine; in a heading it reads as untranslated.

---

**Lines 70-73 — Current:** "3 systèmes ou plus effectuant leur correspondance vers `other` = lacune dans le vocabulaire. Promouvez en code nommé. / 4 codes système ou plus effectuant leur correspondance vers une seule valeur canonique = le vocabulaire peut être trop grossier. / Code système effectuant sa correspondance vers `null` alors qu'un code canonique plus large existe = bogue de correspondance."
**Issue:** "Effectuant leur correspondance vers" is an awkward, over-literal translation of "mapping to." In French technical writing, this is most naturally expressed as "correspondant à" or "associé à."
**Proposed:**
- "3 systèmes ou plus dont les codes correspondent à `other` = lacune dans le vocabulaire. Promouvez en code nommé."
- "4 codes système ou plus correspondant à une seule valeur canonique = le vocabulaire est peut-être trop grossier."
- "Code système correspondant à `null` alors qu'un code canonique plus large existe = erreur de correspondance."
**Rationale:** "Effectuer une correspondance" is technically correct but verbose and bureaucratic. "Correspondre à" is the natural, direct equivalent. Also, "bogue de correspondance" at the end of line 73 is fine but "erreur de correspondance" is slightly more neutral and formal for a policy-facing document.

---

**Line 38 — Current:** "N'adoptez pas les codes d'une norme lorsqu'ils ne servent pas le public cible."
**Issue:** "Public cible" is a direct calque of "target audience." It is understandable but carries a marketing register. In the context of a technical standards document, "les utilisateurs concernés" or "les praticiens visés" is more appropriate.
**Proposed:** "N'adoptez pas les codes d'une norme lorsqu'ils ne servent pas les praticiens visés."
**Rationale:** "Public cible" is commonly used in French but has a distinctly commercial flavour. The English "audience" in this context means domain practitioners, and "praticiens visés" aligns with the register of the rest of the document.

---

## versioning-and-maturity.md

**Overall impression:** This is the strongest translation of the five files. The prose flows naturally and accurately. Two minor issues: one word choice feels like a calque, and the licensing section has a sentence that inverts the French logic slightly.

### Flagged passages

**Line 9 — Current:** "\"Cet élément est-il sûr à utiliser ?\" et \"Contre quel instantané est-ce que je construis ?\" sont des questions différentes."
**Issue:** "Contre quel instantané est-ce que je construis ?" is awkward. "Construire contre un instantané" is a calque of "build against a snapshot." French would say "je développe à partir de quel instantané" or "je travaille sur la base de quel instantané."
**Proposed:** "\"Cet élément est-il sûr à utiliser ?\" et \"Sur la base de quel instantané est-ce que je construis ?\" sont des questions différentes."
**Rationale:** "Construire contre" is a direct import of the English construction "build against." "Sur la base de" or "à partir de" is the natural French equivalent.

---

**Line 66 — Current:** "CC-BY-4.0 a été choisi plutôt que CC0 (qui perd le suivi d'attribution) et CC-BY-SA (dont la clause de partage à l'identique décourage l'adoption par les gouvernements et les intégrateurs commerciaux)."
**Issue:** "Intégrateurs commerciaux" is a calque of "corporate integrators." In French, "commercial" tends to mean "relating to trade/sales" rather than "for-profit/corporate." A more precise term is "intégrateurs du secteur privé" or simply "entreprises d'intégration."
**Proposed:** "CC-BY-4.0 a été choisi plutôt que CC0 (qui ne préserve pas le suivi d'attribution) et CC-BY-SA (dont la clause de partage à l'identique décourage l'adoption par les gouvernements et les intégrateurs du secteur privé)."
**Rationale:** "Qui perd le suivi d'attribution" also slightly misframes CC0 as losing something; "qui ne préserve pas" is more accurate and natural. "Intégrateurs du secteur privé" replaces the ambiguous "commerciaux."

---

## extension-mechanism.md

**Overall impression:** Well translated, technically accurate, and reads naturally throughout. One phrasing echoes an English construction unnecessarily, and one word choice in the credential issuer section is slightly off-register, but neither is serious.

### Flagged passages

**Line 57 — Current:** "Il peut choisir de l'accepter, de l'associer à une valeur canonique ou de la signaler pour révision."
**Issue:** "La signaler pour révision" is a minor calque of "flag it for review." It is intelligible but "la soumettre à révision" or "la marquer comme à vérifier" is more natural in a French administrative context.
**Proposed:** "Il peut choisir de l'accepter, de l'associer à une valeur canonique ou de la soumettre à révision."
**Rationale:** "Signaler pour révision" is understandable but combines a French verb with an English phrasal structure. "Soumettre à révision" is idiomatic and precise.

---

**Line 92 — Current:** "Le vocabulaire grandit grâce à des usages réels, pas par conception de comité."
**Issue:** "Conception de comité" is a calque of "committee design." In French, the natural phrasing for this concept (decisions made by committee without grounding in real practice) is "conception par comité" or "élaboration en comité."
**Proposed:** "Le vocabulaire grandit grâce à des usages réels, pas par élaboration en comité."
**Rationale:** "Conception de comité" reads as "design by committee" with the wrong preposition. "Élaboration en comité" is the standard French idiom for this concept and is widely understood in international policy circles.

---

**Line 97 — Current:** "Listez l'URL de votre contexte après le contexte PublicSchema dans le tableau `@context`"
**Issue:** Register. "Listez" (imperative of "lister") is an anglicism for "dresser une liste" or "indiquer." In formal French instructions, the preferred forms are "indiquez" or "ajoutez."
**Proposed:** "Ajoutez l'URL de votre contexte après le contexte PublicSchema dans le tableau `@context`"
**Rationale:** "Lister" in the sense of "to list items sequentially" is increasingly accepted in French but still reads as an anglicism in formal registers. "Ajouter" is more precise here (you are adding an entry, not making a list) and avoids the issue entirely.
