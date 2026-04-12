# French translation review -- UI dictionary (ui.ts)

Scope: full review of the `fr` object in `site/src/i18n/ui.ts` (~85 translated keys), covering terminology consistency, phrasing quality, and register appropriateness for an internationally neutral francophone audience (EU, West/Central Africa, Canada, Haiti).

---

## Part 1: Terminology glossary and consistency check

### Term inventory

**Concept / Concepts**
- Renderings: `Concepts` (nav.concepts, common.concepts, concepts.page_title, concepts.table.concept, concept_detail.*, home.core_concepts, search.browse_hint, search.placeholder)
- Consistency: uniform throughout.
- Canonical: `Concept / Concepts`. Correct: the English term is used as a proper noun for this schema artefact; keeping it unchanged is standard practice in multilingual technical documentation.

**Property / Properties**
- Renderings: `Propriété / Propriétés` (nav.properties, common.properties, properties.*, property_detail.*, concept_detail.table.property, system_detail.properties)
- Also: `Attributs` appears once in `properties.page_subtitle` ("Attributs réutilisables partagés entre les concepts").
- Inconsistency: the table header says `Propriété`, the subtitle says `Attributs`. These are not synonyms in this domain context.
- Canonical: `Propriété / Propriétés`. Rationale: "propriété" is the correct data-modelling term in French (used in OWL, RDF, JSON Schema documentation in French); "attribut" is more natural in database/UML contexts and is used inconsistently here.

**Vocabulary / Vocabularies**
- Renderings: `Vocabulaire / Vocabulaires` (nav.vocabularies, common.vocabularies, vocab.*, vocab_detail.*, home.vocabularies, search.browse_hint)
- Consistency: uniform throughout.
- Canonical: `Vocabulaire / Vocabulaires`. Correct.

**Standard / Standards**
- Renderings: `Norme / Normes` (vocab.table.standard, vocab_detail.standard_reference, vocab_detail.aligned_standards, vocab_detail.same_standard, systems.table.same_standard, system_detail.relationship_same_standard, concept_detail.table.standard, concept_detail.aligned_standards)
- Consistency: uniform throughout.
- Canonical: `Norme / Normes`. Correct: "norme" is the established French term for a technical standard (ISO, AFNOR usage).

**Mapping / Mappings**
- Renderings: `Correspondance / Correspondances` (vocab_detail.system_mappings, systems.table.value_mappings, system_detail.relationship_value_mapping, system_detail.coverage_mapped, system_detail.report_button, property_detail.system_mappings)
- Consistency: uniform throughout.
- Canonical: `Correspondance / Correspondances`. Correct: avoids the anglicism "mapping" while remaining clear.

**System / Systems**
- Renderings: `Système / Systèmes` (common.systems, footer.systems, systems.*, system_detail.*, vocab_detail.system_mappings, vocab_detail.system_vocabulary)
- Consistency: uniform throughout.
- Canonical: `Système / Systèmes`. Correct.

**Definition**
- Renderings: `Définition` (concepts.table.definition, properties.table.definition, vocab.table.definition, vocab_detail.table.definition, concept_detail.table.definition)
- Consistency: uniform throughout.
- Canonical: `Définition`. Correct.

**Type / Data Types**
- Renderings: `Type` (properties.table.type, concept_detail.table.type, property_detail.type); `Types de données` (common.data_types)
- Consistency: uniform within each use.
- Canonical: `Type` for column headers; `Types de données` for the section label. Correct.

**Evidence**
- Renderings: `Données probantes` (concept_detail.evidence, concept_detail.evidence.* strings)
- Canonical: `Données probantes` is formally correct and widely used in Francophone policy contexts (particularly health/social policy). Appropriate here.

**Coverage**
- Renderings: `Couverture` (system_detail.table.coverage)
- Canonical: `Couverture`. Correct.

**Gaps**
- Renderings: `Lacunes` (system_detail.table.gaps)
- Canonical: `Lacunes`. Correct and plain enough for a policy audience.

