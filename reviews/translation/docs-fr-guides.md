# French translation review — guides docs

## data-model-guide.md

**Overall impression:** The translation is competent and generally readable. The structure and technical content are faithfully rendered. However, several passages carry calques from English, a few phrasings sound stiff or unnatural in spoken/written French, and one term ("appel d'offres" vs. "appel d'offres") is used correctly but inconsistently in headings vs. body text. Nothing is France-coded in a disqualifying way, though "appel d'offres" is standard Francophone administrative vocabulary and is fine. The main issues are phrasing-level calques and one register problem.

### Flagged passages

**Line 3 — Current:** "Plutôt que de greffer la compatibilité après coup, vous concevez votre modèle de données en utilisant PublicSchema comme référence."
**Issue:** Calque. "Greffer la compatibilité" is an awkward metaphor borrowed from the English "retrofitting." "Greffer" (to graft) is technically possible but sounds odd in a technical policy document. The English "retrofitting" is already a metaphor; the French translation should use a more natural equivalent.
**Proposed:** "Plutôt que d'intégrer la compatibilité après coup, vous concevez votre modèle de données en prenant PublicSchema comme référence."
**Rationale:** "Intégrer ... après coup" is the standard Francophone phrase for retrofitting a feature. "En utilisant" is correct but slightly heavier than "en prenant ... comme référence."

---

**Line 36 — Current:** "Là où PublicSchema définit un ensemble de valeurs contrôlées (statut d'inscription, genre, canal de livraison), votre système utilise les mêmes codes ou peut les traduire trivialement."
**Issue:** "Traduire trivialement" is a calque of "translate to them trivially." "Trivialement" exists in French but sounds academic/mathematical in this context; a policy practitioner would find it cold. Also, "peut les traduire trivialement" is awkward word order.
**Proposed:** "Là où PublicSchema définit un ensemble de valeurs contrôlées (statut d'inscription, genre, canal de livraison), votre système utilise les mêmes codes ou peut les convertir sans effort."
**Rationale:** "Convertir sans effort" is natural and immediately understood by a non-technical reader. "Trivialement" is a false friend with "trivially" and carries the wrong register.

---

**Line 37 — Current:** "Compte tenu de ce qui précède, votre système peut produire des exports ou des réponses d'API alignés avec les noms de propriétés et les codes de vocabulaire PublicSchema."
**Issue:** "Compte tenu de ce qui précède" is a legalese/bureaucratic phrase that feels heavy in a how-to guide. The English original says simply "Given the above."
**Proposed:** "Sur cette base, votre système peut produire des exports ou des réponses d'API alignés sur les noms de propriétés et les codes de vocabulaire PublicSchema."
**Rationale:** "Sur cette base" is neutral, clear, and natural in a technical guide. Also, "alignés avec" should be "alignés sur" (standard preposition in French for "aligned to/with a reference").

---

**Line 39 — Current:** "La compatibilité concerne l'alignement sémantique, pas la conformité structurelle."
**Issue:** Minor register issue. "Concerne" is correct but slightly formal; "porte sur" or "est une question d'" would flow more naturally. More importantly, "conformité structurelle" is a calque of "structural conformity" and sounds stiff.
**Proposed:** "La compatibilité est une question d'alignement sémantique, non de conformité de structure."
**Rationale:** "Est une question de" is the natural Francophone idiom for "is about." "Conformité de structure" is lighter than "conformité structurelle" in spoken register, though either is acceptable; the bigger fix is the verb phrase.

---

**Line 73 — Current:** "C'est le choix de conception à la valeur ajoutée la plus élevée car il élimine le besoin de traduction de codes dans chaque future intégration."
**Issue:** Calque of "the single highest-value design choice." "Le choix de conception à la valeur ajoutée la plus élevée" is grammatically correct but sounds like it was assembled word-for-word from English. It is laboured.
**Proposed:** "C'est le choix de conception le plus rentable, car il élimine la nécessité de traduire les codes à chaque nouvelle intégration."
**Rationale:** "Le plus rentable" captures "highest-value" naturally in a cost-benefit framing. "La nécessité de traduire les codes" flows better than "le besoin de traduction de codes." "Chaque future intégration" becomes "chaque nouvelle intégration," which is more natural.

