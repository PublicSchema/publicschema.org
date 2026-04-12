# French translation review: HomepageContent

Scope: full review of `HomepageContent.fr.astro` against the English source, targeting international francophone policy register.

---

## Flagged passages

---

**Flag 1**

- **Line (approx):** 26-29
- **Current:** `Lorsque des programmes servent les mêmes personnes, leurs systèmes ont besoin d'un langage commun. PublicSchema le fournit : des définitions partagées pour les concepts, les champs et les codes de valeurs. Commencez ici ; adaptez et étendez selon le contexte de votre pays.`
- **Issue:** "les codes de valeurs" is an awkward calque of "value codes"; in French technical standards writing the standard term is "codes de valeur" (no plural on "valeur"). Also "Commencez ici ; adaptez et étendez" reproduces the English imperative sequence somewhat mechanically; a native policy text would use an infinitive or noun construction to keep the register consistent with the formal tone of the rest of the paragraph.
- **Proposed:** `Lorsque des programmes servent les mêmes personnes, leurs systèmes ont besoin d'un langage commun. PublicSchema le fournit : des définitions partagées pour les concepts, les champs et les codes de valeur. Prenez-les comme point de départ, puis adaptez-les au contexte de votre pays.`
- **Rationale:** "codes de valeur" is the established form; replacing the semicolon-chained imperatives with a more natural two-step sentence removes the English rhetorical rhythm.

---

**Flag 2**

- **Line (approx):** 43-44
- **Current:** `PublicSchema n'est ni une norme d'API, ni un produit logiciel, ni un référentiel de conformité.`
- **Issue:** "référentiel de conformité" is a reasonable attempt but "référentiel" in French policy contexts almost always denotes a reference catalogue (e.g., RGPD compliance catalogue, DUER), not a compliance framework in the sense of a governance instrument. "Cadre de conformité" is the internationally neutral equivalent.
- **Proposed:** `PublicSchema n'est ni une norme d'API, ni un produit logiciel, ni un cadre de conformité.`
- **Rationale:** "Cadre de conformité" is the standard term across EU institutions, francophone Africa, and international organisations; "référentiel" would be misread as a catalogue or register.

---

**Flag 3**

- **Line (approx):** 46-47
- **Current:** `Chaque définition reçoit un URI stable, prêt à l'emploi dans des Titres vérifiables (Verifiable Credentials).`
- **Issue:** "Titres vérifiables" is not the established francophone term for Verifiable Credentials. The W3C specification is translated as "Attestations vérifiables" in the official French W3C translation and in EU/francophone-Africa digital identity literature. "Titre" has a narrow legal/travel-document connotation in many francophone contexts that does not map onto the VC concept.
- **Proposed:** `Chaque définition reçoit un URI stable, utilisable directement dans des attestations vérifiables (Verifiable Credentials).`
- **Rationale:** "attestations vérifiables" is the W3C-aligned term and is understood across all francophone policy communities; "prêt à l'emploi" is also slightly informal, replaced by the more precise "utilisable directement".

---

**Flag 4**

- **Line (approx):** 47-48
- **Current:** `étendez le reste dans votre propre espace de noms`
- **Issue:** "espace de noms" is a technically correct calque of "namespace" but is jargon that a policy officer would not recognise. The English source is written for a mixed audience; the French should keep this readable for non-developers. The concept is already explained in the "adapting" persona lower on the page, so a brief paraphrase works here.
- **Proposed:** `étendez le reste dans votre propre espace de définition`
- **Rationale:** "espace de définition" is opaque enough to signal a technical concept without being developer-specific jargon, and avoids the anglicism. Alternatively, a fuller paraphrase such as "en définissant vos propres extensions" would be clearer still for a policy audience.

---

**Flag 5**

- **Line (approx):** 55-59
- **Current:** `Les entités comme Personne, Inscription et Paiement reçoivent des définitions claires rédigées pour les gestionnaires de programmes. Chaque concept porte des propriétés nommées et typées [...] définies une fois et réutilisées entre les concepts.`
- **Issue:** "réutilisées entre les concepts" is a literal calque of "reused across concepts". In French the natural preposition here is "d'un concept à l'autre" or "à travers les concepts". "Entre" denotes a relationship between items in a set, not cross-reuse.
- **Proposed:** `[...] définies une fois et réutilisées d'un concept à l'autre.`
- **Rationale:** "d'un concept à l'autre" conveys the reuse pattern naturally; "entre les concepts" is grammatically plausible but creates an unintended reading of shared-between rather than applicable-across.

---

**Flag 6**

