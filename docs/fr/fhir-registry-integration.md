# Intégration du registre avec FHIR

Utilisez les ressources FHIR natives pour les définitions de médicaments et le contenu des répertoires de soins. PublicSchema fournit l'identité intersectorielle du sujet et des liens qualifiés vers les entrées de registre. Il ne reproduit pas le modèle de ressources médicales et n'exige pas de serveur FHIR pour cette intégration fondée sur des fichiers.

L'[exemple exécutable](../../examples/fhir-registry/) contient deux documents distincts :

- `bundle.fhir.json` est un Bundle FHIR R5 natif de type collection contenant 19 ressources. Son type de média est `application/fhir+json`.
- `registry-links.json` est une enveloppe d'adaptateur JSON ordinaire contenant des sujets PublicSchema, des entrées RegistryEntry, des liens RecordReference, des liaisons de ressources explicites et des faits sources sans correspondance. Ses champs d'enveloppe relèvent de la configuration d'application de l'exemple ; ce ne sont ni de nouveaux termes du vocabulaire PublicSchema ni un profil FHIR publié.

Exécutez depuis la racine du dépôt, après la [configuration de développement habituelle](../../CONTRIBUTING.md) :

```bash
uv run --locked python examples/fhir-registry/validate.py
uv run --locked pytest tests/test_fhir_registry.py -q
```

Ces commandes utilisent les dépendances Python existantes et des artefacts locaux. Elles ne nécessitent ni connexion réseau, ni installation de Java, ni service de terminologie, ni registre en fonctionnement. Le vérificateur signale 19 ressources, 19 entrées de registre, 20 références FHIR locales et cinq liens consommateurs. Pour un autre extrait fourni, passez `--bundle PATH --links PATH`.

## Version et choix des ressources

Cet exemple fixe **FHIR R5 5.0.0** et les profils de base publiés `http://hl7.org/fhir/StructureDefinition/{ResourceType}|5.0.0`, y compris celui de Bundle. Chaque ressource déclare ce profil exact dans `meta.profile`. Ces profils de base n'établissent pas la conformité à un guide d'implémentation juridictionnel, à l'EMA UPD, à ISO IDMP ni à un contrat d'échange clinique. Plusieurs ressources de définition de médicaments sont au statut Trial Use, avec des niveaux de maturité différents.