**Used by**
- Renderings: `Utilisé par` (properties.table.used_by, property_detail.used_by)
- Issue: "Propriété" is feminine; "Utilisé par" should agree. However, because this is a table column header referring to the concept ("utilisé par [tels concepts]"), the phrase is idiomatic as-is if read as "[ce vocabulaire/cette propriété est] utilisé[e] par". The lack of agreement is actually a potential issue (see Part 2).
- Canonical: `Utilisé par` is acceptable for a table header. Flag agreement issue in Part 2.

**Search / Browse**
- Renderings: `Rechercher` (nav.search, search.close label uses "Fermer la recherche"); `Parcourir` (search.browse_hint); `Explorer` (footer.explore, home.browse_schema uses "Explorer le schéma")
- Inconsistency: "Browse" is rendered as both `Parcourir` (search.browse_hint) and `Explorer` (footer.explore, home.browse_schema). These are close enough in meaning that inconsistency is a minor issue, but `Parcourir` is more neutral/accurate for "browse" while `Explorer` implies a more active discovery action.
- Canonical: `Parcourir` for "Browse" (navigation/listing contexts); `Explorer` is acceptable for the homepage call-to-action where it conveys invitation. Document the distinction and apply consistently.

**About**
- Renderings: `À propos` (nav.about, footer.about, home.about_project uses "À propos du projet")
- Consistency: uniform. Correct.

**Documentation / Docs**
- Renderings: `Documentation` (nav.docs, footer.docs, docs.page_title, docs.category.technical)
- Consistency: uniform. Correct.

**Supertype / Subtype**
- Renderings: `Supertypes` (concept_detail.supertypes); `Sous-types` (concept_detail.subtypes)
- Inconsistency: "Supertypes" is a raw anglicism (not hyphenated, not adapted); "Sous-types" is correctly calqued. Either both should be kept as anglicisms or both should be calqued. The asymmetry is jarring.
- Canonical: use `Supertypes` and `Sous-types` or adapt both; see Part 2.

**Cardinality**
- Renderings: `Cardinalité` (property_detail.cardinality)
- Canonical: `Cardinalité`. Correct technical term.

**Label (table column)**
- Renderings: `Libellé` (vocab_detail.table.label, property_detail.table.system_label)
- Canonical: `Libellé`. Correct; standard French UI term for "label" in data contexts.

**Code**
- Renderings: `Code` (vocab_detail.table.code, vocab_detail.table.standard_code uses "Code normalisé", property_detail.table.system_code uses "Code système")
- Consistency: uniform within compound forms. Correct.

**Relationship**
- Renderings: `Relation` (system_detail.table.relationship)
- Canonical: `Relation`. Correct; "Relationship" as "Relation" is standard in data modelling French.

---

## Part 2: Line-by-line issues

---

**Key:** `properties.page_subtitle`
**Current:** `Attributs réutilisables partagés entre les concepts.`
**Issue:** "Attributs" contradicts the established term "Propriétés" used everywhere else in the UI, including the page title directly above this subtitle.
**Proposed:** `Propriétés réutilisables partagées entre les concepts.`
**Rationale:** Terminological consistency; "propriété" is also the correct RDF/OWL-adjacent term for this artefact type.

---

**Key:** `properties.table.used_by`
**Current:** `Utilisé par`
**Issue:** "Propriété" is feminine, so a column header meaning "this property is used by..." should read "Utilisée par"; as a standalone header the form is ambiguous but could create agreement confusion.
**Proposed:** `Utilisée par`
**Rationale:** Gender agreement with "Propriété"; matches `property_detail.used_by` which has the same issue.

---

**Key:** `property_detail.used_by`
**Current:** `Utilisé par`
**Issue:** Same gender agreement issue as `properties.table.used_by`; the subject referent is "Propriété" (feminine).
**Proposed:** `Utilisée par`
**Rationale:** Consistent agreement across both occurrences.

---