- **Line (approx):** 87-91
- **Current:** `Une mère inscrite à un programme de transfert monétaire devrait automatiquement être éligible à une prestation de santé maternelle. Mais les deux systèmes définissent le « genre » différemment, le « ménage » différemment, et le « statut d'inscription » différemment. L'orientation nécessite un exercice de correspondance manuelle qui prend des semaines et introduit des erreurs.`
- **Issue:** "L'orientation" is ambiguous: in francophone health/social-protection contexts it primarily means clinical or social referral (aiguillage vers un service), which is actually the right concept, but the sentence structure makes it read as if "orientation" refers back to the definitional disagreement, not to the act of referral. The English "The referral requires..." is cleaner. Additionally "exercice de correspondance manuelle" is a heavy calque of "manual mapping exercise"; the natural policy term is "travail de mise en correspondance manuelle" or simply "exercice de mise en correspondance".
- **Proposed:** `Le renvoi vers la prestation de santé nécessite alors un exercice de mise en correspondance manuelle, qui prend des semaines et génère des erreurs.`
- **Rationale:** Making the referral subject explicit removes ambiguity; "mise en correspondance" is the standard French term for field mapping in interoperability contexts; "génère des erreurs" is more natural than "introduit des erreurs".

---

**Flag 7**

- **Line (approx):** 125-127
- **Current:** `C'est le coût de la coordination : à chaque fois que deux programmes doivent partager des données, quelqu'un passe des semaines à établir des correspondances entre champs et à traduire des codes. C'est coûteux, fragile, et recommence à zéro à chaque mise à niveau d'un système.`
- **Issue:** "recommence à zéro" is correct French but the third item of the series ("recommence à zéro") does not share the same grammatical subject as "C'est coûteux, fragile". The English uses parallel adjectives: "expensive, fragile, and starts over every time." The French mixes predicate adjectives with a full verb clause in a single predicate, which reads awkwardly. "et repart de zéro à chaque mise à niveau" is more natural and grammatically parallel in spirit.
- **Proposed:** `C'est coûteux, fragile, et tout recommence à zéro à chaque mise à niveau d'un système.`
- **Rationale:** Adding "tout" makes the clause complete and independent, resolving the subject mismatch; the sentence now reads naturally as a list of three observations.

---

**Flag 8**

- **Line (approx):** 130-135
- **Current:** `Pire encore, certaines correspondances ne sont pas seulement lentes mais entraînent des pertes d'information. [...] Les définitions partagées ne font pas qu'économiser du temps ; elles rendent possible un échange précis en premier lieu.`
- **Issue:** "en premier lieu" is a calque of "in the first place" used with the meaning "to begin with / at all". In French, "en premier lieu" standardly means "first of all / firstly" in an enumeration, not the concluding "in the first place" sense. The correct phrase for the English meaning is "tout simplement" or "en réalité" or, more precisely, "elles sont la condition même d'un échange fiable".
- **Proposed:** `Les définitions partagées ne font pas qu'économiser du temps ; elles rendent tout simplement possible un échange précis.`
- **Rationale:** Eliminates the false cognate; "tout simplement" conveys the "in the first place / at all" sense naturally in francophone policy writing.

---

**Flag 9**

- **Line (approx):** 194-195
- **Current:** `DCI spécifie comment déplacer des dossiers d'inscription entre systèmes ; PublicSchema spécifie ce que signifient « inscription », « actif » et « benefit_modality » dans ces dossiers.`
- **Issue:** "déplacer des dossiers" is a literal calque of "move records". In French technical and administrative contexts, records are "échangés", "transmis", or "transférés" between systems; "déplacer" implies physical relocation or deletion from the source, which is not the intended meaning.
- **Proposed:** `DCI spécifie comment transférer des dossiers d'inscription entre systèmes ; PublicSchema spécifie ce que signifient « inscription », « actif » et « benefit_modality » dans ces dossiers.`
- **Rationale:** "transférer" is the standard term in interoperability and data-exchange contexts across francophone institutions.

---

**Flag 10**

- **Line (approx):** 196-198
- **Current:** `EU Core Person Vocabulary gère les attributs d'identité ; PublicSchema s'étend au cycle de vie de la prestation au-delà du nom et de la date de naissance.`
- **Issue:** "s'étend au cycle de vie de la prestation" is ambiguous: it could mean PublicSchema stretches itself to cover that lifecycle, or that it extends into that domain. The English is "extends into the delivery lifecycle." A cleaner French rendering distinguishes coverage from extension. Also, the sentence is slightly abrupt without a brief linking phrase acknowledging the complementarity.
- **Proposed:** `EU Core Person Vocabulary couvre les attributs d'identité ; PublicSchema va plus loin, en intégrant le cycle de vie complet de la prestation, au-delà du nom et de la date de naissance.`
- **Rationale:** "va plus loin, en intégrant" is the natural policy-document formulation for extending beyond a neighbouring standard; it also preserves the complementary framing intended by the English.

