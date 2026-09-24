"""Helpers shared by the example submission profiles.

A profile is a local rule for one example exchange, not vocabulary
enforcement. Each script adds this directory to ``sys.path`` so it still runs
as ``uv run --locked python examples/<name>/<script>.py``.
"""
import re
from datetime import date
from urllib.parse import urlsplit

# ASCII digits only: ``\d`` would also accept other scripts' digits.
_DAY = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def parse_day(value, field):
    """Return the calendar day of an exact ``YYYY-MM-DD`` string.

    ``date.fromisoformat`` alone also accepts other ISO 8601 forms such as
    ``20250101`` and ``2025-W01-1``. Every failure is a ValueError that names
    ``field``.
    """
    if not isinstance(value, str) or not _DAY.fullmatch(value):
        raise ValueError(f"{field}: expected an exact YYYY-MM-DD calendar date")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field}: impossible calendar date") from None


def check_period(start, end, *, message=None):
    """Raise ValueError unless known bounds form a non-empty period.

    Both ``start_date``/``end_date`` and ``valid_from``/``valid_to`` include
    their end day, so ``end == start`` is a one-day period. A missing bound is
    unknown, not open-ended, and is not checked. ``message`` replaces the
    default wording for a profile that names its own rule.
    """
    for bound in (start, end):
        if bound is not None and type(bound) is not date:
            raise ValueError("period bounds must be calendar dates; parse them with parse_day")
    if start is None or end is None:
        return
    if end < start:
        raise ValueError(message or "period: ends before it starts")


def absolute_uri(value):
    """Return whether ``value`` is a URI string with a scheme."""
    return isinstance(value, str) and bool(urlsplit(value).scheme)


def coded_value(value):
    """Raise ValueError unless ``value`` keeps an absolute scheme URI and its original code."""
    if not isinstance(value, dict) or not absolute_uri(value.get("code_scheme")):
        raise ValueError("A classification requires an absolute scheme URI")
    if not isinstance(value.get("code_value"), str) or not value["code_value"]:
        raise ValueError("A classification requires its original code")
