# Conception de la divulgation sélective pour les attestations PublicSchema

## Vue d'ensemble

Les attestations PublicSchema sont conçues pour être utilisées avec SD-JWT VC (attestations vérifiables à divulgation sélective JWT), permettant aux détenteurs de ne révéler que les affirmations nécessaires à une interaction spécifique.

## Approche de classification des données

PublicSchema n'attribue pas de classification de données fixe aux propriétés individuelles. Le fait qu'une propriété constitue une donnée personnelle dépend de l'enregistrement dans lequel elle apparaît, pas de la propriété elle-même. Par exemple, `date_of_birth` dans un enregistrement de Personne est une donnée personnelle ; le même champ dans un tableau statistique agrégé ne l'est pas.

En revanche, le comportement de divulgation est défini au **niveau de l'attestation**. Chaque type d'attestation ci-dessous spécifie quelles affirmations sont toujours divulguées et lesquelles sont sélectivement divulgables.

Pour les annotations de sensibilité au niveau des propriétés, consultez [Conception du schéma : Annotations de sensibilité](../schema-design/#7-sensitivity-annotations).

## Valeurs de vocabulaire dans les attestations

Les valeurs de vocabulaire n'ont pas toutes leur place dans les attestations.

**Des faits stables, pas des états transitoires.** Une attestation vérifiable devrait attester des faits qui restent significatifs dans le temps ("cette personne est éligible"), pas des états de processus qui changent en quelques heures ("cette demande est en cours d'examen").

**Pas de valeurs en brouillon dans les attestations de production.** La signification d'une valeur en brouillon peut changer. Les émetteurs ne devraient utiliser que des valeurs ayant atteint la maturité usage expérimental ou normatif.

**Le type d'identifiant seul est insuffisant.** `identifier_type: national_id` est sans signification sans la juridiction émettrice et le schéma d'identifiant. Les vocabulaires utilisés dans les attestations doivent documenter quel contexte supplémentaire est nécessaire.

## Structure des attestations pour SD-JWT VC

![Matrice de divulgation : quelles affirmations sont toujours divulguées par rapport à sélectivement divulgables par type d'attestation](/images/credential-disclosure.svg)

### IdentityCredential

Toujours divulgué :
- `type` (Person)

Sélectivement divulgable :
- `given_name`, `family_name`, `name`
- `date_of_birth`
- `gender`, `sex`
- `nationality`, `marital_status`, `education_level`
- `phone_number`
- `identifiers` (chaque identifiant peut être divulgué indépendamment)

**Cas d'utilisation** : Vérification d'âge sans révéler l'identité complète. Un vérificateur doit confirmer que le détenteur a plus de 18 ans. Le détenteur divulgue uniquement `date_of_birth`, gardant `given_name`, `phone_number` et autres informations personnellement identifiables cachées.

### EnrollmentCredential

Toujours divulgué :
- `type` (Person + Enrollment)
- `enrollment_status`
- `is_enrolled`
- `enrollment_date`, `start_date`

Sélectivement divulgable :
- `program_ref`
- Affirmations d'identité de la Personne (given_name, family_name, date_of_birth)
- Référence `beneficiary`

**Cas d'utilisation** : Preuve d'inscription active pour l'accès aux services. Un vérificateur dans une clinique de santé doit confirmer que le détenteur est inscrit à un programme. Le détenteur divulgue enrollment_status (active) et is_enrolled (true), gardant l'identité du programme et les informations personnelles cachées.

### PaymentCredential

Toujours divulgué :
- `type` (Person + PaymentEvent)
- `payment_status`
- `payment_date`

Sélectivement divulgable :
- `entitlement_ref`
- `enrollment_ref`
- `payment_amount`, `payment_currency`
- `delivery_channel`
- `transaction_reference`
- `failure_reason`
- Affirmations d'identité de la Personne

**Cas d'utilisation** : Preuve de réception de paiement. Un auditeur doit vérifier que les paiements ont été effectués. Le détenteur divulgue payment_amount, payment_date et transaction_reference, mais pas son identité personnelle. Pour les paiements échoués, failure_reason peut être divulgué pour soutenir la résolution des litiges.

### VoucherCredential

Toujours divulgué :
- `type` (Voucher)
- `voucher_status`
- `serial_number`
- `expiry_date`

Sélectivement divulgable :
- `entitlement_ref`
- `issued_to`
- `redeemable_by`
- `amount`, `currency`
- `voucher_format`
- `items` (chaque article de livraison peut être divulgué indépendamment)
- `issue_date`
- `redemption_date`, `redeemed_by`, `redemption_agent`

**Cas d'utilisation** : Remboursement de coupon chez un vendeur. Le détenteur présente l'attestation de coupon. Le vendeur doit confirmer que le coupon est valide (statut), l'identifier (numéro de série) et vérifier qu'il n'a pas expiré (date d'expiration). Le détenteur peut divulguer sélectivement la valeur nominale ou le panier de produits (items) tout en gardant son identité cachée. Les champs post-remboursement (redemption_date, redeemed_by) permettent l'audit sans nécessiter une nouvelle présentation des affirmations d'identité.

### EntitlementCredential

Toujours divulgué :
- `type` (Entitlement)
- `entitlement_status`
- `coverage_period_start`, `coverage_period_end`

Sélectivement divulgable :
- `enrollment_ref`
- `schedule_ref`
- `benefit_modality`
- `benefit_description`
- `amount`, `currency`
- `document_expiry_date`
- Affirmations d'identité de la Personne (via la chaîne d'inscription)

