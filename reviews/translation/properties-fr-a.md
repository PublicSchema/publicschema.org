# French translation review: properties A–C (first batch)

Scope: `address`, `address_area`, `administrative_area`, `administrative_level`, `adoptee`, `adoption_type`, `adoptive_parents`, `affected_locations`, `affected_programs`, `age_at_event`, `altitude_max`, `altitude_min`, `amount`, `annotating_authority`, `annotation_date`, `annotation_text`, `annotation_type`, `annotations`, `applicant`, `area_description`, `assessed_entity`, `assessment_date`, `assessor`, `attendant_at_birth`, `beneficiary`, `benefit_description`, `benefit_modality`, `birth_order`, `birth_ref`, `birth_type`, `building_name`, `cause_of_death`, `cause_of_death_code`, `cause_of_death_coding_system`, `cause_of_death_method`, `cause_of_fetal_death`, `cause_of_fetal_death_code`, `cause_of_fetal_death_coding_system`, `certainty`, `certificate_document_type`, `certificate_format`, `certificate_number`, `child`, `city`, `civil_status_record`, `commodity_type`

---

## Authoring bug: stripped accents

Twelve files have French definitions where all accented characters are missing. This is almost certainly an encoding or copy-paste bug in the authoring tool, not a deliberate choice. The strings must be corrected.

---

**File:** `address_area.yaml`
**Current (fr):** "Le nom d'une zone geographique telle qu'un quartier ou un secteur qui regroupe des adresses en dessous du niveau de la ville."
**Source (en):** "The name of a geographic area such as a neighborhood, quarter, or ward that groups addresses below the city level."
**Issue:** Stripped accents throughout: `geographique` should be `géographique`.
**Proposed:** "Le nom d'une zone géographique telle qu'un quartier ou un secteur regroupant des adresses en dessous du niveau de la ville."
**Rationale:** Accent restoration. Minor phrasing improvement: `qui regroupe` → `regroupant` reads more naturally.

---

**File:** `administrative_area.yaml`
**Current (fr):** "La premiere subdivision administrative (province, etat, region) contenant l'adresse."
**Source (en):** "The first-level administrative subdivision (province, state, region) containing the address."
**Issue:** Stripped accents: `premiere` → `première`, `etat` → `État`.
**Proposed:** "La première subdivision administrative (province, État, région) contenant l'adresse."
**Rationale:** Accent restoration. `état` should be capitalized as `État` when referring to the political entity (a state in a federation).

---

**File:** `administrative_level.yaml`
**Current (fr):** "Le niveau numerique dans la hierarchie administrative, selon la convention OCHA COD-AB : 0 = pays, 1 = premier niveau sous-national (etat, province, region), 2 = deuxieme niveau sous-national (district, comte, departement), et ainsi de suite. Pas de profondeur maximale fixe."
**Source (en):** "The numeric tier in the administrative hierarchy, following the OCHA COD-AB convention: 0 = country, 1 = first subnational (state, province, region), 2 = second subnational (district, county, department), and so on. No fixed maximum depth."
**Issue:** Stripped accents throughout: `numerique` → `numérique`, `hierarchie` → `hiérarchie`, `etat` → `État`, `deuxieme` → `deuxième`, `comte` → `comté`, `departement` → `département`.
**Proposed:** "Le niveau numérique dans la hiérarchie administrative, selon la convention OCHA COD-AB : 0 = pays, 1 = premier niveau sous-national (État, province, région), 2 = deuxième niveau sous-national (district, comté, département), et ainsi de suite. Pas de profondeur maximale fixe."
**Rationale:** Accent restoration throughout.

---

**File:** `affected_locations.yaml`
**Current (fr):** "Les zones geographiques ou administratives affectees par cet evenement."
**Source (en):** "The geographic or administrative areas affected by this event."
**Issue:** Stripped accents: `geographiques` → `géographiques`, `affectees` → `affectées`, `evenement` → `événement`.
**Proposed:** "Les zones géographiques ou administratives affectées par cet événement."
**Rationale:** Accent restoration.

---

**File:** `affected_programs.yaml`
**Current (fr):** "Les programmes dont les operations ou les beneficiaires sont affectes par cet evenement."
**Source (en):** "Programs whose operations or beneficiaries are affected by this event."
**Issue:** Stripped accents: `operations` → `opérations`, `beneficiaires` → `bénéficiaires`, `affectes` → `affectés`, `evenement` → `événement`.
**Proposed:** "Les programmes dont les opérations ou les bénéficiaires sont affectés par cet événement."
**Rationale:** Accent restoration.

---

