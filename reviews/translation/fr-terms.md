# French translation review: TermsContent

Scope: full review of `TermsContent.fr.astro` against `TermsContent.en.astro` for naturalness, register, and fidelity to established francophone licensing conventions.

---

## Flags

---

**Flag 1**

- **Line (approx):** 4
- **Current:** `<h2>Résumé</h2>`
- **Issue:** "Résumé" calques the English heading "Summary" and reads as a section summary in the abstract sense; in a legal/terms-of-use context the standard francophone heading is "Aperçu" or "Vue d'ensemble".
- **Proposed:** `<h2>Aperçu</h2>`
- **Rationale:** CC and open-source license landing pages in French (e.g., the official CC FR deed) use "Aperçu" for the plain-language preamble block, not "Résumé".

---

**Flag 2**

- **Line (approx):** 11-12
- **Current:** `sous réserve de fournir une attribution`
- **Issue:** "sous réserve de" introduces a conditional restriction ("provided that / unless"), implying a limit or caveat; the source says "as long as you provide attribution," which is a positive condition, not a caveat.
- **Proposed:** `à condition de mentionner la source`
- **Rationale:** "à condition de" conveys a positive prerequisite; "mentionner la source" matches the plain-language register used in the CC FR deed.

---

**Flag 3**

- **Line (approx):** 17-18
- **Current:** `les ensembles de valeurs contrôlées et les schémas d'identifiants vérifiables`
- **Issue:** "schémas d'identifiants vérifiables" is a mistranslation of "credential schemas." "Credential" in the VC (Verifiable Credential) context is rendered "attestation vérifiable" in standard francophone W3C and ISO documentation, not "identifiant vérifiable."
- **Proposed:** `les ensembles de valeurs contrôlées et les schémas d'attestations vérifiables`
- **Rationale:** W3C VC Data Model French translations and ISO/IEC 18013 use "attestation vérifiable" for "verifiable credential." "Identifiant vérifiable" describes a DID, not a credential.

---

**Flag 4**

- **Line (approx):** 27
- **Current:** `copier et redistribuer le modèle de référence sur tout support ou dans tout format`
- **Issue:** "sur tout support ou dans tout format" is a word-for-word calque; it is grammatically awkward because "support" and "format" require different prepositions here, and the official CC BY 4.0 French deed uses a different phrasing.
- **Proposed:** `copier et redistribuer le modèle de référence sur tout support et sous tout format`
- **Rationale:** The official CC BY 4.0 deed in French uses "sur tout support et sous tout format," using "sous" for format; this is the established convention readers of CC licenses will recognise.

---

**Flag 5**

- **Line (approx):** 28
- **Current:** `remixer, transformer et développer le modèle de référence`
- **Issue:** "développer" is a calque of "build upon" and risks being read as "to develop (software)," which is too narrow. The official CC BY 4.0 French deed uses "créer à partir."
- **Proposed:** `remixer, transformer et créer à partir du modèle de référence`
- **Rationale:** "créer à partir de" is the phrase used in the official CC BY 4.0 deed (deed.fr); it is unambiguous and will be immediately recognised by readers familiar with CC licensing.

---

**Flag 6**

- **Line (approx):** 32
- **Current:** `vous devez créditer l'œuvre de manière appropriée, fournir un lien vers la licence et indiquer si des modifications ont été effectuées`
- **Issue:** Mostly correct, but "fournir un lien vers la licence" is a slight calque. The official CC deed in French uses "fournir un lien vers cette licence," which is both more natural and more precise ("cette licence" vs. "la licence").
- **Proposed:** `vous devez créditer l'œuvre de manière appropriée, fournir un lien vers cette licence et indiquer si des modifications ont été apportées`
- **Rationale:** "apportées" (modifications brought/made) is the standard collocation in legal and technical French; "effectuées" is not wrong but is more administrative. "Cette licence" matches the CC deed exactly.

---

**Flag 7**

- **Line (approx):** 37
- **Current:** `incluant le pipeline de construction`
- **Issue:** "pipeline de construction" is a hybrid calque; "build pipeline" in French technical documentation is usually "chaîne de compilation" or, in CI/CD contexts, "pipeline de build" (where "build" is borrowed). "Pipeline de construction" reads literally and is not the established term.
- **Proposed:** `incluant le pipeline de build`
- **Rationale:** In francophone developer communities (GitLab, GitHub Actions documentation in French), "pipeline de build" or "pipeline CI/CD" is the accepted term; "pipeline de construction" would cause a double-take.

---

**Flag 8**

- **Line (approx):** 55
- **Current:** `Ce sont des représentations lisibles par machine des définitions.`
- **Issue:** "lisibles par machine" is a direct calque of "machine-readable." The standard francophone technical term is "lisibles par une machine" or more precisely "exploitables par des machines"; the W3C and ISO/IEC standards in French use "exploitable par machine" or "interprétable par machine."
- **Proposed:** `Il s'agit de représentations exploitables par machine des définitions.`
- **Rationale:** "Exploitable par machine" is the term used in W3C standards translated into French; "Il s'agit de" is more natural than "Ce sont" in this register for a defining statement.

---

**Flag 9**

- **Line (approx):** 70
- **Current:** `l'organisme de normalisation demeure la source faisant autorité`
- **Issue:** "la source faisant autorité" is a calque of "authoritative source." The established francophone phrasing is "la source de référence" or "la référence faisant foi." "Faisant autorité" is correct but slightly heavy.
- **Proposed:** `l'organisme de normalisation demeure la source de référence`
- **Rationale:** "Source de référence" is the standard term in French technical and legal documentation for "authoritative source," and avoids the slightly legalistic ring of "faisant autorité" in a plain-language context.

---

**Flag 10**

- **Line (approx):** 75
- **Current:** `Lors de l'utilisation du modèle de référence PublicSchema, une attribution appropriée est :`
- **Issue:** "une attribution appropriée est :" is a calque of "appropriate attribution is:" and reads as an incomplete nominal phrase in French. A more natural formulation uses a verb clause.
- **Proposed:** `Pour citer le modèle de référence PublicSchema, l'attribution recommandée est la suivante :`
- **Rationale:** "la suivante" is required in French before a colon-introduced example; "Pour citer" replaces the nominalized gerund with a natural infinitive purpose clause, as is standard in francophone technical documentation.

---

**Flag 11**

- **Line (approx):** 79-80
- **Current:** `mis à disposition sous`
- **Issue:** Not an error, but this is a French-legal rendering; however it is used correctly in the CC context and the official CC deed uses "sous licence." Consistency with the rest of the page (which also uses "sous la licence") is preferred.
- **Proposed:** `sous licence`
- **Rationale:** The official CC attribution badge text in French reads "sous licence CC BY 4.0," not "mis à disposition sous CC BY 4.0." The blockquote should match the canonical attribution formula.

---

## Overall impression

The translation is competent and accurate in meaning throughout; no passages introduce false information. The main pattern of weakness is that several CC-specific passages diverge from the official Creative Commons French deed text, which will be noticeable to francophone readers who work regularly with CC licenses. A secondary issue is a handful of calques in the technical vocabulary ("lisibles par machine," "pipeline de construction," "schémas d'identifiants vérifiables") that are not wrong in isolation but will read as translated-from-English to a native speaker. With the eleven corrections above applied, the page would read as naturally authored French suitable for both policy and developer audiences.
