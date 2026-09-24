# Rôles des installations

Utilisez `AssetPartyRole` pour une assertion, nécessaire indépendamment, indiquant qui possède, exploite
ou entretient des locaux physiques. Gardez l'identité de l'installation distincte de chaque
acteur et de son prestataire institutionnel. Un campus scolaire peut changer d'exploitant
sans devenir un autre campus ; il en va de même pour des locaux agricoles et un
patrimoine immobilier hospitalier.

Il s'agit d'un usage intersectoriel de la relation sur les biens physiques.
`School`, `HealthFacility` et `AgriculturalFacility` conservent leurs sens
distincts. Une `Farm` est une unité de production économique, et un `ProviderSite` peut être
virtuel. Aucun des deux ne devient un bien physique du seul fait qu'il a un exploitant ou
une adresse.

## Énoncer la responsabilité

L'exemple utilise le référentiel PublicSchema
`https://publicschema.org/vocab/asset-role-type` pour `asset_role_type`. Ce référentiel
définit aussi `keeper` pour un détenteur enregistré.

| Code | Signification | N'établit pas |
| --- | --- | --- |
| `owner` | L'acteur détient la propriété du bien physique identifié. | Un titre foncier, la propriété du prestataire institutionnel ou l'exploitation de l'installation. |
| `operator` | L'acteur exploite les locaux identifiés pour leur finalité opérationnelle. | La propriété, l'entretien des locaux, la gouvernance de l'école ou la responsabilité d'exploitant agricole. |
| `upkeep` | L'acteur est responsable de la mise à disposition et de l'entretien des locaux. | L'identité du prestataire de services ou du propriétaire. |

Utilisez une assertion distincte pour chaque responsabilité, même lorsqu'un acteur en a plusieurs.
Le champ reste ouvert : une source peut conserver son propre référentiel à la place, à condition que ce
référentiel publie ses significations et que son URI accompagne le code. Un mot non qualifié tel que `manager` ne résout pas ces
distinctions.

`asset_actor` identifie une personne, une organisation ou un groupe, y compris des
sous-types institutionnels appropriés. Les installations agricoles enregistrent aussi leur exploitant
sous forme d'AssetPartyRole ; ainsi, une pépinière exploitée conjointement peut avoir un
AssetPartyRole daté dont l'acteur est un InformalGroup. Ne requalifiez pas le groupe en
Organization. Un agent logiciel n'est pas un acteur du bien.

## Garder les adresses distinctes

`AssetAddressAssignment` associe un bien physique à une Address pendant une
période. Il utilise `subject_uri`, `assigned_address`, `address_purpose`, `start_date`
et `end_date`. L'adresse, la géométrie, la Location géographique nommée et l'installation
physique restent des sujets identifiés séparément.

L'exemple utilise `physical` et `postal` du référentiel PublicSchema
`https://publicschema.org/vocab/address-purpose`. Un changement d'adresse postale n'affirme
pas que l'installation a déménagé. Une position pour l'adresse relève de `location` de
l'Address ; la forme d'un bâtiment relève de sa `spatial_geometry`,
avec un encodage et un système de référence de coordonnées explicites. L'école de l'exemple
conserve son adresse physique tandis que sa boîte postale change un mois après le changement
de son exploitant.

La conversion des enregistrements sources d'adresses d'installations nécessite une finalité
d'adresse explicitement indiquée pour chaque attribution. Le [guide de conversion des dates de relation](/docs/relationship-date-migration/)
décrit la correspondance des champs et la conversion des dates. Il ne déduit pas la finalité physique
ou postale du texte de l'adresse.

## Lire les parcours synthétiques

`examples/facility-roles/records.json` contient trois historiques de patrimoine immobilier :

| Parcours | Changement | Assertions préservées indépendamment |
| --- | --- | --- |
| Campus scolaire Riverside | Un EducationProvider en remplace un autre comme exploitant des locaux le 1er juillet 2026. Son adresse postale change le 1er août. | Le campus, le propriétaire public, l'organisation chargée de l'entretien et l'adresse physique conservent leurs identités. Un ProviderSite distinct relie la prestation éducative au campus ; un autre ProviderSite est entièrement virtuel. |
| Locaux de séchage et de stockage de céréales | Une Person en remplace une autre comme exploitant de l'entrepôt le 1er mars 2026. L'adresse postale change le 1er avril. | Les locaux conservent leur identité. Une ProducerOrganization a des assertions de propriétaire et d'entretien identifiées séparément. La Farm et la responsabilité de son exploitant agricole restent distinctes. |
| Locaux de l'hôpital Est | L'organisation qui entretient le patrimoine immobilier change le 1er septembre 2026. | La HealthFacility physique, l'exploitant hospitalier institutionnel et le propriétaire public du patrimoine immobilier restent distincts et inchangés. |

