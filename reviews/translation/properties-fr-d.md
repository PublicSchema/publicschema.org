# Review: FR properties (batch d)

Files reviewed: level_name, literacy, location, location_name, locations, longitude, manner_of_death, marital_status, marriage_ref, matronymic_name, medical_certifier, member_count, memberships, mother, name, nationality, nationality_at_birth, number_of_spouses, object_person, occupation, originating_event, parent_location, parental_role, parents, party_1, party_2, patronymic_name, payment_amount, payment_currency, payment_date, payment_status, person, phone_number, place_of_usual_residence, place_type, postal_code, preferred_language, preferred_name, previous_parents, primary_crop, program_ref, quantity, quantity_redeemed, raw_score, receiving_program, recipient

---

## level_name.yaml

### Issue 1

- **Current (fr):** `Le nom specifique au pays pour ce niveau administratif (p. ex., etat, departement, commune, quartier).`
- **Source (en):** `The country-specific name for this administrative tier (e.g., state, department, commune, ward).`
- **Issue:** Missing accents throughout: "specifique" should be "spécifique", "etat" should be "état", "departement" should be "département". "Quartier" is a reasonable rendering of "ward" in a French-speaking administrative context, but "ward" in English also covers electoral sub-divisions in Anglophone Africa; "arrondissement" or "secteur" might be more neutral. The larger problem is the stripped accents, which suggests the string was not encoded in UTF-8 or was produced without diacritics.
- **Proposed:** `Le nom spécifique au pays pour ce niveau administratif (p. ex., état, département, commune, quartier).`
- **Rationale:** Accents are mandatory in standard French. The rest of the phrasing is natural and correct for a policy audience.

---

## literacy.yaml

Overall: Clean. "Court énoncé simple sur la vie quotidienne" is a faithful and natural rendering of the UNESCO/UN definition. No issues.

---

## location.yaml

Overall: Accurate and natural. "Capturant les coordonnées ou la zone administrative" mirrors the English structure well. No issues.

---

## location_name.yaml

### Issue 1

- **Current (fr):** `Un nom de lieu lisible par un humain pour la localisation.`
- **Source (en):** `A human-readable place name for the location.`
- **Issue:** "Lisible par un humain" is a direct calque of "human-readable" that reads awkwardly in French. The standard phrasing for a label intended for human consumption is "intelligible" or "en langage naturel". "Pour la localisation" also uses the same word twice (the concept is already about Location). A tighter construction replaces both.
- **Proposed:** `Un nom de lieu en langage naturel pour cette localisation.`
- **Rationale:** "En langage naturel" is the conventional French equivalent of "human-readable" in data and metadata standards (ISO 11179, Dublin Core FR). It avoids the anthropomorphic calque.

---

## locations.yaml

### Issue 1

- **Current (fr):** `Lieux nommes au sein de ou representant cette zone geographique.`
- **Source (en):** `Named locations within or representing this geographic area.`
- **Issue:** Missing accents: "nommes" should be "nommés", "geographique" should be "géographique". The phrase "au sein de ou representant" is also awkward; French would normally use "ou" after the verb, not mid-prepositional phrase. A recast reads more naturally.
- **Proposed:** `Lieux nommés qui appartiennent à cette zone géographique ou la représentent.`
- **Rationale:** Restores required accents and replaces the stranded preposition construction with a relative clause, which is idiomatic French.

---

## longitude.yaml

### Issue 1

- **Current (fr):** `La longitude geographique en degres decimaux (WGS84).`
- **Source (en):** `The geographic longitude in decimal degrees (WGS84).`
- **Issue:** Missing accents: "geographique" should be "géographique", "degres" should be "degrés".
- **Proposed:** `La longitude géographique en degrés décimaux (WGS84).`
- **Rationale:** "Degrés décimaux" is the standard French term used in cartography and GIS (IGN, INSPIRE directive). Accents are mandatory.

---

## manner_of_death.yaml

### Issue 1

