"""Invariants for Enrollment and Grievance as Event subtypes.

Event is the abstract supertype for timestamped occurrence records. Enrollment
(the act of registering a beneficiary) and Grievance (a filing) are both events
and must declare Event as their supertype. The Event concept must list them as
subtypes to keep the hierarchy symmetric.
"""
from __future__ import annotations

import yaml

from tests.conftest import SCHEMA_DIR

CONCEPTS = SCHEMA_DIR / "concepts"


def _load(path):
    with path.open() as f:
        return yaml.safe_load(f)


class TestEnrollmentAndGrievanceAreEvents:
    def test_enrollment_supertype_is_event(self):
        data = _load(CONCEPTS / "enrollment.yaml")
        assert data["supertypes"] == ["Event"]

    def test_grievance_supertype_is_event(self):
        data = _load(CONCEPTS / "grievance.yaml")
        assert data["supertypes"] == ["Event"]

    def test_event_lists_enrollment_as_subtype(self):
        event = _load(CONCEPTS / "event.yaml")
        assert "Enrollment" in event["subtypes"]

    def test_event_lists_grievance_as_subtype(self):
        event = _load(CONCEPTS / "event.yaml")
        assert "Grievance" in event["subtypes"]
