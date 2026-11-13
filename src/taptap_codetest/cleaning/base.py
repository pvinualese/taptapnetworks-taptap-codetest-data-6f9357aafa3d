"""Cleaning layer: drops records that violate a business rule.

A `CleaningRule` only decides keep/drop; it never mutates a record's
values (that's the transformation layer's job).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence

from taptap_codetest.records import Record, Rejection


class CleaningRule(ABC):
    """A single pass/fail check applied to one record."""

    @abstractmethod
    def check(self, record: Record) -> str | None:
        """Return None to keep `record`, or the rejection reason to drop it."""


class Cleaner:
    """Applies `CleaningRule`s to a stream of records.

    Dropped records are collected in `rejections`, which is complete once the
    `clean` iterator has been exhausted.
    """

    def __init__(self, rules: Sequence[CleaningRule] | None = None) -> None:
        self.rules = list(rules) if rules is not None else []
        self.rejections: list[Rejection] = []

    def clean(self, records: Iterable[Record]) -> Iterator[Record]:
        for record in records:
            reason = self._first_violation(record)
            if reason is None:
                yield record
            else:
                self.rejections.append(Rejection.of(record, reason))

    def _first_violation(self, record: Record) -> str | None:
        for rule in self.rules:
            reason = rule.check(record)
            if reason is not None:
                return reason
        return None
