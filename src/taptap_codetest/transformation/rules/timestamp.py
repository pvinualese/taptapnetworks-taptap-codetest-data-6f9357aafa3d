from __future__ import annotations

from taptap_codetest.records import Record
from taptap_codetest.timeutils import parse_ts
from taptap_codetest.transformation.base import TransformationRule


class DeriveUtcDateHourRule(TransformationRule):
    """Adds `date_utc` (YYYY-MM-DD) and `hour_utc` (0-23) from `ts`.

    Relies on `ValidTimestampRule` having already dropped unparsable `ts`.
    """

    def apply(self, record: Record) -> Record:
        ts_utc = parse_ts(record.payload["ts"])
        return record.with_payload(
            {
                **record.payload,
                "date_utc": ts_utc.date().isoformat(),
                "hour_utc": ts_utc.hour,
            }
        )
