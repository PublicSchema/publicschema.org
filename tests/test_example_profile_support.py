"""The helpers shared by the example submission profiles."""
from datetime import date, datetime

import pytest

from tests.conftest import load_example

support = load_example("shared/profile_support.py")


def test_parse_day_accepts_an_exact_calendar_date():
    assert support.parse_day("2026-02-28", "start_date") == date(2026, 2, 28)


@pytest.mark.parametrize("value,message", [
    ("20260101", "exact YYYY-MM-DD"),
    ("2026-W01-1", "exact YYYY-MM-DD"),
    ("2026-1-01", "exact YYYY-MM-DD"),
    ("2026-01-01T00:00:00Z", "exact YYYY-MM-DD"),
    (" 2026-01-01", "exact YYYY-MM-DD"),
    ("٢٠٢٦-01-01", "exact YYYY-MM-DD"),
    (20260101, "exact YYYY-MM-DD"),
    (None, "exact YYYY-MM-DD"),
    ("2026-02-30", "impossible calendar date"),
])
def test_parse_day_rejects_other_forms_with_a_value_error_naming_the_field(value, message):
    with pytest.raises(ValueError, match=f"^start_date: (expected an )?{message}"):
        support.parse_day(value, "start_date")


@pytest.mark.parametrize("start,end", [
    (date(2026, 1, 1), date(2026, 1, 2)),
    (None, date(2026, 1, 1)),
    (date(2026, 1, 1), None),
    (None, None),
])
def test_known_forward_periods_and_unknown_bounds_pass(start, end):
    support.check_period(start, end)


def test_an_end_on_the_start_day_is_a_one_day_period():
    day = date(2026, 1, 1)
    support.check_period(day, day)


def test_reversed_period_fails():
    with pytest.raises(ValueError, match="ends before it starts"):
        support.check_period(date(2026, 1, 2), date(2026, 1, 1))


def test_period_message_can_name_the_profile_rule():
    with pytest.raises(ValueError, match="^end_date: custom$"):
        support.check_period(date(2026, 1, 2), date(2026, 1, 1), message="end_date: custom")


@pytest.mark.parametrize("start,end", [
    ("2026-01-01", date(2026, 1, 2)),
    (date(2026, 1, 1), 20260102),
    (datetime(2026, 1, 1), date(2026, 1, 2)),
])
def test_period_bounds_must_already_be_calendar_days(start, end):
    with pytest.raises(ValueError, match="calendar dates"):
        support.check_period(start, end)


@pytest.mark.parametrize("value,expected", [
    ("https://example.org/a", True),
    ("urn:example:a", True),
    ("example.org/a", False),
    ("", False),
    (None, False),
    ({"@id": "https://example.org/a"}, False),
])
def test_absolute_uri(value, expected):
    assert support.absolute_uri(value) is expected


def test_coded_value_requires_an_absolute_scheme_and_its_original_code():
    support.coded_value({"code_scheme": "https://example.org/scheme", "code_value": "a"})
    for value in (
        None,
        {"code_value": "a"},
        {"code_scheme": "scheme", "code_value": "a"},
        {"code_scheme": "https://example.org/scheme"},
        {"code_scheme": "https://example.org/scheme", "code_value": ""},
    ):
        with pytest.raises(ValueError, match="classification requires"):
            support.coded_value(value)