---

**Line 75 — Current:** "Intégrez cette correspondance dans votre système dès le début, pas comme une réflexion après coup."
**Issue:** "Réflexion après coup" is a calque of "afterthought." While "après coup" is genuinely French, the phrase "réflexion après coup" in this specific construction is still a calque. The natural idiom is "en y pensant au dernier moment" or simply "à la dernière minute."
**Proposed:** "Intégrez cette correspondance dans votre système dès le départ, et non en dernière minute."
**Rationale:** "Dès le départ" is slightly more natural than "dès le début" here, and "en dernière minute" is the standard idiomatic contrast to planning ahead. "Dès le début" is not wrong but "dès le départ" is the more common choice in this type of recommendation.

---

**Line 95 — Current:** "Si des colonnes sont vides ou si des valeurs ne correspondent pas aux listes déroulantes, examinez les lacunes."
**Issue:** "Listes déroulantes" is the correct French for "dropdowns" in a UI context, so that is fine. However, "examinez les lacunes" is a calque of "investigate the gaps" — "examiner" means to examine/inspect, not to investigate in the sense of digging deeper. The English "investigate" implies active follow-up.
**Proposed:** "Si des colonnes sont vides ou si des valeurs ne correspondent pas aux listes déroulantes, analysez les écarts."
**Rationale:** "Analyser les écarts" is the standard expression in Francophone quality/data contexts for investigating gaps. "Lacunes" is correct but "écarts" is more precise here (a mismatch between expected and actual).

---

**Line 119 — Current:** "La borne temporelle est de première importance"
**Issue:** This is the heading for the "Time-boundedness is first-class" section. "De première importance" means "of primary importance," which is a reasonable rendering of "first-class," but it changes the meaning. "First-class" in a data modelling context means "a core, explicitly modelled concept" rather than merely "very important." The current translation loses the technical nuance.
**Proposed:** "La délimitation temporelle est un concept de premier plan"
**Rationale:** "De premier plan" better captures "first-class" in the sense of being a central, explicitly supported feature of the model. Alternatively, "La temporalité est traitée en priorité" could work, but "de premier plan" is closer to the technical meaning. Note: "borne temporelle" (temporal bound) is a calque; "délimitation temporelle" or "dimension temporelle" reads more naturally.

---

**Line 121 — Current:** "Concevez votre schéma pour prendre en charge ce modèle plutôt que de stocker uniquement l'état courant."
**Issue:** "L'état courant" is a calque of "current state." In French data/software contexts, the standard phrase is "l'état actuel" or simply "l'état en cours."
**Proposed:** "Concevez votre schéma pour prendre en charge ce modèle plutôt que de ne stocker que l'état actuel."
**Rationale:** "L'état actuel" is the standard Francophone data term. "L'état courant" exists but is less common outside of certain technical contexts and reads as a literal translation.

---

**Line 135 — Current (table cell):** "Liste de contrôle pour la revue de conception champ par champ"
**Issue:** "Revue de conception" is a calque of "design review." In French, the standard term for a structured review of technical design work is "revue de conception" in engineering contexts, so this is actually acceptable. However, "champ par champ" (field-by-field) sounds slightly mechanical.
**Proposed:** No change needed. "Revue de conception" is standard in Francophone engineering and MIS contexts. This passage is acceptable.

---

**Line 143 — Current (table cell):** "Alimentation des tables de correspondance dans votre base de données"
**Issue:** "Alimentation" (feeding/populating) is correct French for seeding/populating, but in a data context "alimentation des tables" can sound like a food metaphor to non-technical readers. The English says "Seeding lookup tables."
**Proposed:** "Initialisation des tables de correspondance dans votre base de données"
**Rationale:** "Initialisation" or "remplissage" are both natural alternatives. "Alimentation" is not wrong and is used in French data engineering ("alimentation d'une base"), so this is a minor point. Flag for consideration rather than a firm correction.

---

## vocabulary-adoption-guide.md

**Overall impression:** This file reads more naturally than the data model guide. The step-by-step structure translates well, the vocabulary is accessible, and there are no France-coded terms. A handful of calques and one awkward term are worth correcting.

### Flagged passages

