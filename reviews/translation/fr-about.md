# French translation review: AboutContent

Scope: full review of `AboutContent.fr.astro` against the English source, checking for unnatural phrasing, calques, anglicisms, and register mismatches for a francophone policy-practitioner audience.

---

## Flagged passages

**Line (approx): 12**
- **Current:** `Ce que PublicSchema fournit`
- **Issue:** Calque of "What PublicSchema provides"; "fournit" is technically correct but reads as a literal verb lift from the English. The natural heading in institutional French uses a noun phrase.
- **Proposed:** `Ce que PublicSchema propose` or `Les ressources de PublicSchema`
- **Rationale:** "Propose" (offers, puts forward) is the standard verb in French institutional writing for presenting a toolkit or framework; "fournit" sounds like a product specification.

---

**Line (approx): 17**
- **Current:** `Il fournit :`
- **Issue:** Same "fournit" issue as the heading; the pronoun "Il" referring back to "PublicSchema" is fine, but the verb is stilted.
- **Proposed:** `Il comprend :`
- **Rationale:** "Comprend" (includes/comprises) is the idiomatic choice in French technical documents when listing the components of a framework.

---

**Line (approx): 19**
- **Current:** `entités sémantiques (Personne, Inscription, Paiement, et autres) avec des définitions rédigées pour les praticiens des politiques publiques, pas pour les développeurs`
- **Issue:** "praticiens des politiques publiques" is a calque of "policy practitioners". The phrase exists in French but feels academic and awkward in this context; a senior policy officer would not self-describe this way.
- **Proposed:** `entités sémantiques (Personne, Inscription, Paiement, entre autres) avec des définitions accessibles aux professionnels des politiques publiques, et non aux seuls développeurs`
- **Rationale:** "accessibles aux professionnels de" is the natural register; "et non aux seuls" is a more idiomatic contrast construction than "pas pour".

---

**Line (approx): 21**
- **Current:** `nous définissons un ensemble canonique avec des correspondances vers la manière dont des systèmes spécifiques encodent les mêmes valeurs`
- **Issue:** "vers la manière dont des systèmes spécifiques encodent les mêmes valeurs" is a heavy calque; "encodent" is an anglicism in this context, and "la manière dont" is wordy.
- **Proposed:** `nous définissons un ensemble canonique accompagné de correspondances avec la façon dont différents systèmes représentent ces mêmes valeurs`
- **Rationale:** "représentent" is the natural verb here; "différents systèmes" flows better than "des systèmes spécifiques" (which reads as if only certain systems are meant).

---

**Line (approx): 22**
- **Current:** `Schémas d'identifiants vérifiables`
- **Issue:** "identifiants vérifiables" is a mistranslation of "Credential schemas". "Verifiable Credentials" are "attestations vérifiables" or "justificatifs vérifiables" in standard francophone usage (EU, W3C working group translations). "Identifiant" means identifier, not credential.
- **Proposed:** `Schémas d'attestations vérifiables`
- **Rationale:** The W3C French working group and EU documents consistently use "attestation vérifiable" for Verifiable Credential; "identifiant" misleads readers into thinking this is about identifiers (like a national ID number).

---

**Line (approx): 22**
- **Current:** `pour émettre des données de concepts sous forme de <a ...>Titres vérifiables (Verifiable Credentials)</a>`
- **Issue:** "Titres vérifiables" is an unusual coinage. "Titre" in French usually means a title (of a document or a person), a security (financial), or an entitlement. It does not carry the credential/attestation meaning naturally. Also "données de concepts" is an odd collocation.
- **Proposed:** `pour publier des données sous forme d'<a ...>attestations vérifiables (Verifiable Credentials)</a>`
- **Rationale:** "Attestation vérifiable" is the established French equivalent. "Publier" is more natural than "émettre" in the context of digital schemas, though "émettre" is acceptable; the main fix is the noun.

---

**Line (approx): 25-26**
- **Current:** `Les pays et les programmes adoptent ce dont ils ont besoin et étendent ce qui manque.`
- **Issue:** "étendent ce qui manque" is a calque of "extend what they don't" (have). The English relies on an elided clause; the French makes it sound like programs extend things that are missing, which is slightly odd.
- **Proposed:** `Les pays et les programmes adoptent ce qui s'applique à leur contexte et complètent ce qui ne correspond pas.`
- **Rationale:** "Complètent" or "adaptent" is the natural verb; the French version preserves the meaning without the awkward ellipsis.

