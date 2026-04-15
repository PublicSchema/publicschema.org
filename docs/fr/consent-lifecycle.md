# Guide du cycle de vie du consentement

Ce guide traite des décisions opérationnelles pour les programmes qui adoptent `ConsentRecord` et `PrivacyNotice`. Il s'adresse aux responsables de mise en oeuvre et aux concepteurs de systèmes d'information, pas aux juristes. Il ne constitue pas un avis juridique.

---

## 1. Choisir une base légale : quand le consentement n'est pas la bonne réponse

`ConsentRecord` stocke la base légale du traitement des données personnelles. Le consentement (`legal_basis = consent`) n'est qu'une des six options possibles. La plupart des programmes de protection sociale choisissent le consentement par défaut et se retrouvent avec des dossiers qui ne résistent pas à un contrôle réglementaire ou à une réclamation d'un bénéficiaire.

Avant de définir `legal_basis = consent`, répondez honnêtement aux trois questions suivantes :

1. Le bénéficiaire peut-il réalistement refuser sans perdre l'accès au service ?
2. L'avis de confidentialité (privacy notice) indique-t-il explicitement que la participation est volontaire ?
3. Le retrait du consentement entraîne-t-il l'arrêt du service ?

Si les trois réponses sont oui, le consentement est le choix honnête. Si l'une des réponses est non, le traitement n'est pas véritablement volontaire et une autre base légale s'applique.

### Quelle base légale utiliser à la place

| Situation | Base légale honnête |
|---|---|
| L'inscription est une condition pour recevoir une prestation | `public_interest` (intérêt public, RGPD art. 6(1)(e)) |
| Le traitement est exigé par une loi, un règlement ou une décision de justice | `legal_obligation` (obligation légale, RGPD art. 6(1)(c)) |
| Le traitement est strictement nécessaire pour protéger la vie d'une personne | `vital_interest` (intérêt vital, RGPD art. 6(1)(d)) |
| Un contrat avec le bénéficiaire l'exige | `contract` (contrat, RGPD art. 6(1)(b)) |
| Le responsable du traitement a un intérêt légitime non contrebalancé par les droits de la personne concernée | `legitimate_interest` (intérêt légitime, RGPD art. 6(1)(f)) ; à utiliser avec précaution |

En pratique, la plupart des inscriptions dans les programmes de protection sociale reposent sur `public_interest` ou `legal_obligation`. Un ministère qui gère un filet de sécurité sociale légal n'obtient presque jamais un consentement véritablement facultatif au stade de l'inscription.

Les codes du vocabulaire `legal_basis` correspondent à `dpv-gdpr:A6-1-a` à `dpv-gdpr:A6-1-f`. Renseignez `legal_basis_reference` avec la référence au droit national applicable (par exemple, `"Loi kényane sur la protection des données 2019, art. 30(1)(b)"`).

### Catégories spéciales de données

Si l'une des valeurs de `personal_data_categories` est une sous-classe de `dpv:SpecialCategoryPersonalData` (données de santé, données biométriques, origine ethnique, conviction religieuse, etc.), vous devez également renseigner `special_category_basis`. La base légale de l'art. 6 et la base spéciale de l'art. 9 sont deux exigences distinctes ; les deux champs sont nécessaires.

---

## 2. Transitions d'état pour consent-status

Le vocabulaire `consent-status` définit neuf valeurs. Toutes les transitions ne sont pas valides.

```
requested (demandé)
  |-- (accord de la personne concernée) --> given (donné)
  |-- (refus de la personne concernée) --> refused (refusé) [terminal]
  |-- (expiration système) --> invalidated (invalidé) [terminal]

given (donné)
  |-- (renouvellement avant expiration) --> renewed (renouvelé)
  |-- (retrait à l'initiative de la personne concernée) --> withdrawn (retiré) [terminal]
  |-- (révocation à l'initiative du responsable) --> revoked (révoqué) [terminal]
  |-- (fin de la période de validité) --> expired (expiré) [terminal]

renewed (renouvelé)
  |-- (retrait à l'initiative de la personne concernée) --> withdrawn (retiré) [terminal]
  |-- (révocation à l'initiative du responsable) --> revoked (révoqué) [terminal]
  |-- (fin de la période de validité) --> expired (expiré) [terminal]

unknown (inconnu)
  (import hérité où l'état d'origine ne peut être déterminé ; à traiter comme non actif)
```

Les états terminaux (`refused`, `withdrawn`, `revoked`, `expired`, `invalidated`) ne doivent pas être remis à un état actif. Un nouveau `ConsentRecord` doit être créé à la place.

