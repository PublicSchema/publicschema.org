# French translation review - TypesContent

Scope: TypesContent.fr.astro, the Types reference page listing string, integer, decimal, boolean, date, datetime, uri, and geojson_geometry data types.

---

## Flags

---

**Flag 1**

- **Line (approx):** 5
- **Current:** `Une séquence de caractères Unicode.`
- **Issue:** Technically accurate but "séquence de caractères" is slightly generic; the established francophone computing term is "chaîne de caractères", which is what ISO and French technical literature use for the `string` type specifically.
- **Proposed:** `Une chaîne de caractères Unicode.`
- **Rationale:** "Chaîne de caractères" is the standard French term for the `string` type in computing (used by ISO/IEC standards in French, AFNOR, and French-language programming documentation); "séquence" is not wrong but is not the established term and may confuse readers expecting the canonical vocabulary.

---

**Flag 2**

- **Line (approx):** 16
- **Current:** `Un nombre entier sans composante fractionnaire.`
- **Issue:** "Composante fractionnaire" is a calque of "fractional component" and reads awkwardly in French. The natural French phrasing is "sans partie décimale" or "sans décimale".
- **Proposed:** `Un nombre entier, sans partie décimale.`
- **Rationale:** "Partie décimale" is the standard French mathematical term (as opposed to "partie entière") and is immediately understood by any French-speaking reader. "Composante fractionnaire" is not natural French and has no grounding in French mathematical or technical documentation.

---

**Flag 3**

- **Line (approx):** 19
- **Current:** `Entier signé (sans virgule décimale)`
- **Issue:** "Virgule décimale" is technically valid but inconsistent: the Format cell uses "virgule décimale" while the description above uses "composante fractionnaire" for the same concept. Beyond the inconsistency, "virgule décimale" is France-centric (it assumes the comma as decimal separator, which is the French convention, but the schema stores values with a period). "Point décimal" or simply "sans décimale" is clearer for an internationally neutral audience.
- **Proposed:** `Entier signé (sans décimale)`
- **Rationale:** Removes the locale-specific "virgule" reference, eliminates the inconsistency with the body text, and matches the neutral register requested.

---

**Flag 4**

- **Line (approx):** 28
- **Current:** `Une valeur numérique pouvant inclure une composante fractionnaire.`
- **Issue:** Same calque issue as Flag 2: "composante fractionnaire" does not exist as a set phrase in French technical writing. It also creates an inconsistency with the Format row on the same entry ("Nombre décimal"), which uses the correct term.
- **Proposed:** `Une valeur numérique pouvant comporter une partie décimale.`
- **Rationale:** "Comporter une partie décimale" is the natural French phrasing and aligns with the Format row ("Nombre décimal") already in the file.

---

**Flag 5**

- **Line (approx):** 41
- **Current:** `Une valeur vrai/faux.`
- **Issue:** "Vrai/faux" is a literal calque of "true/false". In French technical writing, the standard phrasing is "Une valeur booléenne (vrai ou faux)" or simply "Une valeur à deux états : vrai ou faux." The slash notation is not standard in French prose.
- **Proposed:** `Une valeur booléenne : vrai ou faux.`
- **Rationale:** The slash construct is an English typographic convention in prose; French uses "ou" in running text. Adding "booléenne" also helps orient readers who encounter the English type name `boolean` and need the French semantic anchor.

---

**Flag 6**

- **Line (approx):** 52
- **Current:** `Une date calendaire sans composante horaire.`
- **Issue:** "Composante horaire" is again a calque of "time-of-day component". The established French phrase for this distinction is "sans indication d'heure" or "sans heure associée".
- **Proposed:** `Une date du calendrier, sans indication d'heure.`
- **Rationale:** "Sans indication d'heure" is natural French and is the form used in French-language ISO 8601 documentation. "Composante horaire" will read as translated rather than written in French.

---

**Flag 7**

- **Line (approx):** 64
- **Current:** `Une date combinée avec une composante horaire.`
- **Issue:** Same pattern as Flag 6: "composante horaire" is a direct calque. Additionally, "combinée avec" is a somewhat mechanical construction; "assortie d'une heure" or "accompagnée d'une indication d'heure" is more idiomatic.
- **Proposed:** `Une date assortie d'une indication d'heure.`
- **Rationale:** Resolves the recurring calque and is idiomatic French, consistent with the fix proposed in Flag 6.

---

**Flag 8**

