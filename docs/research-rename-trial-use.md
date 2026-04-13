# Research: Rename `trial-use` maturity to `candidate`

Date: 2026-04-13. Scope: enumerate every touchpoint affected by renaming the middle maturity level from `trial-use` (FHIR-derived) to `candidate` (W3C-style).

## Naming summary

| Surface | Current | Proposed |
|---|---|---|
| Internal code (YAML/JSON enum) | `trial-use` | `candidate` |
| Display label (UI, prose) | "trial use" / "Trial use" | "Candidate" |
| CSS class / token | `badge-trial-use`, `--color-trial-use`, `--color-trial-use-bg` | `badge-candidate`, `--color-candidate`, `--color-candidate-bg` |
| FR display label | "usage d'essai" (currently absent) | "Candidat" |
| ES display label | "uso de prueba" (currently absent) | "Candidato" |

The visual treatment (amber palette: `#92400e` text on `#fef3c7` background) is fine to keep. Only labels and identifiers change.

## Touchpoint inventory

### 1. Canonical schemas (4 files, mechanical)

The enum is defined in four JSON Schema files. Update the enum array in each:

- `build/schemas/meta.schema.json:21`
- `build/schemas/concept.schema.json:16`
- `build/schemas/vocabulary.schema.json:16`
- `build/schemas/property.schema.json:16`

### 2. Schema data: YAML files (133 files, mechanical)

133 YAML files contain `maturity: trial-use`. Distribution:

- `schema/concepts/*.yaml`: 14 files
- `schema/properties/*.yaml`: 100+ files
- `schema/vocabularies/**/*.yaml`: ~19 files

Single sed-style find-and-replace on the literal string `maturity: trial-use` → `maturity: candidate` is sufficient. No structural changes.

### 3. Build pipeline (2 files)

- `build/check_translations.py:44` — `MATURITY_REQUIRES_TRANSLATION = ("trial-use", "stable")`. Update tuple entry `"trial-use"` → `"candidate"`.
  - **Pre-existing bug found:** the second tuple entry `"stable"` does not match the enum (which is `normative`). This means the translation gate currently never fires for normative entities. Worth fixing in the same pass: `("candidate", "normative")`.
- `build/check_translations.py:16` — docstring mentions "trial-use or stable". Update to "candidate or normative".
- `build/validate.py:89` — comment mentions "trial-use or normative". Update.

### 4. Site (TypeScript / Astro / CSS)

- `site/src/styles/global.css:50-51, 616` — CSS custom properties and badge class. Rename token + class.
- `site/src/components/pages/ReferencesPage.astro:384-385` — references the CSS variables.
- `site/src/components/pages/ConceptsIndex.astro:16`
- `site/src/components/pages/PropertiesIndex.astro:15`
- `site/src/components/pages/VocabIndex.astro:16`
- `site/src/components/pages/HomePage.astro:17`
  - All four define `const maturityRank: Record<string, number> = { normative: 0, "trial-use": 1, draft: 2 };` for sort order. Rename the key.

No dedicated `MaturityBadge` component exists; badge rendering is inline (`badge badge-{maturity}`). Renaming the data value automatically renames the class, so the only manual CSS edits are the variable + class declarations in `global.css`.

### 5. Diagram (1 file)

- `site/public/images/versioning-axes.svg:27,35` — two `<text>` nodes display "trial use" inside the diagram. Update to "candidate". Color is fine.

### 6. Documentation (5 files, prose)

- `docs/versioning-and-maturity.md` — table row, body prose, multiple references. Largest prose update. Approx. 4 occurrences.
- `docs/schema-design.md` — 2 references in name-stability prose.
- `docs/vocabulary-design.md` — 1 reference ("must be resolved before trial use").
- `docs/selective-disclosure.md` — 1 reference (gate for credential issuance).
- `docs/meta-namespace.md` — 1 reference (matched on `trial_use`, may be a code sample).

### 7. ADRs (3 files, prose)

- `decisions/002-maturity-model.md` — defines the term. Two options:
  - **Option A:** edit ADR-002 in place with an "Amended by ADR-006" note (consistent with how ADR-005 amends ADR-002).
  - **Option B:** keep ADR-002 historical (it documents what was decided at the time), write a new ADR-006 ("Rename trial-use to candidate") that captures the rationale and supersedes the naming.
  - **Recommend Option B.** ADR-002 is "Accepted" and reflects a decision made at a point in time. A new ADR documents the rename rationale (W3C convention, translation, trajectory framing) without rewriting history.
