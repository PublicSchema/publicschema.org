# French translation review — integration docs

## integration-patterns.md

**Overall impression:** Le texte est globalement lisible et techniquement exact. On relève cependant une répétition mécanique du calque "effectuer la correspondance" et quelques tournures légèrement rigides qui trahissent la traduction. Le reste du fichier passe bien.

### Flagged passages

**Line 3 — Current:** "Les mêmes concepts, propriétés et codes de vocabulaire fonctionnent sur n'importe quel transport : API REST, bus d'événements, attestations vérifiables (verifiable credentials), échanges de fichiers et pipelines d'analyse."
**Issue:** La parenthèse "(verifiable credentials)" en anglais est redondante puisque "attestations vérifiables" est déjà la traduction établie. On ne précise pas le terme anglais entre parenthèses pour les autres éléments de la liste.
**Proposed:** "Les mêmes concepts, propriétés et codes de vocabulaire fonctionnent sur n'importe quel transport : API REST, bus d'événements, attestations vérifiables, échanges de fichiers et pipelines d'analyse."
**Rationale:** La parenthèse crée une asymétrie dans la liste et sous-entend que le lecteur ne connaît pas le terme français. À supprimer.

**Line 9 — Current:** "Votre système effectue la correspondance de ses champs et codes avec PublicSchema une seule fois."
**Issue:** Calque de l'anglais "maps its fields." En français on dirait plutôt "aligne" ou "met en correspondance ses champs" sans la structure possessive lourde "de ses champs et codes."
**Proposed:** "Votre système aligne ses champs et codes sur PublicSchema une seule fois."
**Rationale:** "Effectuer la correspondance de" est une locution lourde qui revient tout au long du document. "Aligner sur" est plus naturel pour décrire une action ponctuelle d'harmonisation. L'alternance avec "mettre en correspondance" dans les passages plus techniques est acceptable.

