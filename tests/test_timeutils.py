from datetime import UTC, datetime, timedelta

import pytest

from taptap_codetest.timeutils import (
    PLAUSIBLE_WINDOW_END,
    PLAUSIBLE_WINDOW_START,
    TimestampParseError,
    is_plausible,
    parse_ts,
)

EXPECTED = datetime(2026, 9, 1, 10, 0, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-01T10:00:00Z",
        "2026-09-01T12:00:00+02:00",
        "2026-09-01T07:00:00-03:00",
        1788256800000,
        "1788256800000",
        "2026-09-01 12:00:00",  # Europe/Madrid is UTC+2 in September
    ],
)
def test_accepted_formats(value):
    assert parse_ts(value) == EXPECTED


def test_naive_uses_madrid_winter_offset():
    assert parse_ts("2026-01-15 12:00:00") == datetime(2026, 1, 15, 11, tzinfo=UTC)


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-01T10:00:00",  # ISO without zone
        "2026/09/01 10:00:00",
        "01-09-2026 10:00:00",
        "2026-13-01 10:00:00",
        "2026-09-01",
        "",
        "abc",
        True,
        [1788256800000],
    ],
)
def test_rejected_formats(value):
    with pytest.raises(TimestampParseError):
        parse_ts(value)


@pytest.mark.parametrize(
    "value",
    [
        PLAUSIBLE_WINDOW_START,
        PLAUSIBLE_WINDOW_START.replace(day=26),
        PLAUSIBLE_WINDOW_END - timedelta(seconds=1),
    ],
)
def test_is_plausible_accepts_window_bounds(value):
    assert is_plausible(value) is True


def test_is_plausible_rejects_before_start():
    assert is_plausible(PLAUSIBLE_WINDOW_START - timedelta(seconds=1)) is False


def test_is_plausible_rejects_end_itself_and_after():
    assert is_plausible(PLAUSIBLE_WINDOW_END) is False
    assert is_plausible(PLAUSIBLE_WINDOW_END + timedelta(days=1)) is False
