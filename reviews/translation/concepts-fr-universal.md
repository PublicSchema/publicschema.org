# Review: FR universal concepts

## person.yaml
Overall: Solid and readable, but drops the "Registrant" role example from the English source and uses a semicolon in a context where French punctuation prefers a period.

### Issue 1
- **Current (fr):** `les statuts opérationnels tels que demandeur ou bénéficiaire sont des rôles transitoires définis par la relation de la personne à un programme spécifique.`
- **Source (en):** `operational statuses such as Registrant, Applicant, or Beneficiary are transient roles defined by the person's relationship to a specific Program`
- **Issue:** Three roles are listed in English (Registrant, Applicant, Beneficiary); the French drops "Registrant" entirely, losing a concept that appears in the convergence notes (OpenSPP) and is worth naming here.
- **Proposed:** `les statuts opérationnels tels que Registrant, demandeur ou bénéficiaire sont des rôles transitoires définis par la relation de la personne à un programme spécifique.`
- **Rationale:** "Registrant" is a proper concept label used elsewhere in the schema and should be preserved untranslated, as with Person, Group, etc. Dropping it creates an inconsistency with the English.

### Issue 2
- **Current (fr):** `La personne est l'unité indivisible et persistante d'identité dans les registres; les statuts opérationnels...`
- **Source (en):** `Person is the persistent, indivisible unit of identity in registries; operational statuses...`
- **Issue:** The semicolon joining these two clauses is grammatically acceptable but reads as a run-on in formal French. The second clause introduces a contrasting point and reads more naturally after a period.
- **Proposed:** `La personne est l'unité indivisible et persistante d'identité dans les registres. Les statuts opérationnels...`
- **Rationale:** French style guides generally favor a period over a semicolon when the second clause is a full, independent thought. The English also uses a semicolon, but that is a different convention.

---

## party.yaml
Overall: Clean and accurate, but "permettant des références acceptant l'un ou l'autre" is a calque that reads awkwardly.

### Issue 1
- **Current (fr):** `Party est le supertype partagé pour Person et Group, permettant des références acceptant l'un ou l'autre.`
- **Source (en):** `Party is the shared supertype for Person and Group, enabling references that accept either.`
- **Issue:** "permettant des références acceptant l'un ou l'autre" is an almost word-for-word calque. In technical administrative French, the concept is better expressed as a purpose clause explaining what this enables in practice.
- **Proposed:** `Party est le supertype commun de Person et Group, permettant de les désigner indifféremment dans une référence.`
- **Rationale:** "commun" is more natural than "partagé" in this context (as in "point commun", "supertype commun"). The rewritten clause avoids the clumsy stacking of two participial phrases.

---

## group.yaml
Overall: Good overall; "liens d'appartenance" is accurate and natural.

No issues worth flagging.

---

## group-membership.yaml
Overall: Accurate and fluent; minor word-choice point on "chef".

### Issue 1
- **Current (fr):** `le rôle que la personne joue au sein de ce groupe (tel que chef, conjoint ou dépendant)`
- **Source (en):** `the role the person plays within that group (such as head, spouse, or dependent)`
- **Issue:** "chef" for "head" (of household) is correct in informal usage but the standard term in French administrative and statistical contexts (INSEE, FAO, World Bank French documents) is "chef de ménage" or simply "chef de famille." Without that qualifier, "chef" alone is ambiguous ("boss", "chef de cuisine", etc.).
- **Proposed:** `(tel que chef de groupe, conjoint ou dépendant)`
- **Rationale:** "Chef de groupe" is neutral and internationally understandable, avoids the France-coded "chef de famille", and removes the ambiguity of bare "chef". An alternative would be "responsable du groupe" but that shifts the semantic slightly.

---

## household.yaml
Overall: Accurate and well-phrased; "cuisine commune" is a good choice over a calque of "shared cooking".

No issues worth flagging.

---

## family.yaml
Overall: Clean and faithful to the source.

No issues worth flagging.

---

## identifier.yaml
Overall: Well-translated; one terminology note.

