# French translation review: properties batch C

Files reviewed: family_name_at_birth, family_register_status, farm_area_hectares, formation_date, framework_used, frequency, frequency_rule, full_address, gender, geocodes, geometry, gestational_age, given_name, given_name_at_birth, governing_jurisdiction, grievance_status, grievance_subject, grievance_type, group, group_memberships, group_type, hazard_type, head_of_household, house_number, identifier_scheme_id, identifier_scheme_name, identifier_type, identifier_value, identifiers, implementing_agency, income_source, industry, informant, is_active, is_enrolled, is_reconciled, issue_date, issued_to, issuing_authority, issuing_authority_location, issuing_jurisdiction, issuing_office, items, judgment_date, judgment_reference, latitude

---

## Systematic issue: stripped accents

A large number of files have completely stripped accents across the entire `definition.fr` string. This is a consistent encoding or authoring problem, not isolated typos. Each affected file is listed below with its full corrected translation.

---

### family_name_at_birth

**Current:** `"Le nom de famille de la personne au moment de la naissance, avant tout changement du a un mariage ou autre evenement juridique."`
**Issue:** Stripped accents. "du a" must be "dû à"; "evenement" must be "événement"; "juridique" is correct but the full string is unaccented throughout.
**Proposed:** `"Le nom de famille de la personne au moment de la naissance, avant tout changement dû à un mariage ou autre événement juridique."`
**Rationale:** Corrects missing diacritics throughout the string.

---

### formation_date

**Current:** `"La date a laquelle ce groupe a ete forme ou enregistre."`
**Issue:** Stripped accents. "a laquelle" must be "à laquelle"; "a ete forme" must be "a été formé"; "enregistre" must be "enregistré".
**Proposed:** `"La date à laquelle ce groupe a été formé ou enregistré."`
**Rationale:** Corrects missing diacritics throughout the string.

---

### frequency_rule

**Current:** `"Une regle de recurrence iCalendar (RRULE RFC 5545) specifiant un calendrier personnalise. Utilisee lorsque la propriete frequency est definie sur 'custom'."`
**Issue:** Stripped accents throughout. "regle" must be "règle"; "recurrence" must be "récurrence"; "specifiant" must be "spécifiant"; "personnalise" must be "personnalisé"; "Utilisee" must be "Utilisée"; "propriete" must be "propriété"; "definie" must be "définie".
**Proposed:** `"Une règle de récurrence iCalendar (RRULE RFC 5545) spécifiant un calendrier personnalisé. Utilisée lorsque la propriété frequency est définie sur 'custom'."`
**Rationale:** Corrects missing diacritics throughout. Technical tokens `iCalendar`, `RRULE`, `RFC 5545`, and `'custom'` are preserved unchanged.

---

### full_address

**Current:** `"L'adresse complete redigee sous forme d'une seule chaine de texte. Coexiste avec les composantes structurees de l'adresse pour les systemes qui stockent les adresses en texte libre."`
**Issue:** Stripped accents. "complete" must be "complète"; "redigee" must be "rédigée"; "chaine" must be "chaîne"; "structurees" must be "structurées"; "systemes" must be "systèmes".
**Proposed:** `"L'adresse complète rédigée sous forme d'une seule chaîne de texte. Coexiste avec les composantes structurées de l'adresse pour les systèmes qui stockent les adresses en texte libre."`
**Rationale:** Corrects missing diacritics throughout.

---

### gender

**Current:** `"Le genre de la personne tel qu'enregistre dans un registre de protection sociale ou un document d'identite."`
**Issue:** Stripped accents. "enregistre" must be "enregistré"; "identite" must be "identité".
**Proposed:** `"Le genre de la personne tel qu'enregistré dans un registre de protection sociale ou un document d'identité."`
**Rationale:** Corrects missing diacritics.

---

### geocodes

**Current:** `"Codes administratifs ou statistiques identifiant cette zone dans un systeme de codification (FIPS, P-code, code postal, etc.)."`
**Issue:** Stripped accent. "systeme" must be "système".
**Proposed:** `"Codes administratifs ou statistiques identifiant cette zone dans un système de codification (FIPS, P-code, code postal, etc.)."`
**Rationale:** Corrects one missing accent. Technical tokens `FIPS` and `P-code` are preserved.

---

### geometry

**Current:** `"La limite ou forme geographique, exprimee sous forme d'objet GeoJSON Geometry (Point, Polygon, MultiPolygon, etc.)."`
**Issue:** Stripped accents. "geographique" must be "géographique"; "exprimee" must be "exprimée".
**Proposed:** `"La limite ou forme géographique, exprimée sous forme d'objet GeoJSON Geometry (Point, Polygon, MultiPolygon, etc.)."`
**Rationale:** Corrects missing diacritics. Technical tokens `GeoJSON`, `Geometry`, `Point`, `Polygon`, `MultiPolygon` are preserved.