- **Current (fr):** `Les circonstances dans lesquelles le décès s'est produit: naturel, accident, blessure auto-infligée intentionnelle, agression, intervention légale, guerre, enquête en cours, ou indéterminé. Suit la structure de l'acte de décès de l'OMS.`
- **Source (en):** `The circumstances under which the death occurred: natural, accident, intentional self-harm, assault, legal intervention, war, pending investigation, or could not be determined. Follows the WHO death certificate structure.`
- **Issue:** The enumerated values in the list are adjectives or noun phrases that disagree in gender/number with their implicit head noun. "Les circonstances" is plural feminine, but the list items appear to modify an unstated noun. More importantly, "intentional self-harm" in the WHO ICD-10/WHO death certificate is rendered in French as "blessures auto-infligées intentionnelles" (plural) or more precisely as the category "Lésions auto-infligées intentionnellement". "Blessure auto-infligée intentionnelle" is a partial calque. The WHO French uses "violence auto-infligée intentionnelle" or "lésions auto-infligées". Also, "acte de décès de l'OMS" should be "certificat médical de cause de décès de l'OMS" to match the actual WHO instrument name.
- **Proposed:** `Les circonstances dans lesquelles le décès s'est produit : naturel, accident, violence auto-infligée intentionnelle, agression, intervention légale, guerre, enquête en cours ou indéterminé. Suit la structure du certificat médical de cause de décès de l'OMS.`
- **Rationale:** "Violence auto-infligée intentionnelle" matches the WHO French terminology for this ICD category. "Certificat médical de cause de décès" is the correct French name for the WHO instrument referenced in the English.

---

## marital_status.yaml

Overall: Accurate. "Tel qu'enregistré dans un système administratif" preserves the administrative register nuance. No issues.

---

## marriage_ref.yaml

### Issue 1

- **Current (fr):** `Une référence à l'acte de Mariage que cette rupture (divorce ou annulation) dissout. Relie la fin de l'union à sa formation.`
- **Source (en):** `A reference to the Marriage record that this termination (divorce or annulment) dissolves. Links the end of the union back to its formation.`
- **Issue:** "Rupture" is not the standard civil registration term for the termination of a marriage. In French civil law, the dissolution of a marriage is called "dissolution du mariage" or "dissolution de l'union". "Rupture" is informal and typically used for relationships rather than legal unions. "Dissout" is correct in form (third person singular of "dissoudre") but stylistically the passive "est dissous par" would be more natural here. Minor: "Mariage" (capitalized) is appropriate since it refers to the Marriage concept.
- **Proposed:** `Une référence à l'acte de Mariage que cette dissolution (divorce ou annulation) met fin. Relie la fin de l'union à sa formation.`
- **Rationale:** "Dissolution" is the correct legal term in French civil law for the ending of a marriage. Alternatively: "Une référence à l'acte de Mariage dissous par cette procédure (divorce ou annulation)."

---

## matronymic_name.yaml

### Issue 1

- **Current (fr):** `Un nom derive du prenom de la mere de la personne.`
- **Source (en):** `A name derived from the given name of the person's mother.`
- **Issue:** Missing accents: "derive" should be "dérivé", "prenom" should be "prénom", "mere" should be "mère".
- **Proposed:** `Un nom dérivé du prénom de la mère de la personne.`
- **Rationale:** Accents are mandatory.

---

## medical_certifier.yaml

Overall: Well rendered. "Officier d'état civil" for "registrar" and "certifié la cause du décès" are both correct civil registration terms. No issues.

---

## member_count.yaml

Overall: Clean and accurate. No issues.

---

## memberships.yaml

### Issue 1

- **Current (fr):** `Les liens d'appartenance reliant des personnes à ce groupe, chacun portant le rôle et les dates de cycle de vie.`
- **Source (en):** `The membership links connecting persons to this group, each carrying role and lifecycle dates.`
- **Issue:** "Les dates de cycle de vie" is a calque of "lifecycle dates". In French administrative and social protection writing, the conventional phrase for the dates that bound a membership record (start date, end date) is "les dates de début et de fin" or "les dates d'entrée et de sortie". "Cycle de vie" is an IT/software term (object lifecycle, système de gestion); it will be opaque to a policy officer audience. "Portant" (carrying) is also a calque; "indiquant" or "incluant" is more natural.
- **Proposed:** `Les liens d'appartenance reliant des personnes à ce groupe, chacun indiquant le rôle et les dates d'entrée et de sortie.`
- **Rationale:** "Dates d'entrée et de sortie" is clear to a policy audience and accurately describes what lifecycle dates mean in a membership context.

---

## mother.yaml

Overall: Accurate and precise. "Rattacher la reconnaissance à un acte maternel précis" is well chosen. No issues.

---

## name.yaml

Overall: Clean. "Nom complet d'affichage" is an acceptable rendering. No issues.

---

## nationality.yaml

### Issue 1