**Key:** `property_detail.no_uses`
**Current:** `Non utilisé par aucun concept pour l'instant.`
**Issue:** "Non utilisé par aucun concept" is a double negation (both "non" and "aucun" negate). The correct form is either "Pas encore utilisée par un concept" or "N'est utilisée par aucun concept pour l'instant." Also, gender agreement: "propriété" is feminine.
**Proposed:** `Pas encore utilisée par aucun concept.`
**Rationale:** Removes the ungrammatical double negation and fixes gender agreement; "pour l'instant" is implied and its removal matches the more concise parallel strings in the dictionary.

---

**Key:** `concept_detail.supertypes`
**Current:** `Supertypes`
**Issue:** Raw anglicism; the paired term "Sous-types" (`concept_detail.subtypes`) is a proper French calque, creating an asymmetric pair.
**Proposed:** `Supertypes` (keep) OR rename subtypes to `Sous-types` and change this to `Super-types` for visual consistency.
**Rationale:** If keeping anglicisms, use the same strategy for both. If adapting, hyphenate both: `Super-types` / `Sous-types`. The current asymmetry (one adapted, one not) is inconsistent. Recommendation: `Super-types` / `Sous-types`.

---

**Key:** `concept_detail.abstract_title`
**Current:** `Supertype abstrait : existe pour regrouper des propriétés partagées ; les instances sont enregistrées comme l'un de ses sous-types`
**Issue:** "l'un de ses sous-types" is grammatically correct but slightly awkward in a tooltip context; more importantly, "enregistrées" requires agreement with "instances" (feminine plural) -- this is actually correct as-is, so the agreement is fine. The real issue is the use of a semicolon (";") as a structural separator inside a tooltip, which reads clunky in French. A colon-introduced clause is smoother.
**Proposed:** `Supertype abstrait : regroupe des propriétés partagées ; les instances sont enregistrées sous l'un de ses sous-types.`
**Rationale:** "existe pour regrouper" is verbose; "regroupe" is tighter. "enregistrées comme" is a calque of "recorded as one of"; "enregistrées sous" is more idiomatic in French administrative/data contexts.

---

**Key:** `vocab_detail.same_standard_desc_suffix`
**Current:** `pour ce vocabulaire, les valeurs sont donc directement compatibles sans correspondance :`
**Issue:** The colon at the end is correct (it introduces the list), but "sans correspondance" is ambiguous: it could mean "without any relationship" rather than "without requiring mapping". The English says "without mapping" meaning no translation is needed, which is the positive case.
**Proposed:** `pour ce vocabulaire ; les valeurs sont donc directement compatibles sans conversion :`
**Rationale:** "sans conversion" is clearer than "sans correspondance" for a francophone policy reader who might not know what "correspondance" means in a technical mapping sense; separating the two clauses with a semicolon rather than a comma avoids a run-on.

---

**Key:** `systems.page_subtitle`
**Current:** `Systèmes externes et normes avec des correspondances de vocabulaire vers les valeurs canoniques de PublicSchema.`
**Issue:** "avec des correspondances de vocabulaire vers les valeurs canoniques" is a heavy, French-looking calque of the English structure. "vers les valeurs canoniques" is technically understandable but sounds like translated-English word order.
**Proposed:** `Systèmes externes et normes dont les vocabulaires sont mis en correspondance avec les valeurs canoniques de PublicSchema.`
**Rationale:** Restructures the sentence into natural French subject-verb-complement order; "mis en correspondance avec" is the standard French phrase for "mapped to".

---

**Key:** `system_detail.table.system_name`
**Current:** `Nom dans le système`
**Issue:** This is a reasonable translation but "Nom dans le système" could be read as "the name [of something] inside the system" rather than "the name used by that system". The English "System name" means the name that the external system gives to this concept.
**Proposed:** `Nom dans le système`
**Rationale:** Actually acceptable on reflection; no change needed. Flag retracted.

---

