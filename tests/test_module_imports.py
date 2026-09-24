"""Each schema module declares the imports that define the terms it uses."""

from pathlib import Path

import pytest
import yaml

SCHEMA = Path(__file__).resolve().parents[1] / "schema"
LINKML_TYPES = {
    "string", "integer", "float", "double", "boolean", "decimal", "date", "datetime", "time",
    "date_or_datetime", "uri", "uriorcurie", "curie", "ncname",
}
MODULES = {
    path.relative_to(SCHEMA).with_suffix("").as_posix(): yaml.safe_load(path.read_text()) or {}
    for path in SCHEMA.rglob("*.yaml")
}


def imported(module, seen=None):
    seen = set() if seen is None else seen
    if module in seen or module not in MODULES:
        return seen
    seen.add(module)
    for name in MODULES[module].get("imports") or []:
        if not name.startswith("linkml:"):
            sibling = (Path(module).parent / name).as_posix()
            imported(sibling if sibling in MODULES else name, seen)
    return seen


def references(document):
    for name, body in (document.get("classes") or {}).items():
        body = body or {}
        for ref in [body.get("is_a"), *(body.get("mixins") or []), *(body.get("slots") or [])]:
            yield name, ref
        for slot, usage in (body.get("slot_usage") or {}).items():
            yield name, slot
            yield name, (usage or {}).get("range")
    for name, body in (document.get("slots") or {}).items():
        body = body or {}
        yield name, body.get("range")
        yield name, body.get("is_a")
        for option in body.get("any_of") or []:
            yield name, option.get("range")


@pytest.mark.parametrize("module", sorted(m for m, d in MODULES.items() if d.get("classes") or d.get("slots")))
def test_module_resolves_its_terms_through_its_own_imports(module):
    defined = set(LINKML_TYPES)
    for name in imported(module):
        for section in ("classes", "slots", "enums", "types"):
            defined |= set(MODULES[name].get(section) or {})
    unresolved = {(term, ref) for term, ref in references(MODULES[module]) if ref and ref not in defined}
    assert unresolved == set()
