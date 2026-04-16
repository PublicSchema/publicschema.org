# Enregistrement de consentement : ensemble minimum viable

Lorsqu'un formulaire recueille le consentement avant de procéder à une enquête ou un enregistrement, les propriétés PublicSchema suivantes fournissent un ConsentRecord minimum viable. Les programmes peuvent ajouter d'autres champs, mais ces cinq propriétés capturent la chaîne essentielle qui-quoi-quand exigée par les cadres d'audit et de protection des données.

## Propriétés

| Propriété | Type | Objectif |
|---|---|---|
| `consent_given` | booléen | Si le sujet a donné son consentement. Condition pour continuer. |
| `consenting_party` | référence (Person) | Qui a donné le consentement (le sujet, ou un tuteur pour les mineurs). |
| `consent_date` | date | Quand le consentement a été donné. |
| `purpose` | chaîne (vocabulaire : `consent-purpose`) | Ce que couvre le consentement (par ex. enregistrement, partage de données, recherche). |
| `privacy_notice_version` | chaîne | Quelle version de l'avis de confidentialité a été présentée. |

## Notes d'utilisation

- Si le consentement est refusé (`consent_given: false`), le formulaire doit s'arrêter ou bifurquer. Le ConsentRecord est quand même créé pour documenter le refus.
- Pour les enquêtes auprès des ménages, créer un seul ConsentRecord par ménage (pas par membre), sauf si les membres sont interrogés individuellement.
- `privacy_notice_version` permet aux auditeurs de vérifier que le bon avis a été présenté. Stocker l'identifiant de version, pas le texte complet de l'avis.

## Voir aussi

- [ADR-009 : ConsentRecord et couche de gouvernance des données](../../decisions/009-consent.md)
- [Concept ConsentRecord](../../schema/concepts/consent-record.yaml)
