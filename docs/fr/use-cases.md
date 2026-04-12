# Cas d'utilisation

PublicSchema fournit des définitions communes pour la prestation de services publics. Il existe de nombreuses façons de l'utiliser, de l'alignement des codes de vocabulaire dans des tableurs à l'émission d'attestations vérifiables. Cette page décrit des scénarios concrets où PublicSchema aide les programmes à se coordonner, à partager des données et à atteindre les personnes qu'ils servent.

## Sommaire

- [Déduplication inter-programmes entre secteurs](#déduplication-inter-programmes-entre-secteurs)
- [Attestations portables pour les populations déplacées](#attestations-portables-pour-les-populations-déplacées)
- [Rapportage normalisé entre programmes et donateurs](#rapportage-normalisé-entre-programmes-et-donateurs)
- [Passation de marchés de systèmes interopérables](#passation-de-marchés-de-systèmes-interopérables)
- [De l'enregistrement des naissances à l'inscription multi-secteurs](#de-lenregistrement-des-naissances-à-linscription-multi-secteurs)
- [Suivi de la transition école-travail](#suivi-de-la-transition-école-travail)
- [Vérification de l'éligibilité au point de service](#vérification-de-léligibilité-au-point-de-service)
- [Coordination de la réponse aux catastrophes](#coordination-de-la-réponse-aux-catastrophes)
- [Comparaison inter-pays de programmes et recherche en politiques publiques](#comparaison-inter-pays-de-programmes-et-recherche-en-politiques-publiques)
- [Harmonisation des API au sein d'une fédération](#harmonisation-des-api-au-sein-dune-fédération)
- [Quels artefacts importent pour quel cas d'utilisation](#quels-artefacts-importent-pour-quel-cas-dutilisation)

## Déduplication inter-programmes entre secteurs

**Qui :** Un gouvernement gérant la protection sociale, la restauration scolaire et l'assurance maladie comme programmes distincts, chacun sur un système différent.

**Le problème :** Chaque système contient des enregistrements pour les mêmes familles, décrits différemment. La base de données du ministère de l'éducation les appelle "étudiants", le système de santé les appelle "patients" et le système de transfert d'argent les appelle "bénéficiaires". Il n'existe pas de moyen fiable de vérifier si une personne est déjà inscrite ailleurs. Même lorsque les champs peuvent être associés par leur nom, des codes divergents rendent la comparaison peu fiable : "active" dans un système peut ne pas avoir le même sens que "active" dans un autre.

**Comment PublicSchema aide :** L'équipe d'intégration effectue la correspondance des champs de chaque système avec les propriétés PublicSchema (given_name, national_id, date_of_birth, enrollment_status). Un registre partagé peut alors rapprocher les enregistrements entre systèmes en utilisant un vocabulaire commun. Aucun système n'a besoin de modifier son modèle de données interne.

**Artefacts clés :** Concepts (Personne, Inscription), propriétés, codes de vocabulaire, correspondances de systèmes.

## Attestations portables pour les populations déplacées

**Qui :** Un réfugié enregistré dans un pays, arrivant dans un pays d'accueil qui doit vérifier son identité et son inscription antérieure à des services.

**Le problème :** Les enregistrements de la personne existent dans les systèmes du pays d'origine, mais le pays d'accueil n'y a pas accès. Interroger le système du pays d'origine peut être difficile ou impossible. La personne a besoin d'un moyen de prouver qui elle est et les services qu'elle a reçus.

**Comment PublicSchema aide :** Le pays d'origine émet une attestation vérifiable (verifiable credential) SD-JWT en utilisant les types d'attestation PublicSchema (IdentityCredential, EnrollmentCredential). Le pays d'accueil peut vérifier l'attestation hors ligne car elle utilise un schéma partagé. La divulgation sélective permet à la personne de ne révéler que ce qui est nécessaire (nom, date de naissance, inscription antérieure) sans exposer des informations sensibles.

**Artefacts clés :** Types d'attestation, contexte JSON-LD, règles de divulgation sélective, schémas JSON.

## Rapportage normalisé entre programmes et donateurs

**Qui :** Un donateur, un organe de coordination ou un tableau de bord gouvernemental agrégeant des données de plusieurs programmes, secteurs ou pays.

**Le problème :** Chaque programme rend compte en utilisant ses propres codes et noms de champs. L'un utilise "ACTV" pour une inscription active, un autre utilise "1", un troisième utilise "enrolled". L'agrégation des chiffres entre programmes nécessite une traduction manuelle à chaque période de rapport. Lorsque ces traductions entraînent des pertes (parce que les codes d'un programme ne correspondent pas clairement à ceux d'un autre), les chiffres agrégés ne sont pas fiables.

**Comment PublicSchema aide :** L'organe de coordination définit un modèle de rapportage qui fait référence aux codes de vocabulaire PublicSchema (enrollment-status, payment-status, delivery-channel). Chaque programme effectue la correspondance de ses codes internes une seule fois. À partir de là, l'agrégation est mécanique.

**Artefacts clés :** Codes de vocabulaire, définitions de concepts, définitions de propriétés.

## Passation de marchés de systèmes interopérables

**Qui :** Un gouvernement passant un marché pour un nouveau registre, un système d'information ou un outil de gestion de cas dans un secteur quelconque.

**Le problème :** Les appels d'offres spécifient que "le système doit être interopérable", ce qui est trop vague pour être évalué. Les fournisseurs l'interprètent à leur guise. Il n'existe pas de norme concrète à tester.

**Comment PublicSchema aide :** L'appel d'offres fait directement référence à PublicSchema : "Le système doit exporter les enregistrements de Personne avec les propriétés suivantes : given_name, family_name, date_of_birth, national_id. Les champs de statut doivent utiliser les codes des vocabulaires PublicSchema." Cela fonctionne que vous passiez un marché pour un registre social, un système d'information scolaire ou une base de données de structures de santé. Les fournisseurs disposent d'une cible concrète ; les évaluateurs ont quelque chose de vérifiable.

**Artefacts clés :** Définitions de concepts, inventaire de propriétés, définitions de vocabulaires, schémas JSON.

## De l'enregistrement des naissances à l'inscription multi-secteurs

**Qui :** Une autorité d'enregistrement des faits d'état civil (état civil) délivrant des actes de naissance, connectée à des programmes qui enrôlent automatiquement les nouveau-nés (assurance maladie, allocations destinées aux enfants, suivi de la vaccination).

**Le problème :** Une naissance est enregistrée, mais chaque programme en aval doit être notifié séparément, en utilisant son propre format de saisie. Les intégrations bilatérales entre l'état civil et chaque programme sont coûteuses à construire et à maintenir.

**Comment PublicSchema aide :** Le registre d'état civil publie un enregistrement en utilisant les propriétés PublicSchema de Personne (date_of_birth, sex, location). Le ministère de la santé récupère ce dont il a besoin pour la planification de la vaccination. Le système de protection sociale utilise le même enregistrement pour inscrire automatiquement l'enfant à une allocation pour enfants. Chaque système en aval consomme à partir de la même représentation canonique au lieu de nécessiter sa propre intégration.

**Artefacts clés :** Concepts (Personne, Identifiant), propriétés, codes de vocabulaire, schémas JSON.

## Suivi de la transition école-travail

**Qui :** Un ministère de l'éducation et un ministère du travail, chacun avec ses propres systèmes, cherchant à suivre les résultats des programmes pour les jeunes.

**Le problème :** Le système d'éducation suit les étudiants inscrits en formation professionnelle. Le ministère du travail suit les participants aux programmes d'emploi. Aucun système ne connaît l'autre. Il n'existe aucun moyen de mesurer si les diplômés de la formation professionnelle entrent effectivement dans des programmes d'emploi.

**Comment PublicSchema aide :** Les deux systèmes effectuent la correspondance de leurs modèles de données avec les concepts Personne et Inscription de PublicSchema. Une équipe de politique peut alors relier des enregistrements entre systèmes et mesurer les résultats : parmi les étudiants qui ont terminé la formation professionnelle, combien se sont inscrits à un programme d'emploi dans les six mois ? Le vocabulaire partagé rend la jointure possible sans fusionner les bases de données.

**Artefacts clés :** Concepts (Personne, Inscription, Programme), propriétés, codes de vocabulaire.

## Vérification de l'éligibilité au point de service

**Qui :** Un agent de paiement, une structure de santé ou une école vérifiant l'éligibilité d'une personne au point de service.

**Le problème :** La vérification de l'éligibilité nécessite actuellement une connexion en direct au registre central. Dans les zones reculées ou lors de pannes de système, la prestation de services s'interrompt car l'éligibilité ne peut pas être confirmée.

**Comment PublicSchema aide :** La personne détient une attestation vérifiable sur son téléphone ou sa carte à puce. Au point de service, l'appareil de l'agent vérifie la signature de l'attestation et contrôle que enrollment_status est "active" et que le montant du droit correspond. La vérification fonctionne hors ligne car elle est cryptographique, et non une interrogation de base de données. Les informations personnelles au-delà de ce qui est nécessaire à la transaction restent cachées grâce à la divulgation sélective.

**Artefacts clés :** Types d'attestation, règles de divulgation sélective, schémas JSON.

## Coordination de la réponse aux catastrophes

**Qui :** Plusieurs agences répondant à une catastrophe naturelle : gouvernement, agences des Nations Unies et ONG, enregistrant chacune les populations affectées de manière indépendante.

**Le problème :** Trois organisations enregistrent les familles affectées dans le même district en utilisant des formulaires de saisie et des systèmes différents. Il n'existe aucun moyen de savoir si une famille a déjà été enregistrée par une autre agence, ce qui conduit à une aide dupliquée pour certains et à des lacunes pour d'autres.

**Comment PublicSchema aide :** En alignant la collecte de données sur les concepts Personne et Ménage de PublicSchema, un organe de coordination peut dédupliquer toutes les listes d'enregistrement, identifier les familles qu'aucune agence n'a encore atteintes et allouer les ressources sans double comptage.

**Artefacts clés :** Concepts (Personne, Ménage, Groupe, GroupMembership, Localisation), propriétés, codes de vocabulaire, schémas JSON.

## Comparaison inter-pays de programmes et recherche en politiques publiques

**Qui :** Un analyste de politique publique, un chercheur ou une organisation internationale comparant les programmes de prestation de services publics entre pays.

**Le problème :** Chaque pays définit différemment des concepts tels que "inscription", "droit" et "réclamation". La comparaison nécessite une interprétation manuelle de la documentation de chaque pays, qui est incohérente et souvent incomplète.

**Comment PublicSchema aide :** L'analyste utilise l'inventaire de concepts et de propriétés de PublicSchema comme cadre structuré pour la comparaison. Pour chaque pays et secteur, il effectue la correspondance du modèle de données du programme local avec PublicSchema. Le résultat rend les divergences visibles et identifiables : le pays A collecte les coordonnées GPS des ménages, le pays B non. Le pays A définit l'inscription "inactive" comme "suspendue", le pays B l'utilise pour désigner une inscription "terminée".

**Artefacts clés :** Définitions de concepts (avec descriptions multilingues), inventaire de propriétés, définitions de vocabulaires, correspondances de systèmes.

## Harmonisation des API au sein d'une fédération

**Qui :** Un système national ou régional agrégeant des données de plusieurs agences, ministères ou niveaux de gouvernement.

**Le problème :** Cinq agences exposent chacune une API REST : registre social, système d'information scolaire, système d'information sanitaire, registre d'état civil, base de données d'extension agricole. Les noms de champs et les codes de valeurs diffèrent entre les cinq. La construction d'adaptateurs personnalisés pour chaque API est coûteuse et fragile.

**Comment PublicSchema aide :** La fédération impose que toutes les API alignent les noms de champs sur les propriétés PublicSchema et utilisent les codes de vocabulaire PublicSchema. Chaque agence conserve son schéma interne ; elle expose simplement une interface API alignée sur PublicSchema. La couche de fédération parle un seul langage au lieu de cinq.

**Artefacts clés :** Propriétés (comme noms de champs partagés), codes de vocabulaire (comme ensembles de valeurs partagés), schémas JSON (pour la validation des contrats).

## Quels artefacts importent pour quel cas d'utilisation

| Cas d'utilisation | Concepts | Propriétés | Vocabulaires | Schémas JSON | JSON-LD | Attestations |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Déduplication inter-programmes | x | x | x | | | |
| Attestations portables | x | x | | x | x | x |
| Rapportage normalisé | x | x | x | | | |
| Passation de marchés | x | x | x | x | | |
| Cascade d'enregistrement des naissances | x | x | x | x | | |
| Suivi école-travail | x | x | x | | | |
| Vérification au point de service | | | | x | | x |
| Coordination en cas de catastrophe | x | x | x | x | | |
| Comparaison inter-pays | x | x | x | | | |
| Fédération d'API | | x | x | x | | |

La plupart des cas d'utilisation ne nécessitent que des concepts, des propriétés et des codes de vocabulaire. JSON-LD et les attestations vérifiables sont nécessaires pour un sous-ensemble de scénarios. **Par où commencer :**

- Pour aligner les codes de valeurs sans modifier votre modèle de données, consultez le [Guide d'adoption du vocabulaire](/docs/vocabulary-adoption-guide/).
- Pour effectuer la correspondance de champs entre des systèmes existants, consultez le [Guide d'interopérabilité et de correspondance](/docs/interoperability-guide/).
- Pour concevoir un nouveau système compatible, consultez le [Guide de conception du modèle de données](/docs/data-model-guide/).
- Pour utiliser les contextes JSON-LD ou émettre des attestations vérifiables, consultez le [Guide JSON-LD et VC](/docs/jsonld-vc-guide/).
