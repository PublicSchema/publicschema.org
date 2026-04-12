# Guide JSON-LD et attestations vérifiables

Ce guide explique comment utiliser PublicSchema avec les contextes JSON-LD et les attestations vérifiables SD-JWT. C'est l'une des nombreuses façons d'utiliser PublicSchema. Consultez [Cas d'utilisation](/docs/use-cases/) pour une vue d'ensemble plus large des modèles d'intégration, dont beaucoup ne nécessitent pas JSON-LD ni les VC.

## Ce qu'utilise cette voie d'intégration

Cette voie d'intégration s'appuie sur les artefacts PublicSchema suivants :

- **Contexte JSON-LD** : fait correspondre les noms de propriétés à des URI stables avec des informations de type
- **Schémas JSON** : schémas de validation par concept et par type d'attestation
- **Types d'attestation** : schémas SD-JWT VC pour IdentityCredential, EnrollmentCredential, PaymentCredential

Pour la liste complète des artefacts disponibles, consultez [Artefacts disponibles](#artefacts-disponibles) ci-dessous.

## Démarrage rapide

### 1. Référencer le contexte

Ajoutez le contexte PublicSchema à vos documents JSON-LD :

```json
{
  "@context": "https://publicschema.org/ctx/draft.jsonld",
  "type": "Person",
  "given_name": "Amina",
  "family_name": "Diallo",
  "date_of_birth": "1988-03-15"
}
```

Cela rend vos données lisibles par machine. Tout système qui comprend le contexte PublicSchema peut les traiter.

### 2. Valider vos données

Utilisez les schémas JSON générés pour valider les données au moment de l'exécution :

```python
import json
import jsonschema

# Load the schema for the concept you're using
schema = json.load(open("person.schema.json"))

# Validate your data
data = {"given_name": "Amina", "date_of_birth": "1988-03-15", "gender": "female"}
jsonschema.validate(data, schema)
```

Les schémas sont disponibles à l'adresse `https://publicschema.org/schemas/{Concept}.schema.json`.

### 3. Utiliser les codes de vocabulaire canoniques

Lorsque votre système stocke le statut d'inscription, le statut de paiement, le genre, etc., convertissez vos codes internes vers les codes canoniques PublicSchema :

| Votre système | PublicSchema | Vocabulaire |
|---|---|---|
| `ACTV` | `active` | enrollment-status |
| `M` | `male` | gender-type |
| `BANK` | `bank_transfer` | delivery-channel |

Le fichier `vocabulary.json` contient la liste complète des vocabulaires avec tous les codes, définitions et correspondances de systèmes.

### 4. Émettre des attestations vérifiables

Utilisez les types d'attestation PublicSchema pour émettre des SD-JWT VC :

```json
{
  "iss": "did:web:your-system.example.gov",
  "sub": "did:web:your-system.example.gov:persons:4421",
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
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "is_enrolled": true,
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

### 5. Implémenter la divulgation sélective

Consultez les définitions des types d'attestation dans le guide [Divulgation sélective](/docs/selective-disclosure/) pour déterminer quelles affirmations sont à divulguer de façon sélective dans les SD-JWT VC. Chaque type d'attestation spécifie quelles affirmations sont toujours divulguées et lesquelles sont enveloppées dans `_sd` (révélées seulement lorsque nécessaire).

## Correspondance de systèmes

Si votre système utilise des noms de champs ou des codes différents, utilisez les `system_mappings` dans les fichiers YAML de vocabulaire pour traduire les valeurs. Chaque entrée de système liste ses valeurs avec le code d'origine, le libellé lisible par l'humain et la valeur canonique vers laquelle elle correspond. Par exemple, le vocabulaire gender-type inclut :

```yaml
system_mappings:
  openimis:
    vocabulary_name: Gender
    values:
      - code: "M"
        label: Male
        maps_to: male
      - code: "F"
        label: Female
        maps_to: female
      - code: "O"
        label: Other
        maps_to: other
    unmapped_canonical: [not_stated]
  dci:
    vocabulary_name: GenderCode
    values:
      - code: "1"
        label: Male
        maps_to: male
      - code: "2"
        label: Female
        maps_to: female
      - code: "0"
        label: Not stated
        maps_to: not_stated
```

La liste `unmapped_canonical` montre quelles valeurs PublicSchema n'ont pas d'équivalent dans ce système, rendant les lacunes explicites dans les deux sens. Consultez [Exemple de correspondance](/docs/mapping-example/) pour une présentation complète.

## Artefacts disponibles

| Artefact | URL | Description |
|---|---|---|
| Contexte JSON-LD | [`/ctx/draft.jsonld`](/ctx/draft.jsonld) | Fait correspondre les noms de propriétés à des URI |
| Vocabulaire complet (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) | Vocabulaire complet en tant que @graph JSON-LD unique |
| Vocabulaire complet (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) | Vocabulaire complet en RDF/Turtle |
| Formes SHACL | [`/v/draft/publicschema.shacl.ttl`](/v/draft/publicschema.shacl.ttl) | Formes de validation pour tous les concepts |
| Vocabulaire JSON | [`/vocabulary.json`](/vocabulary.json) | Vocabulaire complet avec tous les concepts, propriétés, vocabulaires |
| Schémas de concepts | `/schemas/{Concept}.schema.json` | Schéma JSON par concept |
| Schémas d'attestations | `/schemas/credentials/{Type}.schema.json` | Schéma JSON SD-JWT VC par type d'attestation |

## Interopérabilité avec schema.org

PublicSchema déclare des équivalences avec schema.org pour les propriétés qui se chevauchent. Le contexte JSON-LD inclut des alias en camelCase :

- `given_name` et `givenName` résolvent tous les deux vers `https://publicschema.org/given_name`
- `date_of_birth` et `birthDate` résolvent tous les deux vers `https://publicschema.org/date_of_birth`
- `start_date` et `startDate` résolvent tous les deux vers `https://publicschema.org/start_date`

Utilisez la convention de nommage que votre système préfère. Les deux sont valides dans le contexte.

## Comportement de repli `@vocab`

Le contexte PublicSchema déclare `"@vocab": "https://publicschema.org/"`. Cela signifie que toute clé JSON qui n'est pas explicitement définie dans le contexte s'étendra silencieusement vers `https://publicschema.org/{clé}`. Par exemple, une faute de frappe comme `"givn_name"` s'étendrait vers `https://publicschema.org/givn_name` au lieu de déclencher une erreur.

Les processeurs JSON-LD ne signaleront pas cela. Pour détecter les fautes de frappe et les propriétés non déclarées, validez vos données par rapport au schéma JSON du concept que vous utilisez. Le schéma JSON n'autorise que les propriétés déclarées, donc `"givn_name"` ne passerait pas la validation.

## Correspondance schema.org `alternateName`

La propriété PublicSchema `preferred_name` est alignée avec `alternateName` de schema.org en tant que `broadMatch`, et non `exactMatch`. L'`alternateName` de schema.org couvre tout nom alternatif (surnoms, anciens noms, abréviations), tandis que `preferred_name` est spécifiquement le nom par lequel la personne préfère être appelée. Si votre système utilise `alternateName` de schema.org, sachez qu'il est sémantiquement plus large.

## Étendre PublicSchema

Consultez le [Mécanisme d'extension](/docs/extension-mechanism/) pour savoir comment ajouter des propriétés, des valeurs de vocabulaire et des concepts personnalisés en utilisant votre propre espace de noms aux côtés des termes PublicSchema.

## Prochaines étapes

- Pour une approche plus légère qui ne nécessite pas JSON-LD, consultez le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/).
- Pour effectuer la correspondance de champs entre des systèmes existants, consultez le [Guide d'interopérabilité et de correspondance](/docs/interoperability-guide/).
- Pour concevoir un nouveau système compatible, consultez le [Guide de conception du modèle de données](/docs/data-model-guide/).
- Pour des scénarios concrets montrant comment PublicSchema est utilisé, consultez les [Cas d'utilisation](/docs/use-cases/).