Lorsque l'état passe à `withdrawn`, renseignez `withdrawal_channel` et, si possible, `withdrawal_reason`. Cela satisfait l'exigence de justification du RGPD art. 7(3) : le responsable peut montrer non seulement que le retrait était possible, mais qu'il a eu lieu et par quel canal.

---

## 3. L'avis de confidentialité comme limite

La portée d'un `ConsentRecord` doit rester à l'intérieur de la portée déclarée du `PrivacyNotice` qu'il référence (via `notice_ref`). La portée comprend :

- Les `purposes` du dossier doivent être un sous-ensemble des `purposes` de l'avis.
- Les `personal_data_categories` du dossier doivent être un sous-ensemble des `data_categories` de l'avis.
- Les `recipients` et `allowed_recipient_categories` du dossier doivent figurer dans les `recipient_categories` ou `recipients_described` de l'avis.

Si le dossier doit dépasser la portée de l'avis, l'avis doit être mis à jour en premier, une nouvelle `notice_version` émise, et un nouveau recueil de consentement effectué auprès de la personne concernée. Il n'est pas possible d'élargir l'avis rétroactivement et de prétendre que le dossier antérieur couvre la nouvelle portée.

Le champ `notice_version` du `ConsentRecord` est un instantané de la version fixée au moment de l'accord. Même si l'avis est corrigé ultérieurement, le dossier continue de référencer la version qui a effectivement été présentée.

---

## 4. Déclencheurs de nouveau consentement

| Type de modification | Nouveau consentement requis ? | Action |
|---|---|---|
| Nouvelle finalité ajoutée à l'avis | Oui | Mettre à jour l'avis, incrémenter la version, recueillir un nouveau consentement |
| Nouvelle organisation destinataire ajoutée | Oui | Mettre à jour l'avis, incrémenter la version, recueillir un nouveau consentement |
| Nouvelle catégorie de données personnelles collectées | Oui | Mettre à jour l'avis, incrémenter la version, recueillir un nouveau consentement |
| Mise à jour d'une traduction ou correction d'une faute | Non | Incrémenter la version de l'avis ; les dossiers existants restent valides |
| Modification des coordonnées du DPO (délégué à la protection des données) | Non | Incrémenter la version de l'avis ; les dossiers existants restent valides |
| Mise à jour de la description de conservation (sans changement de la durée réelle) | Non | Incrémenter la version de l'avis ; les dossiers existants restent valides |
| Reclassification de la juridiction sans changement du cadre juridique réel | Non | Incrémenter la version de l'avis ; les dossiers existants restent valides |

Le critère est sémantique, pas textuel : si la personne concernée aurait le droit de s'opposer à la modification en vertu du droit applicable, un nouveau consentement est nécessaire.

Voir la section 11 sur le coût opérationnel des campagnes de nouveau consentement avant de planifier une modification qui déclenche ce processus.

---

## 5. Transitions à la majorité

Pour un mineur dont le consentement a été donné par un parent ou tuteur (`delegation_type ∈ {parent, legal-guardian}`), définissez `expiry_date` à la date à laquelle la personne concernée atteindra l'âge de la majorité dans la `jurisdiction` applicable.

Avant cette date, contactez la personne concernée, devenue adulte, présentez-lui l'avis et recueillez un nouveau dossier avec `delegation_type = self`. Le dossier parental expiré n'est pas valable pour la poursuite du traitement après la majorité.

Il s'agit d'une solution provisoire pour la version 1. L'ADR-017 introduira un champ formel `capacity_basis` pour les transitions liées à l'âge de la majorité et à la capacité juridique.

Conservez un enregistrement de la tentative de contact. Si la personne ne peut pas être jointe, le traitement doit cesser ou reposer sur une base légale ne nécessitant pas d'accord individuel renouvelé (`legal_obligation`, `public_interest`).

---

## 6. Consentement et éligibilité

Ce sont des préoccupations distinctes et des dossiers distincts.

Un `ConsentRecord` documente la base légale du traitement des données personnelles. Un `EligibilityDecision` documente si une personne remplit les conditions pour bénéficier d'un programme. Ces deux éléments sont indépendants :

