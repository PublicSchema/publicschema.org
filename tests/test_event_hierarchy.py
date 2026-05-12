"""Invariants for Enrollment and Grievance as Event subtypes.

Event is the abstract supertype for timestamped occurrence records. Enrollment
(the act of registering a beneficiary) and Grievance (a filing) are both events
and must declare Event as their supertype. The Event concept must list them as
subtypes to keep the hierarchy symmetric.
"""
from __future__ import annotations

from tests.schema_reader import concept, subtypes_of


class TestEnrollmentAndGrievanceAreEvents:
    def test_enrollment_supertype_is_event(self):
        data = concept("sp/Enrollment")
        assert data["supertypes"] == ["Event"]

    def test_grievance_supertype_is_event(self):
        data = concept("sp/Grievance")
        assert data["supertypes"] == ["Event"]

    def test_event_lists_enrollment_as_subtype(self):
        assert "sp/Enrollment" in subtypes_of("Event")

    def test_event_lists_grievance_as_subtype(self):
        assert "sp/Grievance" in subtypes_of("Event")