---

**Line (approx): 35-36**
- **Current:** `Les définitions portent un poids sémantique, pas seulement une structure.`
- **Issue:** "portent un poids sémantique" is a direct calque of "carry semantic weight". The expression "porter un poids" exists in French but in this technical context it sounds metaphorical in the wrong register.
- **Proposed:** `Les définitions ont une portée sémantique, pas seulement structurelle.`
- **Rationale:** "Avoir une portée sémantique" is the standard phrasing in French linguistics and standards documents.

---

**Line (approx): 36-37**
- **Current:** `La délimitation temporelle est de première importance.`
- **Issue:** "de première importance" is an unusual rendering of "first-class" (as in a first-class citizen in a data model). "First-class" here means "built in at the foundation level, not an afterthought"; "de première importance" means "very important" in French, losing the technical meaning.
- **Proposed:** `La dimension temporelle est traitée comme un élément fondamental du modèle.`
- **Rationale:** The English "first-class" is a technical idiom meaning the concept has native support in the model. The French needs to convey that idea explicitly, not just "important".

---

**Line (approx): 47-48**
- **Current:** `Il se situe au niveau de la couche de données de prestation : entre les normes d'identité, l'interopérabilité des API et l'infrastructure de confiance.`
- **Issue:** "couche de données de prestation" is a calque of "delivery data layer". In French, stacking three nouns this way ("données de prestation") is grammatically possible but heavy and uncommon in institutional writing.
- **Proposed:** `Il occupe la couche de données relative à la prestation de services : entre les normes d'identité, l'interopérabilité des API et l'infrastructure de confiance.`
- **Rationale:** "Relative à la prestation de services" unpacks the English compound noun into readable French; "occupe" is more natural than "se situe au niveau de".

---

**Line (approx): 63**
- **Current:** `Vocabulaire de domaine au sein des identifiants vérifiables`
- **Issue:** Same "identifiants vérifiables" error as line 22. Also "au sein de" is fine but reads slightly heavy for a table cell.
- **Proposed:** `Vocabulaire métier au sein des attestations vérifiables`
- **Rationale:** "Vocabulaire métier" is the standard term in francophone interoperability documents for domain vocabulary; "attestations vérifiables" corrects the translation error.

---

**Line (approx): 68**
- **Current:** `Données du cycle de vie de la prestation au-delà du nom, de la naissance et de la citoyenneté`
- **Issue:** This table cell is syntactically correct but very heavy for a comparison table cell. The chain "du nom, de la naissance et de la citoyenneté" is grammatically fine but the whole phrase reads as a translation rather than as a terse table entry.
- **Proposed:** `Données du cycle de vie de la prestation, au-delà de l'identité civile`
- **Rationale:** "Identité civile" (name, birth, citizenship together) is a standard French administrative term that compresses the three items into one natural expression, as a table cell should be.

---

**Line (approx): 73**
- **Current:** `Qui reçoit quoi, pas quels services existent`
- **Issue:** "pas quels services existent" is grammatically awkward; the verb "existent" dangling at the end of a table cell without a subject pronoun sounds clipped in the wrong way.
- **Proposed:** `Qui reçoit quoi, et non quels services sont disponibles`
- **Rationale:** "Et non" is the standard contrastive in French institutional writing (vs. "pas" which is more colloquial here); "sont disponibles" reads more naturally than the bare "existent".

---

**Line (approx): 77**
- **Current:** `Sémantique partagée derrière les contrats d'API`
- **Issue:** "derrière" (behind) is a spatial metaphor that is a calque of English "behind the API contracts". In French technical writing, "sous-jacente à" or "au fondement de" is the natural phrasing.
- **Proposed:** `Sémantique partagée sous-jacente aux contrats d'API`
- **Rationale:** "Sous-jacente à" is the standard French equivalent of "underlying" or "behind" in a technical/conceptual sense.

---

