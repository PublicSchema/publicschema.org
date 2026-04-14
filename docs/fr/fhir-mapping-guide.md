# Guide de correspondance FHIR

Ce guide explique comment échanger les données PublicSchema sur le handicap et le fonctionnement via FHIR R4. Il couvre les deux formes courantes (`Observation` pour les résultats traités, `QuestionnaireResponse` pour les captures brutes d'enquête), le système de codage LOINC, et la limite entre ce que PublicSchema spécifie et ce qui reste au choix de l'implémenteur.

Portée : les propriétés de fonctionnement du Washington Group (WG-SS, WG-ES, CFM WG/UNICEF), ainsi que les propriétés anthropométriques et de grossesse que les programmes de protection sociale reçoivent couramment des systèmes de santé.

## Pourquoi FHIR compte pour la protection sociale

Les données sur le handicap et le statut fonctionnel proviennent souvent des systèmes de santé. Lorsque ces données circulent vers les programmes de protection sociale (éligibilité aux transferts monétaires, allocation handicap, orientations), le format d'échange est fréquemment FHIR.

PublicSchema n'impose pas FHIR. Il documente la correspondance pour que les implémenteurs alignent leur code sur les observations codées LOINC sans inventer leur propre représentation.

## Les deux schémas

- **`Observation`** : un résultat traité, stocké une seule fois dans un registre de bénéficiaires. `Observation.code` porte le code LOINC de la question WG ; `valueCodeableConcept` porte la réponse (no_difficulty, some_difficulty, a_lot_of_difficulty, cannot_do).
- **`QuestionnaireResponse`** : la saisie brute du formulaire tel qu'administré, avec tous les items du panel, l'ordre préservé et les traces de logique de saut. Pointe vers le panel LOINC WG-SS à `http://loinc.org/q/90151-4`.

Les systèmes SP qui reçoivent le WG-SS d'une enquête reçoivent généralement un `QuestionnaireResponse` et dérivent ensuite des `Observation` par item pour les règles d'éligibilité.

## Codes LOINC

Le panel WG-SS est LOINC `90151-4`. Les codes d'item individuels de WG-SS, WG-ES et CFM sont disponibles via le CSV de publication LOINC (compte gratuit requis sur loinc.org), le serveur de terminologie FHIR de LOINC (`https://fhir.loinc.org`), ou le tableau de correspondance LOINC publié par le Washington Group.

Si aucun code LOINC n'existe pour un item donné, les implémenteurs utilisent un `CodeSystem` local et documentent la lacune. Ne pas inventer de codes LOINC.

## Voir aussi

- La version anglaise de ce guide contient les exemples JSON complets et la discussion détaillée de IPS et des profils nationaux.
- [Guide d'interopérabilité et de correspondance](/fr/docs/interoperability-guide/)
- [Divulgation sélective](/fr/docs/selective-disclosure/)