**Key:** `concept_detail.evidence.all_systems`
**Current:** `Présent dans l'ensemble des {total} systèmes de prestation cartographiés.`
**Issue:** "cartographiés" is a calque of "mapped" in the software sense (data mapping), but in French "cartographié" primarily means "mapped" in the geographic/survey sense. A French policy reader may find this confusing.
**Proposed:** `Présent dans les {total} systèmes de prestation analysés.`
**Rationale:** "analysés" (analysed) or "recensés" (inventoried) is more natural for a francophone policy audience than "cartographiés"; "analysés" keeps a positive, active connotation. Same fix applies to the related strings below.

---

**Key:** `concept_detail.evidence.none`
**Current:** `Pas encore trouvé dans les systèmes de prestation cartographiés.`
**Issue:** Same "cartographiés" calque issue as above.
**Proposed:** `Pas encore trouvé dans les systèmes de prestation analysés.`
**Rationale:** Consistent fix across all three evidence strings.

---

**Key:** `concept_detail.evidence.partial`
**Current:** `Présent dans {count} des {total} systèmes de prestation cartographiés.`
**Issue:** Same "cartographiés" calque issue.
**Proposed:** `Présent dans {count} des {total} systèmes de prestation analysés.`
**Rationale:** Consistent fix across all three evidence strings.

---

**Key:** `search.browse_hint`
**Current:** `Parcourir : Concepts, Propriétés, Vocabulaires`
**Issue:** The colon after "Parcourir" is correct typographically (French requires a space before a colon), and this string does include it. No issue.
**Proposed:** No change needed.
**Rationale:** Correct as-is.

---

**Key:** `footer.tagline`
**Current:** `Définitions communes pour la prestation de services publics. Conçu pour permettre aux programmes de coordonner, partager des données et atteindre les personnes qu'ils servent.`
**Issue:** "Conçu" is masculine singular, agreeing with an implied "ce site/cet outil", which is acceptable but slightly hanging. More critically, "les personnes qu'ils servent" has an ambiguous pronoun reference: "ils" could refer to "programmes" or to "personnes". In the English "reach the people they serve", "they" unambiguously refers to "programs". The French is similarly unambiguous in context but reads slightly more awkwardly.
**Proposed:** `Définitions communes pour la prestation de services publics. Conçu pour permettre aux programmes de se coordonner, de partager des données et d'atteindre les personnes auxquelles ils s'adressent.`
**Rationale:** Adding "de" before each infinitive in the series ("se coordonner, de partager, d'atteindre") is required by French grammar after "permettre à [qqn] de faire qqch"; the current version drops the "de" for the second and third verbs. "les personnes auxquelles ils s'adressent" is clearer and more formal than "les personnes qu'ils servent" (which, while understandable, is a direct calque of "the people they serve").

---

**Key:** `lang.switch_to`
**Current:** `Changer la langue en {language}`
**Issue:** "Changer la langue en {language}" is a calque of "Switch language to {language}". In French, one switches "la langue" not "en" but "vers" or uses a different construction. The natural French is "Passer en {language}" or "Changer de langue : {language}".
**Proposed:** `Passer en {language}`
**Rationale:** "Passer en [langue]" is the standard French UI pattern for language switching (used in major French-language software products); "changer la langue en" reads as translated English.

---

**Key:** `search.min_chars`
**Current:** `Saisissez au moins 2 caractères pour rechercher`
**Issue:** Correct and natural. The imperative "Saisissez" is slightly formal for a search hint but appropriate for the formal-ish register of this product. No issue.
**Proposed:** No change needed.
**Rationale:** Acceptable.

---

**Key:** `home.plus_more`
**Current:** `+{count} de plus`
**Issue:** Correct and idiomatic. No issue.
**Proposed:** No change needed.
**Rationale:** Acceptable.

---

**Key:** `banner.dismiss`
**Current:** `Fermer`
**Issue:** The English is "Dismiss" (dismiss a banner/notification). "Fermer" means "Close" and is the standard French UI term for closing a dialog or panel. "Ignorer" or "Masquer" would be more precise for dismissing an informational banner, but "Fermer" is universally understood.
**Proposed:** `Masquer`
**Rationale:** "Masquer" (hide/dismiss) is more semantically accurate for a dismissible banner than "Fermer" (close), and avoids confusion with closing a window or dialog. "Ignorer" is also acceptable but more informal.

