# French vocabulary review — root + synced defs

## Summary
- Files reviewed: 25
- Files with issues: 16
- Files clean: 9
- Em dashes found: 0

**Files clean (no changes proposed):**
- schema/vocabularies/delivery-channel.yaml
- schema/vocabularies/group-role.yaml
- schema/vocabularies/group-type.yaml
- schema/vocabularies/literacy.yaml
- schema/vocabularies/marital-status.yaml
- schema/vocabularies/payment-status.yaml
- schema/vocabularies/relationship-type.yaml
- schema/vocabularies/sex.yaml
- schema/vocabularies/country.yaml

---

## Per-file findings

### schema/vocabularies/delivery-channel.yaml

No changes proposed.

---

### schema/vocabularies/education-level.yaml

No changes proposed.

---

### schema/vocabularies/employment-status.yaml

#### Top-level definition
No issue. The translation is accurate and natural.

#### values

- `unemployed`.label — current: `Chômeur` — proposed: `Sans emploi` — reason: `Chômeur` is masculine. The label must be gender-neutral since it describes a category, not a gendered individual. `Sans emploi` is the standard neutral form in ILO and French statistical usage, and is internationally understood across all Francophone regions.

- `unemployed`.definition — current: `"Personnes en âge de travailler qui n'étaient pas en emploi, ont mené des activités de recherche d'emploi et étaient actuellement disponibles pour occuper un emploi."` — proposed: `"Personnes en âge de travailler qui n'étaient pas en emploi, qui ont mené des activités de recherche d'emploi et qui étaient disponibles pour prendre un emploi."` — reason: Removes the jarring tense inconsistency between "n'étaient pas" (imperfect) and "actuellement" (present adverb). "Actuellement disponibles" in a past-tense description is awkward; the proposed form stays consistently in the past and replaces "actuellement" with the cleaner implicit past-tense reading. Also, repeating the relative "qui" before each clause is more natural in formal French. "Prendre un emploi" is more natural than "occuper un emploi" in this statistical context (ILO French uses "occuper un emploi" for the employed, "prendre un emploi" for the availability condition of the unemployed).

- `outside_labour_force`.definition — current: `"Personnes en âge de travailler qui n'étaient ni employées ni au chômage pendant la période de référence (par exemple, étudiants, retraités, personnes au foyer, travailleurs découragés)."` — proposed: `"Personnes en âge de travailler qui n'étaient ni en emploi ni au chômage pendant la période de référence (par exemple, étudiants, retraités, personnes au foyer, travailleurs découragés)."` — reason: The French statistical convention (ILO) uses "en emploi" as the adjective form for the employed state, paralleling "au chômage". "Employées" is not wrong, but "en emploi" is the canonical ILO French phrasing and is more consistent with the other ILO-sourced text in this vocabulary.

---

### schema/vocabularies/event-certainty.yaml

This file has **pervasive stripped accents** across the top-level definition and all value labels and definitions. This is a systemic authoring bug — the entire French content requires rewriting with proper diacritics.

#### Top-level definition
- Issue: Stripped accents throughout.
- Current: `"La confiance qu'un evenement s'est produit ou se produira. Les valeurs sont compatibles avec les codes de certitude d'OASIS CAP v1.2."`
- Proposed: `"Le degré de certitude qu'un événement s'est produit ou se produira. Les valeurs sont compatibles avec les codes de certitude d'OASIS CAP v1.2."`
- Reason: Stripped accents repaired (`evenement` → `événement`). Also, "La confiance que" is a calque of the English "The confidence that"; in French statistical and emergency management usage, "degré de certitude" or "niveau de certitude" is the canonical phrasing.

#### values

- `observed`.label — current: `Observe` — proposed: `Observé` — reason: Missing accent.

- `observed`.definition — current: `"L'evenement a ete observe ou confirme."` — proposed: `"L'événement a été observé ou confirmé."` — reason: Multiple stripped accents (`evenement`, `ete`, `observe`, `confirme`).

- `likely`.label — current: `Probable` — proposed: `Probable` — reason: Clean (no accent needed). No change.

- `likely`.definition — current: `"L'evenement est susceptible de se produire (probabilite superieure a 50%)."` — proposed: `"L'événement est susceptible de se produire (probabilité supérieure à 50%)."` — reason: Stripped accents (`evenement`, `probabilite`, `superieure`, `a`).