**Line (approx): 81**
- **Current:** `Modèles de données pour l'échange, pas seulement des indicateurs`
- **Issue:** "pas seulement des indicateurs" reads as a direct calque. The contrast is between exchange data models and statistical indicators; the French is technically correct but tonally casual for a table cell.
- **Proposed:** `Modèles de données pour l'échange, et non de simples indicateurs statistiques`
- **Rationale:** "Et non de simples" is the formal French contrastive; adding "statistiques" clarifies the meaning without ambiguity.

---

**Line (approx): 89**
- **Current:** `C'est le manque à combler`
- **Issue:** "Manque à combler" is correct French but slightly colloquial for a table cell in a technical reference document. It reads more like "that's the gap we need to fill" (conversational) than a concise descriptor.
- **Proposed:** `C'est le vide à combler`
- **Rationale:** "Vide" (void/gap) is more formal and direct in this context; "lacune" would also work: `C'est la lacune à combler`.

---

**Line (approx): 99-100**
- **Current:** `GovStack définit des blocs de construction pour le gouvernement numérique`
- **Issue:** "Blocs de construction" is a calque of "building blocks". The established French term in GovStack's own documentation and in UNDP/EU literature is "blocs fonctionnels" or simply the borrowed "building blocks".
- **Proposed:** `GovStack définit des blocs fonctionnels pour le gouvernement numérique`
- **Rationale:** "Blocs fonctionnels" is the term used in official French-language GovStack documentation; "blocs de construction" reads as a literal translation.

---

**Line (approx): 100-101**
- **Current:** `PublicSchema est le modèle de données partagé dont ces blocs ont implicitement besoin`
- **Issue:** "ont implicitement besoin" is a calque of "implicitly need". The word order and the adverb placement are non-standard; "implicitement" should come before the verb or the construction restructured.
- **Proposed:** `PublicSchema constitue le modèle de données partagé que ces blocs supposent implicitement`
- **Rationale:** "Supposent implicitement" (implicitly presuppose/require) is a natural collocation in French policy and standards writing; "constitue" is stronger than "est" here.

---

**Line (approx): 112**
- **Current:** `PublicSchema commence par la protection sociale : un domaine bien compris, en pleine transformation numérique, avec plusieurs systèmes open source et des problèmes immédiats d'interopérabilité.`
- **Issue:** "commence par" is a calque of "starts with". In French institutional writing, "débute par" or "prend pour point de départ" is more natural. Also "un domaine bien compris" is a calque of "well-understood domain"; "bien compris" in French tends to mean "widely grasped by people" rather than "well-defined and mature".
- **Proposed:** `PublicSchema prend pour point de départ la protection sociale : un domaine bien balisé, en pleine transformation numérique, disposant de plusieurs systèmes open source et confronté à des enjeux immédiats d'interopérabilité.`
- **Rationale:** "Bien balisé" (well-mapped/well-defined) is the natural expression for a domain that is mature and well-understood in terms of scope; "enjeux d'interopérabilité" is stronger and more policy-register than "problèmes d'interopérabilité".

---

**Line (approx): 119**
- **Current:** `au fur et à mesure que l'adoption progresse`
- **Issue:** No issue; this is natural French. (Not flagged.)

---

**Line (approx): 125**
- **Current:** `PublicSchema est un point de départ, pas un cadre imposé.`
- **Issue:** Minor register point. "Pas un cadre imposé" is acceptable but slightly abrupt. "Pas" in formal writing is often replaced by "non pas" or a restructured phrase. This is borderline; flagging as a polish item only.
- **Proposed:** `PublicSchema est un point de départ, non une obligation.`
- **Rationale:** "Non une obligation" is crisper and more formal; it directly echoes the English "not a mandate".

---

**Line (approx): 131**
- **Current:** `Les utiliser directement offre l'interopérabilité sans coût supplémentaire.`
- **Issue:** "offre l'interopérabilité sans coût supplémentaire" is a calque of "gives interoperability at no cost". "Sans coût supplémentaire" is correct but sounds like a commercial pitch. The English means "at no additional effort/overhead", not a financial cost.
- **Proposed:** `Les utiliser directement garantit l'interopérabilité sans effort supplémentaire.`
- **Rationale:** "Sans effort supplémentaire" conveys the intended meaning (no extra work required) and avoids the unintended commercial register of "coût".

