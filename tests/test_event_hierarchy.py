"""Invariants for Enrollment and Grievance as Event subtypes.

Event is the abstract supertype for timestamped occurrence records. Enrollment
(the act of registering a beneficiary) and Grievance (a filing) are both events
and must declare Event as their supertype. The Event concept must list them as
subtypes to keep the hierarchy symmetric.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import PurePath

from build.linkml_reader import load_raw_from_linkml
from tests.conftest import SCHEMA_DIR

CONCEPTS = PurePath("concepts")


@lru_cache(maxsize=1)
def _raws():
    return load_raw_from_linkml(SCHEMA_DIR)


def _kebab_to_pascal(stem: str) -> str:
    return "".join(p.capitalize() for p in stem.split("-"))


def _load(path: PurePath):
    target = _kebab_to_pascal(path.stem)
    for key, concept in _raws()["concepts"].items():
        if key.split("/")[-1] == target:
            return concept
    raise KeyError(f"{path} not found in re-projected LinkML schema")


class TestEnrollmentAndGrievanceAreEvents:
    def test_enrollment_supertype_is_event(self):
        data = _load(CONCEPTS / "enrollment.yaml")
        assert data["supertypes"] == ["Event"]

    def test_grievance_supertype_is_event(self):
        data = _load(CONCEPTS / "grievance.yaml")
        assert data["supertypes"] == ["Event"]

    def test_event_lists_enrollment_as_subtype(self):
        event = _load(CONCEPTS / "event.yaml")
        assert "sp/Enrollment" in event["subtypes"]

    def test_event_lists_grievance_as_subtype(self):
        event = _load(CONCEPTS / "event.yaml")
        assert "sp/Grievance" in event["subtypes"]