- Une personne peut être éligible mais n'avoir pas encore consenti. L'inscription ne devrait pas être effectuée tant qu'un dossier valide n'existe pas.
- Une personne ayant consenti peut être évaluée et déclarée non éligible. Le `ConsentRecord` reste valide ; le traitement pour lequel le consentement a été donné a eu lieu légalement, même si le résultat est un refus.
- Une personne peut retirer son consentement après avoir été inscrite. Le retrait ne revient pas sur l'inscription ; il régit les traitements futurs. L'effacement est un processus distinct (voir l'ADR-010 à venir sur `DataSubjectRightsRequest`).

Ne confondez pas ces notions. Les systèmes qui lient directement l'état du consentement à l'état d'inscription créent des dossiers qu'aucun des deux concepts ne peut correctement représenter.

---

## 7. Performance et indexation

Pour tout système gérant plus de quelques milliers de dossiers, deux pratiques réduisent sensiblement le coût des requêtes :

**Indexer sur `(status, expiry_date)`.** Les balayages d'expiration (trouver tous les dossiers dont la `expiry_date` est dépassée et qui affichent encore `given`) font partie des traitements par lots les plus fréquents. Un index composite sur ces deux champs transforme ce balayage en un parcours de plage plutôt qu'en un scan complet de la table.

**Maintenir des caches récapitulatifs pour les agrégations courantes.** Des requêtes telles que « combien de dossiers de consentement actifs ce programme possède-t-il ? » ou « quel est le taux de couverture du consentement par communauté ? » sont fréquentes dans le suivi et les rapports. Les calculer à la demande sur l'ensemble des dossiers est coûteux. Une table récapitulative mise à jour par un traitement par lots (toutes les heures ou quotidiennement selon le volume) sert le reporting sans toucher au stockage opérationnel.

Le schéma ne dicte pas l'architecture de stockage, mais ces deux points reviennent systématiquement dans les déploiements de terrain.

---

## 8. Consentement verbal sans témoin

Lorsque `collection_medium = verbal` ou que `consent_expression` vaut `opt-in-witnessed` ou `opt-in-biometric`, au moins une entrée dans `witnessed_by` devrait être renseignée.

Il s'agit d'une règle que les adoptants doivent appliquer eux-mêmes. Le schéma ne la valide pas. La raison pour laquelle elle n'est pas appliquée au niveau du schéma est qu'une telle contrainte bloquerait des dossiers valides issus de systèmes qui ne peuvent pas toujours identifier un témoin lors de la numérisation (par exemple, des arriérés de saisie papier). Cependant, un champ `witnessed_by` absent sur un dossier verbal ou biométrique affaiblit considérablement la valeur probante du dossier sur le plan juridique.

Conseils pratiques :

- Formez les agents de terrain à noter le nom et le rôle du témoin au moment de la collecte, pas lors de la numérisation.
- Ajoutez une entrée `witnessed_by` même si le témoin est l'agent lui-même (c'est une preuve plus faible, mais préférable à aucune).
- Pour un consentement verbal par téléphone, enregistrez la référence de l'appel dans `evidence_ref` et l'agent du centre d'appel dans `witnessed_by`.

---

## 9. Consentement biométrique : deux axes orthogonaux

Les données biométriques apparaissent à deux endroits dans un `ConsentRecord`. Il s'agit de choses différentes qui ne doivent pas être confondues.

