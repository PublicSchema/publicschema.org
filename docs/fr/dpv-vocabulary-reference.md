# Référence du vocabulaire DPV pour les programmes publics

Ce document est une liste de départ sélectionnée d'URI du W3C Data Privacy Vocabulary (DPV) pour les trois propriétés à valeur URI sur `ConsentRecord` et `PrivacyNotice` : `purposes` (finalités), `personal_data_categories` (catégories de données personnelles) et `processing_operations` (opérations de traitement).

Il s'agit d'un guide, pas d'un artefact du schéma. Les valeurs listées ici sont des classes DPV ; les adoptants les définissent comme des chaînes URI sur leurs dossiers. PublicSchema ne vérifie pas à l'exécution qu'un URI donné est une classe DPV valide.

**Les adoptants doivent réduire cette liste à la portée réelle de leur programme.** Un programme de traitement des paiements n'a pas besoin de finalités de recherche ou de marketing. Un registre national unique n'a pas besoin d'opérations de transfert international. Partez du sous-ensemble applicable et ajoutez uniquement ce qui est opérationnellement nécessaire.

Lorsque la taxonomie nationale est plus riche que ce que DPV propose, le mécanisme d'extension DPV permet de définir des sous-classes. Par exemple, si votre pays a une catégorie légale « vérification d'identité pour l'aide sociale » que DPV ne nomme pas directement, vous pouvez définir `https://votre.registre/purpose/VerificationIdentiteAideSociale` comme sous-classe de `dpv:IdentityVerification` et utiliser votre URI sur les dossiers.

---

## Finalités (sous-classes de `dpv:Purpose`)

Utilisez ces valeurs pour `ConsentRecord.purposes` et `PrivacyNotice.purposes`.

| URI | Description |
|---|---|
| `dpv:ServiceProvision` | Traitement nécessaire à la fourniture d'un service au concerné (finalité la plus large ; utiliser une sous-classe plus précise si possible). |
| `dpv:ServicePersonalisation` | Adaptation d'un service en fonction des caractéristiques ou de l'historique d'une personne. |
| `dpv:ServiceRegistration` | Inscription d'une personne pour accéder à un service ou en bénéficier. |
| `dpv:ServiceUsageAnalytics` | Analyse de l'utilisation des services pour améliorer leur prestation. |
| `dpv:IdentityVerification` | Vérification qu'une personne est bien celle qu'elle prétend être. |
| `dpv:FraudPreventionAndDetection` | Détection, prévention ou investigation de la fraude. |
| `dpv:LegalCompliance` | Conformité à une obligation légale. |
| `dpv:MaintainCreditCheckingDatabase` | Maintien de dossiers permettant de prendre des décisions d'éligibilité financière. |
| `dpv:CommunicationForCustomerCare` | Contact avec les personnes pour la gestion de cas ou le soutien. |
| `dpv:SocialSecurityBenefitAdministration` | Administration des prestations de sécurité sociale (inscription, paiement, recours). |
| `dpv:PublicBenefitAdministration` | Administration de tout programme d'aide ou de prestation publique. |
| `dpv:EligibilityDetermination` | Détermination de l'éligibilité d'une personne à une prestation ou un service. |
| `dpv:BenefitPaymentProcessing` | Traitement du paiement d'une prestation à un bénéficiaire éligible. |
| `dpv:ProgramMonitoring` | Suivi de l'atteinte des bénéficiaires cibles et des résultats d'un programme. |
| `dpv:MandatedDataSharing` | Partage de données exigé par la loi avec une autre autorité. |
| `dpv:ResearchAndDevelopment` | Recherche, y compris la recherche sur les politiques publiques, l'évaluation d'impact et la conception de programmes. |
| `dpv:Statistics` | Production de statistiques ; les données sont utilisées pour une analyse agrégée, pas pour des décisions individuelles. |
| `dpv:AcademicResearch` | Recherche menée au sein d'un établissement universitaire ou de recherche. |
| `dpv:HumanitarianAssistance` | Traitement dans le cadre d'une réponse humanitaire ou d'une assistance d'urgence. |
| `dpv:DisasterRecovery` | Traitement en appui à la reconstruction après une catastrophe naturelle ou une urgence. |
| `dpv:AuditAndAccountability` | Traitement à des fins d'audit, de contrôle ou de reddition de comptes. |