- **Current (fr):** `Le pays de citoyennete ou de nationalite, exprime de preference sous forme de code ISO 3166-1 alpha-2.`
- **Source (en):** `The country of citizenship or nationality, expressed as an ISO 3166-1 alpha-2 code where possible.`
- **Issue:** Missing accents: "citoyennete" should be "citoyenneté", "nationalite" should be "nationalité", "exprime" should be "exprimé". The English "where possible" is translated as "de préférence" (preferably), which shifts the sense: "where possible" means "when the data allows", while "de préférence" means "we prefer this form". The distinction matters for data quality expectations.
- **Proposed:** `Le pays de citoyenneté ou de nationalité, exprimé sous forme de code ISO 3166-1 alpha-2 lorsque possible.`
- **Rationale:** Restores accents. "Lorsque possible" matches the conditional sense of "where possible" more faithfully than "de préférence".

---

## nationality_at_birth.yaml

Overall: Accurate. "Jus sanguinis" and "jus soli" are retained correctly (no translation needed for legal Latin). "Selon la loi nationale applicable" is precise and internationally neutral. No issues.

---

## number_of_spouses.yaml

### Issue 1

- **Current (fr):** `Le nombre de conjoints actuels de la personne. Capture le type d'union polygame ou polyandrique séparément du statut matrimonial, suivant le cadre du recensement des Nations Unies et l'approche EDS.`
- **Source (en):** `The number of current spouses the person has. Captures polygamous or polyandrous union type separately from marital status, following the UN census framework and DHS approach.`
- **Issue:** "Capture" as a standalone verb opening a sentence is a calque of the English verb "Captures". The convention flagged in this project is to prefer "Recueille" or a more natural French verb. More importantly, "l'approche EDS" may not be understood without expansion by a French-speaking policy officer outside Francophone Africa, where EDS (Enquête Démographique et de Santé) is well known. A brief gloss or the spelled-out form would make this internationally neutral.
- **Proposed:** `Le nombre de conjoints actuels de la personne. Recueille le type d'union polygame ou polyandrique séparément du statut matrimonial, conformément au cadre du recensement des Nations Unies et à l'approche des Enquêtes Démographiques et de Santé (EDS).`
- **Rationale:** "Recueille" replaces the calque. Spelling out "Enquêtes Démographiques et de Santé" with the acronym in parentheses makes the reference accessible to the full target audience.

---

## object_person.yaml

### Issue 1

- **Current (fr):** `La personne à laquelle la personne sujet est liée (l'objet de l'énoncé de relation).`
- **Source (en):** `The person to whom the subject person is related (the object of the relationship statement).`
- **Issue:** "La personne sujet" is a calque of "the subject person". In French, "sujet" used as a noun modifier is not idiomatic; the natural form would be "la personne dont il est question" or, to match the technical framing, "la personne sujet" should at minimum carry a definite article structure: "la personne qui est le sujet". The parenthetical "(l'objet de l'énoncé de relation)" is technically accurate but uses abstract logical vocabulary; a policy reader would understand "la partie en relation" or simply "(le pôle objet de la relation)" better.
- **Proposed:** `La personne à laquelle se rapporte la relation (le pôle objet de l'énoncé de relation).`
- **Rationale:** Removes the repeated "personne … personne sujet" and simplifies the phrasing while preserving the technical meaning for a policy officer.

---

## occupation.yaml

### Issue 1

- **Current (fr):** `La profession principale de la personne, classée selon les sous-grands groupes ISCO-08.`
- **Source (en):** `The person's primary occupation, classified according to the ISCO-08 sub-major groups.`
- **Issue:** "Sous-grands groupes" is a literal calque of "sub-major groups". The official French name of this classification is CITP-08 (Classification Internationale Type des Professions), and the official French term for "sub-major groups" in CITP is "sous-grands groupes" — which is actually correct per the ILO French edition. However, the English uses the English acronym "ISCO-08" while the French should use "CITP-08" (or at minimum acknowledge both). Using only the English acronym in the French definition is inconsistent for a French-language audience.
- **Proposed:** `La profession principale de la personne, classée selon les sous-grands groupes de la CITP-08 (ISCO-08).`
- **Rationale:** "CITP-08" is the official ILO French acronym. Keeping the English acronym in parentheses supports cross-referencing.

---

## originating_event.yaml

Overall: Accurate and natural. "Rattache l'acte à l'événement sous-jacent" is well chosen. No issues.

---

## parent_location.yaml

### Issue 1