---

### given_name

**Current:** `"Le prenom de la personne."`
**Issue:** Stripped accent. "prenom" must be "prénom".
**Proposed:** `"Le prénom de la personne."`
**Rationale:** Corrects one missing accent.

---

### given_name_at_birth

**Current:** `"Le prenom de la personne au moment de la naissance, avant tout changement legal de nom."`
**Issue:** Stripped accents. "prenom" must be "prénom"; "legal" must be "légal".
**Proposed:** `"Le prénom de la personne au moment de la naissance, avant tout changement légal de nom."`
**Rationale:** Corrects missing diacritics.

---

### governing_jurisdiction

**Current:** `"Le pays ou la subdivision dont la legislation regit cette inscription. Implicite dans les programmes nationaux, mais doit etre explicite dans les contextes transfrontaliers ou federes tels que la coordination de la securite sociale entre pays."`
**Issue:** Stripped accents throughout. "legislation" must be "législation"; "regit" must be "régit"; "etre" must be "être"; "federes" must be "fédérés"; "securite" must be "sécurité".
**Proposed:** `"Le pays ou la subdivision dont la législation régit cette inscription. Implicite dans les programmes nationaux, mais doit être explicite dans les contextes transfrontaliers ou fédérés tels que la coordination de la sécurité sociale entre pays."`
**Rationale:** Corrects missing diacritics throughout.

---

### group_memberships

**Current:** `"Appartenances a des groupes detenues par cette personne, la reliant aux menages, familles ou autres groupes."`
**Issue:** Stripped accents. "a des" must be "à des"; "detenues" must be "détenues"; "menages" must be "ménages".
**Proposed:** `"Appartenances à des groupes détenues par cette personne, la reliant aux ménages, familles ou autres groupes."`
**Rationale:** Corrects missing diacritics.

---

### group_type

**Current:** `"La categorie administrative ou sociale du groupe."`
**Issue:** Stripped accent. "categorie" must be "catégorie".
**Proposed:** `"La catégorie administrative ou sociale du groupe."`
**Rationale:** Corrects one missing accent.

---

### hazard_type

**Current:** `"La categorie de risque ou d'evenement perturbateur."`
**Issue:** Stripped accents. "categorie" must be "catégorie"; "evenement" must be "événement".
**Proposed:** `"La catégorie de risque ou d'événement perturbateur."`
**Rationale:** Corrects missing diacritics.

---

### house_number

**Current:** `"Le numero de maison, de batiment ou de parcelle dans une rue ou une route."`
**Issue:** Stripped accents. "numero" must be "numéro"; "batiment" must be "bâtiment".
**Proposed:** `"Le numéro de maison, de bâtiment ou de parcelle dans une rue ou une route."`
**Rationale:** Corrects missing diacritics.

---

### identifier_scheme_id

**Current:** `"Un URI ou un code qui identifie le schema ou le systeme dans le cadre duquel l'identifiant a ete attribue."`
**Issue:** Stripped accents. "schema" must be "schéma"; "systeme" must be "système"; "ete attribue" must be "été attribué".
**Proposed:** `"Un URI ou un code qui identifie le schéma ou le système dans le cadre duquel l'identifiant a été attribué."`
**Rationale:** Corrects missing diacritics. Technical token `URI` is preserved.

---

### identifier_scheme_name

**Current:** `"Le nom lisible du schema d'identification, tel que 'Numero d'identite nationale' ou 'Numero de securite sociale'."`
**Issue:** Stripped accents. "schema" must be "schéma"; "Numero" must be "Numéro" (twice); "identite" must be "identité"; "securite" must be "sécurité".
**Proposed:** `"Le nom lisible du schéma d'identification, tel que 'Numéro d'identité nationale' ou 'Numéro de sécurité sociale'."`
**Rationale:** Corrects missing diacritics throughout, including inside the example values.

---

### identifier_type

**Current:** `"La categorie du document ou numero d'identification."`
**Issue:** Stripped accents. "categorie" must be "catégorie"; "numero" must be "numéro".
**Proposed:** `"La catégorie du document ou numéro d'identification."`
**Rationale:** Corrects missing diacritics.

---

### identifier_value

**Current:** `"La valeur alphanumerique de l'identifiant tel qu'il a ete delivre ou enregistre."`
**Issue:** Stripped accents. "alphanumerique" must be "alphanumérique"; "ete delivre" must be "été délivré"; "enregistre" must be "enregistré".
**Proposed:** `"La valeur alphanumérique de l'identifiant tel qu'il a été délivré ou enregistré."`
**Rationale:** Corrects missing diacritics.

---

### is_active