- `possible`.definition — current: `"L'evenement est possible mais peu probable (probabilite inferieure a 50%)."` — proposed: `"L'événement est possible mais peu probable (probabilité inférieure à 50%)."` — reason: Stripped accents (`evenement`, `probabilite`, `inferieure`).

- `unlikely`.definition — current: `"L'evenement n'est pas prevu."` — proposed: `"L'événement n'est pas prévu."` — reason: Stripped accents (`evenement`, `prevu`). Note: this definition differs from the English ("not expected to occur") — the French "n'est pas prévu" is appropriate and slightly stronger than literal, which is acceptable.

- `unknown`.label — current: `Inconnue` — proposed: `Inconnu` — reason: The label refers to the state of certainty (masculine noun "degré de certitude" or "niveau"), not a gendered entity. `Inconnu` is the canonical masculine/neutral form used when the referent is an abstract state. (Cross-check: event-severity uses `Inconnue` for the same code — see that file's note.)

- `unknown`.definition — current: `"La certitude n'est pas encore determinee."` — proposed: `"La certitude n'est pas encore déterminée."` — reason: Stripped accent (`determinee`).

---

### schema/vocabularies/event-severity.yaml

This file has **pervasive stripped accents** across the top-level definition and most value labels and definitions. Full rewrite of affected strings required.

#### Top-level definition
- Issue: Stripped accents throughout.
- Current: `La gravite observee ou attendue de l'impact d'un evenement. Les valeurs sont compatibles avec les codes de gravite d'OASIS CAP v1.2.`
- Proposed: `La gravité observée ou attendue de l'impact d'un événement. Les valeurs sont compatibles avec les codes de gravité d'OASIS CAP v1.2.`
- Reason: Stripped accents (`gravite` × 2, `observee`, `evenement`).

#### values

- `extreme`.label — current: `Extreme` — proposed: `Extrême` — reason: Missing accent (circumflex).

- `moderate`.label — current: `Moderee` — proposed: `Modérée` — reason: Stripped accents (`Moderee` should be `Modérée`).

- `minor`.definition — current: `Menace minimale ou nulle pour la vie ou les biens.` — proposed: No change needed (no diacritic issue here). Clean.

- `unknown`.definition — current: `La gravite n'est pas encore determinee.` — proposed: `La gravité n'est pas encore déterminée.` — reason: Stripped accents (`gravite`, `determinee`).

- `unknown`.label — current: `Inconnue` — proposed: `Inconnue` — reason: In this context the label refers to the severity level (feminine noun `gravité`), so `Inconnue` is actually correct here. No change. (Contrast with event-certainty above where the referent is abstract/masculine.)

Additional value definitions to check for stripped accents:

- `extreme`.definition — current: `Menace extraordinaire pour la vie ou les biens.` — proposed: No change. Clean.

- `severe`.definition — current: `Menace significative pour la vie ou les biens.` — proposed: No change. Clean.

- `moderate`.definition — current: `Menace possible pour la vie ou les biens.` — proposed: No change. Clean.

- `minor`.label — current: `Mineure` — proposed: No change. Clean.

---

### schema/vocabularies/gender-type.yaml

This file has **pervasive stripped accents** in the values section. The top-level definition is clean.

#### Top-level definition
No issue. Clean.

#### values

- `male`.definition — current: `La personne s'identifie ou est enregistree comme homme.` — proposed: `La personne s'identifie ou est enregistrée comme homme.` — reason: Stripped accent (`enregistree`).

- `female`.definition — current: `La personne s'identifie ou est enregistree comme femme.` — proposed: `La personne s'identifie ou est enregistrée comme femme.` — reason: Stripped accent (`enregistree`).

- `male`.label — current: `Masculin` — proposed: No change. Clean.

- `female`.label — current: `Feminin` — proposed: `Féminin` — reason: Stripped accent (`Feminin` should be `Féminin`).

- `not_stated`.label — current: `Non declare` — proposed: `Non déclaré` — reason: Stripped accent (`declare` should be `déclaré`).

- `not_stated`.definition — current: `Le genre n'a pas ete enregistre ou la personne a refuse de le divulguer.` — proposed: `Le genre n'a pas été enregistré ou la personne a refusé de le divulguer.` — reason: Stripped accents (`ete`, `enregistre`, `refuse`).

---

### schema/vocabularies/group-role.yaml

No changes proposed.

---

### schema/vocabularies/group-type.yaml

No changes proposed.

---

### schema/vocabularies/hazard-type.yaml

This file has **pervasive stripped accents** across the top-level definition and all value labels and definitions. Full rewrite of all affected strings required.

#### Top-level definition
- Issue: Stripped accents throughout.
- Current: `"La categorie de risque ou d'evenement perturbateur, basee sur la classification du Cadre de Sendai avec des extensions pour les chocs sociaux et economiques."`
- Proposed: `"La catégorie de risque ou d'événement perturbateur, basée sur la classification du Cadre de Sendai avec des extensions pour les chocs sociaux et économiques."`
- Reason: Stripped accents (`categorie`, `evenement`, `basee`, `economiques`).

#### values

- `geophysical`.label — current: `Geophysique` — proposed: `Géophysique` — reason: Stripped accent.

- `geophysical`.definition — current: `"Tremblements de terre, glissements de terrain, tsunamis ou activite volcanique."` — proposed: `"Tremblements de terre, glissements de terrain, tsunamis ou activité volcanique."` — reason: Stripped accent (`activite`).

- `meteorological`.label — current: `Meteorologique` — proposed: `Météorologique` — reason: Stripped accent.

- `meteorological`.definition — current: `"Inondations, tempetes, temperatures extremes ou secheresse."` — proposed: `"Inondations, tempêtes, températures extrêmes ou sécheresse."` — reason: Stripped accents (`tempetes`, `temperatures`, `extremes`, `secheresse`).

- `biological`.label — current: `Biologique` — proposed: No change. Clean.

- `biological`.definition — current: `"Epidemies, infestations de ravageurs ou contamination biologique."` — proposed: `"Épidémies, infestations de ravageurs ou contamination biologique."` — reason: Stripped accents (`Epidemies` should be `Épidémies`). Note: the English definition includes "Disease outbreaks, epidemics, pest infestations, or biological contamination." The French drops "disease outbreaks" as a separate term; this may be intentional (épidémie covers both) or an omission. Flagged as an open question.

- `environmental`.label — current: `Environnemental` — proposed: No change. Clean.

- `environmental`.definition — current: `"Pollution, deforestation, desertification ou degradation ecologique."` — proposed: `"Pollution, déforestation, désertification ou dégradation écologique."` — reason: Stripped accents (`deforestation`, `desertification`, `degradation`, `ecologique`).

- `technological`.label — current: `Technologique` — proposed: No change. Clean.

- `technological`.definition — current: `"Accidents industriels, defaillances d'infrastructure ou deversements chimiques."` — proposed: `"Accidents industriels, défaillances d'infrastructure ou déversements chimiques."` — reason: Stripped accents (`defaillances`, `deversements`).

- `conflict`.label — current: `Conflit` — proposed: No change. Clean.

- `conflict`.definition — current: `"Conflit arme, troubles civils ou deplacement force."` — proposed: `"Conflit armé, troubles civils ou déplacement forcé."` — reason: Stripped accents (`arme`, `deplacement`, `force`).

- `economic`.label — current: `Economique` — proposed: `Économique` — reason: Stripped accent on initial capital.

- `economic`.definition — current: `"Chocs economiques tels que flambee des prix, effondrement monetaire ou perturbation des marches."` — proposed: `"Chocs économiques tels que flambée des prix, effondrement monétaire ou perturbation des marchés."` — reason: Stripped accents (`economiques`, `flambee`, `monetaire`, `marches`).

- `other`.definition — current: `"Evenements non couverts par aucune autre categorie."` — proposed: `"Événements non couverts par aucune autre catégorie."` — reason: Stripped accents (`Evenements`, `categorie`).

---

### schema/vocabularies/identifier-type.yaml

This file has **pervasive stripped accents** across all value labels and definitions. The top-level definition also has stripped accents.

#### Top-level definition
- Issue: Stripped accents.
- Current: `Categories de documents ou de numeros d'identification utilises pour identifier les personnes dans les systemes administratifs et de prestation de services.`
- Proposed: `Catégories de documents ou de numéros d'identification utilisés pour identifier les personnes dans les systèmes administratifs et de prestation de services.`
- Reason: Stripped accents (`Categories`, `numeros`, `utilises`, `systemes`).

#### values

- `national_id`.label — current: `Carte d'identite nationale` — proposed: `Carte d'identité nationale` — reason: Stripped accent (`identite`).

- `national_id`.definition — current: `Un numero ou une carte d'identite nationale delivre par le gouvernement.` — proposed: `Un numéro ou une carte d'identité nationale délivré par le gouvernement.` — reason: Stripped accents (`numero`, `identite`, `delivre`).

- `birth_certificate`.definition — current: `Un document officiel de naissance delivre par un registre d'etat civil.` — proposed: `Un document officiel de naissance délivré par un registre d'état civil.` — reason: Stripped accents (`delivre`, `etat`). Note: `acte de naissance` is the canonical civil registration term in French; `document officiel de naissance` is acceptable but see open questions.

- `passport`.definition — current: `Un document de voyage delivre par le gouvernement servant egalement de preuve d'identite et de nationalite.` — proposed: `Un document de voyage délivré par le gouvernement servant également de preuve d'identité et de nationalité.` — reason: Stripped accents (`delivre`, `egalement`, `identite`, `nationalite`).

- `voter_id`.label — current: `Carte d'electeur` — proposed: `Carte d'électeur` — reason: Stripped accent (`electeur`).

- `voter_id`.definition — current: `Un document d'identite delivre a des fins d'inscription electorale.` — proposed: `Un document d'identité délivré à des fins d'inscription électorale.` — reason: Stripped accents (`identite`, `delivre`, `a`, `electorale`).

- `program_id`.definition — current: `Un identifiant de beneficiaire attribue par un programme specifique.` — proposed: `Un identifiant de bénéficiaire attribué par un programme spécifique.` — reason: Stripped accents (`beneficiaire`, `attribue`, `specifique`).

- `household_id`.label — current: `Identifiant de menage` — proposed: `Identifiant de ménage` — reason: Stripped accent (`menage`).

- `household_id`.definition — current: `Un identifiant attribue a un menage plutot qu'a une personne individuelle.` — proposed: `Un identifiant attribué à un ménage plutôt qu'à une personne individuelle.` — reason: Stripped accents (`attribue`, `a` × 2, `menage`, `plutot`).

- `social_security_number`.label — current: `Numero de securite sociale` — proposed: `Numéro de sécurité sociale` — reason: Stripped accents (`Numero`, `securite`).

- `social_security_number`.definition — current: `Un numero attribue par une administration de securite sociale ou d'assurance sociale, distinct du numero d'identite nationale dans de nombreux pays.` — proposed: `Un numéro attribué par une administration de sécurité sociale ou d'assurance sociale, distinct du numéro d'identité nationale dans de nombreux pays.` — reason: Stripped accents (`numero` × 2, `attribue`, `securite`, `identite`).

- `tax_id`.definition — current: `Un numero d'identification fiscale attribue par une autorite fiscale ou de recettes.` — proposed: `Un numéro d'identification fiscale attribué par une autorité fiscale ou de recettes.` — reason: Stripped accents (`numero`, `attribue`, `autorite`).

- `drivers_license`.definition — current: `Un permis delivre par le gouvernement pour conduire des vehicules a moteur, couramment utilise comme piece d'identite.` — proposed: `Un permis délivré par le gouvernement pour conduire des véhicules à moteur, couramment utilisé comme pièce d'identité.` — reason: Stripped accents (`delivre`, `vehicules`, `a`, `utilise`, `piece`, `identite`).

- `marriage_certificate`.definition — current: `Un document officiel de mariage delivre par un registre d'etat civil ou une autorite religieuse.` — proposed: `Un document officiel de mariage délivré par un registre d'état civil ou une autorité religieuse.` — reason: Stripped accents (`delivre`, `etat`, `autorite`).

- `death_certificate`.definition — current: `Un document officiel de deces delivre par un registre d'etat civil ou une autorite sanitaire.` — proposed: `Un document officiel de décès délivré par un registre d'état civil ou une autorité sanitaire.` — reason: Stripped accents (`deces`, `delivre`, `etat`, `autorite`).

- `other`.definition — current: `Un type d'identifiant non couvert par les autres categories.` — proposed: `Un type d'identifiant non couvert par les autres catégories.` — reason: Stripped accent (`categories`).

---

### schema/vocabularies/literacy.yaml

No changes proposed.

---

### schema/vocabularies/marital-status.yaml

No changes proposed.

---

### schema/vocabularies/payment-status.yaml

#### Top-level definition
No issue.

#### values

- `rejected`.definition — current: `Le paiement a été évalué et refusé sur la base d'une décision commerciale ou politique, telle qu'un contrôle d'éligibilité échoué ou une réclamation contestée.` — proposed: `Le paiement a été évalué et refusé sur la base d'une décision institutionnelle ou réglementaire, telle qu'un contrôle d'admissibilité non satisfait ou une réclamation contestée.` — reason: Two issues. First, "éligibilité" should be "admissibilité" per the cross-file consistency rule. Second, "décision commerciale ou politique" is a poor rendering of "business or policy decision" — "commerciale" implies a commercial/profit context inappropriate for social protection; "institutionnelle ou réglementaire" is the correct domain-neutral French for an administrative benefit decision. Also "contrôle d'éligibilité échoué" — the phrase "échoué" applied to a "contrôle" is unusual; "non satisfait" or "négatif" is more natural.

- `cancelled`.definition — current: `Le paiement a été annulé avant la transmission, généralement en raison de changements d'éligibilité ou d'une décision administrative.` — proposed: `Le paiement a été annulé avant la transmission, généralement en raison de changements d'admissibilité ou d'une décision administrative.` — reason: "éligibilité" → "admissibilité" per cross-file consistency rule.

---

### schema/vocabularies/relationship-type.yaml

No changes proposed.

---

### schema/vocabularies/sex.yaml

No changes proposed.

---

### schema/vocabularies/status-in-employment.yaml

#### Top-level definition
No issue. Clean.

#### values

All value labels and definitions appear clean (proper accents, natural French, ILO-aligned terminology). One minor note:

- `contributing_family_worker`.label — current: `Travailleur familial collaborant` — proposed: `Aide familial` — reason: The ILO French canonical term for ICSE-18 "contributing family worker" is "aide familial" (see ILO French publications on ICSE-18). "Travailleur familial collaborant" is a literal back-translation from English and is not the term used in ILO French statistical materials. However, this is a terminology judgment call rather than a diacritic error, so flagged as an open question rather than a hard correction.

---

### schema/vocabularies/unit-of-measure.yaml

This file has **pervasive stripped accents** across the top-level definition and all value definitions. Full rewrite of all affected strings required.

#### Top-level definition
- Issue: Stripped accents throughout.
- Current: `Unites de mesure pour les quantites de biens distribues ou echangeables dans les programmes de prestations.`
- Proposed: `Unités de mesure pour les quantités de biens distribués ou échangeables dans les programmes de prestations.`
- Reason: Stripped accents (`Unites`, `quantites`, `distribues`, `echangeables`).

#### values

- `kg`.definition — current: `Unite de masse egale a 1 000 grammes.` — proposed: `Unité de masse égale à 1 000 grammes.` — reason: Stripped accents (`Unite`, `egale`, `a`).

- `g`.definition — current: `Unite de masse egale a un millieme de kilogramme.` — proposed: `Unité de masse égale à un millième de kilogramme.` — reason: Stripped accents (`Unite`, `egale`, `a`, `millieme`).

- `l`.definition — current: `Unite de volume egale a 1 000 centimetres cubes.` — proposed: `Unité de volume égale à 1 000 centimètres cubes.` — reason: Stripped accents (`Unite`, `egale`, `a`, `centimetres`).

- `ml`.definition — current: `Unite de volume egale a un millieme de litre.` — proposed: `Unité de volume égale à un millième de litre.` — reason: Stripped accents (`Unite`, `egale`, `a`, `millieme`).

- `unit`.label — current: `Unite` — proposed: `Unité` — reason: Stripped accent.

- `unit`.definition — current: `Un article denombrable discret (par ex., un manuel, un paquet de semences).` — proposed: `Un article dénombrable discret (par ex., un manuel, un paquet de semences).` — reason: Stripped accent (`denombrable`).

- `kit`.definition — current: `Un ensemble pre-assemble de plusieurs articles (par ex., kit d'hygiene, kit educatif).` — proposed: `Un ensemble pré-assemblé de plusieurs articles (par ex., kit d'hygiène, kit éducatif).` — reason: Stripped accents (`pre-assemble`, `hygiene`, `educatif`).

- `meal`.definition — current: `Une portion de repas prepare (utilise dans les programmes d'alimentation scolaire et institutionnels).` — proposed: `Une portion de repas préparé (utilisée dans les programmes d'alimentation scolaire et institutionnels).` — reason: Stripped accents (`prepare`, `utilise`). Also: `une portion` is feminine, so the past participle should be `utilisée` not `utilisé`.

- `mt`.label — current: `Tonne metrique` — proposed: `Tonne métrique` — reason: Stripped accent (`metrique`).

- `mt`.definition — current: `Unite de masse egale a 1 000 kilogrammes. Utilisee pour le suivi des produits en vrac.` — proposed: `Unité de masse égale à 1 000 kilogrammes. Utilisée pour le suivi des produits en vrac.` — reason: Stripped accents (`Unite`, `egale`, `a`, `Utilisee`).

---

### schema/vocabularies/voucher-format.yaml

This file has **pervasive stripped accents** across the top-level definition and all value labels and definitions.

#### Top-level definition
- Issue: Stripped accent.
- Current: `La forme physique ou numerique d'un bon.`
- Proposed: `La forme physique ou numérique d'un bon.`
- Reason: Stripped accent (`numerique`).

#### values

- `electronic`.label — current: `Electronique` — proposed: `Électronique` — reason: Missing accent on initial capital.

- `electronic`.definition — current: `Un code ou jeton numerique delivre par SMS, application mobile, code QR ou autre moyen electronique.` — proposed: `Un code ou jeton numérique délivré par SMS, application mobile, code QR ou autre moyen électronique.` — reason: Stripped accents (`numerique`, `delivre`, `electronique`).

- `paper`.definition — current: `Un document imprime que le beneficiaire presente physiquement chez un vendeur ou un point de distribution.` — proposed: `Un document imprimé que le bénéficiaire présente physiquement chez un vendeur ou un point de distribution.` — reason: Stripped accents (`imprime`, `beneficiaire`, `presente`).

---

### schema/vocabularies/voucher-status.yaml

This file has **pervasive stripped accents** across the top-level definition and all value labels and definitions.

#### Top-level definition
- Issue: Stripped accents throughout.
- Current: `Les etats du cycle de vie d'un instrument de bon, de la creation a l'echange ou l'expiration.`
- Proposed: `Les états du cycle de vie d'un instrument de bon, de la création à l'échange ou à l'expiration.`
- Reason: Stripped accents (`etats`, `creation`, `a`, `echange`). Also added second `à` before `l'expiration` for grammatical completeness.

#### values

- `created`.label — current: `Cree` — proposed: `Créé` — reason: Stripped accents (`Cree` should be `Créé`).

- `created`.definition — current: `Le bon a ete genere mais n'a pas encore ete distribue au beneficiaire.` — proposed: `Le bon a été généré mais n'a pas encore été distribué au bénéficiaire.` — reason: Stripped accents (`ete` × 2, `genere`, `distribue`, `beneficiaire`).

- `issued`.label — current: `Emis` — proposed: `Émis` — reason: Stripped accent on initial capital.

- `issued`.definition — current: `Le bon a ete distribue au beneficiaire ou a son representant autorise.` — proposed: `Le bon a été distribué au bénéficiaire ou à son représentant autorisé.` — reason: Stripped accents (`ete`, `distribue`, `beneficiaire`, `a`, `representant`, `autorise`).

- `suspended`.definition — current: `Le bon a ete temporairement desactive et ne peut pas etre echange jusqu'a sa reactivation. Les raisons incluent une suspicion de fraude, des verifications ou des blocages administratifs.` — proposed: `Le bon a été temporairement désactivé et ne peut pas être échangé jusqu'à sa réactivation. Les raisons incluent une suspicion de fraude, des vérifications ou des blocages administratifs.` — reason: Stripped accents (`ete`, `desactive`, `etre`, `echange`, `jusqu'a`, `reactivation`, `verifications`).

- `partially_redeemed`.label — current: `Partiellement echange` — proposed: `Partiellement échangé` — reason: Stripped accent (`echange`).

- `partially_redeemed`.definition — current: `Une partie mais pas la totalite de la valeur du bon ou des produits auxquels il donne droit a ete echangee. Le bon reste actif pour une utilisation ulterieure jusqu'a echange complet ou expiration.` — proposed: `Une partie mais pas la totalité de la valeur du bon ou des produits auxquels il donne droit a été échangée. Le bon reste actif pour une utilisation ultérieure jusqu'à échange complet ou expiration.` — reason: Stripped accents (`totalite`, `a` (auxiliary "a été"), `ete`, `echangee`, `ulterieure`, `jusqu'a`).

- `redeemed`.label — current: `Echange` — proposed: `Échangé` — reason: Stripped accent on initial capital and final.

- `redeemed`.definition — current: `Le bon a ete entierement utilise aupres d'un vendeur ou d'un agent.` — proposed: `Le bon a été entièrement utilisé auprès d'un vendeur ou d'un agent.` — reason: Stripped accents (`ete`, `entierement`, `utilise`, `aupres`).

- `expired`.label — current: `Expire` — proposed: `Expiré` — reason: Stripped accent.

- `expired`.definition — current: `La periode de validite du bon est passee sans echange.` — proposed: `La période de validité du bon est passée sans échange.` — reason: Stripped accents (`periode`, `validite`, `passee`, `echange`).

- `cancelled`.label — current: `Annule` — proposed: `Annulé` — reason: Stripped accent.

- `cancelled`.definition — current: `Le bon a ete annule par le programme avant l'echange.` — proposed: `Le bon a été annulé par le programme avant l'échange.` — reason: Stripped accents (`ete`, `annule`, `echange`).

---

## Group B: Synced vocabularies (top-level definition.fr only)

### schema/vocabularies/country.yaml

#### Top-level definition
No changes proposed. Current: `Pays et territoires tels que définis par la norme ISO 3166-1, utilisant les codes alpha-2.` — Clean, proper diacritics, internationally neutral.

---

### schema/vocabularies/currency.yaml

#### Top-level definition
No changes proposed. Current: `Codes de devises tels que définis par la norme ISO 4217.` — Clean.

---

### schema/vocabularies/language.yaml

#### Top-level definition
No changes proposed. Current: `Codes de langues tels que définis par la norme ISO 639-3, couvrant toutes les langues humaines connues.` — Clean.

---

### schema/vocabularies/region.yaml

#### Top-level definition
No changes proposed. Current: `Régions géographiques et groupements de pays tels que définis par la norme M49 des Nations Unies.` — Clean.

---

### schema/vocabularies/script.yaml

#### Top-level definition
No changes proposed. Current: `Codes de systèmes d'écriture tels que définis par la norme ISO 15924.` — Clean.

---

### schema/vocabularies/occupation.yaml

#### Top-level definition
- Issue: Stripped accents throughout (systemic authoring bug).
- Current: `Categories decrivant la profession d'une personne, basees sur la classification hierarchique complete ISCO-08 (grands groupes, sous-grands groupes, sous-groupes et groupes de base).`
- Proposed: `Catégories décrivant la profession d'une personne, basées sur la classification hiérarchique complète ISCO-08 (grands groupes, sous-grands groupes, sous-groupes et groupes de base).`
- Reason: Stripped accents (`Categories`, `decrivant`, `basees`, `hierarchique`, `complete`). Note: "sous-grands groupes" is the direct translation of "sub-major groups" and is acceptable, though ILO French documentation uses "sous-grands groupes" — no change needed on that term.

---

## Open questions (for Jeremi)

1. **event-certainty / event-severity: `unknown`.label gender** — `event-certainty` uses `Inconnue` for `unknown`, while `event-severity` also uses `Inconnue`. The `unknown` label in both files refers to an unresolved state. In certainty, "la certitude" is feminine and in severity "la gravité" is feminine, so `Inconnue` agrees correctly in both cases. I proposed changing event-certainty's `Inconnue` to `Inconnu` above under a different reasoning (abstract state) — on reflection, since the label refers back to the feminine noun of the vocabulary concept (certainty/severity), `Inconnue` is defensible in both. Please confirm the preferred form.

2. **hazard-type / biological.definition** — The French drops "disease outbreaks" as a separate item (`Épidémies` covers it), while English has "Disease outbreaks, epidemics, pest infestations, or biological contamination." The French omits biological contamination ("contamination biologique" is present) but the "disease outbreaks" is merged. Is this intentional simplification or a translation omission?

3. **identifier-type / birth_certificate.definition** — The canonical civil registration French term is `acte de naissance` (used correctly in the label). The definition uses `document officiel de naissance` — should this be updated to `acte de naissance délivré par le registre d'état civil` for consistency with civil-registration canonical terminology?

4. **status-in-employment / contributing_family_worker.label** — Current: `Travailleur familial collaborant`. ILO French official term for ICSE-18 is `aide familial` (singular, masculine, per ILO French statistical publications). Please confirm which form is preferred: the literal descriptive translation or the ILO canonical term.