---

## Catégories de données personnelles (sous-classes de `dpv-pd:PersonalData`)

Utilisez ces valeurs pour `ConsentRecord.personal_data_categories` et `PrivacyNotice.data_categories`.

### Identifiants

| URI | Description |
|---|---|
| `dpv-pd:Name` | Nom identifiant une personne physique (prénom, nom de famille ou combiné). |
| `dpv-pd:Identifier` | Tout identifiant attribué à une personne (numéro de carte nationale, numéro de dossier, identifiant de registre). |
| `dpv-pd:NationalIdentificationNumber` | Numéro d'identité nationale (par ex. NIN, NIR, CNPJ). |
| `dpv-pd:DateOfBirth` | Date de naissance de la personne. |
| `dpv-pd:Age` | Âge de la personne, qu'il soit exact ou sous forme de tranche. |

### Données démographiques

| URI | Description |
|---|---|
| `dpv-pd:Gender` | Genre tel que déclaré par la personne elle-même. |
| `dpv-pd:Sex` | Sexe biologique de la personne. |
| `dpv-pd:HouseholdComposition` | Nombre et caractéristiques des personnes composant un ménage. |
| `dpv-pd:MaritalStatus` | Situation matrimoniale ou civile. |
| `dpv-pd:Nationality` | Nationalité ou citoyenneté. |
| `dpv-pd:Ethnicity` | Origine ethnique ou raciale. Il s'agit d'une catégorie spéciale au sens du RGPD art. 9. |
| `dpv-pd:Religion` | Conviction religieuse. Il s'agit d'une catégorie spéciale au sens du RGPD art. 9. |
| `dpv-pd:PoliticalOpinion` | Opinions ou affiliations politiques. Il s'agit d'une catégorie spéciale au sens du RGPD art. 9. |
| `dpv-pd:Disability` | Statut ou type de handicap. Il s'agit d'une catégorie spéciale (données de santé) au sens du RGPD art. 9. |

### Coordonnées

| URI | Description |
|---|---|
| `dpv-pd:PhoneNumber` | Numéro de téléphone fixe ou mobile. |
| `dpv-pd:EmailAddress` | Adresse électronique. |
| `dpv-pd:Address` | Adresse postale ou résidentielle. |
| `dpv-pd:Location` | Données de localisation, y compris coordonnées GPS et zone géographique. |

### Données financières

| URI | Description |
|---|---|
| `dpv-pd:Income` | Revenus, salaires ou autres ressources. |
| `dpv-pd:FinancialAccount` | Numéro de compte bancaire, compte mobile money ou identifiant financier similaire. |
| `dpv-pd:FinancialStatus` | Situation financière globale, y compris le niveau de pauvreté ou le statut socio-économique. |
| `dpv-pd:BankAccount` | Coordonnées bancaires spécifiquement. |
| `dpv-pd:AssetData` | Propriété de terres, bétail, biens immobiliers ou autres actifs. |

### Données biométriques (toutes constituent une catégorie spéciale au sens du RGPD art. 9)

| URI | Description |
|---|---|
| `dpv-pd:Biometric` | Toute donnée biométrique (catégorie la plus large ; utiliser une sous-classe plus précise si possible). |
| `dpv-pd:Fingerprint` | Données d'empreintes digitales ou palmaires. |
| `dpv-pd:FacialImage` | Photographie du visage ou gabarit de reconnaissance faciale. |
| `dpv-pd:IrisScan` | Données d'iris ou de reconnaissance irienne. |
| `dpv-pd:VoiceSignature` | Enregistrement vocal utilisé à des fins d'identification. |

### Données de santé (catégorie spéciale au sens du RGPD art. 9)