**File:** `altitude_max.yaml`
**Current (fr):** "L'altitude maximale de la zone, en metres au-dessus du niveau de la mer (datum WGS84)."
**Source (en):** "The maximum altitude of the area, in meters above sea level (WGS84 datum)."
**Issue:** Stripped accent: `metres` → `mètres`.
**Proposed:** "L'altitude maximale de la zone, en mètres au-dessus du niveau de la mer (datum WGS84)."
**Rationale:** Accent restoration.

---

**File:** `altitude_min.yaml`
**Current (fr):** "L'altitude minimale de la zone, en metres au-dessus du niveau de la mer (datum WGS84)."
**Source (en):** "The minimum altitude of the area, in meters above sea level (WGS84 datum)."
**Issue:** Stripped accent: `metres` → `mètres`.
**Proposed:** "L'altitude minimale de la zone, en mètres au-dessus du niveau de la mer (datum WGS84)."
**Rationale:** Accent restoration.

---

**File:** `area_description.yaml`
**Current (fr):** "Une description lisible de la zone geographique, comme un nom de region ou un libelle de limite administrative."
**Source (en):** "A human-readable description of the geographic area, such as a region name or administrative boundary label."
**Issue:** Stripped accents: `geographique` → `géographique`, `region` → `région`, `libelle` → `libellé`.
**Proposed:** "Une description lisible par un humain de la zone géographique, par exemple un nom de région ou un libellé de limite administrative."
**Rationale:** Accent restoration. "lisible par un humain" renders "human-readable" more faithfully.

---

**File:** `building_name.yaml`
**Current (fr):** "Le nom d'un batiment, d'un domaine ou d'un complexe, utilise dans les contextes ou les lieux sont identifies par leur nom plutot que par un numero de rue."
**Source (en):** "The name of a building, estate, or compound, used in contexts where locations are identified by name rather than street number."
**Issue:** Stripped accents throughout: `batiment` → `bâtiment`, `utilise` → `utilisé`, `ou` (relative pronoun) → `où`, `identifies` → `identifiés`, `plutot` → `plutôt`, `numero` → `numéro`.
**Proposed:** "Le nom d'un bâtiment, d'un domaine ou d'un complexe, utilisé dans les contextes où les lieux sont identifiés par leur nom plutôt que par un numéro de rue."
**Rationale:** Accent restoration throughout.

---

**File:** `certainty.yaml`
**Current (fr):** "La confiance que l'evenement s'est produit ou se produira."
**Source (en):** "The confidence that the event has occurred or will occur."
**Issue:** Stripped accent: `evenement` → `événement`.
**Proposed:** "Le degré de certitude que l'événement s'est produit ou se produira."
**Rationale:** Accent restoration. Also, `La confiance que...` is an awkward calque of "The confidence that...". `Le degré de certitude` is the idiomatic French phrase for this concept.

---

**File:** `city.yaml`
**Current (fr):** "La composante ville, bourg ou village de l'adresse."
**Source (en):** "The city, town, or village component of the address."
**Issue:** Word-order awkwardness. The English puts the noun list first and "component" after; the French does too, but `La composante X, Y ou Z de...` reads mechanically. Also the Spanish version, used for comparison, lacks accents too. No accent issue here in French.
**Note:** This is a minor style matter. No change required unless the reviewer wants a more natural rendering such as: "La partie ville, bourg ou village de l'adresse."
**Rationale:** Borderline. Leaving as no mandatory flag.

---

**File:** `commodity_type.yaml`
**Current (fr):** "Le type de produit ou de bien livre ou echangeable."
**Source (en):** "The type of commodity or goods being delivered or redeemable."
**Issue:** Stripped accents: `livre` → `livré`, `echangeable` → `échangeable`.
**Proposed:** "Le type de produit ou de bien livré ou échangeable."
**Rationale:** Accent restoration.

---

## Terminology and phrasing issues

---

**File:** `applicant.yaml`
**Current (fr):** "La personne ou le groupe ayant demandé et reçu cette décision d'éligibilité."
**Source (en):** "The person or group that applied for and received this eligibility decision."
**Issue:** "éligibilité" should be "admissibilité" per project convention.
**Proposed:** "La personne ou le groupe ayant demandé et obtenu cette décision d'admissibilité."
**Rationale:** Project convention: `éligible/éligibilité` → `admissible/admissibilité`. Also `reçu` → `obtenu` is more idiomatic for a formal decision.

---

**File:** `benefit_modality.yaml`
**Current (fr):** "La forme de prestation que l'ayant droit spécifie (espèces, bon, en nature, service, exonération de frais)."
**Source (en):** "The form of benefit the entitlement specifies (cash, voucher, in-kind, service, fee waiver)."
**Issue:** "l'ayant droit" is a calque of "the entitlement" but means "the rights-holder/beneficiary" in French legal language. The subject here is the entitlement (the record or policy instrument), not the person. This will confuse a policy officer.
**Proposed:** "La forme de prestation précisée par le droit (espèces, bon, en nature, service, exonération de frais)."
**Rationale:** `le droit` (without article + possessor) is the standard French term for an entitlement as a legal instrument, as distinct from `l'ayant droit` (the person entitled).