- **Current (fr):** `La localisation parente dans la hierarchie administrative.`
- **Source (en):** `The parent location in the administrative hierarchy.`
- **Issue:** Missing accent: "hierarchie" should be "hiérarchie". Also "localisation parente" is a calque of "parent location". In French GIS and administrative geography, the standard term for this concept is "unité administrative supérieure" or simply "zone parente". "Parente" as an adjective modifying a feminine noun (localisation) is grammatically unusual; "mère" or "supérieure" would be more natural.
- **Proposed:** `La zone administrative parente dans la hiérarchie administrative.`
- **Rationale:** Restores the accent. "Zone administrative parente" is used in French INSPIRE directive documentation and is clearer than "localisation parente". Alternatively "localisation de niveau supérieur" would also work.

---

## parental_role.yaml

Overall: Accurate and precise. "Filiation biologique et la filiation juridique" is the correct French civil law pairing. "Mère porteuse" for "surrogate mother" is natural. No issues.

---

## parents.yaml

Overall: Accurate. "Entité de lien Parent" preserves the concept label. "Mère biologique, père adoptif" are correct. No issues.

---

## party_1.yaml

Overall: Accurate. "Préséance" for "precedence" and the neutral framing are well handled. No issues.

---

## party_2.yaml

Overall: Accurate. Parallel with party_1 and consistent. No issues.

---

## patronymic_name.yaml

### Issue 1

- **Current (fr):** `Un nom derive du prenom du pere de la personne ou d'un ancetre paternel, utilise dans les conventions de denomination ou les patronymes constituent un element distinct du nom complet.`
- **Source (en):** `A name derived from the given name of the person's father or a paternal ancestor, used in naming conventions where patronymics are a distinct component of a person's full name.`
- **Issue:** Multiple missing accents: "derive" → "dérivé", "prenom" → "prénom", "pere" → "père", "ancetre" → "ancêtre", "utilise" → "utilisé", "denomination" → "dénomination", "element" → "élément". Also, the subordinate clause "ou les patronymes constituent un élément distinct" uses "ou" where "où" (relative adverb of place/circumstance) is needed. This is a homophone error that changes the meaning: "ou" = "or", "où" = "where/in which".
- **Proposed:** `Un nom dérivé du prénom du père de la personne ou d'un ancêtre paternel, utilisé dans les conventions de dénomination où les patronymes constituent un élément distinct du nom complet.`
- **Rationale:** Restores all required diacritics and corrects "ou" to "où" (relative adverb of circumstance).

---

## payment_amount.yaml

Overall: Clean and concise. No issues.

---

## payment_currency.yaml

Overall: Clean. "Code de devise ISO 4217" is standard. No issues.

---

## payment_date.yaml

Overall: Clean. No issues.

---

## payment_status.yaml

Overall: Clean. No issues.

---

## person.yaml

### Issue 1

- **Current (fr):** `Une référence à la Personne individuelle à laquelle ce dossier se rapporte.`
- **Source (en):** `A reference to the individual Person this record relates to.`
- **Issue:** "Individuelle" is redundant: a Person is by definition an individual. The English "individual" here is used as an intensifier to distinguish a single person from a group, but in French "la Personne" already carries that meaning. "Dossier" is a reasonable translation of "record" in a social protection context but could be "enregistrement" or "fiche" depending on context; "dossier" implies a file/case, while the English "record" is more neutral.
- **Proposed:** `Une référence à la Personne à laquelle cet enregistrement se rapporte.`
- **Rationale:** Drops the redundant "individuelle". "Enregistrement" is more register-neutral than "dossier" and closer to the English "record".

---

## phone_number.yaml

### Issue 1

- **Current (fr):** `Un numero de telephone de contact pour la personne, incluant l'indicatif pays.`
- **Source (en):** `A contact phone number for the person, including country code.`
- **Issue:** Missing accents: "numero" should be "numéro", "telephone" should be "téléphone". "Incluant l'indicatif pays" is acceptable but "indicatif pays" is slightly informal; the standard French term is "indicatif de pays" (with the preposition).
- **Proposed:** `Un numéro de téléphone de contact pour la personne, incluant l'indicatif de pays.`
- **Rationale:** Restores accents. "Indicatif de pays" is the standard ITU/ISO French term.

---

## place_of_usual_residence.yaml

Overall: Accurate and precise. "Lieu de résidence habituelle" is the standard French demographic term. "Bureaux nationaux de statistiques" is correct. No issues.

---

## place_type.yaml

### Issue 1