---

**Flag 11**

- **Line (approx):** 205-211
- **Current:** `PublicSchema est fondé sur une analyse comparative de six systèmes de protection sociale. Lorsque des normes internationales existent [...] nous les référençons. Lorsqu'elles n'existent pas, nous définissons un ensemble commun basé sur le fonctionnement réel de ces systèmes.`
- **Issue:** "nous les référençons" is a calque of "we reference them". In French standards writing, systems or documents do not "référencer" a standard in this intransitive/ergative sense; one says "nous nous y référons", "nous les citons", or "nous les adoptons comme référence". "Référencer" in French more commonly means to index or list, as in SEO or cataloguing.
- **Proposed:** `Lorsque des normes internationales existent [...] nous nous y référons. Lorsqu'elles n'existent pas, nous définissons un ensemble commun fondé sur le fonctionnement réel de ces systèmes.`
- **Rationale:** "nous nous y référons" is the correct reflexive construction; also replaces the second "basé sur" with "fondé sur" for stylistic consistency with line 207.

---

**Flag 12**

- **Line (approx):** 218
- **Current:** `Voir comment les systèmes se comparent`
- **Issue:** "se comparer" used reflexively here implies the systems are comparing themselves to each other (mutual action), which is an odd anthropomorphism. The English "See how systems compare" means "see how they measure up / how they stack up". The natural French would be "Comparer les systèmes" or "Voir la comparaison des systèmes".
- **Proposed:** `Comparer les systèmes`
- **Rationale:** Active imperative is cleaner and avoids the reflexive-action ambiguity; it also matches the brevity of other CTA links on the page.

---

**Flag 13**

- **Line (approx):** 228
- **Current:** `"Je coordonne des programmes qui servent des populations qui se recoupent"`
- **Issue:** "des populations qui se recoupent" is a literal calque of "overlapping populations". While "se recouper" is understandable, the standard French policy term for overlapping beneficiary populations is "populations dont les bénéficiaires se chevauchent" or, more concisely, "populations communes" or "publics cibles communs". "Se recouper" in French more naturally means "to cross-check" or "to verify" (as in verifying stories that corroborate each other), not "to overlap geographically or demographically".
- **Proposed:** `"Je coordonne des programmes qui servent des publics cibles communs"`
- **Rationale:** "publics cibles communs" is the standard term in francophone social protection coordination documents; it avoids the false-friend risk of "se recouper".

---

**Flag 14**

- **Line (approx):** 240
- **Current:** `"Je construis ou maintiens des intégrations entre systèmes"`
- **Issue:** "Je construis" for "I build" in the sense of developing software integrations is marginally acceptable but atypical in francophone IT/IS contexts, where "développer", "concevoir", or "mettre en place" are standard. "Construis" reads slightly informal and more concrete (building a wall) than the abstract software meaning.
- **Proposed:** `"Je développe ou maintiens des intégrations entre systèmes"`
- **Rationale:** "développer" is the standard verb for building software integrations in francophone technical registers.

---

**Flag 15**

- **Line (approx):** 241-244
- **Current:** `Vous avez besoin de noms de champs et de codes de valeurs partagés pour que les systèmes échangent des données sans couches de traduction personnalisées. Établissez la correspondance de votre système une fois ; chaque autre système correspondant devient interopérable.`
- **Issue:** "Établissez la correspondance de votre système une fois" is a near-literal calque of "Map your system once" that reads awkwardly. In French, "mapper" (from English "map") has entered technical usage but "établir la correspondance" is formal and natural. However, "Établissez la correspondance de votre système" is unusual: in French one "établit la correspondance entre deux systèmes" (between) or "établit la table de correspondance de son système", not "la correspondance de votre système" as a standalone object. Also "chaque autre système correspondant" is ambiguous (another mapped system, or a system that corresponds in some other sense).
- **Proposed:** `Vous avez besoin de noms de champs et de codes de valeur partagés pour que les systèmes échangent des données sans couches de traduction sur mesure. Établissez la correspondance de votre système avec PublicSchema une fois ; tout autre système déjà mappé devient automatiquement interopérable.`
- **Rationale:** "avec PublicSchema" clarifies the direction of the mapping; "sur mesure" replaces "personnalisées" (which can mean personalised, a different concept); "tout autre système déjà mappé" replaces the ambiguous "correspondant"; "codes de valeur" corrects the repeated plural-on-valeur issue from Flag 1.