**File:** `is_active`
**Current:** `"Si ceci est actuellement actif."`
**Source:** `"Whether this is currently active."`
**Issue:** Awkward and impersonal construction. "Si ceci est..." reads like a conditional clause fragment rather than a property definition. The English is admittedly minimal, but the French should follow the pattern used in similar boolean properties (`is_enrolled` uses "Indique si...").
**Proposed:** `"Indique si cet élément est actuellement actif."`
**Rationale:** Aligns with the `is_enrolled` pattern ("Indique si...") and avoids the impersonal demonstrative "ceci" which sounds unnatural in a definition context. Adds the missing accent on "élément".

---

### issue_date

**Current:** `"La date a laquelle cet enregistrement ou document a ete delivre."`
**Issue:** Stripped accents. "a laquelle" must be "à laquelle"; "ete delivre" must be "été délivré".
**Proposed:** `"La date à laquelle cet enregistrement ou document a été délivré."`
**Rationale:** Corrects missing diacritics.

---

### issued_to

**Current:** `"La personne, le menage ou le groupe auquel le bon est attribue."`
**Issue:** Stripped accents. "menage" must be "ménage"; "attribue" must be "attribué".
**Proposed:** `"La personne, le ménage ou le groupe auquel le bon est attribué."`
**Rationale:** Corrects missing diacritics.

---

### issuing_authority

**Current:** `"L'organisation ou l'organe gouvernemental qui a delivre l'identifiant."`
**Issue:** Stripped accent. "delivre" must be "délivré".
**Proposed:** `"L'organisation ou l'organe gouvernemental qui a délivré l'identifiant."`
**Rationale:** Corrects one missing accent.

---

### issuing_jurisdiction

**Current:** `"La juridiction geographique qui a delivre l'identifiant, exprimee sous forme de code de subdivision ISO 3166-2 ou de code de pays ISO 3166-1."`
**Issue:** Stripped accents. "geographique" must be "géographique"; "delivre" must be "délivré"; "exprimee" must be "exprimée".
**Proposed:** `"La juridiction géographique qui a délivré l'identifiant, exprimée sous forme de code de subdivision ISO 3166-2 ou de code de pays ISO 3166-1."`
**Rationale:** Corrects missing diacritics. Technical tokens `ISO 3166-2` and `ISO 3166-1` are preserved.

---

### items

**Current:** `"La liste des lignes de produits dans cette livraison ou ce bon."`
**Issue:** No missing accents, but "lignes de produits" is an unusual rendering of "commodity line items". A commodity line item in a delivery context is more naturally "articles" or "lignes d'articles".
**Source:** `"The list of commodity line items in this delivery or voucher."`
**Proposed:** `"La liste des articles dans cette livraison ou ce bon."`
**Rationale:** "Lignes de produits" is a calque of "product lines" (a different concept). "Articles" is the natural French term for individual items in a delivery list and is unambiguous to a program officer.

---

### latitude

**Current:** `"La latitude geographique en degres decimaux (WGS84)."`
**Issue:** Stripped accents. "geographique" must be "géographique"; "degres decimaux" must be "degrés décimaux".
**Proposed:** `"La latitude géographique en degrés décimaux (WGS84)."`
**Rationale:** Corrects missing diacritics. Technical token `WGS84` is preserved.

---

## Terminology note

### income_source

**Current:** `"La principale source de revenus déclarée pour le ménage, utilisée dans le ciblage et les tests de substitution."`
**Source:** `"The primary reported source of income for the household, used in targeting and proxy means testing."`
**Issue:** "Tests de substitution" is a near-calque for "proxy means testing" but is not an established term for French-speaking policy audiences. The accepted French term in international development practice is "test des moyens indirects" or "évaluation des moyens par approximation". "Substitution" introduces a different semantic (replacement) rather than the concept of using observable proxies to estimate income.
**Proposed:** `"La principale source de revenus déclarée pour le ménage, utilisée dans le ciblage et les tests des moyens par approximation."`
**Rationale:** Aligns with ILO and World Bank French-language documentation terminology. Avoids the misleading "substitution" framing.

---

## Grievance_type: style flag

**Current:** `"La catégorie de grief ou de plainte, classifiant la nature du problème soulevé."`
**Source:** `"The category of grievance or complaint, classifying the nature of the issue raised."`
**Issue:** "classifiant" (present participle) creates a dangling modifier; the subject of the participial clause would be the category itself classifying the nature, which is circular. The English construction has the same weakness but reads less awkwardly in English than the French participial.
**Proposed:** `"La catégorie de grief ou de plainte, selon la nature du problème soulevé."`
**Rationale:** "selon la nature" expresses the same grouping logic more cleanly without the circular participial. Alternatively: `"qui classifie la nature du problème soulevé"` with a relative clause.

---

## Clean files (no issues found)

family_register_status, farm_area_hectares, framework_used, frequency, gestational_age, grievance_status, grievance_subject, group, head_of_household, identifiers, implementing_agency, industry, informant, is_enrolled, is_reconciled, issuing_authority_location, issuing_office, judgment_date, judgment_reference
