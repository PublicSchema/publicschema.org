"""Generate preview.json: the data source for the site's hover cards.

One JSON file per locale, keyed by the entity's site path:

- Concepts: "/Person", "/sp/Enrollment"
- Properties: "/date_of_birth", "/sp/enrollment_status"
- Vocabularies: "/vocab/iso-3166-countries", "/vocab/sp/enrollment-status"

Each entry carries per-locale metadata the hover card needs to render
without round-tripping to the full vocabulary.json.
"""

from typing import Any

DEFAULT_LOCALES = ("en", "fr", "es")
DEFAULT_LOCALE = "en"

# Per-locale character budget for the truncated definition preview.
# French and Spanish prose averages ~15-20% longer than English for the
# same information density, so their limits are higher to keep roughly
# equivalent information in the card.
LOCALE_EXCERPT_LIMIT: dict[str, int] = {
    "en": 220,
    "fr": 260,
    "es": 260,
}


def truncate_excerpt(text: str, limit: int) -> str:
    """Word-boundary-safe truncation with trailing ellipsis.

    If ``text`` is within ``limit``, returns it unchanged. Otherwise cuts
    at the last word boundary at or before ``limit`` and appends "…".
    Never produces a result that splits a word, except when a single word
    exceeds the limit (hard cut fallback).
    """
    if not text:
        return ""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last_space = cut.rfind(" ")
    if last_space <= 0:
        return cut.rstrip() + "…"
    return cut[:last_space].rstrip() + "…"


def _pick_locale(
    field: dict[str, str] | None,
    locale: str,
    fallback: str = DEFAULT_LOCALE,
) -> tuple[str, str]:
    """Return ``(value, locale_used)``. Falls back to ``fallback`` when missing."""
    if not field:
        return "", locale
    if locale in field and field[locale]:
        return field[locale], locale
    if fallback in field and field[fallback]:
        return field[fallback], fallback
    for candidate in DEFAULT_LOCALES:
        if candidate in field and field[candidate]:
            return field[candidate], candidate
    return "", locale


def _base_entry(
    item: dict[str, Any],
    kind: str,
    locale: str,
) -> dict[str, Any]:
    label, _ = _pick_locale(item.get("label"), locale)
    definition, locale_used = _pick_locale(
        item.get("definition"), locale
    )
    limit = LOCALE_EXCERPT_LIMIT.get(locale, 220)
    return {
        "label": label or item["id"],
        "kind": kind,
        "maturity": item.get("maturity", "draft"),
        "href": item["path"],
        "definition_excerpt": truncate_excerpt(definition, limit),
        "locale_used": locale_used,
    }


def _concept_entry(
    concept: dict[str, Any], locale: str
) -> dict[str, Any]:
    entry = _base_entry(concept, "concept", locale)
    entry["domain"] = concept.get("domain")
    entry["abstract"] = bool(concept.get("abstract", False))
    return entry


def _property_entry(
    prop: dict[str, Any], locale: str
) -> dict[str, Any]:
    entry = _base_entry(prop, "property", locale)
    entry["type"] = prop.get("type", "")
    entry["vocabulary"] = prop.get("vocabulary")
    return entry


def _vocabulary_entry(
    vocab: dict[str, Any], locale: str
) -> dict[str, Any]:
    return _base_entry(vocab, "vocabulary", locale)


def build_preview(
    result: dict[str, Any],
    locales: tuple[str, ...] = DEFAULT_LOCALES,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Produce the preview lookup table.

    Returns a dict keyed by the entity's site path. Each value is a
    per-locale dict whose entries carry label, definition excerpt, kind,
    maturity, href, and kind-specific fields (domain/abstract for
    concepts; type/vocabulary for properties).
    """
    preview: dict[str, dict[str, dict[str, Any]]] = {}

    for concept in result.get("concepts", {}).values():
        key = concept["path"]
        preview[key] = {
            locale: _concept_entry(concept, locale) for locale in locales
        }

    for prop in result.get("properties", {}).values():
        key = prop["path"]
        preview[key] = {
            locale: _property_entry(prop, locale) for locale in locales
        }

    for vocab in result.get("vocabularies", {}).values():
        key = vocab["path"]
        preview[key] = {
            locale: _vocabulary_entry(vocab, locale)
            for locale in locales
        }

    return preview