- **Line (approx):** 70
- **Current:** `Toujours inclure un décalage de fuseau horaire ou utiliser UTC (<code>Z</code>). Les heures locales sans indication de fuseau sont ambiguës.`
- **Issue:** The first sentence is a bare infinitive imperative ("Toujours inclure..."), which is grammatically acceptable in French instructional text but reads as mechanically translated. The more natural imperative form uses "Inclure toujours" or, better, a proper imperative: "Toujours inclure" works in notes/labels but sounds clipped. More importantly, "décalage de fuseau horaire" is a correct but verbose calque of "timezone offset"; the concise standard French term is "décalage horaire" (the "de fuseau" is redundant once you have "horaire").
- **Proposed:** `Toujours inclure un décalage horaire ou utiliser UTC (<code>Z</code>). Les heures locales sans fuseau horaire indiqué sont ambiguës.`
- **Rationale:** "Décalage horaire" is the standard French term (it is also how IETF RFC translations render "UTC offset"). The second sentence is lightly reworded to avoid repeating "indication de fuseau" while keeping the meaning.

---

**Flag 9**

- **Line (approx):** 58
- **Current:** `Les systèmes qui ne connaissent que l'année de naissance peuvent utiliser <code>YYYY</code> ou <code>YYYY-01-01</code> avec un qualificatif de précision. Le vocabulaire ne prescrit pas quelle approche utiliser.`
- **Issue:** "Qualificatif de précision" is a literal calque of "precision qualifier" and has no currency in French technical writing. The natural French equivalent is "indicateur de précision" or "qualifiant de précision"; however, since this is a schema-specific term, the clearest option is to describe the function rather than coin a term: "un indicateur de la précision connue".
- **Proposed:** `Les systèmes qui ne disposent que de l'année de naissance peuvent utiliser <code>YYYY</code> ou <code>YYYY-01-01</code> avec un indicateur de précision. Le vocabulaire ne prescrit pas l'approche à retenir.`
- **Rationale:** "Ne disposent que de" is more natural than "ne connaissent que" in a systems/data context. "Indicateur de précision" is the closest established French term. "L'approche à retenir" avoids the calqued "quelle approche utiliser" (which echoes "which approach to use" word-for-word).

---

**Flag 10**

- **Line (approx):** 77
- **Current:** `Utilisé pour des références stables à des enregistrements ou ressources externes.`
- **Issue:** "Enregistrements" is a valid translation of "records" in a database sense, but in the context of URI-referenced external resources, "ressources" already covers both cases, and "enregistrements" risks confusion with audio/video recordings or registry entries. The English source says "external records or resources", where "records" means data records. The French should preserve that meaning without ambiguity.
- **Proposed:** `Utilisé pour référencer de façon stable des enregistrements ou ressources externes.`
- **Rationale:** The restructured sentence is more natural ("référencer de façon stable" vs "pour des références stables à"), though the core term "enregistrements" is kept since it is the correct meaning here. The original phrasing "pour des références stables à des X" is a nominal construction that sounds translated; turning the noun back into a verb improves flow.

---

**Flag 11**

- **Line (approx):** 89
- **Current:** `Une forme géographique exprimée sous la forme d'un objet Geometry <a ...>GeoJSON</a>.`
- **Issue:** "Exprimée sous la forme d'un objet Geometry GeoJSON" has a word-order problem: in French, the brand/standard name "GeoJSON" should precede "Geometry" when "Geometry" is a technical class name subordinate to GeoJSON, not an independent French word. The phrase also contains "sous la forme d'un", which is a verbose calque of "as a". A more natural option is "représentée par un objet GeoJSON Geometry".
- **Proposed:** `Une forme géographique représentée par un objet GeoJSON Geometry.`
- **Rationale:** "Représentée par" is more idiomatic than "exprimée sous la forme de" in a type definition context. Moving "GeoJSON" before "Geometry" mirrors how the specification itself orders the name in all its official French-language materials.

---

## Consistency notes

The following table row labels are rendered inconsistently across the page. All other label-type terms ("Type JSON", "Format", "Exemples", "Schéma JSON") are consistent; only these two have minor issues worth noting:

- "Remarque" (used for `decimal`, `date`, `datetime`) vs nothing in other sections: consistent within the sections that have notes; no issue.
- "Exemple" (singular, geojson_geometry) vs "Exemples" (plural, other sections): this mirrors the English source ("Example" vs "Examples"), so it is not a translation error, but editors may want to verify that the English inconsistency was intentional.

---

## Overall impression

The translation is largely accurate and covers the content faithfully. The main recurring weakness is a pattern of nominal calques ("composante fractionnaire", "composante horaire", "qualificatif de précision") that preserve English syntactic structure instead of using established French technical vocabulary or natural French constructions. A secondary issue is one locale-specific term ("virgule décimale") that assumes the French decimal comma convention in a schema that uses decimal points. With the eleven targeted corrections above, the text would read as natively authored French technical documentation suitable for a broad international francophone audience.