| URI | Description |
|---|---|
| `dpv-pd:HealthData` | Toute donnée relative à la santé physique ou mentale. À utiliser avec `special_category_basis`. |
| `dpv-pd:MedicalHistory` | Antécédents de diagnostics, traitements ou pathologies. |
| `dpv-pd:Disability` | Statut de handicap (voir aussi dans la section Données démographiques). |
| `dpv-pd:Nutrition` | État nutritionnel, y compris les mesures anthropométriques. |

### Données spécifiques aux programmes

| URI | Description |
|---|---|
| `dpv-pd:SocialBenefitData` | Données relatives à la perception ou à l'éligibilité à une prestation de protection sociale. |
| `dpv-pd:SocialMediaData` | Données issues de profils de réseaux sociaux (moins courant en protection sociale). |

---

## Opérations de traitement (sous-classes de `dpv:Processing`)

Utilisez ces valeurs pour `ConsentRecord.processing_operations` et `PrivacyNotice.processing_operations`.

| URI | Description |
|---|---|
| `dpv:Collect` | Collecte de données auprès du concerné ou d'un tiers. |
| `dpv:Record` | Création d'un enregistrement persistant des données. |
| `dpv:Store` | Conservation des données dans un système de stockage. |
| `dpv:Use` | Utilisation des données dans un traitement (sens large ; à combiner avec une finalité précise). |
| `dpv:Retrieve` | Récupération de données depuis un système de stockage ou un tiers. |
| `dpv:Organise` | Structuration ou ordonnancement des données (classement, tri, étiquetage). |
| `dpv:Analyse` | Analyse des données pour en tirer des conclusions ou des informations. |
| `dpv:Derive` | Production de nouvelles données à partir de données existantes (score, agrégation, inférence). |
| `dpv:Profile` | Constitution d'un profil d'une personne à partir de plusieurs points de données. |
| `dpv:Share` | Communication de données à un tiers dans le périmètre du responsable. |
| `dpv:Disclose` | Mise à disposition de données à un tiers hors du périmètre immédiat du responsable. |
| `dpv:Transfer` | Déplacement de données vers une autre juridiction ou un système externe. |
| `dpv:Transmit` | Envoi de données sur un réseau (sous-cas plus précis de Transfer ou Disclose). |
| `dpv:Disseminate` | Publication ou distribution large de données. |
| `dpv:Erase` | Suppression ou destruction de données. |
| `dpv:Anonymise` | Suppression ou transformation des identifiants de façon à ce que les données ne puissent plus être rattachées à une personne. |
| `dpv:Pseudonymise` | Remplacement des identifiants directs par un pseudonyme tout en conservant une clé de ré-identification. |
| `dpv:Align` | Combinaison ou rapprochement de données issues de plusieurs sources. |
| `dpv:Copy` | Duplication de données d'un système ou d'un support vers un autre. |

---

## Lien avec OpenSPP

Le module `spp_consent` d'OpenSPP intègre des données de référence (seed data) pour les finalités et les catégories de données personnelles dans ses fichiers de migration de base de données. En l'état des données OpenSPP extraites dans `external/openspp/`, aucune valeur d'énumération spécifique au consentement n'est disponible. Consultez directement la documentation OpenSPP sur https://docs.openspp.org/en/latest/ pour les valeurs actuelles lors d'une intégration avec des déploiements OpenSPP.

---

## À utiliser comme guide, pas comme schéma

Ces URI sont des points de départ. Ne copiez pas toute la liste dans vos dossiers. Ne définissez que les URI qui décrivent fidèlement le traitement de votre programme. Surestimer le périmètre du traitement dans un dossier de consentement est un problème de conformité, pas une marge de sécurité.

La hiérarchie DPV est bien plus large que cette liste. Cette liste couvre le périmètre pertinent pour les programmes de protection sociale, l'aide humanitaire et l'état civil. Pour d'autres domaines, parcourez le DPV complet sur https://w3id.org/dpv.