Deux enregistrements ServiceCapacityObservation décrivent également 160 places d'apprentissage dotées
en personnel à l'école et 42 lits dotés en personnel à l'hôpital, chacun à un moment d'observation
explicite. Tous deux conservent leur référentiel de mesure local et une QuantityValue avec l'unité UCUM
`1`. Les observations font référence aux installations physiques identifiées séparément,
et non à leurs organisations prestataires. Ces décomptes datés n'établissent ni disponibilité
actuelle, ni accréditation, ni correspondance avec une ressource FHIR.

L'exemple hospitalier répond à une question intersectorielle de patrimoine immobilier. `health/HealthFacility`
a une correspondance proche avec Location de FHIR R5, et l'échange médical devrait conserver les
ressources FHIR natives choisies et leurs identités sources.
`Location.managingOrganization` de FHIR R5 identifie l'organisation responsable
de la mise à disposition et de l'entretien des locaux. C'est une référence unique et optionnelle, sans
période de responsabilité sur cet élément. Un AssetPartyRole daté n'en est donc
pas un substitut exact. Un code d'exploitant ou de propriétaire ne doit pas y être mis en correspondance
sur la seule base de son libellé. Voir la [définition de Location dans FHIR R5](https://hl7.org/fhir/R5/location-definitions.html#Location.managingOrganization)
et les [recommandations d'intégration FHIR](/docs/fhir-registry-integration/).

Les adresses FHIR ont déjà une période d'utilisation. Une assertion d'adresse de bien nécessaire
indépendamment n'exige pas de dupliquer un fait d'adresse médical natif,
et l'attribution elle-même n'est pas une Address FHIR. Conservez la représentation source
choisie et comparez explicitement la sémantique des intervalles avant de projeter des
dates. Voir [Address.period dans FHIR R5](https://hl7.org/fhir/R5/datatypes-definitions.html#Address.period).

## Exécuter l'exemple

Depuis la racine du dépôt :

```bash
uv run --locked python examples/facility-roles/validate_profile.py
uv run --locked pytest tests/test_facility_roles.py
```

Le profil de l'exemple exige des URI d'installation et d'acteur résolus localement ainsi qu'un
code de rôle ou de finalité d'adresse déclaré. Il admet les types concrets d'installation, d'acteur
et de groupe énumérés dans `validate_profile.py`. Des types et des
référentiels sources supplémentaires exigent une décision de profil ; la seule syntaxe d'un URI ne peut pas établir
qu'une cible est une installation physique ou un acteur autorisé. L'exemple utilise des
enregistrements identifiés de premier niveau pour les références et ne récupère pas d'URI distants.

`start_date` et `end_date` incluent tous deux leur jour calendaire ; `end_date` est donc le
dernier jour où la responsabilité est effective. Un rôle antérieur prenant fin le 30 juin et son
remplaçant commençant le 1er juillet ne se chevauchent pas. Une date de fin égale ou postérieure à la date de début
est exigée lorsque les deux dates sont connues. Les dates manquantes restent inconnues, et `effective_on` renvoie un résultat inconnu
lorsque ces bornes manquantes empêchent une réponse affirmative. Aucune règle d'unicité n'est
imposée aux acteurs ou aux rôles simultanés ; l'exclusivité nécessite une règle applicable de la
source.

Les tests valident les mêmes enregistrements au moyen du JSON Schema généré et du SHACL
développé par le contexte, puis appliquent le profil de l'exemple. Ils montrent aussi qu'un
URI bien formé pointant vers un site de prestataire virtuel passe le champ d'acteur du bien du vocabulaire,
qui a la forme d'un URI, mais échoue à la règle d'acteur du profil, et qu'un
groupe peut détenir une responsabilité datée. Les références d'adresse typées ont des vérifications
SHACL distinctes. Ce sont des exemples exécutables locaux, et non une application à l'exécution ni une
revendication de conformité d'adoptant.
