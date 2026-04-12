# Modèles d'intégration

PublicSchema définit ce que les données signifient. Il ne définit pas comment les données se déplacent. Les mêmes concepts, propriétés et codes de vocabulaire fonctionnent sur n'importe quel transport : API REST, bus d'événements, attestations vérifiables, échanges de fichiers et pipelines d'analyse.

## La couche sémantique

![PublicSchema se situe entre votre modèle interne et tout transport](/images/integration-layer.svg)

Votre système aligne ses champs et codes sur PublicSchema une seule fois. À partir de là, la même représentation canonique circule sur n'importe quel canal.

Les exemples ci-dessous utilisent le même enregistrement d'inscription dans chaque modèle.

## API REST

Exposez les noms de propriétés et les codes de vocabulaire PublicSchema dans la surface de votre API. Les systèmes clients obtiennent un contrat prévisible sans connaître votre schéma interne.

```json
GET /api/enrollments/4421

{
  "type": "Enrollment",
  "given_name": "Amina",
  "family_name": "Diallo",
  "enrollment_status": "active",
  "enrollment_date": "2025-01-15",
  "program_ref": "cash-transfer-2025"
}
```

Validez les charges utiles des requêtes et des réponses avec les schémas JSON PublicSchema au point d'entrée de l'API.

## Systèmes orientés événements

Publiez des événements de domaine avec des charges utiles conformes à la structure PublicSchema. Les abonnés, quelle que soit leur plateforme, peuvent les traiter sans table de correspondance bilatérale.

```json
{
  "event": "enrollment.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "type": "Enrollment",
    "given_name": "Amina",
    "family_name": "Diallo",
    "enrollment_status": "active",
    "enrollment_date": "2025-01-15",
    "program_ref": "cash-transfer-2025"
  }
}
```

L'enveloppe de l'événement (type, horodatage, métadonnées de routage) reste à votre discrétion. La charge utile interne utilise PublicSchema.

## Attestations vérifiables

Émettez des SD-JWT VC en utilisant les types d'attestation PublicSchema. Le détenteur contrôle quelles affirmations divulguer à chaque présentation.

```json
{
  "vct": "https://publicschema.org/schemas/credentials/EnrollmentCredential",
  "credentialSubject": {
    "type": "Person",
    "_sd": ["...hash(given_name)...", "...hash(family_name)..."],
    "enrollment": {
      "type": "Enrollment",
      "enrollment_status": "active",
      "enrollment_date": "2025-01-15",
      "_sd": ["...hash(program_ref)..."]
    }
  }
}
```

Les mêmes propriétés apparaissent à la fois dans la réponse de l'API et dans l'attestation. La différence réside dans le modèle de confiance (signatures cryptographiques, divulgation sélective), non dans le vocabulaire.

Consultez [Divulgation sélective](/docs/selective-disclosure/) pour les définitions des types d'attestation et les règles de divulgation.

## Échange par lot et par fichier

Exportez des données sous forme de fichiers CSV ou JSON en utilisant les noms de propriétés PublicSchema comme en-têtes de colonnes. Tout système disposant d'une correspondance PublicSchema peut importer le fichier sans analyse personnalisée.

```csv
given_name,family_name,enrollment_status,enrollment_date,program_ref
Amina,Diallo,active,2025-01-15,cash-transfer-2025
```

Pas d'API, pas d'infrastructure. Une table de correspondance et un fichier CSV aux colonnes bien nommées.

## Entrepôt de données et analyse

Utilisez les codes de vocabulaire PublicSchema comme valeurs de dimension canoniques. Les requêtes inter-programmes fonctionnent parce que `active` signifie la même chose dans chaque table source.

```sql
SELECT program_ref, enrollment_status, COUNT(*)
FROM enrollment
WHERE enrollment_status = 'active'
GROUP BY program_ref, enrollment_status
```

Chaque source effectue la correspondance de ses codes vers les codes PublicSchema au moment du chargement. L'entrepôt parle un seul vocabulaire.

## Les mêmes données, n'importe quel transport

| Couche | Ce que fournit PublicSchema |
|---|---|
| Concepts | Définitions d'entités partagées (Personne, Inscription) |
| Propriétés | Noms de champs canoniques (given_name, enrollment_status) |
| Vocabulaires | Codes de valeurs canoniques (active, suspended, completed) |
| Schémas JSON | Validation des charges utiles pour les API, événements et attestations |
| Contexte JSON-LD | Résolution d'URI lisible par machine pour les données liées et les VC |

## Quel guide lire ensuite

- Pour aligner les codes de vocabulaire sans modifier votre modèle de données : [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/)
- Pour effectuer la correspondance de champs entre des systèmes existants : [Guide d'interopérabilité et de correspondance](/docs/interoperability-guide/)
- Pour concevoir un nouveau système compatible : [Guide de conception du modèle de données](/docs/data-model-guide/)
- Pour utiliser les contextes JSON-LD et émettre des attestations vérifiables : [Guide JSON-LD et VC](/docs/jsonld-vc-guide/)
- Pour des scénarios concrets : [Cas d'utilisation](/docs/use-cases/)