- `decisions/004-naming-conventions.md:20` — passing reference ("once a name is published at trial-use or normative"). Update.
- `decisions/005-event-identifier-split.md:23,49` — references the trial-use audit and trial-use entities. Update.

### 8. Audit artifacts (2 files, filenames + content)

- `docs/trial-use-audit-decisions.md` — 6 occurrences in body.
- `docs/trial-use-audit-findings.md` — 4 occurrences in body, including header line "Audit date: 2026-04-12. Scope: 14 trial-use concepts...".

**Recommendation: keep the filenames as `trial-use-audit-*.md`.** These document an audit conducted under that name. Renaming the files would obscure historical context and break any external links. Update body prose where it would mislead a future reader (e.g., "Audit of entities at the level then called *trial-use*, now *candidate*"), but leave filenames alone. This matches how regulatory bodies treat historical document titles.

### 9. Tests (4 files)

- `tests/test_validate.py:289-291, 365-369` — two test methods named `test_trial_use_*`. Rename method names + update `maturity="trial-use"` literals to `"candidate"`.
- `tests/test_check_translations.py:106-142, 262` — three test methods, plus YAML literal in inline test fixtures. Rename + update.
- `tests/test_release.py:21, 66` — release-test fixtures use `"maturity": "trial-use"`. Update.

### 10. Ideas / unmerged (1 file)

- `ideas/maturity-consistency-validator.md` — 7 references in design notes for an unbuilt validator. Update prose.

### 11. Generated artifacts (regenerate, no manual edit)

These are produced by the build pipeline and will refresh automatically once source files change:

- `site/public/vocabulary.json` (~150 occurrences of `"maturity": "trial-use"`)
- `site/public/schemas/credentials/*.schema.json`
- `site/public/Person.csv`, `site/public/crvs/*.csv`
- Any JSON-LD context outputs

`uv run python scripts/build_data.py` regenerates these. Do not edit by hand.

## Migration / backward-compat considerations

Per ADR-005, no external adopters exist yet, and ADR-002 commits to keeping older context versions resolvable rather than maintaining backward-compatible enum values. So:

- **No deprecation shim needed.** Validators can immediately reject `trial-use` and accept only `candidate`.
- **Bump release version.** Per ADR-002, this is a breaking change to the `maturity` enum, so it warrants a minor bump (vocabulary additive but enum value changed). Update `_meta.yaml`.
- **JSON-LD context** does not appear to encode the maturity values themselves, so context versioning is unaffected.

## Open questions

1. **Display capitalization in UI:** "Candidate" or "candidate"? Current badges use lowercase ("trial use", "draft", "normative"). Keeping lowercase is consistent: render as "candidate".
2. **FR/ES translations of the term:** "candidat" / "candidato" (proposed). Confirm with reviewer pool. Where do these labels live? Currently `versioning-axes.svg` and the badge text both render the raw enum value, so there is no translation file to update. If you want localized badge labels, that is a separate (small) feature.
3. **Should the existing `trial-use-audit-*.md` filenames be renamed?** Recommendation above is to keep them (historical artifacts).
4. **Should ADR-002 be edited in place or superseded by a new ADR?** Recommendation above is to write ADR-006 and leave ADR-002 untouched.
5. **The pre-existing bug in `MATURITY_REQUIRES_TRANSLATION` (uses `"stable"` instead of `"normative"`):** fold the fix into this rename, or handle separately?

## Estimated effort

- Mechanical rename: ~5 minutes (one global find-and-replace across YAML + JSON Schema enums + four TS dict keys + CSS vars/classes + SVG text).
- Prose updates (ADRs, docs, audit body text): ~30 minutes of careful editing.
- New ADR-006: ~15 minutes.
- Test renames + build verification: ~15 minutes.
- Regeneration of `site/public/vocabulary.json` etc: automated.

Total: ~1 hour, single PR.

## Suggested next step

If you confirm the recommendations above (keep audit filenames, write new ADR, fix the translation bug in the same pass), I can write a plan with a task checklist before implementing.