---

**File:** `birth_type.yaml`
**Current (fr):** "Indique si la naissance est unique, gémellaire, triple ou d'un ordre plus élevé. Saisie au niveau de l'accouchement, et non par nouveau-né."
**Source (en):** "Whether the birth was single, twin, triplet, or higher-order multiple. Captured at the level of the delivery, not per infant."
**Issue:** "Saisie" is a known project anti-pattern (calque of "captured"). It should use a form that describes what the field does, not the data entry act.
**Proposed:** "Indique si la naissance est unique, gémellaire, triple ou d'un ordre plus élevé. La valeur est enregistrée au niveau de l'accouchement, et non par nouveau-né."
**Rationale:** Per project convention, `Saisie` (calque of "captures") should be replaced with a more natural expression. `La valeur est enregistrée` is neutral and accurate.

---

**File:** `cause_of_death.yaml`
**Current (fr):** "Une description en texte libre de la cause sous-jacente du décès, telle qu'indiquée sur l'acte de décès. Saisie parallèlement à un cause_of_death_code codé lorsqu'une classification est disponible."
**Source (en):** "A free-text description of the underlying cause of death as stated on the death certificate. Captured alongside a coded cause_of_death_code when classification is available."
**Issue:** "Saisie parallèlement à" is a calque of "Captured alongside". Also "un cause_of_death_code codé" repeats `codé` twice in spirit (code_of_death_code is already a code). The repetition is inherited from English but is more glaring in French.
**Proposed:** "Une description en texte libre de la cause sous-jacente du décès, telle qu'indiquée sur l'acte de décès. Renseigné conjointement avec cause_of_death_code lorsqu'une classification est disponible."
**Rationale:** `Renseigné conjointement avec` avoids the "Saisie" calque while being natural. The redundancy of "codé" is dropped without changing meaning since `cause_of_death_code` already conveys "coded".

---

**File:** `cause_of_fetal_death.yaml`
**Current (fr):** "Une description en texte libre de la cause d'une mortinaissance. Saisie parallèlement à cause_of_fetal_death_code lorsqu'un code CIM-PM ou équivalent est attribué."
**Source (en):** "A free-text description of the cause of a fetal death. Captured alongside cause_of_fetal_death_code when an ICD-PM or equivalent code is assigned."
**Issue:** Same "Saisie parallèlement à" calque as in `cause_of_death`.
**Proposed:** "Une description en texte libre de la cause d'une mortinaissance. Renseigné conjointement avec cause_of_fetal_death_code lorsqu'un code CIM-PM ou équivalent est attribué."
**Rationale:** Consistency fix with `cause_of_death` correction above.

---

**File:** `annotation_type.yaml`
**Current (fr):** "La catégorie de mention: correction ordonnée par tribunal, changement de nationalité, ou autres modifications administratives portant sur la portée de l'acte."
**Source (en):** "The category of annotation: a court-ordered correction, a nationality change, or similar administrative modifications to the record's meaning."
**Issue:** "portant sur la portée de l'acte" is awkward: `portant sur la portée` repeats the same root. "the record's meaning" is better rendered as "le sens de l'acte" or "la teneur de l'acte".
**Proposed:** "La catégorie de mention : correction ordonnée par un tribunal, changement de nationalité, ou autres modifications administratives touchant à la teneur de l'acte."
**Rationale:** `portant sur la portée` is an accidental paronomasia that reads poorly. `touchant à la teneur` avoids the repetition and is precise (la teneur = the substance/meaning of a legal document).

---

## No issues

The following files have clean French translations with no flagged issues:

`address.yaml`, `adoptee.yaml`, `adoption_type.yaml`, `adoptive_parents.yaml`, `age_at_event.yaml`, `amount.yaml`, `annotating_authority.yaml`, `annotation_date.yaml`, `annotation_text.yaml`, `annotations.yaml`, `assessed_entity.yaml`, `assessment_date.yaml`, `assessor.yaml`, `attendant_at_birth.yaml`, `beneficiary.yaml`, `benefit_description.yaml`, `birth_order.yaml`, `birth_ref.yaml`, `cause_of_death_code.yaml`, `cause_of_death_coding_system.yaml`, `cause_of_death_method.yaml`, `cause_of_fetal_death_code.yaml`, `cause_of_fetal_death_coding_system.yaml`, `certificate_document_type.yaml`, `certificate_format.yaml`, `certificate_number.yaml`, `child.yaml`, `civil_status_record.yaml`
