"""Transformation layer: normalizes values on records that survived cleaning.

A `TransformationRule` never drops a record (that's the cleaning layer's
job); it only returns a record with (possibly) different payload values.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence

from taptap_codetest.records import Record


class TransformationRule(ABC):
    """A single value-normalization step applied to one record."""

    name: str = "transformation_rule"

    @abstractmethod
    def apply(self, record: Record) -> Record:
        """Return a record with normalized payload values."""


class Transformer:
    """Applies a sequence of `TransformationRule`s to a stream of records."""

    def __init__(self, rules: Sequence[TransformationRule] | None = None) -> None:
        self.rules = list(rules) if rules is not None else []

    def transform(self, records: Iterable[Record]) -> Iterator[Record]:
        for record in records:
            for rule in self.rules:
                record = rule.apply(record)
            yield record
