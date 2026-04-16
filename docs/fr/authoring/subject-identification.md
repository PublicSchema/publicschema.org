# Modes d'identification du sujet

Les enregistrements de profil (FoodSecurityProfile, FunctioningProfile, AnthropometricProfile, SocioEconomicProfile) référencent leur sujet via la propriété `subject`. Trois modes couvrent l'éventail des scénarios d'identification lors de la collecte sur le terrain.

## Mode 1 : Référence

Le sujet est un enregistrement Person ou Group existant dans le système. Le formulaire stocke une référence (identifiant ou URI).

**Quand l'utiliser :** enquêtes liées à l'enregistrement, visites de suivi, tout contexte où les sujets sont pré-inscrits.

## Mode 2 : En ligne

Le sujet est décrit directement sur l'enregistrement de profil avec suffisamment d'informations d'identification pour un rattachement ultérieur (nom, date de naissance, localisation). Aucun enregistrement Person préexistant n'est requis.

**Quand l'utiliser :** dépistage communautaire, premier contact d'enregistrement, collecte mobile dans des zones sans inscription préalable.

## Mode 3 : Anonyme

Le sujet n'est pas identifié. Le profil capture les données d'observation sans les rattacher à un individu nommé.

**Quand l'utiliser :** enquêtes au niveau de la population (EDS, MICS, SMART), recherche, tout contexte où l'identification individuelle n'est pas nécessaire.

## Choix du mode

| Contexte | Mode | Notes |
|---|---|---|
| Visite de suivi dans un programme | Référence | Le sujet doit exister avant l'ouverture du formulaire |
| Dépistage communautaire PB | En ligne | Créer l'enregistrement Person à partir des données en ligne après le dépistage |
| Enquête nutritionnelle SMART | Anonyme | Pas de suivi individuel ; les données sont agrégées |
| Enquête d'enregistrement des ménages | Référence ou En ligne | Selon que le ménage a été pré-enregistré |