---

**Flag 16**

- **Line (approx):** 252-256
- **Current:** `Vous avez besoin de spécifications d'interopérabilité concrètes pour votre appel d'offres, pas &ldquo;le système doit être interopérable.&rdquo; Référencez les propriétés et codes de vocabulaire de PublicSchema pour que les fournisseurs aient une cible vérifiable.`
- **Issue:** "Référencez" as an imperative (second-person plural) is technically correct but unusual in francophone policy writing for a user-facing instruction. "Citez", "utilisez" or "intégrez" are more natural. Additionally "codes de vocabulaire" is a calque of "vocabulary codes"; the standard French term in this domain is "codes de nomenclature" or simply "codes de valeur".
- **Proposed:** `Vous avez besoin de spécifications d'interopérabilité concrètes pour votre appel d'offres, pas simplement « le système doit être interopérable ». Citez les propriétés et codes de valeur de PublicSchema pour que les prestataires disposent d'une cible vérifiable.`
- **Rationale:** "Citez" is the natural imperative in this context; "prestataires" is the more internationally neutral term for vendors in a procurement context (vs "fournisseurs", which skews toward goods); "codes de valeur" is consistent with the correction applied throughout.

---

**Flag 17**

- **Line (approx):** 265-268
- **Current:** `Vous avez besoin d'un cadre structuré pour la comparaison afin que les divergences deviennent visibles et nommables. L'inventaire des concepts et propriétés de PublicSchema vous fournit une grille commune sur laquelle vous appuyer.`
- **Issue:** "nommables" is a literal calque of "nameable". While the word exists in French, it is rare and sounds academic in a policy document. "Identifiables et documentables" or "repérables et désignables" are more natural. "Une grille commune sur laquelle vous appuyer" is also slightly awkward; the preposition "sur" with "s'appuyer" requires the reflexive, so the correct construction is "sur laquelle s'appuyer" (impersonal) or rephrase entirely.
- **Proposed:** `Vous avez besoin d'un cadre structuré pour que les divergences deviennent visibles et identifiables. L'inventaire des concepts et propriétés de PublicSchema vous offre une grille commune de référence.`
- **Rationale:** "identifiables" is natural and precise; "une grille commune de référence" is a standard policy formulation that avoids the reflexive construction problem.

---

**Flag 18**

- **Line (approx):** 278-282
- **Current:** `Les concepts universels comme Personne et Ménage s'appliquent tels quels. Là où les programmes de votre pays ont besoin de plus (catégories de prestations spécifiques, codes de ciblage par variables proxy, identifiants hérités), étendez PublicSchema dans votre propre espace de noms. L'interopérabilité est préservée ; la spécificité locale n'est pas perdue.`
- **Issue:** "codes de ciblage par variables proxy" is a calque of "proxy-means codes". In francophone social protection, the standard term is "indicateurs de substitution" or "scores de ciblage par approximation" or simply "critères de ciblage indirect". "Variables proxy" is an anglicism used in econometric literature but is not standard in operational policy documents. "Identifiants hérités" is a reasonable translation of "legacy identifiers", though "identifiants existants" or "identifiants issus des systèmes antérieurs" would be clearer to a non-technical policy reader. Also, "espace de noms" recurs here (see Flag 4).
- **Proposed:** `Les concepts universels comme Personne et Ménage s'appliquent tels quels. Là où les programmes de votre pays ont besoin de plus (catégories de prestations spécifiques, scores de ciblage indirect, identifiants existants), étendez PublicSchema dans votre propre espace de définition. L'interopérabilité est préservée ; la spécificité locale n'est pas perdue.`
- **Rationale:** "scores de ciblage indirect" is more accessible to a policy officer than "variables proxy"; "identifiants existants" is clearer than "hérités" for a non-technical reader; "espace de définition" is consistent with Flag 4.

---

## Overall impression

The translation is competent and readable: it covers the full source text without significant omissions, the sentence boundaries are mostly well-chosen, and the domain terminology is generally appropriate. However, it is not yet shippable for a professional international policy audience. The two systemic problems are: (1) a consistent pattern of calqued syntax, particularly with "de valeurs", "se comparer", "déplacer des dossiers", "en premier lieu", and "nommables", all of which carry meaning shifts that would register immediately with a francophone policy officer; and (2) a handful of France-specific or developer-register terms ("référencer" as a transitive verb, "espace de noms", "variables proxy") that would read as odd or technical in an international context. The fixes are targeted: no section needs full re-drafting, but all 18 flags should be addressed before publication.

