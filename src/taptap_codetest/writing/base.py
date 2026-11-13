"""Writing layer: persists a `TableSet` to the output location."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from taptap_codetest.tabular.base import TableSet


class Writer(ABC):
    """Writes each table in a `TableSet` to `output_path`."""

    @abstractmethod
    def write(self, tables: TableSet, output_path: Path) -> None: ...