**Axe 1 : comment le consentement a été exprimé.** `consent_expression = opt-in-biometric` signifie que la personne concernée a utilisé un élément biométrique (généralement une empreinte digitale ou un scan de l'iris) comme acte de signature. Il s'agit du mode de recueil. Le dossier peut ou non impliquer le traitement de données biométriques en tant que données personnelles.

**Axe 2 : quelles données sont traitées.** Si `personal_data_categories` inclut un URI qui est une sous-classe de `dpv:BiometricData` (par exemple, `dpv-pd:Fingerprint`, `dpv-pd:IrisScan` ou `dpv-pd:FacialImage`), alors des données biométriques entrent dans le périmètre du traitement. Il s'agit des catégories de données. Le consentement peut avoir été exprimé biométriquement ou non.

Un dossier peut avoir l'un, l'autre, les deux, ou aucun :

| consent_expression | personal_data_categories inclut biométrique | Situation |
|---|---|---|
| `opt-in-biometric` | Non | Empreinte utilisée comme signature ; aucune donnée biométrique collectée |
| Pas biométrique | Oui | Image faciale collectée ; consentement signé sur papier |
| `opt-in-biometric` | Oui | Empreinte comme signature ET données d'empreinte collectées |
| Pas biométrique | Non | Aucune implication biométrique |

Lorsque des données biométriques sont traitées en tant que catégorie spéciale, assurez-vous que `special_category_basis` est également renseigné (voir section 1).

---

## 10. Immutabilité des champs de conditions

Les propriétés suivantes sont immuables une fois que le `status` a atteint `given`. Elles sont annotées `ps:immutableAfterStatus "given"` dans la sortie RDF du schéma :

`data_subject`, `controllers`, `recipients`, `recipient_role`, `allowed_recipient_categories`, `purposes`, `personal_data_categories`, `processing_operations`, `legal_basis`, `special_category_basis`, `notice_ref`, `notice_version`, `effective_date`, `jurisdiction`, `collection_medium`, `consent_expression`

Ce n'est pas une préférence d'interface ou un choix de conception arbitraire. C'est une exigence légale. Le RGPD art. 7(1) exige que les responsables du traitement soient en mesure de démontrer que le consentement a été donné. Si les conditions du consentement peuvent être modifiées après coup, le dossier ne peut plus servir de preuve. Le même principe s'applique en vertu de la loi kényane sur la protection des données art. 29(2), de la LGPD brésilienne art. 8(3) et des dispositions équivalentes dans d'autres juridictions.

Le schéma émet `ps:immutableAfterStatus "given"` comme annotation lisible par machine sur chacune de ces propriétés, ainsi qu'un `rdfs:comment` en langage naturel dans la sortie Turtle. Il n'émet pas actuellement de contrainte SHACL, car une forme SHACL basée uniquement sur un commentaire représenterait mal l'application effective des règles. Les adoptants doivent appliquer cette règle au niveau de leur application. Un futur ADR la promouvra en contrainte SHACL SPARQL.

Champs qui restent modifiables après `given` :

- `status` (doit être modifié pour enregistrer un retrait, une expiration, etc.)
- `withdrawal_channel`, `withdrawal_reason`, `refusal_reason` (renseignés au fil du cycle de vie)
- `evidence_ref` (additif uniquement : de nouvelles pièces jointes peuvent être ajoutées, pas supprimées)
- `verified_by`, `verified_date` (la vérification de la saisie peut intervenir après la numérisation)
- `collection_session_ref` (corrélation opérationnelle, pas une condition de l'accord)

---

## 11. Coût opérationnel des campagnes de nouveau consentement

Lorsqu'une modification substantielle déclenche un nouveau consentement (voir section 4), sachez qu'une campagne de nouveau consentement dans un programme de terrain est une opération de plusieurs mois, pas une transaction en base de données.

Ce que cela implique généralement :

- Mise à jour de l'avis et de toutes ses versions localisées
- Impression ou distribution des supports d'avis mis à jour
- Formation des agents communautaires et des agents de terrain sur la modification et ses raisons
- Revisites des communautés, parfois plusieurs fois pour atteindre les bénéficiaires absents ou mobiles
- Collecte des nouveaux consentements (papier ou électronique)
- Numérisation des formulaires papier et rapprochement avec les dossiers existants
- Gestion d'une période de réconciliation où certains dossiers sont mis à jour et d'autres pas encore

Des programmes ont connu des cycles de nouveau consentement de 6 à 12 mois lors de déploiements à grande échelle. Planifiez cela avant d'apporter une modification qui déclenche un nouveau consentement. Si la modification peut être formulée comme éditoriale (amélioration d'une traduction, mise à jour d'un contact) plutôt que substantielle, vérifiez qu'elle l'est vraiment avant de choisir la voie la plus simple.

Le coût opérationnel est l'une des raisons pour lesquelles l'arbre de décision de la section 1 est important : un programme qui a initialement revendiqué le consentement mais aurait été mieux servi par `public_interest` peut se retrouver face à une campagne de nouveau consentement pour corriger la base légale sur chaque dossier existant, alors que la mise à jour de la base légale dans un avis référençant `public_interest` ne nécessite aucun nouveau consentement.

---

## 12. Implémentation de référence

Le module `spp_consent` d'OpenSPP est une implémentation de qualité production du modèle de dossier de consentement, alignée sur le W3C DPV v2 et la norme ISO/IEC TS 27560:2023. Il inclut l'export JSON-LD et la gestion du cycle de vie des statuts par une machine à états.

Documentation : https://docs.openspp.org/en/latest/

Le module `spp_consent` ne couvre pas tous les champs du `ConsentRecord` de PublicSchema (par exemple, les champs de flux papier et la présentation multilingue des avis sont des extensions PublicSchema), mais il constitue la référence la plus proche pour la logique d'application des règles à l'exécution et les modèles de sérialisation.
