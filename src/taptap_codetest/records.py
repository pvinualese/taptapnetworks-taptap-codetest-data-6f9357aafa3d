"""Shared types passed between pipeline layers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class Record:
    """A single event plus provenance metadata.

    `payload` is the event's own fields. Provenance is kept outside `payload`
    so rules only see event data, while rejections can still point back to
    the exact original input line.
    """

    payload: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    line_number: int = 0
    raw_line: str = ""

    def with_payload(self, payload: dict[str, Any]) -> Record:
        return replace(self, payload=payload)


@dataclass(frozen=True)
class Rejection:
    """An original input line that was discarded, and why."""

    reason: str
    source_file: str
    line_number: int
    raw_line: str

    @classmethod
    def of(cls, record: Record, reason: str) -> Rejection:
        return cls(reason, record.source_file, record.line_number, record.raw_line)