**Line 15 — Current:** "Les consommateurs obtiennent un contrat prévisible sans connaître votre schéma interne."
**Issue:** "Les consommateurs" est un calque direct de "consumers" (au sens technique d'un système qui consomme une API). En français ce terme est ambiguë car il évoque d'abord les consommateurs finaux.
**Proposed:** "Les systèmes clients obtiennent un contrat prévisible sans connaître votre schéma interne."
**Rationale:** "Systèmes clients" ou "clients de l'API" est la formulation courante dans la documentation technique francophone pour désigner les consommateurs d'une API.

**Line 30 — Current:** "Validez les charges utiles de requête et de réponse avec les schémas JSON PublicSchema à la frontière de l'API."
**Issue:** "À la frontière de l'API" est un calque de "at the API boundary." En français on parle de "point d'entrée de l'API" ou simplement "au niveau de l'API."
**Proposed:** "Validez les charges utiles des requêtes et des réponses avec les schémas JSON PublicSchema au point d'entrée de l'API."
**Rationale:** "Frontière de l'API" n'est pas naturel. "Point d'entrée" ou "au niveau de l'API" rend le même sens sans le calque.

**Line 34 — Current:** "Les abonnés de différents systèmes les consomment sans correspondance bilatérale de champs."
**Issue:** "Les abonnés de différents systèmes les consomment" reproduit la structure calquée du passage précédent ("consumers"). "Correspondance bilatérale" est correct mais peut être allégé.
**Proposed:** "Les abonnés, quelle que soit leur plateforme, peuvent les traiter sans table de correspondance bilatérale."
**Rationale:** "Les traiter" est plus naturel que "les consommer" dans ce contexte. L'ajout de "table de" précise de quoi il s'agit.

**Line 51 — Current:** "L'enveloppe d'événement (type, horodatage, métadonnées de routage) vous appartient."
**Issue:** "L'enveloppe d'événement vous appartient" est un calque quasi-littéral de "The event envelope is yours." En français, "vous appartient" a une connotation de propriété légale ou personnelle peu adaptée au contexte.
**Proposed:** "L'enveloppe de l'événement (type, horodatage, métadonnées de routage) reste à votre discrétion."
**Rationale:** L'idée est que le format de l'enveloppe est libre, laissé à l'implémenteur. "Reste à votre discrétion" ou "est libre" rend cela sans la connotation de propriété du mot "appartient."

**Line 86 — Current:** "Pas d'API, pas d'infrastructure. Une table de correspondance et un CSV bien nommé."
**Issue:** La phrase est une traduction directe d'un slogan volontairement percutant en anglais ("No API, no infrastructure."). Le ton est bien trouvé, mais "bien nommé" peut laisser penser que le nom du fichier CSV est important, alors que l'anglais "well-named" renvoie au fait que les colonnes portent des noms canoniques.
**Proposed:** "Pas d'API, pas d'infrastructure. Une table de correspondance et un fichier CSV aux colonnes bien nommées."
**Rationale:** "Un CSV bien nommé" est ambigu (nom du fichier vs. noms des colonnes). "Aux colonnes bien nommées" précise l'intention.

---

## interoperability-guide.md

**Overall impression:** Le guide est dense et bien structuré. La traduction est généralement fidèle mais souffre de la répétition systématique du calque "effectuer la correspondance de" là où des alternatives plus naturelles existent. Plusieurs occurrences de "vous construisez" au lieu de "vous souhaitez" alourdissent inutilement. Quelques petits problèmes de registre sont signalés ci-dessous.

### Flagged passages

**Line 3 — Current:** "Ce guide est destiné aux équipes qui connectent des systèmes existants : effectuer la correspondance de champs entre plateformes, construire des échanges de données, consolider des enregistrements provenant de sources multiples ou exécuter des pipelines ETL."
**Issue:** La liste après les deux-points est grammaticalement incohérente : le sujet de la phrase principale est "les équipes qui connectent", mais la liste passe à l'infinitif sans verbe de connexion. La phrase anglaise utilise une série de gérondifs ("mapping fields, building exchanges..."), ce qui est naturel en anglais mais ne se calque pas directement en français.
**Proposed:** "Ce guide est destiné aux équipes qui connectent des systèmes existants : mise en correspondance de champs entre plateformes, construction d'échanges de données, consolidation d'enregistrements provenant de sources multiples ou exécution de pipelines ETL."
**Rationale:** Utiliser des formes nominales (mise en correspondance, construction, consolidation, exécution) rend la liste grammaticalement cohérente après les deux-points.

**Line 3 — Current:** "PublicSchema joue le rôle d'un point de référence partagé (une pierre de Rosette) de sorte que chaque système n'ait besoin que d'une seule correspondance au lieu d'une correspondance vers chaque autre système."
**Issue:** "De sorte que chaque système n'ait besoin que d'une seule correspondance" est lourd. "Au lieu d'une correspondance vers chaque autre système" est également un calque syntaxique.
**Proposed:** "PublicSchema joue le rôle de référence partagée (pierre de Rosette), permettant à chaque système de n'établir qu'une seule correspondance plutôt qu'une correspondance avec chacun des autres systèmes."
**Rationale:** "Permettant à chaque système de" est plus fluide que la subordonnée de conséquence. "N'établir qu'une seule correspondance" est plus actif que "n'avoir besoin que d'une seule correspondance."

**Lines 25 and 27 — Current:** "Vous déduplichez des enregistrements entre programmes ou secteurs" / "Vous construisez un entrepôt de données..."
**Issue:** "Vous déduplichez" est un néologisme acceptable, mais la série "vous construisez... vous construisez" (lignes 25-27) répète le même verbe pour des contextes différents et ne suit pas le registre professionnel attendu.
**Proposed:** "Vous dédupliquez des enregistrements entre programmes ou secteurs" / "Vous mettez en place un entrepôt de données..."
**Rationale:** "Dédupliquez" (avec l'orthographe standard, sans le -ch-) est la forme correcte. "Mettez en place" est plus précis que "construisez" pour un entrepôt de données.

**Line 35 — Current:** "Plus important encore, comme chaque système effectue sa correspondance vers les mêmes définitions partagées, le sens est préservé tout au long de la traduction."
**Issue:** "Tout au long de la traduction" est un calque de "across the translation" qui est idiomatique en anglais mais peu naturel ici. On ne "traverse" pas une traduction en français.
**Proposed:** "Plus important encore, comme chaque système se réfère aux mêmes définitions partagées, le sens est préservé lors des échanges."
**Rationale:** "Lors des échanges" exprime l'idée de bout en bout de la chaîne de traduction sans le calque spatial.

**Line 35 — Current:** "Sans vocabulaire partagé, les correspondances bilatérales sont souvent approximatives : les codes d'un système peuvent ne pas avoir d'équivalents dans un autre."
**Issue:** "Approximatives" est une traduction acceptable de "lossy" mais perd la nuance technique (perte d'information). "Avec perte" ou "imparfaites" seraient plus précis.
**Proposed:** "Sans vocabulaire partagé, les correspondances bilatérales sont souvent imparfaites : les codes d'un système peuvent ne pas avoir d'équivalents dans un autre."
**Rationale:** "Avec perte" est utilisé en informatique (compression avec perte) mais peut sembler trop technique dans ce contexte. "Imparfaites" conserve le sens sans jargon, avec l'explication qui suit dans la phrase.

**Line 43 — Current:** "Parcourez la [page des concepts](/concepts/) ou téléchargez le **classeur Excel de définition** pour un concept afin de voir toutes ses propriétés en un seul endroit."
**Issue:** "Parcourez" est correct mais un peu formel pour cette instruction directe. Le reste du guide utilise des impératifs, ce qui est cohérent, mais "parcourez" ajoute un ton légèrement suranné.
**Proposed:** "Consultez la [page des concepts](/concepts/) ou téléchargez le **classeur Excel de définition** pour voir toutes les propriétés d'un concept en un seul endroit."
**Rationale:** "Consultez" est plus courant dans les guides techniques francophones. La légère restructuration ("pour voir toutes les propriétés d'un concept") est plus directe.

**Line 58 — Current:** "Certains champs peuvent se diviser ou se fusionner."
**Issue:** "Se diviser ou se fusionner" est une construction réfléchie qui implique que les champs agissent d'eux-mêmes. L'anglais "split or merge" est actif dans ce contexte (vous devrez peut-être les diviser).
**Proposed:** "Certains champs peuvent être divisés ou fusionnés lors de la correspondance."
**Rationale:** La voix passive avec "lors de la correspondance" clarifie que c'est une action du traducteur, pas un comportement autonome des champs.

**Line 83 — Current:** "Une couche de traduction effectue la correspondance des champs et codes du système A vers les propriétés et codes de vocabulaire PublicSchema."
**Issue:** Nouvelle occurrence du calque "effectue la correspondance." Dans un contexte de flux de données, "traduit" ou "convertit" est plus naturel.
**Proposed:** "Une couche de traduction convertit les champs et codes du système A vers les propriétés et codes de vocabulaire PublicSchema."
**Rationale:** "Convertit" est idiomatique pour des transformations de données. Cela allège aussi la phrase.

**Line 117 — Current:** "Les champs qui n'ont pas été correctement mis en correspondance (mauvais type, contexte requis manquant)"
**Issue:** "Contexte requis manquant" est un calque de "missing required context" qui sonne comme du jargon de développeur. Pour un public de praticiens, préciser le sens est utile.
**Proposed:** "Les champs mal convertis (mauvais type, information contextuelle obligatoire absente)"
**Rationale:** "Information contextuelle obligatoire absente" est plus clair pour un public non développeur. "Mal convertis" est plus naturel que "n'ont pas été correctement mis en correspondance."

**Line 125 — Current:** "La ligne 2 contient les identifiants de propriétés PublicSchema"
**Issue:** "Les identifiants de propriétés" est ambigu : s'agit-il des noms de propriétés, des codes, des ID techniques ? L'anglais dit "property IDs" ce qui renvoie aux identifiants techniques (clés machine).
**Proposed:** "La ligne 2 contient les identifiants techniques des propriétés PublicSchema"
**Rationale:** Préciser "identifiants techniques" évite la confusion avec les libellés de la ligne 1.

**Line 133 — Current:** "Vous souhaitez prototyper un formulaire de collecte de données avant de vous engager dans un système"
**Issue:** "Avant de vous engager dans un système" est un calque de "before committing to a system." En français, "vous engager dans" a une connotation personnelle/décisionnelle un peu forte pour un choix technique.
**Proposed:** "Vous souhaitez prototyper un formulaire de collecte de données avant d'adopter un système dédié"
**Rationale:** "Adopter un système dédié" est plus précis et évite la connotation d'engagement personnel.

**Line 197 — Current:** "Si vous concevez un nouveau système de zéro"
**Issue:** "De zéro" est une traduction correcte mais informelle de "from scratch." Pour un document technique à portée internationale, "de bout en bout" ou "depuis la conception" serait plus neutre.
**Proposed:** "Si vous concevez un nouveau système en partant de zéro"
**Rationale:** L'ajout de "en partant de" rend la locution moins abrupte et plus naturelle en français écrit.

---

## jsonld-vc-guide.md

**Overall impression:** Le guide est bien traduit dans l'ensemble. Le niveau technique est bien géré, les termes spécialisés (JSON-LD, SD-JWT, SHACL) sont laissés intacts à juste titre. On relève quelques occurrences du même calque "effectuer la correspondance" et une phrase sur le comportement de repli qui manque de naturel.

### Flagged passages

**Line 3 — Current:** "C'est l'une des façons d'utiliser PublicSchema."
**Issue:** Correct mais légèrement lourd. L'anglais "This is one of several ways" porte "plusieurs" implicitement.
**Proposed:** "C'est l'une des nombreuses façons d'utiliser PublicSchema."
**Rationale:** Ajouter "nombreuses" est plus fidèle au sens anglais ("one of several") et évite de minimiser les autres approches.

**Line 5 — Current:** "Ce guide explique comment utiliser PublicSchema avec les contextes JSON-LD et les attestations vérifiables (verifiable credentials) SD-JWT."
**Issue:** Même observation que dans integration-patterns.md ligne 3 : la parenthèse "(verifiable credentials)" est redondante.
**Proposed:** "Ce guide explique comment utiliser PublicSchema avec les contextes JSON-LD et les attestations vérifiables SD-JWT."
**Rationale:** Cohérence avec la terminologie établie. La parenthèse n'apporte rien.

**Line 53 — Current:** "Lorsque votre système stocke le statut d'inscription, le statut de paiement, le genre, etc., effectuez la correspondance de vos codes internes vers les codes canoniques PublicSchema"
**Issue:** "Effectuez la correspondance de vos codes internes vers" revient encore. Dans ce contexte d'instruction directe, "convertissez" est plus court et plus naturel.
**Proposed:** "Lorsque votre système stocke le statut d'inscription, le statut de paiement, le genre, etc., convertissez vos codes internes vers les codes canoniques PublicSchema"
**Rationale:** Voir les observations récurrentes sur ce calque.

**Line 95 — Current:** "Consultez les définitions des types d'attestation dans le guide [Divulgation sélective](/docs/selective-disclosure/) pour déterminer quelles affirmations doivent être sélectivement divulgables dans les SD-JWT VC."
**Issue:** "Doivent être sélectivement divulgables" est maladroit : "doivent être divulgables sélectivement" ou simplement "sont à divulguer sélectivement" serait plus clair.
**Proposed:** "Consultez les définitions des types d'attestation dans le guide [Divulgation sélective](/docs/selective-disclosure/) pour déterminer quelles affirmations sont à divulguer de façon sélective dans les SD-JWT VC."
**Rationale:** "Sont à divulguer de façon sélective" est plus idiomatique en français pour exprimer une règle ou une recommandation.

**Line 99 — Current:** "Si votre système utilise des noms de champs ou des codes différents, utilisez les `system_mappings` dans les fichiers YAML de vocabulaire pour effectuer la traduction."
**Issue:** "Pour effectuer la traduction" est neutre et correct, mais "pour traduire" est plus direct.
**Proposed:** "Si votre système utilise des noms de champs ou des codes différents, utilisez les `system_mappings` dans les fichiers YAML de vocabulaire pour traduire les valeurs."
**Rationale:** "Pour traduire les valeurs" est plus précis et plus naturel. "Effectuer la traduction" est une locution verbale lourde là où un verbe simple suffit.

**Line 156 — Current:** "Cela signifie que toute clé JSON qui n'est pas explicitement définie dans le contexte se développera silencieusement vers `https://publicschema.org/{clé}`."
**Issue:** "Se développera" est un calque de "will expand to" (JSON-LD expansion). En français, le terme technique est "sera étendu" ou "s'étendra."
**Proposed:** "Cela signifie que toute clé JSON qui n'est pas explicitement définie dans le contexte s'étendra silencieusement vers `https://publicschema.org/{clé}`."
**Rationale:** "S'étendra" est le terme courant pour l'expansion JSON-LD en français. "Se développera" évoque plutôt une croissance ou une arborescence.

**Line 156 — Current:** "Par exemple, une faute de frappe comme `"givn_name"` se développerait vers `https://publicschema.org/givn_name` au lieu de déclencher une erreur."
**Issue:** Même observation sur "se développerait."
**Proposed:** "Par exemple, une faute de frappe comme `"givn_name"` s'étendrait vers `https://publicschema.org/givn_name` au lieu de déclencher une erreur."
**Rationale:** Cohérence avec la correction précédente.

**Line 158 — Current:** "Le schéma JSON n'autorise que les propriétés déclarées, donc `"givn_name"` échouerait à la validation."
**Issue:** "Échouerait à la validation" est un calque de "would fail validation." En français on dit plutôt "ne passerait pas la validation" ou "serait rejeté par la validation."
**Proposed:** "Le schéma JSON n'autorise que les propriétés déclarées, donc `"givn_name"` ne passerait pas la validation."
**Rationale:** "Ne passerait pas la validation" est idiomatique et plus naturel que "échouerait à la validation."

**Line 162 — Current:** "La propriété PublicSchema `preferred_name` correspond à `alternateName` de schema.org comme `broadMatch`, et non comme `exactMatch`."
**Issue:** "Correspond comme `broadMatch`" est un calque syntaxique de "maps to X as a broadMatch." En français, la structure "correspond [...] comme" est peu idiomatique. Il faudrait reformuler avec "en tant que."
**Proposed:** "La propriété PublicSchema `preferred_name` est alignée avec `alternateName` de schema.org en tant que `broadMatch`, et non `exactMatch`."
**Rationale:** "Est alignée avec [...] en tant que" reproduit la structure technique sans le calque "correspond comme."

---

## related-standards.md

**Overall impression:** Ce fichier est le plus soigné des cinq. La prose est naturelle, les passages argumentatifs se lisent bien. On relève trois points ponctuels à corriger.

### Flagged passages

**Line 3 — Current:** "Il est conçu pour compléter chacune d'elles, non pour leur faire concurrence."
**Issue:** Très bon rendu, mais "faire concurrence" peut être allégé. "Concurrencer" est plus courant et plus direct dans ce registre.
**Proposed:** "Il est conçu pour compléter chacune d'elles, non pour les concurrencer."
**Rationale:** "Concurrencer" (verbe) est plus économique que la locution "faire concurrence à." Changement mineur, purement stylistique.

**Line 26 — Current:** "Cependant, les Vocabulaires de base de l'UE couvrent l'identité et le catalogage des services, pas le cycle de vie de la prestation (inscription, droit, paiement, réclamation)."
**Issue:** "Le droit" seul est ambigu : cela peut désigner le droit au sens juridique général. L'anglais dit "entitlement."
**Proposed:** "Cependant, les Vocabulaires de base de l'UE couvrent l'identité et le catalogage des services, pas le cycle de vie de la prestation (inscription, droits à prestations, paiement, réclamation)."
**Rationale:** "Droits à prestations" est plus précis pour "entitlement" dans le contexte de la protection sociale.

**Line 30 — Current:** "GovStack manque explicitement d'une couche sémantique transversale, ce qui est la lacune que comble PublicSchema."
**Issue:** "Manque explicitement" est une tournure bizarre. L'anglais "explicitly lacks" signifie que ce manque est reconnu et documenté dans les spécifications GovStack, pas que GovStack manque de façon explicite de quelque chose. La nuance est importante.
**Proposed:** "Les spécifications GovStack reconnaissent explicitement l'absence d'une couche sémantique transversale, ce qui est la lacune que comble PublicSchema."
**Rationale:** "Reconnaissent explicitement l'absence" rend fidèlement le sens : ce n'est pas un oubli, c'est un manque reconnu. "Manque explicitement" est une locution contradictoire en français.

**Line 46 — Current:** "Les spécifications connexes comprennent SD-JWT VC pour la divulgation sélective et OpenID4VCI/VP pour l'émission et la présentation d'attestations."
**Issue:** "Comprennent" est une traduction de "include" qui fonctionne, mais est légèrement formel. "Incluent" serait plus direct et cohérent avec le registre du document.
**Proposed:** "Les spécifications connexes incluent SD-JWT VC pour la divulgation sélective et OpenID4VCI/VP pour l'émission et la présentation d'attestations."
**Rationale:** "Comprennent" en français peut suggérer "impliquent" ou "englobent." "Incluent" est plus précis pour "include."

---

## selective-disclosure.md

**Overall impression:** La traduction est solide, particulièrement dans les parties techniques (structure des types d'attestation, payload SD-JWT). On relève quelques calques dans les passages argumentatifs et des formulations alourdies dans le guide d'implémentation.

### Flagged passages

**Line 5 — Current:** "Les attestations PublicSchema sont conçues pour être utilisées avec SD-JWT VC (attestations vérifiables à divulgation sélective JWT), permettant aux détenteurs de ne révéler que les affirmations nécessaires à une interaction spécifique."
**Issue:** La parenthèse "(attestations vérifiables à divulgation sélective JWT)" est une glose de "SD-JWT VC" qui risque de dérouter : "JWT" est un sigle technique et ne se traduit pas. L'expansion telle quelle mêle français et sigle de façon inégale.
**Proposed:** "Les attestations PublicSchema sont conçues pour être utilisées avec SD-JWT VC, un format d'attestations vérifiables à divulgation sélective, permettant aux détenteurs de ne révéler que les affirmations nécessaires à une interaction spécifique."
**Rationale:** Reformuler en apposition ("un format d'attestations vérifiables à divulgation sélective") est plus lisible et évite de forcer le sigle dans la parenthèse.

**Line 9 — Current:** "Le fait qu'une propriété constitue une donnée personnelle dépend de l'enregistrement dans lequel elle apparaît, pas de la propriété elle-même."
**Issue:** Correct et clair. Mais "l'enregistrement" peut être ambigu entre "une entrée dans une base de données" (record) et "l'acte d'enregistrer quelque chose." Dans ce contexte, "l'enregistrement" désigne un record de données.
**Proposed:** "Le fait qu'une propriété constitue une donnée personnelle dépend du contexte de l'enregistrement dans lequel elle apparaît, pas de la propriété elle-même."
**Rationale:** Ajouter "du contexte de" lève l'ambiguïté et renforce le raisonnement : c'est le contexte d'utilisation qui détermine la classification, pas l'enregistrement en tant qu'objet.

**Line 19 — Current:** "Une attestation vérifiable devrait attester des faits qui restent significatifs dans le temps ("cette personne est éligible"), pas des états de processus qui changent en quelques heures ("cette demande est en cours d'examen")."
**Issue:** "Restent significatifs dans le temps" est un calque de "remain meaningful over time." En français, "perdurent dans le temps" ou "gardent leur sens dans la durée" est plus naturel.
**Proposed:** "Une attestation vérifiable devrait attester des faits qui gardent leur sens dans la durée ("cette personne est éligible"), pas des états de processus qui changent en quelques heures ("cette demande est en cours d'examen")."
**Rationale:** "Gardent leur sens dans la durée" est plus idiomatique. "Significatifs" peut être confondu avec "importants" plutôt qu'"ayant une signification stable."

**Line 21 — Current:** "La signification d'une valeur en brouillon peut changer."
**Issue:** "Une valeur en brouillon" est un calque direct de "a draft value." En français, dans le contexte d'une spécification, on parle de "valeur provisoire" ou "valeur à l'état de projet."
**Proposed:** "La signification d'une valeur provisoire peut évoluer."
**Rationale:** "Valeur provisoire" est plus naturel dans les documents normatifs francophones. "Peut évoluer" est plus précis que "peut changer" pour désigner un changement de définition de spécification.

**Line 95 — Current:** "Les champs post-remboursement (redemption_date, redeemed_by) permettent l'audit sans nécessiter une nouvelle présentation des affirmations d'identité."
**Issue:** "Sans nécessiter une nouvelle présentation" est un calque de "without requiring re-presentation." En français, le terme technique est "sans nouvelle présentation" ou "sans devoir re-présenter l'attestation."
**Proposed:** "Les champs post-remboursement (redemption_date, redeemed_by) permettent l'audit sans nouvelle présentation des affirmations d'identité."
**Rationale:** "Sans nécessiter une nouvelle présentation" contient un verbe de modalité superflu. "Sans nouvelle présentation" est plus direct et plus usuel dans les textes normatifs.

**Line 113 — Current:** "Note : les droits par cycle sont de courte durée, donc la rotation des attestations est fréquente ; `document_expiry_date` contrôle la validité de la VC indépendamment de la période de couverture."
**Issue:** "Les droits par cycle" est ambigu. "Par cycle" traduit "per-cycle" (entitlements issued per payment cycle), ce qui n'est pas immédiatement clair en français. "De courte durée" est correct mais "à durée de vie limitée" est plus technique et précis.
**Proposed:** "Note : les droits émis à chaque cycle de paiement ont une durée de vie limitée, ce qui implique un renouvellement fréquent des attestations ; `document_expiry_date` contrôle la validité de la VC indépendamment de la période de couverture."
**Rationale:** "Émis à chaque cycle de paiement" explicite la périodicité. "Durée de vie limitée" est plus précis. "Renouvellement fréquent" est plus idiomatique que "rotation fréquente" dans ce contexte.

**Line 155 — Current:** "Note : les schémas d'attestation PublicSchema utilisent exclusivement le format SD-JWT VC. Les charges utiles SD-JWT VC utilisent `vct` (type d'attestation vérifiable) au lieu du `@context` et des tableaux `type` du W3C VCDM."
**Issue:** "Type d'attestation vérifiable" est une glose de "verifiable credential type" qui est correcte, mais l'abréviation standard en français serait "type d'attestation" sans "vérifiable" puisque le contexte SD-JWT VC le rend évident.
**Proposed:** "Note : les schémas d'attestation PublicSchema utilisent exclusivement le format SD-JWT VC. Les charges utiles SD-JWT VC utilisent `vct` (type d'attestation) au lieu du `@context` et des tableaux `type` du W3C VCDM."
**Rationale:** Allègement mineur, cohérent avec la convention d'éviter les répétitions inutiles du mot "vérifiable" une fois que le contexte le rend implicite.

**Line 161 — Current:** "Les implémenteurs doivent évaluer chaque déploiement et appliquer des protections selon que les données, dans ce contexte, identifient ou concernent une personne physique."
**Issue:** Correct et clair. Le terme "implémenteurs" est un anglicisme courant dans le domaine technique francophone. Il est acceptable mais "équipes de mise en oeuvre" ou "responsables de mise en oeuvre" est plus neutre pour un public international.
**Proposed:** "Les équipes de mise en oeuvre doivent évaluer chaque déploiement et appliquer des protections selon que les données, dans ce contexte, identifient ou concernent une personne physique."
**Rationale:** "Implémenteurs" est compris par les techniciens mais peut paraître jargonneux pour les praticiens de politique. "Équipes de mise en oeuvre" est internationalement neutre et couvre à la fois les équipes techniques et opérationnelles.

**Line 171 — Current:** "Les émetteurs doivent consulter les définitions de types d'attestation ci-dessus lors de la construction de SD-JWT VC."
**Issue:** "Lors de la construction de SD-JWT VC" est un calque de "when constructing SD-JWT VCs." En français, "lors de l'émission de SD-JWT VC" ou "au moment de produire des SD-JWT VC" est plus naturel.
**Proposed:** "Les émetteurs doivent consulter les définitions de types d'attestation ci-dessus au moment de produire des SD-JWT VC."
**Rationale:** "Produire des SD-JWT VC" est plus naturel que "la construction de SD-JWT VC" qui calque la métaphore de construction anglaise.

**Line 172 — Current:** "Les affirmations listées comme "toujours divulguées" apparaissent en clair ; les affirmations "sélectivement divulgables" vont dans `_sd`."
**Issue:** "Apparaissent en clair" est une traduction correcte, mais "sont transmises en clair" ou "figurent en clair" est plus précis dans un contexte de cryptographie/attestations.
**Proposed:** "Les affirmations listées comme "toujours divulguées" figurent en clair dans la charge utile ; les affirmations "sélectivement divulgables" vont dans `_sd`."
**Rationale:** "Figurent en clair dans la charge utile" précise le contexte technique et évite l'ambiguïté d'"apparaissent."

**Line 173 — Current:** "Les détenteurs (applications de portefeuille) doivent présenter une interface de sélection de divulgation distinguant les affirmations toujours divulguées des affirmations sélectivement divulgables."
**Issue:** "Interface de sélection de divulgation" est un calque de "disclosure selection UI." En français, "interface de sélection des informations à divulguer" ou simplement "interface de divulgation" est plus naturel.
**Proposed:** "Les détenteurs (applications de portefeuille) doivent proposer une interface permettant à l'utilisateur de choisir quelles affirmations divulguer, en distinguant les affirmations toujours visibles des affirmations optionnelles."
**Rationale:** La reformulation explicite l'enjeu (l'utilisateur choisit) plutôt que de nommer l'interface abstraitement. "Toujours visibles" et "optionnelles" sont plus parlants pour les concepteurs d'applications que "toujours divulguées / sélectivement divulgables."

**Line 175 — Current:** "En cas de doute, optez par défaut pour la divulgation sélective afin de favoriser la protection de la vie privée."
**Issue:** Correct, mais "favoriser la protection de la vie privée" est un peu timide pour ce qui est en fait un principe de minimisation des données. "Par précaution" ou "par principe de minimisation des données" est plus ancré dans la terminologie RGPD/protection des données qui sera familière au public.
**Proposed:** "En cas de doute, privilégiez la divulgation sélective par précaution, conformément au principe de minimisation des données."
**Rationale:** "Par précaution, conformément au principe de minimisation des données" ancre le conseil dans un référentiel normatif reconnu par le public cible (responsables de protection sociale et informatique dans des pays souvent liés au RGPD ou à des lois similaires).