R5 est le contrat retenu pour cet exemple, car il fournit les ressources de définition de médicaments et les champs de répertoire utilisés ensemble ici. R4 a un [modèle MedicinalProduct](https://hl7.org/fhir/R4/medicinalproduct.html) différent ; la famille des ressources de définition existe aussi en R4B, mais cet exemple ne valide que R5. Un échange R4 ou R4B existant devrait conserver la version et les profils qu'il exige et utiliser une correspondance explicite, plutôt que de réétiqueter sa charge utile comme R5. Voir les [recommandations inter-versions](https://hl7.org/fhir/R5/versions.html) de HL7.

| Aspect | Ressource native et exemple |
| --- | --- |
| Définitions de produits à usage humain et vétérinaire | [MedicinalProductDefinition](https://hl7.org/fhir/R5/medicinalproductdefinition.html), avec des enregistrements de produit distincts et `domain`. Aucun des deux enregistrements ne désigne un lot physique, une prescription ou une interchangeabilité avec l'autre produit. |
| Rôles des ingrédients et détail des substances | [Ingredient](https://hl7.org/fhir/R5/ingredient.html) pointe vers son produit par `for` et vers [SubstanceDefinition](https://hl7.org/fhir/R5/substancedefinition.html) par `substance.code.reference`. Le jeu de test conserve un rapport de dosage numérique et les systèmes d'unités. |
| Forme préparée et usage vétérinaire | [AdministrableProductDefinition](https://hl7.org/fhir/R5/administrableproductdefinition-definitions.html) utilise `formOf`, la voie d'administration, les espèces cibles et des temps d'attente qualifiés par tissu. Le temps d'attente synthétique de zéro jour pour le lait est explicite ; un usage non autorisé ne doit jamais être encodé comme un temps d'attente nul. |
| Configuration de conditionnement | [PackagedProductDefinition](https://hl7.org/fhir/R5/packagedproductdefinition-definitions.html) utilise `packageFor`. Une configuration de conditionnement a sa propre identité ; le contenu fabriqué détaillé et les lots sont hors du périmètre de ce jeu de test. |
| Autorisation de mise sur le marché médicale | [RegulatedAuthorization](https://hl7.org/fhir/R5/regulatedauthorization-definitions.html) possède une référence de sujet distincte, une juridiction, un titulaire, une autorité de réglementation et une période de validité. L'autorisation n'est ni l'identité du produit ni sa disponibilité. |
| Prestataire, locaux, service | [Organization](https://hl7.org/fhir/R5/organization-definitions.html), [Location](https://hl7.org/fhir/R5/location-definitions.html) et [HealthcareService](https://hl7.org/fhir/R5/healthcareservice-definitions.html). `HealthcareService.providedBy` identifie le prestataire clinique, tandis que `Location.managingOrganization` identifie l'organisation responsable de la mise à disposition et de l'entretien. FHIR interprète un `providedBy` absent comme la `managingOrganization` de la Location ; renseignez donc `providedBy` chaque fois que le prestataire diffère de l'organisation gestionnaire. Ce contrat exige `providedBy` sur chaque HealthcareService, et le jeu de test utilise des organisations différentes. |
| Accréditation d'une organisation | [Organization.qualification](https://hl7.org/fhir/R5/organization-definitions.html#Organization.qualification) de R5, avec code, émetteur, identifiant et période. Cela ne transforme pas une accréditation portant uniquement sur des locaux en qualification de l'organisation. |
| Connectivité technique | [Endpoint](https://hl7.org/fhir/R5/endpoint-definitions.html) conserve le type de connexion, le type de charge utile, le type MIME et l'adresse. Un point de terminaison répertorié n'est pas contacté et n'accorde aucun accès. |

Les concepts cliniques sont délibérément synthétiques, souvent exprimés avec `CodeableConcept.text`. Un adoptant doit sélectionner les terminologies sources réelles et les profils publiés applicables. L'exemple n'introduit pas de nouveau système de codes médical.

## Contrat d'identité et de résolution locale

Pour chaque ressource FHIR, une liaison associe une `RegistryEntry` existante à un `fhir_full_url` exact, à un `resource_type`, à un `profile` fixé et à une paire `system`/`value` d'identifiant métier. Ces valeurs identifient des choses différentes :

| Valeur | Signification |
| --- | --- |
| `(register_uri, record_id)` | Clé qualifiée d'entrée PublicSchema. `record_id` reste une chaîne de caractères dont les zéros initiaux sont conservés. |
| `subject_uri` | Assertion d'identité explicite pour la chose ou la définition décrite. Elle n'est pas copiée depuis l'URL de l'enregistrement FHIR. |
| `fullUrl` et `id` de ressource FHIR | Adresse et identité logique locale de l'enregistrement FHIR source. |
| `identifier.system` et `identifier.value` FHIR | Un identifiant métier de la source. Faire concorder cette paire vérifie la correspondance déclarée ; cela ne prouve pas l'autorité de la source et ne fusionne pas les identités. |

`Organization` et `health/HealthFacility` de PublicSchema fournissent dans le fichier annexe des identités intersectorielles utiles indépendamment. Leur détail médical reste en FHIR natif. HealthFacility désigne des locaux physiques et n'est pas équivalent à toute Location FHIR. Cet exemple exige que la Location liée ait `mode: instance` et une classification explicite de site ou de bâtiment (`si`/`bu` dans `http://terminology.hl7.org/CodeSystem/location-physical-type`) ; les localisations conceptuelles et virtuelles sont rejetées.

Les enregistrements de médicaments et de substances omettent le `subject_type` optionnel de PublicSchema : l'exemple ne crée pas de classe médicale native de remplacement et n'utilise pas une classe de ressource FHIR comme preuve du type d'un sujet du monde réel. À la place, chaque lien consommateur déclare `expected_resource_type`, qui est vérifié par rapport à l'enregistrement natif résolu. La valeur renvoyée comprend la ressource FHIR inchangée et le `subject_uri` affirmé séparément.

Toutes les ressources proviennent du Bundle local fourni. Les références absolues doivent correspondre à un `fullUrl` exact ; les références relatives `ResourceType/id` se résolvent par rapport à l'URL de base de l'entrée source. Chaque fullUrl doit concorder avec le type et l'id réels de sa ressource. Les cibles de référence sont vérifiées par rapport aux contraintes `targetProfile` de la StructureDefinition R5 publiée ; un `Reference.type` ou un `Reference.identifier` explicite doit aussi concorder avec l'enregistrement résolu. La seule graphie d'une URL ne suffit pas.

La résolution d'une entrée qualifiée renvoie `resolved`, `missing-record` ou `missing-resource`. Les désaccords d'identité et de type sont des erreurs. L'exemple exige que ses cinq liens consommateurs soient résolus. `RegistryEntry.source_records` peut conserver un pointeur de provenance non résolu, mais ce pointeur n'est pas traité comme une source vérifiée. Aucune URL d'enregistrement, aucun point de terminaison, système d'identifiants, contexte ou URL de profil ne déclenche de requête distante.

Ce contrat volontairement borné rejette les profils supplémentaires, les extensions, les extensions modificatrices, les règles implicites, les ressources contenues, les Bundles imbriqués, les références spécifiques à une version, les références FHIR par identifiant seul et les chemins de référence non décrits par les profils de ressources chargés. La prise en charge de l'un d'eux exige une modification explicite de l'adaptateur et les artefacts applicables. Un FHIR valide hors de ce contrat n'en devient pas pour autant un FHIR invalide.

Le JSON FHIR natif a sa propre sérialisation. N'ajoutez pas le contexte JSON-LD de PublicSchema, ne renommez pas `resourceType` en `@type` et ne décrivez pas ce Bundle comme du JSON-LD. Les consommateurs RDF doivent utiliser la [représentation RDF de FHIR](https://hl7.org/fhir/R5/rdf.html), qui est distincte.

## Correspondance des enregistrements plats de registres de santé vers FHIR

PublicSchema n'a pas de classes natives de médicament, de service de soins ou d'accréditation. Les échanges entre registres portent souvent ces faits dans des enregistrements plats. Les lignes ci-dessous nomment des enregistrements et des champs sources typiques ainsi que la ressource FHIR R5 qui porte chacun d'eux. Ce sont des décisions de correspondance, et non un convertisseur général ni des affirmations d'équivalence exacte. Conservez la source originale et consignez explicitement tout champ sans correspondance avant de remplacer les données sources d'un adoptant.

| Enregistrement ou champ source | Destination FHIR et conditions |
| --- | --- |
| `MedicinalProduct`, `VeterinaryMedicinalProduct` | Utilisez MedicinalProductDefinition. `name` correspond à un nom de produit, `identifiers` à des identifiants métier et `medicinal_classification` à une classification uniquement après préservation du référentiel et du sens du code. Choisissez `combinedPharmaceuticalDoseForm` pour `medicinal_dose_form` uniquement lorsqu'il décrit la même forme au niveau du produit. Le domaine vétérinaire ne détermine pas à lui seul les espèces cibles et n'autorise pas l'usage. |
| `MedicinalIngredient`, `medicinal_ingredients` | Utilisez Ingredient et ses références `for`. `ingredient_substance` peut référencer SubstanceDefinition. Un `ingredient_function` source qui mêle les rôles actif et excipient à des fonctions plus précises exige de décider si chaque valeur relève de `role` ou de `function` en FHIR. Faites correspondre `strength_numerator`/`strength_denominator` au rapport de présentation ou de concentration approprié uniquement lorsque la base de mesure est connue. |
| `AdministrableProduct` | Utilisez AdministrableProductDefinition. `presentation_of` correspond à `formOf`, `administrable_dose_form` à `administrableDoseForm` et `administration_routes` aux structures de voie d'administration lorsque leurs sens concordent. Il n'existe pas de champ `name` général direct. Ses relations détaillées avec les ingrédients utilisent `for` d'Ingredient ; son `ingredient` codé est une représentation différente. Conservez un nom autrement sans correspondance ou un lien source non pris en charge. |
| `PackagedMedicinalProduct` | Utilisez PackagedProductDefinition. `name`, les identifiants et `package_description` peuvent y être conservés. Examinez `packaged_medicines` en tant que `packageFor`, qui identifie le produit associé, séparément du contenu réel `packaging.containedItem`. `package_type` et `package_quantity` exigent un examen du niveau de conditionnement et des unités ; une quantité de substance n'est pas un nombre de contenants. |
| `HealthcareServiceOffering` | Utilisez HealthcareService pour `name`, `healthcare_provider`/`providedBy`, `service_facilities`/`location` et la classification de service de la source. Choisissez `category`, `type` ou `specialty` pour `healthcare_service_kind` selon le sens. Un `service_channel` textuel n'a pas de champ général exact. Pour `service_endpoints`, distinguez une référence à un enregistrement Endpoint de son `address` réseau ; exigez les détails manquants de connexion et de charge utile avant de créer un Endpoint natif. |
| `valid_from` et `valid_to` d'un service | HealthcareService de base en R5 n'a pas de période d'effet générale pour l'offre de service. `active`, `availability` et les horaires d'ouverture ne peuvent pas la remplacer. Conservez les deux dates sources comme sans correspondance jusqu'à ce qu'un profil publié applicable ou une extension justifiée porte ce fait. |
| `FacilityManagementAssignment` | Une attribution de gestion d'installation est ambiguë. Déterminez d'abord si la source affirme l'exploitation du service, l'entretien des locaux, la propriété ou la gouvernance institutionnelle. Location.managingOrganization peut porter une assertion actuelle d'entretien uniquement lorsque ce rôle est établi. Il n'a pas de période de gestion ; les `valid_from`/`valid_to` de la source ne sont donc pas transférés dans cette référence nue. Les rôles datés sur des biens physiques nécessaires indépendamment utilisent `AssetPartyRole` avec un sens de rôle explicite. |
| `FacilityAddressAssignment` | La Location native peut conserver une Address avec sa période d'utilisation. L'`AssetAddressAssignment` intersectoriel reste utile pour l'historique des locaux scolaires et agricoles. Préservez la finalité physique/postale. Une SpatialGeometry arbitraire distincte ne peut pas être comprimée dans `Location.position`, qui est un point avec latitude/longitude et altitude optionnelle. Conservez la géométrie non prise en charge au moyen de l'enregistrement intersectoriel et des liens sources. |
| `HealthcareAccreditation` | La qualification d'une organisation peut utiliser Organization.qualification, en conservant l'identifiant, le code de qualification, l'émetteur et la période applicable. Un sujet portant uniquement sur des locaux, un `accreditation_standard` détaillé ou un `accreditation_scope` n'ont pas ici de champ automatiquement équivalent. Gardez ces assertions et leurs preuves sans correspondance jusqu'à ce qu'un profil applicable soit sélectionné. N'inférez pas une accréditation de l'ensemble de l'organisation à partir du certificat d'un site. |
| `Authorization`, `Registration`, `ServiceCapacityObservation` génériques | Conservés pour leurs sens intersectoriels. Préférez RegulatedAuthorization pour les échanges natifs d'autorisations médicales ; cela ne rend pas équivalents tous les champs d'autorisation générale. Aucune équivalence FHIR n'est revendiquée pour l'observation de capacité générique. Un échange de rapports de santé nécessite un profil pour sa mesure réelle. |

Les bornes de dates exigent une décision explicite. Un `valid_to` source désigne souvent la dernière date applicable. `end_date` de PublicSchema est le dernier jour effectif, et [Period](https://hl7.org/fhir/R5/datatypes-definitions.html#Period) de FHIR inclut aussi sa fin, tout en permettant une précision partielle et des heures. Confirmez la borne de la source avant de convertir ; n'inventez pas d'horodatages et ne copiez pas une période sur un autre fait.

Le fichier annexe illustre `migration_outcomes` avec `state: unmapped`, la RecordReference originale, le chemin source, la valeur source et la raison. Ses exemples conservent une date de début de service générale, une date de fin de gestion ambiguë et un sujet d'accréditation portant uniquement sur des locaux. Utilisez les relations existantes `source_records` et `EvidenceAssertion` pour conserver la provenance dans un registre réel. Cet exemple illustre le signalement des faits non résolus ; il ne convertit pas automatiquement les enregistrements hérités et ne promet pas un aller-retour sans perte.

## Ce que les vérifications établissent

`validate.py` utilise l'archive officielle non modifiée des JSON Schema et les StructureDefinitions de base publiées dans [artefacts](../../examples/fhir-registry/artifacts/). Il vérifie leurs empreintes SHA-256 avant usage. Les archives totalisent environ 650 Ko compressées, n'ajoutent aucune dépendance et ne sont pas téléchargées à l'exécution. Les tests Python valident aussi les instances du fichier annexe PublicSchema par rapport aux schémas PublicSchema réellement générés.

JSON Schema vérifie la structure et les contraintes encodées dans cet artefact. L'adaptateur vérifie en outre les identités locales, les types cibles, les profils attendus et les identifiants métier décrits ci-dessus. Il n'évalue pas les invariants FHIRPath, l'ensemble des règles de choix et de cardinalité, les liaisons terminologiques, la complétude du narratif, l'exactitude clinique ni les profils juridictionnels. Cette distinction suit les [recommandations de validation FHIR](https://hl7.org/fhir/R5/validation.html).

Pour une vérification distincte lors de la rédaction, téléchargez le [validateur HL7 6.9.12](https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/6.9.12) fixé dans un stockage temporaire. Il nécessite Java ; le JAR pèse environ 187 Mo et n'est ni une dépendance du dépôt ni une dépendance d'exécution. Le script d'encapsulation vérifie le SHA-256 `0e53ab1d1a6f1e35f505255c0b8ce10a35fcf27e6e96b503640f784cd07e5ad6` avant l'exécution.

```bash
curl -fsSL https://github.com/hapifhir/org.hl7.fhir.core/releases/download/6.9.12/validator_cli.jar \
  -o /tmp/publicschema-fhir-validator-6.9.12.jar
uv run --locked python examples/fhir-registry/official_validate.py \
  --prepare-cache --cache-home /tmp/publicschema-fhir-cache
uv run --locked python examples/fhir-registry/official_validate.py \
  --jar /tmp/publicschema-fhir-validator-6.9.12.jar \
  --cache-home /tmp/publicschema-fhir-cache \
  --output /tmp/publicschema-fhir-outcome.json
```

La préparation télécharge explicitement des versions fixes depuis `https://packages2.fhir.org/packages/{name}/{version}` : `hl7.fhir.r5.core#5.0.0`, `hl7.fhir.xver-extensions#0.1.0`, `hl7.terminology.r5#6.2.0`, `hl7.fhir.uv.extensions.r5#5.2.0`, `hl7.terminology.r5#7.1.0`, `hl7.fhir.uv.extensions.r5#5.3.0` et `hl7.terminology#7.3.0`. Utilisez un cache dédié. Les paquets existants sont conservés ; un ensemble de versions différent est signalé pour examen. Les versions de publication des paquets et leurs métadonnées sont vérifiées ; contrairement aux artefacts intégrés au dépôt et au JAR, le contenu téléchargé dans ce cache n'est pas épinglé à l'octet près par l'exemple.

La validation elle-même interdit l'accès réseau dans les paramètres de l'outil officiel, désactive son récupérateur de ressources, utilise `-tx n/a`, fixe R5 et une juridiction mondiale, et active les vérifications de références. Les invariants FHIR restent activés. Le script d'encapsulation examine l'OperationOutcome renvoyé et se termine en échec en cas de problème de niveau error/fatal, même si le processus Java a renvoyé zéro. Passez `--bundle PATH` pour un autre Bundle natif.

Lisez les avertissements et les informations du résultat. Dans ce mode hors ligne, les quantités UCUM et le type MIME FHIR de l'exemple ne peuvent pas être validés par un serveur de terminologie, et la liaison de code de base de la qualification d'organisation n'a aucune source à vérifier. Un décompte d'erreurs nul a donc une portée plus étroite qu'une conformité FHIR complète. Un échange réel nécessite toujours les profils qu'il a choisis, sa politique terminologique, l'autorité de la source et les vérifications d'autorisation des consommateurs.
