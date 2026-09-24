# Conversion des dates de relation

Les relations nommées ci-dessous utilisent `start_date` et `end_date`, selon la
[convention des relations](/docs/schema-design/#5-contexte-temporel). Les enregistrements
sources qui portent pour elles une paire `valid_from` et `valid_to` décrivent
généralement une validité calendaire inclusive.

Les définitions publiées utilisent des jours calendaires entiers, et le jour de début
comme le jour de fin sont inclus : `end_date` est le dernier jour effectif
([ADR-027](../../decisions/027-end-date-boundary.md)). Une paire source inclusive
se convertit donc en renommant ses clés. Ces champs ne sont pas des horodatages et
ne décrivent pas le moment où une source a enregistré un fait.

## Relations qui utilisent des dates de début et de fin

| Relation | Ce que bornent les dates |
| --- | --- |
| HoldingParcelLink | La période pendant laquelle une exploitation agricole utilise une parcelle. |
| AnimalResidence | La période pendant laquelle un animal ou un groupe est détenu sur le site agricole identifié. |
| AnimalResponsibility | La période de la responsabilité déclarée de détenteur, de propriétaire ou autre. |
| AgriculturalServiceRole | La période pendant laquelle l'acteur agit comme le prestataire de services décrit. |
| IdentifierAssignment | La période d'attribution d'un identifiant au sujet. |
| NameUsage | La période d'utilisation du nom pour le sujet dans son contexte déclaré. |
| ContactPoint | La période d'utilisation du canal de communication pour joindre le sujet. |
| AssetPartyRole | La période de la responsabilité déclarée sur un bien physique. |
| AssetAddressAssignment | La période pendant laquelle l'adresse s'applique au bien pour sa finalité déclarée. |

RegistryEntry et Registration conservent des `valid_from`/`valid_to` inclusifs, y compris
les spécialisations d'enregistrement et d'autorisation. AgriculturalParcel conserve la
validité de sa description ; Certification et LandTenureAssertion conservent
leur validité de certification ou leur validité juridique substantielle. Ne les convertissez pas
au motif qu'une relation concernant le même sujet est convertie. `recorded_at` reste également inchangé.

## Préserver chaque jour effectif

Uniquement après avoir établi que la source utilise des jours calendaires entiers inclusifs :

1. Copiez tel quel un `valid_from` présent dans `start_date`.
2. Copiez tel quel un `valid_to` présent dans `end_date`.
3. Supprimez les clés sources. Conservez chaque borne omise comme omise.

Par exemple :

```json
{"@type":"AgriculturalServiceRole","valid_from":"2026-12-31","valid_to":"2026-12-31"}
```

devient :

```json
{"@type":"AgriculturalServiceRole","start_date":"2026-12-31","end_date":"2026-12-31"}
```

Les deux décrivent un seul jour effectif. Une fin absente reste inconnue ; elle n'est pas
remplacée par une date maximale ni traitée comme la preuve d'une validité perpétuelle. Une
précision inconnue, des dates partielles, des horodatages et des conventions de borne non
précisées exigent une clarification de la source. Une source dont la fin est le premier jour
où la validité ne s'applique plus n'est pas inclusive : retranchez un jour de sa fin, ou
clarifiez-la, avant d'utiliser l'utilitaire.

## Interpréter les attributions d'installations sources

Les enregistrements sources indiquent souvent seulement qu'une organisation gère une installation,
sans distinguer l'exploitation des locaux de leur entretien ou de leur propriété. Examinez les
preuves de la source avant de choisir un code de rôle, avec son référentiel, pour AssetPartyRole.
Faites correspondre l'installation à `subject_uri` et l'organisation à `asset_actor`, avec un
`asset_role_type` explicite. Conservez l'identité du sujet physique. Si les
preuves établissent plusieurs responsabilités, représentez des assertions distinctes et
conservez leurs liens sources. N'inventez pas ces responsabilités et ne prétendez pas qu'une
déclaration générique de gestion les prouve.

Pour un enregistrement source qui attribue une adresse à une installation :

| Fait source | AssetAddressAssignment |
| --- | --- |
| L'installation | `subject_uri`, faisant référence à l'installation physique |
| L'adresse | `assigned_address`, en conservant l'Address |
| Une position ou une géométrie sur l'attribution | Aucun champ sur l'attribution ; enregistrez une position dans `location` de l'Address ou dans la `spatial_geometry` du bien |
| Aucune finalité explicite | Ajoutez une `address_purpose` étayée par la source sous forme de CodedValue, en conservant son référentiel. |

Le choix du rôle ou de la finalité de l'adresse est une étape sémantique que l'utilitaire
n'effectue pas. Il ne convertit les dates d'un AssetPartyRole ou d'un AssetAddressAssignment
qu'une fois présents le bien, sa partie ou son adresse, et un code de rôle ou de finalité
qualifié par son référentiel. La présence d'un code ne démontre pas l'existence de ses preuves
sources ; cela reste de la responsabilité de l'implémenteur.

Pour les faits médicaux déjà représentés en FHIR natif, conservez cette représentation
choisie. Une assertion partagée sur le patrimoine immobilier n'a d'utilité que lorsque des consommateurs
en ont besoin indépendamment. Voir [responsabilités et adresses des installations](/docs/facility-roles/).

## Utiliser l'utilitaire à portée limitée

L'utilitaire, qui n'utilise que la bibliothèque standard, lit un document JSON et écrit un résultat
complet sur la sortie standard. Il ne réécrit pas son entrée et n'utilise pas la construction du
vocabulaire comme cadre de conversion. Il attend des enregistrements déjà mis en correspondance avec
les types PublicSchema ci-dessus qui portent encore les `valid_from`/`valid_to` de la source.
Examinez d'abord le contrat de la source, puis exécutez depuis la racine du dépôt :

```bash
uv run --locked python examples/relationship-date-migration/migrate.py \
  --source-boundary inclusive-calendar-days \
  examples/relationship-date-migration/source-records.json
```

Comparez le résultat avec `examples/relationship-date-migration/records.json`.
Lorsque vous enregistrez votre propre résultat, choisissez un fichier de sortie différent du
fichier d'entrée. L'entrée porte les clés de date de la source et ne doit pas être validée comme
charge utile de relation PublicSchema avant la conversion.

Le point d'entrée Python est
`migrate_relationship_dates(document, source_boundary="inclusive-calendar-days")`.
Il renvoie une copie profonde. Repasser le résultat dans l'utilitaire est idempotent et ne
nécessite pas de déclaration de borne source lorsqu'il ne reste aucune date de validité source.
Tout diagnostic lève MigrationError ; la CLI émet des diagnostics JSON sur l'erreur
standard, se termine avec le code de sortie 2 et n'émet aucun document partiel sur la sortie standard.
Les chemins utilisent l'échappement JSON Pointer. L'argument d'origine et le fichier d'entrée
restent inchangés en cas de succès comme d'échec.

L'utilitaire accepte l'alias compact de `@type` de chaque relation et son identifiant
PublicSchema exact, sous forme d'IRI compacte `publicschema:` ou d'URI absolu.
HoldingParcelLink, AnimalResidence et AgriculturalServiceRole sont dans le domaine `agri/` ;
les autres relations sont à la racine. Les identifiants de type sont conservés. Un
espace de noms arbitraire portant le même nom local est rejeté, de même que les types multiples
impliquant ces relations. L'interprétation des alias de contexte et le JSON-LD développé
nécessitent un adaptateur distinct. Les autres classes, y compris les types d'enregistrements
sources pas encore mis en correspondance avec PublicSchema, conservent leurs dates d'origine.

Les paires mêlant dates sources et dates actuelles sont rejetées même lorsqu'elles semblent concorder.
Rapprochez-les à partir de la source. Les dates exactes impossibles, les intervalles effectifs
inversés et une précision non prise en charge produisent des diagnostics de champ distincts et
déterministes.

Exécutez les vérifications ciblées :

```bash
uv run --locked pytest tests/test_relationship_date_migration.py
```

Les tests comparent l'appartenance des jours effectifs de part et d'autre de la conversion, y compris
dans des cas de mois, d'année, de jour bissextile et de jour unique. Ils couvrent les bornes inconnues,
les identifiants de classe non pris en charge, le sens des attributions d'installations, les bornes
omises, l'idempotence et l'échec atomique. Les jeux de test convertis sont aussi vérifiés par rapport
au JSON Schema réellement généré et aux sorties SHACL développées par le contexte. La hiérarchie de
classes générée est examinée pour trouver les descendants de chaque relation convertie, de sorte qu'un
sous-type concerné ne puisse pas sortir silencieusement des types admis par l'utilitaire. Les champs
optionnels du vocabulaire n'imposent pas à eux seuls toutes les règles de profil.
