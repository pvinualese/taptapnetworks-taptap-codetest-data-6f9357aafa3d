"""Reconciles redeliveries of the same event (same `event_id`, different
field values) into a single record.

`DuplicateLineRule` already drops byte-identical redeliveries outright.
This resolves the remaining case the brief calls out — "a few are not"
byte-identical — in two steps:

1. Within a group of same-`event_id` records, only the one(s) with the
   most recent `ts` are kept; every other copy is stale — superseded by
   a more recent delivery — and is rejected outright, not merged in.
2. If more than one record survives step 1 (they all share that same,
   most recent, `ts`), a field that agrees across them is kept; a field
   that still disagrees has no `ts` left to break the tie with and is
   set to `None` rather than guessed.

Relies on `ValidTimestampRule` having already dropped records with an
unparsable `ts`, since this needs every survivor's `ts` to be parseable.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable, Iterator
from itertools import count
from typing import Any

from taptap_codetest.records import Record, Rejection
from taptap_codetest.timeutils import parse_ts


class EventIdMerger:
    """Merges every group of records that share an `event_id`.

    A record with a missing `event_id` is never grouped with another —
    each passes through on its own. Rejections (stale, superseded
    copies) are collected in `rejections`, complete once `merge`'s
    iterator has been exhausted.
    """

    def __init__(self) -> None:
        self.rejections: list[Rejection] = []

    def merge(self, records: Iterable[Record]) -> Iterator[Record]:
        groups: OrderedDict[Any, list[Record]] = OrderedDict()
        unidentified = count()
        for record in records:
            event_id = record.payload.get("event_id")
            key = event_id if event_id is not None else ("_no_event_id", next(unidentified))
            groups.setdefault(key, []).append(record)

        for group in groups.values():
            yield group[0] if len(group) == 1 else self._resolve_group(group)

    def _resolve_group(self, group: list[Record]) -> Record:
        parsed_ts = [parse_ts(record.payload["ts"]) for record in group]
        most_recent = max(parsed_ts)

        current = [r for r, ts in zip(group, parsed_ts) if ts == most_recent]
        stale = [r for r, ts in zip(group, parsed_ts) if ts != most_recent]

        event_id = group[0].payload.get("event_id")
        for record in stale:
            self.rejections.append(
                Rejection.of(
                    record,
                    f"stale_event_id: a more recent copy of event_id {event_id!r} was kept",
                )
            )

        return current[0] if len(current) == 1 else self._merge_same_ts(current)

    def _merge_same_ts(self, group: list[Record]) -> Record:
        payloads = [record.payload for record in group]
        fields = {key for payload in payloads for key in payload} - {"ts"}

        # Every record here shares the same ts by construction (that's
        # exactly how `current` was built), so it needs no resolving.
        merged: dict[str, Any] = {"ts": payloads[0]["ts"]}
        for field in fields:
            values = [payload.get(field) for payload in payloads]
            merged[field] = values[0] if all(value == values[0] for value in values[1:]) else None

        return group[0].with_payload(merged)