**Line 3 — Current:** "C'est la façon la plus légère d'utiliser PublicSchema."
**Issue:** "La façon la plus légère" is a calque of "the lightest way." "Légère" in this sense (low-overhead, minimal) is not idiomatic in French outside of aviation/physics. A French speaker would say "la manière la moins contraignante" or "l'approche la plus simple."
**Proposed:** "C'est l'approche la plus simple pour utiliser PublicSchema."
**Rationale:** "L'approche la plus simple" is natural and keeps the meaning. "Légère" is not wrong but it borrows the English "lightweight" framing, which does not translate cleanly.

---

**Line 21 — Current:** "Vous voulez un gain rapide avant de vous engager dans une intégration plus approfondie."
**Issue:** "Un gain rapide" is a direct calque of "a quick win." While understood, "gain rapide" is not natural French phrasing in this context.
**Proposed:** "Vous souhaitez obtenir des résultats concrets rapidement avant de vous engager dans une intégration plus approfondie."
**Rationale:** "Obtenir des résultats concrets rapidement" is the natural French equivalent of "a quick win" in a policy/project context. Alternatively, "une victoire rapide" exists but sounds odd; "un résultat tangible à court terme" is another option.

---

**Line 75 — Current:** "Par exemple, 'pending' dans votre système peut signifier 'en attente d'approbation' tandis que le 'pending' canonique signifie 'en attente de paiement'."
**Issue:** Using the English word 'pending' in quotes within a French explanation is unavoidable for code references, but the sentence structure is slightly awkward. This is a borderline issue. More importantly, "canonique" appears several times in this document as an adjective, which is a calque of "canonical" used as a technical term. In French, "canonique" exists (especially in mathematics and linguistics) and is acceptable in a technical document, but "de référence" is more accessible to a policy audience.
**Proposed (for "canonique" used throughout):** Consider replacing "le 'pending' canonique" with "le code de référence 'pending'," and similarly reviewing uses of "codes canoniques" throughout the document. A global replacement of "canonique/canoniques" with "de référence" would improve accessibility for non-technical readers.
**Rationale:** "Canonique" is understood by technical staff but may be opaque to policy officers, who are part of the target audience. "De référence" or "normalisé" communicate the same concept more accessibly.

---

**Line 81 — Current:** "Ajoutez une colonne à votre export qui traduit les codes internes en codes canoniques. Votre modèle de rapportage fait référence à la colonne canonique."
**Issue:** "Votre modèle de rapportage" is a calque of "your reporting template." In French, "modèle de rapport" or "modèle de rapportage" are both used; "rapportage" is accepted in Francophone international development contexts, so this is acceptable. However, "fait référence à" is slightly formal; "pointe vers" or "utilise" would be more direct.
**Proposed:** "Votre modèle de rapport utilise la colonne de référence."
**Rationale:** "Utilise" is clearer than "fait référence à" in a how-to instruction. "La colonne de référence" is more natural than "la colonne canonique."

---

**Line 97 — Current:** "Là où les codes de votre système ne correspondent pas à l'ensemble canonique, la lacune est visible et documentée plutôt que cachée dans des traductions ad hoc."
**Issue:** "L'ensemble canonique" (the canonical set) is another instance of the "canonique" calque noted above. "Des traductions ad hoc" borrows the Latin "ad hoc" which is acceptable in formal French but slightly out of register here.
**Proposed:** "Là où les codes de votre système ne correspondent pas à l'ensemble de référence, l'écart est visible et documenté plutôt que masqué dans des traductions improvisées."
**Rationale:** "L'ensemble de référence" replaces "l'ensemble canonique." "Masqué" is more precise than "caché" (which is also correct). "Traductions improvisées" replaces "traductions ad hoc" with a fully French expression that carries the same meaning.

---

**Line 98 — Current:** "Si vous souhaitez ultérieurement aligner les noms de champs, adopter des schémas JSON ou émettre des attestations, la correspondance de vocabulaire est déjà faite."
**Issue:** No major issue. This reads naturally. Minor note: "émettre des attestations" correctly follows the project convention for "issue credentials." This is fine.
**Proposed:** No change needed.

---