---

**Line (approx): 134**
- **Current:** `Le vocabulaire évolue par l'adoption réelle, pas par la conception en comité.`
- **Issue:** "la conception en comité" is a calque of "committee design". In French, the idiomatic expression for this is "la conception par comité" (not "en comité") or more naturally "une conception de comité".
- **Proposed:** `Le vocabulaire évolue par l'adoption réelle, non par une conception de comité.`
- **Rationale:** "Une conception de comité" is the standard French expression (calqued or not, it is the established phrase); "par la conception en comité" is grammatically off.

---

**Line (approx): 143-144**
- **Current:** `Le projet est maintenu par Jeremi Joslin pour permettre des décisions rapides et tranchées dans les premières phases.`
- **Issue:** "décisions rapides et tranchées" is a translation of "fast, opinionated decisions". "Tranchées" (cut/sliced) is unusual here; the intended meaning is "clear-cut, decisive, taking a clear stance". "Tranchées" can work colloquially but is slightly odd in formal writing.
- **Proposed:** `Le projet est maintenu par Jeremi Joslin pour permettre des prises de décision rapides et assumées dans les premières phases.`
- **Rationale:** "Prises de décision assumées" (decisions that own a point of view) conveys "opinionated" more naturally in French than "tranchées".

---

**Line (approx): 144-145**
- **Current:** `Les retours des experts du domaine, des implémenteurs de systèmes et des organismes de normalisation sont activement sollicités.`
- **Issue:** "implémenteurs de systèmes" is a calque and a borrowing. "Implémenteur" is not a standard French word; the standard term is "intégrateur" or "concepteur de systèmes" in francophone public-sector writing.
- **Proposed:** `Les contributions des experts du domaine, des intégrateurs de systèmes et des organismes de normalisation sont activement sollicitées.`
- **Rationale:** "Intégrateur" is the established French professional term for system implementer in the public-sector IT context; "contributions" is slightly more formal than "retours" (which can sound like user feedback/returns).

---

**Line (approx): 148-149**
- **Current:** `d'abord à un groupe consultatif de contributeurs et d'experts du domaine, puis à une structure formelle multi-parties prenantes`
- **Issue:** "multi-parties prenantes" is a calque of "multi-stakeholder". The standard French term in international policy and UN documents is "multipartite" or "à parties prenantes multiples". "Multi-parties prenantes" used as a compound adjective is non-standard.
- **Proposed:** `d'abord à un groupe consultatif de contributeurs et d'experts du domaine, puis à une structure formelle multipartite`
- **Rationale:** "Multipartite" is the standard adjective in international French policy and governance documents (UNESCO, UN, EU); it is concise and unambiguous.

---

**Line (approx): 153-154**
- **Current:** `Concepts et propriétés avec des URI stables. Définitions rédigées pour les praticiens du domaine. Publié sous forme de site de référence.`
- **Issue:** "Publié sous forme de site de référence" has a gender agreement error. "Publié" is masculine singular, but the implicit subject is "le projet" or the whole set of deliverables. However, the preceding two sentences use noun-only fragments. The inconsistency in sentence structure (noun phrases vs. a passive participle phrase) is jarring.
- **Proposed:** `Concepts et propriétés avec des URI stables. Définitions rédigées pour les professionnels du domaine. Publication sous forme de site de référence.`
- **Rationale:** Using "Publication" as a noun keeps all three items parallel as noun phrases, avoids the gender agreement ambiguity, and is more consistent in register.

---

## Overall impression

The translation is largely serviceable and correct at the sentence level; a policy reader would understand it without confusion. However, it shows a consistent pattern of sentence-by-sentence calquing from English: word order is often carried over unchanged, English compound nouns are unpacked mechanically ("blocs de construction", "couche de données de prestation"), and a handful of terms are either mistranslated ("identifiants vérifiables" for Verifiable Credentials) or unnatural ("implémenteurs", "multi-parties prenantes"). The most urgent fix before publishing is the "identifiants/titres vérifiables" error, which is a factual mistranslation that would confuse or mislead a French-speaking practitioner familiar with W3C or EU credential standards. With the fixes above applied, the text would reach a professional level; as it stands, it needs targeted revision rather than a full redo.