- **Current (fr):** `La catégorie de lieu où l'événement d'état civil s'est produit (établissement de santé, domicile, en chemin, etc.). Complète le lieu spécifique en décrivant le type de cadre dans lequel il s'est produit.`
- **Source (en):** `The category of place where the vital event occurred (health facility, home, en route, etc.). Complements the specific Location by describing what kind of setting it was.`
- **Issue:** "En chemin" for "en route" is natural French. However, "le type de cadre dans lequel il s'est produit" repeats "s'est produit" from the first sentence, creating a jarring echo. "Cadre" is adequate but "environnement" or "milieu" would be slightly more natural in a health/CRVS context for "setting". Also, "Complète le lieu spécifique" has the concept label "Location" in the English ("the specific Location"), which is preserved in the English; the French drops it. Concept labels should be preserved.
- **Proposed:** `La catégorie de lieu où l'événement d'état civil s'est produit (établissement de santé, domicile, en chemin, etc.). Complète la Localisation spécifique en décrivant le type de milieu concerné.`
- **Rationale:** Preserves the "Location" concept label as "Localisation" (consistent with the concept label convention). "Le type de milieu concerné" avoids the repeated verb and is more concise.

---

## postal_code.yaml

### Issue 1

- **Current (fr):** `Le code postal ou code zip de l'adresse.`
- **Source (en):** `The postal or zip code of the address.`
- **Issue:** "Code zip" is an Americanism. Outside the United States, this term is not standard; the French-language equivalent used internationally is "code postal" or, to distinguish US ZIP codes specifically, "code ZIP". For an internationally neutral audience, repeating "code postal" and adding the American variant in parentheses is clearer.
- **Proposed:** `Le code postal de l'adresse (ou code ZIP aux États-Unis).`
- **Rationale:** Keeps "code postal" as the primary term (internationally neutral) and relegates the Americanism to a parenthetical for completeness.

---

## preferred_language.yaml

Overall: Accurate. "La langue de communication préférée" and "codes ISO 639-3" are correct. No issues.

---

## preferred_name.yaml

### Issue 1

- **Current (fr):** `Le nom sous lequel une personne est couramment connue, lorsqu'il differe de son nom legal. Couvre les noms d'usage, les noms professionnels et les conventions de denomination ou prenom et nom de famille sont insuffisants.`
- **Source (en):** `The name a person is commonly known by, when it differs from their legal name. Covers chosen names, professional names, and naming conventions where given name plus family name is insufficient.`
- **Issue:** Missing accents: "differe" → "diffère", "legal" → "légal", "denomination" → "dénomination", "prenom" → "prénom". Same "ou/où" error as in patronymic_name: "ou prenom et nom de famille sont insuffisants" uses "ou" (or) but should be "où" (where/in which). Also, "noms d'usage" is the correct French term for "chosen names" in a civil registration context (it covers both chosen names and commonly-used names), but the English "chosen names" specifically refers to gender-chosen names or self-selected names. The established French term is "noms choisis" for this specific sense, distinct from "noms d'usage" (names in common use). Whether to collapse them depends on editorial policy; at minimum the accent and homophone errors must be fixed.
- **Proposed:** `Le nom sous lequel une personne est couramment connue, lorsqu'il diffère de son nom légal. Couvre les noms choisis, les noms professionnels et les conventions de dénomination où prénom et nom de famille sont insuffisants.`
- **Rationale:** Restores all diacritics. Corrects "ou" to "où". Uses "noms choisis" to match the English "chosen names" more precisely.

---

## previous_parents.yaml

Overall: Accurate and precise. "Adoption plénière" and "adoption simple" are the correct French civil law terms. "Droits parentaux biologiques" is standard. No issues.

---

## primary_crop.yaml

### Issue 1

- **Current (fr):** `La principale culture ou activité agricole de l'exploitation.`
- **Source (en):** `The primary crop or agricultural activity of the farm.`
- **Issue:** "L'exploitation" is a good translation of "farm" in an agricultural policy context (it means farm holding/operation). No language issue, but worth noting that "exploitation" is slightly formal and appropriate for the policy audience here. No change needed. Actually, the translation is clean.

Overall: Clean. No issues.

---

## program_ref.yaml

### Issue 1

- **Current (fr):** `Reference au programme.`
- **Source (en):** `Reference to the program.`
- **Issue:** Missing accent: "Reference" should be "Référence".
- **Proposed:** `Référence au programme.`
- **Rationale:** "Référence" requires the accent.

---

## quantity.yaml

### Issue 1

