from __future__ import annotations

from taptap_codetest.cleaning.base import CleaningRule
from taptap_codetest.records import Record
from taptap_codetest.timeutils import (
    PLAUSIBLE_WINDOW_END,
    PLAUSIBLE_WINDOW_START,
    TimestampParseError,
    is_plausible,
    parse_ts,
)


class ValidTimestampRule(CleaningRule):
    """Drops events whose `ts` is missing, not in an accepted format, or
    falls outside the plausible window `[PLAUSIBLE_WINDOW_START,
    PLAUSIBLE_WINDOW_END)` — such a timestamp is not real.
    """

    def check(self, record: Record) -> str | None:
        ts = record.payload.get("ts")
        if ts is None:
            return "missing_ts"
        try:
            parsed = parse_ts(ts)
        except TimestampParseError as exc:
            return f"invalid_ts: {exc}"
        if not is_plausible(parsed):
            return (
                f"implausible_ts: {parsed.isoformat()} outside "
                f"[{PLAUSIBLE_WINDOW_START.isoformat()}, {PLAUSIBLE_WINDOW_END.isoformat()})"
            )
        return None
