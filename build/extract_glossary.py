"""Extract a translation glossary from schema YAML and UI term seeds.

Produces translations/glossary.yaml with two sections:

- domain_terms: auto-extracted from schema/concepts/, schema/properties/, and
  schema/vocabularies/. Entries mirror whatever label/definition translations
  the YAML files already provide. The script overwrites this section on every
  run, so hand edits to domain_terms will be lost; edit the source YAML
  instead.

- ui_terms: manually curated UI labels (buttons, nav, status text). Preserved
  across runs. Seeded from the OpenSPP glossary plus overrides/additions
  listed in this script.

Run from the repo root with `uv run python -m build.extract_glossary`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from build.loader import load_yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"
GLOSSARY_PATH = PROJECT_ROOT / "translations" / "glossary.yaml"

# Optional path to an OpenSPP glossary JSON file, used to seed UI term
# translations. Set via the OPENSPP_GLOSSARY_PATH environment variable.
# When unset or the file does not exist, the script skips OpenSPP seeding.
OPENSPP_GLOSSARY = Path(os.environ.get("OPENSPP_GLOSSARY_PATH", "")
                        ) if os.environ.get("OPENSPP_GLOSSARY_PATH") else None

LOCALES = ("en", "fr", "es")

# UI terms that PublicSchema uses. If a key exists in the OpenSPP glossary,
# we seed with its translations; otherwise the entry is created with only the
# English string filled in (fr/es left empty for a human to complete).
#
# Add new UI terms here. If a term overlaps with OpenSPP but we want a
# different translation, put the override in UI_OVERRIDES below.
UI_SEED_KEYS: dict[str, dict[str, str]] = {
    "search": {"en": "Search", "context": "Search action/button label"},
    "download": {"en": "Download", "context": "Download action/button label"},
    "home": {"en": "Home", "context": "Homepage breadcrumb/nav label"},
    "about": {"en": "About", "context": "About page nav label"},
    "docs": {"en": "Docs", "context": "Documentation nav label"},
    "menu": {"en": "Menu", "context": "Mobile menu label"},
    "concept": {"en": "Concept", "context": "Schema entity type"},
    "property": {"en": "Property", "context": "Schema attribute type"},
    "vocabulary": {"en": "Vocabulary", "context": "Controlled value set"},
    "system": {"en": "System", "context": "External mapped delivery system"},
    "definition": {"en": "Definition", "context": "Table column header"},
    "label": {"en": "Label", "context": "Table column header"},
    "code": {"en": "Code", "context": "Table column header (vocabulary value code)"},
    "values": {"en": "Values", "context": "Section heading on vocabulary pages"},
    "maturity": {"en": "Maturity", "context": "Lifecycle status badge label"},
    "type": {"en": "Type", "context": "Property data type column"},
    "cardinality": {"en": "Cardinality", "context": "Property multiplicity label"},
    "standard": {"en": "Standard", "context": "External standard reference"},
    "match": {"en": "Match", "context": "Mapping match strength"},
    "coverage": {"en": "Coverage", "context": "System mapping coverage indicator"},
    "gaps": {"en": "Gaps", "context": "System mapping coverage gaps"},
    "status": {"en": "Status", "context": "Review/mapping status"},
    "submit": {"en": "Submit", "context": "Form submit action"},
    "cancel": {"en": "Cancel", "context": "Cancel action"},
    "dismiss": {"en": "Dismiss", "context": "Banner/notification dismiss action"},
    "no_results": {"en": "No results", "context": "Search empty-state"},
    "loading": {"en": "Loading", "context": "Async loading indicator"},
}

# Explicit PublicSchema translations. OpenSPP only covers a handful of
# generic UI terms (search, download, cancel), so most of these are filled
# here. Keep these short, neutral, and consistent with the ui.ts dictionary.
UI_OVERRIDES: dict[str, dict[str, str]] = {
    "home": {"fr": "Accueil", "es": "Inicio"},
    "about": {"fr": "À propos", "es": "Acerca de"},
    "docs": {"fr": "Documentation", "es": "Documentación"},
    "menu": {"fr": "Menu", "es": "Menú"},
    "concept": {"fr": "Concept", "es": "Concepto"},
    "property": {"fr": "Propriété", "es": "Propiedad"},
    "vocabulary": {"fr": "Vocabulaire", "es": "Vocabulario"},
    "system": {"fr": "Système", "es": "Sistema"},
    "definition": {"fr": "Définition", "es": "Definición"},
    "label": {"fr": "Libellé", "es": "Etiqueta"},
    "code": {"fr": "Code", "es": "Código"},
    "values": {"fr": "Valeurs", "es": "Valores"},
    "maturity": {"fr": "Maturité", "es": "Madurez"},
    "cardinality": {"fr": "Cardinalité", "es": "Cardinalidad"},
    "standard": {"fr": "Norme", "es": "Norma"},
    "match": {"fr": "Correspondance", "es": "Correspondencia"},
    "coverage": {"fr": "Couverture", "es": "Cobertura"},
    "gaps": {"fr": "Lacunes", "es": "Brechas"},
    "status": {"fr": "Statut", "es": "Estado"},
    "submit": {"fr": "Envoyer", "es": "Enviar"},
    "cancel": {"fr": "Annuler", "es": "Cancelar"},
    "dismiss": {"fr": "Fermer", "es": "Cerrar"},
    "no_results": {"fr": "Aucun résultat", "es": "Sin resultados"},
    "loading": {"fr": "Chargement", "es": "Cargando"},
}


def _load_all_yaml_with_paths(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    items = []
    for p in sorted(directory.rglob("*.yaml")):
        data = load_yaml(p)
        if "id" in data:
            data["_source_path"] = str(p.relative_to(PROJECT_ROOT))
            items.append(data)
    return items


def _pick_labels(entry: dict) -> dict[str, str]:
    """Return a {locale: label} map for a schema entry.

    Concepts and properties do not have structured labels (the id doubles as
    the canonical label), so we just use the id for all locales. Vocabulary
    values do have structured labels; handled separately.
    """
    return {loc: entry["id"] for loc in LOCALES}


def _pick_definition(entry: dict) -> dict[str, str]:
    definition = entry.get("definition") or {}
    return {loc: (definition.get(loc) or "").strip() for loc in LOCALES}


def _extract_domain_terms() -> list[dict]:
    """Extract concepts, properties, vocabularies, and vocabulary values."""
    terms: list[dict] = []

    for concept in _load_all_yaml_with_paths(SCHEMA_DIR / "concepts"):
        terms.append(
            {
                "kind": "concept",
                "id": concept["id"],
                "labels": _pick_labels(concept),
                "definition": _pick_definition(concept),
                "source": concept["_source_path"],
            }
        )

    for prop in _load_all_yaml_with_paths(SCHEMA_DIR / "properties"):
        terms.append(
            {
                "kind": "property",
                "id": prop["id"],
                "labels": _pick_labels(prop),
                "definition": _pick_definition(prop),
                "source": prop["_source_path"],
            }
        )

    for vocab in _load_all_yaml_with_paths(SCHEMA_DIR / "vocabularies"):
        terms.append(
            {
                "kind": "vocabulary",
                "id": vocab["id"],
                "labels": _pick_labels(vocab),
                "definition": _pick_definition(vocab),
                "source": vocab["_source_path"],
            }
        )
        for value in vocab.get("values") or []:
            label = value.get("label") or {}
            definition = value.get("definition") or {}
            terms.append(
                {
                    "kind": "vocabulary_value",
                    "id": f"{vocab['id']}/{value['code']}",
                    "labels": {
                        loc: (label.get(loc) or "").strip() for loc in LOCALES
                    },
                    "definition": {
                        loc: (definition.get(loc) or "").strip() for loc in LOCALES
                    },
                    "source": vocab["_source_path"],
                }
            )

    return terms


def _load_openspp_glossary() -> dict[str, Any]:
    if OPENSPP_GLOSSARY is None or not OPENSPP_GLOSSARY.exists():
        return {}
    return json.loads(OPENSPP_GLOSSARY.read_text())


def _openspp_lookup(glossary: dict, key: str) -> dict | None:
    """OpenSPP splits entries across terms, ui_labels, and status_labels."""
    for section in ("terms", "ui_labels", "status_labels"):
        entry = (glossary.get(section) or {}).get(key)
        if entry:
            return entry
    return None


def _build_ui_terms() -> list[dict]:
    openspp = _load_openspp_glossary()
    entries: list[dict] = []
    for key, seed in UI_SEED_KEYS.items():
        source = _openspp_lookup(openspp, key)
        override = UI_OVERRIDES.get(key, {})
        en = override.get("en") or (source or {}).get("en") or seed["en"]
        fr = override.get("fr") or (source or {}).get("fr") or ""
        es = override.get("es") or (source or {}).get("es") or ""
        context = seed.get("context", "")
        if source and not context:
            context = source.get("context", "")
        entries.append(
            {
                "key": key,
                "en": en,
                "fr": fr,
                "es": es,
                "context": context,
            }
        )
    return entries


def _load_existing_ui_terms() -> list[dict]:
    if not GLOSSARY_PATH.exists():
        return []
    data = yaml.safe_load(GLOSSARY_PATH.read_text()) or {}
    return data.get("ui_terms") or []


def _merge_ui_terms(seeded: list[dict], existing: list[dict]) -> list[dict]:
    """Prefer existing translations (hand-curated) over seed defaults."""
    by_key = {item["key"]: item for item in existing if "key" in item}
    merged: list[dict] = []
    for item in seeded:
        prior = by_key.get(item["key"])
        if prior:
            merged.append(
                {
                    "key": item["key"],
                    "en": prior.get("en") or item["en"],
                    "fr": prior.get("fr") or item["fr"],
                    "es": prior.get("es") or item["es"],
                    "context": prior.get("context") or item["context"],
                }
            )
        else:
            merged.append(item)
    # Preserve any hand-added keys not in the seed list.
    seeded_keys = {item["key"] for item in seeded}
    for prior in existing:
        key = prior.get("key")
        if key and key not in seeded_keys:
            merged.append(prior)
    return merged


def build_glossary() -> dict:
    existing_ui = _load_existing_ui_terms()
    ui_terms = _merge_ui_terms(_build_ui_terms(), existing_ui)
    domain_terms = _extract_domain_terms()
    return {
        "_meta": {
            "description": (
                "Translation glossary for PublicSchema. domain_terms is "
                "auto-extracted from schema YAML and overwritten on every "
                "run. ui_terms is hand-curated and preserved across runs."
            ),
            "locales": list(LOCALES),
            "domain_term_count": len(domain_terms),
            "ui_term_count": len(ui_terms),
        },
        "ui_terms": ui_terms,
        "domain_terms": domain_terms,
    }


def write_glossary(data: dict, path: Path = GLOSSARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=100,
        )
    )


def main(argv: list[str]) -> int:
    data = build_glossary()
    write_glossary(data)
    print(
        f"Wrote {GLOSSARY_PATH.relative_to(PROJECT_ROOT)}: "
        f"{data['_meta']['domain_term_count']} domain terms, "
        f"{data['_meta']['ui_term_count']} UI terms."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
