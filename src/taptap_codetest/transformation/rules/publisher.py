from __future__ import annotations

import pandas as pd

from taptap_codetest.records import Record
from taptap_codetest.transformation.base import TransformationRule

UNKNOWN_PUBLISHER = "UNKNOWN"


class EnrichPublisherNameRule(TransformationRule):
    """Adds `publisher_name` by looking up `publisher_id` against the
    publisher dimension (`publishers.csv`).

    A few events reference a `publisher_id` that isn't in that file; they
    still count, they just get `"UNKNOWN"` as their name rather than being
    dropped.
    """

    def __init__(self, publishers: pd.DataFrame) -> None:
        self._names = dict(zip(publishers["publisher_id"], publishers["publisher_name"]))

    def apply(self, record: Record) -> Record:
        name = self._names.get(record.payload.get("publisher_id"), UNKNOWN_PUBLISHER)
        return record.with_payload({**record.payload, "publisher_name": name})
