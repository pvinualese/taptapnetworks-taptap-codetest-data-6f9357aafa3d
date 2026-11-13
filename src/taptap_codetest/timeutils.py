"""Parsing of the event `ts` field, shared by cleaning and transformation."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

NAIVE_TZ = ZoneInfo("Europe/Madrid")

# Events outside this window are not real. Start is inclusive, end is exclusive.
PLAUSIBLE_WINDOW_START = datetime(2026, 8, 25, tzinfo=UTC)
PLAUSIBLE_WINDOW_END = datetime(2026, 9, 10, tzinfo=UTC)

_ISO_AWARE_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})"
)
_NAIVE_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
_EPOCH_MS_RE = re.compile(r"\d+")


class TimestampParseError(ValueError):
    pass


def parse_ts(value: Any) -> datetime:
    """Return `value` as an aware UTC datetime.

    Accepted: ISO-8601 with `Z`, ISO-8601 with explicit offset, epoch millis
    as a number or as a digit string, and naive `YYYY-MM-DD HH:MM:SS`, which
    is Europe/Madrid local time (not UTC).
    """
    if isinstance(value, bool):
        raise TimestampParseError(f"unsupported ts type: {value!r}")
    if isinstance(value, (int, float)):
        return _from_epoch_ms(value)
    if not isinstance(value, str):
        raise TimestampParseError(f"unsupported ts type: {value!r}")

    try:
        if _EPOCH_MS_RE.fullmatch(value):
            return _from_epoch_ms(int(value))
        if _ISO_AWARE_RE.fullmatch(value):
            return datetime.fromisoformat(value).astimezone(UTC)
        if _NAIVE_RE.fullmatch(value):
            naive = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return naive.replace(tzinfo=NAIVE_TZ).astimezone(UTC)
    except ValueError as exc:
        raise TimestampParseError(f"invalid ts value: {value!r}") from exc

    raise TimestampParseError(f"unrecognized ts format: {value!r}")


def is_plausible(ts: datetime) -> bool:
    """Whether `ts` falls in `[PLAUSIBLE_WINDOW_START, PLAUSIBLE_WINDOW_END)`."""
    return PLAUSIBLE_WINDOW_START <= ts < PLAUSIBLE_WINDOW_END


def _from_epoch_ms(value: int | float) -> datetime:
    try:
        return datetime.fromtimestamp(value / 1000, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise TimestampParseError(f"epoch ms out of range: {value!r}") from exc