### Issue 1
- **Current (fr):** `tel qu'un numéro d'identité nationale`
- **Source (en):** `such as a national ID number`
- **Issue:** "numéro d'identité nationale" is not standard. In French administrative usage the term is "numéro d'identité national" (masculine adjective agreeing with "numéro", not "identité") or more precisely "numéro d'identification national" or "numéro de carte d'identité nationale". "Identité nationale" in France carries a politically loaded connotation (the former Ministère de l'Immigration et de l'Identité nationale). A neutral Francophone formulation avoids this.
- **Proposed:** `tel qu'un numéro d'identification national`
- **Rationale:** "Numéro d'identification national" is used across Francophone Africa, Belgium, Switzerland, and international organizations (IOM, UNHCR). It is politically neutral and grammatically correct.

---

## relationship.yaml
Overall: Accurate and readable; one awkward construction worth addressing.

### Issue 1
- **Current (fr):** `Trois grands types existent : la parenté (liens biologiques ou juridiques), l'administratif (bénéficiaire, soignant, mandataire de paiement) et l'économique (dépendant, survivant).`
- **Source (en):** `Three broad types exist: kinship (biological or legal ties), administrative (grantee, caregiver, payment proxy), and economic (dependent, survivor).`
- **Issue:** "l'administratif" and "l'économique" are substantivized adjectives, which is acceptable in French but reads as a register mismatch alongside the noun "la parenté". The three items in the list should be parallel. Also, "bénéficiaire" here translates "grantee" but in this schema "bénéficiaire" normally means Beneficiary (a person receiving program benefits), not "grantee" in the relationship sense. This risks confusion.
- **Proposed:** `Trois grands types existent : la parenté (liens biologiques ou juridiques), les liens administratifs (ayant droit, soignant, mandataire de paiement) et les liens économiques (personne à charge, survivant).`
- **Rationale:** "les liens administratifs / économiques" is parallel with "la parenté", makes the list consistent, and removes the awkward nominalized adjectives. "Ayant droit" is the standard French legal term for "grantee" in social protection contexts and avoids collision with "bénéficiaire". "Personne à charge" is clearer than "dépendant" (which reads as an adjective).

---

## address.yaml
Overall: Critical issue -- all French accents are entirely missing. The text reads as plain ASCII and is unpublishable.

### Issue 1
- **Current (fr):** `Un emplacement physique ou postal structure utilise pour joindre une personne, un menage ou une organisation. Les adresses combinent des composantes spatiales et administratives telles que la rue, le quartier, le district et le code postal.`
- **Source (en):** `A structured physical or postal location used to reach a person, household, or organization. Addresses combine spatial and administrative components such as street, settlement, district, and postal code.`
- **Issue:** Every accented character is missing: "structuré", "utilisé", "ménage" all appear unaccented. This is a file encoding or authoring error. The text is garbled French.
- **Proposed:** `Un emplacement physique ou postal structuré, utilisé pour joindre une personne, un ménage ou une organisation. Les adresses combinent des composantes spatiales et administratives telles que la rue, le quartier, le district et le code postal.`
- **Rationale:** Restore missing accents. Also adds a comma after "structuré" for rhythm. Note: "quartier" for "settlement" is a slight shift -- "settlement" in this context typically means a populated place (village, locality), not a neighbourhood. "Localité" would be more accurate.

### Issue 2
- **Current (fr):** `le quartier` (for "settlement")
- **Source (en):** `settlement`
- **Issue:** "Quartier" means neighbourhood or quarter within a city. "Settlement" in address contexts means a populated locality (village, hamlet, bourg). This is a semantic drift.
- **Proposed:** `la localité`
- **Rationale:** "Localité" is the standard French administrative term for a named inhabited place, used by INSEE, UNHCR, and Francophone government systems.

---

## location.yaml
Overall: Critical issue -- all accents are missing, same encoding problem as address.yaml. Also a grammatical agreement error.

