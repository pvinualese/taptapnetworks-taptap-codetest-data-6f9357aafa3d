"""Tabular layer: turns a stream of records into one or more named tables.

Keeping this as a dict of {table_name: DataFrame} (rather than a single
table) lets a future `Tabulator` split events by type, add a dimension
table, etc. without changing the writing layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

import pandas as pd

from taptap_codetest.records import Record

TableSet = dict[str, pd.DataFrame]


class Tabulator(ABC):
    """Builds a `TableSet` from a stream of records."""

    @abstractmethod
    def build(self, records: Iterable[Record]) -> TableSet:
        """Return the named tables produced from `records`."""
