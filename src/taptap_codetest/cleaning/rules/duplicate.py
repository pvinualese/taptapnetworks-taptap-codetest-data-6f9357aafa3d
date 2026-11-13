from __future__ import annotations

from taptap_codetest.cleaning.base import CleaningRule
from taptap_codetest.records import Record


class DuplicateLineRule(CleaningRule):
    """Drops a record whose raw line already appeared earlier in the run.

    Delivery is at-least-once, so the exact same line can repeat, in the
    same file or a later one. Only the first occurrence is kept. This rule
    is stateful (it remembers every raw line it has seen), so a fresh
    instance is needed per pipeline run — see `default_rules()`.
    """

    def __init__(self) -> None:
        self._first_seen_at: dict[str, tuple[str, int]] = {}

    def check(self, record: Record) -> str | None:
        first = self._first_seen_at.get(record.raw_line)
        if first is not None:
            source_file, line_number = first
            return f"duplicate_line: duplicate of {source_file}:{line_number}"
        self._first_seen_at[record.raw_line] = (record.source_file, record.line_number)
        return None