### Issue 1
- **Current (fr):** `Une zone geographique ou administrative nommee, telle qu'une region, un district, une commune ou un village. La localisation indique ou se situe un menage ou un evenement dans une hierarchie administrative, distinct d'une adresse postale.`
- **Source (en):** `A named geographic or administrative area, such as a region, district, commune, or village. Location captures where a household or event is situated within an administrative hierarchy, distinct from a street address.`
- **Issue:** All accents are missing ("géographique", "nommée", "région", "ménage", "événement"). File encoding error, same as address.yaml.
- **Proposed:** `Une zone géographique ou administrative nommée, telle qu'une région, un district, une commune ou un village. La localisation indique où se situe un ménage ou un événement dans une hiérarchie administrative, distincte d'une adresse postale.`
- **Rationale:** Restore accents throughout. Also fixes the agreement error: "distincte" (feminine, agreeing with "localisation") rather than "distinct" (masculine).

### Issue 2
- **Current (fr):** `La localisation indique ou se situe...`
- **Source (en):** `Location captures where a household or event is situated...`
- **Issue:** Beyond the missing accent on "où", the phrase "indique où se situe" is a slight calque. In French administrative writing, the more natural construction uses "précise" or "renseigne sur".
- **Proposed:** `La localisation précise où se situe un ménage ou un événement dans une hiérarchie administrative, distincte d'une adresse postale.`
- **Rationale:** "Précise où" is a common French construction for "specifies/captures where". "Indique où" is not wrong, but "précise" better conveys the intentional, structured nature of the data.

---

## geographic-area.yaml
Overall: Critical issue -- all accents are missing, same encoding problem as address.yaml and location.yaml.

### Issue 1
- **Current (fr):** `Une region geographique definie par une geometrie de limites, des codes administratifs ou des lieux nommes. Utilisee pour specifier l'etendue spatiale des alertes, de la couverture des programmes et d'autres concepts lies a un lieu.`
- **Source (en):** `A defined geographic region described by boundary geometry, administrative codes, or named locations. Used to specify the spatial extent of alerts, program coverage, and other location-bounded concepts.`
- **Issue:** All accents stripped: "région", "géographique", "définie", "géométrie", "nommés", "Utilisée", "spécifier", "étendue", "liés". File encoding error, same root cause as address.yaml and location.yaml.
- **Proposed:** `Une région géographique définie par une géométrie de limites, des codes administratifs ou des lieux nommés. Utilisée pour spécifier l'étendue spatiale des alertes, de la couverture des programmes et d'autres concepts liés à un lieu.`
- **Rationale:** Restore all accents. No other changes needed; the translation is otherwise accurate and fluent.

---

## event.yaml
Overall: Well-written and fluent; one word-choice note on "livraisons".

### Issue 1
- **Current (fr):** `(évaluations, décisions, paiements, livraisons, orientations, etc.)`
- **Source (en):** `(assessments, decisions, payments, deliveries, referrals, etc.)`
- **Issue:** "livraisons" typically means physical deliveries of goods (e.g., a delivery truck). In social protection, "deliveries" in this list refers to service or in-kind benefit delivery events. "Livraisons" is not wrong but could be misread. "Prestations" or "remises" are more common in this domain.
- **Proposed:** `(évaluations, décisions, paiements, remises de prestations, orientations, etc.)`
- **Rationale:** "Remises de prestations" makes the social protection context explicit. If brevity is preferred, "prestations" alone is acceptable since the context (delivery system) is established.

---

## Cross-cutting issues

### Encoding error affecting three files
address.yaml, location.yaml, and geographic-area.yaml all have French definitions where every accented character is absent. This is not a translation error in the text itself but a systematic encoding failure at the time of authoring (likely saved as ASCII or Latin-1 rather than UTF-8, or pasted from a tool that stripped diacritics). All three files need their `definition.fr` values re-encoded with proper UTF-8 accents before publication.

### Terminology consistency
The following term pairs are used consistently and correctly across all 12 files -- no drift detected:
- "ménage" for Household
- "groupe" for Group (lowercase when used generically)
- "appartenance" / "lien d'appartenance" for membership
- "prestation" / "prestations" for benefits/services
- "programme" for Program