**Line 103 — Current:** "Si votre système utilise déjà des codes d'une norme internationale (par exemple, ISO 3166 pour les pays), vérifiez si PublicSchema référence la même norme."
**Issue:** "PublicSchema référence la même norme" — the verb "référencer" used intransitively like this is a calque of "references." In French, "faire référence à" or "renvoyer à" is more idiomatic.
**Proposed:** "Si votre système utilise déjà des codes d'une norme internationale (par exemple, ISO 3166 pour les pays), vérifiez si PublicSchema renvoie à la même norme."
**Rationale:** "Renvoie à la même norme" is the natural French expression. "Référencer" as a transitive verb ("référencer une norme") is acceptable, but "PublicSchema référence la même norme" without an explicit object marker reads strangely.

---

## use-cases.md

**Overall impression:** This is the strongest of the three translations. The scenario-based format translates well, the language is clear and accessible, and the register is appropriate for an international policy audience. There are a few calques and one structural issue with a repeated sentence pattern, but no France-coded vocabulary. Minimal corrections needed.

### Flagged passages

**Line 3 — Current:** "Les façons de l'utiliser sont nombreuses, de l'alignement des codes de vocabulaire dans des tableurs à l'émission d'attestations vérifiables."
**Issue:** "Les façons de l'utiliser sont nombreuses" is a slightly awkward inversion; it delays the subject. The English is "There are many ways to use it." In French, a more natural construction would keep the flow of the sentence.
**Proposed:** "Il existe de nombreuses façons de l'utiliser, de l'alignement des codes de vocabulaire dans des tableurs à l'émission d'attestations vérifiables."
**Rationale:** "Il existe de nombreuses façons" is the standard French construction for "there are many ways." The current phrasing is grammatically correct but reads as a calque of the English structure.

---

**Line 23 — Current:** "Même lorsque les champs peuvent être mis en correspondance par leur nom, des codes divergents rendent la comparaison peu fiable : 'active' dans un système peut ne pas avoir le même sens que 'active' dans un autre."
**Issue:** "Mis en correspondance" (put in correspondence) is the correct French for "mapped," but this phrase recurs frequently throughout all three documents. It is slightly mechanical. In some of these occurrences "appariés" or "associés" would be more natural. This specific instance is borderline acceptable, but flagged for consistency review.
**Proposed:** "Même lorsque les champs peuvent être associés par leur nom, des codes divergents rendent la comparaison peu fiable."
**Rationale:** "Associés par leur nom" is slightly more natural in this description of a practical problem than "mis en correspondance par leur nom." Reserve "mis en correspondance" / "correspondance" for when the mapping is the deliberate technical act (building a mapping table), not a description of informal name-matching.

---

**Line 33 — Current:** "Rappeler le système d'origine peut être peu pratique ou impossible."
**Issue:** "Rappeler le système d'origine" is ambiguous in French. "Rappeler" means both "to call back" and "to recall/remember." The English "Calling back to the origin system" means making a remote API call. The French "rappeler" in a technical context could be misread as "to recall" the system (i.e., to remember it or to decommission it).
**Proposed:** "Interroger le système du pays d'origine peut être difficile ou impossible."
**Rationale:** "Interroger un système" is the standard French technical term for calling/querying a remote system. "Peut être difficile ou impossible" replaces "peu pratique ou impossible," which itself is a minor calque of "impractical or impossible" (though "peu pratique" is acceptable French).

---

**Line 35 — Current:** "Le pays d'accueil peut vérifier l'attestation hors ligne car elle utilise un schéma partagé."
**Issue:** No issue with the French itself. However, this sentence uses "attestation" (singular) but the preceding sentence uses "une attestation vérifiable (verifiable credential)." The parenthetical English term in line 35 is appropriate for first introduction. In line 35, the reference back to "l'attestation" is clean. This is fine.
**Proposed:** No change needed.

---

**Line 44 — Current:** "L'agrégation des chiffres entre programmes nécessite une traduction manuelle à chaque cycle de rapportage."
**Issue:** "Cycle de rapportage" is a calque of "reporting cycle." The Francophone international development equivalent is "cycle de rapport" or "période de rapport." "Rapportage" is gaining acceptance in Francophone contexts (particularly Francophone Africa and international organisations), so this is a minor flag rather than a clear error.
**Proposed:** "L'agrégation des chiffres entre programmes nécessite une traduction manuelle à chaque période de rapport."
**Rationale:** "Période de rapport" is more universally understood. "Cycle de rapportage" is acceptable in certain Francophone contexts but "période de rapport" is safer for a pan-Francophone audience.