- **Current (fr):** `La quantite d'un produit dans l'unite de mesure specifiee.`
- **Source (en):** `The amount of a commodity in the specified unit of measure.`
- **Issue:** Missing accents: "quantite" → "quantité", "unite" → "unité", "specifiee" → "spécifiée". Also, "produit" for "commodity" is a slight semantic shift: "produit" is product/goods generically, while "commodity" in a social protection/food assistance context typically means "denrée" (foodstuff) or "marchandise" (good/commodity). "Produit" is acceptable but "denrée ou produit" would be more precise for the target domain.
- **Proposed:** `La quantité d'une denrée ou d'un produit dans l'unité de mesure spécifiée.`
- **Rationale:** Restores accents. "Denrée ou produit" covers both food commodity and non-food item contexts common in social protection in-kind transfers.

---

## quantity_redeemed.yaml

### Issue 1

- **Current (fr):** `La quantite de ce produit qui a ete echangee ou collectee jusqu'a present.`
- **Source (en):** `The amount of this commodity that has been redeemed or collected so far.`
- **Issue:** Missing accents throughout: "quantite" → "quantité", "ete" → "été", "echangee" → "échangée", "collectee" → "collectée", "jusqu'a" → "jusqu'à". Same "produit" vs "commodity" issue as in quantity.yaml. "Échangée" for "redeemed" is acceptable in a voucher context, but "utilisée" or "encaissée" is more standard in French social protection program language for voucher redemption.
- **Proposed:** `La quantité de cette denrée ou de ce produit qui a été encaissée ou collectée jusqu'à présent.`
- **Rationale:** Restores all accents. "Encaissée" is the standard French term for voucher redemption/cashing in. "Jusqu'à présent" requires the accent on "à".

---

## raw_score.yaml

Overall: Clean. "Le score numérique produit par l'instrument d'évaluation" is accurate and natural. No issues.

---

## receiving_program.yaml

### Issue 1

- **Current (fr):** `Référence au programme ou à l'organisation vers lequel l'orientation est dirigée.`
- **Source (en):** `Reference to the program or organization to which the referral is directed.`
- **Issue:** Gender agreement error. "Lequel" is masculine singular, but it refers to the closest antecedent "l'organisation" (feminine). The correct form is "vers lequel ou laquelle" or, better, restructuring to avoid the agreement conflict. Also "l'orientation" is a good rendering of "referral" in a French social service context; no issue there.
- **Proposed:** `Référence au programme ou à l'organisation vers lesquels l'orientation est dirigée.`
- **Rationale:** "Lesquels" (masculine plural used when the antecedents are mixed gender) resolves the agreement conflict cleanly. Alternatively: "vers lequel ou laquelle" for explicit gender marking, but the plural is more concise.

---

## recipient.yaml

### Issue 1

- **Current (fr):** `La personne ou le groupe qui a reçu ou est destiné à recevoir le paiement. Le destinataire peut différer du bénéficiaire inscrit, par exemple lorsqu'un tuteur, un mandataire de paiement ou un survivant perçoit au nom du bénéficiaire.`
- **Source (en):** `The person or group that received or is intended to receive the payment. The recipient may differ from the enrolled beneficiary, for example when a guardian, payment proxy, or survivor collects on behalf of the beneficiary.`
- **Issue:** "Est destiné à recevoir" is grammatically fine but applies the masculine singular ("destiné") to an antecedent that is "la personne ou le groupe" (a feminine or mixed pair). Strictly, "destinés à recevoir" (plural to cover both) would be more correct, or the sentence can be restructured. The second sentence is accurate and natural. "Mandataire de paiement" is a good rendering of "payment proxy".
- **Proposed:** `La personne ou le groupe qui a reçu ou est destiné à recevoir le paiement.` (no change to second sentence)
- **Rationale:** The agreement issue is minor; "destiné" could reasonably be read as attracted to "groupe" (nearest masculine noun). If strictly correct agreement is desired, "destinés" (plural) would cover both antecedents. Flag as low severity.

---

## Summary of issues by type

| Type | Count | Files |
|---|---|---|
| Missing diacritics | 10 | level_name, locations, longitude, matronymic_name, nationality, patronymic_name, phone_number, preferred_name, program_ref, quantity, quantity_redeemed |
| Calque / awkward construction | 5 | location_name, memberships, number_of_spouses, object_person, person |
| Homophone error (ou/où) | 2 | patronymic_name, preferred_name |
| Wrong technical term | 3 | manner_of_death, occupation, quantity/quantity_redeemed |
| Grammar/agreement | 2 | receiving_program, recipient |
| Terminology drift | 1 | marriage_ref |
| Dropped concept label | 1 | place_type |
