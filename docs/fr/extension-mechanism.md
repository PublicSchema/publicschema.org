# Étendre PublicSchema

## Principes

PublicSchema est descriptif, pas prescriptif. Les systèmes adoptent les concepts, propriétés et vocabulaires qui leur sont applicables. Lorsqu'un système a besoin de quelque chose que PublicSchema ne fournit pas, il l'étend en utilisant son propre espace de noms.

JSON-LD rend cela simple : tout terme absent du contexte PublicSchema peut être défini dans un contexte supplémentaire.

## Comment étendre

### Ajouter des propriétés personnalisées à un concept PublicSchema

Utilisez une seconde entrée `@context` avec votre propre espace de noms :

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "beneficiary_category": "myorg:beneficiary_category",
      "proxy_score_v2": {
        "@id": "myorg:proxy_score_v2",
        "@type": "xsd:decimal"
      }
    }
  ],
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "beneficiary_category": "ultra_poor",
  "proxy_score_v2": 23.7
}
```

Les termes PublicSchema (`given_name`, `family_name`) résolvent vers des URI PublicSchema. Vos termes personnalisés (`beneficiary_category`, `proxy_score_v2`) résolvent vers votre espace de noms. Les deux coexistent proprement.

### Ajouter des valeurs de vocabulaire personnalisées

Si un vocabulaire PublicSchema ne couvre pas les codes de votre système, étendez-le :

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/"
    }
  ],
  "type": "Enrollment",
  "beneficiary": "...",
  "program_ref": "...",
  "enrollment_status": "myorg:waitlisted"
}
```

Le vérificateur voit que `enrollment_status` a une valeur de votre espace de noms, pas de l'ensemble canonique PublicSchema. Il peut choisir de l'accepter, de l'associer à une valeur canonique ou de la signaler pour révision.

### Ajouter des concepts entièrement nouveaux

Définissez votre concept dans votre propre espace de noms :

```json
{
  "@context": [
    "https://publicschema.org/ctx/draft.jsonld",
    {
      "myorg": "https://data.myorg.gov/ns/",
      "CaseManagementRecord": "myorg:CaseManagementRecord",
      "case_worker": {"@id": "myorg:case_worker", "@type": "@id"},
      "case_notes": "myorg:case_notes"
    }
  ],
  "type": "CaseManagementRecord",
  "beneficiary": "did:web:example.gov/persons/123",
  "case_worker": "did:web:example.gov/staff/456",
  "case_notes": "Follow-up visit scheduled for 2025-04-15"
}
```

Notez que `beneficiary` résout toujours vers la définition PublicSchema, même s'il est utilisé sur un concept personnalisé. Réutilisez les termes PublicSchema là où ils s'appliquent.

## Règles pratiques

1. **Réutiliser avant d'inventer.** Vérifiez la liste de propriétés de PublicSchema avant de définir une propriété personnalisée. Si une propriété existe avec la bonne sémantique, utilisez-la.

2. **Placez vos extensions dans un espace de noms.** Ne définissez jamais un terme nu qui pourrait entrer en collision avec un futur ajout PublicSchema. Utilisez toujours un préfixe d'espace de noms (`myorg:custom_field`).

3. **Documentez vos extensions.** Publiez votre contexte étendu à une URL stable afin que les autres systèmes puissent comprendre vos données.

4. **Proposez en amont.** Si votre extension s'avère utile dans plusieurs systèmes, proposez son inclusion dans PublicSchema. Le vocabulaire grandit grâce à des usages réels, pas par conception de comité.

## Pour les émetteurs d'attestations

Lors de l'émission d'une attestation vérifiable qui utilise des extensions :

- Listez l'URL de votre contexte après le contexte PublicSchema dans le tableau `@context`
- Utilisez le type d'attestation PublicSchema (par exemple, `EnrollmentCredential`) plus votre propre type si nécessaire
- Les propriétés étendues suivent les mêmes directives de sensibilité : annotez-les comme `standard`, `sensitive` ou `restricted` (consultez [Conception du schéma : Annotations de sensibilité](../schema-design/#7-sensitivity-annotations))

Les vérificateurs qui comprennent votre contexte traiteront les extensions. Ceux qui ne le comprennent pas comprendront quand même tous les termes PublicSchema.