---

**Line 43 — Current:** "Lorsque ces traductions sont approximatives (parce que les codes d'un programme ne correspondent pas clairement à ceux d'un autre), les chiffres agrégés ne sont pas fiables."
**Issue:** "Approximatives" is used to translate "lossy." While "lossy" in information theory means data is lost in translation, "approximatives" means imprecise/rough, which is close but not identical. A more precise French translation would signal that information is actually lost.
**Proposed:** "Lorsque ces traductions entraînent des pertes (parce que les codes d'un programme ne correspondent pas clairement à ceux d'un autre), les chiffres agrégés ne sont pas fiables."
**Rationale:** "Entraînent des pertes" directly conveys the "lossy" concept (information loss). "Approximatives" softens the problem too much for a policy audience who need to understand the data quality risk.

---

**Line 55 — Current:** "Cela fonctionne que vous passiez un marché pour un registre social, un système d'information scolaire ou une base de données de structures de santé."
**Issue:** "Structures de santé" (health facilities/structures) is a standard Francophone public health term used across sub-Saharan Africa and international organisations, so this is appropriate. No change needed.
**Proposed:** No change needed.

---

**Line 62 — Current:** "Une autorité d'enregistrement des faits d'état civil (état civil) délivrant des actes de naissance, connectée à des programmes qui inscrivent automatiquement les nouveau-nés (assurance maladie, allocations pour enfants, suivi de la vaccination)."
**Issue:** "Inscrivent automatiquement" is a calque of "auto-enroll." In French, "enrôler automatiquement" is more natural in a social protection context, or "enregistrent automatiquement." "Inscrire" tends to be used for education/training contexts. Also, "allocations pour enfants" for "child grants" is acceptable for a pan-Francophone audience (noting that "allocations familiales" is France-coded, but "allocations pour enfants" is neutral enough).
**Proposed:** "connectée à des programmes qui enrôlent automatiquement les nouveau-nés (assurance maladie, allocations destinées aux enfants, suivi de la vaccination)"
**Rationale:** "Enrôler" is the standard term in Francophone social protection for "enroll" (a person in a programme). "Inscrire" is used more for schools. "Allocations destinées aux enfants" is a very minor rewording to avoid any echo of the France-specific "allocations pour enfants/allocations familiales" framing, though "allocations pour enfants" is sufficiently neutral.

---

**Line 85 — Current:** "La vérification fonctionne hors ligne car elle est cryptographique, et non une interrogation de base de données."
**Issue:** "Une interrogation de base de données" is a calque of "a database lookup." While "interrogation" is the correct French database term (SQL queries are "requêtes d'interrogation"), "une interrogation de base de données" sounds slightly technical in this policy-facing document. However, it is correct and the contrast being made is clear.
**Proposed:** No change needed. The technical contrast is clear enough and "interrogation de base de données" is standard French data terminology.

---

**Line 105 — Current:** "Le résultat rend les divergences visibles et nommables : le pays A collecte les coordonnées GPS des ménages, le pays B non."
**Issue:** "Nommables" is a calque of "nameable." While technically a French word, it is not commonly used in policy documents and sounds awkward.
**Proposed:** "Le résultat rend les divergences visibles et identifiables : le pays A collecte les coordonnées GPS des ménages, le pays B non."
**Rationale:** "Identifiables" is the natural French term here. Something that is "visible and nameable" in English means it can be seen and precisely labelled; "visibles et identifiables" captures this in natural French.

---

**Line 115 — Current:** "Chaque agence conserve son schéma interne ; elle ajoute simplement une surface d'API alignée sur PublicSchema."
**Issue:** "Une surface d'API" is a calque of "an API surface." In French technical documentation, "surface d'API" is sometimes used, but "une interface API" or "un point d'accès API" is more natural and widely understood.
**Proposed:** "Chaque agence conserve son schéma interne ; elle expose simplement une interface API alignée sur PublicSchema."
**Rationale:** "Expose une interface API" is the standard Francophone expression for publishing an API surface. "Ajoute simplement une surface d'API" is technically intelligible but reads as an English calque.
