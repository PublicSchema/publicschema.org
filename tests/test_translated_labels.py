"""Translated labels identify one term of each kind, as the English titles do."""

from collections import defaultdict
from pathlib import Path

import pytest
import yaml

SCHEMA = Path(__file__).resolve().parents[1] / "schema"

# Published pairs that already share a translated label. New terms must not join this list.
PUBLISHED_SHARED_LABELS = {
    frozenset({"CrvsPerson", "Person"}),
    frozenset({"scoring", "scoring_method"}),
    frozenset({"replaces", "supersedes_ref"}),
    frozenset({"recipient", "beneficiary"}),
    frozenset({"cognition_remembering_frequency", "remembering_frequency"}),
}


def shared_labels(key):
    names = defaultdict(set)
    for path in SCHEMA.glob("*.yaml"):
        document = yaml.safe_load(path.read_text()) or {}
        for kind in ("classes", "slots", "enums"):
            for name, body in (document.get(kind) or {}).items():
                label = ((body or {}).get("annotations") or {}).get(key)
                if label:
                    names[(kind, label.strip().casefold())].add(name)
    return {frozenset(group) for group in names.values() if len(group) > 1}


@pytest.mark.parametrize("key", ["label_fr", "label_es"])
def test_no_two_terms_of_a_kind_share_a_translated_label(key):
    assert shared_labels(key) - PUBLISHED_SHARED_LABELS == set()