---

**Key:** `404.go_home`
**Current:** `retourner à la page d'accueil`
**Issue:** "Retourner à la page d'accueil" is correct. Minor register note: in a UI link context, "revenir à la page d'accueil" is more commonly used in Francophone digital products.
**Proposed:** `revenir à la page d'accueil`
**Rationale:** "Revenir" (come back) is more natural than "retourner" (go back/return) for navigating home from a 404; "retourner" can imply physically returning to a place, while "revenir" is the standard web navigation phrasing.

---

**Key:** `vocab_detail.external_values_note_suffix`
**Current:** `La liste complète des valeurs est disponible dans les téléchargements ci-dessus`
**Issue:** "dans les téléchargements ci-dessus" is a calque of "in the downloads above". The French idiom for "available for download" is "disponible en téléchargement" or "accessible via les liens de téléchargement ci-dessus".
**Proposed:** `La liste complète des valeurs est accessible via les liens de téléchargement ci-dessus`
**Rationale:** "disponible dans les téléchargements" sounds like the values list is somehow inside a folder called "downloads"; "accessible via les liens de téléchargement" makes clear it refers to download links on the page.

---

**Key:** `concept_detail.abstract_badge`
**Current:** `abstrait`
**Issue:** Grammatically correct. The badge label "abstract" maps to "abstrait". However, "abstrait" in isolation on a badge without further context can look like an artistic/philosophical descriptor rather than a technical data modelling term. "Abstract" in English UI is widely understood in technical contexts; in French, "abstrait" carries more ambiguity.
**Proposed:** `abstrait`
**Rationale:** No change recommended; this is a technical badge and the tooltip (`concept_detail.abstract_title`) provides the necessary clarification. Changing to a longer phrase would break the badge format.

---

**Key:** `docs.category.landscape`
**Current:** `Panorama`
**Issue:** "Panorama" is a reasonable translation of "Landscape" in the sense of "landscape of systems/tools". It is used in this sense in Francophone policy and institutional reports ("panorama des systèmes", "panorama des acteurs"). No issue.
**Proposed:** No change needed.
**Rationale:** Correct and appropriate.

---

**Key:** `system_detail.report_button`
**Current:** `Signaler un problème avec ces correspondances`
**Issue:** Correct and natural. "Signaler un problème" is the standard French UI pattern for "Report an issue". No issue.
**Proposed:** No change needed.
**Rationale:** Acceptable.

---

**Key:** `vocab_detail.no_mapping`
**Current:** `aucun équivalent`
**Issue:** Correct. Natural and concise.
**Proposed:** No change needed.
**Rationale:** Acceptable.

---

**Key:** `footer.built_with`
**Current:** `Réalisé avec`
**Issue:** "Réalisé avec" is a reasonable rendering of "Built with". However, in French digital product footers, "Construit avec" is more literal and commonly used; "Réalisé avec" is more common in film credits. This is a minor style preference, not a clear error.
**Proposed:** `Construit avec`
**Rationale:** "Construit avec" better matches the technical register of a developer-facing footer; "Réalisé avec" skews toward creative/artistic production contexts.

---

## Part 3: Overall impression

The French translation is functional and clearly written by someone with genuine French fluency; it avoids the worst anglicisms and uses correct register for the most part. The two most significant systemic problems are: (1) the "cartographiés" calque for "mapped" appearing three times in the evidence strings, which will confuse a francophone policy reader; and (2) the grammatical error in `footer.tagline` where "permettre" requires "de" before each infinitive in the series. Beyond those, the translation needs light polish (the `Attributs`/`Propriétés` inconsistency, the `lang.switch_to` calque, the `property_detail.no_uses` double negation) but is not a full redo. It is shippable after addressing the ~10 flagged items.
