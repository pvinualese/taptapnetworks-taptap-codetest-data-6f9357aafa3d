"""Writing layer: persists a `TableSet` to the output location."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from taptap_codetest.tabular.base import TableSet


class Writer(ABC):
    """Writes each table in a `TableSet` to `output_path`.

    When `partition_column` is given and a table has that column, its rows
    are split by the column's distinct values into one subdirectory per
    value, named `<partition_label>=<value>` — events are partitioned by
    when they happened, not by which file or table they came from. A table
    without that column, or no `partition_column` configured, is written
    flat at the top of `output_path`.

    Subclasses only need to say how to write one table to one path; this
    base class owns the (shared) partitioning and directory layout.
    """

    def __init__(self, partition_column: str | None = None, partition_label: str | None = None) -> None:
        self.partition_column = partition_column
        self.partition_label = partition_label if partition_label is not None else partition_column

    @property
    @abstractmethod
    def extension(self) -> str:
        """File extension (with leading dot) this writer produces."""

    @abstractmethod
    def _write_one(self, table: pd.DataFrame, path: Path) -> None:
        """Write a single table to `path`."""

    def write(self, tables: TableSet, output_path: Path) -> None:
        for name, table in tables.items():
            if self.partition_column is not None and self.partition_column in table.columns:
                self._write_partitioned(name, table, output_path)
            else:
                output_path.mkdir(parents=True, exist_ok=True)
                self._write_one(table, output_path / f"{name}{self.extension}")

    def _write_partitioned(self, name: str, table: pd.DataFrame, output_path: Path) -> None:
        for value, group in table.groupby(self.partition_column, sort=True):
            partition_dir = output_path / f"{self.partition_label}={value}"
            partition_dir.mkdir(parents=True, exist_ok=True)
            self._write_one(group, partition_dir / f"{name}{self.extension}")
