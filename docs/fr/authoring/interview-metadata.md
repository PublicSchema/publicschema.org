# Métadonnées d'entretien

Chaque enregistrement de profil porte un contexte administratif sur la façon dont les données ont été collectées. Ce guide explique comment les auteurs de formulaires doivent renseigner les propriétés clés de métadonnées d'entretien.

## `observation_date`

La date de collecte des données. Pour la plupart des formulaires de terrain, c'est la date du jour (renseignée automatiquement à l'ouverture ou à la soumission du formulaire). Lorsque la saisie se fait après coup (par ex. transcription papier-numérique), la observation_date doit être la date de collecte originale, pas la date de transcription.

## `performed_by`

L'agent qui a effectué la collecte. Cela peut être :

- **Une référence à un enregistrement Agent** (Person ou Organization) lorsque l'enquêteur est un utilisateur connu et enregistré dans le système.
- **Un nom affiché** lorsque le système ne maintient pas de registre d'enquêteurs.

Les systèmes de formulaires qui authentifient les enquêteurs doivent remplir ce champ automatiquement à partir de l'utilisateur connecté.

## `instrument_used`

Une référence à l'enregistrement Instrument décrivant l'outil de collecte. Pour les instruments standard (WG-SS, SMART, FCS du PAM), utiliser l'identifiant canonique du registre d'instruments PublicSchema.

## `administration_mode`

Comment l'instrument a été administré. Valeurs du vocabulaire `administration-mode` :

- `self` : le sujet a rempli l'instrument lui-même
- `proxy` : un aidant ou un membre du ménage a répondu au nom du sujet
- `assisted` : le sujet a répondu avec l'aide d'un enquêteur
- `mixed` : certains items étaient auto-déclarés, d'autres déclarés par procuration

Pour les instruments enfants (CFM 2-4, CFM 5-17), le mode est toujours `proxy` car c'est l'aidant qui répond.

## `respondent` et `respondent_relationship`

Lorsque le mode d'administration est `proxy` ou `mixed`, enregistrer qui a répondu et sa relation avec le sujet. `respondent` est une référence ou une description de la personne qui a répondu. `respondent_relationship` utilise le vocabulaire `relationship-type` (par ex. parent, conjoint, aidant).