**Cas d'utilisation** : Preuve du droit à une prestation. Un bénéficiaire doit démontrer qu'il a droit à une prestation pour une période spécifique (par exemple, pour accéder à un service complémentaire). Le détenteur divulgue entitlement_status (approved) et la période de couverture, gardant les détails du programme et l'identité cachés. Note : les droits par cycle sont de courte durée, donc la rotation des attestations est fréquente ; `document_expiry_date` contrôle la validité de la VC indépendamment de la période de couverture.

## Structure de la charge utile SD-JWT VC

Une SD-JWT VC sépare les affirmations toujours divulguées des affirmations sélectivement divulgables en utilisant le mécanisme `_sd`. Voici comment un EnrollmentCredential est structuré :

```json
{
  "iss": "did:web:registry.example.gov.sn",
  "sub": "did:web:registry.example.gov.sn:persons:4421",
  "iat": 1706745600,
  "nbf": 1706745600,
  "exp": 1738435200,
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "_sd_alg": "sha-256",
  "cnf": {
    "jwk": { "kty": "EC", "crv": "P-256", "x": "...", "y": "..." }
  },

  "credentialSubject": {
    "type": "Person",
    "_sd": [
      "...hash(given_name)...",
      "...hash(family_name)...",
      "...hash(date_of_birth)...",
      "...hash(gender)..."
    ],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "start_date": "2025-02-01",
      "_sd": [
        "...hash(program_ref)...",
        "...hash(beneficiary)..."
      ]
    }
  }
}
```

Note : les schémas d'attestation PublicSchema utilisent exclusivement le format SD-JWT VC. Les charges utiles SD-JWT VC utilisent `vct` (type d'attestation vérifiable) au lieu du `@context` et des tableaux `type` du W3C VCDM. L'affirmation `cnf` lie l'attestation à la clé du détenteur pour la preuve de liaison de clé. Les schémas JSON générés dans `dist/schemas/credentials/` valident les charges utiles SD-JWT VC, pas les enveloppes W3C VCDM.

Le tableau `_sd` contient des hachages des affirmations divulgables. Les valeurs réelles sont fournies séparément sous forme de divulgations que le détenteur peut choisir d'inclure ou d'omettre lors de la présentation de l'attestation.

## Guide de traitement traditionnel des données

Les exigences de traitement des données dépendent du contexte de l'attestation ou du jeu de données, pas des définitions individuelles de propriétés. Les implémenteurs doivent évaluer chaque déploiement et appliquer des protections selon que les données, dans ce contexte, identifient ou concernent une personne physique.

Guide général :
- **Les métadonnées structurelles** (paramètres de programme, statuts, dates) ne nécessitent généralement aucun traitement spécial au-delà de la protection normale des données.
- **Les données liées à une personne** (affirmations d'identité, enregistrements spécifiques à une personne) nécessitent des protections standard : contrôle d'accès, chiffrement au repos, périodes de rétention définies.
- **Les données sensibles** (propriétés qui révèlent des circonstances comme l'état de santé, la pauvreté ou le statut de victime dans la plupart des contextes) nécessitent une justification pour être collectées ou divulguées. Consultez l'annotation `sensitivity` dans [Conception du schéma](../schema-design/#7-sensitivity-annotations).
- **Les données restreintes** (scores d'évaluation, indices de vulnérabilité) nécessitent des protections renforcées : journalisation des accès, limitation des finalités, analyse d'impact sur la protection des données.

## Guide d'implémentation

1. **Les émetteurs** doivent consulter les définitions de types d'attestation ci-dessus lors de la construction de SD-JWT VC. Les affirmations listées comme "toujours divulguées" apparaissent en clair ; les affirmations "sélectivement divulgables" vont dans `_sd`. Pour les propriétés non couvertes par un type d'attestation défini, l'émetteur détermine le comportement de divulgation en fonction du contexte de l'attestation.

2. **Les détenteurs** (applications de portefeuille) doivent présenter une interface de sélection de divulgation distinguant les affirmations toujours divulguées des affirmations sélectivement divulgables. Les affirmations intrinsèquement sensibles (scores d'évaluation, indices de vulnérabilité) doivent nécessiter une confirmation explicite. En cas de doute, optez par défaut pour la divulgation sélective afin de favoriser la protection de la vie privée.

3. **Les vérificateurs** ne doivent demander que les affirmations dont ils ont besoin. Une demande d'affirmations intrinsèquement sensibles doit inclure une justification (par exemple, une référence à l'autorité d'audit).

4. **Le pipeline de construction** produit les métadonnées de propriétés dans `vocabulary.json`. Les implémentations de portefeuille et de vérificateur doivent utiliser les définitions de types d'attestation dans ce document pour configurer les politiques de divulgation.
