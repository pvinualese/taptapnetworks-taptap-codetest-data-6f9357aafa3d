"""Default tabulator: one flat "events" table with every record's payload."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from taptap_codetest.records import Record
from taptap_codetest.tabular.base import Tabulator, TableSet

DEFAULT_TABLE_NAME = "events"


class EventTabulator(Tabulator):
    def __init__(self, table_name: str = DEFAULT_TABLE_NAME) -> None:
        self.table_name = table_name

    def build(self, records: Iterable[Record]) -> TableSet:
        rows = [record.payload for record in records]
        return {self.table_name: pd.DataFrame(rows)}
